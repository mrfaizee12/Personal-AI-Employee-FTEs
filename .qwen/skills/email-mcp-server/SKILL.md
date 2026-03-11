---
name: email-mcp-server
description: |
  MCP Server for sending emails via Gmail API. Provides tools for composing,
  drafting, and sending emails. Supports attachments and HTML content.
  Requires Gmail API credentials with send scope.
---

# Email MCP Server

Model Context Protocol server for Gmail email operations.

## Prerequisites

### 1. Gmail API Setup

Same credentials as Gmail Watcher, but with send scope:

```env
SCOPES = [
    'https://www.googleapis.com/auth/gmail_send',
    'https://www.googleapis.com/auth/gmail.compose'
]
```

### 2. Install Dependencies

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 3. Authentication

```bash
python mcp_servers/email_mcp.py --authenticate
```

## Tools Provided

| Tool | Description |
|------|-------------|
| `email_send` | Send an email immediately |
| `email_draft` | Create a draft email |
| `email_reply` | Reply to an existing email |

## Usage

### Start the MCP Server

```bash
# HTTP transport (recommended)
python mcp_servers/email_mcp.py --port 8809

# Or stdio transport (for Claude Code integration)
python mcp_servers/email_mcp.py
```

### Call Tools via HTTP

```bash
# Send an email
python scripts/mcp-client.py call -u http://localhost:8809 \
  -t email_send \
  -p '{"to": "client@example.com", "subject": "Invoice #123", "body": "Please find attached..."}'

# Create a draft
python scripts/mcp-client.py call -u http://localhost:8809 \
  -t email_draft \
  -p '{"to": "team@example.com", "subject": "Meeting Notes", "body": "Here are the notes..."}'
```

## Tool Schemas

### email_send

```json
{
  "to": "recipient@example.com (required)",
  "subject": "Email subject (required)",
  "body": "Email body text (required)",
  "html": "HTML body (optional)",
  "attachment": "File path to attach (optional)"
}
```

### email_draft

```json
{
  "to": "recipient@example.com (required)",
  "cc": "cc@example.com (optional)",
  "bcc": "bcc@example.com (optional)",
  "subject": "Email subject (required)",
  "body": "Email body (required)",
  "html": "HTML body (optional)"
}
```

### email_reply

```json
{
  "thread_id": "Gmail thread ID (required)",
  "body": "Reply body (required)",
  "include_original": "Include original email (default: true)"
}
```

## Configuration

Create `.env` file:

```env
GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
GMAIL_TOKEN_PATH=/path/to/token.json
DRY_RUN=false
```

## Human-in-the-Loop Pattern

For sensitive emails, use draft mode first:

1. Qwen creates draft via `email_draft`
2. Creates approval file in `/Pending_Approval/`
3. User reviews and moves to `/Approved/`
4. Orchestrator sends the draft

## Example: Send Invoice Email

```python
# Via MCP client
result = client.call_tool('email_send', {
    'to': 'client@example.com',
    'subject': 'Invoice #1234 - January 2026',
    'body': '''Dear Client,

Please find attached your invoice for January 2026.

Amount: $1,500.00
Due Date: February 15, 2026

Thank you for your business!

Best regards,
Your Company''',
    'attachment': '/path/to/invoice.pdf'
})
```

## Error Handling

| Error | Meaning | Solution |
|-------|---------|----------|
| `credentials_not_found` | No valid Gmail credentials | Run `--authenticate` |
| `quota_exceeded` | Gmail API rate limit | Wait 24 hours |
| `invalid_recipient` | Bad email format | Check email address |
| `attachment_not_found` | File doesn't exist | Verify file path |

## Security Notes

- ⚠️ Never commit credentials or tokens
- ✅ Use DRY_RUN mode for testing
- ✅ Log all sent emails
- ✅ Require approval for new recipients

## Integration with Orchestrator

The orchestrator can trigger email sending after approval:

```bash
# Terminal: Start Email MCP Server
python mcp_servers/email_mcp.py --port 8809

# Terminal: Start Orchestrator
python orchestrator.py . --continuous
```

When an approval file is moved to `/Approved/`, the orchestrator calls the MCP server to send the email.
