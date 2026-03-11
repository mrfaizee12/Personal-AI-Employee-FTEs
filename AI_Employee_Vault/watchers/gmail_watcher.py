"""
Gmail Watcher - Monitors Gmail for new unread/important emails.

Creates action files in /Needs_Action folder for Qwen Code to process.

Usage:
    python gmail_watcher.py /path/to/vault
    python gmail_watcher.py /path/to/vault --authenticate  # First-time auth
"""

import sys
import os
import pickle
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher

# Google API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    import json
    GOOGLE_LIBS_AVAILABLE = True
except ImportError as e:
    GOOGLE_LIBS_AVAILABLE = False
    print(f"Warning: Google API libraries not installed: {e}")
    print("Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    print("\nTrying to continue anyway...")


class GmailWatcher(BaseWatcher):
    """Watches Gmail inbox for new unread/important emails."""
    
    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, vault_path: str, credentials_path: str = None,
                 token_path: str = None, check_interval: int = 120,
                 keywords: list = None, all_unread: bool = False,
                 debug: bool = False):
        """
        Initialize the Gmail watcher.

        Args:
            vault_path: Path to the Obsidian vault root
            credentials_path: Path to credentials.json from Google Cloud
            token_path: Path to store/load authentication token
            check_interval: Seconds between checks (default: 120)
            keywords: List of keywords to filter emails (optional)
            all_unread: If True, check all unread emails (not just 'important')
            debug: If True, show debug information about all emails
        """
        super().__init__(vault_path, check_interval)

        # Paths
        self.credentials_path = Path(credentials_path) if credentials_path else None
        self.token_path = Path(token_path) if token_path else None

        # Auto-detect paths if not provided
        if not self.credentials_path:
            self.credentials_path = Path(__file__).parent.parent.parent / 'credentials.json'
        if not self.token_path:
            self.token_path = Path(__file__).parent.parent / 'token.json'

        # Keywords filter
        self.keywords = keywords or []
        
        # Auto-approval mode - create approval files automatically
        self.auto_approve = True
        
        # Query mode
        self.all_unread = all_unread
        self.debug = debug

        # Gmail service
        self.service = None
        self.processed_ids = set()

        # Load previously processed email IDs
        self._load_processed_ids()

        self.logger.info(f'Credentials: {self.credentials_path}')
        self.logger.info(f'Token: {self.token_path}')
        self.logger.info(f'Query mode: {"all unread" if all_unread else "unread + important"}')
    
    def _load_processed_ids(self):
        """Load previously processed email IDs from cache file."""
        cache_file = self.vault_path / 'Logs' / '.gmail_cache.pkl'
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    self.processed_ids = pickle.load(f)
                self.logger.info(f'Loaded {len(self.processed_ids)} cached email IDs')
            except Exception as e:
                self.logger.warning(f'Could not load cache: {e}')
                self.processed_ids = set()
    
    def _save_processed_ids(self):
        """Save processed email IDs to cache file."""
        cache_file = self.vault_path / 'Logs' / '.gmail_cache.pkl'
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(self.processed_ids, f)
        except Exception as e:
            self.logger.error(f'Could not save cache: {e}')
    
    def _authenticate(self):
        """Run interactive authentication flow."""
        print("Starting Gmail authentication...")
        print(f"Using credentials: {self.credentials_path}")
        
        if not self.credentials_path.exists():
            print(f"\nError: credentials.json not found at {self.credentials_path}")
            print("\nDownload it from:")
            print("1. https://console.cloud.google.com/")
            print("2. Create/select project")
            print("3. Enable Gmail API")
            print("4. Create OAuth 2.0 credentials")
            print("5. Download credentials.json")
            sys.exit(1)
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_path), self.SCOPES)
            creds = flow.run_local_server(port=8080, prompt='consent')

            # Save token
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, 'w') as f:
                f.write(creds.to_json())

            print(f"\n[OK] Authentication successful!")
            print(f"Token saved to: {self.token_path}")
            print("\nYou can now run the watcher without --authenticate")

        except Exception as e:
            print(f"\n[ERROR] Authentication failed: {e}")
            sys.exit(1)
    
    def _get_credentials(self):
        """Get valid Gmail API credentials."""
        creds = None
        
        # Load from token file
        if self.token_path.exists():
            try:
                with open(self.token_path, 'r') as f:
                    token_data = f.read()
                creds = Credentials.from_authorized_user_info(
                    json.loads(token_data), self.SCOPES)
            except Exception as e:
                self.logger.warning(f'Could not load token: {e}')
        
        # Refresh or re-authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    from google.auth.transport.requests import Request
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.error(f'Could not refresh token: {e}')
                    creds = None
            
            if not creds:
                self.logger.error('No valid credentials. Run with --authenticate first.')
                return None
        
        return creds
    
    def _connect(self):
        """Connect to Gmail API."""
        creds = self._get_credentials()
        if not creds:
            return False
        
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info('Connected to Gmail API')
            return True
        except Exception as e:
            self.logger.error(f'Could not connect to Gmail API: {e}')
            return False
    
    def check_for_updates(self) -> list:
        """Check for new unread/important emails."""
        if not self.service:
            if not self._connect():
                return []

        emails = []

        try:
            # Build query based on mode
            if self.all_unread:
                query = 'is:unread'  # All unread emails
            else:
                query = 'is:unread is:important'  # Only important unread
            
            # Fetch emails
            if self.debug:
                print(f'\n[DEBUG] Gmail query: {query}')
            
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()

            messages = results.get('messages', [])
            
            if self.debug:
                print(f'[DEBUG] Found {len(messages)} email(s) matching query')

            for msg in messages:
                msg_id = msg['id']

                # Skip already processed
                if msg_id in self.processed_ids:
                    if self.debug:
                        print(f'[DEBUG] Skipping already processed: {msg_id}')
                    continue

                # Get full message details
                message = self.service.users().messages().get(
                    userId='me', id=msg_id
                ).execute()

                # Extract headers
                headers = {h['name']: h['value']
                          for h in message['payload']['headers']}

                email_data = {
                    'id': msg_id,
                    'from': headers.get('From', 'Unknown'),
                    'to': headers.get('To', ''),
                    'subject': headers.get('Subject', 'No Subject'),
                    'date': headers.get('Date', ''),
                    'snippet': message.get('snippet', ''),
                    'thread_id': message.get('threadId', '')
                }
                
                if self.debug:
                    print(f'\n[DEBUG] New email found:')
                    print(f'  From: {email_data["from"]}')
                    print(f'  Subject: {email_data["subject"]}')
                    print(f'  Date: {email_data["date"]}')

                # Apply keyword filter if set
                if self.keywords:
                    text = f"{email_data['subject']} {email_data['snippet']}".lower()
                    if not any(kw.lower() in text for kw in self.keywords):
                        if self.debug:
                            print(f'[DEBUG] Skipping (no keywords match)')
                        self.processed_ids.add(msg_id)
                        continue

                emails.append(email_data)
                self.processed_ids.add(msg_id)
                
                if self.debug:
                    print(f'[DEBUG] ✓ Added to processing queue')

        except HttpError as error:
            self.logger.error(f'Gmail API error: {error}')
        except Exception as e:
            self.logger.error(f'Error checking emails: {e}')

        # Save cache
        if emails:
            self._save_processed_ids()
        
        if self.debug:
            print(f'\n[DEBUG] Total emails to process: {len(emails)}')

        return emails
    
    def create_action_file(self, email_data: dict) -> Path:
        """Create an action file for the email."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_subject = "".join(c for c in email_data['subject'] 
                               if c.isalnum() or c in ' -_')[:50]
        
        filename = f"EMAIL_{timestamp}_{safe_subject}.md"
        filepath = self.needs_action / filename
        
        # Parse date
        received_date = email_data.get('date', '')
        if received_date:
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(received_date)
                received_iso = dt.isoformat()
            except:
                received_iso = datetime.now().isoformat()
        else:
            received_iso = datetime.now().isoformat()
        
        content = f'''---
type: email
from: {email_data['from']}
to: {email_data['to']}
subject: {email_data['subject']}
received: {received_iso}
priority: high
status: pending
gmail_id: {email_data['id']}
thread_id: {email_data['thread_id']}
---

# Email Received

**From:** {email_data['from']}  
**To:** {email_data['to']}  
**Subject:** {email_data['subject']}  
**Received:** {received_date}

## Content

{email_data['snippet']}

## Suggested Actions

- [ ] Read full email content
- [ ] Draft reply if needed
- [ ] Create approval request for sensitive actions
- [ ] Move to /Done when complete

## Notes

*Add your analysis and response draft here...*

---
*Created by GmailWatcher*
'''
        
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f'Created action file: {filename}')
        
        # Create approval file automatically if auto_approve is enabled
        if self.auto_approve:
            self._create_approval_file(email_data, filepath)
        
        return filepath
    
    def _create_approval_file(self, email_data: dict, action_file: Path):
        """Create an approval request file automatically for emails needing reply."""
        from datetime import datetime
        
        # Determine if email needs reply (simple heuristic: not from automated systems)
        from_address = email_data.get('from', '').lower()
        subject = email_data.get('subject', '').lower()
        
        # Skip automated systems (LinkedIn, Google, ChatGPT, etc.)
        automated_senders = ['linkedin', 'google', 'noreply', 'no-reply', 'chatgpt', 'openai', 'github', 'microsoft']
        if any(sender in from_address for sender in automated_senders):
            self.logger.info(f'  Skipping approval for automated sender: {from_address}')
            return
        
        # Create approval file for personal/business emails
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_subject = "".join(c for c in email_data['subject'] if c.isalnum() or c in ' -_')[:30]
        approval_filename = f"APPROVAL_email_reply_{safe_subject}_{timestamp}.md"
        
        pending_approval = self.vault_path / 'Pending_Approval'
        pending_approval.mkdir(parents=True, exist_ok=True)
        
        approval_content = f'''---
type: approval_request
action: email_send
to: {email_data['from']}
from: {email_data['to']}
subject: Re: {email_data['subject']}
created: {datetime.now().isoformat()}
expires: {(datetime.now()).isoformat()}
status: pending
priority: medium
original_email: {action_file.name}
---

# Approval Required: Email Reply

## Email Details

**Action:** Send Email Reply  
**To:** {email_data['from']}  
**From:** {email_data['to']}  
**Subject:** Re: {email_data['subject']}  
**Original Email:** {action_file.name}

---

## Draft Reply

```
Dear Sender,

Thank you for your email. This is an automated acknowledgment that your message has been received.

A member of our team will review your message and respond shortly.

Best regards,
AI Employee Assistant
```

---

## Reply Analysis

**Why reply is needed:**
- ✅ Personal email (not automated system)
- ✅ Requires acknowledgment
- ✅ Professional courtesy

**Company Handbook Compliance:**
- ✅ Polite and professional tone
- ✅ No sensitive information shared
- ✅ Appropriate for approval workflow

---

## To Approve

Move this file to `/Approved/` folder:

```powershell
move Pending_Approval\\{approval_filename} Approved\\
```

The orchestrator will send the email automatically.

## To Reject

Move this file to `/Rejected/` folder with a reason.

---

*Created automatically by GmailWatcher - Silver Tier*
*Human-in-the-Loop Approval Required*
'''
        
        approval_filepath = pending_approval / approval_filename
        approval_filepath.write_text(approval_content, encoding='utf-8')
        self.logger.info(f'  ✅ Created approval file: {approval_filename}')
    
    def show_account_info(self):
        """Show information about the authenticated Gmail account."""
        print('[INFO] Checking authenticated Gmail account...')
        
        if not self.service:
            if not self._connect():
                print('[ERROR] Could not connect to Gmail API')
                print('Run: python gmail_watcher.py --authenticate')
                return False
        
        try:
            # Get profile information
            profile = self.service.users().getProfile(userId='me').execute()
            
            print(f'\n[OK] Authenticated Gmail Account:')
            print(f'  Email: {profile.get("emailAddress", "Unknown")}')
            print(f'  Name: {profile.get("displayName", "Unknown")}')
            print(f'  Total emails: {profile.get("messagesTotal", "Unknown"):,}')
            print(f'  Total threads: {profile.get("threadsTotal", "Unknown"):,}')
            
            # Count unread emails
            unread_result = self.service.users().messages().list(
                userId='me', q='is:unread', maxResults=1
            ).execute()
            unread_count = int(unread_result.get('resultSizeEstimate', 0))
            
            print(f'  Unread emails: {unread_count:,}')
            
            return True
            
        except Exception as e:
            print(f'[ERROR] Could not get account info: {e}')
            return False
    
    def clear_cache(self):
        """Clear the processed email cache (useful for testing)."""
        cache_file = self.vault_path / 'Logs' / '.gmail_cache.pkl'
        if cache_file.exists():
            cache_file.unlink()
            print('[OK] Gmail cache cleared')
            print('[INFO] Next run will re-process all emails')
            self.processed_ids = set()
        else:
            print('[INFO] No cache to clear')


def main():
    """Entry point for the Gmail watcher."""
    import argparse

    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument('vault_path', nargs='?', default='.',
                       help='Path to Obsidian vault')
    parser.add_argument('--authenticate', action='store_true',
                       help='Run authentication flow')
    parser.add_argument('--show-account', action='store_true',
                       help='Show authenticated Gmail account info')
    parser.add_argument('--clear-cache', action='store_true',
                       help='Clear processed email cache (for testing)')
    parser.add_argument('--all-unread', action='store_true',
                       help='Check ALL unread emails (not just important)')
    parser.add_argument('--debug', action='store_true',
                       help='Show debug information about emails')
    parser.add_argument('--interval', type=int, default=120,
                       help='Check interval in seconds')
    parser.add_argument('--keywords', type=str, default='',
                       help='Comma-separated keywords to filter')

    args = parser.parse_args()

    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f'[ERROR] Vault path does not exist: {vault_path}')
        sys.exit(1)

    # Parse keywords
    keywords = [k.strip() for k in args.keywords.split(',') if k.strip()] if args.keywords else None

    # Create watcher
    watcher = GmailWatcher(
        str(vault_path),
        check_interval=args.interval,
        keywords=keywords,
        all_unread=args.all_unread,
        debug=args.debug
    )

    # Run different modes
    if args.authenticate:
        watcher._authenticate()
    elif args.show_account:
        success = watcher.show_account_info()
        sys.exit(0 if success else 1)
    elif args.clear_cache:
        watcher.clear_cache()
    else:
        # Run the watcher
        print('[INFO] Starting Gmail Watcher...')
        print(f'[INFO] Mode: {"All unread" if args.all_unread else "Unread + Important"} emails')
        if args.keywords:
            print(f'[INFO] Keywords: {args.keywords}')
        print(f'[INFO] Check interval: {args.interval}s')
        print('[INFO] Press Ctrl+C to stop')
        watcher.run()


if __name__ == '__main__':
    main()
