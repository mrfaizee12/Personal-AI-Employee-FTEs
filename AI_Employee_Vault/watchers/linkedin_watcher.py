"""
LinkedIn Watcher - Monitors LinkedIn for new notifications and messages.

Uses direct Playwright (not MCP) with persistent browser session.
This follows the same pattern as WhatsApp Watcher in the hackathon document.

Usage:
    python linkedin_watcher.py /path/to/vault
    
First time setup:
    python linkedin_watcher.py /path/to/vault --login
    (Manually log in to LinkedIn when browser opens)
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from base_watcher import BaseWatcher

# Try to import Playwright
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not installed. Run: pip install playwright")
    print("Then run: playwright install")


class LinkedInWatcher(BaseWatcher):
    """Watches LinkedIn for new activity using Playwright with persistent session."""
    
    def __init__(self, vault_path: str, check_interval: int = 300,
                 session_path: str = None):
        """
        Initialize the LinkedIn watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 300 = 5 min)
            session_path: Path to store persistent browser session
        """
        super().__init__(vault_path, check_interval)
        
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error('Playwright not available')
            return
        
        # Session path for persistent browser context
        self.session_path = Path(session_path) if session_path else None
        if not self.session_path:
            self.session_path = self.vault_path / '.linkedin_session'
        
        # Ensure session directory exists
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f'Session path: {self.session_path}')
    
    def check_for_updates(self) -> list:
        """Check for new LinkedIn notifications using Playwright."""
        notifications = []
        
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context (saved session)
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=True,  # Run in background
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox'
                    ]
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Try to go to LinkedIn notifications
                try:
                    page.goto('https://www.linkedin.com/notifications/', 
                             timeout=30000, wait_until='domcontentloaded')
                    
                    # Wait for page to load
                    page.wait_for_timeout(5000)
                    
                    # Check if we're on login page (session expired)
                    if 'login' in page.url.lower():
                        self.logger.warning('LinkedIn session expired. Need to re-login.')
                        browser.close()
                        return []
                    
                    # Get page content and look for notifications
                    content = page.content()
                    
                    # Look for notification indicators
                    if 'notification' in content.lower() or 'unread' in content.lower():
                        # Extract notification text
                        notifications_text = self._extract_notifications(page)
                        if notifications_text:
                            notifications.append({
                                'type': 'notification',
                                'content': notifications_text,
                                'timestamp': datetime.now().isoformat()
                            })
                    
                    # Also check messages
                    try:
                        page.goto('https://www.linkedin.com/messaging/', 
                                 timeout=30000, wait_until='domcontentloaded')
                        page.wait_for_timeout(3000)
                        
                        msg_content = page.content()
                        if 'message' in msg_content.lower():
                            messages_text = self._extract_messages(page)
                            if messages_text:
                                notifications.append({
                                    'type': 'message',
                                    'content': messages_text,
                                    'timestamp': datetime.now().isoformat()
                                })
                    except Exception as e:
                        self.logger.debug(f'Could not check messages: {e}')
                    
                    browser.close()
                    
                except Exception as e:
                    self.logger.error(f'Error navigating LinkedIn: {e}')
                    browser.close()
                    return []
                    
        except Exception as e:
            self.logger.error(f'Error checking LinkedIn: {e}')
        
        return notifications
    
    def _extract_notifications(self, page) -> str:
        """Extract notification text from the page."""
        try:
            # Try to get notification elements
            notifications = []
            
            # Look for notification list items
            elements = page.query_selector_all('[aria-label*="notification"]')
            for elem in elements[:5]:  # Get first 5 notifications
                try:
                    text = elem.inner_text()
                    if text.strip():
                        notifications.append(text.strip())
                except:
                    pass
            
            # If no specific elements, get page title and some content
            if not notifications:
                title = page.title()
                notifications.append(f'LinkedIn Page: {title}')
            
            return ' | '.join(notifications)[:500]  # Limit to 500 chars
            
        except Exception as e:
            self.logger.debug(f'Could not extract notifications: {e}')
            return 'LinkedIn notifications detected'
    
    def _extract_messages(self, page) -> str:
        """Extract message previews from LinkedIn messaging."""
        try:
            messages = []
            
            # Look for message conversation items
            elements = page.query_selector_all('[aria-label*="message"]')
            for elem in elements[:3]:  # Get first 3 messages
                try:
                    text = elem.inner_text()
                    if text.strip():
                        messages.append(text.strip())
                except:
                    pass
            
            if not messages:
                title = page.title()
                messages.append(f'LinkedIn Messaging: {title}')
            
            return ' | '.join(messages)[:500]
            
        except Exception as e:
            self.logger.debug(f'Could not extract messages: {e}')
            return 'LinkedIn messages detected'
    
    def post_to_linkedin(self, content: str, image_path: str = None) -> bool:
        """
        Post content to LinkedIn.
        
        Args:
            content: The post content (text)
            image_path: Optional path to image to attach
            
        Returns:
            True if post was successful, False otherwise
        """
        print('[INFO] Starting LinkedIn post...')
        
        if not PLAYWRIGHT_AVAILABLE:
            print('[ERROR] Playwright not installed')
            return False
        
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,  # Show browser so user can see what's happening
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage'
                    ],
                    viewport={'width': 1280, 'height': 800}
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to LinkedIn feed
                print('[INFO] Navigating to LinkedIn...')
                page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=30000)
                page.wait_for_timeout(5000)
                
                # Check if logged in
                if 'login' in page.url.lower():
                    print('[ERROR] Not logged in. Run: python linkedin_watcher.py --login')
                    browser.close()
                    return False
                
                # Find and click the "Start a post" button
                print('[INFO] Opening post composer...')
                try:
                    # Try different selectors for the post button
                    post_button = None
                    selectors = [
                        '[aria-label="Start a post"]',
                        'button:has-text("Start a post")',
                        '.share-box-feed-entry__trigger'
                    ]
                    for selector in selectors:
                        try:
                            post_button = page.query_selector(selector)
                            if post_button:
                                break
                        except:
                            pass
                    
                    if post_button:
                        post_button.click()
                        page.wait_for_timeout(3000)
                    else:
                        print('[WARN] Could not find post button, trying alternative method...')
                        # Try to find the text area directly
                        pass
                        
                except Exception as e:
                    print(f'[WARN] Error clicking post button: {e}')
                
                # Find the text area and type the content
                print('[INFO] Entering post content...')
                try:
                    # Look for the editable text area
                    text_area = page.query_selector('[role="textbox"][contenteditable="true"]')
                    if text_area:
                        text_area.fill(content)
                        page.wait_for_timeout(2000)
                        print('[OK] Post content entered')
                    else:
                        print('[ERROR] Could not find text area for post')
                        browser.close()
                        return False
                except Exception as e:
                    print(f'[ERROR] Error entering text: {e}')
                    browser.close()
                    return False
                
                # Add image if provided
                if image_path and os.path.exists(image_path):
                    print(f'[INFO] Adding image: {image_path}')
                    try:
                        # Find and click the media/photo button
                        media_button = page.query_selector('input[type="file"][accept*="image"]')
                        if media_button:
                            media_button.set_input_files(image_path)
                            page.wait_for_timeout(3000)
                            print('[OK] Image added')
                    except Exception as e:
                        print(f'[WARN] Could not add image: {e}')
                
                # Click the Post button
                print('[INFO] Posting...')
                try:
                    # Look for the Post button
                    post_submit_button = None
                    selectors = [
                        'button:has-text("Post")',
                        '[aria-label="Post"]',
                        'button.share-box-feed-entry__submit-button'
                    ]
                    for selector in selectors:
                        try:
                            post_submit_button = page.query_selector(selector)
                            if post_submit_button:
                                # Check if button is enabled
                                if not post_submit_button.is_disabled():
                                    break
                                post_submit_button = None
                        except:
                            pass
                    
                    if post_submit_button:
                        post_submit_button.click()
                        page.wait_for_timeout(5000)
                        print('[OK] Post submitted!')
                        
                        # Check for success message
                        if 'posted' in page.content().lower() or 'feed' in page.url.lower():
                            print('[OK] Post successfully published to LinkedIn')
                            browser.close()
                            return True
                        else:
                            print('[WARN] Post may not have been published')
                            browser.close()
                            return False
                    else:
                        print('[ERROR] Could not find Post button')
                        browser.close()
                        return False
                        
                except Exception as e:
                    print(f'[ERROR] Error submitting post: {e}')
                    browser.close()
                    return False
                
                browser.close()
                return True
                
        except Exception as e:
            print(f'[ERROR] LinkedIn post failed: {e}')
            return False
    
    def create_action_file(self, notification: dict) -> Path:
        
        filename = f"LINKEDIN_{notif_type}_{timestamp}.md"
        filepath = self.needs_action / filename
        
        content = f'''---
type: linkedin_{notif_type}
source: LinkedIn
received: {notification.get('timestamp', datetime.now().isoformat())}
priority: medium
status: pending
---

# LinkedIn {notif_type.title()} Detected

**Type:** {notif_type}  
**Received:** {notification.get('timestamp', 'Unknown')}

## Content

{notification.get('content', 'No content available')}

## Suggested Actions

- [ ] Review LinkedIn activity
- [ ] Respond to important messages (create approval request)
- [ ] Post updates if appropriate (requires approval)
- [ ] Check LinkedIn manually: https://www.linkedin.com/
- [ ] Move to /Done when complete

## Notes

*Add your analysis and response draft here...*

---
*Created by LinkedInWatcher*

**Note:** This watcher uses Playwright with persistent browser session.
If session expires, run: `python linkedin_watcher.py --login`
'''
        
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f'Created action file: {filename}')
        return filepath
    
    def login(self):
        """Interactive LinkedIn login to create persistent session."""
        print('[INFO] Starting LinkedIn login process...')
        print('[INFO] A browser window will open. Please log in to LinkedIn.')
        print('[INFO] After successful login, the browser will close automatically.')
        print('[INFO] Your session will be saved for future use.')
        print()
        print('[INFO] IMPORTANT: Complete any 2FA/CAPTCHA if prompted.')
        print('[INFO] Make sure you reach your LinkedIn feed page.')
        print()
        
        if not PLAYWRIGHT_AVAILABLE:
            print('[ERROR] Playwright not installed.')
            print('Run: pip install playwright')
            print('Then: playwright install')
            return False
        
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,  # Show browser for login
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage'
                    ],
                    viewport={'width': 1280, 'height': 800}
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to LinkedIn login
                print('[INFO] Navigating to LinkedIn login...')
                page.goto('https://www.linkedin.com/login', wait_until='domcontentloaded', timeout=30000)
                
                print('[INFO] Please log in to LinkedIn in the browser window.')
                print('[INFO] Waiting up to 180 seconds for login...')
                print('[INFO] Checking every 10 seconds...')
                print()
                
                # Wait for user to log in (check every 10 seconds for up to 180 seconds)
                logged_in = False
                for i in range(18):
                    page.wait_for_timeout(10000)
                    
                    # Check if we're on feed page (logged in)
                    current_url = page.url.lower()
                    if 'feed' in current_url or '/mynetwork/' in current_url or '/jobs/' in current_url:
                        print('[OK] Login successful! Detected LinkedIn feed page.')
                        logged_in = True
                        break
                    elif i % 6 == 5:  # Every minute
                        print(f'[INFO] Still waiting... ({(i+1)*10} seconds)')
                
                if not logged_in:
                    print()
                    print('[WARN] Login may not have completed.')
                    print('[INFO] Please manually verify you can access LinkedIn.')
                    print('[INFO] Session data is saved anyway.')
                
                # Give user a moment then close
                page.wait_for_timeout(5000)
                browser.close()
                
                print()
                print('[INFO] Browser closed.')
                print(f'[INFO] Session saved to: {self.session_path.absolute()}')
                print('[INFO] Next time you run the watcher, you will be logged in!')
                print()
                print('[NEXT] Run: python linkedin_watcher.py .')
                
                return True
                
        except Exception as e:
            print(f'[ERROR] Login process failed: {e}')
            return False


def main():
    """Entry point for the LinkedIn watcher."""
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Watcher for AI Employee')
    parser.add_argument('vault_path', nargs='?', default='.', 
                       help='Path to Obsidian vault')
    parser.add_argument('--login', action='store_true',
                       help='Run interactive login to create session')
    parser.add_argument('--post', type=str,
                       help='Post content to LinkedIn (provide text in quotes)')
    parser.add_argument('--image', type=str,
                       help='Path to image to attach with post')
    parser.add_argument('--interval', type=int, default=300,
                       help='Check interval in seconds')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f'[ERROR] Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    # Create watcher
    watcher = LinkedInWatcher(str(vault_path), check_interval=args.interval)
    
    # Run login, post, or watcher
    if args.login:
        success = watcher.login()
        sys.exit(0 if success else 1)
    elif args.post:
        # Post to LinkedIn
        print(f'[INFO] Posting to LinkedIn...')
        success = watcher.post_to_linkedin(args.post, args.image)
        sys.exit(0 if success else 1)
    else:
        # Run the watcher
        print('[INFO] Starting LinkedIn Watcher...')
        print('[INFO] Checking every {} seconds'.format(args.interval))
        print('[INFO] If not logged in, run: python linkedin_watcher.py --login')
        watcher.run()


if __name__ == '__main__':
    main()
