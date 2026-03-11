"""
Scheduling Helper - Run AI Employee tasks on schedule.

Supports:
- Windows Task Scheduler
- Linux/Mac cron
- Python APScheduler (cross-platform)

Usage:
    python scheduling_helper.py install --task daily_briefing --time 08:00
    python scheduling_helper.py install --task orchestrator --interval 60
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

# Check for APScheduler
try:
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False


class SchedulerHelper:
    """Helper for scheduling AI Employee tasks."""
    
    def __init__(self, vault_path: str):
        self.vault = Path(vault_path)
        self.scripts_dir = self.vault
        self.logs_dir = self.vault / 'Logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def install_windows_task(self, task_name: str, trigger_type: str,
                             trigger_value: str) -> bool:
        """Install task in Windows Task Scheduler."""
        if os.name != 'nt':
            print('Not a Windows system')
            return False
        
        script = self._get_script_for_task(task_name)
        if not script:
            return False
        
        # Create XML for task scheduler
        xml_content = self._create_windows_task_xml(
            task_name, script, trigger_type, trigger_value)
        
        xml_path = self.logs_dir / f'{task_name}.xml'
        xml_path.write_text(xml_content)
        
        # Import task
        try:
            subprocess.run([
                'schtasks', '/Create', '/TN', f'AI_Employee_{task_name}',
                '/XML', str(xml_path), '/F'
            ], check=True)
            print(f'✓ Task installed: AI_Employee_{task_name}')
            return True
        except subprocess.CalledProcessError as e:
            print(f'✗ Failed to install task: {e}')
            return False
    
    def install_cron_job(self, task_name: str, trigger_type: str,
                         trigger_value: str) -> bool:
        """Install cron job on Linux/Mac."""
        if os.name == 'nt':
            print('Not a Linux/Mac system')
            return False
        
        script = self._get_script_for_task(task_name)
        if not script:
            return False
        
        cron_schedule = self._get_cron_schedule(trigger_type, trigger_value)
        cron_line = f'{cron_schedule} cd {self.vault} && python {script}\n'
        
        print(f'Add this to your crontab (run: crontab -e):')
        print(cron_line)
        print('\nOr manually add with:')
        print(f'echo "{cron_line}" | crontab -')
        
        return True
    
    def run_with_apscheduler(self, task_name: str, trigger_type: str,
                             trigger_value: str):
        """Run tasks using APScheduler (cross-platform)."""
        if not APSCHEDULER_AVAILABLE:
            print('APScheduler not installed. Run: pip install apscheduler')
            return
        
        scheduler = BlockingScheduler()
        
        # Add job based on trigger type
        if trigger_type == 'interval':
            trigger = IntervalTrigger(seconds=int(trigger_value))
        elif trigger_type == 'cron':
            hour, minute = trigger_value.split(':')
            trigger = CronTrigger(hour=int(hour), minute=int(minute))
        else:
            print(f'Unknown trigger type: {trigger_type}')
            return
        
        job_func = self._get_job_function(task_name)
        if not job_func:
            return
        
        scheduler.add_job(job_func, trigger)
        
        print(f'Starting scheduler for {task_name}...')
        print(f'Trigger: {trigger_type} = {trigger_value}')
        print('Press Ctrl+C to stop')
        
        try:
            scheduler.start()
        except KeyboardInterrupt:
            print('\nScheduler stopped')
    
    def _get_script_for_task(self, task_name: str) -> str:
        """Get script path for task name."""
        scripts = {
            'orchestrator': 'orchestrator.py . --continuous',
            'gmail_watcher': 'watchers/gmail_watcher.py .',
            'filesystem_watcher': 'watchers/filesystem_watcher.py .',
            'daily_briefing': 'scripts/generate_briefing.py',
            'linkedin_post': 'mcp_servers/linkedin_mcp.py --post-daily'
        }
        return scripts.get(task_name)
    
    def _create_windows_task_xml(self, task_name: str, script: str,
                                  trigger_type: str, trigger_value: str):
        """Create XML for Windows Task Scheduler."""
        if trigger_type == 'interval':
            repetition = f'<Repetition Interval="PT{trigger_value}S" Duration="PT24H"/>'
            schedule = ''
        else:
            hour, minute = trigger_value.split(':')
            repetition = ''
            schedule = f'<StartBoundary>{datetime.now().date()}T{hour}:{minute}:00</StartBoundary>'
        
        return f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>AI Employee - {task_name}</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      {schedule}
      {repetition}
      <Enabled>true</Enabled>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>python</Command>
      <Arguments>{script}</Arguments>
      <WorkingDirectory>{self.vault}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
    
    def _get_cron_schedule(self, trigger_type: str, trigger_value: str) -> str:
        """Get cron schedule string."""
        if trigger_type == 'interval':
            seconds = int(trigger_value)
            if seconds % 3600 == 0:
                hours = seconds // 3600
                return f'0 */{hours} * * *'
            elif seconds % 60 == 0:
                minutes = seconds // 60
                return f'*/{minutes} * * * *'
            else:
                return f'* * * * *'  # Every minute
        elif trigger_type == 'cron':
            hour, minute = trigger_value.split(':')
            return f'{minute} {hour} * * *'
        return '* * * * *'
    
    def _get_job_function(self, task_name: str):
        """Get job function for task."""
        def orchestrator_job():
            print(f'[{datetime.now()}] Running orchestrator...')
            subprocess.run(['python', 'orchestrator.py', '.'], cwd=self.vault)
        
        def briefing_job():
            print(f'[{datetime.now()}] Generating daily briefing...')
            # Would call Qwen Code to generate briefing
        
        jobs = {
            'orchestrator': orchestrator_job,
            'daily_briefing': briefing_job
        }
        return jobs.get(task_name)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Employee Scheduling Helper')
    parser.add_argument('command', choices=['install', 'run'], 
                       help='Command to run')
    parser.add_argument('--task', required=True, help='Task name')
    parser.add_argument('--trigger', default='interval', 
                       help='Trigger type: interval, cron')
    parser.add_argument('--value', default='60', 
                       help='Trigger value: seconds or HH:MM')
    parser.add_argument('--vault', default='.', help='Vault path')
    parser.add_argument('--platform', choices=['auto', 'windows', 'linux'], 
                       default='auto', help='Target platform')
    
    args = parser.parse_args()
    
    helper = SchedulerHelper(args.vault)
    
    if args.command == 'install':
        platform = args.platform
        if platform == 'auto':
            platform = 'windows' if os.name == 'nt' else 'linux'
        
        if platform == 'windows':
            helper.install_windows_task(args.task, args.trigger, args.value)
        else:
            helper.install_cron_job(args.task, args.trigger, args.value)
    
    elif args.command == 'run':
        helper.run_with_apscheduler(args.task, args.trigger, args.value)


if __name__ == '__main__':
    main()
