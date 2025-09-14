#!/usr/bin/env python3
"""
Environment Validator - Checks development environment setup
Validates tools, dependencies, and configurations for optimal Claude Code experience
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class EnvironmentValidator:
    def __init__(self):
        self.project_root = Path.cwd()
        self.results = {
            'core_tools': [],
            'formatters': [],
            'project_config': [],
            'performance': [],
            'issues': [],
            'warnings': []
        }

    def validate_all(self) -> Dict:
        """Comprehensive environment validation"""
        try:
            print("🔧 Validating development environment...")

            # Core development tools
            self._check_core_tools()

            # Code formatters and linters
            self._check_formatters()

            # Project configuration
            self._check_project_config()

            # Performance considerations
            self._check_performance_factors()

            # Generate report
            return self._generate_report()

        except Exception as e:
            return {'error': f"Environment validation failed: {e}"}

    def _check_core_tools(self):
        """Check essential development tools"""
        core_tools = [
            ('python3', 'Python 3.8+', self._check_python_version),
            ('node', 'Node.js', self._check_node_version),
            ('npm', 'NPM package manager', None),
            ('git', 'Git version control', self._check_git_config),
            ('bash', 'Bash shell', None),
            ('curl', 'HTTP client', None)
        ]

        for tool, description, version_check in core_tools:
            if self._command_exists(tool):
                version_info = ""
                if version_check:
                    version_info = version_check()

                self.results['core_tools'].append({
                    'tool': tool,
                    'status': 'available',
                    'description': description,
                    'version': version_info
                })
            else:
                self.results['issues'].append(f"Missing core tool: {description} ({tool})")

    def _check_formatters(self):
        """Check code formatters and linters"""
        formatters = [
            ('prettier', 'Prettier code formatter'),
            ('eslint', 'ESLint JavaScript linter'),
            ('black', 'Black Python formatter'),
            ('ruff', 'Ruff Python linter'),
            ('npx', 'Node.js package runner')
        ]

        for formatter, description in formatters:
            if self._command_exists(formatter):
                # Try to get version
                version = self._get_tool_version(formatter)
                self.results['formatters'].append({
                    'tool': formatter,
                    'status': 'available',
                    'description': description,
                    'version': version
                })
            else:
                # These are optional, so warn instead of error
                self.results['warnings'].append(f"Optional tool missing: {description} ({formatter})")

    def _check_project_config(self):
        """Check project configuration files"""
        config_files = [
            ('package.json', 'Node.js project configuration'),
            ('.prettierrc', 'Prettier configuration'),
            ('.eslintrc.js', 'ESLint configuration'),
            ('.eslintrc.json', 'ESLint configuration'),
            ('tsconfig.json', 'TypeScript configuration'),
            ('pyproject.toml', 'Python project configuration'),
            ('.gitignore', 'Git ignore rules'),
            ('README.md', 'Project documentation')
        ]

        for config_file, description in config_files:
            file_path = self.project_root / config_file

            if file_path.exists():
                # Check file size and readability
                try:
                    stat = file_path.stat()
                    size_kb = stat.st_size / 1024

                    self.results['project_config'].append({
                        'file': config_file,
                        'status': 'present',
                        'description': description,
                        'size_kb': round(size_kb, 2)
                    })
                except:
                    self.results['warnings'].append(f"Cannot read config file: {config_file}")

    def _check_performance_factors(self):
        """Check factors that affect development performance"""
        # Check project size
        try:
            # Count files (quick estimate)
            file_count = len(list(self.project_root.rglob('*')))
            self.results['performance'].append({
                'metric': 'project_files',
                'value': file_count,
                'status': 'good' if file_count < 10000 else 'warning'
            })
        except:
            pass

        # Check .serena memory size
        try:
            serena_path = self.project_root / '.serena'
            if serena_path.exists():
                # Rough size estimate
                total_size = sum(f.stat().st_size for f in serena_path.rglob('*') if f.is_file())
                size_mb = total_size / (1024 * 1024)

                self.results['performance'].append({
                    'metric': 'serena_memory_mb',
                    'value': round(size_mb, 2),
                    'status': 'good' if size_mb < 100 else 'warning'
                })
        except:
            pass

        # Check available disk space
        try:
            stat = os.statvfs(self.project_root)
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)

            self.results['performance'].append({
                'metric': 'free_disk_gb',
                'value': round(free_gb, 1),
                'status': 'good' if free_gb > 1 else 'critical'
            })
        except:
            pass

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists"""
        try:
            result = subprocess.run(
                ['which', command],
                capture_output=True,
                timeout=2,
                check=True
            )
            return result.returncode == 0
        except:
            return False

    def _get_tool_version(self, tool: str) -> str:
        """Get version of a tool"""
        version_flags = ['--version', '-v', 'version']

        for flag in version_flags:
            try:
                result = subprocess.run(
                    [tool, flag],
                    capture_output=True,
                    timeout=3,
                    text=True
                )
                if result.returncode == 0:
                    # Extract version from output (first line, first few words)
                    version_line = result.stdout.split('\n')[0]
                    words = version_line.split()
                    if len(words) > 1:
                        return ' '.join(words[:3])
                    return version_line[:50]
            except:
                continue

        return "unknown"

    def _check_python_version(self) -> str:
        """Check Python version and return details"""
        try:
            result = subprocess.run(
                ['python3', '--version'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                version_str = result.stdout.strip()
                # Check if version is 3.8+
                if 'Python 3.' in version_str:
                    version_num = version_str.split()[1]
                    major, minor = version_num.split('.')[:2]
                    if int(major) >= 3 and int(minor) >= 8:
                        return f"{version_str} ✓"
                    else:
                        self.results['issues'].append(f"Python version too old: {version_str} (need 3.8+)")
                        return f"{version_str} ⚠️"
                return version_str
        except:
            return "unknown"

    def _check_node_version(self) -> str:
        """Check Node.js version"""
        try:
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                version_str = result.stdout.strip()
                # Check if version is reasonably recent (v16+)
                if version_str.startswith('v'):
                    version_num = int(version_str[1:].split('.')[0])
                    if version_num >= 16:
                        return f"{version_str} ✓"
                    else:
                        self.results['warnings'].append(f"Node.js version old: {version_str} (recommend v18+)")
                        return f"{version_str} ⚠️"
                return version_str
        except:
            return "unknown"

    def _check_git_config(self) -> str:
        """Check Git configuration"""
        try:
            # Check user.name and user.email
            name_result = subprocess.run(
                ['git', 'config', 'user.name'],
                capture_output=True,
                text=True,
                timeout=2
            )
            email_result = subprocess.run(
                ['git', 'config', 'user.email'],
                capture_output=True,
                text=True,
                timeout=2
            )

            name = name_result.stdout.strip() if name_result.returncode == 0 else "not set"
            email = email_result.stdout.strip() if email_result.returncode == 0 else "not set"

            if name != "not set" and email != "not set":
                return f"configured ({name})"
            else:
                self.results['warnings'].append("Git user.name or user.email not configured")
                return "partially configured"

        except:
            return "unknown"

    def _generate_report(self) -> Dict:
        """Generate comprehensive environment report"""
        # Calculate health score
        total_checks = (len(self.results['core_tools']) +
                       len(self.results['formatters']) +
                       len(self.results['project_config']))

        issues_count = len(self.results['issues'])
        warnings_count = len(self.results['warnings'])

        # Health score: 100% - (issues * 20) - (warnings * 5)
        health_score = max(0, 100 - (issues_count * 20) - (warnings_count * 5))

        report = {
            'timestamp': datetime.now().isoformat(),
            'health_score': health_score,
            'environment_type': self._detect_environment_type(),
            'checks': {
                'core_tools': len(self.results['core_tools']),
                'formatters': len(self.results['formatters']),
                'configs': len(self.results['project_config']),
                'performance_metrics': len(self.results['performance'])
            },
            'issues_count': issues_count,
            'warnings_count': warnings_count,
            'details': self.results,
            'recommendations': self._get_recommendations()
        }

        return report

    def _detect_environment_type(self) -> str:
        """Detect what type of project this appears to be"""
        project_types = []

        if (self.project_root / 'package.json').exists():
            project_types.append('Node.js')

        if (self.project_root / 'pyproject.toml').exists() or (self.project_root / 'requirements.txt').exists():
            project_types.append('Python')

        if (self.project_root / 'tsconfig.json').exists():
            project_types.append('TypeScript')

        if (self.project_root / 'Cargo.toml').exists():
            project_types.append('Rust')

        if (self.project_root / 'go.mod').exists():
            project_types.append('Go')

        return ', '.join(project_types) if project_types else 'Unknown'

    def _get_recommendations(self) -> List[str]:
        """Generate environment improvement recommendations"""
        recommendations = []

        if self.results['issues']:
            recommendations.append("Install missing core development tools")

        if len(self.results['formatters']) < 3:
            recommendations.append("Install code formatters (prettier, eslint, black) for better code quality")

        if not any('prettier' in str(f) for f in self.results['formatters']):
            recommendations.append("Install Prettier for consistent code formatting")

        # Check performance recommendations
        for metric in self.results['performance']:
            if metric.get('status') == 'warning':
                if metric['metric'] == 'project_files' and metric['value'] > 10000:
                    recommendations.append("Large project detected - consider using .gitignore to exclude build files")
                elif metric['metric'] == 'serena_memory_mb' and metric['value'] > 100:
                    recommendations.append("Serena memory size large - consider periodic cleanup")
            elif metric.get('status') == 'critical':
                if metric['metric'] == 'free_disk_gb' and metric['value'] < 1:
                    recommendations.append("⚠️ Low disk space - free up space for optimal performance")

        if not any('git' in str(t) for t in self.results['core_tools']):
            recommendations.append("Configure Git user.name and user.email for proper commit attribution")

        return recommendations

def main():
    """Main entry point"""
    validator = EnvironmentValidator()

    if len(sys.argv) > 1 and sys.argv[1] == 'quick':
        # Quick validation
        print("⚡ Quick environment check...")
        issues = len([t for t in validator.results['core_tools'] if t.get('status') != 'available'])
        if issues == 0:
            print("✅ Core tools available")
        else:
            print(f"⚠️ {issues} core tool issues")
        return

    # Full validation
    report = validator.validate_all()

    if 'error' in report:
        print(f"❌ {report['error']}")
        sys.exit(1)

    # Display results
    print(f"\n📊 Environment Health: {report['health_score']}%")
    print(f"   🔧 Project Type: {report['environment_type']}")
    print(f"   ✅ Tools Available: {report['checks']['core_tools'] + report['checks']['formatters']}")
    print(f"   📁 Configs Found: {report['checks']['configs']}")

    if report['issues_count'] > 0:
        print(f"   ❌ Issues: {report['issues_count']}")

    if report['warnings_count'] > 0:
        print(f"   ⚠️ Warnings: {report['warnings_count']}")

    # Show details
    if report['details']['core_tools']:
        print(f"\n🔧 Core Tools:")
        for tool in report['details']['core_tools']:
            print(f"   ✅ {tool['description']}: {tool['version']}")

    if report['details']['issues']:
        print(f"\n❌ Issues:")
        for issue in report['details']['issues']:
            print(f"   • {issue}")

    if report['details']['warnings']:
        print(f"\n⚠️ Warnings:")
        for warning in report['details']['warnings']:
            print(f"   • {warning}")

    if report['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"   • {rec}")

    # Save report
    try:
        report_file = Path('.serena/memories/context/environment_report.json')
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📝 Report saved to {report_file}")

    except Exception as e:
        print(f"Could not save report: {e}")

if __name__ == "__main__":
    main()