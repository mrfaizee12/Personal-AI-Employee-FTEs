# AI Employee Vault - Bronze Tier

Personal AI Employee implementation following the hackathon blueprint.

## Quick Start

### 1. Open Vault in Obsidian

Open this folder (`AI_Employee_Vault`) in Obsidian to use as your dashboard.

### 2. Start the File System Watcher

```bash
cd watchers
python filesystem_watcher.py ..
```

This watches the `/Inbox` folder for new files.

### 3. Run the Orchestrator

```bash
# Single cycle
python orchestrator.py .

# Continuous mode (every 60 seconds)
python orchestrator.py . --continuous
```

### 4. Use Qwen Code to Process Tasks

```bash
qwen --cd .
```

Then prompt:
> "Process all files in /Needs_Action folder. Read each file, create plans for complex tasks, and move completed items to /Done."

## Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md           # Main dashboard (open in Obsidian)
├── Company_Handbook.md    # Rules of engagement
├── Business_Goals.md      # Your objectives
├── orchestrator.py        # Master process
├── requirements.txt       # Python dependencies
├── watchers/
│   ├── base_watcher.py    # Base class for all watchers
│   └── filesystem_watcher.py  # File drop watcher
├── Inbox/                 # Drop files here
├── Needs_Action/          # Items pending processing
├── Plans/                 # Claude's action plans
├── Pending_Approval/      # Awaiting your approval
├── Approved/              # Approved actions
├── Rejected/              # Rejected actions
├── Done/                  # Completed items
├── Accounting/            # Financial records
├── Briefings/             # CEO briefings
└── Logs/                  # System logs
```

## How It Works

1. **Drop a file** into `/Inbox` folder
2. **Watcher detects** it and creates action file in `/Needs_Action/`
3. **Orchestrator triggers** Qwen Code to process
4. **Qwen reads** the file, creates a plan, executes actions
5. **You approve** sensitive actions (move from `/Pending_Approval` to `/Approved`)
6. **Qwen completes** the task and moves to `/Done`

## Bronze Tier Capabilities

✅ Obsidian vault with Dashboard.md and Company_Handbook.md  
✅ File System Watcher (monitors /Inbox folder)  
✅ Claude Code integration (manual trigger)  
✅ Basic folder structure (/Inbox, /Needs_Action, /Done)  
✅ Orchestrator for workflow management  

## Next Steps (Silver Tier)

- Add Gmail Watcher
- Add WhatsApp Watcher
- Implement MCP servers for external actions
- Add human-in-the-loop approval workflow
- Schedule with cron/Task Scheduler

## Troubleshooting

**Watcher not detecting files?**
- Ensure watcher is running: `python filesystem_watcher.py ..`
- Check logs in `/Logs/` folder
- Verify file is not a `.md` file (those are ignored)

**Orchestrator not updating dashboard?**
- Run with verbose output: `python orchestrator.py .`
- Check file permissions on Dashboard.md

**Qwen Code not processing?**
- Ensure Qwen Code is installed: `qwen --version`
- Run Qwen in the vault directory: `qwen --cd .`

## Security Notes

- Never commit `.env` files with credentials
- Keep API keys in environment variables
- Review all actions in `/Logs/` regularly
- Start with `DRY_RUN=true` for sensitive operations

---

*Built for Personal AI Employee Hackathon 0 - Bronze Tier*
