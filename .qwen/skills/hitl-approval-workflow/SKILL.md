---
name: hitl-approval-workflow
description: |
  Human-in-the-Loop approval workflow for sensitive actions.
  Creates approval request files, monitors /Approved/ folder,
  and executes actions after human approval.
---

# HITL Approval Workflow

Human-in-the-Loop pattern for sensitive actions requiring approval.

## When to Use Approval

| Action Type | Auto-Approve | Require Approval |
|-------------|-------------|------------------|
| Email to known contact | ✅ Yes | New contact |
| Payment < $50 recurring | ✅ Yes | New payee or ≥ $50 |
| Social media post | ✅ Scheduled | Replies/DMs |
| File create/read | ✅ Yes | Delete/move |

## Workflow

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│   Qwen      │────▶│  Create Approval│────▶│   Human     │
│  Detects    │     │  Request File   │     │   Reviews   │
│   Action    │     │  in Pending/    │     │   & Moves   │
└─────────────┘     └─────────────────┘     └──────┬──────┘
                                                   │
                    ┌─────────────────┐            │
                    │   Execute       │◀───────────┘
                    │   Action via    │     ┌──────┴──────┐
                    │   MCP Server    │     │ /Approved/  │
                    └─────────────────┘     │ /Rejected/  │
                                            └─────────────┘
```

## Approval File Format

```markdown
---
type: approval_request
action: email_send
to: client@example.com
subject: Invoice #1234
amount: 1500.00
created: 2026-02-27T10:30:00Z
expires: 2026-02-28T10:30:00Z
status: pending
---

# Approval Required

**Action:** Send Email  
**To:** client@example.com  
**Subject:** Invoice #1234  
**Amount:** $1,500.00

## Details

Please find attached your invoice for January 2026.

## To Approve

Move this file to `/Approved/` folder.

## To Reject

Move this file to `/Rejected/` folder with reason.

---
*Created by AI Employee*
```

## Usage

### 1. Create Approval Request

Qwen Code creates file in `/Pending_Approval/`:

```bash
# File: Pending_Approval/APPROVAL_email_client_a.md
```

### 2. Human Reviews

User opens file, reviews details, then:
- **Approve:** Move to `/Approved/`
- **Reject:** Move to `/Rejected/` (add reason)

### 3. Orchestrator Executes

```python
# Orchestrator detects file in /Approved/
# Calls appropriate MCP server
# Logs result
# Moves file to /Done/
```

## Python Implementation

```python
from pathlib import Path
from datetime import datetime

class ApprovalWorkflow:
    def __init__(self, vault_path: str):
        self.vault = Path(vault_path)
        self.pending = self.vault / 'Pending_Approval'
        self.approved = self.vault / 'Approved'
        self.rejected = self.vault / 'Rejected'
    
    def create_request(self, action_type: str, details: dict) -> Path:
        """Create approval request file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"APPROVAL_{action_type}_{timestamp}.md"
        filepath = self.pending / filename
        
        content = f'''---
type: approval_request
action: {action_type}
created: {datetime.now().isoformat()}
expires: {(datetime.now()).isoformat()}
status: pending
---

# Approval Required

**Action:** {action_type}

## Details
{self._format_details(details)}

## To Approve
Move to /Approved/

## To Reject
Move to /Rejected/ with reason.
'''
        filepath.write_text(content)
        return filepath
    
    def check_approved(self) -> list:
        """Check for approved actions."""
        return list(self.approved.glob('*.md'))
    
    def execute_and_archive(self, filepath: Path):
        """Execute approved action and move to Done."""
        # Parse and execute
        # Move to Done
        pass
```

## Integration with Orchestrator

```python
# In orchestrator.py
def check_approved_actions(self):
    approved = list(self.approved.glob('*.md'))
    for file in approved:
        self.execute_approval(file)
        self.archive_to_done(file)

def execute_approval(self, filepath: Path):
    content = filepath.read_text()
    # Parse action type and details
    # Call appropriate MCP server
    # Log result
```

## Logging

All approvals logged to `/Logs/approvals_YYYY-MM-DD.json`:

```json
{
  "timestamp": "2026-02-27T10:30:00Z",
  "action": "email_send",
  "file": "APPROVAL_email_send_20260227_103000.md",
  "status": "approved",
  "executed": true,
  "result": {"message_id": "18d4f2a3b5c6e7f8"}
}
```

## Security

- ✅ All sensitive actions require approval
- ✅ Approval files have expiration
- ✅ Rejected actions logged with reason
- ✅ Audit trail in /Logs/
