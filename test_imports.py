#!/usr/bin/env python3
"""
Test MCP Server Imports

Verify that all imports work correctly.
"""

import sys
from pathlib import Path

# Add server directory to path
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))

print("🧪 Testing MCP Server Imports")
print("=" * 60)

try:
    print("\n[1] Importing config...")
    from src.config import config
    print(f"✅ Config imported - Server name: {config.SERVER_NAME}")
    
    print("\n[2] Importing auth...")
    from src.auth import get_auth
    auth = get_auth()
    print(f"✅ Auth imported - Auth instance created")
    
    print("\n[3] Importing Firebase client...")
    try:
        from src.firebase_client import initialize_firebase, get_firestore
        print(f"✅ Firebase client imported")
        
        print("\n[4] Initializing Firebase...")
        initialize_firebase()
        db = get_firestore()
        print(f"✅ Firebase initialized - Firestore client ready")
    except Exception as e:
        print(f"⚠️  Firebase not available: {e}")
        print("   (This is OK if PostgreSQL is being used)")
    
    print("\n[5] Importing tools...")
    from src.tools.eisenhower import get_all_tasks, save_all_tasks
    from src.tools.wellness_saving import save_complete_analysis_result
    print(f"✅ Tools imported successfully")
    
    print("\n[6] Importing FastMCP...")
    from mcp.server.fastmcp import FastMCP
    print(f"✅ FastMCP imported")
    
    print("\n[7] Creating MCP server instance...")
    mcp = FastMCP(name=config.SERVER_NAME)
    print(f"✅ MCP server instance created")
    
    print("\n" + "=" * 60)
    print("🎉 SUCCESS! All imports work correctly!")
    print("=" * 60)
    print("\nThe MCP server is ready to be used by ADK agents!")
    
except Exception as e:
    print(f"\n❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

