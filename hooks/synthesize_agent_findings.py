#!/usr/bin/env python3
"""
Synthesize Agent Findings - Combine insights from multiple agents into actionable knowledge
Now with Serena MCP integration for proper memory persistence
"""

import json
import os
import sys
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

class AgentFindingsSynthesizer:
    def __init__(self, temp_dir: str = '/tmp/claude_session', use_serena: bool = True):
        self.temp_dir = Path(temp_dir)
        self.use_serena = use_serena
        
        # Temp paths for immediate capture
        self.temp_findings = self.temp_dir / 'findings'
        self.temp_agents = self.temp_dir / 'agents'
        self.temp_logs = self.temp_dir / 'logs'
        
        # Ensure temp directories exist
        for path in [self.temp_findings, self.temp_agents, self.temp_logs]:
            path.mkdir(parents=True, exist_ok=True)
    
    def save_to_serena(self, namespace: str, key: str, data: Any) -> bool:
        """Save data to Serena MCP memory"""
        if not self.use_serena:
            # Fallback to temp file if Serena not available
            fallback_path = self.temp_dir / 'serena_fallback' / namespace
            fallback_path.mkdir(parents=True, exist_ok=True)
            with open(fallback_path / f"{key}.json", 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        try:
            # Use Serena MCP save_memory command
            # This would be called through Claude Code's MCP interface
            # For hooks, we'll use a helper script that Claude Code can invoke
            
            # Create a marker file for Claude Code to process
            mcp_request = {
                'namespace': namespace,
                'key': key,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            
            # Write to pending MCP operations queue
            mcp_queue = self.temp_dir / 'mcp_queue.jsonl'
            with open(mcp_queue, 'a') as f:
                f.write(json.dumps({
                    'operation': 'save_memory',
                    'server': 'serena',
                    'params': mcp_request
                }) + '\n')
            
            return True
            
        except Exception as e:
            self.log_error(f"Failed to save to Serena: {str(e)}")
            return False
    
    def load_from_serena(self, namespace: str, key: str) -> Optional[Dict]:
        """Load data from Serena MCP memory"""
        if not self.use_serena:
            fallback_path = self.temp_dir / 'serena_fallback' / namespace / f"{key}.json"
            if fallback_path.exists():
                with open(fallback_path, 'r') as f:
                    return json.load(f)
            return None
        
        try:
            # Queue MCP load request
            mcp_queue = self.temp_dir / 'mcp_queue.jsonl'
            with open(mcp_queue, 'a') as f:
                f.write(json.dumps({
                    'operation': 'load_memory',
                    'server': 'serena',
                    'params': {
                        'namespace': namespace,
                        'key': key
                    }
                }) + '\n')
            
            # For immediate needs, check temp cache
            cache_file = self.temp_dir / 'serena_cache' / namespace / f"{key}.json"
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            self.log_error(f"Failed to load from Serena: {str(e)}")
            return None
    
    def synthesize_immediate(self, task_id: str):
        """Immediate synthesis after a task completes"""
        try:
            # Read the raw output from temp
            raw_file = self.temp_agents / f"raw_{task_id}.txt"
            if not raw_file.exists():
                return
            
            with open(raw_file, 'r') as f:
                raw_output = f.read()
            
            # Extract patterns and insights
            finding = self.extract_finding_from_output(raw_output, task_id)
            
            if finding:
                # Save to temp for batching
                temp_finding_file = self.temp_findings / f"{task_id}.json"
                with open(temp_finding_file, 'w') as f:
                    json.dump(finding, f, indent=2)
                
                # Queue for Serena persistence
                self.queue_for_serena_save('findings', task_id, finding)
                
                print(f"✓ Immediate synthesis for task {task_id}")
        
        except Exception as e:
            self.log_error(f"Immediate synthesis failed for {task_id}: {str(e)}")
    
    def synthesize_incremental(self, agent_id: Optional[str] = None):
        """Incremental synthesis when subagents stop"""
        try:
            # Get pending synthesis items
            pending_file = self.temp_findings / 'pending_synthesis.jsonl'
            if not pending_file.exists():
                return
            
            pending_items = []
            with open(pending_file, 'r') as f:
                for line in f:
                    try:
                        pending_items.append(json.loads(line))
                    except:
                        continue
            
            if len(pending_items) >= 3:  # Batch threshold
                # Group and synthesize
                synthesis = self.create_incremental_synthesis(pending_items)
                
                if synthesis:
                    # Save to Serena
                    synthesis_key = f"incremental_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    self.save_to_serena('synthesis', synthesis_key, synthesis)
                    
                    # Clear processed items
                    open(pending_file, 'w').close()
                    
                    print(f"✓ Incremental synthesis completed ({len(pending_items)} items)")
        
        except Exception as e:
            self.log_error(f"Incremental synthesis failed: {str(e)}")
    
    def synthesize_phase(self, consolidate: bool = True):
        """Phase-level synthesis"""
        try:
            # Collect all findings from current phase
            phase_findings = []
            
            for finding_file in self.temp_findings.glob("*.json"):
                with open(finding_file, 'r') as f:
                    phase_findings.append(json.load(f))
            
            if not phase_findings:
                return
            
            # Create phase synthesis
            phase_synthesis = self.create_phase_synthesis(phase_findings)
            
            if phase_synthesis:
                # Save to Serena
                phase_key = f"phase_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.save_to_serena('synthesis', phase_key, phase_synthesis)
                
                if consolidate:
                    # Archive temp findings
                    archive_dir = self.temp_dir / 'archived_phases'
                    archive_dir.mkdir(exist_ok=True)
                    
                    for finding_file in self.temp_findings.glob("*.json"):
                        finding_file.rename(archive_dir / finding_file.name)
                
                print(f"✓ Phase synthesis completed ({len(phase_findings)} findings)")
        
        except Exception as e:
            self.log_error(f"Phase synthesis failed: {str(e)}")
    
    def synthesize_final(self, session_id: str, output_path: Optional[str] = None):
        """Final synthesis for entire session"""
        try:
            # Collect all synthesis results
            all_syntheses = []
            
            # Load from Serena (check MCP cache)
            cache_dir = self.temp_dir / 'serena_cache' / 'synthesis'
            if cache_dir.exists():
                for cache_file in cache_dir.glob("*.json"):
                    with open(cache_file, 'r') as f:
                        all_syntheses.append(json.load(f))
            
            # Add any remaining temp findings
            for finding_file in self.temp_findings.glob("*.json"):
                with open(finding_file, 'r') as f:
                    all_syntheses.append(json.load(f))
            
            # Create final comprehensive synthesis
            final_synthesis = self.create_final_synthesis(session_id, all_syntheses)
            
            if final_synthesis:
                # Save to Serena with session context
                final_key = f"session_{session_id}_final"
                self.save_to_serena('synthesis', final_key, final_synthesis)
                
                # Also save master recommendations
                if 'recommendations' in final_synthesis:
                    self.save_to_serena('recommendations', session_id, 
                                       final_synthesis['recommendations'])
                
                # Save patterns for reuse
                if 'patterns' in final_synthesis:
                    self.save_to_serena('patterns', f"session_{session_id}", 
                                       final_synthesis['patterns'])
                
                # Optional file output for external use
                if output_path:
                    with open(output_path, 'w') as f:
                        json.dump(final_synthesis, f, indent=2)
                
                print(f"✓ Final synthesis for session {session_id} saved to Serena")
                print(f"  - {len(all_syntheses)} total findings processed")
                print(f"  - {len(final_synthesis.get('recommendations', []))} recommendations")
                print(f"  - {len(final_synthesis.get('patterns', []))} patterns identified")
        
        except Exception as e:
            self.log_error(f"Final synthesis failed: {str(e)}")
    
    def extract_finding_from_output(self, output: str, task_id: str) -> Dict:
        """Extract structured finding from agent output"""
        finding = {
            'task_id': task_id,
            'timestamp': datetime.now().isoformat(),
            'patterns': [],
            'issues': [],
            'solutions': [],
            'insights': {}
        }
        
        # Parse output for patterns (simplified - could use NLP)
        lines = output.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            
            # Detect patterns
            if any(keyword in line_lower for keyword in ['pattern', 'found', 'detected', 'identified']):
                finding['patterns'].append({
                    'type': 'detected',
                    'content': line.strip()[:200]
                })
            
            # Detect issues
            if any(keyword in line_lower for keyword in ['error', 'issue', 'problem', 'warning']):
                finding['issues'].append({
                    'type': 'identified',
                    'content': line.strip()[:200]
                })
            
            # Detect solutions
            if any(keyword in line_lower for keyword in ['fixed', 'resolved', 'solution', 'implemented']):
                finding['solutions'].append({
                    'type': 'applied',
                    'content': line.strip()[:200]
                })
        
        # Extract key insights
        if output:
            finding['insights']['summary'] = output[:500]
            finding['insights']['length'] = len(output)
        
        return finding if (finding['patterns'] or finding['issues'] or finding['solutions']) else None
    
    def create_incremental_synthesis(self, items: List[Dict]) -> Dict:
        """Create synthesis from incremental items"""
        return {
            'type': 'incremental',
            'timestamp': datetime.now().isoformat(),
            'item_count': len(items),
            'patterns': self.extract_common_patterns(items),
            'issues': self.extract_common_issues(items),
            'solutions': self.combine_solutions(items)
        }
    
    def create_phase_synthesis(self, findings: List[Dict]) -> Dict:
        """Create phase-level synthesis"""
        return {
            'type': 'phase',
            'timestamp': datetime.now().isoformat(),
            'finding_count': len(findings),
            'task_ids': [f.get('task_id') for f in findings if 'task_id' in f],
            'patterns': self.extract_common_patterns(findings),
            'issues': self.extract_common_issues(findings),
            'solutions': self.combine_solutions(findings),
            'confidence': self.calculate_confidence(findings)
        }
    
    def create_final_synthesis(self, session_id: str, all_data: List[Dict]) -> Dict:
        """Create final comprehensive synthesis"""
        patterns = self.extract_common_patterns(all_data)
        issues = self.extract_common_issues(all_data)
        solutions = self.combine_solutions(all_data)
        
        return {
            'type': 'final',
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'total_items': len(all_data),
            'patterns': patterns,
            'issues': issues,
            'solutions': solutions,
            'recommendations': self.generate_recommendations(patterns, issues, solutions),
            'confidence': self.calculate_confidence(all_data),
            'summary': self.generate_summary(all_data)
        }
    
    def extract_common_patterns(self, items: List[Dict]) -> List[Dict]:
        """Extract patterns that appear multiple times"""
        all_patterns = []
        for item in items:
            if 'patterns' in item:
                all_patterns.extend(item['patterns'])
        
        # Count occurrences
        pattern_counts = defaultdict(int)
        for pattern in all_patterns:
            pattern_key = str(pattern.get('content', ''))[:50]
            pattern_counts[pattern_key] += 1
        
        # Return patterns that appear multiple times
        common = []
        for key, count in pattern_counts.items():
            if count > 1:
                common.append({
                    'pattern': key,
                    'frequency': count,
                    'confidence': 'high' if count > 2 else 'medium'
                })
        
        return sorted(common, key=lambda x: x['frequency'], reverse=True)[:10]
    
    def extract_common_issues(self, items: List[Dict]) -> List[Dict]:
        """Extract recurring issues"""
        all_issues = []
        for item in items:
            if 'issues' in item:
                all_issues.extend(item['issues'])
        
        issue_counts = defaultdict(int)
        for issue in all_issues:
            issue_key = str(issue.get('content', ''))[:50]
            issue_counts[issue_key] += 1
        
        recurring = []
        for key, count in issue_counts.items():
            if count > 1:
                recurring.append({
                    'issue': key,
                    'frequency': count,
                    'severity': 'high' if count > 2 else 'medium'
                })
        
        return recurring
    
    def combine_solutions(self, items: List[Dict]) -> List[Dict]:
        """Combine and rank solutions"""
        all_solutions = []
        for item in items:
            if 'solutions' in item:
                all_solutions.extend(item['solutions'])
        
        # Group similar solutions
        solution_groups = defaultdict(list)
        for solution in all_solutions:
            solution_key = str(solution.get('content', ''))[:30]
            solution_groups[solution_key].append(solution)
        
        combined = []
        for key, group in solution_groups.items():
            combined.append({
                'solution': key,
                'occurrences': len(group),
                'confidence': 'high' if len(group) > 1 else 'medium'
            })
        
        return sorted(combined, key=lambda x: x['occurrences'], reverse=True)[:10]
    
    def calculate_confidence(self, items: List[Dict]) -> float:
        """Calculate overall confidence score"""
        if not items:
            return 0.0
        
        score = min(len(items) * 0.1, 0.5)  # More items = higher confidence
        
        # Check for patterns
        has_patterns = any('patterns' in item and item['patterns'] for item in items)
        if has_patterns:
            score += 0.2
        
        # Check for solutions
        has_solutions = any('solutions' in item and item['solutions'] for item in items)
        if has_solutions:
            score += 0.3
        
        return min(score, 1.0)
    
    def generate_recommendations(self, patterns: List, issues: List, solutions: List) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # High-confidence patterns to follow
        for pattern in patterns[:3]:
            if pattern.get('confidence') == 'high':
                recommendations.append({
                    'type': 'pattern',
                    'priority': 'high',
                    'action': f"Apply pattern: {pattern['pattern']}"
                })
        
        # Critical issues to address
        for issue in issues[:3]:
            if issue.get('severity') == 'high':
                recommendations.append({
                    'type': 'issue',
                    'priority': 'high',
                    'action': f"Address recurring issue: {issue['issue']}"
                })
        
        # Proven solutions to implement
        for solution in solutions[:3]:
            if solution.get('confidence') == 'high':
                recommendations.append({
                    'type': 'solution',
                    'priority': 'medium',
                    'action': f"Implement solution: {solution['solution']}"
                })
        
        return recommendations
    
    def generate_summary(self, items: List[Dict]) -> str:
        """Generate executive summary"""
        task_count = len(set(item.get('task_id', '') for item in items if 'task_id' in item))
        pattern_count = sum(len(item.get('patterns', [])) for item in items)
        solution_count = sum(len(item.get('solutions', [])) for item in items)
        
        return (f"Processed {len(items)} findings from {task_count} tasks. "
                f"Identified {pattern_count} patterns and {solution_count} solutions.")
    
    def queue_for_serena_save(self, namespace: str, key: str, data: Dict):
        """Queue data for Serena MCP save"""
        queue_file = self.temp_dir / 'serena_queue.jsonl'
        with open(queue_file, 'a') as f:
            f.write(json.dumps({
                'timestamp': datetime.now().isoformat(),
                'namespace': namespace,
                'key': key,
                'data': data
            }) + '\n')
    
    def log_error(self, message: str):
        """Log errors to temp log file"""
        error_log = self.temp_logs / 'synthesis_errors.log'
        with open(error_log, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")

def main():
    parser = argparse.ArgumentParser(description='Synthesize agent findings')
    parser.add_argument('--mode', choices=['immediate', 'incremental', 'phase', 'final'],
                       default='immediate', help='Synthesis mode')
    parser.add_argument('--task-id', help='Task ID for immediate synthesis')
    parser.add_argument('--agent-id', help='Agent ID for incremental synthesis')
    parser.add_argument('--session-id', help='Session ID for final synthesis')
    parser.add_argument('--temp-dir', default='/tmp/claude_session',
                       help='Temporary directory for captures')
    parser.add_argument('--use-serena', action='store_true', default=True,
                       help='Use Serena MCP for persistence')
    parser.add_argument('--persist-to-serena', action='store_true',
                       help='Force immediate persistence to Serena')
    parser.add_argument('--consolidate', action='store_true',
                       help='Consolidate and archive after phase synthesis')
    parser.add_argument('--output', help='Output file path for final synthesis')
    
    args = parser.parse_args()
    
    synthesizer = AgentFindingsSynthesizer(
        temp_dir=args.temp_dir,
        use_serena=args.use_serena
    )
    
    if args.mode == 'immediate' and args.task_id:
        synthesizer.synthesize_immediate(args.task_id)
    elif args.mode == 'incremental':
        synthesizer.synthesize_incremental(args.agent_id)
    elif args.mode == 'phase':
        synthesizer.synthesize_phase(consolidate=args.consolidate)
    elif args.mode == 'final' and args.session_id:
        synthesizer.synthesize_final(args.session_id, args.output)
    else:
        print(f"Error: Mode '{args.mode}' requires appropriate arguments")
        sys.exit(1)

if __name__ == "__main__":
    main()