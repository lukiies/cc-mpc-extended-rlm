# Documentation Website Guide

This guide explains how the Enhanced RLM documentation website feature works — turning your `.claude/topics/*.md` knowledge base files into a polished, login-protected static HTML website.

---

## Overview

The documentation website is an **optional feature** of Enhanced RLM. When enabled, it generates a single-page application (SPA) from your project's knowledge base topic files, providing a convenient web interface for browsing project documentation.

### Key Characteristics

- **Single HTML file**: The entire website (CSS, JS, content) is bundled into one `index.html`
- **Static generation**: Built offline by a Python script, no server-side processing needed
- **Client-side auth**: Simple login screen using localStorage (not server-side security)
- **Responsive design**: Works on desktop, tablet, and mobile
- **Dark/light theme**: User preference persisted in localStorage
- **SPA routing**: Hash-based navigation (`#topic-slug`) with sidebar and right-side TOC

### Architecture

```
.claude/topics/*.md           Source markdown files (knowledge base)
        ↓
website/build.py              Python build script (reads .env + topics)
        ↓
website/index.html             Generated static SPA (single file, ~200KB)
        ↓
scp to server                 Deployed via SSH/SCP
        ↓
https://prefix.domain          Live website (nginx/Apache)
```

---

## Configuration (.env)

All website settings are stored in the project's `.env` file (never committed to git). Copy `examples/.env.example` to your project root and customize:

```env
WEBSITE_ENABLED=true
WEBSITE_PREFIX=docs
WEBSITE_DOMAIN=example.com
WEBSITE_TITLE=My Project Knowledge Base
WEBSITE_SUBTITLE=Project Documentation
WEBSITE_DEPLOY_HOST=myserver
WEBSITE_DEPLOY_PATH=/var/www/{prefix}.{domain}/index.html
WEBSITE_USERS=admin@example.com:SecurePass!:Admin:admin,reader@example.com:ReadPass:Reader:user
```

### Configuration Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `WEBSITE_ENABLED` | Yes | Enable/disable website feature | `true` or `false` |
| `WEBSITE_PREFIX` | Yes | URL prefix (subdomain) | `rdm`, `docs`, `kb` |
| `WEBSITE_DOMAIN` | Yes | Base domain | `example.com` |
| `WEBSITE_TITLE` | No | Website title | `RDM Knowledge Base` |
| `WEBSITE_SUBTITLE` | No | Subtitle | `COMP11017 Research Design` |
| `WEBSITE_DEPLOY_HOST` | Yes | SSH host alias | `mail`, `myserver` |
| `WEBSITE_DEPLOY_PATH` | Yes | Remote file path | `/var/www/docs.example.com/index.html` |
| `WEBSITE_USERS` | Yes | Login credentials | `email:pass:name:role,...` |

### User Format

`WEBSITE_USERS` is a comma-separated list of user entries. Each entry has 4 colon-separated fields:

```
email:password:display_name:role
```

- **email**: Login email address
- **password**: Login password (plaintext — this is client-side auth only)
- **display_name**: Shown in the UI after login
- **role**: `admin` or `user` (currently cosmetic)

---

## Build Script (website/build.py)

Each project has its own `build.py` in the `website/` directory. A template is provided at `examples/website/build.py` in the cc-mpc-extended-rlm repository.

### How It Works

1. **Reads `.env`** from the project root for website configuration
2. **Scans `.claude/topics/*.md`** for markdown content
3. **Converts markdown → HTML** using a built-in converter (supports tables, code blocks, lists, headers, inline formatting)
4. **Extracts headings** (h2, h3) for the right-side table of contents
5. **Generates `website/index.html`** with all CSS, JS, and content inlined

### TOPIC_ORDER

The `TOPIC_ORDER` list in `build.py` controls which topics appear and in what order:

```python
TOPIC_ORDER = [
    ('topic-slug', 'Display Title', 'icon-name'),
    ('getting-started', 'Getting Started', 'book-open'),
    ('api-reference', 'API Reference', 'code'),
]
```

- **topic-slug**: Matches the filename without `.md` extension (e.g., `getting-started.md`)
- **Display Title**: Shown in sidebar, cards, and content headers
- **icon-name**: Lucide icon name for the topic card (decorative SVG)

**Important**: Topic files not listed in `TOPIC_ORDER` will NOT appear on the website. When adding a new topic, you MUST also add it to `TOPIC_ORDER`.

### Available Icons

The builder includes SVG definitions for these icons:
`book-open`, `presentation`, `file-text`, `lightbulb`, `clipboard-list`, `book`, `users`, `bar-chart-2`, `pen-tool`, `file-check`, `target`, `compass`, `code`, `settings`, `shield`, `database`, `globe`, `terminal`, `layers`, `zap`

### Build Command

```bash
# Standard
python website/build.py

# Windows with specific Python path
PYTHONIOENCODING=utf-8 /c/Users/username/miniconda3/python website/build.py
```

### Deploy Command

```bash
scp website/index.html <WEBSITE_DEPLOY_HOST>:<WEBSITE_DEPLOY_PATH>
```

---

## Auto-Deploy (CLAUDE.md Integration)

When `WEBSITE_ENABLED=true` in `.env`, the project's `CLAUDE.md` should include an auto-deploy trigger rule. This ensures Claude automatically rebuilds and deploys the website whenever topic files are modified.

### Trigger Rule Template

Add this to your project's `CLAUDE.md`:

```markdown
## Auto-Deploy: Documentation Website (TRIGGER RULE)

**CRITICAL: This rule MUST be evaluated after EVERY file modification in `.claude/topics/`.**

### Trigger Condition
Whenever ANY file in `.claude/topics/*.md` or `.claude/INDEX.md` is created, modified, or deleted during the current session, you MUST:

1. **Rebuild the static site:**
   ```
   cd "<workspace-root>" && PYTHONIOENCODING=utf-8 python website/build.py
   ```

2. **Deploy to the server:**
   ```
   scp website/index.html <DEPLOY_HOST>:<DEPLOY_PATH>
   ```

3. **Confirm deployment** with a brief message.

### When NOT to trigger
- If the session only READ topic files without modifying them
- If `build.py` itself was modified but no topic files changed (rebuild anyway in that case)
```

Replace `<DEPLOY_HOST>` and `<DEPLOY_PATH>` with values from your `.env`.

---

## Server Setup

The website requires a web server (nginx, Apache, etc.) configured with:

1. **DNS**: Point `prefix.domain` to your server
2. **SSL**: Recommended via Let's Encrypt (certbot)
3. **Web root**: Directory containing the deployed `index.html`

### nginx Example

```nginx
server {
    listen 80;
    server_name docs.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name docs.example.com;

    ssl_certificate /etc/letsencrypt/live/docs.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/docs.example.com/privkey.pem;

    root /var/www/docs.example.com;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### Let's Encrypt Setup

```bash
sudo certbot --nginx -d docs.example.com
```

---

## Security Considerations

**Important**: The website uses **client-side authentication only**. This means:

- Credentials are stored in the generated HTML/JS (obfuscated but extractable)
- Anyone with the HTML file can bypass authentication by reading the source
- This is adequate for **convenience-level access control** (preventing casual browsing)
- It is NOT adequate for **protecting sensitive or confidential data**

For truly sensitive documentation, use server-side authentication (nginx basic auth, OAuth, etc.).

---

## Website Design

### Layout

```
┌──────────────┬─────────────────────────────┬────────────┐
│   Sidebar    │       Main Content          │    TOC     │
│  (280px)     │                             │  (240px)   │
│              │  ┌───────────────────────┐  │            │
│  Navigation  │  │  Header (56px)        │  │  Right-    │
│  items       │  ├───────────────────────┤  │  side      │
│              │  │                       │  │  table of  │
│              │  │  Article content      │  │  contents  │
│              │  │  (markdown → HTML)    │  │            │
│              │  │                       │  │  h2, h3    │
│              │  │                       │  │  headings  │
│              │  └───────────────────────┘  │            │
└──────────────┴─────────────────────────────┴────────────┘
```

### Responsive Breakpoints

- **> 1100px**: Full layout (sidebar + content + TOC)
- **768px - 1100px**: Sidebar + content (TOC hidden)
- **< 768px**: Mobile layout (sidebar as overlay)

### Theming

CSS custom properties for light/dark modes:
- Light: White background, dark text
- Dark: Dark background (#0f1419), light text
- Font: Inter (Google Fonts)
- Accent color: Blue (#2563eb light / #60a5fa dark)

### Client-Side Features

- **Login**: localStorage-based session (`{prefix}-auth`)
- **Theme**: Persisted in localStorage (`{prefix}-theme`)
- **Navigation**: Hash-based routing (`#topic-slug`)
- **Scroll tracking**: TOC highlights active section
- **Back-to-top**: Button appears on scroll > 300px
- **Mobile menu**: Hamburger toggle with overlay

---

## Adding a New Topic (Checklist)

When adding a new topic to a project's website:

1. Create the `.md` file in `.claude/topics/`
2. **Add entry to `TOPIC_ORDER` in `website/build.py`** (files not in this list won't appear)
3. Update `.claude/INDEX.md` with the new topic row
4. Rebuild: `python website/build.py`
5. Deploy: `scp website/index.html <host>:<path>`

---

## For Projects Without a Website

If `WEBSITE_ENABLED=false` (or `.env` doesn't exist), the website feature is completely inactive:
- No build script is needed
- No auto-deploy rules are triggered
- The knowledge base still works normally through the MCP server

---

*Part of the [Enhanced RLM MCP Server](https://github.com/lukiies/cc-mpc-extended-rlm) project.*
