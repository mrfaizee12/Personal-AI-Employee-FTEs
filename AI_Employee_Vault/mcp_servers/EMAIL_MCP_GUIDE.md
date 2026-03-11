# Email MCP Server - Quick Guide

## ✅ Authentication Complete!

Your Email MCP is now authenticated with Gmail.

---

## How It Works

The Email MCP server is **not meant to run standalone**. It's called automatically by the Orchestrator when you approve an email.

---

## Workflow

```
1. Gmail Watcher detects email
   ↓
2. Orchestrator triggers Qwen Code
   ↓
3. Qwen drafts reply
   ↓
4. Creates approval file in Pending_Approval/
   ↓
5. YOU move file to Approved/
   ↓
6. Orchestrator calls Email MCP automatically
   ↓
7. Email sent!
```

---

## What You Need To Do

### Step 1: Approve the Email

```powershell
# Move approval file to Approved folder
move Pending_Approval\APPROVAL_email_reply_ai-employee.md Approved\
```

### Step 2: Orchestrator Handles the Rest

The orchestrator will:
1. Detect the approved file
2. Call Email MCP to send the email
3. Move files to Done/
4. Update Dashboard

**You don't need to run the Email MCP server manually!**

---

## If You Want to Test Email Sending

```powershell
# Test sending an email directly
python -c "from mcp_servers.email_mcp import EmailMCP; mcp = EmailMCP(); result = mcp.send_email('test@example.com', 'Test Subject', 'Test Body'); print(result)"
```

---

## Current Status

| Component | Status |
|-----------|--------|
| Authentication | ✅ Complete |
| Token saved | ✅ mcp_servers/token.json |
| Gmail API access | ✅ Ready |
| Ready to send | ✅ Yes |

---

**Next:** Approve your email and it will be sent automatically!

```powershell
move Pending_Approval\APPROVAL_email_reply_ai-employee.md Approved\
```
