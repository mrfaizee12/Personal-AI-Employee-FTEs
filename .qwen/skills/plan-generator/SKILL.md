---
name: plan-generator
description: |
  Creates Plan.md files for complex tasks. Breaks down tasks into
  actionable steps with checkboxes, estimates, and dependencies.
  Used by Qwen Code for reasoning and task tracking.
---

# Plan Generator Skill

Creates structured Plan.md files for complex multi-step tasks.

## When to Create a Plan

| Task Complexity | Action |
|-----------------|--------|
| Simple (1-2 steps) | Execute directly |
| Medium (3-5 steps) | Create Plan.md |
| Complex (5+ steps) | Create Plan.md + Approval |

## Plan.md Format

```markdown
---
type: plan
task: Send invoice to Client A
created: 2026-02-27T10:30:00Z
status: in_progress
priority: high
estimated_duration: 30 minutes
---

# Plan: Send Invoice to Client A

## Objective
Generate and send January 2026 invoice to Client A for $1,500.

## Context
- Client requested invoice via WhatsApp on 2026-02-26
- Agreed amount: $1,500 for consulting services
- Payment terms: Net 15

## Steps

- [x] Identify client details (email: client@example.com)
- [x] Calculate amount ($1,500 from agreement)
- [ ] Generate invoice PDF
  - Use template from /Templates/invoice.md
  - Include: Date, Items, Total, Due date
- [ ] Send via email (REQUIRES APPROVAL)
  - To: client@example.com
  - Subject: Invoice #2026-01 - $1,500
  - Attachment: /Invoices/2026-01_Client_A.pdf
- [ ] Log transaction to /Accounting/
- [ ] Move to /Done when complete

## Dependencies

- Invoice PDF generation before email send
- Approval required before sending

## Notes

*Add observations during execution...*

---
*Created by PlanGenerator*
```

## Usage

### Qwen Code Creates Plan

```
I have a complex task: Send invoice to Client A

Creating Plan.md...
```

### Plan File Location

```
/Vault/Plans/PLAN_send_invoice_client_a_20260227.md
```

### Update Plan During Execution

As steps complete, Qwen updates the file:

```markdown
- [x] Identify client details
- [x] Calculate amount
- [x] Generate invoice PDF
- [ ] Send via email (pending approval)
```

## Python Implementation

```python
from pathlib import Path
from datetime import datetime

class PlanGenerator:
    def __init__(self, vault_path: str):
        self.vault = Path(vault_path)
        self.plans_dir = self.vault / 'Plans'
        self.plans_dir.mkdir(parents=True, exist_ok=True)
    
    def create_plan(self, task: str, objective: str, 
                    steps: list, context: str = '') -> Path:
        """Create a new Plan.md file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_task = "".join(c for c in task if c.isalnum() or c in ' -_')[:30]
        filename = f"PLAN_{safe_task}_{timestamp}.md"
        filepath = self.plans_dir / filename
        
        steps_md = '\n'.join([f'- [ ] {step}' for step in steps])
        
        content = f'''---
type: plan
task: {task}
created: {datetime.now().isoformat()}
status: in_progress
priority: medium
---

# Plan: {task}

## Objective
{objective}

## Context
{context}

## Steps

{steps_md}

## Notes

*Add observations during execution...*

---
*Created by PlanGenerator*
'''
        filepath.write_text(content, encoding='utf-8')
        return filepath
    
    def update_step(self, plan_path: Path, step_index: int, 
                    completed: bool):
        """Mark a step as complete/incomplete."""
        content = plan_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if line.strip().startswith('- [ ]') and i > step_index:
                if completed:
                    lines[i] = line.replace('- [ ]', '- [x]')
                else:
                    lines[i] = line.replace('- [x]', '- [ ]')
                break
        
        plan_path.write_text('\n'.join(lines), encoding='utf-8')
    
    def mark_complete(self, plan_path: Path):
        """Mark plan as complete."""
        content = plan_path.read_text(encoding='utf-8')
        content = content.replace('status: in_progress', 'status: completed')
        content = content.replace(f'---\n*Created', 
                                  f'\n**Completed:** {datetime.now().isoformat()}\n---\n*Created')
        plan_path.write_text(content, encoding='utf-8')
```

## Integration with Qwen Code

Qwen Code prompt for plan creation:

```
I have this task in /Needs_Action: [task description]

This is a complex task requiring multiple steps.

Please:
1. Create a Plan.md in /Plans/ with:
   - Clear objective
   - Context from the original file
   - Step-by-step checklist
   - Identify steps needing approval
2. Start executing the first steps
3. Update the plan as you progress
```

## Example Plans

### Email Response Plan

```markdown
# Plan: Respond to Client Inquiry

## Steps
- [x] Read email content
- [x] Identify key questions
- [ ] Draft response
- [ ] Review against Company_Handbook.md
- [ ] Create approval request
- [ ] Send after approval
```

### Payment Plan

```markdown
# Plan: Pay Monthly Subscription

## Steps
- [x] Identify vendor and amount
- [x] Check if recurring (yes - Netflix $15/month)
- [x] Verify under auto-approve threshold (< $50)
- [ ] Process payment via banking portal
- [ ] Log to /Accounting/
- [ ] Update Dashboard.md
```

## Status Tracking

| Status | Meaning |
|--------|---------|
| `pending` | Plan created, not started |
| `in_progress` | Currently executing |
| `blocked` | Waiting for approval/external |
| `completed` | All steps done |
| `cancelled` | Plan abandoned |
