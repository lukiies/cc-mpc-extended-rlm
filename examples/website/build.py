"""Build static HTML site from .claude/topics/ markdown files.

Configuration is read from .env in the project root.
See .env.example for available settings.
"""
import os
import re
import json
import html as html_mod

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..')
TOPICS_DIR = os.path.join(PROJECT_ROOT, '.claude', 'topics')
OUT_DIR = os.path.dirname(__file__)
ENV_FILE = os.path.join(PROJECT_ROOT, '.env')


def load_env(path):
    """Load key=value pairs from a .env file."""
    env = {}
    if not os.path.exists(path):
        return env
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            env[key] = value
    return env


def load_users_from_env(env):
    """Parse WEBSITE_USERS from .env into list of user dicts."""
    users_str = env.get('WEBSITE_USERS', '')
    if not users_str.strip():
        return []
    users = []
    for i, entry in enumerate(users_str.split(','), start=1):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split(':')
        if len(parts) < 4:
            continue
        users.append({
            "id": str(i),
            "email": parts[0].strip(),
            "password": parts[1].strip(),
            "name": parts[2].strip(),
            "role": parts[3].strip(),
        })
    return users


# Load configuration from .env
_env = load_env(ENV_FILE)
WEBSITE_PREFIX = _env.get('WEBSITE_PREFIX', 'kb')
WEBSITE_TITLE = _env.get('WEBSITE_TITLE', 'Knowledge Base')
WEBSITE_SUBTITLE = _env.get('WEBSITE_SUBTITLE', 'Documentation')
DEMO_USERS = load_users_from_env(_env)

# Topic ordering and display config (project-specific — update when adding new topics)
# Format: (filename-without-ext, 'Display Title', 'icon-name')
# Files in .claude/topics/ NOT listed here will NOT appear on the website.
# Available icons: book-open, presentation, file-text, lightbulb, clipboard-list,
#   book, users, bar-chart-2, pen-tool, file-check, target, compass, code,
#   settings, shield, database, globe, terminal, layers, zap
TOPIC_ORDER = [
    # ('getting-started', 'Getting Started', 'book-open'),
    # ('api-reference', 'API Reference', 'code'),
    # ('architecture', 'Architecture Overview', 'layers'),
    # ('troubleshooting', 'Troubleshooting', 'settings'),
]


def md_to_html(md_text):
    """Convert markdown to HTML (simple converter for our known format)."""
    lines = md_text.split('\n')
    html_lines = []
    in_table = False
    in_code = False
    in_list = False
    list_type = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith('```'):
            if in_code:
                html_lines.append('</code></pre>')
                in_code = False
            else:
                lang = line.strip()[3:].strip()
                html_lines.append(f'<pre class="code-block"><code class="language-{lang}">')
                in_code = True
            i += 1
            continue

        if in_code:
            html_lines.append(html_mod.escape(line))
            i += 1
            continue

        # Empty line - close lists
        if not line.strip():
            if in_list:
                html_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None
            if in_table:
                html_lines.append('</tbody></table></div>')
                in_table = False
            html_lines.append('')
            i += 1
            continue

        # Tables
        if '|' in line and line.strip().startswith('|'):
            cells = [c.strip() for c in line.strip().split('|')[1:-1]]
            if not cells:
                i += 1
                continue
            # Check if separator row
            if all(re.match(r'^[-:]+$', c) for c in cells):
                i += 1
                continue
            if not in_table:
                in_table = True
                html_lines.append('<div class="table-wrapper"><table><thead><tr>')
                for cell in cells:
                    html_lines.append(f'<th>{inline_format(cell)}</th>')
                html_lines.append('</tr></thead><tbody>')
                # Skip separator if next
                if i + 1 < len(lines) and re.match(r'^\|[-|: ]+\|$', lines[i+1].strip()):
                    i += 1
            else:
                html_lines.append('<tr>')
                for cell in cells:
                    html_lines.append(f'<td>{inline_format(cell)}</td>')
                html_lines.append('</tr>')
            i += 1
            continue

        if in_table and '|' not in line:
            html_lines.append('</tbody></table></div>')
            in_table = False

        # Headers
        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m:
            if in_list:
                html_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None
            level = len(m.group(1))
            text = m.group(2)
            slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
            css_class = f'heading-{level}'
            html_lines.append(f'<h{level} id="{slug}" class="{css_class}">{inline_format(text)}</h{level}>')
            i += 1
            continue

        # Unordered list
        m = re.match(r'^(\s*)[-*]\s+(.+)$', line)
        if m:
            content = m.group(2)
            if not in_list or list_type != 'ul':
                if in_list:
                    html_lines.append(f'</{list_type}>')
                html_lines.append('<ul>')
                in_list = True
                list_type = 'ul'
            html_lines.append(f'<li>{inline_format(content)}</li>')
            i += 1
            continue

        # Ordered list
        m = re.match(r'^(\s*)\d+\.\s+(.+)$', line)
        if m:
            content = m.group(2)
            if not in_list or list_type != 'ol':
                if in_list:
                    html_lines.append(f'</{list_type}>')
                html_lines.append('<ol>')
                in_list = True
                list_type = 'ol'
            html_lines.append(f'<li>{inline_format(content)}</li>')
            i += 1
            continue

        # Close list if not a list item
        if in_list:
            html_lines.append(f'</{list_type}>')
            in_list = False
            list_type = None

        # Regular paragraph
        html_lines.append(f'<p>{inline_format(line)}</p>')
        i += 1

    # Close any open elements
    if in_list:
        html_lines.append(f'</{list_type}>')
    if in_table:
        html_lines.append('</tbody></table></div>')
    if in_code:
        html_lines.append('</code></pre>')

    return '\n'.join(html_lines)


def inline_format(text):
    """Apply inline markdown formatting."""
    text = html_mod.escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code class="inline-code">\1</code>', text)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    return text


def extract_headings(md_text):
    """Extract h2 and h3 headings from markdown for the TOC."""
    headings = []
    for m in re.finditer(r'^(#{2,3})\s+(.+)$', md_text, re.MULTILINE):
        level = len(m.group(1))
        text = m.group(2)
        slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
        # Strip inline markdown for display
        display = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        display = re.sub(r'\*(.+?)\*', r'\1', display)
        display = re.sub(r'`(.+?)`', r'\1', display)
        headings.append({'level': level, 'text': display, 'slug': slug})
    return headings


def build_nav_html():
    nav = []
    for slug, title, icon in TOPIC_ORDER:
        nav.append(f'''
        <a href="#{slug}" class="nav-item" data-target="{slug}">
            <span class="nav-text">{title}</span>
        </a>''')
    return '\n'.join(nav)


def build_toc_html(headings):
    """Build table of contents HTML for a topic's right panel."""
    if not headings:
        return ''
    items = []
    for h in headings:
        indent_class = 'toc-h3' if h['level'] == 3 else 'toc-h2'
        items.append(f'<a href="#{h["slug"]}" class="toc-item {indent_class}" data-heading="{h["slug"]}">{html_mod.escape(h["text"])}</a>')
    return '\n'.join(items)


def build_content_sections():
    sections = []
    toc_data = {}  # slug -> headings list for JS

    for slug, title, icon in TOPIC_ORDER:
        filepath = os.path.join(TOPICS_DIR, f'{slug}.md')
        if not os.path.exists(filepath):
            continue
        with open(filepath, 'r', encoding='utf-8') as f:
            md = f.read()
        # Remove the first H1 title (we use our own)
        md_body = re.sub(r'^#\s+.+\n', '', md, count=1)
        content_html = md_to_html(md_body)
        headings = extract_headings(md_body)
        toc_html = build_toc_html(headings)
        toc_data[slug] = headings

        sections.append(f'''
    <section id="{slug}" class="content-section" style="display:none;">
        <div class="content-with-toc">
            <div class="section-main">
                <div class="section-header">
                    <h1>{title}</h1>
                </div>
                <div class="section-body">
                    {content_html}
                </div>
            </div>
            <aside class="toc-panel" data-section="{slug}">
                <div class="toc-header">On this page</div>
                <nav class="toc-nav">
                    {toc_html}
                </nav>
            </aside>
        </div>
    </section>''')
    return '\n'.join(sections), toc_data


def generate_index_html():
    nav_html = build_nav_html()
    content_html, toc_data = build_content_sections()
    users_json = json.dumps(DEMO_USERS)

    return f'''<!DOCTYPE html>
<html lang="en" class="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{WEBSITE_TITLE} - {WEBSITE_SUBTITLE}</title>
    <meta name="description" content="{WEBSITE_TITLE} - {WEBSITE_SUBTITLE}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* ===== CSS Reset & Base ===== */
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        :root {{
            --bg: #ffffff;
            --bg-secondary: #f8f9fa;
            --bg-tertiary: #f1f3f5;
            --fg: #0f1419;
            --fg-secondary: #536471;
            --fg-muted: #8899a6;
            --border: #e1e8ed;
            --border-light: #eef1f4;
            --primary: #1a1a2e;
            --primary-fg: #ffffff;
            --accent: #2563eb;
            --accent-light: #dbeafe;
            --destructive: #dc2626;
            --destructive-light: #fef2f2;
            --success: #16a34a;
            --success-light: #f0fdf4;
            --warning: #d97706;
            --warning-light: #fffbeb;
            --sidebar-w: 280px;
            --toc-w: 240px;
            --header-h: 56px;
            --radius: 8px;
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
            --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
            --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.04);
            --transition: 200ms ease;
        }}

        .dark {{
            --bg: #0f1419;
            --bg-secondary: #16202a;
            --bg-tertiary: #1c2938;
            --fg: #e7e9ea;
            --fg-secondary: #8899a6;
            --fg-muted: #536471;
            --border: #2f3940;
            --border-light: #253341;
            --primary: #e7e9ea;
            --primary-fg: #0f1419;
            --accent: #3b82f6;
            --accent-light: #1e3a5f;
            --destructive: #ef4444;
            --destructive-light: #3b1111;
            --success: #22c55e;
            --success-light: #0d331a;
            --warning: #f59e0b;
            --warning-light: #3b2f0d;
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
            --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.3);
            --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.4);
        }}

        html {{ scroll-behavior: smooth; }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 15px;
            line-height: 1.65;
            color: var(--fg);
            background: var(--bg);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}

        /* ===== Login Screen ===== */
        .login-screen {{
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
            position: relative;
            overflow: hidden;
        }}

        .login-screen::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 30% 50%, rgba(37, 99, 235, 0.08) 0%, transparent 50%),
                        radial-gradient(circle at 70% 50%, rgba(99, 102, 241, 0.06) 0%, transparent 50%);
            animation: bgShift 20s ease-in-out infinite alternate;
        }}

        @keyframes bgShift {{
            0% {{ transform: translate(0, 0); }}
            100% {{ transform: translate(-5%, 3%); }}
        }}

        .login-card {{
            position: relative;
            z-index: 1;
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 40px;
            width: 100%;
            max-width: 420px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4);
        }}

        .login-logo {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 8px;
        }}

        .login-logo-icon {{
            width: 44px;
            height: 44px;
            background: linear-gradient(135deg, #2563eb, #6366f1);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 16px;
            flex-shrink: 0;
        }}

        .login-logo-text {{
            color: #e2e8f0;
            font-size: 20px;
            font-weight: 700;
        }}

        .login-logo-sub {{
            color: #64748b;
            font-size: 12px;
            font-weight: 400;
        }}

        .login-description {{
            color: #94a3b8;
            font-size: 14px;
            margin: 16px 0 28px;
            line-height: 1.5;
        }}

        .login-form {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .form-group {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}

        .form-label {{
            font-size: 13px;
            font-weight: 500;
            color: #94a3b8;
        }}

        .form-input {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 14px;
            color: #e2e8f0;
            font-family: inherit;
            transition: all var(--transition);
            outline: none;
        }}

        .form-input::placeholder {{
            color: #475569;
        }}

        .form-input:focus {{
            border-color: #2563eb;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
        }}

        .login-error {{
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.2);
            border-radius: 8px;
            padding: 10px 14px;
            color: #fca5a5;
            font-size: 13px;
            display: none;
        }}

        .login-btn {{
            background: linear-gradient(135deg, #2563eb, #4f46e5);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 11px 20px;
            font-size: 14px;
            font-weight: 600;
            font-family: inherit;
            cursor: pointer;
            transition: all var(--transition);
            margin-top: 4px;
        }}

        .login-btn:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }}

        .login-btn:active {{
            transform: translateY(0);
        }}

        .login-divider {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 20px 0 16px;
        }}

        .login-divider::before, .login-divider::after {{
            content: '';
            flex: 1;
            height: 1px;
            background: rgba(255, 255, 255, 0.08);
        }}

        .login-divider span {{
            color: #475569;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 500;
        }}

        .quick-access {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .quick-access-title {{
            color: #64748b;
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 2px;
        }}

        .quick-btn {{
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 8px;
            padding: 10px 14px;
            cursor: pointer;
            transition: all var(--transition);
            color: #cbd5e1;
            font-family: inherit;
            font-size: 13px;
            text-align: left;
        }}

        .quick-btn:hover {{
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(255, 255, 255, 0.12);
        }}

        .quick-btn-avatar {{
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 13px;
            flex-shrink: 0;
        }}

        .quick-btn-avatar.student {{
            background: rgba(34, 197, 94, 0.15);
            color: #4ade80;
        }}

        .quick-btn-avatar.admin {{
            background: rgba(168, 85, 247, 0.15);
            color: #c084fc;
        }}

        .quick-btn-info {{
            flex: 1;
        }}

        .quick-btn-name {{
            font-weight: 500;
            color: #e2e8f0;
            font-size: 13px;
        }}

        .quick-btn-email {{
            font-size: 11px;
            color: #64748b;
        }}

        .quick-btn-role {{
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 9999px;
            font-weight: 500;
        }}

        .quick-btn-role.student {{
            background: rgba(34, 197, 94, 0.1);
            color: #4ade80;
        }}

        .quick-btn-role.admin {{
            background: rgba(168, 85, 247, 0.1);
            color: #c084fc;
        }}

        /* ===== Layout ===== */
        .app-layout {{
            display: flex;
            min-height: 100vh;
        }}

        .app-layout.hidden {{
            display: none;
        }}

        /* ===== Sidebar ===== */
        .sidebar {{
            width: var(--sidebar-w);
            background: var(--bg-secondary);
            border-right: 1px solid var(--border);
            position: fixed;
            top: 0;
            left: 0;
            bottom: 0;
            display: flex;
            flex-direction: column;
            z-index: 40;
            transition: transform var(--transition);
        }}

        .sidebar-header {{
            padding: 16px 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 12px;
            min-height: var(--header-h);
        }}

        .sidebar-logo {{
            width: 32px;
            height: 32px;
            background: var(--accent);
            border-radius: var(--radius);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 14px;
            flex-shrink: 0;
        }}

        .sidebar-title {{
            font-size: 15px;
            font-weight: 600;
            color: var(--fg);
            line-height: 1.2;
        }}

        .sidebar-subtitle {{
            font-size: 11px;
            color: var(--fg-muted);
            font-weight: 400;
        }}

        .sidebar-nav {{
            flex: 1;
            overflow-y: auto;
            padding: 8px;
        }}

        .nav-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 12px;
            border-radius: 6px;
            color: var(--fg-secondary);
            text-decoration: none;
            font-size: 13.5px;
            font-weight: 450;
            transition: all var(--transition);
            cursor: pointer;
            margin-bottom: 2px;
        }}

        .nav-item:hover {{
            background: var(--bg-tertiary);
            color: var(--fg);
        }}

        .nav-item.active {{
            background: var(--accent-light);
            color: var(--accent);
            font-weight: 550;
        }}

        .dark .nav-item.active {{
            background: var(--accent-light);
            color: #93c5fd;
        }}

        .sidebar-footer {{
            padding: 12px 20px;
            border-top: 1px solid var(--border);
            font-size: 11px;
            color: var(--fg-muted);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .logout-btn {{
            background: none;
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 11px;
            color: var(--fg-muted);
            cursor: pointer;
            font-family: inherit;
            transition: all var(--transition);
        }}

        .logout-btn:hover {{
            color: var(--destructive);
            border-color: var(--destructive);
        }}

        /* ===== Main Content ===== */
        .main-content {{
            margin-left: var(--sidebar-w);
            flex: 1;
            display: flex;
            flex-direction: column;
        }}

        .main-header {{
            height: var(--header-h);
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            padding: 0 24px;
            background: var(--bg);
            position: sticky;
            top: 0;
            z-index: 30;
            gap: 12px;
        }}

        .menu-toggle {{
            display: none;
            background: none;
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 6px 8px;
            cursor: pointer;
            color: var(--fg);
        }}

        .header-title {{
            font-size: 15px;
            font-weight: 500;
            color: var(--fg-secondary);
            flex: 1;
        }}

        .header-user {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            color: var(--fg-muted);
            padding: 4px 10px;
            border: 1px solid var(--border-light);
            border-radius: 6px;
        }}

        .header-user-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--success);
        }}

        .theme-toggle {{
            background: none;
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 6px 10px;
            cursor: pointer;
            color: var(--fg-secondary);
            font-size: 16px;
            transition: all var(--transition);
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .theme-toggle:hover {{
            background: var(--bg-tertiary);
            color: var(--fg);
            border-color: var(--fg-muted);
        }}

        /* ===== Content with TOC ===== */
        .content-with-toc {{
            display: flex;
            gap: 0;
            padding: 32px;
        }}

        .section-main {{
            flex: 1;
            min-width: 0;
            max-width: 800px;
        }}

        /* ===== TOC Panel (Right) ===== */
        .toc-panel {{
            width: var(--toc-w);
            flex-shrink: 0;
            margin-left: 32px;
            position: sticky;
            top: calc(var(--header-h) + 32px);
            align-self: flex-start;
            max-height: calc(100vh - var(--header-h) - 64px);
            overflow-y: auto;
            scrollbar-width: none;
            -ms-overflow-style: none;
        }}
        .toc-panel::-webkit-scrollbar {{
            display: none;
        }}

        .toc-header {{
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--fg-muted);
            padding-bottom: 10px;
            margin-bottom: 4px;
            border-bottom: 1px solid var(--border-light);
        }}

        .toc-nav {{
            display: flex;
            flex-direction: column;
        }}

        .toc-item {{
            display: block;
            padding: 5px 0 5px 12px;
            font-size: 12.5px;
            color: var(--fg-muted);
            text-decoration: none;
            border-left: 2px solid transparent;
            transition: all var(--transition);
            line-height: 1.4;
        }}

        .toc-item:hover {{
            color: var(--fg-secondary);
        }}

        .toc-item.active {{
            color: var(--accent);
            border-left-color: var(--accent);
            font-weight: 500;
        }}

        .toc-h3 {{
            padding-left: 24px;
            font-size: 12px;
        }}

        .content-area {{
            flex: 1;
            padding: 32px;
            max-width: 900px;
        }}

        /* ===== Welcome Section ===== */
        .welcome-section {{
            padding: 48px 32px;
            max-width: 900px;
        }}

        .welcome-title {{
            font-size: 28px;
            font-weight: 700;
            color: var(--fg);
            margin-bottom: 8px;
        }}

        .welcome-subtitle {{
            font-size: 16px;
            color: var(--fg-secondary);
            margin-bottom: 32px;
        }}

        .topic-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 12px;
        }}

        .topic-card {{
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 16px;
            cursor: pointer;
            transition: all var(--transition);
            text-decoration: none;
            color: var(--fg);
            background: var(--bg);
        }}

        .topic-card:hover {{
            border-color: var(--accent);
            box-shadow: var(--shadow-md);
            transform: translateY(-1px);
        }}

        .topic-card-title {{
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 4px;
        }}

        .topic-card-desc {{
            font-size: 12px;
            color: var(--fg-muted);
        }}

        /* ===== Content Sections ===== */
        .section-header {{
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 2px solid var(--border);
        }}

        .section-header h1 {{
            font-size: 24px;
            font-weight: 700;
            color: var(--fg);
        }}

        .section-body h2 {{
            font-size: 20px;
            font-weight: 650;
            color: var(--fg);
            margin: 32px 0 12px 0;
            padding-bottom: 6px;
            border-bottom: 1px solid var(--border-light);
        }}

        .section-body h3 {{
            font-size: 16px;
            font-weight: 600;
            color: var(--fg);
            margin: 24px 0 8px 0;
        }}

        .section-body h4 {{
            font-size: 14.5px;
            font-weight: 600;
            color: var(--fg-secondary);
            margin: 20px 0 6px 0;
        }}

        .section-body p {{
            margin-bottom: 12px;
            color: var(--fg);
        }}

        .section-body ul, .section-body ol {{
            margin: 8px 0 16px 0;
            padding-left: 24px;
        }}

        .section-body li {{
            margin-bottom: 6px;
            color: var(--fg);
        }}

        .section-body li::marker {{
            color: var(--fg-muted);
        }}

        .section-body strong {{
            font-weight: 600;
            color: var(--fg);
        }}

        .section-body em {{
            font-style: italic;
        }}

        .section-body a {{
            color: var(--accent);
            text-decoration: none;
            font-weight: 450;
        }}

        .section-body a:hover {{
            text-decoration: underline;
        }}

        /* ===== Tables ===== */
        .table-wrapper {{
            overflow-x: auto;
            margin: 16px 0;
            border: 1px solid var(--border);
            border-radius: var(--radius);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13.5px;
        }}

        th {{
            background: var(--bg-secondary);
            padding: 10px 14px;
            text-align: left;
            font-weight: 600;
            font-size: 12.5px;
            text-transform: uppercase;
            letter-spacing: 0.025em;
            color: var(--fg-secondary);
            border-bottom: 1px solid var(--border);
        }}

        td {{
            padding: 10px 14px;
            border-bottom: 1px solid var(--border-light);
            vertical-align: top;
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tr:hover td {{
            background: var(--bg-secondary);
        }}

        /* ===== Code ===== */
        .inline-code {{
            background: var(--bg-tertiary);
            border: 1px solid var(--border-light);
            border-radius: 4px;
            padding: 1px 5px;
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 0.88em;
            color: var(--accent);
        }}

        .code-block {{
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 16px;
            overflow-x: auto;
            margin: 12px 0;
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 13px;
            line-height: 1.6;
        }}

        /* ===== Back to Top ===== */
        .back-top {{
            display: none;
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: var(--accent);
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            font-size: 18px;
            cursor: pointer;
            box-shadow: var(--shadow-md);
            z-index: 50;
            transition: all var(--transition);
        }}

        .back-top:hover {{
            transform: scale(1.1);
        }}

        /* ===== Overlay ===== */
        .sidebar-overlay {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.4);
            z-index: 35;
        }}

        /* ===== Responsive ===== */
        @media (max-width: 1100px) {{
            .toc-panel {{
                display: none;
            }}
        }}

        @media (max-width: 768px) {{
            .sidebar {{
                transform: translateX(-100%);
            }}
            .sidebar.open {{
                transform: translateX(0);
            }}
            .sidebar-overlay.open {{
                display: block;
            }}
            .main-content {{
                margin-left: 0;
            }}
            .menu-toggle {{
                display: block;
            }}
            .content-with-toc {{
                padding: 20px 16px;
            }}
            .content-area, .welcome-section {{
                padding: 20px 16px;
            }}
            .topic-grid {{
                grid-template-columns: 1fr;
            }}
            .header-user {{
                display: none;
            }}
            .login-card {{
                padding: 28px 20px;
            }}
        }}

        /* ===== Print ===== */
        @media print {{
            .sidebar, .main-header, .back-top, .toc-panel, .login-screen {{ display: none !important; }}
            .main-content {{ margin-left: 0; }}
            .content-section {{ display: block !important; page-break-inside: avoid; }}
        }}

        /* ===== Scrollbar ===== */
        .toc-nav {{
            scrollbar-width: none;
            -ms-overflow-style: none;
        }}
        .toc-nav::-webkit-scrollbar {{
            display: none;
        }}
        .sidebar-nav::-webkit-scrollbar {{
            width: 4px;
        }}
        .sidebar-nav::-webkit-scrollbar-thumb {{
            background: var(--border);
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <!-- ===== LOGIN SCREEN ===== -->
    <div class="login-screen" id="loginScreen">
        <div class="login-card">
            <div class="login-logo">
                <div class="login-logo-icon">RDM</div>
                <div>
                    <div class="login-logo-text">{WEBSITE_TITLE}</div>
                    <div class="login-logo-sub">{WEBSITE_SUBTITLE}</div>
                </div>
            </div>
            <p class="login-description">Sign in to access the {WEBSITE_TITLE} knowledge base.</p>

            <form class="login-form" id="loginForm" autocomplete="off">
                <div class="login-error" id="loginError">Invalid email or password</div>
                <div class="form-group">
                    <label class="form-label" for="loginEmail">Email</label>
                    <input class="form-input" type="email" id="loginEmail" placeholder="you@uws.ac.uk" required>
                </div>
                <div class="form-group">
                    <label class="form-label" for="loginPassword">Password</label>
                    <input class="form-input" type="password" id="loginPassword" placeholder="Enter password" required>
                </div>
                <button class="login-btn" type="submit">Sign in</button>
            </form>

        </div>
    </div>

    <!-- ===== APP LAYOUT ===== -->
    <div class="app-layout hidden" id="appLayout">
        <!-- Sidebar -->
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-logo">RDM</div>
                <div>
                    <div class="sidebar-title">{WEBSITE_TITLE}</div>
                    <div class="sidebar-subtitle">{WEBSITE_SUBTITLE}</div>
                </div>
            </div>
            <nav class="sidebar-nav">
                <a href="#home" class="nav-item active" data-target="home">
                    <span class="nav-text">Home</span>
                </a>
                {nav_html}
            </nav>
            <div class="sidebar-footer">
                <span>MSc AI &middot; UWS 2025/26</span>
                <button class="logout-btn" id="logoutBtn">Sign out</button>
            </div>
        </aside>

        <!-- Overlay for mobile -->
        <div class="sidebar-overlay" id="overlay"></div>

        <!-- Main -->
        <main class="main-content">
            <header class="main-header">
                <button class="menu-toggle" id="menuBtn" aria-label="Toggle menu">&#9776;</button>
                <span class="header-title" id="headerTitle">{WEBSITE_SUBTITLE}</span>
                <div class="header-user" id="headerUser">
                    <span class="header-user-dot"></span>
                    <span id="headerUserName"></span>
                </div>
                <button class="theme-toggle" id="themeBtn" aria-label="Toggle theme">
                    <span id="themeIcon">&#9789;</span>
                    <span style="font-size:12px" id="themeLabel">Dark</span>
                </button>
            </header>

            <!-- Home / Welcome -->
            <section id="home" class="welcome-section content-section">
                <h1 class="welcome-title">{WEBSITE_TITLE}</h1>
                <p class="welcome-subtitle">Select a topic from the sidebar or click a card below to get started.</p>
                <div class="topic-grid">
                    {''.join(f"""
                    <a class="topic-card" href="#{slug}" data-target="{slug}">
                        <div class="topic-card-title">{title}</div>
                        <div class="topic-card-desc">Click to view</div>
                    </a>""" for slug, title, icon in TOPIC_ORDER)}
                </div>
            </section>

            <!-- Topic Sections -->
            <div id="contentArea" style="display:none;">
                {content_html}
            </div>
        </main>
    </div>

    <button class="back-top" id="backTop" aria-label="Back to top">&uarr;</button>

    <script>
    (function() {{
        // ===== AUTH =====
        const USERS = {users_json};
        const loginScreen = document.getElementById('loginScreen');
        const appLayout = document.getElementById('appLayout');
        const loginForm = document.getElementById('loginForm');
        const loginError = document.getElementById('loginError');
        const loginEmail = document.getElementById('loginEmail');
        const loginPassword = document.getElementById('loginPassword');
        const logoutBtn = document.getElementById('logoutBtn');
        const headerUserName = document.getElementById('headerUserName');

        function getAuth() {{
            try {{
                return JSON.parse(localStorage.getItem('{WEBSITE_PREFIX}-auth'));
            }} catch(e) {{
                return null;
            }}
        }}

        function setAuth(user) {{
            localStorage.setItem('{WEBSITE_PREFIX}-auth', JSON.stringify(user));
        }}

        function clearAuth() {{
            localStorage.removeItem('{WEBSITE_PREFIX}-auth');
        }}

        function authenticate(email, password) {{
            const user = USERS.find(u => u.email === email && u.password === password);
            return user || null;
        }}

        function showApp(user) {{
            loginScreen.style.display = 'none';
            appLayout.classList.remove('hidden');
            headerUserName.textContent = user.name;
            setAuth(user);
        }}

        function showLogin() {{
            clearAuth();
            loginScreen.style.display = 'flex';
            appLayout.classList.add('hidden');
        }}

        // Check existing session
        const existing = getAuth();
        if (existing) {{
            showApp(existing);
        }}

        loginForm.addEventListener('submit', function(e) {{
            e.preventDefault();
            const user = authenticate(loginEmail.value.trim(), loginPassword.value);
            if (user) {{
                loginError.style.display = 'none';
                showApp(user);
                // Navigate to home or hash
                const hash = window.location.hash.slice(1);
                if (hash && document.getElementById(hash)) {{
                    showSection(hash);
                }}
            }} else {{
                loginError.style.display = 'block';
                loginPassword.value = '';
            }}
        }});

        logoutBtn.addEventListener('click', function() {{
            showLogin();
        }});

        // ===== THEME =====
        const themeBtn = document.getElementById('themeBtn');
        const themeIcon = document.getElementById('themeIcon');
        const themeLabel = document.getElementById('themeLabel');

        let dark = localStorage.getItem('{WEBSITE_PREFIX}-theme') === 'dark';
        function applyTheme() {{
            document.documentElement.className = dark ? 'dark' : 'light';
            themeIcon.textContent = dark ? '\\u2600' : '\\u263D';
            themeLabel.textContent = dark ? 'Light' : 'Dark';
            localStorage.setItem('{WEBSITE_PREFIX}-theme', dark ? 'dark' : 'light');
        }}
        applyTheme();
        themeBtn.addEventListener('click', function() {{ dark = !dark; applyTheme(); }});

        // ===== SIDEBAR / MOBILE =====
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('overlay');
        const menuBtn = document.getElementById('menuBtn');
        const headerTitle = document.getElementById('headerTitle');
        const contentArea = document.getElementById('contentArea');
        const backTop = document.getElementById('backTop');
        const navItems = document.querySelectorAll('.nav-item');
        const sections = document.querySelectorAll('.content-section');
        const topicCards = document.querySelectorAll('.topic-card');

        menuBtn.addEventListener('click', function() {{
            sidebar.classList.toggle('open');
            overlay.classList.toggle('open');
        }});
        overlay.addEventListener('click', function() {{
            sidebar.classList.remove('open');
            overlay.classList.remove('open');
        }});

        // ===== NAVIGATION =====
        function showSection(id) {{
            sections.forEach(s => s.style.display = 'none');
            navItems.forEach(n => n.classList.remove('active'));

            const target = document.getElementById(id);
            if (target) {{
                target.style.display = 'block';
            }}

            if (id === 'home') {{
                contentArea.style.display = 'none';
            }} else {{
                document.getElementById('home').style.display = 'none';
                contentArea.style.display = 'block';
            }}

            navItems.forEach(n => {{
                if (n.getAttribute('data-target') === id) n.classList.add('active');
            }});

            const activeNav = document.querySelector('.nav-item.active');
            if (activeNav) {{
                headerTitle.textContent = activeNav.querySelector('.nav-text').textContent;
            }}

            sidebar.classList.remove('open');
            overlay.classList.remove('open');

            window.scrollTo(0, 0);

            // Update TOC highlight
            updateTocHighlight();
        }}

        navItems.forEach(function(item) {{
            item.addEventListener('click', function(e) {{
                e.preventDefault();
                const target = this.getAttribute('data-target');
                showSection(target);
                history.pushState(null, '', '#' + target);
            }});
        }});

        topicCards.forEach(function(card) {{
            card.addEventListener('click', function(e) {{
                e.preventDefault();
                const target = this.getAttribute('data-target');
                showSection(target);
                history.pushState(null, '', '#' + target);
            }});
        }});

        // ===== TOC scroll tracking =====
        function updateTocHighlight() {{
            const visibleSection = document.querySelector('.content-section[style*="display: block"], .content-section[style*="display:block"]');
            if (!visibleSection) return;
            const tocPanel = visibleSection.querySelector('.toc-panel');
            if (!tocPanel) return;

            const headings = visibleSection.querySelectorAll('h2[id], h3[id]');
            const tocItems = tocPanel.querySelectorAll('.toc-item');
            if (!headings.length || !tocItems.length) return;

            let activeId = null;
            const offset = 100;
            for (let i = headings.length - 1; i >= 0; i--) {{
                const rect = headings[i].getBoundingClientRect();
                if (rect.top <= offset) {{
                    activeId = headings[i].id;
                    break;
                }}
            }}

            // If no heading is above offset, use the first one
            if (!activeId && headings.length) {{
                activeId = headings[0].id;
            }}

            tocItems.forEach(function(item) {{
                if (item.getAttribute('data-heading') === activeId) {{
                    item.classList.add('active');
                }} else {{
                    item.classList.remove('active');
                }}
            }});
        }}

        // TOC click handling
        document.querySelectorAll('.toc-item').forEach(function(item) {{
            item.addEventListener('click', function(e) {{
                e.preventDefault();
                const targetId = this.getAttribute('data-heading');
                const el = document.getElementById(targetId);
                if (el) {{
                    const top = el.getBoundingClientRect().top + window.pageYOffset - 80;
                    window.scrollTo({{ top: top, behavior: 'smooth' }});
                }}
            }});
        }});

        window.addEventListener('scroll', function() {{
            updateTocHighlight();
            backTop.style.display = window.scrollY > 300 ? 'block' : 'none';
        }});

        // Handle hash on load
        const hash = window.location.hash.slice(1);
        if (hash && document.getElementById(hash) && getAuth()) {{
            showSection(hash);
        }}

        // Handle back/forward
        window.addEventListener('popstate', function() {{
            const h = window.location.hash.slice(1) || 'home';
            showSection(h);
        }});

        backTop.addEventListener('click', function() {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }});
    }})();
    </script>
</body>
</html>'''


if __name__ == '__main__':
    import sys

    if not TOPIC_ORDER:
        print('WARNING: TOPIC_ORDER is empty. Website will have no navigation.', file=sys.stderr)
        print('Add entries to TOPIC_ORDER in build.py for each .claude/topics/*.md file.', file=sys.stderr)

    if not DEMO_USERS:
        print('WARNING: No users configured. Check WEBSITE_USERS in .env', file=sys.stderr)

    # Check for topic files not in TOPIC_ORDER
    if os.path.isdir(TOPICS_DIR):
        topic_slugs = {t[0] for t in TOPIC_ORDER}
        for fname in os.listdir(TOPICS_DIR):
            if fname.endswith('.md'):
                slug = fname[:-3]
                if slug not in topic_slugs:
                    print(f'WARNING: {fname} exists but is not in TOPIC_ORDER (will not appear on website)', file=sys.stderr)

    html = generate_index_html()
    out_path = os.path.join(OUT_DIR, 'index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Generated {out_path} ({len(html)} bytes)')
