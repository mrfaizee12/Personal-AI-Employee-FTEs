# Silver Tier - Focus: Gmail + LinkedIn Watchers

**Status:** In Progress  
**Date:** March 1, 2026

---

## Silver Tier Requirements (Hackathon Document)

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | All Bronze requirements | ✅ | Complete |
| 2 | Two or more Watcher scripts | 🟡 | FileSystemWatcher ✅ + GmailWatcher 🟡 + LinkedInWatcher 🟡 |
| 3 | Auto-post on LinkedIn | ⏳ | LinkedIn MCP Server ready |
| 4 | Plan.md generation | ✅ | Orchestrator updated |
| 5 | One working MCP server | ⏳ | Email MCP ready |
| 6 | HITL approval workflow | ✅ | Implemented in orchestrator |
| 7 | Basic scheduling | ✅ | scheduling_helper.py created |
| 8 | All as Agent Skills | ✅ | Skills documented |

---

## Focus Area: Gmail + LinkedIn Watchers

### Gmail Watcher ✅

**File:** `watchers/gmail_watcher.py`

**Status:**
- [x] Script created
- [x] OAuth2 authentication flow
- [x] Credentials.json detected
- [ ] Token.json (awaiting user authorization)
- [ ] First test run

**Setup Steps:**

1. **Credentials file exists:** ✅
   - Location: `G:\gitub-desktop\Personal-AI-Employee-FTEs\credentials.json`
   - Project: ai-employee-488821

2. **Run authentication:**
   ```bash
   cd AI_Employee_Vault
   python watchers/gmail_watcher.py --authenticate
   ```

3. **Authorize the app:**
   - Visit the URL shown in terminal
   - Sign in with Google
   - Grant Gmail API permissions
   - Redirect to localhost:8080

4. **Token saved:** `AI_Employee_Vault/token.json`

5. **Test the watcher:**
   ```bash
   python watchers/gmail_watcher.py .
   ```

**Configuration:**
- Check interval: 120 seconds (default)
- Keywords filter: urgent, asap, invoice, payment, help
- Scope: `gmail_readonly` (safe, read-only access)

---

### LinkedIn Watcher 🟡

**File:** `watchers/linkedin_watcher.py`

**Status:**
- [x] Script created
- [x] Playwright MCP integration
- [ ] Login test
- [ ] First monitoring run

**Setup Steps:**

1. **Start Playwright MCP:**
   ```bash
   bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh
   ```

2. **Run LinkedIn login:**
   ```bash
   cd AI_Employee_Vault
   python watchers/linkedin_watcher.py --login
   ```

3. **Log in to LinkedIn:**
   - Browser window opens
   - Enter credentials
   - Complete any 2FA
   - Wait for "Login successful" message

4. **Test the watcher:**
   ```bash
   python watchers/linkedin_watcher.py .
   ```

**Configuration:**
- Check interval: 300 seconds (5 minutes)
- Keywords: message, connection, job, post, comment, hire, opportunity
- Uses browser automation (no API needed)

---

## Running Both Watchers

### Terminal Setup

```bash
# Terminal 1: Gmail Watcher
cd AI_Employee_Vault
python watchers/gmail_watcher.py .

# Terminal 2: LinkedIn Watcher
cd AI_Employee_Vault
python watchers/linkedin_watcher.py .

# Terminal 3: File System Watcher (Bronze)
cd AI_Employee_Vault
python watchers/filesystem_watcher.py .

# Terminal 4: Orchestrator
cd AI_Employee_Vault
python orchestrator.py . --continuous
```

---

## Testing Checklist

### Gmail Watcher Test

- [ ] Authentication completed
- [ ] token.json created
- [ ] Watcher starts without errors
- [ ] Send test email to yourself
- [ ] Email detected within 2 minutes
- [ ] Action file created in Needs_Action
- [ ] Orchestrator picks up the file

### LinkedIn Watcher Test

- [ ] Playwright MCP running
- [ ] Login successful
- [ ] Session saved
- [ ] Watcher starts without errors
- [ ] Notifications detected
- [ ] Action file created in Needs_Action

### Integration Test

- [ ] Drop file in Inbox
- [ ] Send email
- [ ] Both watchers running
- [ ] Orchestrator processing
- [ ] Qwen Code can read all action files

---

## Skills Created for Silver Tier

| Skill | Location | Status |
|-------|----------|--------|
| gmail-watcher | `.qwen/skills/gmail-watcher/SKILL.md` | ✅ |
| email-mcp-server | `.qwen/skills/email-mcp-server/SKILL.md` | ✅ |
| linkedin-poster | `.qwen/skills/linkedin-poster/SKILL.md` | ✅ |
| hitl-approval-workflow | `.qwen/skills/hitl-approval-workflow/SKILL.md` | ✅ |
| plan-generator | `.qwen/skills/plan-generator/SKILL.md` | ✅ |

---

## Next Steps

1. **Complete Gmail Authentication** (user action required)
2. **Test LinkedIn Login** (user action required)
3. **Run both watchers simultaneously**
4. **Verify action files are created**
5. **Test Qwen Code processing**
6. **Document any issues**

---

## Troubleshooting

### Gmail Issues

| Issue | Solution |
|-------|----------|
| "Credentials not found" | Check credentials.json path |
| "Token expired" | Re-run `--authenticate` |
| "No emails detected" | Check Gmail labels, filters |
| "API quota exceeded" | Wait 24 hours |

### LinkedIn Issues

| Issue | Solution |
|-------|----------|
| "MCP client not available" | Start Playwright MCP first |
| "Login timeout" | Try again, increase wait time |
| "No notifications" | Check if logged in correctly |
| "Browser won't open" | Check Playwright installation |

---

*Focus: Complete Gmail + LinkedIn watcher setup first, then expand to other Silver Tier features.*
