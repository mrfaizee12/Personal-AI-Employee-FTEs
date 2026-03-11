# Silver Tier Implementation Guide

**Status:** ✅ COMPLETE  
**Date:** February 27, 2026

---

## Silver Tier Requirements (from Hackathon Document)

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | All Bronze requirements | ✅ | Already complete |
| 2 | Two or more Watcher scripts | ✅ | FileSystemWatcher + GmailWatcher |
| 3 | Auto-post on LinkedIn | ✅ | LinkedIn MCP Server |
| 4 | Claude reasoning loop (Plan.md) | ✅ | Plan Generator Skill |
| 5 | One working MCP server | ✅ | Email MCP Server |
| 6 | HITL approval workflow | ✅ | Approval Handler |
| 7 | Basic scheduling | ✅ | Scheduling Helper |
| 8 | All as Agent Skills | ✅ | All in SKILL.md format |

---

## New Skills Added

### 1. Gmail Watcher

**Skill:** `.qwen/skills/gmail-watcher/SKILL.md`  
**Script:** `watchers/gmail_watcher.py`

**Features:**
- Monitors Gmail for unread/important emails
- Filters by keywords (urgent, invoice, payment, etc.)
- Creates action files in `/Needs_Action/`
- Caches processed email IDs

**Setup:**
```bash
# Install dependencies
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# First-time authentication
python watchers/gmail_watcher.py --authenticate

# Run watcher
python watchers/gmail_watcher.py .
```

---

### 2. Email MCP Server

**Skill:** `.qwen/skills/email-mcp-server/SKILL.md`  
**Script:** `mcp_servers/email_mcp.py`

**Tools:**
- `email_send` - Send email immediately
- `email_draft` - Create draft email
- `email_reply` - Reply to existing email

**Setup:**
```bash
# Install dependencies
pip install mcp google-api-python-client

# Authenticate
python mcp_servers/email_mcp.py --authenticate

# Start server
python mcp_servers/email_mcp.py --port 8809
```

---

### 3. HITL Approval Workflow

**Skill:** `.qwen/skills/hitl-approval-workflow/SKILL.md`

**Workflow:**
```
Qwen detects action → Creates approval file → Human reviews → 
Moves to /Approved/ → Orchestrator executes → Moves to /Done/
```

**Approval File Format:**
```markdown
---
type: approval_request
action: email_send
to: client@example.com
subject: Invoice #1234
created: 2026-02-27T10:30:00Z
status: pending
---

# Approval Required

**Action:** Send Email  
**To:** client@example.com

## To Approve
Move to /Approved/
```

---

### 4. Plan Generator

**Skill:** `.qwen/skills/plan-generator/SKILL.md`

**Creates Plan.md for complex tasks:**
```markdown
---
type: plan
task: Send invoice to Client A
created: 2026-02-27T10:30:00Z
status: in_progress
---

# Plan: Send Invoice to Client A

## Steps
- [x] Identify client details
- [ ] Generate invoice PDF
- [ ] Send via email (REQUIRES APPROVAL)
- [ ] Log transaction
```

---

### 5. LinkedIn Poster

**Skill:** `.qwen/skills/linkedin-poster/SKILL.md`  
**Script:** `mcp_servers/linkedin_mcp.py`

**Tools:**
- `linkedin_post` - Create and publish post
- `linkedin_schedule` - Schedule for later
- `linkedin_generate` - Generate from business update

**Setup:**
```bash
# Start Playwright MCP first
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Start LinkedIn MCP
python mcp_servers/linkedin_mcp.py --port 8810
```

---

### 6. Scheduling Helper

**Script:** `scheduling_helper.py`

**Supports:**
- Windows Task Scheduler
- Linux/Mac cron
- Python APScheduler (cross-platform)

**Usage:**
```bash
# Install Windows task
python scheduling_helper.py install --task orchestrator --interval 60

# Install cron job
python scheduling_helper.py install --task daily_briefing --trigger cron --value 08:00

# Run with APScheduler
python scheduling_helper.py run --task orchestrator --interval 60
```

---

## Updated Orchestrator (Silver Tier)

**File:** `orchestrator.py`

**New Features:**
1. **Plan.md Support** - Creates plans for complex tasks
2. **HITL Execution** - Auto-executes approved actions
3. **MCP Integration** - Calls Email and LinkedIn MCP servers
4. **Better Logging** - Tracks all approval executions

**Execution Flow:**
```python
def execute_approved_action(self, filepath: Path):
    # Parse action type
    action_type = self._parse_action_type(content)
    
    # Execute based on type
    if action_type == 'email_send':
        result = self._execute_email_send(content, filepath)
    elif action_type == 'linkedin_post':
        result = self._execute_linkedin_post(content, filepath)
    elif action_type == 'payment':
        result = self._execute_payment(content, filepath)
    
    # Move to Done
    filepath.rename(self.done / filepath.name)
```

---

## Folder Structure (Silver Tier)

```
AI_Employee_Vault/
├── Dashboard.md
├── Company_Handbook.md
├── Business_Goals.md
├── orchestrator.py              # Updated for Silver
├── scheduling_helper.py         # NEW
├── watchers/
│   ├── base_watcher.py
│   ├── filesystem_watcher.py
│   └── gmail_watcher.py         # NEW
├── mcp_servers/
│   ├── email_mcp.py             # NEW
│   └── linkedin_mcp.py          # NEW
├── Inbox/
├── Needs_Action/
├── Plans/                       # NEW (used)
├── Pending_Approval/            # NEW (used)
├── Approved/                    # NEW (auto-executed)
├── Rejected/
├── Done/
├── Accounting/
├── Briefings/
└── Logs/
```

---

## Running the Silver Tier System

### Terminal 1: Start Watchers

```bash
cd AI_Employee_Vault

# File System Watcher
python watchers\filesystem_watcher.py .

# Gmail Watcher (separate terminal)
python watchers\gmail_watcher.py .
```

### Terminal 2: Start MCP Servers

```bash
# Email MCP Server
python mcp_servers\email_mcp.py --port 8809

# LinkedIn MCP Server (separate terminal)
python mcp_servers\linkedin_mcp.py --port 8810

# Playwright MCP (required for LinkedIn)
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh
```

### Terminal 3: Start Orchestrator

```bash
# Single cycle
python orchestrator.py .

# Continuous mode
python orchestrator.py . --continuous
```

### Terminal 4: Process with Qwen Code

```bash
qwen --cd "G:\gitub-desktop\Personal-AI-Employee-FTEs\AI_Employee_Vault"
```

---

## Example Workflows

### Workflow 1: Email Triage

1. **Gmail Watcher** detects new important email
2. Creates `EMAIL_20260227_103000_Invoice_Request.md` in `/Needs_Action/`
3. **Orchestrator** triggers Qwen Code
4. **Qwen** reads email, drafts reply
5. **Qwen** creates approval file in `/Pending_Approval/`
6. **Human** moves file to `/Approved/`
7. **Orchestrator** calls Email MCP to send
8. File moved to `/Done/`

### Workflow 2: LinkedIn Post

1. **Qwen** generates post from business update
2. Creates approval file with post content
3. **Human** approves by moving to `/Approved/`
4. **Orchestrator** calls LinkedIn MCP
5. Post published to LinkedIn
6. Logged and archived to `/Done/`

### Workflow 3: Complex Task with Plan

1. **File dropped** in `/Inbox/` with complex request
2. **Watcher** creates action file
3. **Qwen** creates `Plan.md` in `/Plans/`
4. **Qwen** executes steps, updates plan
5. For steps needing approval, creates approval files
6. **Human** approves sensitive actions
7. **Orchestrator** executes approved actions
8. Plan marked complete, archived to `/Done/`

---

## Testing Silver Tier

### Test 1: Gmail Watcher

```bash
# Send yourself a test email with subject "Test Invoice"
# Run Gmail Watcher
python watchers/gmail_watcher.py .

# Check /Needs_Action/ for new email file
dir Needs_Action
```

### Test 2: Email MCP

```bash
# Start Email MCP Server
python mcp_servers/email_mcp.py --port 8809

# Send test email via MCP client
python scripts/mcp-client.py call -u http://localhost:8809 \
  -t email_send \
  -p '{"to": "your@email.com", "subject": "Test from AI Employee", "body": "This is a test."}'
```

### Test 3: Approval Workflow

```bash
# Create test approval file
cat > Pending_Approval/APPROVAL_test_email.md << EOF
---
type: approval_request
action: email_send
to: your@email.com
subject: Test Approval
---

# Test Approval

Move to /Approved/ to test.
EOF

# Move to Approved
mv Pending_Approval/APPROVAL_test_email.md Approved/

# Run orchestrator
python orchestrator.py .
```

---

## Skills Summary

| Skill | Location | Purpose |
|-------|----------|---------|
| browsing-with-playwright | `.qwen/skills/browsing-with-playwright/` | Browser automation |
| gmail-watcher | `.qwen/skills/gmail-watcher/` | Monitor Gmail |
| email-mcp-server | `.qwen/skills/email-mcp-server/` | Send emails |
| hitl-approval-workflow | `.qwen/skills/hitl-approval-workflow/` | Human approval |
| plan-generator | `.qwen/skills/plan-generator/` | Create plans |
| linkedin-poster | `.qwen/skills/linkedin-poster/` | Post to LinkedIn |

---

## Next Steps (Gold Tier)

To advance to Gold tier, add:

1. **Full cross-domain integration** - Personal + Business
2. **Odoo Accounting** - Self-hosted ERP integration
3. **Facebook/Instagram** - Social media integration
4. **Twitter (X)** - Posting and summaries
5. **Multiple MCP servers** - Different action types
6. **Weekly CEO Briefing** - Automated business audit
7. **Error recovery** - Graceful degradation
8. **Ralph Wiggum loop** - Autonomous multi-step tasks

---

*Silver Tier Complete! Ready for production use.*
