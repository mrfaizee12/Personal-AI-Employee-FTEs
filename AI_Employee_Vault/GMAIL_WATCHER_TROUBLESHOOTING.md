# Gmail Watcher - Troubleshooting & Usage Guide

## ✅ Issue Fixed!

The Gmail watcher has been updated to detect **all unread emails**, not just those marked as "important" by Gmail.

---

## What Was The Problem?

The original query was:
```
is:unread is:important
```

This only fetched emails that Gmail considers "important" - which excludes:
- Emails from new senders (like your test email to ibcoder123@gmail)
- Emails Gmail's algorithm hasn't learned yet
- Marketing emails, newsletters, etc.

---

## ✅ Solution: New Modes Available

### Mode 1: Check ALL Unread Emails (Recommended for Testing)

```powershell
python watchers\gmail_watcher.py . --all-unread
```

This checks **every unread email** regardless of importance.

### Mode 2: Original Mode (Unread + Important)

```powershell
python watchers\gmail_watcher.py .
```

Default behavior - only "important" unread emails.

### Mode 3: Debug Mode (See What's Happening)

```powershell
python watchers\gmail_watcher.py . --all-unread --debug
```

Shows detailed information about every email found:
```
[DEBUG] Gmail query: is:unread
[DEBUG] Found 5 email(s) matching query

[DEBUG] New email found:
  From: friend@example.com
  Subject: Test Email
  Date: Mon, 8 Mar 2026 23:30:00 +0000
[DEBUG] ✓ Added to processing queue
```

---

## New Commands

### Show Account Info

Check which Gmail account is authenticated:

```powershell
python watchers\gmail_watcher.py --show-account
```

**Output:**
```
[OK] Authenticated Gmail Account:
  Email: ibcoder123@gmail.com
  Name: Your Name
  Total emails: 1,234
  Total threads: 567
  Unread emails: 23
```

### Clear Cache (For Testing)

Clear the processed email cache so emails are re-processed:

```powershell
python watchers\gmail_watcher.py --clear-cache
```

**Use this when:**
- Testing and want to re-process same emails
- Emails were missed and you want to retry
- Debugging email detection issues

### Filter by Keywords

Only process emails containing specific words:

```powershell
python watchers\gmail_watcher.py . --keywords "invoice,payment,urgent"
```

This will only create action files for emails containing those keywords.

---

## Complete Usage Examples

### First Time Setup

```powershell
# 1. Authenticate
python watchers\gmail_watcher.py --authenticate

# 2. Check account
python watchers\gmail_watcher.py --show-account

# 3. Start monitoring (all unread)
python watchers\gmail_watcher.py . --all-unread
```

### Daily Use

```powershell
# Normal monitoring (important emails only)
python watchers\gmail_watcher.py .

# Monitoring with debug output
python watchers\gmail_watcher.py . --debug

# Monitoring all unread with keywords
python watchers\gmail_watcher.py . --all-unread --keywords "invoice,payment"
```

### Testing

```powershell
# 1. Clear cache
python watchers\gmail_watcher.py --clear-cache

# 2. Send yourself a test email

# 3. Run with debug
python watchers\gmail_watcher.py . --all-unread --debug

# 4. Check Needs_Action/ folder for new .md file
```

---

## Why Your Test Email Wasn't Detected

**Scenario:** You sent email from your account to `ibcoder123@gmail.com`

**Possible reasons it wasn't detected:**

1. ❌ **Not marked as "important"** - Gmail doesn't know this sender yet
   - **Fix:** Use `--all-unread` flag

2. ❌ **Already processed** - Email was already checked once
   - **Fix:** Use `--clear-cache` to reset

3. ❌ **Wrong Gmail account** - Authenticated account is different from ibcoder123
   - **Fix:** Use `--show-account` to verify

4. ❌ **Email already read** - You opened it in Gmail
   - **Fix:** Mark as unread in Gmail, or use `--all-unread` which still won't catch read emails

---

## How To Test Properly

### Step 1: Verify Account

```powershell
python watchers\gmail_watcher.py --show-account
```

Make sure it shows `ibcoder123@gmail.com`

### Step 2: Clear Cache

```powershell
python watchers\gmail_watcher.py --clear-cache
```

### Step 3: Send Fresh Test Email

From a **different email address**, send to `ibcoder123@gmail.com`:
- Subject: `Test Email for AI Employee`
- Body: `This is a test`
- **Don't open the email after sending**

### Step 4: Run Watcher with Debug

```powershell
python watchers\gmail_watcher.py . --all-unread --debug
```

### Step 5: Check Output

You should see:
```
[DEBUG] New email found:
  From: your-other-email@example.com
  Subject: Test Email for AI Employee
[DEBUG] ✓ Added to processing queue
[INFO] Created action file: EMAIL_20260308_235000_Test_Email.md
```

### Step 6: Verify File Created

```powershell
dir Needs_Action\EMAIL_*.md
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `--authenticate` | First-time OAuth setup |
| `--show-account` | Show which Gmail account |
| `--clear-cache` | Reset processed emails |
| `--all-unread` | Check ALL unread (not just important) |
| `--debug` | Show detailed email info |
| `--keywords "word1,word2"` | Filter by keywords |
| `--interval 60` | Check every 60 seconds |

---

## Expected Behavior After Fix

```powershell
# Start watcher
python watchers\gmail_watcher.py . --all-unread

# Output:
[INFO] Starting Gmail Watcher...
[INFO] Mode: All unread emails
[INFO] Check interval: 120s
[INFO] Press Ctrl+C to stop

# Send test email...
# Within 2 minutes:
[INFO] Created action file: EMAIL_20260308_235000_Subject.md

# File appears in Needs_Action/ folder!
```

---

## Still Not Working?

### Run Maximum Debug Mode

```powershell
python watchers\gmail_watcher.py . --all-unread --debug
```

This will show:
- Exactly what query is being run
- How many emails match
- Details of each email
- Why each email is included/excluded

### Check Gmail Labels

Make sure the email is in **Inbox**, not:
- Spam
- Trash
- Archived
- Categories (Promotions, Social, etc.)

Gmail's "important" marker is separate from labels. Using `--all-unread` bypasses this.

---

*Last updated: March 8, 2026*
