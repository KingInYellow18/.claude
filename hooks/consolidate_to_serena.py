#!/usr/bin/env python3
"""Consolidates temp data to Serena MCP memory"""
import json
import sys
from pathlib import Path
import subprocess

def save_to_serena(namespace, key, data):
    """Use Serena MCP to save memory"""
    # This would call Serena's save_memory MCP command
    # via Claude Code's MCP interface
    cmd = [
        "npx", "@modelcontextprotocol/cli",
        "call", "serena", "save_memory",
        json.dumps({
            "namespace": namespace,
            "key": key,
            "data": data
        })
    ]
    subprocess.run(cmd, capture_output=True)

# Rest of consolidation logic...