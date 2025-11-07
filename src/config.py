"""
MCP Server Configuration

Loads environment variables from the ROOT backend .env file.
Environment variables are inherited from the parent process (main FastAPI app).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend root (3 levels up from this file)
# This file: agents/mcp_server/src/config.py
# Backend root: ../../../
backend_root = Path(__file__).parent.parent.parent.parent
env_path = backend_root / '.env'

# Load environment from root .env if it exists
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded .env from: {env_path}")
else:
    # Environment variables will be inherited from parent process
    print(f"ℹ️  No .env file at {env_path}, using inherited environment variables")

class Config:
    """
    MCP Server Configuration
    
    Environment variables are either:
    1. Loaded from root backend .env file, OR
    2. Inherited from parent process (FastAPI app) when run as subprocess
    """
    
    # Firebase Configuration
    SERVICE_ACCOUNT_KEY_PATH = os.getenv('SERVICE_ACCOUNT_KEY_PATH', '')
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', '')
    
    # Server Metadata
    SERVER_NAME = "study-mcp-server"
    SERVER_VERSION = "1.0.0"
    
    # Debugging: Print loaded config
    def __init__(self):
        print(f"🔧 MCP Server Config:")
        print(f"   SERVICE_ACCOUNT_KEY_PATH: {'SET' if self.SERVICE_ACCOUNT_KEY_PATH else 'NOT SET'}")
        print(f"   FIREBASE_PROJECT_ID: {self.FIREBASE_PROJECT_ID or 'NOT SET (will auto-detect)'}")

config = Config()
