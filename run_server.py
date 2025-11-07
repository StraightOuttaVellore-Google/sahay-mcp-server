#!/usr/bin/env python3
"""
MCP Server Wrapper - Properly starts the MCP server with correct imports

This wrapper ensures the MCP server can be run directly without import issues.
"""

import sys
from pathlib import Path

# Add parent directory to path so imports work
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))

# Now import and run the server
from src.main import mcp

if __name__ == "__main__":
    print("🚀 Starting MCP Server...")
    print(f"📁 Server directory: {server_dir}")
    mcp.run()

