#!/usr/bin/env node

const ClaudeAgentBridge = require('../scripts/claude-integration');
const fs = require('fs');
const path = require('path');

class AgentHooks {
  constructor() {
    this.bridge = new ClaudeAgentBridge();
    this.initialized = false;
  }

  async initialize() {
    if (this.initialized) return;
    await this.bridge.initialize();
    this.initialized = true;
  }

  // Git pre-commit hook
  async preCommitHook(files = []) {
    try {
      await this.initialize();

      const changedFiles = this.parseChangedFiles(files);
      const relevantFiles = this.filterRelevantFiles(changedFiles);

      if (relevantFiles.length === 0) return { success: true };

      console.log('🤖 Running agent pre-commit checks...');

      // Run security audit on code changes
      const securityResult = await this.runSecurityAudit(relevantFiles);
      if (!securityResult.success) {
        return {
          success: false,
          message: 'Security audit failed',
          details: securityResult,
        };
      }

      // Run healthcare compliance if medical content changed
      const complianceResult = await this.runComplianceCheck(relevantFiles);
      if (!complianceResult.success) {
        return {
          success: false,
          message: 'Compliance check failed',
          details: complianceResult,
        };
      }

      return { success: true };
    } catch (error) {
      console.error('Pre-commit hook error:', error.message);
      return { success: false, message: error.message };
    }
  }

  // File change hook (watch mode)
  async fileChangeHook(filePath) {
    try {
      await this.initialize();

      const fileType = this.detectFileType(filePath);

      switch (fileType) {
        case 'medical-content':
          await this.processMedicalContentChange(filePath);
          break;
        case 'spec-kit':
          await this.processSpecKitChange(filePath);
          break;
        case 'code':
          await this.processCodeChange(filePath);
          break;
        case 'agent':
          await this.processAgentChange(filePath);
          break;
        case 'registry':
          await this.processRegistryChange(filePath);
          break;
        default:
          // No specific processing needed
          break;
      }
    } catch (error) {
      console.error(`File change hook error for ${filePath}:`, error.message);
    }
  }

  // Command line hook
  async commandHook(command, args = []) {
    try {
      await this.initialize();

      switch (command) {
        case 'agent-help':
          return this.showAgentHelp();
        case 'agent-info':
          return this.showAgentInfo(args[0]);
        case 'agent-test':
          return this.testAgent(args[0], args.slice(1));
        case 'agent-reload':
          await this.reloadAgents();
          return { success: true, message: 'Agents reloaded' };
        default:
          return null;
      }
    } catch (error) {
      console.error('Command hook error:', error.message);
      return { success: false, message: error.message };
    }
  }

  // IDE integration hook
  async ideHook(action, data) {
    try {
      await this.initialize();

      switch (action) {
        case 'completion':
          return this.getCodeCompletions(data);
        case 'analyze':
          return this.analyzeCode(data);
        case 'suggest-agents':
          return this.suggestAgentsForContext(data);
        default:
          return null;
      }
    } catch (error) {
      console.error('IDE hook error:', error.message);
      return null;
    }
  }

  // Spec-kit validation hook
  async specKitValidationHook() {
    try {
      await this.initialize();

      console.log('🤖 Running spec-kit validation checks...');

      // Check if spec-kit project exists
      const specKitDir = path.join(process.cwd(), '.specify');
      if (!fs.existsSync(specKitDir)) {
        return { success: true, message: 'No spec-kit project found' };
      }

      // Run spec-kit validation
      const specKitAgent = this.bridge.orchestrator.loader.getAgent('spec-kit-executor');
      if (!specKitAgent) {
        return { success: true, message: 'Spec-kit executor agent not found' };
      }

      const task = 'Validate spec-kit project structure and readiness';
      const result = await this.bridge.orchestrator.executeAgent('spec-kit-executor', task, {
        validation: true,
      });

      return { success: true, result };
    } catch (error) {
      console.error('Spec-kit validation hook error:', error.message);
      return { success: false, message: error.message };
    }
  }

  // Spec-kit execution hook
  async specKitExecutionHook(action = 'status') {
    try {
      await this.initialize();

      const specKitAgent = this.bridge.orchestrator.loader.getAgent('spec-kit-executor');
      if (!specKitAgent) {
        return { success: false, message: 'Spec-kit executor agent not found' };
      }

      let task;
      switch (action) {
        case 'status':
          task = 'Get current spec-kit execution status';
          break;
        case 'pause':
          task = 'Pause current spec-kit execution';
          break;
        case 'resume':
          task = 'Resume paused spec-kit execution';
          break;
        case 'cancel':
          task = 'Cancel current spec-kit execution';
          break;
        default:
          task = 'Get spec-kit execution status';
      }

      const result = await this.bridge.orchestrator.executeAgent('spec-kit-executor', task, { action });

      return { success: true, result };
    } catch (error) {
      console.error('Spec-kit execution hook error:', error.message);
      return { success: false, message: error.message };
    }
  }

  // Build system hook
  async buildHook(buildType = 'development') {
    try {
      await this.initialize();

      console.log(`🤖 Running agent build checks for ${buildType}...`);

      // Run spec-kit validation if project exists
      const specKitValidation = await this.specKitValidationHook();
      if (!specKitValidation.success) {
        return {
          success: false,
          message: 'Spec-kit validation failed',
          details: specKitValidation,
        };
      }

      // Validate agent configurations
      const validation = await this.validateAgentConfigurations();
      if (!validation.success) {
        return {
          success: false,
          message: 'Agent validation failed',
          details: validation,
        };
      }

      // Run tests for critical agents
      const testResult = await this.runCriticalAgentTests(buildType);
      if (!testResult.success) {
        return {
          success: false,
          message: 'Agent tests failed',
          details: testResult,
        };
      }

      // Performance check for agents
      const perfResult = await this.checkAgentPerformance();
      if (!perfResult.success && buildType === 'production') {
        return {
          success: false,
          message: 'Performance check failed',
          details: perfResult,
        };
      }

      return { success: true };
    } catch (error) {
      console.error('Build hook error:', error.message);
      return { success: false, message: error.message };
    }
  }

  // Helper methods
  parseChangedFiles(files) {
    if (typeof files === 'string') {
      return files.split('\n').filter((f) => f.trim());
    }
    return Array.isArray(files) ? files : [];
  }

  filterRelevantFiles(files) {
    return files.filter((file) => {
      const ext = path.extname(file);
      return (
        ['.js', '.ts', '.vue', '.py', '.md'].includes(ext) &&
        !file.includes('node_modules') &&
        !file.includes('.git')
      );
    });
  }

  detectFileType(filePath) {
    const ext = path.extname(filePath);
    const basename = path.basename(filePath);

    if (ext === '.md' && basename.includes('medical')) {
      return 'medical-content';
    }
    if (filePath.includes('.specify/')) {
      return 'spec-kit';
    }
    if (['.js', '.ts', '.vue', '.py'].includes(ext)) {
      return 'code';
    }
    if (filePath.includes('.claude/agents/')) {
      return 'agent';
    }
    if (filePath.includes('agents.json')) {
      return 'registry';
    }
    return 'other';
  }

  async runSecurityAudit(files) {
    try {
      const securityAgent = this.bridge.orchestrator.loader.getAgent('security_auditor');
      if (!securityAgent) {
        return { success: true, message: 'Security agent not found' };
      }

      const task = `Audit security for files: ${files.join(', ')}`;
      const result = await this.bridge.orchestrator.executeAgent('security_auditor', task, { files });

      return { success: true, result };
    } catch (error) {
      return { success: false, message: error.message };
    }
  }

  async runComplianceCheck(files) {
    try {
      const complianceAgent = this.bridge.orchestrator.loader.getAgent('healthcare_compliance_agent');
      if (!complianceAgent) {
        return { success: true, message: 'Compliance agent not found' };
      }

      const medicalFiles = files.filter((f) => this.detectFileType(f) === 'medical-content');
      if (medicalFiles.length === 0) {
        return { success: true };
      }

      const task = `Review healthcare compliance for files: ${medicalFiles.join(', ')}`;
      const result = await this.bridge.orchestrator.executeAgent('healthcare_compliance_agent', task, {
        files: medicalFiles,
      });

      return { success: true, result };
    } catch (error) {
      return { success: false, message: error.message };
    }
  }

  async processMedicalContentChange(filePath) {
    console.log(`🏥 Processing medical content change: ${filePath}`);
    // Trigger medical content validation
    const complianceAgent = this.bridge.orchestrator.loader.getAgent('healthcare_compliance_agent');
    if (complianceAgent) {
      await this.bridge.orchestrator.executeAgent(
        'healthcare_compliance_agent',
        `Validate medical content: ${filePath}`
      );
    }
  }

  async processCodeChange(filePath) {
    console.log(`💻 Processing code change: ${filePath}`);
    // Could trigger code analysis, testing, etc.
  }

  async processAgentChange(filePath) {
    console.log(`🤖 Processing agent change: ${filePath}`);
    // Reload agents when agent files change
    await this.reloadAgents();
  }

  async processRegistryChange(filePath) {
    console.log(`📋 Processing registry change: ${filePath}`);
    // Validate and reload agents when registry changes
    await this.validateAgentRegistry();
    await this.reloadAgents();
  }

  async processSpecKitChange(filePath) {
    console.log(`📋 Processing spec-kit change: ${filePath}`);

    // Trigger spec-kit validation when task files change
    const specKitAgent = this.bridge.orchestrator.loader.getAgent('spec-kit-executor');
    if (specKitAgent) {
      await this.bridge.orchestrator.executeAgent(
        'spec-kit-executor',
        `Validate spec-kit file change: ${filePath}`,
        { filePath, validation: true }
      );
    }
  }

  async showAgentHelp() {
    const agents = this.bridge.orchestrator.loader.getAllAgents();
    const helpText = `
🤖 Available Agent Commands:

@agent-name <task>              - Execute specific agent
@task-orchestrator <command>    - Use task orchestrator
@agent-orchestrator <command>   - Use agent orchestrator

Available Agents (${agents.length}):
${agents.map((a) => `  • ${a.displayName} (@${a.name})`).join('\n')}

Use 'claude-agent list' for detailed information
    `;
    return { success: true, message: helpText };
  }

  async showAgentInfo(agentName) {
    const agent = this.bridge.orchestrator.loader.getAgent(agentName);
    if (!agent) {
      return { success: false, message: `Agent ${agentName} not found` };
    }

    const info = `
Agent Information:
  Name: ${agent.displayName}
  ID: ${agent.name}
  Category: ${agent.category}
  Capabilities: ${agent.capabilities.join(', ') || 'None'}
  Triggers: ${agent.triggers.join(', ') || 'None'}
  Dependencies: ${agent.dependencies.join(', ') || 'None'}
    `;
    return { success: true, message: info };
  }

  async testAgent(agentName, args) {
    try {
      const task = args.join(' ');
      if (!task) {
        return { success: false, message: 'Task required for agent testing' };
      }

      const result = await this.bridge.orchestrator.executeAgent(agentName, task);
      return { success: true, result };
    } catch (error) {
      return { success: false, message: error.message };
    }
  }

  async reloadAgents() {
    console.log('🔄 Reloading agents...');
    await this.bridge.orchestrator.loader.loadAgents();
    console.log(`✅ Reloaded ${this.bridge.orchestrator.loader.agents.size} agents`);
  }

  async validateAgentConfigurations() {
    const agents = this.bridge.orchestrator.loader.getAllAgents();
    const issues = [];

    agents.forEach((agent) => {
      if (!agent.capabilities || agent.capabilities.length === 0) {
        issues.push(`Agent ${agent.name} has no capabilities defined`);
      }
      if (!agent.displayName || agent.displayName.trim() === '') {
        issues.push(`Agent ${agent.name} has no display name`);
      }
    });

    return {
      success: issues.length === 0,
      issues,
      message: issues.length === 0 ? 'All agents validated' : `${issues.length} issues found`,
    };
  }

  async validateAgentRegistry() {
    try {
      const registryPath = path.join(process.cwd(), '.claude', 'agents.json');
      if (!fs.existsSync(registryPath)) {
        console.log('⚠️  Agent registry not found');
        return { success: false, message: 'Registry not found' };
      }

      const registry = JSON.parse(fs.readFileSync(registryPath, 'utf8'));
      const issues = [];

      // Validate registry structure
      if (!registry.agents || !Array.isArray(registry.agents)) {
        issues.push('Registry missing agents array');
      }

      if (!registry.categories || typeof registry.categories !== 'object') {
        issues.push('Registry missing categories object');
      }

      // Validate each agent
      registry.agents.forEach((agent, index) => {
        if (!agent.name) issues.push(`Agent ${index}: Missing name`);
        if (!agent.displayName) issues.push(`Agent ${index}: Missing displayName`);
        if (!agent.category) issues.push(`Agent ${index}: Missing category`);
        if (!agent.triggers || !Array.isArray(agent.triggers)) {
          issues.push(`Agent ${index}: Missing or invalid triggers`);
        }
        if (!agent.capabilities || !Array.isArray(agent.capabilities)) {
          issues.push(`Agent ${index}: Missing or invalid capabilities`);
        }
        if (!agent.file) issues.push(`Agent ${index}: Missing file path`);
      });

      // Check for duplicate agent names
      const names = registry.agents.map((a) => a.name);
      const duplicates = names.filter((name, index) => names.indexOf(name) !== index);
      if (duplicates.length > 0) {
        issues.push(`Duplicate agent names: ${[...new Set(duplicates)].join(', ')}`);
      }

      console.log(`📋 Registry validation: ${issues.length} issues found`);
      if (issues.length > 0) {
        issues.forEach((issue) => console.log(`  • ${issue}`));
      }

      return {
        success: issues.length === 0,
        issues,
        message: issues.length === 0 ? 'Registry validated' : `${issues.length} validation issues`,
      };
    } catch (error) {
      console.error('Registry validation error:', error.message);
      return { success: false, message: error.message };
    }
  }

  async runCriticalAgentTests(buildType) {
    // Test critical agents
    const criticalAgents = ['security_auditor', 'healthcare_compliance_agent', 'docs_architect'];
    const results = [];

    for (const agentName of criticalAgents) {
      try {
        const agent = this.bridge.orchestrator.loader.getAgent(agentName);
        if (agent) {
          const result = await this.bridge.orchestrator.executeAgent(agentName, 'Health check');
          results.push({ agent: agentName, success: true });
        }
      } catch (error) {
        results.push({
          agent: agentName,
          success: false,
          error: error.message,
        });
      }
    }

    const failedTests = results.filter((r) => !r.success);
    return {
      success: failedTests.length === 0,
      results,
      message: failedTests.length === 0 ? 'All critical agents passed' : `${failedTests.length} agents failed`,
    };
  }

  async checkAgentPerformance() {
    // Basic performance check
    const startTime = Date.now();
    await this.bridge.orchestrator.initialize();
    const loadTime = Date.now() - startTime;

    return {
      success: loadTime < 5000, // 5 seconds threshold
      loadTime,
      message: `Agents loaded in ${loadTime}ms`,
    };
  }

  async getCodeCompletions(data) {
    // Implement code completion suggestions using agents
    return null;
  }

  async analyzeCode(data) {
    try {
      const securityAgent = this.bridge.orchestrator.loader.getAgent('security_auditor');
      if (securityAgent) {
        return await this.bridge.orchestrator.executeAgent('security_auditor', `Analyze code: ${data.code}`);
      }
      return null;
    } catch (error) {
      return null;
    }
  }

  async suggestAgentsForContext(data) {
    try {
      const context = {
        fileType: data.fileType,
        content: data.content.substring(0, 500), // First 500 chars
      };

      const suggestions = await this.bridge.orchestrator.getAgentsForTask(data.content, context);
      return suggestions.map((agent) => ({
        name: agent.name,
        displayName: agent.displayName,
        category: agent.category,
      }));
    } catch (error) {
      return [];
    }
  }
}

// Export for use in other scripts
module.exports = AgentHooks;

// If run directly, handle command line arguments
if (require.main === module) {
  const hooks = new AgentHooks();
  const [command, ...args] = process.argv.slice(2);

  hooks
    .commandHook(command, args)
    .then((result) => {
      if (result) {
        console.log(result.message);
        if (!result.success) {
          process.exit(1);
        }
      }
    })
    .catch((error) => {
      console.error('Hook execution failed:', error.message);
      process.exit(1);
    });
}
