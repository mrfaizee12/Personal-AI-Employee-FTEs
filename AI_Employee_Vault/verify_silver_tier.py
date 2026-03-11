"""
Silver Tier Verification Script

Tests all Silver tier components:
- Gmail Watcher
- Email MCP Server
- HITL Approval Workflow
- Plan Generator
- LinkedIn Poster
- Scheduling Helper

Usage:
    python verify_silver_tier.py
"""

import sys
import os
from pathlib import Path

def check(name: str, condition: bool, details: str = ''):
    """Print check result."""
    status = '[OK]' if condition else '[FAIL]'
    print(f'{status} {name}')
    if details:
        print(f'  {details}')
    return condition

def main():
    vault_path = Path(__file__).parent
    print('=== Silver Tier Verification ===\n')
    
    passed = 0
    total = 0
    
    # Check 1: Gmail Watcher
    total += 1
    gmail_watcher = vault_path / 'watchers' / 'gmail_watcher.py'
    if check('Gmail Watcher Script', gmail_watcher.exists(), 
             str(gmail_watcher)):
        passed += 1
    
    # Check 2: Email MCP Server
    total += 1
    email_mcp = vault_path / 'mcp_servers' / 'email_mcp.py'
    if check('Email MCP Server', email_mcp.exists(),
             str(email_mcp)):
        passed += 1
    
    # Check 3: LinkedIn MCP Server
    total += 1
    linkedin_mcp = vault_path / 'mcp_servers' / 'linkedin_mcp.py'
    if check('LinkedIn MCP Server', linkedin_mcp.exists(),
             str(linkedin_mcp)):
        passed += 1
    
    # Check 4: Scheduling Helper
    total += 1
    scheduling_helper = vault_path / 'scheduling_helper.py'
    if check('Scheduling Helper', scheduling_helper.exists(),
             str(scheduling_helper)):
        passed += 1
    
    # Check 5: Skills Directory
    total += 1
    skills_dir = vault_path.parent / '.qwen' / 'skills'
    skills = ['gmail-watcher', 'email-mcp-server', 'hitl-approval-workflow', 
              'plan-generator', 'linkedin-poster']
    skills_exist = all((skills_dir / s).exists() for s in skills)
    if check('Silver Tier Skills', skills_exist,
             f'Checking: {", ".join(skills)}'):
        passed += 1
    
    # Check 6: Required Folders
    total += 1
    folders = ['Plans', 'Pending_Approval', 'Approved', 'Rejected']
    folders_exist = all((vault_path / f).exists() for f in folders)
    if check('Required Folders', folders_exist,
             f'Checking: {", ".join(folders)}'):
        passed += 1
    
    # Check 7: Orchestrator (Silver Tier)
    total += 1
    orchestrator = vault_path / 'orchestrator.py'
    if orchestrator.exists():
        content = orchestrator.read_text(encoding='utf-8')
        has_plans = 'self.plans' in content
        has_hitl = 'execute_approved_action' in content
        if check('Orchestrator (Silver Tier)', has_plans and has_hitl,
                 'Plan support + HITL execution'):
            passed += 1
    else:
        check('Orchestrator (Silver Tier)', False, 'File not found')
    
    # Check 8: Requirements
    total += 1
    requirements = vault_path / 'requirements.txt'
    if requirements.exists():
        content = requirements.read_text(encoding='utf-8')
        has_google = 'google-api-python-client' in content
        has_mcp = 'mcp' in content
        has_aps = 'APScheduler' in content
        if check('Requirements (Silver Tier)', has_google and has_mcp and has_aps,
                 'Gmail + MCP + APScheduler'):
            passed += 1
    else:
        check('Requirements (Silver Tier)', False, 'File not found')
    
    # Check 9: Documentation
    total += 1
    silver_guide = vault_path / 'SILVER_TIER_GUIDE.md'
    silver_summary = vault_path / 'SILVER_TIER_SUMMARY.md'
    if check('Silver Tier Documentation', 
             silver_guide.exists() and silver_summary.exists(),
             'Guide + Summary'):
        passed += 1
    
    # Check 10: Python Dependencies
    total += 1
    try:
        import google.api
        has_google = True
    except ImportError:
        has_google = False
    
    try:
        import mcp
        has_mcp = True
    except ImportError:
        has_mcp = False
    
    try:
        import apscheduler
        has_aps = True
    except ImportError:
        has_aps = False
    
    deps_installed = has_google and has_mcp and has_aps
    details = []
    if has_google: details.append('Google API OK')
    else: details.append('Google API FAIL (run: pip install google-api-python-client)')
    if has_mcp: details.append('MCP OK')
    else: details.append('MCP FAIL (run: pip install mcp)')
    if has_aps: details.append('APScheduler OK')
    else: details.append('APScheduler FAIL (run: pip install apscheduler)')
    
    if check('Python Dependencies', deps_installed,
             ', '.join(details)):
        passed += 1
    
    # Summary
    print('\n=== Summary ===')
    print(f'{passed}/{total} checks passed')
    
    if passed == total:
        print('\n[SUCCESS] Silver Tier verification PASSED!')
        print('\nNext steps:')
        print('1. Install dependencies: pip install -r requirements.txt')
        print('2. Setup Gmail API: python watchers/gmail_watcher.py --authenticate')
        print('3. Start services: See SILVER_TIER_SUMMARY.md')
        return 0
    else:
        print('\n[WARNING] Some checks failed. Review the output above.')
        failed = total - passed
        print(f'\nFailed: {failed}')
        return 1

if __name__ == '__main__':
    sys.exit(main())
