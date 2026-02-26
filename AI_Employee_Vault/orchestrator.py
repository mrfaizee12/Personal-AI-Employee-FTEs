"""
Orchestrator - Master process for the AI Employee.

This script:
1. Monitors the Needs_Action folder for new items
2. Triggers Qwen Code to process pending items
3. Updates the Dashboard.md with current status
4. Manages the overall workflow

Usage:
    python orchestrator.py /path/to/vault
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
import re


class Orchestrator:
    """Main orchestrator for the AI Employee."""
    
    def __init__(self, vault_path: str):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.dashboard = self.vault_path / 'Dashboard.md'
        self.logs_dir = self.vault_path / 'Logs'
        
        # Ensure directories exist
        for dir_path in [self.needs_action, self.pending_approval, 
                         self.approved, self.done, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def count_files(self, directory: Path) -> int:
        """Count files in a directory."""
        try:
            return len([f for f in directory.iterdir() if f.is_file()])
        except Exception:
            return 0
    
    def update_dashboard(self):
        """Update the Dashboard.md with current status."""
        if not self.dashboard.exists():
            return
        
        pending_count = self.count_files(self.needs_action)
        approval_count = self.count_files(self.pending_approval)
        done_today = self._count_files_today(self.done)
        
        content = self.dashboard.read_text(encoding='utf-8')
        
        # Update pending tasks count
        content = re.sub(
            r'\| Pending Tasks \|.*\|',
            f'| Pending Tasks | {pending_count} |',
            content
        )
        
        # Update awaiting approval count
        content = re.sub(
            r'\| Awaiting Approval \|.*\|',
            f'| Awaiting Approval | {approval_count} |',
            content
        )
        
        # Update completed today
        content = re.sub(
            r'\| Completed Today \|.*\|',
            f'| Completed Today | {done_today} |',
            content
        )
        
        # Update system status
        content = re.sub(
            r'\| Watchers \|.*\|',
            '| Watchers | 🟢 Running |',
            content
        )
        
        content = re.sub(
            r'\| Orchestrator \|.*\|',
            '| Orchestrator | 🟢 Running |',
            content
        )
        
        # Update last_updated timestamp
        now = datetime.now().isoformat()
        content = re.sub(
            r'last_updated:.*',
            f'last_updated: {now}',
            content
        )
        
        # Update last sync
        content = re.sub(
            r'\| Last Sync \|.*\|',
            f'| Last Sync | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} |',
            content
        )
        
        self.dashboard.write_text(content, encoding='utf-8')
    
    def _count_files_today(self, directory: Path) -> int:
        """Count files created/modified today."""
        today = datetime.now().date()
        count = 0
        try:
            for f in directory.iterdir():
                if f.is_file():
                    mtime = datetime.fromtimestamp(f.stat().st_mtime).date()
                    if mtime == today:
                        count += 1
        except Exception:
            pass
        return count
    
    def get_pending_items(self) -> list:
        """Get list of pending items in Needs_Action."""
        items = []
        try:
            for f in self.needs_action.iterdir():
                if f.is_file() and f.suffix == '.md':
                    items.append(f)
        except Exception as e:
            print(f'Error reading Needs_Action: {e}')
        return items
    
    def process_with_qwen(self, items: list):
        """
        Process items using Qwen Code.

        This triggers Qwen Code to read the items and create plans.
        For Bronze tier, this is a simple trigger that can be enhanced
        in higher tiers with the Ralph Wiggum loop.
        """
        if not items:
            return

        print(f'\n[QWEN] Triggering Qwen Code to process {len(items)} item(s)...')

        # Create a prompt for Qwen
        prompt = self._create_qwen_prompt(items)

        # For Bronze tier, we just log that Qwen should be triggered
        # In higher tiers, this would actually call Qwen Code API
        # or use the Ralph Wiggum loop

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'qwen_trigger',
            'items_count': len(items),
            'items': [str(i.name) for i in items],
            'status': 'pending_qwen_execution'
        }

        self._log_action(log_entry)

        print('[OK] Qwen Code trigger logged')
        print('  To process manually, run:')
        print(f'  qwen --cd "{self.vault_path}"')
        print('  Then ask Qwen to "Process all files in /Needs_Action"')

    def _create_qwen_prompt(self, items: list) -> str:
        """Create a prompt for Qwen Code."""
        item_list = '\n'.join([f'- {i.name}' for i in items])

        return f'''
I have {len(items)} item(s) in /Needs_Action that need processing:

{item_list}

Please:
1. Read each file in /Needs_Action
2. Understand what action is required
3. Create a Plan.md for complex tasks
4. Execute simple tasks directly
5. Create approval requests for sensitive actions
6. Move completed items to /Done
7. Update the Dashboard.md

Remember to follow the Company_Handbook.md rules.
'''
    
    def _log_action(self, entry: dict):
        """Log an action to the logs directory."""
        log_file = self.logs_dir / f'orchestrator_{datetime.now().strftime("%Y-%m-%d")}.json'
        
        # Append to existing log or create new
        if log_file.exists():
            content = log_file.read_text(encoding='utf-8')
            # Simple append (for production, use proper JSON array handling)
            content = content.rstrip(']\n') + ',\n  ' + str(entry).replace("'", '"') + '\n]'
        else:
            content = '[\n  ' + str(entry).replace("'", '"') + '\n]'
        
        log_file.write_text(content, encoding='utf-8')
    
    def check_approved_actions(self):
        """Check for approved actions that need execution."""
        approved_items = list(self.approved.iterdir())
        if not approved_items:
            return
        
        print(f'\n[APPROVALS] Found {len(approved_items)} approved action(s)')
        print('  In Bronze tier, manual execution is required')
        print('  Review approved files and execute actions manually')
        
        for item in approved_items:
            print(f'  - {item.name}')
    
    def run_once(self):
        """Run a single orchestration cycle."""
        print('\n[ORCHESTRATOR] Running orchestration cycle...')
        print(f'   Vault: {self.vault_path}')
        
        # Update dashboard
        self.update_dashboard()
        print('[OK] Dashboard updated')
        
        # Check for pending items
        pending = self.get_pending_items()
        if pending:
            print(f'[INFO] Found {len(pending)} pending item(s)')
            self.process_with_qwen(pending)
        else:
            print('[OK] No pending items')
        
        # Check for approved actions
        self.check_approved_actions()
        
        print('[OK] Orchestration cycle complete\n')
    
    def run_continuous(self, interval: int = 60):
        """
        Run orchestration continuously.
        
        Args:
            interval: Seconds between cycles (default: 60)
        """
        import time
        
        print(f'[START] Starting continuous orchestration (interval: {interval}s)')
        print('   Press Ctrl+C to stop\n')
        
        try:
            while True:
                self.run_once()
                time.sleep(interval)
        except KeyboardInterrupt:
            print('\n[STOP] Stopped by user')
            # Update dashboard to show stopped status
            self.update_dashboard()


def main():
    """Entry point for the orchestrator."""
    if len(sys.argv) < 2:
        # Default to vault in same directory
        vault_path = Path(__file__).parent
    else:
        vault_path = Path(sys.argv[1])
    
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    orchestrator = Orchestrator(str(vault_path))
    
    # Check for --continuous flag
    if len(sys.argv) > 2 and sys.argv[2] == '--continuous':
        orchestrator.run_continuous(interval=60)
    else:
        orchestrator.run_once()


if __name__ == '__main__':
    main()
