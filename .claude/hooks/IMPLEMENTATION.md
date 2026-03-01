# Svelte Hooks Implementation for Claude Code

This directory contains a complete implementation of Claude Code hooks specifically designed for Svelte/SvelteKit projects.

## 📁 Directory Structure

```
.claude/hooks/
├── scripts/              # Executable hook scripts
│   ├── svelte-validator.py        # Validates Svelte syntax
│   ├── format-and-lint.sh         # Formats and lints code
│   ├── typescript-check.py        # TypeScript type checking
│   ├── test-runner.sh             # Runs tests automatically
│   ├── bundle-size-check.py       # Monitors bundle size
│   ├── component-analyzer.py      # Analyzes component complexity
│   ├── bash-validator.py          # Validates bash commands
│   ├── prompt-enhancer.py         # Enhances user prompts
│   └── story-sync-check.sh        # Checks for Storybook stories
├── examples/             # Example configurations
│   ├── settings-minimal.json      # Basic setup
│   ├── settings-comprehensive.json # Full feature set
│   ├── settings-team.json         # Team collaboration
│   ├── settings-performance.json  # Performance focus
│   └── settings-storybook.json    # Storybook integration
├── install-svelte-hooks.sh        # Installation script
└── README.md                      # Documentation

```

## 🚀 Quick Installation

Run the installation script from your Svelte project root:

```bash
# Clone or download the hooks to a temporary location
curl -L https://github.com/your-repo/claude-svelte-hooks/archive/main.tar.gz | tar xz
cd claude-svelte-hooks-main

# Run the installer
./install-svelte-hooks.sh
```

The installer will:
1. Create `.claude/hooks/scripts/` directory
2. Copy all hook scripts
3. Help you choose a configuration preset
4. Check for required dependencies
5. Set up `.gitignore` entries

## 🔧 Manual Installation

1. **Copy hook scripts**:
   ```bash
   mkdir -p .claude/hooks/scripts
   cp -r /path/to/hooks/scripts/* .claude/hooks/scripts/
   chmod +x .claude/hooks/scripts/*.{py,sh}
   ```

2. **Choose a configuration**:
   ```bash
   cp /path/to/hooks/examples/settings-minimal.json .claude/settings.json
   ```

3. **Install dependencies**:
   ```bash
   npm install -D @sveltejs/cli prettier eslint typescript
   ```

## 📝 Hook Scripts Overview

### Core Validation Hooks

#### `svelte-validator.py`
- **Trigger**: PostToolUse on Write/Edit/MultiEdit
- **Purpose**: Validates Svelte syntax using `sv check`
- **Blocks on**: Svelte compilation errors

#### `format-and-lint.sh`
- **Trigger**: PostToolUse on Write/Edit/MultiEdit
- **Purpose**: Auto-formats with Prettier and lints with ESLint
- **Blocks on**: ESLint errors (warnings are shown but don't block)

#### `typescript-check.py`
- **Trigger**: PostToolUse on Write/Edit/MultiEdit
- **Purpose**: Incremental TypeScript type checking
- **Blocks on**: Type errors in the edited file

### Testing Hooks

#### `test-runner.sh`
- **Trigger**: Pre/PostToolUse on Write/Edit/MultiEdit
- **Purpose**: Runs tests for modified components
- **Features**:
  - Pre-edit: Warns if tests are failing
  - Post-edit: Runs tests and blocks on failures
  - Reminds to create tests for new components

### Performance Hooks

#### `bundle-size-check.py`
- **Trigger**: PostToolUse on Write/Edit/MultiEdit
- **Purpose**: Monitors bundle size impact
- **Blocks on**:
  - Bundle exceeds 500KB (configurable)
  - Single change increases size by >50KB

#### `component-analyzer.py`
- **Trigger**: PostToolUse on Write/Edit/MultiEdit
- **Purpose**: Analyzes component complexity
- **Checks**:
  - Component size (lines)
  - Number of props, state variables, effects
  - Nested loops complexity
  - Memory leak patterns

### Utility Hooks

#### `bash-validator.py`
- **Trigger**: PreToolUse on Bash
- **Purpose**: Validates bash commands for safety and best practices
- **Features**:
  - Warns about dangerous commands
  - Suggests better alternatives (e.g., ripgrep over grep)

#### `prompt-enhancer.py`
- **Trigger**: UserPromptSubmit
- **Purpose**: Adds context and validates prompts
- **Features**:
  - Blocks prompts with sensitive information
  - Adds relevant Svelte context
  - Corrects common typos

#### `story-sync-check.sh`
- **Trigger**: PostToolUse on Write
- **Purpose**: Reminds to create Storybook stories for new components

## ⚙️ Configuration Examples

### Minimal Setup
Perfect for getting started:
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit|MultiEdit",
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/scripts/format-and-lint.sh"
      }]
    }]
  }
}
```

### Team Configuration
Focuses on collaboration and standards:
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit|MultiEdit",
      "hooks": [
        {
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/scripts/doc-enforcer.py"
        },
        {
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/scripts/breaking-change-detector.py"
        }
      ]
    }]
  }
}
```

## 🛠️ Customization

### Modifying Thresholds

Most scripts have configurable thresholds at the top of the file:

```python
# In bundle-size-check.py
MAX_BUNDLE_SIZE_KB = 500  # Maximum bundle size in KB
MAX_INCREASE_KB = 50      # Maximum allowed increase in KB

# In component-analyzer.py
THRESHOLDS = {
    "max_lines": 200,
    "max_props": 10,
    "max_effects": 5,
}
```

### Adding New Rules

Example of adding a new validation rule to `bash-validator.py`:

```python
VALIDATION_RULES = [
    # Add your rule
    (
        r"your-pattern-here",
        "Your warning message"
    ),
]
```

## 🐛 Troubleshooting

### Hooks Not Running
1. Check if scripts are executable: `ls -la .claude/hooks/scripts/`
2. Verify settings.json syntax: `jq . .claude/settings.json`
3. Run Claude with debug: `claude --debug`

### Scripts Failing
1. Test script manually:
   ```bash
   echo '{"tool_name":"Write","tool_input":{"file_path":"test.svelte"}}' | \
   .claude/hooks/scripts/svelte-validator.py
   ```
2. Check script permissions
3. Verify dependencies are installed

### Performance Issues
1. Increase timeout in settings.json:
   ```json
   {
     "type": "command",
     "command": "...",
     "timeout": 60
   }
   ```
2. Use incremental builds where possible
3. Move slow hooks to PreCompact or Stop events

## 📚 Resources

- [Claude Code Hooks Documentation](https://docs.anthropic.com/claude-code/hooks-guide)
- [Hook Reference](https://docs.anthropic.com/claude-code/hooks-reference)
- [Svelte Documentation](https://svelte.dev/docs)
- [SvelteKit Documentation](https://kit.svelte.dev/docs)

## 🤝 Contributing

To contribute new hooks:
1. Create a new script in `scripts/`
2. Make it executable
3. Add example configuration
4. Document usage in this README
5. Test thoroughly

## 📄 License

These hooks are provided as examples and can be freely used and modified for your projects.
