# Multi-Agent Coordination Patterns

This document defines how the PR Code Reviewer coordinates with specialized CI/CD agents.

## Agent Registry

| Agent | Skill | Trigger | Confidence Threshold |
|-------|-------|---------|---------------------|
| Test-Triage Agent | test_triage_skill | Test failure detected | 0.70 |
| Security Agent | security_gate_skill | Security-sensitive changes | 0.85 |
| Observability Agent | canary_analysis_skill | Production deployment | 0.80 |
| Feature-Flag Agent | feature_flag_tuning_skill | Feature flag changes | 0.75 |
| Postmortem Agent | incident_analysis_skill | Incident-related PRs | 0.70 |

## Coordination Workflow

### 1. PR Classification

```python
def classify_pr(changes):
    """Classify PR type to determine which agents to invoke."""
    classifications = []

    if changes.has_test_failures:
        classifications.append("TEST_TRIAGE")

    if changes.modifies_auth or changes.modifies_crypto or changes.has_cves:
        classifications.append("SECURITY")

    if changes.affects_production or changes.is_deployment:
        classifications.append("OBSERVABILITY")

    if changes.modifies_feature_flags:
        classifications.append("FEATURE_FLAG")

    if changes.related_to_incident:
        classifications.append("POSTMORTEM")

    return classifications
```

### 2. Agent Invocation Pattern

```yaml
# agent-invocation.yaml
workflow:
  - name: classify
    agent: pr-code-reviewer
    outputs: [classifications]

  - name: parallel-analysis
    parallel:
      - agent: test-triage
        condition: "TEST_TRIAGE in classifications"
        trust_tier: T1
      - agent: security
        condition: "SECURITY in classifications"
        trust_tier: T2
      - agent: observability
        condition: "OBSERVABILITY in classifications"
        trust_tier: T2

  - name: aggregate-findings
    agent: pr-code-reviewer
    inputs: [parallel-analysis.outputs]

  - name: policy-evaluation
    engine: opa
    policies: [security, deployment, quality]

  - name: decision
    agent: pr-code-reviewer
    inputs: [aggregate-findings, policy-evaluation]
    outputs: [final_decision, decision_log]
```

### 3. Agent Communication Protocol

```json
{
  "message_id": "uuid-v4",
  "timestamp": "2025-08-16T14:32:00Z",
  "source_agent": "pr-code-reviewer",
  "target_agent": "security-agent",
  "message_type": "ANALYSIS_REQUEST",
  "payload": {
    "pr_number": 1234,
    "files_changed": ["auth/login.ts", "auth/middleware.ts"],
    "classification": "SECURITY",
    "context": {
      "auth_modified": true,
      "crypto_modified": false,
      "dependencies_changed": []
    }
  },
  "required_confidence": 0.85,
  "timeout_seconds": 60
}
```

### 4. Agent Response Format

```json
{
  "message_id": "uuid-v4",
  "timestamp": "2025-08-16T14:32:30Z",
  "source_agent": "security-agent",
  "target_agent": "pr-code-reviewer",
  "message_type": "ANALYSIS_RESPONSE",
  "payload": {
    "findings": [
      {
        "id": "SEC-001",
        "type": "AUTHENTICATION",
        "severity": "HIGH",
        "location": "auth/login.ts:45",
        "description": "Missing rate limiting on login endpoint",
        "recommendation": "Add rate limiting middleware",
        "confidence": 0.92
      }
    ],
    "overall_risk": "MEDIUM",
    "blocks_deployment": false,
    "requires_human_review": true
  },
  "confidence_score": 0.92,
  "processing_time_ms": 2340
}
```

### 5. Conflict Resolution

When agents provide conflicting recommendations:

```python
def resolve_conflicts(agent_findings):
    """
    Resolve conflicts between agent recommendations.

    Priority: Security > Observability > Test-Triage > Feature-Flag > Postmortem
    """
    priority_order = [
        "security-agent",
        "observability-agent",
        "test-triage-agent",
        "feature-flag-agent",
        "postmortem-agent"
    ]

    # Group findings by topic
    grouped = group_by_topic(agent_findings)

    # For each topic, use highest priority agent's recommendation
    resolved = {}
    for topic, findings in grouped.items():
        for agent in priority_order:
            if agent in findings:
                resolved[topic] = findings[agent]
                break

    return resolved
```

### 6. Escalation Protocol

```yaml
escalation_rules:
  - condition: "any_agent.confidence < 0.70"
    action: require_human_review
    notify: [security-team, platform-team]

  - condition: "security-agent.blocks_deployment == true"
    action: block_merge
    notify: [security-team]

  - condition: "all_agents.confidence > 0.90 and policy.allows == true"
    action: auto_approve
    trust_tier: T3
```

## Agent Definitions

### Test-Triage Agent

**Purpose:** Identifies flaky tests and suggests retries or quarantines.

**Inputs:**
- Test failure logs
- Historical pass rates
- Code changes in failure paths

**Outputs:**
- Classification: FLAKY / REGRESSION / ENVIRONMENT
- Recommended action: RETRY / QUARANTINE / BLOCK
- Confidence score

### Security Agent

**Purpose:** Summarizes CVEs and enforces risk-based gates.

**Inputs:**
- Dependency changes
- Authentication/authorization code changes
- CVE database

**Outputs:**
- CVE summary with severity
- Risk assessment
- Deployment gate decision

### Observability Agent

**Purpose:** Evaluates canary health against SLOs.

**Inputs:**
- Canary metrics (Prometheus/Datadog)
- SLO thresholds
- Historical baseline

**Outputs:**
- Health assessment
- Promotion/rollback recommendation
- Confidence score

### Feature-Flag Agent

**Purpose:** Dynamically tunes ramp percentages.

**Inputs:**
- Feature flag configuration
- Error rates
- User feedback metrics

**Outputs:**
- Recommended ramp percentage
- Risk assessment
- Rollback threshold

### Postmortem Agent

**Purpose:** Generates incident timelines and remediation PRs.

**Inputs:**
- Incident data
- Related PRs and commits
- Timeline events

**Outputs:**
- Incident timeline
- Root cause analysis
- Remediation recommendations
