# Boosting Continuous Learning: cc-mpc-extended-rlm + Claude Code Features

A comprehensive guide to combining the cc-mpc-extended-rlm knowledge base system with Claude Code's native extensibility features (hooks, skills, agents, plugins) to create an **active, self-reinforcing learning system** where knowledge capture is automatic, not voluntary.

**Status:** Architecture & implementation guide
**Created:** 2026-03-23
**Audience:** Developers using cc-mpc-extended-rlm who want to maximize behavioral continuity and knowledge growth across sessions

---

## Table of Contents

1. [System Overview - What We're Building](#1-system-overview)
2. [Current Architecture - What Works Today](#2-current-architecture)
3. [The Gap - Where Knowledge Gets Lost](#3-the-gap)
4. [Enhancement Strategy - From Passive to Active Learning](#4-enhancement-strategy)
5. [Implementation 1: Hooks - Automatic Triggers](#5-hooks)
6. [Implementation 2: Skills - Structured Workflows](#6-skills)
7. [Implementation 3: MCP Tool Enhancements](#7-mcp-tools)
8. [Implementation 4: Agents - Background Intelligence](#8-agents)
9. [Implementation 5: Plugin Packaging](#9-plugin)
10. [Priority Roadmap](#10-roadmap)
11. [Technical Reference](#11-reference)

---

## 1. System Overview - What We're Building <a name="1-system-overview"></a>

### The Vision

Today, the three-tier knowledge system (MEMORY.md + CLAUDE.md + `.claude/topics/`) works well - but it relies on Claude **voluntarily** following the self-learning protocol. Knowledge capture is a set of instructions in text files that can be skipped, forgotten, or half-done.

The enhanced system makes knowledge capture **involuntary and effortless**:

```
TODAY (Passive):
  Session -> Work -> Maybe update KB -> End
    \-> Knowledge capture depends on Claude following text instructions

ENHANCED (Active):
  Session -> Work -> Hooks auto-capture -> Skills guide routing -> Agents consolidate -> End
    \-> Knowledge capture is enforced by the system itself
```

### Architecture Diagram

```
+---------------------------------------------------------------------+
|                    CLAUDE CODE SESSION                               |
|                                                                     |
|  +-------------+    +--------------+    +------------------------+ |
|  | SessionStart |---->| Warm-up Hook |---->| Load recent context    | |
|  |    Hook      |    | (git log,    |    | + MEMORY.md + KB stats | |
|  +-------------+    |  last session)|    +------------------------+ |
|                      +--------------+                               |
|                                                                     |
|  +-------------------------------------------------------------+   |
|  |                      WORK PHASE                              |   |
|  |                                                              |   |
|  |  PostToolUse Hook ------> Auto-clear KB cache on topic edits |   |
|  |  /learn Skill -----------> Guided 3-tier routing             |   |
|  |  /kb-health Skill -------> KB diagnostics & maintenance      |   |
|  |  update_kb() MCP Tool ---> Atomic KB writes (1 call vs 4)   |   |
|  +-------------------------------------------------------------+   |
|                                                                     |
|  +--------------+    +--------------+    +---------------------+  |
|  |  PreCompact  |---->| Capture any  |---->| Lessons survive     |  |
|  |    Hook      |    | unsaved      |    | context compression  |  |
|  |              |    | lessons      |    |                      |  |
|  +--------------+    +--------------+    +---------------------+  |
|                                                                     |
|  +--------------+    +--------------+    +---------------------+  |
|  |  Stop Hook   |---->| Did session  |---->| Block exit until    |  |
|  |  (enforced)  |    | produce      |    | lessons are saved   |  |
|  |              |    | lessons?     |    |                      |  |
|  +--------------+    +--------------+    +---------------------+  |
|                                                                     |
|  +--------------+    +------------------------------------------+ |
|  | Consolidation|---->| Background agent merges feedback_*.md,   | |
|  | Agent        |    | prunes stale project_*.md, splits large  | |
|  | (on-demand)  |    | topic files, updates INDEX.md            | |
|  +--------------+    +------------------------------------------+ |
+---------------------------------------------------------------------+
         |                    |                    |
         v                    v                    v
   +----------+      +--------------+     +------------------+
   | MEMORY.md|      |  CLAUDE.md   |     | .claude/topics/  |
   | (Tier 1) |      |  (Tier 2)    |     | (Tier 3 via MCP) |
   | Behavior |      |  Rules       |     | Technical KB     |
   +----------+      +--------------+     +------------------+
```

---

## 2. Current Architecture - What Works Today <a name="2-current-architecture"></a>

### Three-Tier Knowledge System

| Tier | Purpose | Location | Loaded | Token Cost |
|------|---------|----------|--------|------------|
| **1. Behavioral Identity** | HOW to work | `MEMORY.md` + `feedback_*.md` | Every turn | 120 lines |
| **2. Project Rules** | WHAT to follow | `CLAUDE.md` (repo root) | Every turn | 200-400 lines |
| **3. Technical Knowledge** | WHAT to know | `.claude/topics/*.md` | On-demand via MCP | 1500 tokens/query |

### cc-mpc-extended-rlm Query Pipeline

```
User query
  -> Keyword extraction (stop words removed)
    -> Ripgrep search (CLAUDE.md + .claude/ folder)
      -> Smart chunking (by headers for MD, by functions for code)
        -> TF-IDF ranking (top 10 chunks)
          -> Haiku distillation (budget: 1K-6K tokens by query type)
            -> Cached response (1-hour TTL)
              -> Stats tracking (input/output tokens, cache hits)
```

### MCP Tools Available

| Tool | Purpose |
|------|---------|
| `ask_knowledge_base(query, context?)` | Main search - returns Haiku-distilled answer |
| `list_knowledge_base()` | Show KB structure and file sizes |
| `get_kb_session_stats()` | Accumulated token usage for session |
| `reset_kb_session_stats()` | Reset counters for new task |
| `clear_knowledge_cache()` | Invalidate cached responses |

### Self-Learning Protocol (Current - Text-Based)

After every non-trivial task, Claude is *instructed* to:
1. Analyze the session for lessons
2. Route to appropriate tier (behavioral -> MEMORY.md, technical -> topics/, procedural -> CLAUDE.md)
3. Update modular topic files
4. Update INDEX.md

**The weakness:** This is entirely voluntary. No enforcement mechanism exists.

---

## 3. The Gap - Where Knowledge Gets Lost <a name="3-the-gap"></a>

### Failure Modes (observed across 120+ sessions)

| Failure | Frequency | Impact | Root Cause |
|---------|-----------|--------|------------|
| **Skipped self-learning step** | 40% of sessions | Lessons not captured | No enforcement - just instructions |
| **Stale KB cache after edits** | 15% of topic edits | Wrong answers from KB | Manual cache clear forgotten |
| **Lessons lost to compaction** | 10% of long sessions | Mid-session discoveries vanish | No PreCompact preservation |
| **Cold session start** | Every session | Slow warm-up, repeated questions | No recent-context injection |
| **KB rot over time** | Gradual | Topics grow >100 lines, INDEX stale | No automated maintenance |
| **Multi-step KB update** | Every KB write | 3-4 tool calls per update | No atomic operation |
| **Memory file sprawl** | Over months | 10+ feedback_*.md files need consolidation | No automated consolidation |

### Cost of These Gaps

- **Repeated mistakes:** 2-3 per session without behavioral enforcement
- **Wasted tokens:** Re-reading files that KB already knows about
- **User re-explanations:** "I already told you this last session"
- **Knowledge decay:** Good lessons written but never found again due to poor indexing

---

## 4. Enhancement Strategy - From Passive to Active Learning <a name="4-enhancement-strategy"></a>

### Design Principles

1. **Involuntary > Voluntary:** Hooks fire automatically - Claude can't skip them
2. **Atomic > Multi-step:** One MCP call to update KB instead of 3-4 tool calls
3. **Guided > Freeform:** Skills provide structured workflows for complex decisions
4. **Background > Foreground:** Agents handle maintenance without blocking the user
5. **Graceful > Blocking:** Enhance the flow, don't break it when something fails

### Feature Mapping

| Claude Code Feature | Learning System Role | Why This Feature |
|--------------------|--------------------|-----------------|
| **Hooks** | Automatic triggers at key moments | Can't be skipped - fires on events |
| **Skills** | Guided knowledge routing workflows | Makes complex decisions easy |
| **MCP Tools** | Atomic KB operations | Reduces steps, prevents partial updates |
| **Agents** | Background maintenance & analysis | Non-blocking, autonomous |
| **Plugin** | Packaging all of the above | Portable, versioned, shareable |

---

## 5. Implementation 1: Hooks - Automatic Triggers <a name="5-hooks"></a>

Hooks are the **highest-impact, lowest-effort** enhancement. They fire automatically on events and cannot be skipped.

### 5.1 PostToolUse: Auto-Clear KB Cache on Topic Edits

**Problem:** After editing `.claude/topics/*.md`, KB queries return stale cached results until someone manually calls `clear_knowledge_cache`.

**Solution:**

```json
{
  "PostToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "command",
          "command": "jq -r '.tool_input.file_path // .tool_response.filePath // empty' | { read -r f; if echo \"$f\" | grep -q '\\.claude/topics/\\|CLAUDE\\.md\\|\\.claude/INDEX'; then echo '{\"systemMessage\": \"KB topic file modified - remember to clear KB cache (mcp__enhanced-rlm__clear_knowledge_cache) so future queries return fresh data.\"}'; fi; } 2>/dev/null || true",
          "timeout": 5
        }
      ]
    }
  ]
}
```

**How it works:**
1. Fires after every Write/Edit operation
2. Checks if the edited file is a KB topic, CLAUDE.md, or INDEX.md
3. If yes, sends a systemMessage reminding Claude to clear the cache
4. Non-blocking - timeout 5s, fails silently

**Impact:** Eliminates stale-cache bugs entirely. Zero manual effort.

### 5.2 PreCompact: Preserve Unsaved Lessons

**Problem:** Long sessions accumulate discoveries that get compressed away before being saved to KB.

**Solution:**

```json
{
  "PreCompact": [
    {
      "matcher": "auto",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Before context compaction, review the conversation for any unsaved knowledge: (1) user corrections about approach or behavior, (2) technical gotchas discovered during debugging, (3) patterns that worked well and should be reused, (4) mistakes made and how they were fixed. Output as additionalContext with format: 'UNSAVED LESSONS: [numbered list]'. If nothing worth saving, output empty additionalContext.",
          "timeout": 30
        }
      ]
    }
  ]
}
```

**How it works:**
1. Fires before context compression (both manual and automatic)
2. An LLM (Haiku) reviews the conversation for unsaved lessons
3. Outputs them as `additionalContext` that survives compaction
4. Claude sees these lessons in the compressed context and can still act on them

**Impact:** Most impactful single enhancement - ensures no lesson is ever lost to context compression.

### 5.3 Stop: Enforce Self-Learning Protocol

**Problem:** Claude often skips the "update KB" step at end of session, especially for routine tasks.

**Solution:**

```json
{
  "Stop": [
    {
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Review the session transcript. Determine if this session produced any lessons worth preserving: (1) User corrections about behavior or approach, (2) New technical gotchas discovered, (3) Patterns or solutions that a fresh session wouldn't know. If YES: output {\"decision\": \"block\", \"reason\": \"Self-learning check: This session produced lessons that should be saved before ending. Lessons found: [brief list]. Please save them to the appropriate tier (MEMORY.md for behavioral, .claude/topics/ for technical, feedback_*.md for user feedback) and then continue.\"}. If NO meaningful lessons: output {\"decision\": \"approve\"}.",
          "timeout": 30
        }
      ]
    }
  ]
}
```

**How it works:**
1. Fires when Claude tries to end the session
2. An LLM reviews the transcript for unsaved lessons
3. If lessons found -> blocks exit, provides the list, asks Claude to save them
4. If no lessons -> approves exit normally
5. After Claude saves, it tries to stop again -> hook approves this time

**Impact:** Turns self-learning from a suggestion into a mandatory gate. The single biggest behavioral change.

**Tuning considerations:**
- Set `timeout: 30` to prevent hanging on large sessions
- The prompt should be specific about what counts as a "lesson" to avoid false positives
- Consider adding a bypass mechanism (e.g., if user says "skip learning") to avoid frustration on trivial sessions

### 5.4 SessionStart: Warm-Up with Recent Context

**Problem:** Each session starts cold with no awareness of recent work.

**Solution:**

```json
{
  "SessionStart": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "cd \"$CLAUDE_PROJECT_DIR\" && recent=$(git log --oneline -5 --format='%h %s' 2>/dev/null | tr '\\n' '; ') && echo \"{\\\"hookSpecificOutput\\\": {\\\"additionalContext\\\": \\\"Recent commits in this project: $recent\\\"}}\"",
          "timeout": 5
        }
      ]
    }
  ]
}
```

**How it works:**
1. Fires at the start of every session
2. Reads the 5 most recent git commits
3. Injects them as `additionalContext` so Claude immediately knows what changed recently
4. Fast (5s timeout), non-blocking

**Impact:** Faster warm-up, better continuity between sessions. Claude can reference recent work without being asked.

---

## 6. Implementation 2: Skills - Structured Workflows <a name="6-skills"></a>

Skills turn complex multi-step processes into guided one-command workflows.

### 6.1 `/learn` Skill - Guided Knowledge Capture

**Location:** `skills/learn/SKILL.md`

```markdown
---
name: learn
description: Use this skill when the user says "/learn", "save this lesson", "remember this", "update the knowledge base", or when the self-learning protocol should be invoked after completing a task. Guides three-tier knowledge routing.
version: 1.0.0
---

# Knowledge Capture - Three-Tier Routing

Guide the user through capturing a lesson from the current session.

## Step 1: Identify the Lesson

Ask: "What did you learn or discover in this session?" If the user doesn't specify, analyze the conversation for:
- User corrections about approach or behavior
- Technical gotchas discovered during debugging
- Patterns or solutions worth preserving
- Mistakes made and how they were fixed

## Step 2: Classify the Lesson Type

Determine which tier the lesson belongs to:

| If the lesson is about... | Route to | Example |
|--------------------------|----------|---------|
| HOW to work (approach, verification, focus) | **MEMORY.md** (Tier 1) | "Always verify the running system before declaring done" |
| User preference or feedback | **feedback_*.md** in auto-memory | "User prefers discussing approach before coding" |
| User role or context | **user_*.md** in auto-memory | "User is a PM focused on efficiency" |
| Project deadline or decision | **project_*.md** in auto-memory | "Merge freeze starts Thursday" |
| Technical detail about the project | **.claude/topics/*.md** (Tier 3) | "FK correction invoices require two-tier flow" |
| Critical procedural rule | **CLAUDE.md** (Tier 2) | "Never query large tables for static lookups" |
| Universal lesson (any project) | **cc-mpc-extended-rlm/docs/** | "Always test auth with curl, not just browser" |

## Step 3: Write the Lesson

Follow these rules:
- **Be detailed:** Exact commands, paths, logic - not summaries
- **Include WHY:** The incident or context that produced this lesson
- **Include HOW TO APPLY:** When and where this lesson matters
- **Fresh Instance Rule:** Would a brand new Claude session find this, understand it, and follow it?

## Step 4: Update Indexes

After writing:
- If new topic file -> update `.claude/INDEX.md`
- If new memory file -> update Memory File Index in `MEMORY.md`
- Call `mcp__enhanced-rlm__clear_knowledge_cache` if topic files changed

## Step 5: Confirm

Report what was saved and where. Include the exact file path.
```

**Usage:** User types `/learn` or "save this lesson" -> Claude walks through the routing decision.

### 6.2 `/kb-health` Skill - Knowledge Base Diagnostics

**Location:** `skills/kb-health/SKILL.md`

```markdown
---
name: kb-health
description: Use this skill when the user says "/kb-health", "check knowledge base", "KB diagnostics", "audit KB", or wants to assess the health and quality of the knowledge base. Identifies stale, oversized, or missing content.
version: 1.0.0
---

# Knowledge Base Health Check

Run a comprehensive diagnostic on the three-tier knowledge system.

## Checks to Perform

### 1. Topic File Size Audit
- Read all files in `.claude/topics/`
- Flag any file over 100 lines (should be split)
- Flag any file under 5 lines (may be stub/incomplete)
- Report total topic count and average size

### 2. INDEX.md Consistency
- Compare files in `.claude/topics/` with entries in `.claude/INDEX.md`
- Flag topics not in INDEX (orphaned)
- Flag INDEX entries pointing to missing files (broken links)

### 3. MEMORY.md Health
- Count lines in MEMORY.md (target: <=120, max: 200)
- Check Memory File Index for broken links
- Count feedback_*.md, user_*.md, project_*.md files
- Flag if consolidation needed (>10 individual memory files)

### 4. CLAUDE.md Gotchas Section
- Count items in Key Gotchas (target: 10-25)
- Flag if section is getting too long

### 5. KB Token Efficiency
- Call `mcp__enhanced-rlm__get_kb_session_stats`
- Report average tokens per query
- Flag if consistently above targets (simple >1500, code >3000)

### 6. Staleness Check
- Check git log for `.claude/topics/` - flag files not modified in 30+ days
- These may be outdated or superseded

## Output Format

```
## KB Health Report

### Summary
- Topics: X files, avg Y lines
- MEMORY.md: Z/120 lines
- Memory files: N (feedback: A, user: B, project: C)
- INDEX consistency: [OK / X issues]

### Issues Found
1. [Issue description + recommended action]
2. ...

### Recommendations
- [Actionable suggestions]
```
```

### 6.3 `/kb-stats` Skill - Quick Token Usage Report

**Location:** `skills/kb-stats/SKILL.md`

```markdown
---
name: kb-stats
description: Use this skill when the user says "/kb-stats", "KB usage", "token stats", or wants a quick summary of knowledge base token consumption for the current session.
version: 1.0.0
---

# KB Token Usage Report

Quick summary of knowledge base usage in the current session.

1. Call `mcp__enhanced-rlm__get_kb_session_stats`
2. Format the results clearly
3. Compare against efficiency targets:
   - Simple queries: <1,500 input tokens
   - Code example queries: <3,000 input tokens
   - Complex queries: <4,000 input tokens
4. Note any anomalies or optimization suggestions
```

---

## 7. Implementation 3: MCP Tool Enhancements <a name="7-mcp-tools"></a>

These require changes to the cc-mpc-extended-rlm Python codebase.

### 7.1 `update_knowledge_base()` - Atomic KB Writes

**Problem:** Updating the KB currently requires 3-4 separate tool calls:
1. Write/Edit the topic file
2. Update INDEX.md (if new topic)
3. Clear cache
4. Verify

**Solution:** A single MCP tool that does all of this atomically.

**Implementation sketch** (add to `server.py`):

```python
@mcp.tool()
async def update_knowledge_base(
    topic: str,
    content: str,
    description: str = "",
    mode: str = "replace",
    update_index: bool = True
) -> str:
    """
    Atomically update a knowledge base topic file and refresh indexes.

    Args:
        topic: Topic filename without extension (e.g., "ksef-buyer-nip-rules")
        content: Full markdown content for the topic file
        description: One-line description for INDEX.md entry (required if new topic)
        mode: "replace" (overwrite) or "append" (add to end)
        update_index: Whether to update INDEX.md (default True)

    Returns:
        Confirmation message with what was updated
    """
    topic_path = kb_path / ".claude" / "topics" / f"{topic}.md"
    index_path = kb_path / ".claude" / "INDEX.md"

    # 1. Write/update topic file
    if mode == "append" and topic_path.exists():
        existing = topic_path.read_text(encoding="utf-8")
        topic_path.write_text(existing + "\n" + content, encoding="utf-8")
    else:
        topic_path.write_text(content, encoding="utf-8")

    # 2. Update INDEX.md if new topic and description provided
    if update_index and description:
        # Check if topic already in INDEX
        index_content = index_path.read_text(encoding="utf-8")
        topic_link = f"[{topic}](topics/{topic}.md)"
        if topic_link not in index_content:
            # Append to appropriate section or end
            new_entry = f"| {topic_link} | {description} |\n"
            index_content += new_entry
            index_path.write_text(index_content, encoding="utf-8")

    # 3. Clear cache
    _response_cache.clear()

    # 4. Count lines for verification
    lines = len(content.strip().split("\n"))
    warning = f" [!] File is {lines} lines (target: <100)" if lines > 100 else ""

    return (
        f"Updated .claude/topics/{topic}.md ({lines} lines){warning}. "
        f"Cache cleared. "
        f"{'INDEX.md updated.' if update_index and description else 'INDEX.md unchanged.'}"
    )
```

**Usage by Claude:**
```
# Before (4 tool calls):
1. Edit(.claude/topics/new-topic.md, content)
2. Edit(.claude/INDEX.md, add entry)
3. mcp__enhanced-rlm__clear_knowledge_cache()
4. Read(.claude/topics/new-topic.md)  # verify

# After (1 tool call):
mcp__enhanced-rlm__update_knowledge_base(
    topic="new-topic",
    content="# New Topic\n\n...",
    description="Description for INDEX.md"
)
```

**Impact:** Reduces KB update friction from 4 steps to 1. Makes self-learning faster and more reliable.

### 7.2 `get_recent_sessions_summary()` - Session Continuity

**Problem:** Each session starts with no awareness of what happened in previous sessions.

**Implementation sketch:**

```python
@mcp.tool()
async def get_recent_sessions_summary(days: int = 7) -> str:
    """
    Summarize recent knowledge base activity and git commits.

    Args:
        days: How many days back to look (default 7)

    Returns:
        Summary of recent KB changes and project commits
    """
    import subprocess
    from datetime import datetime, timedelta

    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    # Recent git commits
    result = subprocess.run(
        ["git", "log", f"--since={since}", "--oneline", "--format=%h %s"],
        capture_output=True, text=True, cwd=str(kb_path)
    )
    commits = result.stdout.strip()

    # Recently modified topic files
    result = subprocess.run(
        ["find", str(kb_path / ".claude" / "topics"), "-name", "*.md",
         "-newer", f"/tmp/kb-since-{since}", "-printf", "%f\\n"],
        capture_output=True, text=True
    )
    # Fallback: use git log for topic changes
    result = subprocess.run(
        ["git", "log", f"--since={since}", "--name-only",
         "--format=", "--", ".claude/topics/"],
        capture_output=True, text=True, cwd=str(kb_path)
    )
    topics_changed = set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()

    return (
        f"## Recent Activity (last {days} days)\n\n"
        f"### Commits\n{commits or 'None'}\n\n"
        f"### KB Topics Modified\n"
        + ("\n".join(f"- {t}" for t in topics_changed) if topics_changed else "None")
    )
```

### 7.3 `kb_health_check()` - Automated Diagnostics

**Implementation sketch:**

```python
@mcp.tool()
async def kb_health_check() -> str:
    """
    Run automated health check on the knowledge base.
    Reports oversized files, missing INDEX entries, and staleness.
    """
    topics_dir = kb_path / ".claude" / "topics"
    index_path = kb_path / ".claude" / "INDEX.md"

    issues = []
    stats = {"total_files": 0, "total_lines": 0, "oversized": 0}

    # Check topic files
    for f in sorted(topics_dir.glob("*.md")):
        lines = len(f.read_text(encoding="utf-8").strip().split("\n"))
        stats["total_files"] += 1
        stats["total_lines"] += lines
        if lines > 100:
            issues.append(f"[!] {f.name}: {lines} lines (target: <100, consider splitting)")
            stats["oversized"] += 1

    # Check INDEX consistency
    index_content = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    for f in topics_dir.glob("*.md"):
        if f.name not in index_content:
            issues.append(f"[X] {f.name}: not referenced in INDEX.md (orphaned)")

    avg_lines = stats["total_lines"] // max(stats["total_files"], 1)

    report = (
        f"## KB Health Report\n\n"
        f"- **Topics:** {stats['total_files']} files, avg {avg_lines} lines\n"
        f"- **Oversized (>100 lines):** {stats['oversized']}\n"
        f"- **Issues found:** {len(issues)}\n\n"
    )
    if issues:
        report += "### Issues\n" + "\n".join(f"- {i}" for i in issues) + "\n"
    else:
        report += "[OK] No issues found.\n"

    return report
```

---

## 8. Implementation 4: Agents - Background Intelligence <a name="8-agents"></a>

### 8.1 Knowledge Consolidation Agent

**Purpose:** Automatically merge and clean up accumulated memory files and oversized topics.

**File:** `agents/kb-consolidator.md`

```markdown
---
name: kb-consolidator
description: Use this agent when the user says "consolidate KB", "clean up knowledge base",
  "merge feedback files", or when /kb-health reports that consolidation is needed. Examples:

<example>
Context: /kb-health reports 12 feedback_*.md files in auto-memory
user: "The KB health check says I need consolidation"
assistant: "I'll launch the kb-consolidator agent to merge related feedback files
  and clean up the knowledge base."
<commentary>
Agent should merge similar feedback files, prune stale project context,
and split oversized topic files.
</commentary>
</example>

model: sonnet
color: yellow
tools: ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
---

You are a knowledge base maintenance specialist. Your job is to consolidate
and optimize the three-tier knowledge system.

**Your Responsibilities:**

1. **Merge similar feedback files:**
   - Read all feedback_*.md files in the auto-memory directory
   - Group by theme (approach, testing, deployment, etc.)
   - Merge related files, preserving all Why/How-to-apply context
   - If >5 feedback files on same theme, consolidate into a single topic

2. **Prune stale project context:**
   - Read all project_*.md files
   - Check if dates/deadlines have passed
   - Archive or remove outdated project context

3. **Split oversized topic files:**
   - Check all .claude/topics/*.md files
   - Any file >100 lines should be split into focused sub-topics
   - Update INDEX.md for new files

4. **Verify INDEX.md consistency:**
   - Every topic file should be in INDEX.md
   - Every INDEX.md entry should point to an existing file
   - Fix any inconsistencies

**Output:** Report what was changed, what was merged, what was pruned.
```

### 8.2 Session Learnings Extractor Agent

**Purpose:** Analyze a completed session transcript and extract lessons worth preserving.

**File:** `agents/session-learner.md`

```markdown
---
name: session-learner
description: Use this agent to extract lessons from a completed session. Analyzes
  the conversation for corrections, discoveries, and patterns worth preserving. Examples:

<example>
Context: End of a debugging session where several gotchas were discovered
user: "What did we learn this session?"
assistant: "I'll launch the session-learner agent to analyze our conversation
  and extract any lessons worth saving to the knowledge base."
<commentary>
Agent reviews the full conversation, identifies corrections and discoveries,
and routes them to the appropriate tier.
</commentary>
</example>

model: sonnet
color: cyan
tools: ["Read", "Write", "Edit", "Glob", "Grep"]
---

You are a knowledge extraction specialist. Analyze the current session
and identify lessons worth preserving.

**Analysis Process:**

1. **Scan for user corrections:**
   - "No, not that" / "Don't do X" / "Stop doing Y" -> behavioral feedback
   - "Yes, exactly" / "Perfect" -> validated approach (positive feedback)

2. **Scan for technical discoveries:**
   - Debugging sessions that revealed non-obvious behavior
   - Configuration gotchas that took multiple attempts
   - API quirks or undocumented behavior

3. **Scan for pattern validations:**
   - Approaches that worked well on first try
   - Reusable solutions worth templating

4. **Route each lesson:**
   - Behavioral -> suggest MEMORY.md update
   - User feedback -> suggest feedback_*.md
   - Technical -> suggest .claude/topics/ update
   - Procedural -> suggest CLAUDE.md gotcha

**Output Format:**
```
## Session Lessons

### Behavioral (-> MEMORY.md)
- [Lesson with context]

### Technical (-> .claude/topics/)
- [Lesson with context]

### None Found
[If session was routine with no new lessons]
```
```

---

## 9. Implementation 5: Plugin Packaging <a name="9-plugin"></a>

Package all enhancements as a Claude Code plugin for portability across projects.

### Plugin Structure

```
cc-learning-boost/
+-- .claude-plugin/
|   +-- plugin.json
+-- skills/
|   +-- learn/
|   |   +-- SKILL.md
|   +-- kb-health/
|   |   +-- SKILL.md
|   +-- kb-stats/
|       +-- SKILL.md
+-- agents/
|   +-- kb-consolidator.md
|   +-- session-learner.md
+-- hooks/
|   +-- hooks.json
+-- README.md
```

### plugin.json

```json
{
  "name": "cc-learning-boost",
  "version": "1.0.0",
  "description": "Active continuous learning system for cc-mpc-extended-rlm. Hooks enforce self-learning, skills guide knowledge routing, agents handle maintenance.",
  "author": {
    "name": "SoftWork",
    "url": "https://github.com/lukiies"
  },
  "keywords": [
    "learning", "knowledge-base", "memory", "self-learning",
    "cc-mpc-extended-rlm", "three-tier-architecture"
  ]
}
```

### hooks/hooks.json

```json
{
  "description": "Active learning hooks - enforce self-learning protocol, preserve lessons during compaction, auto-clear KB cache",
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path // .tool_response.filePath // empty' | { read -r f; if echo \"$f\" | grep -q '\\.claude/topics/\\|CLAUDE\\.md\\|\\.claude/INDEX'; then echo '{\"systemMessage\": \"KB topic file modified - call mcp__enhanced-rlm__clear_knowledge_cache to refresh.\"}'; fi; } 2>/dev/null || true",
            "timeout": 5
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Before context compaction, review the conversation for unsaved knowledge: (1) user corrections, (2) technical gotchas, (3) patterns that worked, (4) mistakes fixed. Output as additionalContext: 'UNSAVED LESSONS: [list]'. If nothing, output empty additionalContext.",
            "timeout": 30
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Review session for unsaved lessons: user corrections, gotchas, validated patterns. If found: {\"decision\": \"block\", \"reason\": \"Self-learning: [lessons]. Save before stopping.\"}. If none: {\"decision\": \"approve\"}.",
            "timeout": 30
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cd \"$CLAUDE_PROJECT_DIR\" 2>/dev/null && recent=$(git log --oneline -5 --format='%h %s' 2>/dev/null | tr '\\n' '; ') && if [ -n \"$recent\" ]; then echo \"{\\\"hookSpecificOutput\\\": {\\\"additionalContext\\\": \\\"Recent project commits: $recent\\\"}}\"; fi || true",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

---

## 10. Priority Roadmap <a name="10-roadmap"></a>

### Phase 1: Quick Wins (1-2 hours, no code changes to cc-mpc-extended-rlm)

| # | Enhancement | Type | Effort | Impact |
|---|------------|------|--------|--------|
| 1 | PostToolUse cache-clear hook | Hook | 10 min | Eliminates stale cache bugs |
| 2 | PreCompact lesson preservation hook | Hook | 15 min | Prevents knowledge loss in long sessions |
| 3 | Stop self-learning enforcement hook | Hook | 15 min | Makes learning mandatory |
| 4 | SessionStart warm-up hook | Hook | 10 min | Faster session startup |

**How to deploy Phase 1:**
Add hooks to `.claude/settings.local.json` (project-level) or `/.claude/settings.json` (global). No plugin needed.

### Phase 2: Guided Workflows (2-4 hours, skill files only)

| # | Enhancement | Type | Effort | Impact |
|---|------------|------|--------|--------|
| 5 | `/learn` skill | Skill | 30 min | Guided knowledge routing |
| 6 | `/kb-health` skill | Skill | 30 min | Automated KB diagnostics |
| 7 | `/kb-stats` skill | Skill | 15 min | Quick token usage reports |

**How to deploy Phase 2:**
Create skill files in a plugin directory or `.claude/skills/` (if project-local skills supported).

### Phase 3: Atomic Operations (4-8 hours, Python changes to cc-mpc-extended-rlm)

| # | Enhancement | Type | Effort | Impact |
|---|------------|------|--------|--------|
| 8 | `update_knowledge_base()` MCP tool | MCP | 2-3 hrs | Atomic KB writes |
| 9 | `kb_health_check()` MCP tool | MCP | 1-2 hrs | Automated diagnostics |
| 10 | `get_recent_sessions_summary()` MCP tool | MCP | 1-2 hrs | Session continuity |

**How to deploy Phase 3:**
Add tools to `server.py`, bump version, push to git. All projects auto-pull on next session.

### Phase 4: Intelligence (4-8 hours, agent + plugin packaging)

| # | Enhancement | Type | Effort | Impact |
|---|------------|------|--------|--------|
| 11 | kb-consolidator agent | Agent | 2-3 hrs | Background maintenance |
| 12 | session-learner agent | Agent | 2-3 hrs | Automated lesson extraction |
| 13 | Plugin packaging | Plugin | 1-2 hrs | Portable, versioned, shareable |

**How to deploy Phase 4:**
Create plugin directory with all components, install via marketplace or local path.

---

## 11. Technical Reference <a name="11-reference"></a>

### Hook Events Available

| Event | When | Matcher | Use For |
|-------|------|---------|---------|
| `PreToolUse` | Before tool runs | Tool name | Validate, modify, block |
| `PostToolUse` | After tool completes | Tool name | React, log, trigger |
| `Stop` | Agent considers stopping | - | Completeness check |
| `SubagentStop` | Subagent stopping | - | Task completion |
| `UserPromptSubmit` | User sends prompt | - | Context injection |
| `SessionStart` | Session begins | - | Environment setup |
| `PreCompact` | Before compression | "manual"/"auto" | Preserve critical info |
| `PostCompact` | After compression | "manual"/"auto" | Verify preservation |
| `Notification` | Notification fires | Type | Logging |

### Hook Output Schema

```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Message injected into Claude's context",
  "decision": "approve|block",
  "reason": "Why (becomes next prompt if blocking)",
  "hookSpecificOutput": {
    "hookEventName": "PreCompact",
    "additionalContext": "Text preserved through compaction",
    "permissionDecision": "allow|deny|ask",
    "updatedInput": {}
  }
}
```

### Skill File Format

```markdown
---
name: skill-identifier
description: Trigger conditions with specific phrases
version: 1.0.0
---

# Skill body - instructions for Claude
```

**Location:** `skills/skill-name/SKILL.md` inside a plugin directory.

### Agent File Format

```markdown
---
name: agent-identifier
description: Use this agent when [conditions]. Examples:
  <example>...</example>
model: inherit|sonnet|opus|haiku
color: blue|cyan|green|yellow|magenta|red
tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

Agent system prompt - role, responsibilities, process, output format.
```

**Location:** `agents/agent-name.md` inside a plugin directory.

### Settings File Locations

| File | Scope | Git-tracked | Priority |
|------|-------|-------------|----------|
| `/.claude/settings.json` | Global (all projects) | N/A | Lowest |
| `.claude/settings.json` | Project (shared) | Yes | Medium |
| `.claude/settings.local.json` | Project (personal) | No (.gitignore) | Highest |

Hooks defined in any of these files are active. Later files override earlier ones.

### cc-mpc-extended-rlm Codebase Locations

| File | Purpose |
|------|---------|
| `src/enhanced_rlm/server.py` | MCP server - add new tools here |
| `src/enhanced_rlm/config.py` | Configuration - token budgets, file patterns |
| `src/enhanced_rlm/search.py` | Ripgrep search + keyword extraction |
| `src/enhanced_rlm/chunker.py` | File chunking by type |
| `src/enhanced_rlm/ranker.py` | TF-IDF scoring |
| `src/enhanced_rlm/haiku_client.py` | Haiku API + caching |
| `start_server.sh` | Startup wrapper (secrets, git pull, exec) |

### Environment Variables in Hooks

| Variable | Available In | Purpose |
|----------|-------------|---------|
| `$CLAUDE_PROJECT_DIR` | All hooks | Project root directory |
| `$CLAUDE_PLUGIN_ROOT` | Plugin hooks | Plugin directory (portable paths) |
| `$CLAUDE_ENV_FILE` | SessionStart only | Persist env vars across sessions |
| `$CLAUDE_CODE_REMOTE` | All hooks | Set if running in remote context |

---

## Appendix: Evidence & Metrics

### Before vs After (Projected)

| Metric | Current (Passive) | Enhanced (Active) | Why |
|--------|-------------------|-------------------|-----|
| Lessons captured per session | 60% | 95% | Stop hook enforces capture |
| Lessons lost to compaction | 10% | 0% | PreCompact hook preserves them |
| Stale KB cache incidents | 15% of edits | 0% | PostToolUse auto-reminds |
| Session warm-up time | Slow (asks about recent work) | Fast (recent commits injected) | SessionStart hook |
| KB update steps | 3-4 tool calls | 1 MCP call | `update_knowledge_base()` |
| KB maintenance effort | Manual (user notices issues) | Semi-auto (diagnostics + agent) | `/kb-health` + consolidator |

### Token Cost of Hooks

| Hook | Tokens per Trigger | Frequency | Session Cost |
|------|-------------------|-----------|-------------|
| PostToolUse (cache-clear) | 50 (command only) | 5-10 per session | 250-500 |
| PreCompact | 500 (prompt-based) | 0-2 per session | 0-1000 |
| Stop | 500 (prompt-based) | 1 per session | 500 |
| SessionStart | 50 (command only) | 1 per session | 50 |
| **Total overhead** | | | **800-2050 tokens/session** |

This is negligible compared to the knowledge preserved and behavioral improvements gained.

---

*This guide is a living document. Update it as enhancements are implemented and new patterns emerge.*

*Related:*
- *[MEMORY_INTEGRATION_GUIDE.md](MEMORY_INTEGRATION_GUIDE.md) - Three-tier architecture setup*
- *[DEVELOPMENT_BEST_PRACTICES.md](DEVELOPMENT_BEST_PRACTICES.md) - Universal coding lessons*
