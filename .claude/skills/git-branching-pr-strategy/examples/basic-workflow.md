# Basic Workflow Examples

This guide demonstrates typical workflows using the Git Branching and PR Strategy skill.

## Example 1: Feature Development

### Step 1: Create a Feature Branch
```bash
/feature PROJ-123 Add user authentication system
```

**Output:**
```
✅ Synced with main branch
✅ Created branch: feature/PROJ-123-add-user-authentication-system
```

### Step 2: Implement Your Changes
```bash
# Make your code changes
git add .
git commit -m "feat: implement user authentication"
git commit -m "feat: add JWT token handling"
git commit -m "test: add authentication unit tests"
```

### Step 3: Validate Branch Before PR
```bash
/validate_branch
```

**Output:**
```
✅ Validating branch...
✅ Branch validation passed
✅ Running linting checks...
✅ Linting passed (ESLint)
✅ Running test suite...
✅ Tests passed (npm test)
✅ Coverage check passed: 85% (npm test:coverage)
✅ All quality gates passed
✅ Branch feature/PROJ-123-add-user-authentication-system is ready for PR
```

### Step 4: Create Pull Request
```bash
/create_pr --title "✨ PROJ-123: Add user authentication system"
```

**Output:**
```
✅ Pushing branch feature/PROJ-123-add-user-authentication-system...
✅ Branch pushed: feature/PROJ-123-add-user-authentication-system
✅ Creating GitHub PR...
✅ GitHub PR created
✅ Pull Request created: https://github.com/your-org/your-repo/pull/45
✅ Title: ✨ PROJ-123: Add user authentication system
```

### Step 5: Review and Merge
```bash
/review_pr
```

**Output:**
```
ℹ PR Status for feature/PROJ-123-add-user-authentication-system:
ℹ State: OPEN
ℹ Mergeable: true
ℹ Review Decision: APPROVED
ℹ URL: https://github.com/your-org/your-repo/pull/45
```

```bash
/merge_pr --method squash --delete-branch
```

**Output:**
```
✅ Merging Pull Request...
✅ Pull Request merged
✅ PR merged for branch: feature/PROJ-123-add-user-authentication-system
```

## Example 2: Bug Fix Workflow

### Step 1: Create Bugfix Branch
```bash
/bugfix BUG-124 Fix login validation error
```

### Step 2: Implement Fix
```bash
# Fix the bug
git add .
git commit -m "fix: resolve login validation edge case"
git commit -m "test: add regression test for login validation"
```

### Step 3: Quick Validation
```bash
/validate_branch
```

### Step 4: Create PR
```bash
/create_pr --description "Fixes the login validation issue where users with special characters in passwords were incorrectly rejected. Includes regression tests."
```

## Example 3: Hotfix Process

### Step 1: Create Hotfix Branch
```bash
/hotfix HOT-125 Fix critical security vulnerability
```

### Step 2: Implement Minimal Fix
```bash
# Implement critical fix
git add .
git commit -m "hotfix: patch XSS vulnerability in user input"
```

### Step 3: Expedited Validation
```bash
/validate_branch
```

### Step 4: Create and Merge PR
```bash
/create_pr --draft --title "🚨 HOT-125: Critical security patch"
/create_pr --ready  # Convert to ready PR
/merge_pr --method merge
```

## Example 4: Working with Draft PRs

### Create Draft PR for Early Feedback
```bash
/create_pr --draft --title "WIP: Payment integration"
```

### Update PR When Ready
```bash
# Continue working...
git add .
git commit -m "feat: complete payment integration"
git commit -m "test: add payment flow tests"

/create_pr --ready --title "✨ PROJ-126: Implement payment integration"
```

## Example 5: Branch Management

### Check Current Status
```bash
/status
```

**Output:**
```
=== Git Status ===
Current Branch: feature/PROJ-123-add-user-authentication-system
Working Directory: Clean
Ahead: 3 commits
Behind: 0 commits

=== Branch Memory ===
Type: feature
Issue ID: PROJ-123
Created: 11/18/2024
PR: https://github.com/your-org/your-repo/pull/45

=== Statistics ===
Total Branches: 5
Active: 3
Merged: 2
Archived: 0
```

### Sync with Main Branch
```bash
/sync_branch
```

**Output:**
```
✅ Syncing with main branch...
✅ Synced with main branch
✅ Current branch synced with main
```

### Clean Up Old Branches
```bash
/cleanup_branches --older-than 30d
```

**Output:**
```
✅ Cleaning up stale branches...
✅ Cleaned up 2 Git branches and 1 memory entries
```

## Example 6: Quality Gate Failures

### When Linting Fails
```bash
/validate_branch
```

**Output:**
```
✖ Linting failed
✖ Branch validation failed:
  - Linting check failed: ESLint found 2 errors
```

**Solution:** Fix linting errors:
```bash
npm run lint -- --fix
```

### When Tests Fail
```bash
/validate_branch
```

**Output:**
```
✖ Tests failed (npm test)
✖ Quality gates failed:
  - Tests check failed: Test failures: 2 test(s) failed
```

**Solution:** Fix failing tests:
```bash
npm test
# Check test output and fix issues
```

### When Coverage is Too Low
```bash
/validate_branch
```

**Output:**
```
✖ Coverage check failed: 75% < 80%
✖ Quality gates failed:
  - Coverage check failed: Coverage 75% is below required 80%
```

**Solution:** Add more tests or adjust coverage requirement in config.

## Example 7: Working with Different Branch Types

### Feature Branch
```bash
/feature PROJ-127 Implement search functionality
```

### Bugfix Branch
```bash
/bugfix BUG-128 Fix search result pagination
```

### Release Branch
```bash
# Manually create release branch for versioning
git checkout -b release/v1.2.0
```

### Hotfix Branch
```bash
/hotfix HOT-129 Fix critical search performance issue
```

## Example 8: Advanced PR Options

### Create PR with Custom Options
```bash
/create_pr \
  --title "🚀 PROJ-130: Advanced search with filters" \
  --description "Implements advanced search functionality including:
- Category filtering
- Price range filtering
- Date-based filtering
- Saved search preferences

Tests cover all filter combinations and edge cases." \
  --draft
```

### Merge with Specific Method
```bash
# Squash merge (default)
/merge_pr --method squash --delete-branch

# Regular merge
/merge_pr --method merge

# Rebase merge
/merge_pr --method rebase
```

## Example 9: Troubleshooting

### Branch Already Exists
```bash
/feature PROJ-123 Add user authentication
```

**Error:**
```
✖ Failed to create feature branch: Branch 'feature/PROJ-123-add-user-authentication' already exists
```

**Solution:** Use different description or switch to existing branch:
```bash
git checkout feature/PROJ-123-add-user-authentication
```

### GitHub CLI Not Authenticated
```bash
/create_pr
```

**Error:**
```
✖ Failed to create Pull Request: Not in a git repository or GitHub CLI not authenticated
```

**Solution:** Authenticate GitHub CLI:
```bash
gh auth login
```

### Working Directory Not Clean
```bash/validate_branch
```

**Error:**
```
✖ Branch validation failed:
  - Working directory is not clean
```

**Solution:** Commit or stash changes:
```bash
git add .
git commit -m "WIP: save progress"
# or
git stash
```

These examples demonstrate the typical workflows and how to handle common scenarios when using the Git Branching and PR Strategy skill.
