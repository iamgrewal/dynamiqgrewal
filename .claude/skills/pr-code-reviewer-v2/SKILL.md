---
name: pr-code-reviewer
description: Perform structured, high-quality pull request reviews using the code-reviewer plugin with AI-Augmented CI/CD patterns. This skill should be used when reviewing GitHub PRs, resolving existing review comments, enforcing test coverage, validating architecture, ensuring production readiness, conducting security audits, or implementing policy-as-code guardrails. Implements Trust Tier Framework (T0-T3), Decision Logging for SOC 2/ISO 27001 compliance, and integrates with Policy Engine (OPA) for hard constraints.
---

# PR Code Reviewer (AI-Augmented CI/CD)

## Overview

Perform comprehensive pull request reviews using a structured, risk-aware workflow with **AI-Augmented CI/CD patterns**. This skill implements the reference architecture from "AI-Augmented CI/CD Pipelines" (arXiv:2508.11867) including:

- **Policy-as-Code Guardrails** (Open Policy Agent)
- **Trust Tier Framework** (T0-T3 progressive autonomy)
- **Decision Logging** (JSON format for SOC 2/ISO 27001)
- **Automated Canary Analysis Integration**
- **Multi-Agent Coordination** with specialized CI/CD agents

## When to Use This Skill

- Reviewing a GitHub pull request before merge
- Processing unresolved review comments from Copilot or teammates
- Enforcing test coverage on new features
- Validating security compliance before production deployment
- Conducting architecture reviews on significant changes
- Preparing release branch validation
- Quality enforcement during sprint reviews
- Implementing policy gates for CI/CD pipelines
- Setting up canary deployment analysis

---

## Part 1: Policy Engine (The Safety Net)

### Open Policy Agent (OPA) Integration

Before any AI agent takes action, hard constraints are enforced via OPA Rego policies. These policies **cannot be overridden** by AI recommendations.

#### Policy Structure

```
policies/
├── security.rego      # Security hard constraints
├── deployment.rego    # Deployment gate policies
├── quality.rego       # Quality gate policies
└── compliance.rego    # Compliance requirements
```

#### Example: Security Policy (security.rego)

```rego
package cicd.security

# Deny deployment if critical CVEs exist
deny[msg] {
    input.scan.critical_count > 0
    msg := sprintf("Critical vulnerabilities found: %v. Deployment blocked.", [input.scan.critical_count])
}

# Deny if secrets are detected
deny[msg] {
    input.scan.secrets_detected == true
    msg := "Hardcoded secrets detected. Deployment blocked."
}

# Deny if authentication changes lack review
deny[msg] {
    input.changes.auth_modified == true
    input.review.security_approved == false
    msg := "Authentication changes require security team approval."
}
```

#### Policy Evaluation

Run policy evaluation before any AI recommendation:

```bash
# Evaluate policies against PR context
opa eval -d policies/ -i pr-context.json "data.cicd.security.deny"
```

**Rule:** If ANY policy denies, the action is blocked regardless of AI confidence score.

---

## Part 2: Trust Tier Framework

### Progressive Autonomy Model

AI agents operate at different trust levels based on proven accuracy:

| Tier | Name | Autonomy | Trigger Condition |
|------|------|----------|-------------------|
| **T0** | Advisory | Read-only recommendations | Initial deployment, < 70% accuracy |
| **T1** | Comment | Post comments on PRs | 70-80% accuracy over 100 decisions |
| **T2** | Act | Apply safe fixes, label PRs | 80-90% accuracy over 500 decisions |
| **T3** | Full | Approve, merge, rollback | > 90% accuracy over 1000+ decisions |

### Tier Escalation Criteria

```json
{
  "tier_thresholds": {
    "T0_to_T1": {
      "min_decisions": 100,
      "min_accuracy": 0.70,
      "min_precision": 0.75,
      "audit_period_days": 30
    },
    "T1_to_T2": {
      "min_decisions": 500,
      "min_accuracy": 0.80,
      "min_precision": 0.85,
      "audit_period_days": 60
    },
    "T2_to_T3": {
      "min_decisions": 1000,
      "min_accuracy": 0.90,
      "min_precision": 0.92,
      "audit_period_days": 90,
      "requires_human_approval": true
    }
  }
}
```

### Current Tier Actions

| Action | T0 | T1 | T2 | T3 |
|--------|----|----|----|----|
| Post review comments | ❌ | ✅ | ✅ | ✅ |
| Apply auto-fixes | ❌ | ❌ | ✅ (safe only) | ✅ |
| Label PRs | ❌ | ❌ | ✅ | ✅ |
| Approve PR | ❌ | ❌ | ❌ | ✅ |
| Auto-merge | ❌ | ❌ | ❌ | ✅ |
| Trigger rollback | ❌ | ❌ | ❌ | ✅ |

---

## Part 3: Decision Logging

### Structured Decision Format (SOC 2/ISO 27001 Compliant)

Every AI decision is logged in JSON format for auditability:

```json
{
  "decision_id": "uuid-v4",
  "timestamp": "2025-08-16T14:32:00Z",
  "decision_type": "PR_REVIEW | SECURITY_GATE | CANARY_PROMOTION | ROLLBACK",
  "agent_id": "pr-code-reviewer-v2",
  "agent_version": "2.0.0",
  "model": "claude-sonnet-4-5-20250929",
  "trust_tier": "T2",

  "input": {
    "pr_number": 1234,
    "repository": "org/repo",
    "files_changed": 15,
    "lines_added": 450,
    "lines_deleted": 120
  },

  "analysis": {
    "issues_found": 3,
    "severity_breakdown": {
      "critical": 0,
      "high": 1,
      "medium": 2,
      "low": 5
    },
    "security_scan_result": "pass",
    "test_coverage_delta": "+2.5%"
  },

  "policy_evaluation": {
    "policy_file": "security.rego",
    "result": "allow",
    "denied_rules": []
  },

  "confidence_score": 0.87,
  "decision": "APPROVE_WITH_SUGGESTIONS",

  "action_taken": {
    "comments_posted": 3,
    "labels_applied": ["ready-for-review", "security-reviewed"],
    "auto_fixes_applied": 1
  },

  "human_override": false,
  "override_reason": null
}
```

### Decision Log Storage

```bash
# Append to decision log
echo '{"decision_id":"..."}' >> .ai-cicd/decisions/YYYY-MM-DD.jsonl

# Query decisions
jq 'select(.decision_type == "SECURITY_GATE" and .confidence_score < 0.8)' .ai-cicd/decisions/*.jsonl
```

---

## Part 4: Review Workflow

### Phase 1: Load PR Context

```
1. Run code-reviewer plugin to load full PR diff
2. Fetch all review threads (open and resolved)
3. Identify unresolved threads requiring action
4. Detect technology stack using scripts/detect-stack.py
5. Load relevant reference checklists based on detected stack
6. Evaluate OPA policies against PR context
7. Determine current trust tier
```

**Stack Detection:** Run `python3 scripts/detect-stack.py` to identify:
- Primary language(s)
- Framework(s) in use
- Test framework(s)
- Build system
- Security tools configured

### Phase 2: Policy Gate Check

Before proceeding with AI analysis, verify policy compliance:

```bash
# Generate PR context for policy evaluation
python3 scripts/generate-policy-context.py --pr $PR_NUMBER > /tmp/pr-context.json

# Evaluate all policies
opa eval -d policies/ -i /tmp/pr-context.json "data.cicd"
```

**If ANY policy denies:**
1. Log the denial with decision_id
2. Post blocking comment on PR
3. Do NOT proceed with AI recommendations
4. Require human intervention

### Phase 3: Resolve Existing Comments

For each open review thread, classify and respond:

#### Comment Classification

| Type | Auto-Fix? | Trust Tier Required | Action |
|------|-----------|---------------------|--------|
| Bug | Yes (if safe) | T2+ | Fix directly, add regression test |
| Style/formatting | Yes | T1+ | Apply formatter, resolve thread |
| Naming | Yes | T1+ | Rename with IDE refactoring |
| Missing test | Yes | T2+ | Add test covering the case |
| Security issue | **No** | T3 (comment only) | Reply with severity, recommend fix |
| Performance concern | Maybe | T2+ | Profile first, then decide |
| Documentation gap | Yes | T1+ | Add/update docs |
| Architecture concern | **No** | T3 (comment only) | Reply with trade-off analysis |

#### Decision Framework

**Implement directly when:**
- Change is localized (< 20 lines)
- No architecture impact
- Aligns with existing repository patterns
- Test coverage can be added
- No security sensitivity
- Trust tier >= T2

**Reply without editing when:**
- Non-trivial design trade-off required
- Product decision needed
- Public API contract affected
- Database schema migration required
- Security-sensitive logic involved
- Breaking change potential
- Trust tier < required tier

### Phase 4: AI Agent Coordination

Invoke specialized agents based on PR content:

| Agent | Trigger | Purpose |
|-------|---------|---------|
| **Test-Triage Agent** | Test failures detected | Classify flaky vs regression, suggest retries |
| **Security Agent** | Security-sensitive changes | Summarize CVEs, enforce risk gates |
| **Observability Agent** | Performance-critical paths | Evaluate canary health against SLOs |
| **Feature-Flag Agent** | Feature flag changes | Tune ramp percentages based on metrics |
| **Postmortem Agent** | Incident-related PRs | Generate timelines, suggest remediation |

See `references/agent-coordination.md` for detailed agent invocation patterns.

### Phase 5: Fresh Holistic Review

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

### Phase 6: Test Validation

**Requirement:** New features MUST include tests. Bug fixes SHOULD include regression tests.

#### Flaky Test Detection (Test-Triage Agent)

```python
# Classify test failure
if historical_pass_rate < 0.85:
    classification = "LIKELY_FLAKY"
    action = "QUARANTINE_AND_RETRY"
elif code_changed_in_failure_path:
    classification = "CODE_REGRESSION"
    action = "BLOCK_AND_FIX"
else:
    classification = "ENVIRONMENT_ISSUE"
    action = "INVESTIGATE_INFRA"
```

### Phase 7: Canary Analysis Integration

For PRs affecting production services:

```yaml
# canary-analysis-config.yaml
canary:
  analysis:
    interval: 1m
    threshold: 0.95
    max_weight: 30
    step_weight: 5

  metrics:
    - name: request-success-rate
      threshold_range:
        min: 99.9
    - name: request-duration-p99
      threshold_range:
        max: 200ms

  decision:
    confidence_threshold: 0.8
    action_on_failure: rollback
```

**Observability Agent Integration:**
- Connects to Prometheus/Datadog
- Evaluates canary health against SLOs
- If confidence > 0.8 that canary is failing, triggers rollback

### Phase 8: Structured Output

Produce final review using `assets/review-template.md` with decision log entry:

```markdown
## Code Review Summary
**PR:** [PR number and title]
**Overall Assessment:** Approve / Request Changes / Comment
**Stack Detected:** [languages/frameworks]
**Trust Tier:** [T0-T3]
**Decision ID:** [uuid for audit trail]
**Policy Evaluation:** [allow/deny with rules]
**Confidence Score:** [0.0-1.0]

### Key Changes
[Brief summary of what this PR accomplishes]

## Critical Issues (Blocking)
| Issue | Location | Severity | Action Required |
|-------|----------|----------|-----------------|
| [Description] | file:line | CRITICAL | Must fix before merge |

## Policy Compliance
| Policy | Status | Notes |
|--------|--------|-------|
| security.rego | ✅ PASS | No critical CVEs |
| deployment.rego | ✅ PASS | All gates satisfied |

## Agent Findings
| Agent | Finding | Confidence | Action |
|-------|---------|------------|--------|
| Test-Triage | Flaky test detected | 0.87 | Quarantine |
| Security | CVE-2025-1234 in deps | 0.92 | Update required |

## Decision Log
```json
{
  "decision_id": "...",
  "confidence_score": 0.87,
  "decision": "APPROVE_WITH_SUGGESTIONS"
}
```

## Recommendation
[Final merge recommendation with any conditions]
```

---

## Part 5: Automated Canary Analysis (ACA)

### Integration with Argo Rollouts / Spinnaker

```yaml
# argo-rollouts-analysis.yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: ai-canary-analysis
spec:
  metrics:
  - name: success-rate
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          sum(rate(http_requests_total{status!~"5.."}[1m])) /
          sum(rate(http_requests_total[1m]))
    successCondition: result[0] >= 0.999

  - name: ai-confidence
    provider:
      job:
        spec:
          template:
            spec:
              containers:
              - name: ai-analyzer
                image: ai-cicd/observability-agent:latest
                command: ["./analyze-canary"]
                args: ["--confidence-threshold", "0.8"]
    successCondition: result.confidence >= 0.8
```

### Rollback Decision Logic

```python
def evaluate_canary(metrics, slo_thresholds):
    """
    Observability Agent evaluates canary health.
    Triggers automatic rollback if confidence > 0.8 that canary is failing.
    """
    failing_slos = []

    for metric, value in metrics.items():
        threshold = slo_thresholds.get(metric)
        if threshold and not threshold_satisfied(value, threshold):
            failing_slos.append({
                "metric": metric,
                "value": value,
                "threshold": threshold,
                "severity": "HIGH" if value < threshold * 0.9 else "MEDIUM"
            })

    confidence = calculate_failure_confidence(failing_slos)

    decision = {
        "decision_id": str(uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "decision_type": "CANARY_PROMOTION",
        "agent_id": "observability-agent",
        "confidence_score": confidence,
        "failing_slos": failing_slos,
        "decision": "ROLLBACK" if confidence > 0.8 else "PROMOTE"
    }

    log_decision(decision)

    if decision["decision"] == "ROLLBACK":
        trigger_rollback()
        notify_team(decision)

    return decision
```

---

## Severity Classification

See `references/severity-classification.md` for complete definitions.

| Level | Criteria | Merge Impact | Policy Gate |
|-------|----------|--------------|-------------|
| CRITICAL | Security vulnerability, data corruption risk, production breakage | BLOCKS merge | security.rego |
| HIGH | Missing tests, edge case bugs, poor error handling | Strongly recommend fix | quality.rego |
| MEDIUM | Maintainability risk, minor bugs, code smell | Should address | - |
| LOW | Style improvement, minor refactor, docs | Nice to have | - |

---

## Guardrails

- **Policy First:** OPA policies are absolute - AI cannot override
- **Trust Tiers:** Actions limited by proven accuracy
- **Decision Logging:** Every action logged for compliance
- **Minimal edits:** Prefer targeted fixes over refactors
- **No large refactors:** Save for dedicated PRs
- **Follow patterns:** Match existing repository conventions
- **Avoid noise:** Don't leave trivial comments
- **Comment when uncertain:** Don't auto-edit risky areas
- **Never auto-merge without T3:** Always require human approval at lower tiers
- **Security first:** When in doubt, block and escalate
- **Canary safety:** Rollback if confidence > 0.8 that canary is failing

---

## Resources

### scripts/
- `detect-stack.py` - Identifies languages, frameworks, and build tools in the PR
- `generate-policy-context.py` - Generates JSON context for OPA policy evaluation
- `log-decision.py` - Appends decision to audit log in JSON format
- `evaluate-canary.py` - Observability Agent canary health check

### references/
- `security-checklist.md` - OWASP-based security review checklist
- `testing-standards.md` - Test coverage and quality requirements
- `performance-checklist.md` - Performance anti-patterns and optimizations
- `severity-classification.md` - Detailed severity definitions and examples
- `agent-coordination.md` - Multi-agent invocation patterns
- `trust-tier-framework.md` - Trust tier escalation criteria
- `opa-policies.md` - OPA Rego policy reference

### assets/
- `review-template.md` - Copy-paste template for structured review output
- `decision-log-schema.json` - JSON schema for decision logging

### policies/
- `security.rego` - Security hard constraints
- `deployment.rego` - Deployment gate policies
- `quality.rego` - Quality gate policies
- `compliance.rego` - Compliance requirements

---

## Success Criteria

- [ ] All unresolved comments processed
- [ ] No unaddressed critical issues
- [ ] OPA policy evaluation passed
- [ ] Test coverage maintained or improved
- [ ] Security scan completed
- [ ] Decision logged with full audit trail
- [ ] Trust tier actions respected
- [ ] Review summary posted
- [ ] Clear next steps documented
- [ ] Threads resolved with explanations

---

## Metrics (DORA + AI-Specific)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Lead Time | -25% | Time from commit to production |
| MTTR | -26% | Mean time to recovery |
| Agent Accuracy | >90% | Correct decisions / total decisions |
| False Positive Rate | <5% | Incorrect blocks / total blocks |
| Policy Coverage | 100% | All critical paths gated |
| Decision Audit Trail | 100% | All decisions logged |
