# PowerShell Commands for AI Employee

## Starting Playwright MCP Server

### Option 1: PowerShell Script (Recommended for Windows)

```powershell
# Navigate to scripts directory
cd G:\gitub-desktop\Personal-AI-Employee-FTEs\.qwen\skills\browsing-with-playwright\scripts

# Start the server
.\start-server.ps1

# Or specify a different port
.\start-server.ps1 -Port 8809
```

### Option 2: Bash Script (Also Works)

```powershell
cd G:\gitub-desktop\Personal-AI-Employee-FTEs
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh
```

### Option 3: Direct npx Command

```powershell
npx @playwright/mcp@latest --port 8808 --shared-browser-context
```

---

## Stopping Playwright MCP Server

### Option 1: PowerShell Script

```powershell
cd G:\gitub-desktop\Personal-AI-Employee-FTEs\.qwen\skills\browsing-with-playwright\scripts
.\stop-server.ps1
```

### Option 2: Bash Script

```powershell
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

### Option 3: Manual (Task Manager)

```powershell
# Find the process
Get-Process | Where-Object {$_.ProcessName -like "*node*"}

# Stop it
Stop-Process -Name node -Force
```

---

## Verifying Server is Running

```powershell
# Run verify script
python .qwen\skills\browsing-with-playwright\scripts\verify.py

# Expected output: [OK] Playwright MCP server running
```

---

## Running LinkedIn Watcher

```powershell
# 1. Start Playwright MCP first
.\.qwen\skills\browsing-with-playwright\scripts\start-server.ps1

# 2. Login to LinkedIn (first time only)
cd AI_Employee_Vault
python watchers\linkedin_watcher.py --login

# 3. Start the watcher
python watchers\linkedin_watcher.py .
```

---

## Running Gmail Watcher

```powershell
# 1. Authenticate (first time only)
cd AI_Employee_Vault
python watchers\gmail_watcher.py --authenticate

# 2. Start the watcher
python watchers\gmail_watcher.py .
```

---

## Running All Watchers

```powershell
# Terminal 1: Playwright MCP (for LinkedIn)
.\.qwen\skills\browsing-with-playwright\scripts\start-server.ps1

# Terminal 2: Gmail Watcher
cd AI_Employee_Vault
python watchers\gmail_watcher.py .

# Terminal 3: LinkedIn Watcher
cd AI_Employee_Vault
python watchers\linkedin_watcher.py .

# Terminal 4: File System Watcher
cd AI_Employee_Vault
python watchers\filesystem_watcher.py .

# Terminal 5: Orchestrator
cd AI_Employee_Vault
python orchestrator.py . --continuous
```

---

## Quick Status Checks

```powershell
# Check if Playwright is running
python .qwen\skills\browsing-with-playwright\scripts\verify.py

# Check what's in Needs_Action
dir AI_Employee_Vault\Needs_Action\

# Check logs
type AI_Employee_Vault\Logs\watcher_*.log
```

---

## Execution Policy (If Scripts Won't Run)

If you get an execution policy error:

```powershell
# Allow scripts for current session
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run with bypass
powershell -ExecutionPolicy Bypass -File .\start-server.ps1
```

---

## Common Issues

### "start-server.ps1 cannot be loaded"
**Solution:** Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### "Port 8808 already in use"
**Solution:** Stop existing server: `.\stop-server.ps1` or use different port: `.\start-server.ps1 -Port 8809`

### "npm/npx not found"
**Solution:** Install Node.js from https://nodejs.org/

### "ModuleNotFoundError: google.oauth2"
**Solution:** `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`

---

## Useful Aliases (Add to PowerShell Profile)

```powershell
# Edit profile
notepad $PROFILE

# Add these lines:
function Start-Playwright { & "$PSScriptRoot\.qwen\skills\browsing-with-playwright\scripts\start-server.ps1" }
function Stop-Playwright { & "$PSScriptRoot\.qwen\skills\browsing-with-playwright\scripts\stop-server.ps1" }
function Verify-Playwright { python "$PSScriptRoot\.qwen\skills\browsing-with-playwright\scripts\verify.py" }
```

Then you can just run:
```powershell
Start-Playwright
Stop-Playwright
Verify-Playwright
```

---

*Last updated: March 1, 2026*
