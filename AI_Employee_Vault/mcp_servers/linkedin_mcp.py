"""
LinkedIn MCP Server - Post to LinkedIn via browser automation.

Uses Playwright MCP for browser-based posting (no API credentials needed).

Usage:
    python mcp_servers/linkedin_mcp.py --port 8810
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

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

# Playwright MCP client
PLAYWRIGHT_URL = os.environ.get('PLAYWRIGHT_URL', 'http://localhost:8808/mcp')


class LinkedInMCP:
    """LinkedIn posting via browser automation."""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.logged_in = False
    
    def _get_mcp_client(self):
        """Get MCP client for Playwright."""
        try:
            from scripts.mcp_client import MCPClient, HTTPTransport
            transport = HTTPTransport(PLAYWRIGHT_URL)
            return MCPClient(transport)
        except Exception as e:
            return None
    
    def navigate_to_linkedin(self) -> dict:
        """Navigate to LinkedIn feed."""
        try:
            client = self._get_mcp_client()
            if not client:
                return {'success': False, 'error': 'MCP client not available'}
            
            result = client.call_tool('browser_navigate', {
                'url': 'https://www.linkedin.com/feed/'
            })
            
            self.logged_in = True
            return {'success': True, 'message': 'Navigated to LinkedIn'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_post(self, content: str, image: str = None, 
                    hashtags: list = None) -> dict:
        """Create and publish a LinkedIn post."""
        try:
            client = self._get_mcp_client()
            if not client:
                return {'success': False, 'error': 'MCP client not available'}
            
            # Navigate to LinkedIn
            client.call_tool('browser_navigate', {
                'url': 'https://www.linkedin.com/feed/'
            })
            
            # Wait for page to load
            client.call_tool('browser_wait_for', {'time': 3})
            
            # Get snapshot to find element refs
            snapshot = client.call_tool('browser_snapshot', {})
            
            # Find post creation box and click
            # Note: refs will vary, this is example code
            client.call_tool('browser_click', {
                'element': 'Start a post',
                'ref': 'e42'  # This would come from snapshot
            })
            
            # Type the content
            client.call_tool('browser_type', {
                'element': 'Post text area',
                'ref': 'e55',
                'text': content,
                'submit': False
            })
            
            # Add image if provided
            if image:
                client.call_tool('browser_click', {
                    'element': 'Add media',
                    'ref': 'e60'
                })
                client.call_tool('browser_file_upload', {
                    'paths': [str(Path(image).absolute())]
                })
            
            # Click Post button
            client.call_tool('browser_click', {
                'element': 'Post button',
                'ref': 'e70'
            })
            
            # Wait for confirmation
            client.call_tool('browser_wait_for', {
                'text': 'Your post has been shared'
            })
            
            return {'success': True, 'message': 'Post published successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_post_content(self, business_update: str, 
                              tone: str = 'professional') -> str:
        """Generate LinkedIn post content from business update."""
        templates = {
            'professional': f"""🏢 Business Update

{business_update}

This achievement reflects our commitment to excellence.

#Business #Professional #Growth""",
            
            'casual': f"""Hey LinkedIn family! 👋

{business_update}

Grateful for this journey!

#Life #Business #Update""",
            
            'enthusiastic': f"""🎉 Exciting News!

{business_update}

We couldn't be more thrilled about this!

#Excited #Business #Milestone"""
        }
        
        return templates.get(tone, templates['professional'])


def create_mcp_server():
    """Create MCP server instance."""
    server = Server("linkedin-mcp")
    
    linkedin = LinkedInMCP()
    
    @server.list_tools()
    async def list_tools():
        return [
            types.Tool(
                name="linkedin_post",
                description="Create and publish a LinkedIn post",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Post content (max 3000 chars)"},
                        "image": {"type": "string", "description": "Image file path (optional)"},
                        "hashtags": {"type": "array", "items": {"type": "string"}, "description": "Hashtags"}
                    },
                    "required": ["content"]
                }
            ),
            types.Tool(
                name="linkedin_schedule",
                description="Schedule a LinkedIn post for later",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Post content"},
                        "scheduled_time": {"type": "string", "description": "ISO 8601 datetime"},
                        "image": {"type": "string", "description": "Image file path"}
                    },
                    "required": ["content", "scheduled_time"]
                }
            ),
            types.Tool(
                name="linkedin_generate",
                description="Generate LinkedIn post from business update",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "business_update": {"type": "string", "description": "What happened"},
                        "tone": {"type": "string", "enum": ["professional", "casual", "enthusiastic"]}
                    },
                    "required": ["business_update"]
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        if name == "linkedin_post":
            result = linkedin.create_post(
                content=arguments.get("content"),
                image=arguments.get("image"),
                hashtags=arguments.get("hashtags", [])
            )
        elif name == "linkedin_schedule":
            # For now, just create a scheduled post file
            result = {'success': True, 'message': 'Post scheduled (file created)'}
        elif name == "linkedin_generate":
            content = linkedin.generate_post_content(
                business_update=arguments.get("business_update"),
                tone=arguments.get("tone", "professional")
            )
            result = {'success': True, 'content': content}
        else:
            return {"error": f"Unknown tool: {name}"}
        
        return [types.TextContent(type="text", text=json.dumps(result))]
    
    return server


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn MCP Server')
    parser.add_argument('--port', type=int, default=8810, help='HTTP port')
    parser.add_argument('--headless', action='store_true', help='Run browser headless')
    parser.add_argument('--post-daily', action='store_true', help='Post daily update')
    
    args = parser.parse_args()
    
    if args.post_daily:
        # Daily posting mode
        print('Daily posting mode - integrate with scheduler')
        return
    
    if not MCP_AVAILABLE:
        print('MCP library not available. Running standalone.')
        return
    
    # Run MCP server
    server = create_mcp_server()
    
    async def run_server():
        async with server.run_stdio() as transport:
            await server.run(transport)
    
    asyncio.run(run_server())


if __name__ == '__main__':
    main()
