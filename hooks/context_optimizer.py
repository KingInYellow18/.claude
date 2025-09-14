#!/usr/bin/env python3
"""
Context Optimizer - Smart context management before compaction
Preserves important context while pruning redundant information
"""

import json
import os
from datetime import datetime
from pathlib import Path

class ContextOptimizer:
    def __init__(self):
        self.memory_path = Path('.serena/memories/context')
        self.priority_patterns = [
            'architecture',
            'decision',
            'error',
            'pattern',
            'TODO',
            'FIXME',
            'critical',
            'important'
        ]
        
    def optimize(self):
        """Optimize context before compaction"""
        try:
            # Get context size from environment
            context_size = int(os.environ.get('CONTEXT_SIZE', '0'))
            max_context = int(os.environ.get('MAX_CONTEXT', '200000'))
            
            usage_percent = (context_size / max_context) * 100
            
            if usage_percent < 70:
                print(f"📊 Context at {usage_percent:.1f}% - no optimization needed")
                return
            
            print(f"🔄 Optimizing context ({usage_percent:.1f}% used)...")
            
            # Save important context before compaction
            self._preserve_critical_context()
            
            # Suggest what can be safely removed
            self._identify_redundant_context()
            
            # Update optimization metrics
            self._update_metrics(context_size, max_context)
            
        except Exception as e:
            # Non-blocking - just log
            print(f"Context optimization notice: {e}")
    
    def _preserve_critical_context(self):
        """Save critical context that must survive compaction"""
        try:
            critical = {
                'timestamp': datetime.now().isoformat(),
                'preserved_items': []
            }
            
            # Check for architecture decisions
            arch_file = Path('.serena/memories/architecture/current.json')
            if arch_file.exists():
                with open(arch_file, 'r') as f:
                    arch_data = json.load(f)
                    critical['preserved_items'].append({
                        'type': 'architecture',
                        'summary': self._summarize_data(arch_data)
                    })
            
            # Check for recent decisions
            decisions_file = Path('.serena/memories/decisions/recent.json')
            if decisions_file.exists():
                with open(decisions_file, 'r') as f:
                    decisions = json.load(f)
                    critical['preserved_items'].append({
                        'type': 'decisions',
                        'count': len(decisions)
                    })
            
            # Save critical context
            critical_file = self.memory_path / 'critical_preserved.json'
            critical_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(critical_file, 'w') as f:
                json.dump(critical, f, indent=2)
            
            print(f"   ✓ Preserved {len(critical['preserved_items'])} critical items")
            
        except:
            pass
    
    def _identify_redundant_context(self):
        """Identify context that can be safely removed"""
        try:
            suggestions = []
            
            # Check for old test results
            test_results = Path('.serena/memories/tasks/test_results')
            if test_results.exists():
                old_tests = list(test_results.glob('*.json'))
                if len(old_tests) > 5:
                    suggestions.append(f"Old test results ({len(old_tests)-5} files)")
            
            # Check for duplicate patterns
            patterns_file = Path('.serena/memories/patterns/discovered.json')
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    patterns = json.load(f)
                    if len(patterns) > 50:
                        suggestions.append(f"Excess patterns ({len(patterns)-50} items)")
            
            # Log suggestions
            if suggestions:
                print("   💡 Can safely compact:")
                for suggestion in suggestions:
                    print(f"      - {suggestion}")
            
        except:
            pass
    
    def _update_metrics(self, context_size: int, max_context: int):
        """Track optimization metrics"""
        try:
            metrics_file = self.memory_path / 'optimization_metrics.jsonl'
            metrics_file.parent.mkdir(parents=True, exist_ok=True)
            
            metric = {
                'timestamp': datetime.now().isoformat(),
                'context_size': context_size,
                'max_context': max_context,
                'usage_percent': round((context_size / max_context) * 100, 2)
            }
            
            with open(metrics_file, 'a') as f:
                f.write(json.dumps(metric) + '\n')
            
        except:
            pass
    
    def _summarize_data(self, data: dict) -> str:
        """Create brief summary of data"""
        try:
            # Just get key counts for summary
            if isinstance(data, dict):
                return f"{len(data)} items"
            elif isinstance(data, list):
                return f"{len(data)} entries"
            else:
                return "data present"
        except:
            return "unknown"

def main():
    optimizer = ContextOptimizer()
    optimizer.optimize()

if __name__ == "__main__":
    main()