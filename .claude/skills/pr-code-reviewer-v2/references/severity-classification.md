# Severity Classification

Detailed severity definitions and examples for PR review findings.

## Severity Levels

| Level | Blocks Merge? | SLA | Examples |
|-------|---------------|-----|----------|
| CRITICAL | Yes | Fix immediately | Security vulnerability, data loss |
| HIGH | Usually | Fix before merge | Missing tests, major bugs |
| MEDIUM | No | Fix soon | Code smell, minor bugs |
| LOW | No | Nice to have | Style, documentation |

---

## CRITICAL

**Definition:** Issues that could cause security breaches, data loss, production outages, or significant business impact.

**Merge Policy:** Must be resolved before merge. No exceptions without documented risk acceptance.

### Categories

#### Security Vulnerabilities
- SQL injection
- Command injection
- Authentication bypass
- Authorization bypass
- Hardcoded secrets/credentials
- Path traversal
- SSRF to internal resources
- Cryptographic weaknesses

#### Data Integrity
- Data corruption risk
- Data loss potential
- Transaction integrity issues
- Race conditions on critical paths
- Missing backup/recovery

#### Production Stability
- Breaking changes without migration
- Database schema changes without rollback
- Infinite loops or recursion
- Resource exhaustion (memory, connections)
- Unhandled exceptions in critical paths

### Examples

```python
# CRITICAL: SQL Injection
query = f"SELECT * FROM users WHERE id = {user_input}"

# CRITICAL: Hardcoded Secret
API_KEY = "sk-live-abc123..."

# CRITICAL: Data Loss
def delete_user(user_id):
    # No transaction, could partial fail
    db.users.delete(user_id)
    db.orders.delete(user_id)  # If this fails, user gone but orders remain
```

---

## HIGH

**Definition:** Issues that could cause bugs, missing functionality, or significant technical debt.

**Merge Policy:** Strongly recommended to fix before merge. Can be deferred with documented issue.

### Categories

#### Missing Tests
- New feature without tests
- Bug fix without regression test
- Critical path untested

#### Bugs
- Edge case failures
- Incorrect business logic
- Error handling gaps
- State machine violations

#### Performance
- N+1 queries
- Missing pagination
- Memory leaks
- Unbounded operations

#### API Contracts
- Breaking changes without version bump
- Missing input validation
- Inconsistent error responses

### Examples

```python
# HIGH: Missing test for new feature
def calculate_discount(price, tier):
    # Complex business logic with no test
    if tier == 'gold':
        return price * 0.8
    elif tier == 'silver':
        return price * 0.9
    return price

# HIGH: N+1 Query
for order in orders:
    user = db.get_user(order.user_id)  # Query per order

# HIGH: Missing validation
def create_user(email):
    # No email format validation
    return db.insert_user(email)
```

---

## MEDIUM

**Definition:** Issues that affect code quality, maintainability, or could lead to future problems.

**Merge Policy:** Should be addressed, but not blocking.

### Categories

#### Code Quality
- Dead code
- Duplicate code
- Complex conditionals (high cyclomatic complexity)
- Missing error handling for edge cases
- Inconsistent patterns

#### Maintainability
- Missing documentation for public APIs
- Unclear variable/function names
- Magic numbers without constants
- Overly long functions (> 50 lines)
- Deep nesting (> 3 levels)

#### Dependencies
- Outdated dependencies
- Unused dependencies
- Duplicate functionality in dependencies

#### Configuration
- Debug mode settings
- Missing environment validation
- Hardcoded configuration values

### Examples

```python
# MEDIUM: Dead code
def old_calculation(x):
    # This function is never called
    return x * 2

# MEDIUM: Magic number
if user.age > 21:  # What is 21?
    allow_access()

# BETTER
LEGAL_AGE = 21
if user.age > LEGAL_AGE:
    allow_access()

# MEDIUM: Missing docstring for public API
def process_payment(amount, currency):
    # Public API without documentation
    pass
```

---

## LOW

**Definition:** Suggestions for improvement, style preferences, or minor optimizations.

**Merge Policy:** Nice to have. Can be addressed in follow-up PRs.

### Categories

#### Style
- Naming conventions
- Formatting inconsistencies
- Comment quality
- Import organization

#### Documentation
- Minor typos
- Clarity improvements
- Example updates

#### Minor Optimizations
- Slight performance improvements
- Code simplification
- Better error messages

#### Best Practices
- Optional type hints
- Optional logging
- Optional metrics

### Examples

```python
# LOW: Naming could be clearer
def proc(d):
    return d['value']

# BETTER
def extract_value(data):
    return data['value']

# LOW: Minor optimization
result = []
for x in items:
    result.append(x.value)

# BETTER (but not critical)
result = [x.value for x in items]

# LOW: Comment improvement
# Fix the bug
if x > 0:
    return x

# BETTER
# Return positive values to avoid negative balance errors
if x > 0:
    return x
```

---

## Classification Decision Tree

```
┌─────────────────────────────────────────────────────────────┐
│ Is there a security vulnerability?                           │
│ └─ YES → CRITICAL                                            │
│                                                              │
│ Is there risk of data loss or corruption?                    │
│ └─ YES → CRITICAL                                            │
│                                                              │
│ Could this cause production outage?                          │
│ └─ YES → CRITICAL                                            │
│                                                              │
│ Is there a bug that affects functionality?                   │
│ └─ YES → Are there missing tests?                            │
│       └─ YES → HIGH                                          │
│       └─ NO → HIGH                                           │
│                                                              │
│ Is there a performance issue (N+1, memory leak)?             │
│ └─ YES → HIGH                                                │
│                                                              │
│ Is there dead code, duplication, or complexity?              │
│ └─ YES → MEDIUM                                              │
│                                                              │
│ Is there a style or documentation issue?                     │
│ └─ YES → LOW                                                 │
│                                                              │
│ Is it a minor improvement suggestion?                        │
│ └─ YES → LOW                                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Context Factors

Factors that can adjust severity:

### Increase Severity
- Issue in authentication/authorization code
- Issue in payment/financial code
- Issue affects public API
- Issue in high-traffic endpoint
- No easy rollback available
- Multiple components affected

### Decrease Severity
- Issue in rarely used feature
- Easy workaround available
- Quick fix possible
- Low traffic area
- Internal tool only

---

## Severity Examples by Category

### Security
| Issue | Base Severity | Context Adjustment | Final |
|-------|---------------|-------------------|-------|
| SQL injection | CRITICAL | - | CRITICAL |
| Missing CSRF token | HIGH | Auth endpoint → CRITICAL | CRITICAL |
| Verbose error message | MEDIUM | Contains stack trace → HIGH | HIGH |
| Missing rate limiting | MEDIUM | Login endpoint → HIGH | HIGH |

### Testing
| Issue | Base Severity | Context Adjustment | Final |
|-------|---------------|-------------------|-------|
| New feature, no tests | HIGH | - | HIGH |
| Bug fix, no regression test | HIGH | - | HIGH |
| Missing edge case test | MEDIUM | Critical path → HIGH | HIGH |
| Test naming unclear | LOW | - | LOW |

### Performance
| Issue | Base Severity | Context Adjustment | Final |
|-------|---------------|-------------------|-------|
| N+1 query | HIGH | High traffic → CRITICAL | CRITICAL |
| Missing pagination | HIGH | Low traffic → MEDIUM | MEDIUM |
| Unoptimized algorithm | MEDIUM | Batch job → LOW | LOW |
| Large bundle size | MEDIUM | Critical path → HIGH | HIGH |

---

## Review Comment Format

```markdown
**[SEVERITY]** Issue Title

Location: `file:line`

**Problem:**
Description of what's wrong.

**Impact:**
Why this matters.

**Suggestion:**
```language
// Code example of fix
```

**References:**
- Link to docs/standards if applicable
```

### Example

```markdown
**[HIGH]** Missing test coverage for discount calculation

Location: `src/services/pricing.ts:42`

**Problem:**
The `calculateDiscount` function has complex conditional logic but no unit tests.

**Impact:**
Changes to pricing logic could introduce bugs without detection.

**Suggestion:**
Add tests for:
- Gold tier discount (20%)
- Silver tier discount (10%)
- Default (no discount)
- Edge case: negative prices
- Edge case: zero price

```typescript
describe('calculateDiscount', () => {
  it('should apply 20% discount for gold tier', () => {
    expect(calculateDiscount(100, 'gold')).toBe(80);
  });
});
```
```
