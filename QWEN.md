# Personal AI Employee FTEs - Project Context

## Project Overview

This is a **hackathon/educational project** focused on building "Digital FTEs" (Full-Time Equivalents) - autonomous AI agents that act as personal/business employees. The project uses **Claude Code** as the reasoning engine and **Obsidian** (local Markdown) as the dashboard/memory system.

**Core Concept:** Create a 24/7 autonomous agent that:
- Monitors communications (Gmail, WhatsApp, LinkedIn)
- Manages business tasks and accounting
- Posts to social media
- Generates executive briefings ("Monday Morning CEO Briefing")
- Operates with human-in-the-loop approval for sensitive actions

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

## Architecture

### Key Components

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Claude Code | Reasoning engine with Ralph Wiggum persistence loop |
| **Memory/GUI** | Obsidian Vault | Dashboard.md, Company_Handbook.md, task tracking |
| **Senses** | Python Watchers | Monitor Gmail, WhatsApp, filesystem for triggers |
| **Hands** | MCP Servers | Model Context Protocol for external actions |

### Folder Structure (Obsidian Vault)

```
Vault/
├── Dashboard.md              # Real-time summary
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Q1/Q2 objectives
├── Inbox/                    # New items to process
├── Needs_Action/             # Items requiring attention
├── Done/                     # Completed tasks
├── Plans/                    # Generated plans (Plan.md)
├── Pending_Approval/         # Awaiting human approval
├── Approved/                 # Approved actions
├── Accounting/               # Bank transactions, invoices
└── Briefings/                # CEO briefings
```

## Technologies & Dependencies

### Required Software
- **Claude Code** - Primary AI reasoning engine
- **Obsidian** v1.10.6+ - Knowledge base & dashboard
- **Python** 3.13+ - Watcher scripts, orchestration
- **Node.js** v24+ LTS - MCP servers
- **GitHub Desktop** - Version control

### Installed Skills
- **browsing-with-playwright** - Browser automation via Playwright MCP

### Key Python Scripts (in `.qwen/skills/browsing-with-playwright/scripts/`)
- `mcp-client.py` - Universal MCP client (HTTP/stdio transports)
- `verify.py` - Server health verification
- `start-server.sh` / `stop-server.sh` - Playwright MCP lifecycle

## Building & Running

### Playwright MCP Server

```bash
# Start the browser automation server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify it's running
python .qwen/skills/browsing-with-playwright/scripts/verify.py

# Stop the server (closes browser first)
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

### MCP Client Usage

```bash
# List available tools
python scripts/mcp-client.py list -u http://localhost:8808

# Call a tool (navigate)
python scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_navigate -p '{"url": "https://example.com"}'

# Take a screenshot
python scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_take_screenshot -p '{"type": "png", "fullPage": true}'

# Emit tool schemas as markdown
python scripts/mcp-client.py emit -u http://localhost:8808
```

### Ralph Wiggum Persistence Loop

For autonomous multi-step task completion:

```bash
# Start a Ralph loop (keeps Claude working until task complete)
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

## Development Conventions

### Agent Skills Pattern
All AI functionality should be implemented as [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) - reusable, promptable capabilities that Claude can invoke.

### Human-in-the-Loop (HITL)
For sensitive actions (payments, sending messages):
1. Claude creates approval request file in `/Pending_Approval/`
2. User reviews and moves file to `/Approved/` or `/Rejected/`
3. Orchestrator triggers actual MCP action only after approval

### Watcher Pattern
All watchers follow the `BaseWatcher` abstract class:
- Check for updates at defined intervals
- Create `.md` action files in `/Needs_Action/`
- Log errors gracefully
- Never block on failures

### Security Rules
- Secrets never sync (`.env`, tokens, WhatsApp sessions, banking creds)
- Cloud agents work in draft-only mode
- Local agent owns final "send/post" actions
- Vault sync includes only markdown/state files

## Hackathon Tiers

| Tier | Description | Estimated Time |
|------|-------------|----------------|
| **Bronze** | Foundation (1 watcher, basic vault) | 8-12 hours |
| **Silver** | Functional assistant (2+ watchers, MCP integration) | 20-30 hours |
| **Gold** | Autonomous employee (full integration, Odoo, briefings) | 40+ hours |
| **Platinum** | Cloud + Local deployment, 24/7 operation | 60+ hours |

## Key Files

| File | Purpose |
|------|---------|
| `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md` | Comprehensive hackathon guide, architecture blueprint |
| `skills-lock.json` | Tracks installed Qwen skills and their sources |
| `.qwen/skills/browsing-with-playwright/SKILL.md` | Playwright MCP usage documentation |
| `.qwen/skills/browsing-with-playwright/scripts/mcp-client.py` | Core MCP client library |

## Common Workflows

### Form Submission (Browser Automation)
1. Navigate to page (`browser_navigate`)
2. Get snapshot to find element refs (`browser_snapshot`)
3. Fill form fields using refs (`browser_fill_form` or `browser_type`)
4. Click submit (`browser_click`)
5. Wait for confirmation (`browser_wait_for`)
6. Screenshot result (`browser_take_screenshot`)

### Email Triage (Watcher Pattern)
1. Gmail Watcher polls for unread important emails
2. Creates `.md` file in `/Needs_Action/` with email content
3. Claude reads, drafts reply, moves to `/Pending_Approval/`
4. User approves, MCP sends email

### CEO Briefing Generation
1. Scheduled trigger (Sunday night via cron/Task Scheduler)
2. Claude reads `Business_Goals.md`, `Accounting/`, `Tasks/Done/`
3. Generates `Briefings/YYYY-MM-DD_Monday_Briefing.md`
4. Includes: Revenue, bottlenecks, proactive suggestions

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Playwright server not responding | Run `bash scripts/stop-server.sh && bash scripts/start-server.sh` |
| Element not found | Run `browser_snapshot` first to get current refs |
| Click fails | Try `browser_hover` first, then click |
| Form not submitting | Use `"submit": true` with `browser_type` |
| Ralph loop stuck | Check max iterations, review completion criteria |

## Resources

- **Zoom Meetings:** Wednesdays 10:00 PM PKT (First: Jan 7, 2026)
- **YouTube:** [@panaversity](https://www.youtube.com/@panaversity)
- **Ralph Wiggum Reference:** [GitHub](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
- **Agent Skills Docs:** [Claude Platform](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
