# LinkedIn Watcher - Login Guide

## ✅ What's Fixed

The LinkedIn watcher now uses **direct Playwright** (not MCP) with persistent browser session - exactly like the WhatsApp Watcher pattern in the hackathon document!

---

## Step-by-Step Login Process

### Step 1: Run Login Command

```powershell
cd G:\gitub-desktop\Personal-AI-Employee-FTEs\AI_Employee_Vault
python watchers\linkedin_watcher.py --login
```

### Step 2: A Browser Window Opens

**What happens:**
- A Chromium browser window opens
- It navigates to LinkedIn login page
- You have **180 seconds (3 minutes)** to log in

### Step 3: Log In to LinkedIn

**In the browser window:**

1. **Enter your email/phone**
2. **Enter your password**
3. **Complete 2FA if prompted** (SMS code, authenticator app, etc.)
4. **Complete any CAPTCHA** if shown
5. **Wait until you see your LinkedIn feed**

**Important:**
- Don't close the browser manually
- The browser will close automatically when login is detected
- Make sure you reach the feed page (not just the login page)

### Step 4: Login Detected

When login is successful, you'll see:

```
[OK] Login successful! Detected LinkedIn feed page.
[INFO] Browser closed.
[INFO] Session saved to: C:\...\AI_Employee_Vault\.linkedin_session
[INFO] Next time you run the watcher, you will be logged in!
[NEXT] Run: python linkedin_watcher.py .
```

### Step 5: Run the Watcher

```powershell
# Start monitoring LinkedIn
python watchers\linkedin_watcher.py .
```

---

## How It Works

```
1. First run (--login):
   - Browser opens → You log in → Session cookies saved
   - Browser closes automatically

2. Subsequent runs:
   - Browser opens with saved session → Already logged in!
   - Checks notifications every 5 minutes
   - Creates action files in /Needs_Action/
```

---

## Troubleshooting

### "Login timeout"

**Cause:** Took longer than 180 seconds to log in

**Solution:** Run the command again - the session is partially saved, so next time will be faster

### "Browser doesn't open"

**Cause:** Playwright browsers not installed

**Solution:** Run `playwright install chromium`

### "ModuleNotFoundError: playwright"

**Solution:** Run `pip install playwright`

### "Session expired"

**Cause:** LinkedIn cookies expired (happens after a few days/weeks)

**Solution:** Run `python linkedin_watcher.py --login` again

---

## What Gets Monitored

The watcher checks:

1. **LinkedIn Notifications** (`/notifications/`)
   - Connection requests
   - Post likes/comments
   - Profile views
   - Job alerts

2. **LinkedIn Messages** (`/messaging/`)
   - New messages
   - Conversation previews

When activity is detected, it creates a file in `Needs_Action/` for Qwen Code to process.

---

## Quick Commands

```powershell
# First time: Log in
python watchers\linkedin_watcher.py --login

# Start monitoring
python watchers\linkedin_watcher.py .

# Monitor with custom interval (e.g., 2 minutes)
python watchers\linkedin_watcher.py . --interval 120
```

---

## Session Location

```
G:\gitub-desktop\Personal-AI-Employee-FTEs\AI_Employee_Vault\.linkedin_session\

This folder contains:
- Browser cookies
- Local storage
- Session tokens
```

**Don't delete this folder** unless you want to log in again!

---

*Last updated: March 7, 2026*
