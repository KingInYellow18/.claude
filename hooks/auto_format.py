#!/usr/bin/env python3
"""
Auto Format - Non-blocking background formatting
Runs formatters but doesn't block on failure
"""

import json
import os
import subprocess
import threading
from pathlib import Path

class AutoFormatter:
    def __init__(self):
        self.supported_extensions = {
            '.ts': ['prettier', 'eslint'],
            '.tsx': ['prettier', 'eslint'],
            '.js': ['prettier', 'eslint'],
            '.jsx': ['prettier', 'eslint'],
            '.py': ['black', 'ruff'],
            '.json': ['prettier'],
            '.yml': ['prettier'],
            '.yaml': ['prettier'],
            '.css': ['prettier'],
            '.scss': ['prettier'],
            '.md': ['prettier']
        }
        
    def format_file(self):
        """Format file in background without blocking"""
        try:
            tool_input = json.loads(os.environ.get('TOOL_INPUT', '{}'))
            file_path = tool_input.get('file_path', '')
            
            if not file_path:
                return
            
            # Get file extension
            ext = Path(file_path).suffix.lower()
            
            if ext not in self.supported_extensions:
                return
            
            # Run formatters in background thread
            thread = threading.Thread(
                target=self._run_formatters,
                args=(file_path, ext),
                daemon=True
            )
            thread.start()
            
            print(f"🎨 Formatting {file_path} in background...")
            
        except Exception:
            # Never block
            pass
    
    def _run_formatters(self, file_path: str, ext: str):
        """Run formatters in background thread"""
        formatters = self.supported_extensions.get(ext, [])
        
        for formatter in formatters:
            try:
                if formatter == 'prettier':
                    self._run_prettier(file_path)
                elif formatter == 'eslint':
                    self._run_eslint(file_path)
                elif formatter == 'black':
                    self._run_black(file_path)
                elif formatter == 'ruff':
                    self._run_ruff(file_path)
            except:
                # Silently continue if formatter fails
                pass
    
    def _run_prettier(self, file_path: str):
        """Run Prettier formatter"""
        try:
            # Check if prettier exists
            result = subprocess.run(
                ['npx', 'prettier', '--version'],
                capture_output=True,
                timeout=2
            )
            
            if result.returncode == 0:
                # Format the file
                subprocess.run(
                    ['npx', 'prettier', '--write', file_path],
                    capture_output=True,
                    timeout=5
                )
        except:
            pass
    
    def _run_eslint(self, file_path: str):
        """Run ESLint with auto-fix"""
        try:
            # Check if eslint exists
            result = subprocess.run(
                ['npx', 'eslint', '--version'],
                capture_output=True,
                timeout=2
            )
            
            if result.returncode == 0:
                # Fix the file
                subprocess.run(
                    ['npx', 'eslint', '--fix', file_path],
                    capture_output=True,
                    timeout=5
                )
        except:
            pass
    
    def _run_black(self, file_path: str):
        """Run Black formatter for Python"""
        try:
            subprocess.run(
                ['black', '--quiet', file_path],
                capture_output=True,
                timeout=5
            )
        except:
            pass
    
    def _run_ruff(self, file_path: str):
        """Run Ruff linter/formatter for Python"""
        try:
            subprocess.run(
                ['ruff', 'check', '--fix', '--quiet', file_path],
                capture_output=True,
                timeout=5
            )
        except:
            pass

def main():
    formatter = AutoFormatter()
    formatter.format_file()

if __name__ == "__main__":
    main()