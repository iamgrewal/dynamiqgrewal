# Trust Tier Framework

Progressive autonomy model for AI-augmented CI/CD pipelines.

## Overview

The Trust Tier Framework defines four levels of AI agent autonomy, progressing from read-only recommendations (T0) to full autonomous decision-making (T3). Agents must demonstrate consistent accuracy before advancing tiers.

## Tier Definitions

### Tier 0: Advisory (Read-Only)

**Description:** Initial deployment phase. Agent can only observe and generate reports.

**Allowed Actions:**
- Read PR context
- Generate analysis reports
- Provide recommendations (not visible to users)

**Prohibited Actions:**
- Post comments
- Modify code
- Approve/merge PRs
- Trigger deployments

**Escalation to T1:**
- Minimum 100 decisions logged
- Accuracy >= 70%
- Precision >= 75%
- 30-day audit period with no critical errors

### Tier 1: Comment

**Description:** Agent can post comments on PRs but cannot make changes.

**Allowed Actions:**
- All T0 actions
- Post review comments
- Suggest code changes (as suggestions, not edits)

**Prohibited Actions:**
- Apply code changes
- Label PRs
- Approve/merge PRs
- Trigger deployments

**Escalation to T2:**
- Minimum 500 decisions logged
- Accuracy >= 80%
- Precision >= 85%
- 60-day audit period
- No false negatives on security issues

### Tier 2: Act

**Description:** Agent can apply safe fixes and label PRs.

**Allowed Actions:**
- All T1 actions
- Apply auto-fixes (whitelisted categories only)
- Label PRs with predefined labels
- Trigger test re-runs

**Prohibited Actions:**
- Approve/merge PRs
- Trigger production deployments
- Modify security-sensitive code
- Bypass policy gates

**Safe Fix Categories:**
- Formatting (Prettier, Black, etc.)
- Import organization
- Simple refactoring (rename, extract variable)
- Documentation updates
- Test additions

**Escalation to T3:**
- Minimum 1000 decisions logged
- Accuracy >= 90%
- Precision >= 92%
- 90-day audit period
- Explicit human approval required
- No critical errors in last 30 days

### Tier 3: Full Autonomy

**Description:** Agent has full decision-making authority including merge approval.

**Allowed Actions:**
- All T2 actions
- Approve PRs
- Auto-merge (with conditions)
- Trigger deployments
- Rollback deployments
- Modify any code category

**Prohibited Actions:**
- Override OPA policy denials
- Bypass human approval for security changes

**Conditions for Auto-Merge:**
- All policy gates pass
- No unresolved comments
- All CI checks pass
- Confidence score >= 0.90
- Not a security-sensitive change

## Accuracy Metrics

### Calculation

```
Accuracy = (True Positives + True Negatives) / Total Decisions

Precision = True Positives / (True Positives + False Positives)

Recall = True Positives / (True Positives + False Negatives)

F1 Score = 2 * (Precision * Recall) / (Precision + Recall)
```

### Decision Categories

| Category | True Positive | False Positive | True Negative | False Negative |
|----------|--------------|----------------|---------------|----------------|
| Security Issue | Correctly identified | Incorrectly flagged | Correctly passed | Missed vulnerability |
| Test Failure | Correctly classified | Incorrectly blocked | Correctly passed | Missed regression |
| Code Quality | Correctly suggested | Unnecessary suggestion | Correctly passed | Missed issue |

### Severity Weighting

```
Weighted Accuracy = Σ (Decision_Weight * Accuracy_Category) / Σ Decision_Weight

Weights:
- CRITICAL: 10
- HIGH: 5
- MEDIUM: 2
- LOW: 1
```

## Tier Management

### Promotion Process

```yaml
tier_promotion:
  trigger: "Agent meets all criteria for next tier"

  steps:
    - name: verify_metrics
      action: Query decision log for accuracy metrics

    - name: audit_review
      action: Human review of sample decisions
      sample_size: 50
      require_approval: true

    - name: security_review
      action: Security team review of agent permissions
      required_for: T2, T3

    - name: update_config
      action: Update agent configuration with new tier

    - name: notify_stakeholders
      action: Send notification to platform and security teams

    - name: log_promotion
      action: Record promotion in audit log
```

### Demotion Process

```yaml
tier_demotion:
  triggers:
    - "False negative on security issue"
    - "Accuracy drops below tier threshold for 7 consecutive days"
    - "Critical error causing production impact"
    - "Human override of 3+ decisions in 24 hours"

  steps:
    - name: immediate_demotion
      action: Reduce tier by 1 level immediately

    - name: incident_report
      action: Generate incident report

    - name: root_cause_analysis
      action: Analyze what went wrong

    - name: remediation
      action: Fix underlying issue

    - name: re_qualification
      action: Agent must re-qualify for higher tier
```

## Audit Requirements

### Decision Log Retention

| Tier | Retention Period | Storage |
|------|-----------------|---------|
| T0 | 30 days | Standard |
| T1 | 90 days | Standard |
| T2 | 1 year | Compliance |
| T3 | 3 years | Compliance + Immutable |

### Audit Trail

Every decision must include:
- Decision ID (UUID)
- Timestamp (ISO 8601)
- Agent ID and version
- Trust tier at time of decision
- Model used
- Input context
- Analysis performed
- Confidence score
- Final decision
- Policy evaluation result
- Human override (if any)

### Compliance Reporting

```yaml
compliance_reports:
  - name: daily_accuracy
    frequency: daily
    recipients: [platform-team]

  - name: weekly_audit
    frequency: weekly
    recipients: [platform-team, security-team]

  - name: monthly_compliance
    frequency: monthly
    recipients: [platform-team, security-team, compliance]
    format: SOC2/ISO27001 compliant
```

## Implementation Checklist

### Tier 0 Setup
- [ ] Agent registered in configuration
- [ ] Decision logging enabled
- [ ] Audit trail configured
- [ ] Initial metrics baseline established

### Tier 1 Setup
- [ ] GitHub/GitLab API permissions for comments
- [ ] Comment templates configured
- [ ] Suggestion format validated
- [ ] Notification routing configured

### Tier 2 Setup
- [ ] Write permissions for safe categories
- [ ] Label management permissions
- [ ] CI trigger permissions
- [ ] Safe category whitelist configured

### Tier 3 Setup
- [ ] Full repository permissions
- [ ] Deployment trigger permissions
- [ ] Rollback permissions
- [ ] Security team approval documented
- [ ] Incident response procedures documented
