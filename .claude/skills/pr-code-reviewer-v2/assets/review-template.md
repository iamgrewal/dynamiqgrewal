# Code Review Summary

**PR:** [#NUMBER] TITLE
**Reviewer:** Claude Code Reviewer
**Date:** YYYY-MM-DD
**Overall Assessment:** [Approve / Request Changes / Comment]
**Stack Detected:** [languages/frameworks]

---

## Key Changes

[Brief summary of what this PR accomplishes in 2-3 sentences]

---

## Critical Issues (Blocking)

> These issues must be resolved before merge.

| # | Issue | Location | Severity | Action Required |
|---|-------|----------|----------|-----------------|
| 1 | [Description] | `file:line` | CRITICAL | [What needs to be done] |

### Details

#### 1. [Issue Title]

**Location:** `path/to/file.ext:line`

**Problem:**
[Description of the issue]

**Impact:**
[Why this is critical]

**Recommendation:**
```language
// Code example of suggested fix
```

---

## Important Issues (Non-Blocking)

> These should be addressed but don't block merge.

| # | Issue | Location | Severity | Recommendation |
|---|-------|----------|----------|----------------|
| 1 | [Description] | `file:line` | HIGH | [What should be done] |
| 2 | [Description] | `file:line` | MEDIUM | [What should be done] |

### Details

#### 1. [Issue Title]

**Location:** `path/to/file.ext:line`

**Problem:**
[Description of the issue]

**Recommendation:**
```language
// Code example of suggested fix
```

---

## Suggestions

> Nice-to-have improvements for future consideration.

| # | Suggestion | Location | Priority |
|---|------------|----------|----------|
| 1 | [Description] | `file:line` | LOW |
| 2 | [Description] | `file:line` | LOW |

---

## Positive Feedback

> Highlighting good patterns and quality contributions.

- [Specific good pattern or clean code example]
- [Thorough test coverage example]
- [Good documentation example]
- [Smart architectural decision]

---

## Testing

| Metric | Status |
|--------|--------|
| Coverage | [percentage or status] |
| New tests added | [count] |
| Regression tests | [yes/no] |
| Test quality | [assessment] |

### Test Coverage Notes

- [Notes about test coverage adequacy]
- [Any gaps identified]

---

## Security Notes

| Check | Status |
|-------|--------|
| SQL Injection | [Pass/Fail/N/A] |
| XSS | [Pass/Fail/N/A] |
| Authentication | [Pass/Fail/N/A] |
| Authorization | [Pass/Fail/N/A] |
| Secrets | [Pass/Fail/N/A] |
| Input Validation | [Pass/Fail/N/A] |

### Security Findings

- [Any security concerns or "No security issues identified"]

---

## Performance Notes

| Check | Status |
|-------|--------|
| N+1 Queries | [Pass/Fail/N/A] |
| Memory Leaks | [Pass/Fail/N/A] |
| Async Blocking | [Pass/Fail/N/A] |
| Pagination | [Pass/Fail/N/A] |

### Performance Findings

- [Any performance concerns or "No performance issues identified"]

---

## Files Changed Summary

| File | Lines Added | Lines Deleted | Type |
|------|-------------|---------------|------|
| `path/to/file.ext` | +XX | -XX | [feature/fix/refactor/test] |

---

## Recommendation

[Final recommendation with any conditions]

### Merge Conditions (if applicable)

- [ ] Condition 1
- [ ] Condition 2

### Next Steps

1. [Action item 1]
2. [Action item 2]

---

## Review Statistics

| Metric | Value |
|--------|-------|
| Files reviewed | X |
| Critical issues | X |
| Important issues | X |
| Suggestions | X |
| Threads resolved | X |
| Time estimate | X min |
