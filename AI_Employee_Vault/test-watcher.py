"""
Test script for File System Watcher - runs a single cycle.
"""

import sys
from pathlib import Path

# Add watchers directory to path
sys.path.insert(0, str(Path(__file__).parent / 'watchers'))

from filesystem_watcher import FileSystemWatcher

if __name__ == '__main__':
    vault_path = Path(__file__).parent if len(sys.argv) < 2 else Path(sys.argv[1])
    
    print(f'Testing FileSystemWatcher...')
    print(f'Vault: {vault_path}')
    
    watcher = FileSystemWatcher(str(vault_path), check_interval=1)
    
    # Run a single check cycle
    print('Checking for files...')
    items = watcher.check_for_updates()
    
    if items:
        print(f'Found {len(items)} file(s):')
        for item in items:
            print(f'  - {item.name}')
            action_file = watcher.create_action_file(item)
            print(f'    Created: {action_file.name}')
    else:
        print('No files found in Inbox')
    
    print('\nTest complete!')
