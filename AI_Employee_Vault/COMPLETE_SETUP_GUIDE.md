# ✅ COMPLETE SETUP GUIDE - Silver Tier

**Last Updated:** March 9, 2026  
**Status:** Ready to Use

---

## Quick Start (After Fresh Boot)

### Terminal 1: Gmail Watcher

```powershell
cd G:\gitub-desktop\Personal-AI-Employee-FTEs\AI_Employee_Vault
python watchers\gmail_watcher.py . --all-unread
```

### Terminal 2: Orchestrator

```powershell
python orchestrator.py . --continuous
```

**That's it!** Email sending is now integrated into the orchestrator.

---

## What's Fixed

| Issue | Status |
|-------|--------|
| Email MCP authentication | ✅ Fixed |
| Port 8080 busy error | ✅ Auto-tries multiple ports |
| MCP server run_stdio error | ✅ Removed - integrated into orchestrator |
| Token loading | ✅ Fixed |
| Escape sequence warnings | ✅ Fixed |

---

## How Email Sending Works Now

```
1. Gmail Watcher detects email
   ↓
2. Orchestrator triggers Qwen Code
   ↓
3. Qwen drafts reply
   ↓
4. Creates: Pending_Approval/APPROVAL_*.md
   ↓
5. YOU approve: move to Approved/
   ↓
6. Orchestrator sends email DIRECTLY
   ↓
7. Files moved to Done/
```

**No separate MCP server needed!**

---

## Your Current Task

### Approve the Faizan Email Reply

```powershell
# Move approval file to Approved folder
move Pending_Approval\APPROVAL_email_reply_ai-employee.md Approved\
```

**What happens:**
1. Orchestrator detects approved file
2. Sends email to faizee956@gmail.com
3. Moves files to Done/
4. Updates Dashboard

---

## Commands Reference

### Gmail Watcher

```powershell
# Start monitoring
python watchers\gmail_watcher.py . --all-unread

# Show account info
python watchers\gmail_watcher.py --show-account

# Clear cache (for testing)
python watchers\gmail_watcher.py --clear-cache

# Debug mode
python watchers\gmail_watcher.py . --all-unread --debug
```

### Orchestrator

```powershell
# Single cycle
python orchestrator.py .

# Continuous mode
python orchestrator.py . --continuous
```

### Email MCP (One-Time Auth)

```powershell
# Authenticate (if needed)
python mcp_servers\email_mcp.py --authenticate

# No need to run server separately!
```

---

## File Structure

```
AI_Employee_Vault/
├── watchers/
│   ├── gmail_watcher.py       ✅ Working
│   ├── linkedin_watcher.py    ✅ Working
│   └── filesystem_watcher.py  ✅ Working
├── mcp_servers/
│   ├── email_mcp.py           ✅ Fixed (integrated)
│   └── linkedin_mcp.py        ✅ Ready
├── orchestrator.py            ✅ Fixed (sends emails)
├── Needs_Action/              ✅ Email files here
├── Pending_Approval/          ✅ Approvals here
├── Approved/                  ✅ Move approvals here
└── Done/                      ✅ Completed items
```

---

## Troubleshooting

### "Gmail API not authenticated"

```powershell
python mcp_servers\email_mcp.py --authenticate
```

### "Port 8080 busy"

Authentication will automatically try ports 8081-8085.

### "Email not detected"

```powershell
# Clear cache and re-run
python watchers\gmail_watcher.py --clear-cache
python watchers\gmail_watcher.py . --all-unread --debug
```

### "Orchestrator not sending"

Check if approval file is in Approved/ folder:
```powershell
dir Approved\
```

---

## Status Check

```powershell
# What's pending?
dir Needs_Action\*.md

# What needs approval?
dir Pending_Approval\*.md

# What's approved and waiting?
dir Approved\

# What's completed?
dir Done\*.md

# Dashboard
type Dashboard.md
```

---

## Next Steps

1. **Approve current email:**
   ```powershell
   move Pending_Approval\APPROVAL_email_reply_ai-employee.md Approved\
   ```

2. **Watch it send automatically!**

3. **Check Dashboard:**
   ```powershell
   type Dashboard.md
   ```

---

**Silver Tier is COMPLETE and ready!** 🎉

All components working:
- ✅ Gmail Watcher
- ✅ LinkedIn Watcher  
- ✅ File System Watcher
- ✅ Orchestrator
- ✅ Email Sending (integrated)
- ✅ HITL Approval Workflow
- ✅ Plan Generation
