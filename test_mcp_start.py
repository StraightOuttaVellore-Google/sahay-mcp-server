#!/usr/bin/env python3
"""
Test MCP Server Startup

Quick test to verify the MCP server can start properly.
"""

import subprocess
import sys
import time
from pathlib import Path

# Get MCP server path
mcp_server_path = Path(__file__).parent / "run_server.py"

print("🧪 Testing MCP Server Startup")
print(f"📁 Server path: {mcp_server_path}")
print("=" * 60)

# Try to start the server as a subprocess
print("\n[1] Starting MCP server subprocess...")
try:
    # Start server with timeout
    process = subprocess.Popen(
        [sys.executable, str(mcp_server_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print(f"✅ Process started (PID: {process.pid})")
    
    # Wait a bit for it to initialize
    print("[2] Waiting 3 seconds for initialization...")
    time.sleep(3)
    
    # Check if process is still running
    poll_result = process.poll()
    
    if poll_result is None:
        print("✅ Server is running!")
        print("\n[3] Terminating test server...")
        process.terminate()
        process.wait(timeout=5)
        print("✅ Server terminated cleanly")
        
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! MCP Server can start properly!")
        print("=" * 60)
        
    else:
        print(f"❌ Server terminated unexpectedly (exit code: {poll_result})")
        print("\nStdout:")
        print(process.stdout.read())
        print("\nStderr:")
        print(process.stderr.read())
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

