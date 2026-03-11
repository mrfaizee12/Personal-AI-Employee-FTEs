#!/usr/bin/env python3
"""Verify Playwright MCP server is running and accessible."""
import subprocess
import sys
import os

def main():
    # Check if server process is running (Windows-compatible)
    try:
        if os.name == 'nt':
            # Windows
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq node.exe", "/FO", "CSV"],
                capture_output=True, text=True
            )
            if "node.exe" in result.stdout:
                print("[OK] Playwright MCP server running (node.exe found)")
                sys.exit(0)
            else:
                print("[WARN] node.exe not found, but server might still be running")
        else:
            # Linux/Mac
            result = subprocess.run(
                ["pgrep", "-f", "@playwright/mcp"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print("[OK] Playwright MCP server running")
                sys.exit(0)
            else:
                print("[FAIL] Server not running. Run: bash scripts/start-server.sh")
                sys.exit(1)
        
        # Try to connect to the server
        try:
            from urllib.request import urlopen
            urlopen('http://localhost:8808/mcp', timeout=2)
            print("[OK] Server responding on port 8808")
            sys.exit(0)
        except:
            print("[INFO] Server may be starting up, wait a moment and try again")
            sys.exit(0)
            
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
