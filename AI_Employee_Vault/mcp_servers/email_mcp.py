"""
Email MCP Server - Send emails via Gmail API.

Provides MCP tools for:
- email_send: Send an email immediately
- email_draft: Create a draft email
- email_reply: Reply to an existing email

Usage:
    python mcp_servers/email_mcp.py --port 8809
"""

import sys
import os
import json
import pickle
import base64
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

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
    # Don't exit - might not need Google APIs if just listing tools

# MCP Server imports
try:
    from mcp.server.models import InitializationOptions
    import mcp.types as types
    from mcp.server import Server
    import asyncio
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: MCP library not installed.")
    print("Run: pip install mcp")


class EmailMCP:
    """Email MCP Server implementation."""

    # Correct Gmail API scopes (using dots, not slashes)
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self, credentials_path: str = None, token_path: str = None,
                 dry_run: bool = False):
        self.credentials_path = Path(credentials_path) if credentials_path else None
        self.token_path = Path(token_path) if token_path else None
        self.dry_run = dry_run

        # Auto-detect paths
        if not self.credentials_path:
            # Look for credentials.json in project root (3 levels up from mcp_servers/)
            self.credentials_path = Path(__file__).parent.parent.parent.parent / 'credentials.json'
        if not self.token_path:
            # Token in same directory as email_mcp.py or vault root
            self.token_path = Path(__file__).parent / 'token.json'
        if not self.token_path.exists():
            self.token_path = Path(__file__).parent.parent / 'token.json'

        self.service = None
        self._connect()
    
    def _get_credentials(self):
        """Get valid Gmail API credentials."""
        creds = None

        if self.token_path.exists():
            try:
                with open(self.token_path, 'r') as f:
                    token_data = json.loads(f.read())
                creds = Credentials.from_authorized_user_info(token_data, self.SCOPES)
            except Exception as e:
                print(f'Could not load token: {e}')

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    from google.auth.transport.requests import Request
                    creds.refresh(Request())
                except Exception as e:
                    print(f'Could not refresh token: {e}')
                    creds = None
            else:
                if creds and creds.expired:
                    print('Token expired. Please re-authenticate.')

        return creds
    
    def _connect(self):
        """Connect to Gmail API."""
        creds = self._get_credentials()
        if not creds:
            print('No valid credentials. Run with --authenticate first.')
            return False
        
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            print('Connected to Gmail API')
            return True
        except Exception as e:
            print(f'Could not connect to Gmail API: {e}')
            return False
    
    def _create_message(self, to: str, subject: str, body: str, 
                        html: str = None, attachment: str = None):
        """Create email message."""
        if html:
            message = MIMEMultipart('alternative')
            message.attach(MIMEText(body, 'plain'))
            message.attach(MIMEText(html, 'html'))
        else:
            message = MIMEText(body)
        
        message['to'] = to
        message['subject'] = subject
        
        # Add attachment
        if attachment:
            try:
                with open(attachment, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={Path(attachment).name}'
                )
                message.attach(part)
            except Exception as e:
                raise ValueError(f'Could not attach file: {e}')
        
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    
    def send_email(self, to: str, subject: str, body: str, 
                   html: str = None, attachment: str = None) -> dict:
        """Send an email."""
        if self.dry_run:
            return {
                'success': True,
                'dry_run': True,
                'message': f'Would send email to {to} with subject: {subject}'
            }
        
        try:
            message = self._create_message(to, subject, body, html, attachment)
            sent = self.service.users().messages().send(
                userId='me', body=message).execute()
            
            return {
                'success': True,
                'message_id': sent['id'],
                'thread_id': sent['threadId']
            }
        except HttpError as error:
            return {
                'success': False,
                'error': f'Gmail API error: {error}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_draft(self, to: str, subject: str, body: str,
                     cc: str = None, bcc: str = None, html: str = None) -> dict:
        """Create a draft email."""
        if self.dry_run:
            return {
                'success': True,
                'dry_run': True,
                'message': f'Would create draft to {to}'
            }
        
        try:
            message = self._create_message(to, subject, body, html)
            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc
            
            draft = self.service.users().drafts().create(
                userId='me', body={'message': message}).execute()
            
            return {
                'success': True,
                'draft_id': draft['id'],
                'message_id': draft['message']['id']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def reply_to_email(self, thread_id: str, body: str, 
                       include_original: bool = True) -> dict:
        """Reply to an email."""
        if self.dry_run:
            return {
                'success': True,
                'dry_run': True,
                'message': f'Would reply to thread {thread_id}'
            }
        
        try:
            # Get original message
            original = self.service.users().messages().get(
                userId='me', threadId=thread_id).execute()
            
            # Extract original subject and sender
            headers = {h['name']: h['value'] 
                      for h in original['payload']['headers']}
            original_subject = headers.get('Subject', 'Re:')
            original_from = headers.get('From', '')
            
            # Create reply subject
            if not original_subject.startswith('Re:'):
                subject = f'Re: {original_subject}'
            else:
                subject = original_subject
            
            # Create reply body
            if include_original:
                full_body = f'{body}\n\n--- Original Message ---\n'
            else:
                full_body = body
            
            message = self._create_message(
                to=original_from,
                subject=subject,
                body=full_body
            )
            message['In-Reply-To'] = original['id']
            message['References'] = original['id']
            
            sent = self.service.users().messages().send(
                userId='me', body=message).execute()
            
            return {
                'success': True,
                'message_id': sent['id'],
                'thread_id': sent['threadId']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def create_mcp_server():
    """Create MCP server instance."""
    server = Server("email-mcp")
    
    # Get vault path from environment or default
    vault_path = Path(os.environ.get('VAULT_PATH', '.'))
    credentials_path = vault_path / 'credentials.json'
    token_path = vault_path / 'token.json'
    dry_run = os.environ.get('DRY_RUN', 'false').lower() == 'true'
    
    email_mcp = EmailMCP(
        credentials_path=str(credentials_path),
        token_path=str(token_path),
        dry_run=dry_run
    )
    
    @server.list_tools()
    async def list_tools():
        return [
            types.Tool(
                name="email_send",
                description="Send an email via Gmail",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email address"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body text"},
                        "html": {"type": "string", "description": "HTML body (optional)"},
                        "attachment": {"type": "string", "description": "File path to attach (optional)"}
                    },
                    "required": ["to", "subject", "body"]
                }
            ),
            types.Tool(
                name="email_draft",
                description="Create a draft email",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email"},
                        "cc": {"type": "string", "description": "CC recipient"},
                        "bcc": {"type": "string", "description": "BCC recipient"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body"},
                        "html": {"type": "string", "description": "HTML body"}
                    },
                    "required": ["to", "subject", "body"]
                }
            ),
            types.Tool(
                name="email_reply",
                description="Reply to an existing email",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "thread_id": {"type": "string", "description": "Gmail thread ID"},
                        "body": {"type": "string", "description": "Reply body"},
                        "include_original": {"type": "boolean", "description": "Include original email"}
                    },
                    "required": ["thread_id", "body"]
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        if name == "email_send":
            result = email_mcp.send_email(
                to=arguments.get("to"),
                subject=arguments.get("subject"),
                body=arguments.get("body"),
                html=arguments.get("html"),
                attachment=arguments.get("attachment")
            )
        elif name == "email_draft":
            result = email_mcp.create_draft(
                to=arguments.get("to"),
                cc=arguments.get("cc"),
                bcc=arguments.get("bcc"),
                subject=arguments.get("subject"),
                body=arguments.get("body"),
                html=arguments.get("html")
            )
        elif name == "email_reply":
            result = email_mcp.reply_to_email(
                thread_id=arguments.get("thread_id"),
                body=arguments.get("body"),
                include_original=arguments.get("include_original", True)
            )
        else:
            return {"error": f"Unknown tool: {name}"}
        
        return [types.TextContent(type="text", text=json.dumps(result))]
    
    return server


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Email MCP Server')
    parser.add_argument('--port', type=int, default=8809, help='HTTP port')
    parser.add_argument('--authenticate', action='store_true', help='Run auth flow')
    parser.add_argument('--dry-run', action='store_true', help='Don\'t send real emails')
    
    args = parser.parse_args()
    
    if args.authenticate:
        # Run authentication
        from google_auth_oauthlib.flow import InstalledAppFlow
        
        # Look for credentials.json in project root (parent of AI_Employee_Vault)
        vault_root = Path(__file__).parent.parent  # AI_Employee_Vault directory
        credentials_path = vault_root.parent / 'credentials.json'  # Project root
        
        if not credentials_path.exists():
            print(f'credentials.json not found at: {credentials_path}')
            print('Download from Google Cloud Console.')
            sys.exit(1)

        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path), EmailMCP.SCOPES)
        
        # Try different ports if 8080 is busy
        for port in [8080, 8081, 8082, 8083, 8084, 8085]:
            try:
                print(f'[INFO] Attempting authentication on port {port}...')
                creds = flow.run_local_server(port=port, prompt='consent')
                print(f'[OK] Authentication successful on port {port}!')
                break
            except OSError as e:
                if 'address' in str(e).lower():
                    print(f'[WARN] Port {port} is busy, trying next port...')
                    continue
                else:
                    raise
        
        # Save token in vault directory
        token_path = Path(__file__).parent / 'token.json'
        with open(token_path, 'w') as f:
            f.write(creds.to_json())

        print(f'✓ Token saved to {token_path}')
        print('[NEXT] Run: python mcp_servers\\email_mcp.py --port 8809')
        return
    
    if not MCP_AVAILABLE:
        print('MCP library not available. Running in standalone mode.')
        print('Use: python -c "from mcp_servers.email_mcp import EmailMCP; mcp = EmailMCP()"')
        return

    # Run MCP server
    server = create_mcp_server()
    
    print('Email MCP Server starting on stdio...')
    print('Press Ctrl+C to stop')
    
    # Run the server with stdio transport
    async def run_server():
        async with server.run_stdio() as transport:
            await server.run(transport)
    
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print('\nEmail MCP Server stopped')
    except Exception as e:
        print(f'Server error: {e}')
        print('\nNote: MCP server is designed to be called by a client, not run directly.')
        print('The Gmail Watcher and Orchestrator will use this server automatically.')


if __name__ == '__main__':
    main()
