# Gmail Not Detecting Emails - Troubleshooting

## Problem

Emails sent to ibcoder123@gmail.com are not being detected by Gmail Watcher.

## Root Causes (from Hackathon Document)

According to the hackathon document, the Gmail watcher should:
1. Check **ALL unread emails** (not just "important")
2. Use proper OAuth authentication
3. Process emails and create action files

## Issues Found

### Issue 1: Wrong Query Mode

The watcher is using `is:unread is:important` which filters out new senders.

**Fix:** Use `--all-unread` flag or change default to check all unread.

### Issue 2: Authentication Expired

Token may have expired or needs refresh.

**Fix:** Re-authenticate with Gmail.

### Issue 3: Cache Blocking

Previously processed email IDs are cached, preventing re-detection.

**Fix:** Clear cache before testing.

---

## Complete Fix - Step by Step

### Step 1: Re-authenticate Gmail

```powershell
cd G:\gitub-desktop\Personal-AI-Employee-FTEs\AI_Employee_Vault

# Re-authenticate to refresh token
python watchers\gmail_watcher.py --authenticate
```

**Follow OAuth flow:**
1. Copy URL from terminal
2. Open in browser
3. Sign in to ibcoder123@gmail.com
4. Grant permissions
5. Redirect to localhost

### Step 2: Clear Cache

```powershell
python watchers\gmail_watcher.py --clear-cache
```

### Step 3: Send Test Email

From a **different email account**, send to `ibcoder123@gmail.com`:

- **Subject:** `TEST EMAIL DETECTION`
- **Body:** `Testing if Gmail watcher detects this email`
- **Important:** Do NOT open/read this email in Gmail

### Step 4: Run Watcher with Debug

```powershell
python watchers\gmail_watcher.py . --all-unread --debug
```

**Expected Output:**
```
[DEBUG] Gmail query: is:unread
[DEBUG] Found X email(s) matching query

[DEBUG] New email found:
  From: your-other-email@gmail.com
  Subject: TEST EMAIL DETECTION
  Date: Tue, 10 Mar 2026 02:40:00 +0500
[DEBUG] ✓ Added to processing queue

[INFO] Created action file: EMAIL_20260310_024000_TEST_EMAIL_DETECTION.md
```

### Step 5: Verify File Created

```powershell
dir Needs_Action\EMAIL_*.md
type Needs_Action\EMAIL_*.md
```

---

## If Still Not Working

### Check Which Account is Authenticated

```powershell
python watchers\gmail_watcher.py --show-account
```

**Must show:** `ibcoder123@gmail.com`

If it shows a different account, you authenticated the wrong account. Re-authenticate.

### Check Gmail Labels

Make sure the test email is:
- ✅ In **Inbox** (not archived)
- ✅ Marked as **Unread** (blue dot)
- ✅ Not in Spam/Trash
- ✅ Not in Categories (Promotions/Social)

### Check Gmail Query Manually

Go to Gmail and search: `is:unread`

You should see your test email. If not, the email is either:
- Already read
- In wrong folder
- Filtered away

### Try Without Keyword Filter

```powershell
# Run without any keyword filtering
python watchers\gmail_watcher.py . --all-unread --debug
```

### Check Logs

```powershell
type Logs\watcher_GmailWatcher_*.log
```

Look for errors or connection issues.

---

## Quick Test Script

Create a test email file manually to verify the system works:

```powershell
# Create test file manually
echo "---
type: email
from: test@example.com
subject: Manual Test
received: 2026-03-10T02:40:00
priority: high
status: pending
---

# Manual Test Email

This is a manually created test.
" > Needs_Action\MANUAL_TEST_EMAIL.md

# Run orchestrator
python orchestrator.py .
```

If orchestrator processes this file, the system works - the issue is just with Gmail detection.

---

## Expected Workflow (from Hackathon Doc)

```
1. Email arrives at ibcoder123@gmail.com
   ↓
2. Gmail Watcher polls every 2 minutes
   Query: is:unread (ALL unread, not just important)
   ↓
3. For each new email:
   - Fetch full message
   - Extract headers (From, To, Subject, Date)
   - Create action file in Needs_Action/
   - Mark as processed
   ↓
4. Orchestrator detects new file
   ↓
5. Triggers Qwen Code to process
   ↓
6. Qwen drafts reply, creates approval
   ↓
7. Human approves
   ↓
8. Email sent via MCP
```

---

## Commands Summary

```powershell
# 1. Re-authenticate
python watchers\gmail_watcher.py --authenticate

# 2. Clear cache
python watchers\gmail_watcher.py --clear-cache

# 3. Send test email (manually from different account)

# 4. Run watcher with debug
python watchers\gmail_watcher.py . --all-unread --debug

# 5. Check for action files
dir Needs_Action\EMAIL_*.md

# 6. View created file
type Needs_Action\EMAIL_*.md
```

---

## Success Criteria

✅ Action file created in `Needs_Action/` within 2 minutes of email arrival
✅ File contains correct From, Subject, Date
✅ Orchestrator picks up the file
✅ Qwen Code processes it

---

**Try the steps above and report which step fails!**
