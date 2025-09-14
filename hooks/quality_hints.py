#!/usr/bin/env python3
"""
Quality Hints - Non-blocking quality suggestions
Informs but never blocks execution
"""

import json
import os
import re
import sys

class QualityHints:
    def __init__(self):
        self.hints_given = set()
        self.session_file = '.serena/memories/context/quality_hints.json'
        
    def check_code_quality(self):
        """Provide quality hints without blocking"""
        try:
            tool_input = json.loads(os.environ.get('TOOL_INPUT', '{}'))
            file_path = tool_input.get('file_path', '')
            content = tool_input.get('content', '')
            
            if not content:
                return
            
            hints = []
            
            # Check for common issues (but don't block)
            if 'TODO' in content or 'FIXME' in content:
                hints.append("📝 Found TODO/FIXME - remember to address before production")
            
            if 'console.log' in content and not file_path.endswith('.test.js'):
                hints.append("🔍 console.log detected - consider using proper logging")
            
            if 'any' in content and file_path.endswith('.ts'):
                hints.append("📊 TypeScript 'any' type found - consider specific types")
            
            # Check for potential security issues (inform only)
            if re.search(r'(password|secret|token|key)\s*=\s*["\'][^"\']+["\']', content):
                hints.append("🔐 Possible hardcoded secret - use environment variables")
            
            # Check for missing error handling
            if 'catch' not in content and ('async' in content or '.then' in content):
                hints.append("⚡ Async code without error handling detected")
            
            # Output hints if any (but don't block)
            if hints:
                print("💡 Quality hints (non-blocking):")
                for hint in hints:
                    print(f"   {hint}")
                
                # Save hints for later review
                self._save_hints(file_path, hints)
            
        except Exception:
            # Never fail
            pass
    
    def _save_hints(self, file_path: str, hints: list):
        """Save hints for later review"""
        try:
            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            
            hints_data = {}
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    hints_data = json.load(f)
            
            if file_path not in hints_data:
                hints_data[file_path] = []
            
            hints_data[file_path].extend(hints)
            
            with open(self.session_file, 'w') as f:
                json.dump(hints_data, f, indent=2)
                
        except:
            pass

def main():
    hints = QualityHints()
    hints.check_code_quality()

if __name__ == "__main__":
    main()