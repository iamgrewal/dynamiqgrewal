---
name: pr-code-reviewer
description: Perform structured, high-quality pull request reviews using the code-reviewer plugin. This skill should be used when reviewing GitHub PRs, resolving existing review comments, enforcing test coverage, validating architecture, ensuring production readiness, or conducting security audits. Automates comment resolution, applies safe fixes, runs security scans, and produces structured review summaries with severity classification.
---

# PR Code Reviewer

## Overview

Perform comprehensive pull request reviews using a structured, risk-aware workflow. Resolve existing review comments, apply safe automated fixes, validate quality gates, run security scans, and produce a structured final review summary.

## When to Use This Skill

- Reviewing a GitHub pull request before merge
- Processing unresolved review comments from Copilot or teammates
- Enforcing test coverage on new features
- Validating security compliance before production deployment
- Conducting architecture reviews on significant changes
- Preparing release branch validation
- Quality enforcement during sprint reviews

## Workflow

### Phase 1: Load PR Context

```
1. Run code-reviewer plugin to load full PR diff
2. Fetch all review threads (open and resolved)
3. Identify unresolved threads requiring action
4. Detect technology stack using scripts/detect-stack.py
5. Load relevant reference checklists based on detected stack
```

**Stack Detection:** Run `python3 scripts/detect-stack.py` to identify:
- Primary language(s)
- Framework(s) in use
- Test framework(s)
- Build system
- Security tools configured

### Phase 2: Resolve Existing Comments

For each open review thread, classify and respond:

#### Comment Classification

| Type | Auto-Fix? | Action |
|------|-----------|--------|
| Bug | Yes (if safe) | Fix directly, add regression test |
| Style/formatting | Yes | Apply formatter, resolve thread |
| Naming | Yes | Rename with IDE refactoring |
| Missing test | Yes | Add test covering the case |
| Security issue | **No** | Reply with severity, recommend fix |
| Performance concern | Maybe | Profile first, then decide |
| Documentation gap | Yes | Add/update docs |
| Architecture concern | **No** | Reply with trade-off analysis |

#### Decision Framework

**Implement directly when:**
- Change is localized (< 20 lines)
- No architecture impact
- Aligns with existing repository patterns
- Test coverage can be added
- No security sensitivity

**Reply without editing when:**
- Non-trivial design trade-off required
- Product decision needed
- Public API contract affected
- Database schema migration required
- Security-sensitive logic involved
- Breaking change potential

**After implementing fixes:**
1. Run relevant tests to confirm no regression
2. Resolve the thread in GitHub with summary
3. Document fix in commit message

### Phase 3: Sanity Validation

After resolving comments, verify code hygiene:

| Check | Action |
|-------|--------|
| Unused imports | Remove |
| Dead code | Delete |
| Null safety | Add guards or assertions |
| Logging consistency | Unify format/levels |
| Error handling | Ensure proper propagation |
| Naming consistency | Apply project conventions |
| Dependency injection | Verify proper patterns |
| Debug logs | Remove all |
| Magic numbers | Extract to constants |
| TODO comments | Create issues or resolve |

### Phase 4: Fresh Holistic Review

#### Correctness Checks

- [ ] Edge cases handled
- [ ] Null/undefined handling complete
- [ ] Off-by-one errors absent
- [ ] Unhandled promises caught
- [ ] Race conditions prevented
- [ ] Resource leaks absent
- [ ] State transitions valid

#### Security Scan (see references/security-checklist.md)

Run deep security analysis:
- SQL injection vectors
- XSS vulnerabilities
- Authentication bypass risks
- Authorization gaps
- Sensitive data exposure in logs
- Hardcoded secrets/credentials
- Insecure deserialization
- CSRF vulnerabilities
- Path traversal risks
- Command injection vectors

**For security findings:** Use severity classification from `references/severity-classification.md`. Blocking issues must be resolved before merge.

#### Performance Analysis (see references/performance-checklist.md)

- [ ] N+1 queries identified and resolved
- [ ] Unbounded loops have limits
- [ ] Blocking I/O moved to async where appropriate
- [ ] Memory growth bounded
- [ ] Filtering operations optimized
- [ ] Caching applied where beneficial
- [ ] Database indexes utilized

#### API & Contract Validation

- [ ] Breaking changes documented
- [ ] Version compatibility maintained
- [ ] Backward compatibility verified
- [ ] Migration path documented
- [ ] Deprecation notices added

### Phase 5: Test Validation

**Requirement:** New features MUST include tests. Bug fixes SHOULD include regression tests.

#### Coverage Verification

```bash
# Python
pytest --cov --cov-report=term-missing

# Node.js/TypeScript
npm test -- --coverage --coverageReporters=text

# Go
go test -cover ./...

# Rust
cargo test -- --nocapture
```

#### Test Quality Checks

- [ ] Happy path covered
- [ ] Edge cases tested
- [ ] Error conditions validated
- [ ] Integration coverage for critical paths
- [ ] No flaky tests introduced
- [ ] Proper mocking (no over-mocking)
- [ ] Assertions meaningful and specific

**If safe to add tests:**
- Add small missing test cases
- Improve assertion specificity
- Remove redundant/duplicate tests

**If risky to modify tests:**
- Leave a comment requesting test addition
- Note in review summary

### Phase 6: Structured Output

Produce final review using `assets/review-template.md`:

```markdown
## Code Review Summary
**PR:** [PR number and title]
**Overall Assessment:** Approve / Request Changes / Comment
**Stack Detected:** [languages/frameworks]

### Key Changes
[Brief summary of what this PR accomplishes]

## Critical Issues (Blocking)
| Issue | Location | Severity | Action Required |
|-------|----------|----------|-----------------|
| [Description] | file:line | CRITICAL | Must fix before merge |

## Important Issues (Non-Blocking)
| Issue | Location | Severity | Recommendation |
|-------|----------|----------|----------------|
| [Description] | file:line | HIGH/MEDIUM | Should address |

## Suggestions
| Suggestion | Location | Priority |
|------------|----------|----------|
| [Description] | file:line | LOW |

## Positive Feedback
- [Highlight good patterns, clean code, thorough tests]

## Testing
- Coverage: [percentage or status]
- New tests added: [count]
- Regression tests: [status]

## Security Notes
- Scan result: [clean/issues found]
- Issues: [list or "none"]

## Recommendation
[Final merge recommendation with any conditions]
```

## Severity Classification

See `references/severity-classification.md` for complete definitions.

| Level | Criteria | Merge Impact |
|-------|----------|--------------|
| CRITICAL | Security vulnerability, data corruption risk, production breakage | BLOCKS merge |
| HIGH | Missing tests, edge case bugs, poor error handling | Strongly recommend fix |
| MEDIUM | Maintainability risk, minor bugs, code smell | Should address |
| LOW | Style improvement, minor refactor, docs | Nice to have |

## Guardrails

- **Minimal edits:** Prefer targeted fixes over refactors
- **No large refactors:** Save for dedicated PRs
- **Follow patterns:** Match existing repository conventions
- **Avoid noise:** Don't leave trivial comments
- **Comment when uncertain:** Don't auto-edit risky areas
- **Never auto-merge:** Always require human approval
- **Security first:** When in doubt, block and escalate

## Resources

### scripts/
- `detect-stack.py` - Identifies languages, frameworks, and build tools in the PR

### references/
- `security-checklist.md` - OWASP-based security review checklist
- `testing-standards.md` - Test coverage and quality requirements
- `performance-checklist.md` - Performance anti-patterns and optimizations
- `severity-classification.md` - Detailed severity definitions and examples

### assets/
- `review-template.md` - Copy-paste template for structured review output

## Success Criteria

- [ ] All unresolved comments processed
- [ ] No unaddressed critical issues
- [ ] Test coverage maintained or improved
- [ ] Security scan completed
- [ ] Review summary posted
- [ ] Clear next steps documented
- [ ] Threads resolved with explanations
