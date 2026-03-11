# LinkedIn Watcher - Quick Start Guide

## The Problem

LinkedIn Watcher needs browser automation, but LinkedIn requires login. The automated login doesn't work reliably due to LinkedIn's security.

## ✅ Solution: Two-Step Process

### Step 1: Start Playwright MCP

```powershell
# This opens a browser window
.\.qwen\skills\browsing-with-playwright\scripts\start-server.ps1
```

**A browser window will open** - keep it open!

### Step 2: Manually Log In to LinkedIn

In the browser window that opened:

1. Navigate to: `https://www.linkedin.com/login`
2. Enter your credentials
3. Complete any 2FA
4. You should see your LinkedIn feed

### Step 3: Run the Watcher

**Keep the browser open** and run:

```powershell
cd AI_Employee_Vault
python watchers\linkedin_watcher.py .
```

The watcher will now be able to check LinkedIn because you're already logged in!

---

## How It Works

```
1. Playwright MCP starts → Browser opens
2. You log in manually → Session cookies active
3. Watcher uses same browser session → Can access LinkedIn
4. No need to log in again (until cookies expire)
```

---

## Quick Commands

```powershell
# Start Playwright (opens browser)
.\.qwen\skills\browsing-with-playwright\scripts\start-server.ps1

# [MANUALLY LOG IN TO LINKEDIN IN THE BROWSER]

# Start LinkedIn Watcher
cd AI_Employee_Vault
python watchers\linkedin_watcher.py .

# Start Gmail Watcher (alternative)
python watchers\gmail_watcher.py .
```

---

## Troubleshooting

### "Browser doesn't open"
**Solution:** Run `npx @playwright/mcp@latest --port 8808 --shared-browser-context` manually

### "LinkedIn shows login page"
**Solution:** You need to log in first. The watcher can't access LinkedIn without authentication.

### "Watcher says no notifications"
**Solution:** That's normal if you don't have new notifications. Check `Needs_Action/` folder.

### "Want to stop the watcher"
**Solution:** Press `Ctrl+C` in the terminal

---

## Alternative: Use Gmail Watcher (Easier!)

Gmail has a proper API and is much easier to set up:

```powershell
# Authenticate (opens browser, one-time)
cd AI_Employee_Vault
python watchers\gmail_watcher.py --authenticate

# Start watcher
python watchers\gmail_watcher.py .
```

**Gmail watcher works 24/7 after one-time authentication!**

---

*Last updated: March 1, 2026*
