---
name: gmail-watcher
description: |
  Monitor Gmail for new unread/important emails and create action files in Obsidian vault.
  Uses Gmail API to fetch emails and creates .md files in /Needs_Action folder for processing.
  Requires Gmail API credentials setup.
---

# Gmail Watcher Skill

Monitors Gmail inbox and creates actionable files for new emails.

## Prerequisites

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json`

### 2. Install Dependencies

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 3. First-Time Authentication

```bash
python watchers/gmail_watcher.py --authenticate
```

This creates `token.json` for future use.

## Configuration

Create `.env` file in vault root:

```env
GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
GMAIL_TOKEN_PATH=/path/to/token.json
VAULT_PATH=/path/to/AI_Employee_Vault
CHECK_INTERVAL=120
```

## Usage

### Start Gmail Watcher

```bash
cd AI_Employee_Vault
python watchers\gmail_watcher.py .
```

### With Custom Settings

```bash
python watchers\gmail_watcher.py . --interval 60 --keywords "urgent,invoice,payment"
```

## How It Works

1. **Polls Gmail** every 120 seconds (configurable)
2. **Filters** unread + important emails
3. **Creates action file** in `/Needs_Action/`
4. **Logs** activity to `/Logs/`

## Action File Format

Each email creates a `.md` file:

```markdown
---
type: email
from: client@example.com
subject: Invoice Request
received: 2026-02-27T10:30:00
priority: high
status: pending
gmail_id: 18d4f2a3b5c6e7f8
---

# Email Content

Client message snippet here...

## Suggested Actions

- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
```

## Keywords Filter (Optional)

Only process emails containing specific keywords:

```bash
python watchers\gmail_watcher.py . --keywords "urgent,asap,invoice,payment,help"
```

## Files Created

| File | Purpose |
|------|---------|
| `watchers/gmail_watcher.py` | Main watcher script |
| `watchers/gmail_auth.py` | Authentication helper |
| `.env` | Configuration (never commit!) |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `credentials.json not found` | Download from Google Cloud Console |
| `token.json expired` | Run `--authenticate` again |
| `No emails detected` | Check Gmail labels/filters |
| `API quota exceeded` | Wait 24h or request quota increase |

## Security Notes

- ⚠️ **NEVER** commit `credentials.json` or `token.json` to git
- ⚠️ Add to `.gitignore`:
  ```
  credentials.json
  token.json
  .env
  ```
- ✅ Use app-specific passwords if 2FA enabled
- ✅ Rotate credentials monthly

## Example Output

```
2026-02-27 10:30:00 - GmailWatcher - INFO: Starting GmailWatcher
2026-02-27 10:30:00 - GmailWatcher - INFO: Watching folder: G:\...\AI_Employee_Vault
2026-02-27 10:32:15 - GmailWatcher - INFO: Found 2 new email(s)
2026-02-27 10:32:15 - GmailWatcher - INFO: Created action file for: EMAIL_18d4f2a3b5c6e7f8.md
```

## Integration with Orchestrator

Gmail Watcher works with the orchestrator:

1. Watcher creates file in `/Needs_Action/`
2. Orchestrator detects pending items
3. Orchestrator triggers Qwen Code
4. Qwen processes email and creates response

```bash
# Terminal 1: Gmail Watcher
python watchers\gmail_watcher.py .

# Terminal 2: Orchestrator
python orchestrator.py . --continuous
```
