# Claude Code Hooks System

This directory contains the hook system for Claude Code, providing intelligent workflow automation, memory management, and development environment optimization.

## 🚀 Quick Start

```bash
# Check system health
python3 .claude/hooks/hook_health_monitor.py

# Validate environment
python3 .claude/hooks/env_validator.py

# View performance dashboard
python3 .claude/hooks/performance_dashboard.py
```

## 📁 Hook Files Overview

### Core Memory Management
- **`memory_manager.py`** - Advanced memory management with Serena integration
  - Context caching and retrieval
  - Pattern tracking and deduplication
  - Parallel execution efficiency analysis
  - Serena MCP operation tracking

### Workflow Automation
- **`auto_format.py`** - Background code formatting (Prettier, ESLint, Black, Ruff)
- **`quality_hints.py`** - Non-blocking code quality suggestions
- **`context_optimizer.py`** - Smart context management before compaction
- **`doc_cache.py`** - Context7 documentation caching for offline access

### System Monitoring
- **`hook_health_monitor.py`** - Validates all hooks are functional
- **`env_validator.py`** - Checks development environment setup
- **`performance_dashboard.py`** - Visualizes performance metrics and trends

## ⚙️ Configuration

Hooks are configured in `.claude/settings.local.json`:

### Event Triggers
- **SessionStart**: Initialize memory structure
- **PreToolUse**: Load context, validate environment
- **PostToolUse**: Save patterns, format code, track metrics
- **PreCompact**: Optimize context before compaction
- **Stop**: Save session checkpoint

### Tool Integration
- **Task tool**: `memory_manager.py pre_task` → `memory_manager.py post_task`
- **Serena MCP**: `memory_manager.py serena_sync` for operation tracking
- **File operations**: Auto-formatting and quality hints

## 🔧 Commands Reference

### Memory Manager
```bash
# Initialize memory structure
python3 memory_manager.py init

# Load context before task execution
python3 memory_manager.py pre_task

# Save patterns and metrics after task
python3 memory_manager.py post_task

# Track Serena MCP operations
python3 memory_manager.py serena_sync
```

### Monitoring Tools
```bash
# Full health check
python3 hook_health_monitor.py

# Quick health check
python3 hook_health_monitor.py quick

# Full environment validation
python3 env_validator.py

# Full performance dashboard
python3 performance_dashboard.py
```

## 📊 Performance Features

### Intelligent Caching
- 10-minute TTL for context data
- Pattern deduplication with MD5 hashing
- Efficient memory usage tracking

### Parallel Execution Analysis
- Efficiency calculation and tips
- Agent coordination metrics
- Performance trend analysis

### Code Navigation Tracking
- Serena operation patterns
- Refactoring success tracking
- Navigation frequency analysis

## 🧠 Memory Structure

The hooks create and manage this memory structure:

```
.serena/memories/
├── architecture/     # System design decisions
├── patterns/        # Discovered code patterns
│   ├── discovered.json
│   ├── navigation.jsonl
│   └── refactorings.jsonl
├── decisions/       # Technical choices with rationale
├── context/         # Session and optimization data
│   ├── session.json
│   ├── optimization_metrics.jsonl
│   ├── hook_health.json
│   ├── environment_report.json
│   └── performance_dashboard.json
├── tasks/           # Task execution metrics
│   └── metrics.jsonl
└── documentation/   # Cached Context7 responses
```

## 🔍 Health Monitoring

### Hook Health Monitor
- Validates all hook files exist and are executable
- Checks settings.local.json configuration
- Verifies required dependencies
- Validates Serena memory structure

### Environment Validator
- Checks core development tools (Python, Node.js, Git)
- Validates code formatters (Prettier, ESLint, Black, Ruff)
- Analyzes project configuration files
- Monitors performance factors (disk space, project size)

### Performance Dashboard
- Task execution statistics
- Context usage patterns
- Navigation behavior analysis
- Efficiency trends and recommendations

## 🚨 Troubleshooting

### Common Issues

1. **"Permission denied" errors**
   ```bash
   chmod +x .claude/hooks/*.py
   ```

2. **"Module not found" errors**
   ```bash
   # Check Python installation
   python3 --version

   # Ensure hooks directory is accessible
   ls -la .claude/hooks/
   ```

3. **"Hook failed" messages**
   ```bash
   # Run health check to identify issues
   python3 .claude/hooks/hook_health_monitor.py
   ```

4. **Missing dependencies**
   ```bash
   # Check what's missing
   python3 .claude/hooks/env_validator.py

   # Install missing tools as needed
   npm install -g prettier eslint
   pip install black ruff
   ```

### Debug Mode

Add debug output to any hook by setting environment variable:
```bash
export HOOK_DEBUG=1
```

## 🔄 Updates and Maintenance

### Periodic Tasks
- Run `hook_health_monitor.py` weekly
- Check `performance_dashboard.py` for optimization opportunities
- Clean old metrics with `find .serena/memories -name "*.jsonl" -size +10M`

### Memory Cleanup
The system automatically:
- Limits patterns to last 100 entries
- Caches documentation with size limits
- Rotates old log files
- Provides cleanup recommendations

## 🎯 Best Practices

1. **Non-blocking Design**: All hooks fail gracefully without blocking execution
2. **Efficient Caching**: Context is cached with TTL to reduce I/O
3. **Pattern Recognition**: Code patterns are automatically discovered and reused
4. **Performance Tracking**: Parallel execution efficiency is monitored and optimized
5. **Health Monitoring**: System health is continuously validated

## 📈 Performance Optimization

### Parallel Execution Tips
- Use Task tool for agent deployments
- Monitor efficiency scores in dashboard
- Keep agent counts appropriate for task complexity

### Memory Usage
- Context optimization triggers at 70% usage
- Critical context is preserved during compaction
- Old patterns are automatically rotated

### Development Speed
- Auto-formatting runs in background
- Quality hints are non-blocking
- Documentation is cached for offline access

---

*This hook system provides intelligent automation while maintaining full transparency and control over your Claude Code workflow.*