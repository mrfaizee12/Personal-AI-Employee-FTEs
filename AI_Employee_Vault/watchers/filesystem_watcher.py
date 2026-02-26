"""
File System Watcher - Monitors a drop folder for new files.

This is the simplest watcher for the Bronze tier.
Users can drop any file into the Inbox folder, and it will be
moved to Needs_Action with metadata for Claude to process.

Supported files: All files EXCEPT .log files (system logs)
- .txt files: Plain text documents
- .md files: Markdown documents
- .pdf, .docx, etc.: Binary files (copied as-is)
- .log files: Ignored (system logs)

Usage:
    python filesystem_watcher.py /path/to/vault
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

# Add watchers directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_watcher import BaseWatcher


class FileSystemWatcher(BaseWatcher):
    """Watches a folder for new files and creates action files."""
    
    def __init__(self, vault_path: str, check_interval: int = 30):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        self.inbox = self.vault_path / 'Inbox'
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.logger.info(f'Watching folder: {self.inbox}')
    
    def check_for_updates(self) -> list:
        """Check for new files in the Inbox folder."""
        files = []
        try:
            for file_path in self.inbox.iterdir():
                if file_path.is_file() and file_path.suffix != '.log':
                    file_id = f"{file_path.stem}_{file_path.stat().st_mtime}"
                    if file_id not in self.processed_ids:
                        files.append(file_path)
                        self.processed_ids.add(file_id)
        except Exception as e:
            self.logger.error(f'Error checking inbox: {e}')
        return files
    
    def create_action_file(self, file_path: Path) -> Path:
        """
        Create an action file for the dropped file.
        
        Copies the file to Needs_Action and creates a metadata .md file.
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = f"{timestamp}_{file_path.name}"
        
        # Copy the file to Needs_Action
        dest = self.needs_action / f'FILE_{unique_id}'
        shutil.copy2(file_path, dest)
        
        # Create metadata file
        meta_path = self.needs_action / f'FILE_{unique_id}.meta.md'
        file_size = file_path.stat().st_size
        
        content = f'''---
type: file_drop
original_name: {file_path.name}
size: {file_size} bytes
dropped: {datetime.now().isoformat()}
status: pending
source_file: {dest.name}
---

# File Dropped for Processing

**Original File:** `{file_path.name}`  
**Size:** {file_size} bytes  
**Dropped At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Suggested Actions

- [ ] Review file contents
- [ ] Determine required action
- [ ] Execute action or create plan
- [ ] Move to /Done when complete

## Notes

*Add your analysis here...*

---
*Created by FileSystemWatcher*
'''
        meta_path.write_text(content, encoding='utf-8')
        
        # Remove original from inbox
        file_path.unlink()
        
        self.logger.info(f'Created action file for: {file_path.name}')
        return meta_path


def main():
    """Entry point for running the watcher."""
    if len(sys.argv) < 2:
        # Default to vault in same directory
        vault_path = Path(__file__).parent
    else:
        vault_path = Path(sys.argv[1])
    
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    watcher = FileSystemWatcher(str(vault_path), check_interval=30)
    watcher.run()


if __name__ == '__main__':
    main()
