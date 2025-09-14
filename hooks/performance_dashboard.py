#!/usr/bin/env python3
"""
Performance Dashboard - Visualize memory manager and hook performance metrics
Aggregates and displays performance insights from hook system
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

class PerformanceDashboard:
    def __init__(self):
        self.memory_base = Path('.serena/memories')
        self.metrics_file = self.memory_base / 'tasks' / 'metrics.jsonl'
        self.context_file = self.memory_base / 'context' / 'optimization_metrics.jsonl'
        self.navigation_file = self.memory_base / 'patterns' / 'navigation.jsonl'

    def generate_dashboard(self) -> Dict:
        """Generate comprehensive performance dashboard"""
        try:
            print("📊 Generating performance dashboard...")

            dashboard = {
                'generated_at': datetime.now().isoformat(),
                'summary': self._generate_summary(),
                'task_performance': self._analyze_task_performance(),
                'context_usage': self._analyze_context_usage(),
                'navigation_patterns': self._analyze_navigation_patterns(),
                'efficiency_trends': self._analyze_efficiency_trends(),
                'recommendations': []
            }

            # Add recommendations based on analysis
            dashboard['recommendations'] = self._generate_recommendations(dashboard)

            return dashboard

        except Exception as e:
            return {'error': f"Dashboard generation failed: {e}"}

    def _generate_summary(self) -> Dict:
        """Generate high-level performance summary"""
        summary = {
            'total_tasks': 0,
            'avg_efficiency': 0,
            'total_context_optimizations': 0,
            'active_patterns': 0,
            'session_days': 0
        }

        try:
            # Count total tasks
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    lines = f.readlines()
                    summary['total_tasks'] = len(lines)

                    # Calculate average efficiency from recent tasks
                    recent_efficiencies = []
                    for line in lines[-20:]:  # Last 20 tasks
                        try:
                            task = json.loads(line)
                            if task.get('agent_count', 1) > 1:
                                # Calculate efficiency
                                duration = task.get('duration_ms', 1000)
                                agents = task.get('agent_count', 1)
                                efficiency = min(100, int((duration / agents / duration) * 100))
                                recent_efficiencies.append(efficiency)
                        except:
                            continue

                    if recent_efficiencies:
                        summary['avg_efficiency'] = int(sum(recent_efficiencies) / len(recent_efficiencies))

            # Count context optimizations
            if self.context_file.exists():
                with open(self.context_file, 'r') as f:
                    summary['total_context_optimizations'] = len(f.readlines())

            # Count active patterns
            patterns_file = self.memory_base / 'patterns' / 'discovered.json'
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    patterns = json.load(f)
                    summary['active_patterns'] = len(patterns)

            # Estimate session days
            session_file = self.memory_base / 'context' / 'session.json'
            if session_file.exists():
                try:
                    stat = session_file.stat()
                    days_old = (datetime.now().timestamp() - stat.st_mtime) / (24 * 3600)
                    summary['session_days'] = max(1, int(days_old))
                except:
                    summary['session_days'] = 1

        except Exception as e:
            summary['error'] = str(e)

        return summary

    def _analyze_task_performance(self) -> Dict:
        """Analyze task execution performance"""
        analysis = {
            'task_distribution': defaultdict(int),
            'duration_stats': {},
            'success_rate': 0,
            'parallel_usage': 0
        }

        if not self.metrics_file.exists():
            return analysis

        try:
            durations = []
            success_count = 0
            total_count = 0
            parallel_count = 0

            with open(self.metrics_file, 'r') as f:
                for line in f:
                    try:
                        task = json.loads(line)
                        total_count += 1

                        # Duration analysis
                        duration = task.get('duration_ms', 0)
                        if duration > 0:
                            durations.append(duration)

                        # Success rate
                        if task.get('success', False):
                            success_count += 1

                        # Parallel usage
                        agent_count = task.get('agent_count', 1)
                        if agent_count > 1:
                            parallel_count += 1

                        # Task distribution by hour
                        timestamp = task.get('timestamp', '')
                        if timestamp:
                            try:
                                dt = datetime.fromisoformat(timestamp.replace('Z', ''))
                                hour = dt.hour
                                analysis['task_distribution'][f"{hour:02d}:00"] += 1
                            except:
                                pass

                    except:
                        continue

            # Calculate statistics
            if durations:
                analysis['duration_stats'] = {
                    'avg_ms': int(sum(durations) / len(durations)),
                    'min_ms': min(durations),
                    'max_ms': max(durations),
                    'total_tasks': len(durations)
                }

            if total_count > 0:
                analysis['success_rate'] = int((success_count / total_count) * 100)
                analysis['parallel_usage'] = int((parallel_count / total_count) * 100)

        except Exception as e:
            analysis['error'] = str(e)

        return analysis

    def _analyze_context_usage(self) -> Dict:
        """Analyze context optimization patterns"""
        analysis = {
            'optimization_frequency': 0,
            'avg_context_usage': 0,
            'peak_usage_times': []
        }

        if not self.context_file.exists():
            return analysis

        try:
            usage_data = []
            timestamps = []

            with open(self.context_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        usage_percent = entry.get('usage_percent', 0)
                        usage_data.append(usage_percent)

                        timestamp = entry.get('timestamp', '')
                        if timestamp:
                            timestamps.append(timestamp)

                    except:
                        continue

            if usage_data:
                analysis['optimization_frequency'] = len(usage_data)
                analysis['avg_context_usage'] = int(sum(usage_data) / len(usage_data))

                # Find peak usage times (>80%)
                for i, usage in enumerate(usage_data):
                    if usage > 80 and i < len(timestamps):
                        try:
                            dt = datetime.fromisoformat(timestamps[i].replace('Z', ''))
                            analysis['peak_usage_times'].append({
                                'time': dt.strftime('%H:%M'),
                                'usage': usage
                            })
                        except:
                            continue

        except Exception as e:
            analysis['error'] = str(e)

        return analysis

    def _analyze_navigation_patterns(self) -> Dict:
        """Analyze code navigation patterns"""
        analysis = {
            'total_navigations': 0,
            'popular_operations': defaultdict(int),
            'navigation_frequency': 0
        }

        if not self.navigation_file.exists():
            return analysis

        try:
            with open(self.navigation_file, 'r') as f:
                lines = f.readlines()
                analysis['total_navigations'] = len(lines)

                for line in lines:
                    try:
                        nav = json.loads(line)
                        operation = nav.get('operation', 'unknown')
                        analysis['popular_operations'][operation] += 1
                    except:
                        continue

            # Calculate frequency (navigations per day)
            if lines:
                try:
                    # Get time span from first to last navigation
                    first_nav = json.loads(lines[0])
                    last_nav = json.loads(lines[-1])

                    first_time = datetime.fromisoformat(first_nav['timestamp'].replace('Z', ''))
                    last_time = datetime.fromisoformat(last_nav['timestamp'].replace('Z', ''))

                    time_span_days = max(1, (last_time - first_time).days + 1)
                    analysis['navigation_frequency'] = int(len(lines) / time_span_days)

                except:
                    pass

        except Exception as e:
            analysis['error'] = str(e)

        return analysis

    def _analyze_efficiency_trends(self) -> Dict:
        """Analyze parallel execution efficiency trends"""
        analysis = {
            'efficiency_over_time': [],
            'best_efficiency': 0,
            'worst_efficiency': 100,
            'trend': 'stable'
        }

        if not self.metrics_file.exists():
            return analysis

        try:
            efficiencies = []
            recent_efficiencies = []

            with open(self.metrics_file, 'r') as f:
                for line in f:
                    try:
                        task = json.loads(line)
                        agent_count = task.get('agent_count', 1)

                        if agent_count > 1:
                            # Calculate efficiency
                            duration = task.get('duration_ms', 1000)
                            ideal_time = duration / agent_count
                            efficiency = min(100, int((ideal_time / duration) * 100))

                            efficiencies.append(efficiency)
                            timestamp = task.get('timestamp', '')

                            if timestamp:
                                analysis['efficiency_over_time'].append({
                                    'timestamp': timestamp,
                                    'efficiency': efficiency,
                                    'agent_count': agent_count
                                })

                    except:
                        continue

            if efficiencies:
                analysis['best_efficiency'] = max(efficiencies)
                analysis['worst_efficiency'] = min(efficiencies)

                # Determine trend (compare first and last 5 entries)
                if len(efficiencies) >= 10:
                    early_avg = sum(efficiencies[:5]) / 5
                    recent_avg = sum(efficiencies[-5:]) / 5

                    if recent_avg > early_avg + 10:
                        analysis['trend'] = 'improving'
                    elif recent_avg < early_avg - 10:
                        analysis['trend'] = 'declining'
                    else:
                        analysis['trend'] = 'stable'

        except Exception as e:
            analysis['error'] = str(e)

        return analysis

    def _generate_recommendations(self, dashboard: Dict) -> List[str]:
        """Generate performance recommendations based on analysis"""
        recommendations = []

        try:
            # Check task performance
            task_perf = dashboard.get('task_performance', {})
            success_rate = task_perf.get('success_rate', 0)

            if success_rate < 85:
                recommendations.append(f"⚠️ Task success rate is {success_rate}% - consider reviewing task configurations")

            parallel_usage = task_perf.get('parallel_usage', 0)
            if parallel_usage < 30:
                recommendations.append(f"💡 Only {parallel_usage}% of tasks use parallel agents - consider more parallel execution")

            # Check context usage
            context_usage = dashboard.get('context_usage', {})
            avg_usage = context_usage.get('avg_context_usage', 0)

            if avg_usage > 85:
                recommendations.append("🔄 High context usage detected - consider more frequent compaction")

            peak_times = context_usage.get('peak_usage_times', [])
            if len(peak_times) > 5:
                recommendations.append("📊 Frequent context peaks - consider optimizing memory retention")

            # Check efficiency trends
            efficiency = dashboard.get('efficiency_trends', {})
            trend = efficiency.get('trend', 'stable')

            if trend == 'declining':
                recommendations.append("📉 Parallel efficiency declining - review agent coordination")
            elif trend == 'improving':
                recommendations.append("✅ Great job! Parallel efficiency is improving")

            best_efficiency = efficiency.get('best_efficiency', 0)
            if best_efficiency < 70:
                recommendations.append("⚡ Low parallel efficiency - consider reducing agent count or improving task decomposition")

            # Check navigation patterns
            nav_patterns = dashboard.get('navigation_patterns', {})
            nav_frequency = nav_patterns.get('navigation_frequency', 0)

            if nav_frequency > 50:
                recommendations.append("🔍 High navigation frequency - consider caching frequently accessed code")

            # Summary recommendations
            summary = dashboard.get('summary', {})
            total_tasks = summary.get('total_tasks', 0)

            if total_tasks > 1000:
                recommendations.append("🗃️ Large task history - consider archiving old metrics")

            if not recommendations:
                recommendations.append("✅ Performance looks good! Keep up the great work.")

        except Exception as e:
            recommendations.append(f"⚠️ Could not generate all recommendations: {e}")

        return recommendations

def main():
    """Main entry point"""
    dashboard = PerformanceDashboard()

    if len(sys.argv) > 1 and sys.argv[1] == 'quick':
        print("⚡ Quick performance overview...")
        summary = dashboard._generate_summary()
        print(f"   📈 Tasks: {summary.get('total_tasks', 0)}")
        print(f"   ⚡ Avg Efficiency: {summary.get('avg_efficiency', 0)}%")
        print(f"   🧠 Active Patterns: {summary.get('active_patterns', 0)}")
        return

    # Full dashboard
    report = dashboard.generate_dashboard()

    if 'error' in report:
        print(f"❌ {report['error']}")
        sys.exit(1)

    # Display dashboard
    print("📊 Claude Code Performance Dashboard")
    print("=" * 50)

    # Summary section
    summary = report['summary']
    print(f"\n📈 Summary:")
    print(f"   • Total Tasks: {summary.get('total_tasks', 0)}")
    print(f"   • Average Efficiency: {summary.get('avg_efficiency', 0)}%")
    print(f"   • Context Optimizations: {summary.get('total_context_optimizations', 0)}")
    print(f"   • Active Patterns: {summary.get('active_patterns', 0)}")
    print(f"   • Session Days: {summary.get('session_days', 0)}")

    # Task performance
    task_perf = report['task_performance']
    if task_perf.get('duration_stats'):
        print(f"\n⏱️  Task Performance:")
        stats = task_perf['duration_stats']
        print(f"   • Average Duration: {stats.get('avg_ms', 0)}ms")
        print(f"   • Success Rate: {task_perf.get('success_rate', 0)}%")
        print(f"   • Parallel Usage: {task_perf.get('parallel_usage', 0)}%")

    # Context usage
    context = report['context_usage']
    if context.get('optimization_frequency', 0) > 0:
        print(f"\n🧠 Context Usage:")
        print(f"   • Optimizations: {context.get('optimization_frequency', 0)}")
        print(f"   • Average Usage: {context.get('avg_context_usage', 0)}%")
        peak_count = len(context.get('peak_usage_times', []))
        if peak_count > 0:
            print(f"   • Peak Usage Events: {peak_count}")

    # Navigation patterns
    nav = report['navigation_patterns']
    if nav.get('total_navigations', 0) > 0:
        print(f"\n🔍 Code Navigation:")
        print(f"   • Total Navigations: {nav.get('total_navigations', 0)}")
        print(f"   • Daily Frequency: {nav.get('navigation_frequency', 0)}")

        popular_ops = nav.get('popular_operations', {})
        if popular_ops:
            top_op = max(popular_ops.items(), key=lambda x: x[1])
            print(f"   • Most Used: {top_op[0]} ({top_op[1]} times)")

    # Efficiency trends
    efficiency = report['efficiency_trends']
    if efficiency.get('best_efficiency', 0) > 0:
        print(f"\n⚡ Efficiency Trends:")
        print(f"   • Best Efficiency: {efficiency.get('best_efficiency', 0)}%")
        print(f"   • Worst Efficiency: {efficiency.get('worst_efficiency', 100)}%")
        print(f"   • Trend: {efficiency.get('trend', 'stable').capitalize()}")

    # Recommendations
    recommendations = report['recommendations']
    if recommendations:
        print(f"\n💡 Recommendations:")
        for rec in recommendations[:5]:  # Show top 5
            print(f"   • {rec}")

    # Save report
    try:
        report_file = Path('.serena/memories/context/performance_dashboard.json')
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📝 Dashboard saved to {report_file}")

    except Exception as e:
        print(f"Could not save dashboard: {e}")

if __name__ == "__main__":
    main()