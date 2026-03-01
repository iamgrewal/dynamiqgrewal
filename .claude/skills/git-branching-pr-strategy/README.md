# Git Branching and PR Strategy Skill

A comprehensive Claude skill for automating Git branching workflows, Pull Request management, and enforcing quality gates in Trunk-Based Development and GitHub Flow environments.

## 🚀 Features

### Core Workflow Automation
- **Intelligent Branch Creation**: Automated branch naming with issue ID integration
- **PR Creation**: Automatic template filling with commit history and changed files
- **Quality Gates**: Configurable linting, testing, build, and security validation
- **Branch Memory**: Smart tracking of branch lifecycle and metadata

### Supported Branch Types
- **Feature Branches**: `/feature PROJ-123 Add user authentication`
- **Bugfix Branches**: `/bugfix PROJ-124 Fix login validation`
- **Hotfix Branches**: `/hotfix PROJ-125 Critical security patch`

### Quality Gates
- **Linting**: ESLint, Prettier, Flake8, Ruff support
- **Testing**: Jest, Vitest, pytest, Go test, Cargo test
- **Build**: npm, yarn, pnpm, Go build, Cargo build
- **Security**: npm audit, safety, bandit, gosec
- **Coverage**: Configurable minimum coverage requirements

### Integrations
- **GitHub**: PR creation, status checks, merge automation
- **Jira**: Issue linking and metadata sync
- **Linear**: Issue tracking integration

## 📦 Installation

1. **Clone to Claude Skills Directory**
```bash
git clone <repository-url> ~/.claude/skills/git-branching-pr-strategy
cd ~/.claude/skills/git-branching-pr-strategy
```

2. **Install Dependencies**
```bash
npm install
```

3. **Configure Project**
```bash
cp config/project.json.example config/project.json
# Edit config/project.json with your settings
```

4. **Install GitHub CLI** (recommended)
```bash
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# Other platforms: https://cli.github.com/manual/installation
```

5. **Authenticate GitHub CLI**
```bash
gh auth login
```

## ⚙️ Configuration

### Basic Configuration

Edit `config/project.json`:

```json
{
  "mainBranch": "main",
  "developBranch": "develop",
  "branchPrefix": {
    "feature": "feature/",
    "bugfix": "bugfix/",
    "hotfix": "hotfix/",
    "release": "release/"
  },
  "prTemplate": ".github/PULL_REQUEST_TEMPLATE.md",
  "requireIssueLink": true,
  "autoSync": true,
  "maxBranchAge": "30d",
  "enforceConventionalCommits": true,
  "requireTestCoverage": true,
  "minTestCoverage": 80,
  "qualityGates": {
    "lintRequired": true,
    "testsRequired": true,
    "buildRequired": true,
    "securityScan": true
  }
}
```

### Quality Gates Configuration

Configure which quality checks are required:

```json
{
  "qualityGates": {
    "lintRequired": true,
    "testsRequired": true,
    "buildRequired": true,
    "securityScan": false
  }
}
```

### GitHub Integration

Configure GitHub-specific settings:

```json
{
  "integrations": {
    "github": {
      "enabled": true,
      "autoAssignReviewers": true,
      "requireApprovals": 1,
      "autoMerge": false,
      "mergeMethod": "squash"
    }
  }
}
```

## 🎯 Usage

### Basic Workflow

#### 1. Create a Feature Branch
```bash
/feature PROJ-456 Add user authentication system
```

#### 2. Work on Your Changes
```bash
# Make your changes...
git add .
git commit -m "feat: implement user authentication"
```

#### 3. Validate Branch Before PR
```bash
/validate_branch
```

#### 4. Create Pull Request
```bash
/create_pr --title "✨ PROJ-456: Add user authentication"
```

#### 5. Review and Merge
```bash
/review_pr
/merge_pr --method squash --delete-branch
```

### Advanced Usage

#### Create Draft PR
```bash
/create_pr --draft --title "WIP: Authentication feature"
```

#### Update Existing PR
```bash
/create_pr --title "Updated title" --ready
```

#### Sync with Main Branch
```bash
/sync_branch
```

#### Clean Up Old Branches
```bash
/cleanup_branches --older-than 30d
```

#### Check Status
```bash
/status
```

## 🔧 Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `feature <issue-id> <description>` | Create feature branch | `/feature PROJ-123 Add user login` |
| `bugfix <issue-id> <description>` | Create bugfix branch | `/bugfix PROJ-124 Fix validation` |
| `hotfix <issue-id> <description>` | Create hotfix branch | `/hotfix PROJ-125 Security fix` |
| `create_pr [options]` | Create pull request | `/create_pr --draft` |
| `review_pr [branch]` | Review PR status | `/review_pr feature/auth` |
| `merge_pr [branch] [options]` | Merge pull request | `/merge_pr --method squash` |
| `validate_branch [branch]` | Validate branch | `/validate_branch` |
| `sync_branch [branch]` | Sync with main | `/sync_branch` |
| `cleanup_branches [options]` | Clean old branches | `/cleanup_branches --older-than 30d` |
| `status` | Show current status | `/status` |

## 🎨 Command Options

### PR Creation Options
- `--title <title>`: Custom PR title
- `--description <text>`: Custom PR description
- `--draft`: Create draft PR
- `--ready`: Mark PR as ready for review

### Merge Options
- `--method <squash|merge|rebase>`: Merge method
- `--delete-branch`: Delete branch after merge

### Cleanup Options
- `--older-than <Nd>`: Branches older than N days
- `--dry-run`: Show what would be cleaned up

## 📊 Branch Memory

The skill maintains a memory of all branches with metadata:

- **Branch Information**: Type, issue ID, description
- **Activity Tracking**: Creation, last activity, merge dates
- **PR Links**: Automatic linking to pull requests
- **Statistics**: Branch counts, age distributions

### Memory Commands

```bash
# View branch statistics
/status

# Search branches
# (Available through the skill API)

# Export branch data
# (Available through the skill API)
```

## 🔄 Integration with Workflows

### Pre-commit Hooks

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Validate branch before commit
node ~/.claude/skills/git-branching-pr-strategy/index.js validate_branch
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
# GitHub Actions example
- name: Validate Branch
  run: |
    node ~/.claude/skills/git-branching-pr-strategy/index.js validate_branch

- name: Create PR
  if: github.event_name == 'push' && github.ref != 'refs/heads/main'
  run: |
    node ~/.claude/skills/git-branching-pr-strategy/index.js create_pr
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Team Workflows

#### Feature Development
1. Product manager creates issue in Jira/Linear
2. Developer creates branch: `/feature PROJ-123 Add feature`
3. Developer implements and tests changes
4. Automated validation: `/validate_branch`
5. Create PR: `/create_pr`
6. Code review and merge

#### Bug Fixes
1. Bug report created in issue tracker
2. Developer creates branch: `/bugfix BUG-456 Fix issue`
3. Fix implemented and tested
4. Quality gates validated
5. PR created and reviewed
6. Hotfix deployed if needed

#### Hotfix Process
1. Critical issue identified
2. Create hotfix branch: `/hotfix HOT-789 Security fix`
3. Minimal fix implemented
4. Quick validation and PR
5. Fast-track review and merge
6. Release to production

## 🛡️ Quality Gates

### Configurable Checks

#### Linting
- **JavaScript/TypeScript**: ESLint, Prettier
- **Python**: Flake8, Black, Ruff
- **Go**: gofmt, golint
- **Rust**: clippy, rustfmt

#### Testing
- **JavaScript**: Jest, Vitest, Mocha
- **Python**: pytest, unittest
- **Go**: go test
- **Rust**: cargo test

#### Security
- **Node.js**: npm audit, yarn audit
- **Python**: safety, bandit
- **Go**: gosec
- **General**: Snyk, GitHub security

#### Coverage
- Configurable minimum coverage percentage
- Support for multiple coverage formats
- Integration with CI/CD reporting

## 🐛 Troubleshooting

### Common Issues

#### Branch Creation Fails
```bash
Error: Branch 'feature/PROJ-123-add-feature' already exists
```
**Solution**: Use a different description or check existing branches.

#### GitHub CLI Not Found
```bash
Error: GitHub CLI (gh) is not installed
```
**Solution**: Install GitHub CLI from https://cli.github.com/

#### PR Creation Fails
```bash
Error: Not in a git repository or GitHub CLI not authenticated
```
**Solution**: Run `gh auth login` to authenticate.

#### Quality Gates Fail
```bash
Error: Linting failed
```
**Solution**: Fix linting errors or disable linting requirement in config.

### Debug Mode

Enable debug logging:
```bash
export GIT_SKILL_DEBUG=true
```

### Logs and Debugging

Check branch memory:
```bash
cat .git/branch-memory.json
```

Validate configuration:
```bash
node ~/.claude/skills/git-branching-pr-strategy/index.js status
```

## 🤝 Contributing

### Development Setup

1. **Fork and Clone**
```bash
git clone <your-fork>
cd git-branching-pr-strategy
npm install
```

2. **Run Tests**
```bash
npm test
```

3. **Lint Code**
```bash
npm run lint
```

### Adding New Features

1. **Create Feature Branch**
```bash
/feature NEW-123 Add new integration
```

2. **Implement Changes**
3. **Add Tests**
4. **Update Documentation**
5. **Create PR**

### Code Style

- Use ES6+ modules
- Follow conventional commits
- Add JSDoc comments
- Include error handling
- Write tests for new features

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by Trunk-Based Development principles
- Built with modern Node.js ecosystem
- Integrates with popular Git workflows
- Supports multiple programming languages

## 📞 Support

- **Issues**: Create an issue in the repository
- **Documentation**: See `/help` command
- **Examples**: Check the `examples/` directory

---

**Happy coding with automated Git workflows! 🚀**
