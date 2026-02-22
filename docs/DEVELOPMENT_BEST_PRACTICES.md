# Development Best Practices - Lessons from Real Projects

Universal lessons learned across projects using cc-mpc-extended-rlm. These apply to any project, regardless of tech stack.

---

## Web Authentication Security

### CRITICAL: Client-Side Auth is NOT Security

**Incident:** A login screen was built that hid content with CSS (`display:none`). All protected content was embedded in the HTML/markdown files served statically. Anyone could `curl` the files directly or disable CSS/JS to see everything.

**Rule:** CSS/JS-based content hiding is cosmetic, not security. Protected content must NEVER be sent to unauthenticated clients.

### Architecture Pattern: Server-Side Auth for Static Sites

When a "static" site needs authentication:
1. **Login page** - standalone HTML with ZERO protected content, only the login form
2. **Auth backend** - validates credentials, issues signed cookies/tokens
3. **App shell** - served ONLY after cookie/token validation, contains layout but NO embedded content
4. **Content API** - all content fetched via authenticated API calls (server checks credentials per request)
5. **Never combine** login page and app content in the same HTML file

### Security Testing: Always Test at HTTP Level

Browser-based testing is **misleading** for security. Always verify with `curl`:

```bash
# Test 1: Login page loads and contains zero protected content
curl -s http://site.com/ | grep -c "protected_keyword"  # Must be 0

# Test 2: Direct content access without cookie returns 401
curl -s -o /dev/null -w "%{http_code}" http://site.com/docs/secret.md  # Must be 401

# Test 3: Protected pages redirect without auth
curl -s -o /dev/null -w "%{http_code}" http://site.com/app  # Must be 302

# Test 4: API endpoints require auth
curl -s http://site.com/api/whoami  # Must return 401
```

---

## Deployment & Permissions

### Service User File Access

When deploying apps as systemd services (running as `www-data` or similar):

- **Home directory traversal**: If project is under `/home/user/`, the home dir needs `o+rx` for the service user to traverse into it
- **`.env` permissions**: Should be `640` with service user's group (e.g., `chgrp www-data .env`)
- **Project directory**: Needs `o+rX` recursively for service user to read files
- **Gotcha**: A service may start successfully but return empty data because it can't read config files - always check permissions first

### Systemd Service Checklist

```bash
# After deploying a new service:
sudo systemctl status service-name     # Check it's running
sudo journalctl -u service-name -n 20  # Check logs for errors
curl -s http://localhost:PORT/          # Verify it responds
ls -la /path/to/.env                   # Verify permissions
```

---

## Self-Learning Protocol Observations

### What Works Well
- **Routing lessons by type** (project-specific vs universal) prevents cluttering individual projects with generic knowledge
- **Auto-memory reinforcement** of critical rules (like session startup check) ensures compliance across sessions
- **Modular topic files** (<100 lines) enable efficient Haiku extraction
- **5-point security testing checklist** catches issues that browser testing misses

### Common Mistakes to Avoid
- Building features with cosmetic validation instead of real security
- Testing only in the browser (use curl/wget for security verification)
- Deploying without checking file permissions for the service user
- Combining public and protected content in the same page/response
- Not defining test procedures before implementing security features

---

*Updated: 2026-02-22 | Source: marketing-research project session*
