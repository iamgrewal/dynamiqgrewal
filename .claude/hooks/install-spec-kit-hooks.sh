#!/bin/bash

# Spec-Kit Git Hooks Installation Script
# Installs git hooks for spec-kit project validation and management

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Installing Spec-Kit Git Hooks${NC}"

# Get the directory where this script is located
HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")"

# Git hooks directory
GIT_HOOKS_DIR="$PROJECT_ROOT/.git/hooks"

# Check if we're in a git repository
if [ ! -d "$GIT_HOOKS_DIR" ]; then
    echo -e "${YELLOW}⚠️  Not a git repository. Skipping hook installation.${NC}"
    exit 0
fi

echo -e "${GREEN}🔧 Setting up hooks in: $GIT_HOOKS_DIR${NC}"

# Function to create a hook
create_hook() {
    local hook_name="$1"
    local hook_path="$GIT_HOOKS_DIR/$hook_name"

    echo "Creating hook: $hook_name"

    cat > "$hook_path" << EOF
#!/bin/bash
# Spec-Kit Git Hook: $hook_name
# This hook is managed by the spec-kit system

NODE_ENV=production node "$HOOKS_DIR/spec-kit-hooks.js" "$hook_name" "\$@"
EOF

    # Make the hook executable
    chmod +x "$hook_path"

    echo -e "${GREEN}✅ Hook created: $hook_name${NC}"
}

# Install hooks
echo -e "${BLUE}📦 Installing Spec-Kit hooks...${NC}"

# Pre-commit hook for validation
create_hook "pre-commit"

# Post-merge hook for project updates
create_hook "post-merge"

# Pre-push hook for workflow checks
create_hook "pre-push"

# Commit-msg hook for task tracking
create_hook "commit-msg"

# Create hook configuration file
CONFIG_FILE="$PROJECT_ROOT/.specify/hooks.json"
mkdir -p "$(dirname "$CONFIG_FILE")"

cat > "$CONFIG_FILE" << EOF
{
  "version": "1.0.0",
  "installed": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "hooks": {
    "pre-commit": {
      "enabled": true,
      "description": "Validate spec-kit files before commit"
    },
    "post-merge": {
      "enabled": true,
      "description": "Update spec-kit project after merge"
    },
    "pre-push": {
      "enabled": true,
      "description": "Check workflow status before push"
    },
    "commit-msg": {
      "enabled": true,
      "description": "Track task completion in commit messages"
    }
  },
  "settings": {
    "validation_level": "strict",
    "require_task_completion": false,
    "allow_bypass": true,
    "auto_update_tasks": true
  }
}
EOF

echo -e "${GREEN}📝 Hook configuration created: $CONFIG_FILE${NC}"

# Create hook management script
MANAGE_SCRIPT="$PROJECT_ROOT/.specify/hooks-manage.sh"
cat > "$MANAGE_SCRIPT" << 'EOF'
#!/bin/bash
# Spec-Kit Hook Management Script

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GIT_HOOKS_DIR="$(git rev-parse --show-toplevel)/.git/hooks"

case "$1" in
    "enable")
        echo "🔧 Enabling Spec-Kit hooks..."
        find "$GIT_HOOKS_DIR" -name "*.sample" -delete
        for hook in pre-commit post-merge pre-push commit-msg; do
            if [ -f "$HOOKS_DIR/spec-kit-hooks.js" ]; then
                ln -sf "$HOOKS_DIR/spec-kit-hooks.js" "$GIT_HOOKS_DIR/$hook" 2>/dev/null || \
                cp "$HOOKS_DIR/spec-kit-hooks.js" "$GIT_HOOKS_DIR/$hook"
                chmod +x "$GIT_HOOKS_DIR/$hook"
            fi
        done
        echo "✅ Hooks enabled"
        ;;
    "disable")
        echo "🔧 Disabling Spec-Kit hooks..."
        for hook in pre-commit post-merge pre-push commit-msg; do
            if [ -f "$GIT_HOOKS_DIR/$hook" ] && grep -q "spec-kit-hooks.js" "$GIT_HOOKS_DIR/$hook"; then
                mv "$GIT_HOOKS_DIR/$hook" "$GIT_HOOKS_DIR/$hook.disabled"
            fi
        done
        echo "✅ Hooks disabled"
        ;;
    "status")
        echo "📊 Spec-Kit Hook Status:"
        for hook in pre-commit post-merge pre-push commit-msg; do
            if [ -f "$GIT_HOOKS_DIR/$hook" ] && grep -q "spec-kit-hooks.js" "$GIT_HOOKS_DIR/$hook"; then
                echo "  ✅ $hook: enabled"
            else
                echo "  ❌ $hook: disabled"
            fi
        done
        ;;
    "uninstall")
        echo "🗑️  Uninstalling Spec-Kit hooks..."
        for hook in pre-commit post-merge pre-push commit-msg; do
            if [ -f "$GIT_HOOKS_DIR/$hook" ] && grep -q "spec-kit-hooks.js" "$GIT_HOOKS_DIR/$hook"; then
                rm "$GIT_HOOKS_DIR/$hook"
            fi
        done
        rm -f "$HOOKS_DIR/hooks.json"
        echo "✅ Hooks uninstalled"
        ;;
    *)
        echo "Usage: $0 {enable|disable|status|uninstall}"
        echo ""
        echo "Commands:"
        echo "  enable    - Enable Spec-Kit hooks"
        echo "  disable   - Disable Spec-Kit hooks"
        echo "  status    - Show hook status"
        echo "  uninstall - Remove Spec-Kit hooks"
        exit 1
        ;;
esac
EOF

chmod +x "$MANAGE_SCRIPT"

echo -e "${GREEN}🎉 Spec-Kit hooks installation complete!${NC}"
echo ""
echo -e "${BLUE}📋 Installed hooks:${NC}"
echo "  • pre-commit   - Validate spec-kit files before commit"
echo "  • post-merge   - Update project after merge"
echo "  • pre-push     - Check workflow status before push"
echo "  • commit-msg   - Track task completion in commits"
echo ""
echo -e "${BLUE}⚙️  Management:${NC}"
echo "  Use '$PROJECT_ROOT/.specify/hooks-manage.sh' to manage hooks"
echo "  Available commands: enable, disable, status, uninstall"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo "  • Hooks will automatically validate spec-kit files"
echo "  • Task completion is tracked from commit messages"
echo "  • Incomplete workflows will warn before pushing"
echo "  • Use hooks-manage.sh to temporarily disable if needed"
echo ""
echo -e "${GREEN}✨ Ready for spec-driven development!${NC}"
