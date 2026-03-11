# LinkedIn Poster - Complete Guide

## ✅ Silver Tier Requirement: "Automatically Post on LinkedIn"

The LinkedIn watcher now supports **both monitoring AND posting**!

---

## Commands

### 1. Login (First Time)

```powershell
python watchers\linkedin_watcher.py --login
```

- Browser opens
- You log in to LinkedIn
- Session saved
- Browser closes automatically

### 2. Post to LinkedIn

```powershell
# Simple text post
python watchers\linkedin_watcher.py --post "Excited to announce our new AI Employee project! #AI #Automation"

# Post with image
python watchers\linkedin_watcher.py --post "Check out our latest update!" --image "C:\path\to\image.png"
```

### 3. Monitor LinkedIn

```powershell
python watchers\linkedin_watcher.py .
```

- Checks notifications every 5 minutes
- Checks messages
- Creates action files in `Needs_Action/`

---

## How Posting Works

```python
1. Opens browser with saved session (already logged in)
2. Navigates to LinkedIn feed
3. Clicks "Start a post" button
4. Types your content
5. Adds image (if provided)
6. Clicks "Post" button
7. Confirms post was published
8. Closes browser
```

---

## Example Posts

### Business Update

```powershell
python watchers\linkedin_watcher.py --post "🎉 Excited to share that we've completed the Silver Tier of our AI Employee project! 

Key features:
✅ Gmail monitoring
✅ LinkedIn automation
✅ Automated approvals
✅ Smart scheduling

#AI #Automation #Productivity"
```

### Lead Generation

```powershell
python watchers\linkedin_watcher.py --post "💡 Are you struggling with manual data entry and email management?

Our AI Employee can help:
- Auto-process emails
- Monitor communications 24/7
- Generate smart responses
- Save hours daily

DM me to learn more!

#BusinessAutomation #AI #Productivity"
```

### With Image

```powershell
python watchers\linkedin_watcher.py --post "📊 Weekly progress update! Our AI Employee is now fully functional." --image "G:\Projects\screenshot.png"
```

---

## Integration with Qwen Code

The real power comes from **automated posting via Qwen Code**:

### Workflow

1. **Qwen generates post** from business update
2. **Creates approval file** in `Pending_Approval/`
3. **You approve** by moving to `Approved/`
4. **Orchestrator posts** to LinkedIn
5. **Logs result** and moves to `Done/`

### Example: Auto-Generate Post from Business News

```markdown
File: Needs_Action/BUSINESS_UPDATE_new_client.md

---
type: business_update
content: "Just signed a $5000 deal with Client X"
---

Generate a LinkedIn post about this business update.
```

**Qwen Code processes this and:**
1. Generates post content
2. Creates approval file
3. After approval, calls: `python linkedin_watcher.py --post "..."`

---

## Human-in-the-Loop (HITL) Pattern

For safety, always use approval workflow:

```
1. Qwen creates: Pending_Approval/APPROVAL_linkedin_post.md
   Content: "Post: Excited to announce..."
   
2. You review and move to: Approved/

3. Orchestrator executes:
   python linkedin_watcher.py --post "Excited to announce..."

4. Result logged, file moved to Done/
```

---

## Scheduling Posts

Use Windows Task Scheduler or cron:

### Windows Task Scheduler

```powershell
# Create scheduled task to post every weekday at 9 AM
python ..\scheduling_helper.py install --task linkedin_post --trigger cron --value "09:00"
```

### Manual Scheduling

```powershell
# Post every day at 9 AM (add to Task Scheduler)
cd AI_Employee_Vault
python watchers\linkedin_watcher.py --post "Good morning! Here's your daily productivity tip..."
```

---

## Best Practices

### ✅ Do's

- **Use approval workflow** for all posts
- **Review generated content** before posting
- **Add relevant hashtags** (3-5 max)
- **Include images** for higher engagement
- **Post during business hours** (9 AM - 5 PM)
- **Keep posts under 1300 characters**

### ❌ Don'ts

- Don't post sensitive client information
- Don't post without review
- Don't spam (max 1-2 posts per day)
- Don't use too many hashtags

---

## Troubleshooting

### "Not logged in"

**Solution:** `python linkedin_watcher.py --login`

### "Could not find post button"

**Cause:** LinkedIn changed their UI

**Solution:** The watcher tries multiple selectors. If it still fails, manually verify you can see the "Start a post" button on LinkedIn.

### "Post button is disabled"

**Cause:** Post content is empty or LinkedIn thinks you're a bot

**Solution:** 
- Make sure content is not empty
- Wait a few seconds between actions
- Make sure you're logged in

### "Image not found"

**Solution:** Check the file path is absolute and exists

---

## Quick Reference

```powershell
# Login (first time)
python watchers\linkedin_watcher.py --login

# Post text
python watchers\linkedin_watcher.py --post "Your post content here"

# Post with image
python watchers\linkedin_watcher.py --post "Content" --image "C:\path\to\image.png"

# Monitor for activity
python watchers\linkedin_watcher.py .

# Monitor with custom interval (2 minutes)
python watchers\linkedin_watcher.py . --interval 120
```

---

## Silver Tier Status

| Requirement | Status |
|-------------|--------|
| 2+ Watcher scripts | ✅ Gmail + LinkedIn + FileSystem |
| **Auto-post on LinkedIn** | ✅ **COMPLETE** |
| Plan.md generation | ✅ Implemented |
| Working MCP server | ✅ Email MCP |
| HITL workflow | ✅ Implemented |
| Scheduling | ✅ Created |

---

*Last updated: March 8, 2026*
