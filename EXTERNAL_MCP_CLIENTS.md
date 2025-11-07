# 🔌 External MCP Client Integration Guide

## ✅ Async Operations Confirmed

**YES, everything is fully async:**
- ✅ Voice journal saving: `asyncio.create_task()` - non-blocking
- ✅ Agent analysis: Fully async ADK agents with parallel execution
- ✅ MCP server tools: All `async def` functions
- ✅ Firestore operations: Async-compatible (Firestore SDK is async-ready)
- ✅ Real-time sync: Automatic via Firestore listeners

---

## 🎯 Using MCP Server with External Clients

### Supported Clients:
- ✅ **Cursor** (has MCP server support)
- ✅ **Claude Desktop** (has MCP server support)
- ✅ **Claude Code** (has MCP server support)
- ✅ Any MCP-compatible client

---

## 🔐 Authentication Flow

### **Step 1: Login**

When connecting via external client (Cursor, Claude, etc.), use the login tool:

```json
{
  "name": "mcp_login",
  "arguments": {
    "username": "your_username_or_email",
    "password": "your_password"
  }
}
```

**Response:**
```json
{
  "success": true,
  "user_id": "uuid-here",
  "username": "your_username",
  "email": "your@email.com",
  "session_token": "optional-token",
  "message": "Login successful. Use user_id for all tool calls.",
  "database": "firestore"
}
```

### **Step 2: Use Tools with user_id**

After login, use `user_id` in all tool calls:

```json
{
  "name": "eisenhower_get_tasks",
  "arguments": {
    "userId": "uuid-from-login"
  }
}
```

```json
{
  "name": "save_complete_wellness_analysis",
  "arguments": {
    "userId": "uuid-from-login",
    "session_id": "...",
    "mode": "wellness",
    "transcript_summary": {...},
    "stats_recommendations": {...},
    "safety_approved": true,
    "safety_score": 0.95
  }
}
```

---

## ⚡ Real-Time Sync Guaranteed!

**All data operations use Firebase Firestore:**
- ✅ `save_complete_wellness_analysis` → Saves to Firestore
- ✅ `eisenhower_save_tasks` → Saves to Firestore
- ✅ `daily_data_save` → Saves to Firestore
- ✅ All wellness tools → Save to Firestore

**Result:**
- Changes appear instantly across:
  - Your main app frontend
  - Cursor/Claude when they query data
  - Any other client connected to the same Firestore

---

## 📋 Setup for External Clients

### **For Cursor:**

1. **Configure MCP Server:**
   ```json
   // .cursor/mcp.json or Cursor settings
   {
     "mcpServers": {
       "wellness-mcp": {
         "command": "python",
         "args": [
           "/path/to/backend_working_voiceagent/google-hackathon-backend-5b3907c4ed9eb19dbaa08b898a42a4ee1ea5e5fe/agents/mcp_server/src/main.py"
         ],
         "env": {
           "SERVICE_ACCOUNT_KEY_PATH": "/path/to/firebase-service-account.json",
           "FIREBASE_PROJECT_ID": "your-project-id"
         }
       }
     }
   }
   ```

2. **First Use:**
   - Ask Cursor: "Use the mcp_login tool with my username and password"
   - Cursor will call the tool and get your user_id
   - Then use any other tool with that user_id

### **For Claude Desktop:**

1. **Configure in `claude_desktop_config.json`:**
   ```json
   {
     "mcpServers": {
       "wellness-mcp": {
         "command": "python",
         "args": [
           "/path/to/agents/mcp_server/src/main.py"
         ],
         "env": {
           "SERVICE_ACCOUNT_KEY_PATH": "/path/to/firebase-service-account.json"
         }
       }
     }
   }
   ```

2. **Usage:**
   - Ask Claude: "Login to wellness MCP server with username X and password Y"
   - Claude gets user_id
   - Then: "Get my Eisenhower tasks" (Claude uses user_id automatically)

---

## 🔄 Complete Async Flow Example

### **Scenario: Using Cursor to analyze a voice journal**

1. **Login (one-time):**
   ```
   Cursor → mcp_login("my_username", "my_password")
          → Returns: { user_id: "abc-123" }
   ```

2. **Create analysis:**
   ```
   Cursor → save_complete_wellness_analysis(
             userId="abc-123",
             session_id="session-456",
             mode="wellness",
             transcript_summary={...},
             stats_recommendations={...},
             safety_approved=true,
             safety_score=0.95
           )
   ```

3. **Real-time sync happens automatically:**
   ```
   Firestore saves:
   - voiceJournalSessions/session-456 → updated
   - agentRecommendedTasks/{id} → created
   - wellnessPathways/{id} → created
   
   Your frontend sees changes instantly! 🎉
   Cursor sees the data immediately! 🎉
   Any other client sees it too! 🎉
   ```

4. **Query tasks:**
   ```
   Cursor → eisenhower_get_tasks(userId="abc-123")
          → Returns all tasks (including newly saved ones!)
   ```

---

## 🛡️ Security Notes

1. **Password Storage:**
   - Passwords are hashed (using same backend password hashing)
   - Never stored in plain text
   - Verification uses secure password hash comparison

2. **Session Tokens:**
   - Optional session tokens can be generated
   - Can be used as API keys for future calls
   - Stored in memory (cleared on server restart)

3. **User ID Validation:**
   - All tools validate user_id exists
   - Firestore rules can add additional security
   - Backend JWT still required for main app API

---

## ✅ Verification Checklist

- [ ] MCP server runs: `python agents/mcp_server/src/main.py`
- [ ] Firebase initialized: Check logs for "✅ Firebase initialized"
- [ ] Login works: Test `mcp_login` with valid credentials
- [ ] Tools work: Test `eisenhower_get_tasks` with returned user_id
- [ ] Real-time sync: Save data via tool, check Firestore console
- [ ] External client connected: Cursor/Claude can see all tools

---

## 🚀 Benefits

1. **Unified Data:** Everything in Firestore, no database split
2. **Real-Time Sync:** Changes appear everywhere instantly
3. **Multi-Client Support:** Use with your app, Cursor, Claude simultaneously
4. **Async Everything:** No blocking operations, fast responses
5. **Secure Auth:** Username/password with proper hashing

---

**Everything works async and with real-time sync!** 🎉
