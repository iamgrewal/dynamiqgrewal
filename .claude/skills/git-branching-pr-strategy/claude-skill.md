# Git Branching and PR Strategy Skill

Automate, enforce, and optimize Git branching workflows with AI-driven automation for Trunk-Based Development and GitHub Flow.

## Overview

This skill provides comprehensive Git workflow automation including:
- Intelligent branch creation and management
- Automated Pull Request creation and management
- Quality gates and validation checks
- Branch memory management
- Integration with issue tracking systems

## Features

### Core Workflow Automation
- **Feature Branch Creation**: `/feature <issue-id> <description>`
- **Bugfix Branch Creation**: `/bugfix <issue-id> <description>`
- **Hotfix Branch Creation**: `/hotfix <issue-id> <description>`
- **PR Creation**: `/create_pr` with automatic template filling
- **Branch Validation**: `/validate_branch` for pre-commit checks
- **Branch Synchronization**: `/sync_branch` to keep branches updated

### Quality Gates
- Automated branch naming conventions
- Pre-commit validation checks
- PR template enforcement
- Test coverage requirements
- Code quality validation

### Memory Management
- Branch state tracking
- Issue-to-branch mapping
- Work progress memory
- Automated cleanup of stale branches

## Installation

1. Clone this skill to your Claude skills directory
2. Install dependencies: `npm install`
3. Configure your project settings in `config/`
4. Initialize the skill: `npm run setup`

## Configuration

### Project Setup
Edit `config/project.json`:
```json
{
  "mainBranch": "main",
  "branchPrefix": "feature/",
  "prTemplate": ".github/PULL_REQUEST_TEMPLATE.md",
  "requireIssueLink": true,
  "autoSync": true
}
```

### Branch Naming Rules
Edit `config/branch-rules.json`:
```json
{
  "feature": "feature/[JIRA-123]-short-description",
  "bugfix": "bugfix/[JIRA-124]-fix-description",
  "hotfix": "hotfix/[JIRA-125]-urgent-fix"
}
```

## Usage Examples

### Create a new feature branch
```bash
/feature PROJ-456 Add user authentication
```

### Create and submit a PR
```bash
/create_pr
```

### Validate current branch
```bash
/validate_branch
```

### Clean up stale branches
```bash
/cleanup_branches --older-than 30d
```

## Integration

This skill integrates with:
- GitHub CLI for PR management
- JIRA/Linear for issue tracking
- CI/CD pipelines for quality gates
- Git hooks for pre-commit validation

## Troubleshooting

### Common Issues
- **Branch naming conflicts**: Check `config/branch-rules.json`
- **PR creation failures**: Verify GitHub CLI authentication
- **Sync issues**: Ensure remote tracking is properly configured

### Debug Mode
Enable debug logging:
```bash
export GIT_SKILL_DEBUG=true
```

## Contributing

1. Fork the repository
2. Create a feature branch: `/feature NEW-123 add-new-feature`
3. Implement changes with tests
4. Create PR: `/create_pr`
5. Ensure all quality gates pass
