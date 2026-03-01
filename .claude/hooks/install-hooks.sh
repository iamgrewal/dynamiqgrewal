#!/bin/bash

# Installation script for agent hooks
# This script sets up git hooks and system integrations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HOOKS_DIR="$PROJECT_ROOT/.git/hooks"

echo "🤖 Installing Claude Agent hooks..."

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

# Install pre-commit hook
cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/bin/bash
# Claude Agent pre-commit hook

node "$(dirname "$0")/../.claude/hooks/agent-hooks.js" pre-commit "$@"
EOF

chmod +x "$HOOKS_DIR/pre-commit"
echo "✅ Pre-commit hook installed"

# Install post-commit hook (optional)
cat > "$HOOKS_DIR/post-commit" << 'EOF'
#!/bin/bash
# Claude Agent post-commit hook

# Run any post-commit agent tasks here
node "$(dirname "$0")/../.claude/hooks/agent-hooks.js" post-commit "$@"
EOF

chmod +x "$HOOKS_DIR/post-commit"
echo "✅ Post-commit hook installed"

# Create npm scripts for agent management
echo "📦 Adding npm scripts..."

# Check if package.json exists
if [ -f "$PROJECT_ROOT/package.json" ]; then
  # Add agent scripts to package.json
  if command -v jq >/dev/null 2>&1; then
    jq '.scripts += {
      "agent:list": "node .claude/agent-cli.js list",
      "agent:status": "node .claude/agent-cli.js status",
      "agent:interactive": "node .claude/agent-cli.js interactive",
      "agent:reload": "node .claude/agent-cli.js reload",
      "agent:test": "node .claude/agent-cli.js test"
    }' "$PROJECT_ROOT/package.json" > "$PROJECT_ROOT/package.json.tmp" && \
    mv "$PROJECT_ROOT/package.json.tmp" "$PROJECT_ROOT/package.json"
    echo "✅ npm scripts added to package.json"
  else
    echo "⚠️  jq not found. Please add the following scripts to package.json manually:"
    echo '    "agent:list": "node .claude/agent-cli.js list",'
    echo '    "agent:status": "node .claude/agent-cli.js status",'
    echo '    "agent:interactive": "node .claude/agent-cli.js interactive",'
    echo '    "agent:reload": "node .claude/agent-cli.js reload",'
    echo '    "agent:test": "node .claude/agent-cli.js test"'
  fi
else
  echo "⚠️  package.json not found. Skipping npm script installation."
fi

# Create VS Code tasks if .vscode directory exists
VSCODE_DIR="$PROJECT_ROOT/.vscode"
if [ -d "$VSCODE_DIR" ]; then
  cat > "$VSCODE_DIR/tasks.json" << 'EOF'
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Agent: List Agents",
      "type": "shell",
      "command": "node",
      "args": [".claude/agent-cli.js", "list"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    },
    {
      "label": "Agent: Show Status",
      "type": "shell",
      "command": "node",
      "args": [".claude/agent-cli.js", "status"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    },
    {
      "label": "Agent: Interactive Mode",
      "type": "shell",
      "command": "node",
      "args": [".claude/agent-cli.js", "interactive"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": true,
        "panel": "terminal"
      },
      "isBackground": true
    },
    {
      "label": "Agent: Reload Agents",
      "type": "shell",
      "command": "node",
      "args": [".claude/agent-cli.js", "reload"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    }
  ]
}
EOF
  echo "✅ VS Code tasks created"
fi

# Install dependencies for agent system
echo "📥 Installing agent system dependencies..."
cd "$SCRIPT_DIR/.."
if command -v npm >/dev/null 2>&1; then
  npm install
  echo "✅ Dependencies installed"
else
  echo "⚠️  npm not found. Please install dependencies manually:"
  echo "   cd .claude && npm install"
fi

# Make CLI executable
chmod +x "$SCRIPT_DIR/../agent-cli.js"

# Create symbolic link for global access (optional)
if [ -w "/usr/local/bin" ]; then
  ln -sf "$SCRIPT_DIR/../agent-cli.js" "/usr/local/bin/claude-agent"
  echo "✅ Global 'claude-agent' command installed"
else
  echo "💡 To install globally, run:"
  echo "   sudo ln -sf '$SCRIPT_DIR/../agent-cli.js' '/usr/local/bin/claude-agent'"
  echo "   Or add to your PATH: export PATH=\"\$PATH:$SCRIPT_DIR/..\""
fi

echo ""
echo "🎉 Claude Agent hooks installation complete!"
echo ""
echo "Available commands:"
echo "  claude-agent list              # List all agents"
echo "  claude-agent status            # Show system status"
echo "  claude-agent interactive       # Start interactive mode"
echo "  claude-agent execute <agent> <task>  # Execute specific agent"
echo "  claude-agent auto <task>       # Auto-select and execute agent"
echo ""
echo "Git hooks are now active and will run agent checks on commits."
echo "VS Code tasks are available in the command palette (Ctrl+Shift+P)."
