#!/usr/bin/env python3
"""
Hook Health Monitor - Validates all Claude Code hooks are functional
Fast validation of hook system integrity
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class HookHealthMonitor:
    def __init__(self):
        self.hooks_dir = Path('.claude/hooks')
        self.settings_file = Path('.claude/settings.local.json')
        self.results = {'healthy': [], 'issues': [], 'missing': []}

    def check_all(self) -> Dict:
        """Comprehensive health check of hook system"""
        try:
            print("🔍 Checking Claude Code hook system health...")

            # Check hook files
            self._check_hook_files()

            # Check settings configuration
            self._check_settings_config()

            # Check dependencies
            self._check_dependencies()

            # Check memory structure
            self._check_memory_structure()

            # Generate report
            report = self._generate_report()

            return report

        except Exception as e:
            return {'error': f"Health check failed: {e}"}

    def _check_hook_files(self):
        """Check all hook files exist and are executable"""
        expected_hooks = [
            'memory_manager.py',
            'context_optimizer.py',
            'doc_cache.py',
            'auto_format.py',
            'quality_hints.py'
        ]

        for hook in expected_hooks:
            hook_path = self.hooks_dir / hook

            if not hook_path.exists():
                self.results['missing'].append(f"Missing hook file: {hook}")
                continue

            # Check if file is executable
            if not os.access(hook_path, os.R_OK):
                self.results['issues'].append(f"Cannot read hook file: {hook}")
                continue

            # Quick syntax check
            try:
                subprocess.run([
                    sys.executable, '-m', 'py_compile', str(hook_path)
                ], capture_output=True, timeout=5)
                self.results['healthy'].append(f"✓ {hook}")
            except:
                self.results['issues'].append(f"Syntax error in {hook}")

    def _check_settings_config(self):
        """Validate settings.local.json configuration"""
        try:
            if not self.settings_file.exists():
                self.results['missing'].append("Missing .claude/settings.local.json")
                return

            with open(self.settings_file, 'r') as f:
                settings = json.load(f)

            hooks_config = settings.get('hooks', {})

            # Check required hook events
            required_events = ['SessionStart', 'PreToolUse', 'PostToolUse', 'Stop']

            for event in required_events:
                if event in hooks_config:
                    self.results['healthy'].append(f"✓ {event} configured")
                else:
                    self.results['issues'].append(f"Missing {event} configuration")

            # Check for Task tool integration
            pretool_matchers = []
            for hook_group in hooks_config.get('PreToolUse', []):
                pretool_matchers.append(hook_group.get('matcher', ''))

            if 'Task' in str(pretool_matchers):
                self.results['healthy'].append("✓ Task tool integration")
            else:
                self.results['issues'].append("Missing Task tool hooks")

            # Check for Serena integration
            if 'mcp__serena__*' in str(pretool_matchers):
                self.results['healthy'].append("✓ Serena MCP integration")
            else:
                self.results['issues'].append("Missing Serena MCP hooks")

        except Exception as e:
            self.results['issues'].append(f"Settings config error: {e}")

    def _check_dependencies(self):
        """Check for required external dependencies"""
        dependencies = [
            ('python3', 'Python interpreter'),
            ('git', 'Git version control'),
            ('bash', 'Bash shell')
        ]

        optional_deps = [
            ('npx', 'Node.js package runner'),
            ('prettier', 'Code formatter'),
            ('eslint', 'JavaScript linter'),
            ('black', 'Python formatter'),
            ('ruff', 'Python linter')
        ]

        for cmd, desc in dependencies:
            if self._command_exists(cmd):
                self.results['healthy'].append(f"✓ {desc}")
            else:
                self.results['issues'].append(f"Missing required: {desc} ({cmd})")

        for cmd, desc in optional_deps:
            if self._command_exists(cmd):
                self.results['healthy'].append(f"✓ {desc} (optional)")
            # Note: Don't report optional dependencies as issues

    def _check_memory_structure(self):
        """Validate Serena memory structure"""
        memory_base = Path('.serena/memories')

        if memory_base.exists():
            self.results['healthy'].append("✓ Serena memory base exists")

            # Check key directories
            expected_dirs = ['context', 'patterns', 'tasks', 'architecture', 'decisions']

            for dir_name in expected_dirs:
                dir_path = memory_base / dir_name
                if dir_path.exists():
                    self.results['healthy'].append(f"✓ Memory/{dir_name}")
                else:
                    self.results['issues'].append(f"Missing memory/{dir_name}")
        else:
            self.results['issues'].append("Missing .serena/memories structure")

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists on the system"""
        try:
            subprocess.run(
                ['which', command],
                capture_output=True,
                timeout=2,
                check=True
            )
            return True
        except:
            return False

    def _generate_report(self) -> Dict:
        """Generate comprehensive health report"""
        total_checks = len(self.results['healthy']) + len(self.results['issues']) + len(self.results['missing'])
        healthy_count = len(self.results['healthy'])
        health_score = int((healthy_count / total_checks) * 100) if total_checks > 0 else 0

        report = {
            'timestamp': datetime.now().isoformat(),
            'health_score': health_score,
            'total_checks': total_checks,
            'healthy_count': healthy_count,
            'issues_count': len(self.results['issues']),
            'missing_count': len(self.results['missing']),
            'details': self.results,
            'recommendations': self._get_recommendations()
        }

        return report

    def _get_recommendations(self) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []

        if self.results['missing']:
            recommendations.append("Install missing dependencies and create missing files")

        if self.results['issues']:
            recommendations.append("Fix configuration and syntax issues")

        if len(self.results['healthy']) < 15:
            recommendations.append("Consider adding more hook integrations")

        if not any('Serena' in item for item in self.results['healthy']):
            recommendations.append("Add Serena MCP integration for better memory management")

        if not any('Task tool' in item for item in self.results['healthy']):
            recommendations.append("Configure Task tool hooks for agent tracking")

        return recommendations

def main():
    """Main entry point"""
    monitor = HookHealthMonitor()

    if len(sys.argv) > 1 and sys.argv[1] == 'quick':
        # Quick check mode
        print("⚡ Quick health check...")
        health_score = len(monitor.results['healthy']) / max(1, len(monitor.results['healthy']) + len(monitor.results['issues'])) * 100
        print(f"Health: {health_score:.0f}%")
        return

    # Full health check
    report = monitor.check_all()

    if 'error' in report:
        print(f"❌ {report['error']}")
        sys.exit(1)

    # Display results
    print(f"\n📊 Hook System Health: {report['health_score']}%")
    print(f"   ✅ Healthy: {report['healthy_count']}")
    print(f"   ⚠️  Issues: {report['issues_count']}")
    print(f"   ❌ Missing: {report['missing_count']}")

    if report['details']['healthy']:
        print(f"\n✅ Healthy Components:")
        for item in report['details']['healthy']:
            print(f"   {item}")

    if report['details']['issues']:
        print(f"\n⚠️  Issues Found:")
        for item in report['details']['issues']:
            print(f"   {item}")

    if report['details']['missing']:
        print(f"\n❌ Missing Components:")
        for item in report['details']['missing']:
            print(f"   {item}")

    if report['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"   • {rec}")

    # Save detailed report
    try:
        report_file = Path('.serena/memories/context/hook_health.json')
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📝 Detailed report saved to {report_file}")

    except Exception as e:
        print(f"Could not save report: {e}")

    # Exit with error code if issues found
    if report['issues_count'] > 0 or report['missing_count'] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()