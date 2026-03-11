---
name: linkedin-poster
description: |
  MCP Server for posting to LinkedIn. Creates and schedules posts,
  generates content from business updates, and tracks engagement.
  Uses LinkedIn API or browser automation via Playwright.
---

# LinkedIn Poster Skill

Automated LinkedIn posting for business lead generation.

## Prerequisites

### Option 1: LinkedIn API (Recommended)

1. Create LinkedIn App at [LinkedIn Developer](https://www.linkedin.com/developers/)
2. Get API credentials
3. Request `w_member_social` permission

### Option 2: Browser Automation

Uses Playwright MCP (already installed) for browser-based posting.

## Usage

### Start LinkedIn MCP Server

```bash
# Browser automation mode (no API needed)
python mcp_servers/linkedin_mcp.py --port 8810
```

### Tools Provided

| Tool | Description |
|------|-------------|
| `linkedin_post` | Create and publish a post |
| `linkedin_schedule` | Schedule a post for later |
| `linkedin_generate` | Generate post from business update |

## Tool Schemas

### linkedin_post

```json
{
  "content": "Post text (required, max 3000 chars)",
  "image": "Image file path (optional)",
  "hashtags": ["hashtag1", "hashtag2"]
}
```

### linkedin_schedule

```json
{
  "content": "Post text (required)",
  "scheduled_time": "ISO 8601 datetime",
  "image": "Image file path (optional)"
}
```

### linkedin_generate

```json
{
  "business_update": "Description of what happened",
  "tone": "professional | casual | enthusiastic"
}
```

## Usage Examples

### Post via HTTP

```bash
python scripts/mcp-client.py call -u http://localhost:8810 \
  -t linkedin_post \
  -p '{"content": "Excited to announce our new AI Employee product!", "hashtags": ["AI", "Automation"]}'
```

### Generate Post from Update

```bash
python scripts/mcp-client.py call -u http://localhost:8810 \
  -t linkedin_generate \
  -p '{"business_update": "Closed $5000 deal with Client A", "tone": "professional"}'
```

## Browser Automation Flow

```python
# 1. Navigate to LinkedIn
browser_navigate: https://www.linkedin.com/feed/

# 2. Click create post
browser_click: ref="e42" (post creation box)

# 3. Type content
browser_type: ref="e55", text="Post content here..."

# 4. Add image (optional)
browser_click: ref="e60" (image button)
browser_file_upload: paths=["/path/to/image.jpg"]

# 5. Post
browser_click: ref="e70" (Post button)

# 6. Wait for confirmation
browser_wait_for: text="Your post has been shared"
```

## Content Templates

### Business Update

```
🎉 Business Update

We're excited to share that [achievement]!

This milestone represents [significance].

Thank you to our amazing clients and partners.

#Business #Growth #[Industry]
```

### Lead Generation

```
💡 [Industry Insight]

Are you struggling with [common problem]?

We've helped [X] clients solve this by [solution].

DM me to learn how we can help you too!

#[Industry] #Solution #Business
```

### Client Success

```
✅ Client Success Story

Just helped [Client Type] achieve [result]!

The key was [strategy/insight].

Ready for similar results? Let's talk!

#ClientSuccess #Results #[Industry]
```

## Human-in-the-Loop

For public posts, use approval workflow:

1. Qwen generates draft post
2. Creates approval file in `/Pending_Approval/`
3. User reviews and approves
4. MCP server publishes

## Scheduling

### Windows Task Scheduler

```xml
<Task>
  <Trigger>
    <CalendarTrigger>
      <StartBoundary>2026-02-28T09:00:00</StartBoundary>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Trigger>
  <Action>
    <Exec>
      <Command>python</Command>
      <Arguments>mcp_servers/linkedin_mcp.py --post-daily</Arguments>
    </Exec>
  </Action>
</Task>
```

### Cron (Linux/Mac)

```bash
# Post every weekday at 9 AM
0 9 * * 1-5 cd /path/to/vault && python mcp_servers/linkedin_mcp.py --post-daily
```

## Integration with Orchestrator

```python
# In orchestrator.py
def post_to_linkedin(self, content: str, hashtags: list = None):
    """Post to LinkedIn via MCP server."""
    result = self.mcp_client.call('linkedin_post', {
        'content': content,
        'hashtags': hashtags or []
    })
    self.log_action('linkedin_post', result)
```

## Best Practices

- ✅ Post during business hours (9 AM - 5 PM)
- ✅ Use 3-5 relevant hashtags
- ✅ Include images for higher engagement
- ✅ Keep posts under 1300 characters
- ✅ Engage with comments within 24 hours

## Security

- ⚠️ Never post sensitive client information
- ⚠️ Review all posts before publishing
- ⚠️ Use approval workflow for public posts
