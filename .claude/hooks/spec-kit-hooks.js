#!/usr/bin/env node

/**
 * Spec-Kit Git Hooks Integration
 *
 * Provides git hooks for spec-kit project validation and management
 * Integrates with the spec-kit-executor agent for automated workflows
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class SpecKitHooks {
  constructor() {
    this.claudeBridge = null;
    this.initialized = false;
  }

  async initialize() {
    if (this.initialized) return;

    try {
      // Try to load Claude Code integration if available
      const bridgePath = path.join(__dirname, '../scripts/claude-integration');
      if (fs.existsSync(bridgePath + '.js')) {
        const ClaudeAgentBridge = require(bridgePath);
        this.claudeBridge = new ClaudeAgentBridge();
        await this.claudeBridge.initialize();
      }
      this.initialized = true;
    } catch (error) {
      console.log('⚠️  Claude Code integration not available, running in standalone mode');
    }
  }

  // Git pre-commit hook for spec-kit validation
  async preCommitHook(files = []) {
    try {
      await this.initialize();

      console.log('📋 Running spec-kit pre-commit validation...');

      // Check if this is a spec-kit project
      if (!this.isSpecKitProject()) {
        return {
          success: true,
          message: 'Not a spec-kit project, skipping validation',
        };
      }

      // Get changed files
      const changedFiles = this.parseChangedFiles(files);
      const specKitFiles = this.filterSpecKitFiles(changedFiles);

      if (specKitFiles.length === 0) {
        return { success: true, message: 'No spec-kit files changed' };
      }

      console.log(`🔍 Validating ${specKitFiles.length} spec-kit file(s)...`);

      // Run spec-kit validation
      const validation = await this.runSpecKitValidation(specKitFiles);
      if (!validation.success) {
        return {
          success: false,
          message: 'Spec-kit validation failed',
          details: validation,
        };
      }

      // Check task dependencies if task files were modified
      if (specKitFiles.some((f) => f.includes('.task') || f.includes('tasks.md'))) {
        const depCheck = await this.validateTaskDependencies();
        if (!depCheck.success) {
          return {
            success: false,
            message: 'Task dependency validation failed',
            details: depCheck,
          };
        }
      }

      // Check if workflow is currently running
      const workflowCheck = await this.checkWorkflowStatus();
      if (workflowCheck.running && !workflowCheck.paused) {
        console.log('⚠️  Spec-kit workflow is currently running, commit may affect execution');
      }

      console.log('✅ Spec-kit validation passed');
      return { success: true };
    } catch (error) {
      console.error('❌ Spec-kit pre-commit hook error:', error.message);
      return { success: false, message: error.message };
    }
  }

  // Git post-merge hook for spec-kit project updates
  async postMergeHook() {
    try {
      await this.initialize();

      if (!this.isSpecKitProject()) {
        return { success: true };
      }

      console.log('📋 Running spec-kit post-merge validation...');

      // Validate project structure after merge
      const structureCheck = await this.validateProjectStructure();
      if (!structureCheck.success) {
        console.log('⚠️  Project structure issues detected after merge');
      }

      // Update agent registry if needed
      await this.updateAgentRegistry();

      // Check if spec-kit configuration changed
      const configChanged = this.configFilesChanged();
      if (configChanged) {
        console.log('🔄 Spec-kit configuration changed, running full validation...');
        await this.runFullValidation();
      }

      console.log('✅ Post-merge validation completed');
      return { success: true };
    } catch (error) {
      console.error('❌ Spec-kit post-merge hook error:', error.message);
      return { success: false, message: error.message };
    }
  }

  // Git pre-push hook to ensure workflow completion
  async prePushHook() {
    try {
      await this.initialize();

      if (!this.isSpecKitProject()) {
        return { success: true };
      }

      console.log('📋 Running spec-kit pre-push checks...');

      // Check if there are incomplete workflows
      const workflowStatus = await this.checkWorkflowStatus();
      if (workflowStatus.incomplete) {
        console.log('⚠️  Incomplete spec-kit workflows detected:');
        workflowStatus.incomplete.forEach((workflow) => {
          console.log(`   - ${workflow.name}: ${workflow.status} (${workflow.progress}%)`);
        });

        // Ask for confirmation
        const proceed = await this.promptUser('There are incomplete spec-kit workflows. Push anyway? (y/N): ');

        if (!proceed.toLowerCase().startsWith('y')) {
          return {
            success: false,
            message: 'Push cancelled due to incomplete workflows',
          };
        }
      }

      // Validate that all committed tasks are properly formatted
      const validation = await this.validateCommittedTasks();
      if (!validation.success) {
        return {
          success: false,
          message: 'Task validation failed',
          details: validation,
        };
      }

      console.log('✅ Pre-push checks passed');
      return { success: true };
    } catch (error) {
      console.error('❌ Spec-kit pre-push hook error:', error.message);
      return { success: false, message: error.message };
    }
  }

  // Git commit-msg hook for task completion tracking
  async commitMsgHook(commitMsgFile) {
    try {
      await this.initialize();

      if (!this.isSpecKitProject()) {
        return { success: true };
      }

      const commitMsg = fs.readFileSync(commitMsgFile, 'utf8');

      // Check for task completion patterns
      const taskCompletion = this.parseTaskCompletion(commitMsg);
      if (taskCompletion.tasks.length > 0) {
        console.log(`📋 Detected ${taskCompletion.tasks.length} task completion(s) in commit message`);

        // Update task status if Claude bridge is available
        if (this.claudeBridge) {
          await this.updateTaskStatus(taskCompletion.tasks);
        }
      }

      // Validate commit message format for spec-kit projects
      const msgValidation = this.validateCommitMessage(commitMsg);
      if (!msgValidation.valid) {
        return {
          success: false,
          message: 'Commit message validation failed',
          details: msgValidation,
        };
      }

      return { success: true };
    } catch (error) {
      console.error('❌ Spec-kit commit-msg hook error:', error.message);
      return { success: false, message: error.message };
    }
  }

  // Helper methods
  isSpecKitProject() {
    return (
      fs.existsSync(path.join(process.cwd(), '.specify')) ||
      fs.existsSync(path.join(process.cwd(), 'specs')) ||
      fs.existsSync(path.join(process.cwd(), 'tasks.md'))
    );
  }

  parseChangedFiles(files) {
    if (typeof files === 'string') {
      return files.split('\n').filter((f) => f.trim());
    }
    return Array.isArray(files) ? files : [];
  }

  filterSpecKitFiles(files) {
    return files.filter((file) => {
      return (
        file.includes('.specify/') ||
        file.includes('specs/') ||
        file.includes('tasks.md') ||
        file.includes('.task') ||
        file.includes('plan.md') ||
        file.includes('config.json')
      );
    });
  }

  async runSpecKitValidation(files) {
    if (!this.claudeBridge) {
      return {
        success: true,
        message: 'Claude bridge not available, skipping validation',
      };
    }

    try {
      const result = await this.claudeBridge.orchestrator.executeAgent(
        'spec-kit-executor',
        `Validate spec-kit files: ${files.join(', ')}`,
        { files, validation: true }
      );
      return { success: true, result };
    } catch (error) {
      return { success: false, message: error.message };
    }
  }

  async validateTaskDependencies() {
    if (!this.claudeBridge) {
      return { success: true };
    }

    try {
      const result = await this.claudeBridge.orchestrator.executeAgent(
        'spec-kit-executor',
        'Validate task dependencies and execution order',
        { dependencyCheck: true }
      );
      return { success: true, result };
    } catch (error) {
      return { success: false, message: error.message };
    }
  }

  async checkWorkflowStatus() {
    if (!this.claudeBridge) {
      return { running: false, incomplete: [] };
    }

    try {
      const result = await this.claudeBridge.orchestrator.executeAgent(
        'spec-kit-executor',
        'Check current workflow status',
        { statusCheck: true }
      );
      return result || { running: false, incomplete: [] };
    } catch (error) {
      return { running: false, incomplete: [] };
    }
  }

  async validateProjectStructure() {
    // Check required directories and files
    const required = ['.specify', 'specs'];
    const missing = required.filter((dir) => !fs.existsSync(dir));

    if (missing.length > 0) {
      return { success: false, missing };
    }

    return { success: true };
  }

  async updateAgentRegistry() {
    // Trigger agent registry update if available
    if (this.claudeBridge) {
      try {
        await this.claudeBridge.orchestrator.executeAgent(
          'context-manager',
          'Update agent registry after merge',
          { registryUpdate: true }
        );
      } catch (error) {
        // Non-critical, continue
      }
    }
  }

  configFilesChanged() {
    // Check if spec-kit config files changed (simplified)
    // In a real implementation, this would compare with git status
    return false;
  }

  async runFullValidation() {
    if (!this.claudeBridge) return;

    try {
      await this.claudeBridge.orchestrator.executeAgent('spec-kit-executor', 'Run full project validation', {
        fullValidation: true,
      });
    } catch (error) {
      console.log('⚠️  Full validation failed:', error.message);
    }
  }

  async validateCommittedTasks() {
    if (!this.claudeBridge) {
      return { success: true };
    }

    try {
      const result = await this.claudeBridge.orchestrator.executeAgent(
        'spec-kit-executor',
        'Validate committed tasks',
        { taskValidation: true }
      );
      return { success: true, result };
    } catch (error) {
      return { success: false, message: error.message };
    }
  }

  parseTaskCompletion(commitMsg) {
    // Simple pattern matching for task completion
    const patterns = [/task[-\s]?(\d+)/gi, /#(\d+)/gi, /complete[sd]?\s+task[-\s]?(\d+)/gi];

    const tasks = [];
    patterns.forEach((pattern) => {
      let match;
      while ((match = pattern.exec(commitMsg)) !== null) {
        tasks.push(match[1]);
      }
    });

    return { tasks: [...new Set(tasks)] };
  }

  validateCommitMessage(commitMsg) {
    // Basic validation for spec-kit commit messages
    const issues = [];

    if (commitMsg.length > 72) {
      issues.push('Commit message should be 72 characters or less');
    }

    if (!commitMsg.match(/^[A-Z]/)) {
      issues.push('Commit message should start with capital letter');
    }

    if (commitMsg.endsWith('.')) {
      issues.push('Commit message should not end with period');
    }

    return {
      valid: issues.length === 0,
      issues,
    };
  }

  async updateTaskStatus(tasks) {
    try {
      await this.claudeBridge.orchestrator.executeAgent(
        'task-executor',
        `Update task status for completed tasks: ${tasks.join(', ')}`,
        { tasks, status: 'completed' }
      );
    } catch (error) {
      console.log('⚠️  Failed to update task status:', error.message);
    }
  }

  async promptUser(question) {
    const readline = require('readline');
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    return new Promise((resolve) => {
      rl.question(question, (answer) => {
        rl.close();
        resolve(answer);
      });
    });
  }
}

// Export for use as module
module.exports = SpecKitHooks;

// CLI execution
if (require.main === module) {
  const hook = new SpecKitHooks();
  const hookType = process.argv[2];
  const args = process.argv.slice(3);

  hook
    .initialize()
    .then(() => {
      switch (hookType) {
        case 'pre-commit':
          hook.preCommitHook(args).then((result) => {
            process.exit(result.success ? 0 : 1);
          });
          break;
        case 'post-merge':
          hook.postMergeHook().then((result) => {
            process.exit(result.success ? 0 : 1);
          });
          break;
        case 'pre-push':
          hook.prePushHook().then((result) => {
            process.exit(result.success ? 0 : 1);
          });
          break;
        case 'commit-msg':
          hook.commitMsgHook(args[0]).then((result) => {
            process.exit(result.success ? 0 : 1);
          });
          break;
        default:
          console.error('Unknown hook type:', hookType);
          process.exit(1);
      }
    })
    .catch((error) => {
      console.error('Hook initialization failed:', error.message);
      process.exit(1);
    });
}
