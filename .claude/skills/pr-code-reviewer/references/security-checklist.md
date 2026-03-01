# Security Review Checklist

OWASP-based security checklist for pull request review. Use this checklist during Phase 4 (Fresh Holistic Review) to identify security vulnerabilities.

## Injection Attacks

### SQL Injection
- [ ] No string concatenation in SQL queries
- [ ] Parameterized queries / prepared statements used
- [ ] ORM/query builder used correctly
- [ ] User input sanitized before database operations
- [ ] No raw SQL with user-controlled data

```python
# BAD
query = f"SELECT * FROM users WHERE id = {user_input}"

# GOOD
cursor.execute("SELECT * FROM users WHERE id = ?", (user_input,))
```

### Command Injection
- [ ] No shell execution with user input
- [ ] `subprocess` with `shell=False` or argument lists
- [ ] Input validated/escaped before system calls
- [ ] No backticks or `$()` with user data

```javascript
// BAD
exec(`ls ${userDir}`)

// GOOD
execFile('ls', [userDir])
```

### LDAP Injection
- [ ] LDAP queries use parameterized syntax
- [ ] Special characters escaped in DN/filter

### NoSQL Injection
- [ ] MongoDB queries don't accept raw objects from users
- [ ] Query operators validated

## Authentication & Authorization

### Authentication
- [ ] Passwords hashed with strong algorithm (bcrypt, argon2)
- [ ] No plaintext password storage
- [ ] Session tokens are cryptographically random
- [ ] Session tokens invalidated on logout
- [ ] Rate limiting on authentication endpoints
- [ ] Account lockout after failed attempts
- [ ] MFA available for sensitive operations

### Authorization
- [ ] Authorization checks on every protected route
- [ ] Role-based access control (RBAC) implemented
- [ ] Resource ownership verified
- [ ] No direct object references without authorization
- [ ] Principle of least privilege applied

```typescript
// BAD
app.get('/api/users/:id', (req, res) => {
  return db.getUser(req.params.id) // No auth check!
})

// GOOD
app.get('/api/users/:id', authenticate, authorize('read:user'), (req, res) => {
  if (req.user.id !== req.params.id && !req.user.isAdmin) {
    return res.status(403).json({ error: 'Forbidden' })
  }
  return db.getUser(req.params.id)
})
```

## Cross-Site Scripting (XSS)

- [ ] Output encoding applied (context-aware)
- [ ] Content Security Policy (CSP) headers set
- [ ] No `innerHTML` with user content
- [ ] No `eval()` with user input
- [ ] DOMPurify or similar for HTML sanitization
- [ ] HTTPOnly flag on session cookies
- [ ] X-XSS-Protection header enabled

```javascript
// BAD
element.innerHTML = userInput

// GOOD
element.textContent = userInput
// OR
element.innerHTML = DOMPurify.sanitize(userInput)
```

## Cross-Site Request Forgery (CSRF)

- [ ] CSRF tokens on state-changing operations
- [ ] SameSite cookie attribute set
- [ ] Origin/Referer header validation
- [ ] Double-submit cookie pattern (if applicable)

## Sensitive Data Exposure

### Data at Rest
- [ ] Sensitive data encrypted in database
- [ ] Encryption keys managed securely (not in code)
- [ ] PII minimized and anonymized where possible

### Data in Transit
- [ ] HTTPS enforced
- [ ] TLS 1.2+ required
- [ ] HSTS header enabled
- [ ] Certificate pinning for mobile apps

### Logging
- [ ] No passwords in logs
- [ ] No API keys in logs
- [ ] No PII in logs (or masked)
- [ ] Sensitive request bodies filtered

```python
# BAD
logger.info(f"User login: {email}, password: {password}")

# GOOD
logger.info(f"User login attempt: {hash_email(email)}")
```

## XML External Entities (XXE)

- [ ] XML parsers disable external entities
- [ ] DTD processing disabled
- [ ] Use JSON instead of XML where possible

```python
# BAD
parser = xml.etree.ElementTree.XMLParser()

# GOOD
parser = defusedxml.ElementTree.XMLParser()
```

## Insecure Deserialization

- [ ] No `pickle` with untrusted data
- [ ] No `yaml.load()` without `Loader=yaml.SafeLoader`
- [ ] No `ObjectInputStream` with untrusted data
- [ ] Input validation before deserialization
- [ ] Use JSON for data interchange

```python
# BAD
data = pickle.loads(untrusted_input)

# GOOD
data = json.loads(untrusted_input)
```

## Broken Access Control

- [ ] No predictable IDs (use UUIDs)
- [ ] Directory traversal prevented
- [ ] File upload restrictions in place
- [ ] API rate limiting implemented
- [ ] CORS configured properly

### Path Traversal
```python
# BAD
with open(f"/uploads/{filename}") as f:  # filename could be "../../etc/passwd"

# GOOD
import os
safe_path = os.path.join("/uploads", os.path.basename(filename))
if not safe_path.startswith("/uploads/"):
    raise SecurityError("Invalid path")
```

## Security Misconfiguration

- [ ] Debug mode disabled in production
- [ ] Default credentials changed
- [ ] Unnecessary features disabled
- [ ] Error messages don't leak stack traces
- [ ] Security headers configured:
  - X-Frame-Options
  - X-Content-Type-Options
  - Strict-Transport-Security
  - Content-Security-Policy
  - X-Permitted-Cross-Domain-Policies

## Cryptographic Failures

- [ ] Strong algorithms (AES-256-GCM, SHA-256+)
- [ ] No MD5 or SHA1 for security purposes
- [ ] No custom cryptography
- [ ] Random numbers use crypto-safe generators
- [ ] Key rotation implemented

```python
# BAD
import random
token = str(random.random())

# GOOD
import secrets
token = secrets.token_urlsafe(32)
```

## Insufficient Logging & Monitoring

- [ ] Failed login attempts logged
- [ ] Access control failures logged
- [ ] Input validation failures logged
- [ ] Logs include sufficient context
- [ ] Alerting on suspicious patterns

## Server-Side Request Forgery (SSRF)

- [ ] URL validation on user-provided URLs
- [ ] Whitelist allowed domains
- [ ] Block internal IP ranges
- [ ] No raw response returned to user

```python
# BAD
response = requests.get(user_provided_url)

# GOOD
url = validate_and_normalize_url(user_provided_url)
if not is_allowed_domain(url):
    raise SecurityError("Domain not allowed")
response = requests.get(url, timeout=5)
```

## Dependency Security

- [ ] `npm audit` / `pip-audit` / `cargo audit` run
- [ ] No known vulnerable dependencies
- [ ] Dependencies pinned to specific versions
- [ ] Regular dependency updates scheduled

## Secrets Management

- [ ] No hardcoded API keys
- [ ] No hardcoded database credentials
- [ ] No hardcoded encryption keys
- [ ] Secrets in environment variables or vault
- [ ] `.env` files in `.gitignore`
- [ ] Pre-commit hooks prevent secret commits

```bash
# Check for secrets
git diff --staged | grep -E "(api[_-]?key|secret|password|token)"
```

## Quick Severity Reference

| Vulnerability | Severity | Blocks Merge? |
|--------------|----------|---------------|
| SQL Injection | CRITICAL | Yes |
| Command Injection | CRITICAL | Yes |
| Authentication Bypass | CRITICAL | Yes |
| Hardcoded Secrets | CRITICAL | Yes |
| XSS (Stored) | HIGH | Yes |
| CSRF | HIGH | Usually |
| Path Traversal | HIGH | Yes |
| Sensitive Data in Logs | MEDIUM-HIGH | Depends |
| Missing Rate Limiting | MEDIUM | No |
| Debug Mode Enabled | MEDIUM | Yes |
| Outdated Dependencies | MEDIUM | No |
