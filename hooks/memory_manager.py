#!/usr/bin/env python3
"""
Memory Manager - Core hook for Serena memory operations
Optimized for speed and non-blocking operations
"""

import json
import os
import sys
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class MemoryManager:
    def __init__(self):
        self.base_path = Path('.serena/memories')
        self.categories = ['architecture', 'patterns', 'decisions', 'context', 'tasks']
        self.cache_file = self.base_path / 'cache.json'
        self.cache = self._load_cache()
        
    def _load_cache(self) -> Dict:
        """Load memory cache for fast access"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache asynchronously"""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except:
            pass  # Non-blocking - don't fail on cache errors
    
    def init(self):
        """Initialize memory structure (called on SessionStart)"""
        try:
            # Create directories
            for category in self.categories:
                (self.base_path / category).mkdir(parents=True, exist_ok=True)
            
            # Initialize session log
            session_file = self.base_path / 'context' / 'session.json'
            session_data = {
                'started': datetime.now().isoformat(),
                'mode': 'HYBRID',
                'max_agents': 5,
                'phases': []
            }
            
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            print(f"✓ Memory initialized at {self.base_path}")
            
        except Exception as e:
            # Non-blocking - just log
            print(f"Memory init notice: {e}")
    
    def pre_task(self):
        """Load relevant context before Task tool execution"""
        try:
            tool_input = json.loads(os.environ.get('TOOL_INPUT', '{}'))
            task_type = tool_input.get('type', 'unknown')
            
            # Quick context lookup from cache
            relevant_context = self._get_relevant_context(task_type)
            
            if relevant_context:
                # Save to temp file for agent access
                context_file = self.base_path / 'context' / 'current_context.json'
                with open(context_file, 'w') as f:
                    json.dump(relevant_context, f)
                
                # Just inform, don't block
                print(f"📋 Loaded {len(relevant_context)} context items for {task_type}")
            
        except Exception as e:
            # Never block execution
            pass
    
    def post_task(self):
        """Save task results and patterns to memory"""
        try:
            tool_response = json.loads(os.environ.get('TOOL_RESPONSE', '{}'))
            
            # Extract patterns asynchronously
            if 'patterns' in tool_response:
                self._save_patterns(tool_response['patterns'])
            
            # Track task metrics
            task_metrics = {
                'timestamp': datetime.now().isoformat(),
                'duration_ms': tool_response.get('duration_ms', 0),
                'agent_count': tool_response.get('agent_count', 1),
                'success': tool_response.get('status') == 'success'
            }
            
            # Append to metrics log (non-blocking)
            metrics_file = self.base_path / 'tasks' / 'metrics.jsonl'
            metrics_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(metrics_file, 'a') as f:
                f.write(json.dumps(task_metrics) + '\n')
            
            # Update cache
            self.cache['last_task'] = task_metrics
            self._save_cache()
            
            # Calculate efficiency (non-blocking)
            if task_metrics['agent_count'] > 1:
                efficiency = self._calculate_efficiency(task_metrics)
                if efficiency < 80:
                    print(f"💡 Tip: Parallel efficiency {efficiency}% - consider fewer agents")
            
        except Exception:
            pass  # Never block on post-processing
    
    def serena_sync(self):
        """Sync Serena operations with memory"""
        try:
            tool_name = os.environ.get('TOOL_NAME', '')
            operation = tool_name.split('__')[-1] if '__' in tool_name else ''
            
            if operation in ['find_symbol', 'get_symbol_dependencies']:
                # Track code navigation patterns
                nav_log = self.base_path / 'patterns' / 'navigation.jsonl'
                nav_log.parent.mkdir(parents=True, exist_ok=True)
                
                nav_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'operation': operation,
                    'input': os.environ.get('TOOL_INPUT', '')
                }
                
                with open(nav_log, 'a') as f:
                    f.write(json.dumps(nav_entry) + '\n')
            
            elif operation in ['replace_symbol_body', 'insert_before_symbol']:
                # Track refactoring patterns
                self._track_refactoring(operation)
            
        except Exception:
            pass  # Non-blocking sync
    
    def _get_relevant_context(self, task_type: str) -> Dict:
        """Quickly retrieve relevant context from cache"""
        context = {}
        
        try:
            # Check cache first
            if task_type in self.cache.get('contexts', {}):
                cache_entry = self.cache['contexts'][task_type]
                # Use cached context if fresh (< 10 minutes)
                if time.time() - cache_entry.get('timestamp', 0) < 600:
                    return cache_entry.get('data', {})
            
            # Load fresh context
            patterns_file = self.base_path / 'patterns' / f'{task_type}.json'
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    context['patterns'] = json.load(f)
            
            decisions_file = self.base_path / 'decisions' / 'recent.json'
            if decisions_file.exists():
                with open(decisions_file, 'r') as f:
                    context['decisions'] = json.load(f)
            
            # Update cache
            if 'contexts' not in self.cache:
                self.cache['contexts'] = {}
            
            self.cache['contexts'][task_type] = {
                'timestamp': time.time(),
                'data': context
            }
            
        except Exception:
            pass
        
        return context
    
    def _save_patterns(self, patterns: List[Dict]):
        """Save discovered patterns for reuse"""
        try:
            patterns_file = self.base_path / 'patterns' / 'discovered.json'
            patterns_file.parent.mkdir(parents=True, exist_ok=True)
            
            existing = []
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    existing = json.load(f)
            
            # Deduplicate using pattern hashes
            pattern_hashes = {self._hash_pattern(p) for p in existing}
            
            for pattern in patterns:
                pattern_hash = self._hash_pattern(pattern)
                if pattern_hash not in pattern_hashes:
                    existing.append(pattern)
                    pattern_hashes.add(pattern_hash)
            
            # Keep only recent patterns (last 100)
            existing = existing[-100:]
            
            with open(patterns_file, 'w') as f:
                json.dump(existing, f, indent=2)
            
        except Exception:
            pass
    
    def _track_refactoring(self, operation: str):
        """Track successful refactoring patterns"""
        try:
            refactor_log = self.base_path / 'patterns' / 'refactorings.jsonl'
            refactor_log.parent.mkdir(parents=True, exist_ok=True)
            
            entry = {
                'timestamp': datetime.now().isoformat(),
                'operation': operation,
                'input_summary': self._summarize_input()
            }
            
            with open(refactor_log, 'a') as f:
                f.write(json.dumps(entry) + '\n')
            
        except Exception:
            pass
    
    def _calculate_efficiency(self, metrics: Dict) -> int:
        """Calculate parallel execution efficiency"""
        try:
            duration = metrics.get('duration_ms', 1000)
            agents = metrics.get('agent_count', 1)
            
            # Ideal time would be duration/agents
            ideal_time = duration / agents
            
            # Efficiency is how close we got to ideal
            efficiency = int((ideal_time / duration) * 100)
            
            return min(100, efficiency)  # Cap at 100%
            
        except:
            return 100
    
    def _hash_pattern(self, pattern: Dict) -> str:
        """Generate hash for pattern deduplication"""
        pattern_str = json.dumps(pattern, sort_keys=True)
        return hashlib.md5(pattern_str.encode()).hexdigest()[:8]
    
    def _summarize_input(self) -> str:
        """Create brief summary of tool input"""
        try:
            tool_input = json.loads(os.environ.get('TOOL_INPUT', '{}'))
            # Just get the first 100 chars for summary
            input_str = json.dumps(tool_input)
            return input_str[:100] + '...' if len(input_str) > 100 else input_str
        except:
            return "unknown"

def main():
    """Main entry point"""
    manager = MemoryManager()
    
    if len(sys.argv) < 2:
        print("Usage: memory_manager.py [init|pre_task|post_task|serena_sync]")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == 'init':
        manager.init()
    elif command == 'pre_task':
        manager.pre_task()
    elif command == 'post_task':
        manager.post_task()
    elif command == 'serena_sync':
        manager.serena_sync()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()