#!/usr/bin/env python3
"""
Documentation Cache - Cache Context7 responses for offline use
Fast, non-blocking caching
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path

class DocCache:
    def __init__(self):
        self.cache_path = Path('.serena/memories/documentation')
        self.cache_index = self.cache_path / 'index.json'
        self.max_cache_size_mb = 50  # Limit cache size
        
    def cache_documentation(self):
        """Cache Context7 documentation responses"""
        try:
            tool_input = json.loads(os.environ.get('TOOL_INPUT', '{}'))
            tool_response = os.environ.get('TOOL_RESPONSE', '')
            
            # Extract library info
            library = tool_input.get('library', 'unknown')
            version = tool_input.get('version', 'latest')
            
            # Create cache key
            cache_key = f"{library}_{version}"
            cache_hash = hashlib.md5(cache_key.encode()).hexdigest()[:8]
            
            # Save documentation
            self.cache_path.mkdir(parents=True, exist_ok=True)
            doc_file = self.cache_path / f"{cache_hash}.json"
            
            doc_data = {
                'library': library,
                'version': version,
                'cached_at': datetime.now().isoformat(),
                'content': tool_response
            }
            
            with open(doc_file, 'w') as f:
                json.dump(doc_data, f)
            
            # Update index
            self._update_index(cache_key, cache_hash)
            
            # Quick size check (non-blocking)
            self._check_cache_size()
            
            print(f"📚 Cached {library}@{version} docs")
            
        except Exception:
            # Never block on caching
            pass
    
    def _update_index(self, cache_key: str, cache_hash: str):
        """Update cache index"""
        try:
            index = {}
            if self.cache_index.exists():
                with open(self.cache_index, 'r') as f:
                    index = json.load(f)
            
            index[cache_key] = {
                'hash': cache_hash,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.cache_index, 'w') as f:
                json.dump(index, f, indent=2)
                
        except:
            pass
    
    def _check_cache_size(self):
        """Quick cache size check"""
        try:
            # Fast approximation - just count files
            cache_files = list(self.cache_path.glob('*.json'))
            
            if len(cache_files) > 100:  # Arbitrary limit
                # Remove oldest files
                cache_files.sort(key=lambda x: x.stat().st_mtime)
                for old_file in cache_files[:20]:  # Remove 20 oldest
                    old_file.unlink()
                    
        except:
            pass

def main():
    cache = DocCache()
    cache.cache_documentation()

if __name__ == "__main__":
    main()