"""
Authentication Module for MCP Server

SUPPORTS THREE USE CASES:
=========================

1. PRIMARY USE CASE (Your App):
   ------------------------------
   Backend (JWT authenticated) → ADK Agents → MCP Server
   
   Flow:
   - User logs in with email/password → Gets JWT token
   - JWT validates user on all API calls
   - Backend extracts user_id from JWT
   - Agent analysis receives user_id from authenticated context
   - MCP server tools receive user_id from agent
   - MCP server TRUSTS user_id (already authenticated by backend)
   
   NO ADDITIONAL AUTH NEEDED - Backend JWT handles everything!

2. EXTERNAL MCP CLIENTS (Cursor, Claude Code, etc.):
   ---------------------------------------------------
   External LLM client → MCP Server (username/password login)
   
   Flow:
   - User calls mcp_login(username, password) tool
   - MCP server validates credentials against Firebase/PostgreSQL
   - Returns user_id (or session_token)
   - Subsequent tool calls use user_id directly
   - All data saved to Firestore (real-time sync enabled!)
   
3. API KEY MODE (Optional):
   -------------------------
   External client with pre-generated API key
   
   Usage:
       from .auth import get_auth
       
       auth = get_auth()
       if auth.validate_user_access(user_id):  # No api_key needed!
           # Proceed with operation
           pass
"""

import os
from typing import Optional, Dict
from dotenv import load_dotenv
import logging
import secrets
import sys
from pathlib import Path

load_dotenv()

logger = logging.getLogger(__name__)

# Import backend utilities for password verification
# Path calculation: auth.py is in mcp_server/src/
# Backend root is 4 parents up: ../../../
backend_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

try:
    from utils import verify_password, hash_password
    from firebase_db import get_firestore
    BACKEND_UTILS_AVAILABLE = True
    logger.info("Backend utils imported successfully - full auth functionality available")
except ImportError as e:
    # If backend utils not available, define minimal versions
    BACKEND_UTILS_AVAILABLE = False
    logger.warning(f"Backend utils not available - limited auth functionality: {e}")
    
    def verify_password(password: str, hashed: str) -> bool:
        """Fallback password verification"""
        try:
            from pwdlib import PasswordHash
            password_hash = PasswordHash.recommended()
            return password_hash.verify(password, hashed)
        except:
            return False


class MCPAuth:
    """
    Authentication handler for MCP server tools.
    
    PRIMARY MODE: Trust user_id from backend (already JWT authenticated)
    OPTIONAL MODE: API key for external LLM access
    """
    
    def __init__(self):
        """Initialize auth system"""
        # OPTIONAL: Admin API key for external LLM access (not required for main app)
        self.admin_api_key = os.getenv("MCP_ADMIN_API_KEY", "")
        
        # OPTIONAL: User-specific API keys (for external LLM access)
        self.api_key_to_user: Dict[str, str] = {}
        
        # Only load user API keys if admin key is set
        if self.admin_api_key:
            self._load_user_api_keys()
            logger.info("MCP Auth: External LLM access enabled (API key mode)")
        else:
            logger.info("MCP Auth: Backend-only mode (no external LLM access)")
    
    def _load_user_api_keys(self):
        """Load user API keys from environment variables (OPTIONAL)"""
        # Format: MCP_USER_API_KEY_<user_id>=<api_key>
        # Only needed if you want external LLM access
        
        for key, value in os.environ.items():
            if key.startswith("MCP_USER_API_KEY_"):
                user_id = key.replace("MCP_USER_API_KEY_", "").replace("_", "-")
                self.api_key_to_user[value] = user_id
                logger.info(f"Loaded API key for user: {user_id[:8]}...")
    
    def validate_user_access(
        self, 
        user_id: str, 
        api_key: Optional[str] = None
    ) -> bool:
        """
        Validate access to user_id data.
        
        PRIMARY FLOW (Your App):
        -------------------------
        - Backend authenticates user via JWT (email/password login)
        - Backend passes user_id to agents
        - Agents pass user_id to MCP server
        - MCP server TRUSTS user_id (no api_key needed)
        
        OPTIONAL FLOW (External LLMs):
        -------------------------------
        - External LLM (Claude, etc.) provides api_key
        - MCP server validates api_key → user_id mapping
        
        Args:
            user_id: User ID from backend (already JWT authenticated)
            api_key: Optional API key (only for external LLM use)
        
        Returns:
            bool: True if access granted
        """
        if not user_id:
            logger.warning("Empty user_id provided")
            return False
        
        # PRIMARY MODE: Trust backend authentication
        if api_key is None:
            # Backend has already authenticated via JWT
            # user_id comes from authenticated context
            logger.debug(f"✅ Backend-authenticated access: {user_id[:8]}...")
            return True
        
        # OPTIONAL MODE: External LLM with API key
        return self.validate_api_key(api_key, user_id)
    
    def validate_api_key(self, api_key: str, user_id: str) -> bool:
        """
        OPTIONAL: Validate API key for external LLM access.
        
        Only used if you want to use MCP server with Claude Desktop, etc.
        NOT needed for your main application (backend handles auth via JWT).
        
        Args:
            api_key: API key from external LLM
            user_id: User ID being accessed
        
        Returns:
            bool: True if API key is valid
        """
        if not api_key:
            logger.warning("Empty API key provided")
            return False
        
        # Admin API key has access to all users
        if api_key == self.admin_api_key and self.admin_api_key:
            logger.info(f"✅ Admin API key validated: {user_id[:8]}...")
            return True
        
        # User-specific API key
        mapped_user_id = self.api_key_to_user.get(api_key)
        if mapped_user_id == user_id:
            logger.info(f"✅ User API key validated: {user_id[:8]}...")
            return True
        
        logger.warning(f"❌ Invalid API key for user: {user_id[:8]}...")
        return False
    
    # =======================================================================
    # OPTIONAL METHODS: Only for external LLM access (not required for app)
    # =======================================================================
    
    def register_user_api_key(self, user_id: str, api_key: Optional[str] = None) -> str:
        """
        OPTIONAL: Generate API key for external LLM access.
        
        Use this if you want users to access MCP server via Claude Desktop.
        NOT needed for your main app (backend JWT handles auth).
        """
        if not api_key:
            api_key = f"sk_mcp_{secrets.token_urlsafe(32)}"
        
        self.api_key_to_user[api_key] = user_id
        logger.info(f"API key registered for user: {user_id[:8]}...")
        
        return api_key
    
    def revoke_api_key(self, api_key: str) -> bool:
        """OPTIONAL: Revoke an API key."""
        if api_key in self.api_key_to_user:
            user_id = self.api_key_to_user[api_key]
            del self.api_key_to_user[api_key]
            logger.info(f"API key revoked for user: {user_id[:8]}...")
            return True
        
        logger.warning("Attempted to revoke non-existent API key")
        return False
    
    def list_user_api_keys(self, user_id: str) -> list:
        """OPTIONAL: List API keys for a user (for external LLM access)."""
        keys = []
        for api_key, uid in self.api_key_to_user.items():
            if uid == user_id:
                masked = f"{api_key[:10]}...{api_key[-4:]}"
                keys.append(masked)
        return keys
    
    # =======================================================================
    # EXTERNAL MCP CLIENT AUTHENTICATION (Cursor, Claude Code, etc.)
    # =======================================================================
    
    def login_with_credentials(self, username: str, password: str) -> Dict:
        """
        Authenticate user with username/password for external MCP clients.
        
        Supports:
        - Cursor MCP server integration
        - Claude Desktop integration
        - Any external LLM that supports MCP protocol
        
        All data operations use Firestore, so real-time sync is automatic!
        
        Args:
            username: User's username or email
            password: User's password (plain text)
        
        Returns:
            Dict with:
            - success: bool
            - user_id: str (if success)
            - error: str (if failure)
        """
        try:
            # Try Firestore first (primary database)
            if BACKEND_UTILS_AVAILABLE:
                try:
                    db = get_firestore()
                    
                    # Search by username
                    users_ref = db.collection('users')
                    username_query = users_ref.where('username', '==', username).limit(1)
                    user_docs = list(username_query.stream())
                    
                    # If not found, try email
                    if not user_docs:
                        email_query = users_ref.where('email', '==', username).limit(1)
                        user_docs = list(email_query.stream())
                    
                    if user_docs:
                        user_doc = user_docs[0]
                        user_data = user_doc.to_dict()
                        user_id = user_doc.id
                        
                        # Verify password
                        stored_password = user_data.get('password')
                        if stored_password and verify_password(password, stored_password):
                            logger.info(f"✅ Login successful via Firestore: {user_id[:8]}...")
                            
                            # Store session (optional - can generate API key)
                            session_token = secrets.token_urlsafe(32)
                            self.api_key_to_user[f"session_{session_token}"] = user_id
                            
                            return {
                                "success": True,
                                "user_id": user_id,
                                "username": user_data.get("username"),
                                "email": user_data.get("email"),
                                "session_token": session_token,
                                "message": "Login successful. Use user_id for all tool calls.",
                                "database": "firestore"
                            }
                except Exception as e:
                    logger.warning(f"Firestore login attempt failed: {e}")
                    # Fallback to PostgreSQL
            
            # Fallback to PostgreSQL (if available)
            try:
                from db import get_session, engine
                from sqlmodel import Session, select
                from model import Users
                
                with Session(engine) as session:
                    # Try username first
                    user = session.exec(
                        select(Users).where(Users.username == username)
                    ).first()
                    
                    # Try email if username not found
                    if not user:
                        user = session.exec(
                            select(Users).where(Users.email == username)
                        ).first()
                    
                    if user and verify_password(password, user.password):
                        user_id = str(user.user_id)
                        logger.info(f"✅ Login successful via PostgreSQL: {user_id[:8]}...")
                        
                        # Store session
                        session_token = secrets.token_urlsafe(32)
                        self.api_key_to_user[f"session_{session_token}"] = user_id
                        
                        return {
                            "success": True,
                            "user_id": user_id,
                            "username": user.username,
                            "email": user.email,
                            "session_token": session_token,
                            "message": "Login successful. Use user_id for all tool calls.",
                            "database": "postgresql"
                        }
            except Exception as e:
                logger.warning(f"PostgreSQL login attempt failed: {e}")
            
            # If all attempts failed
            logger.warning(f"❌ Login failed for username: {username[:10]}...")
            return {
                "success": False,
                "error": "Invalid username/email or password",
                "message": "Please check your credentials and try again."
            }
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Authentication service error"
            }


# Global auth instance (singleton)
_auth_instance = None


def get_auth() -> MCPAuth:
    """
    Get the global MCP auth instance (singleton pattern).
    
    Returns:
        MCPAuth: The authentication handler
    """
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = MCPAuth()
    return _auth_instance


def reset_auth():
    """Reset the auth instance (useful for testing)"""
    global _auth_instance
    _auth_instance = None

