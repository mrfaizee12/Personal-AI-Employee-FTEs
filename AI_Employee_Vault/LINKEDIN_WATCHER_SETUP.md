# LinkedIn Watcher - Setup Guide

## The Challenge

LinkedIn Watcher requires browser automation via Playwright MCP. However, LinkedIn login can't be fully automated because:
1. LinkedIn has strong bot detection
2. 2FA may be required
3. CAPTCHA may appear

## Solution: Manual Login + Session Persistence

The watcher uses a **persistent browser session** that you log into once, and it saves the cookies for future use.

---

## Setup Steps

### Step 1: Start Playwright MCP

```powershell
# Start the browser automation server
.\.qwen\skills\browsing-with-playwright\scripts\start-server.ps1
```

### Step 2: Manual LinkedIn Login (One Time)

Since automated login is unreliable, do this manually:

1. **Open the browser that Playwright launches**
   - When you start Playwright MCP, a browser window opens
   - OR navigate manually in that browser

2. **Go to LinkedIn and log in**
   ```
   https://www.linkedin.com/login
   ```

3. **Complete any 2FA/CAPTCHA**

4. **Verify you're on your feed**
   ```
   https://www.linkedin.com/feed/
   ```

5. **Keep the browser open** - The session is stored automatically

### Step 3: Test the Watcher

```powershell
cd AI_Employee_Vault
python watchers\linkedin_watcher.py .
```

---

## How It Works

```
1. Playwright MCP starts → Browser opens
2. You log in manually → Session cookies saved
3. Watcher runs → Reuses saved session
4. No need to log in again!
```

---

## Alternative: Use LinkedIn API (For Developers)

If you have LinkedIn API access:

1. Create app at https://www.linkedin.com/developers/
2. Get API credentials
3. Use `linkedin-api` Python package:
   ```bash
   pip install linkedin-api
   ```

---

## Current Status

| Component | Status |
|-----------|--------|
| Playwright MCP | ✅ Working |
| Browser Automation | ✅ Working |
| Manual Login | ⏳ Required (one time) |
| Session Persistence | ⏳ After login |
| Notification Monitoring | ⏳ After login |

---

## Next Steps

1. **Start Playwright MCP**
2. **Log in to LinkedIn in the browser window**
3. **Run the watcher**
4. **Check Needs_Action/ for LinkedIn notifications**

---

*Note: The LinkedIn watcher is designed to work AFTER you've manually logged in once. The session will persist for future runs.*
