"""
Firebase Client for MCP Server

Initializes Firebase Admin SDK for Firestore access.
Uses the same credentials as the main backend app.
"""

import firebase_admin
from firebase_admin import credentials, firestore
from .config import config
from pathlib import Path
import json
import os

_app = None
_db = None

def initialize_firebase():
    """
    Initialize Firebase Admin SDK with service account credentials.
    
    Resolves SERVICE_ACCOUNT_KEY_PATH relative to backend root directory,
    not the MCP server directory.
    """
    global _app, _db
    
    if _app:
        return _app
    
    try:
        service_account_path = config.SERVICE_ACCOUNT_KEY_PATH
        
        if not service_account_path:
            raise Exception("SERVICE_ACCOUNT_KEY_PATH not set in environment variables")
        
        # Resolve path relative to backend root
        # If it's already an absolute path, Path() will preserve it
        # If it's relative, resolve it from backend root (4 levels up from this file)
        if not os.path.isabs(service_account_path):
            backend_root = Path(__file__).parent.parent.parent.parent
            service_account_path = backend_root / service_account_path
        else:
            service_account_path = Path(service_account_path)
        
        print(f"🔑 Loading Firebase credentials from: {service_account_path}")
        
        if not service_account_path.exists():
            raise FileNotFoundError(
                f"Firebase service account file not found: {service_account_path}\n"
                f"Make sure the file exists in the backend root directory."
            )
        
        # Read and parse service account JSON
        with open(service_account_path, 'r') as f:
            service_account_info = json.load(f)
        
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(service_account_info)
        _app = firebase_admin.initialize_app(cred)
        _db = firestore.client()
        
        print(f"✅ Firebase Admin SDK initialized successfully")
        print(f"   Project: {service_account_info.get('project_id', 'unknown')}")
        
        return _app
        
    except FileNotFoundError as e:
        raise Exception(f"Firebase credentials file not found: {e}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON in Firebase credentials file: {e}")
    except Exception as e:
        raise Exception(f"Firebase initialization failed: {e}")

def get_firestore():
    """
    Get Firestore database client instance.
    
    Returns:
        firestore.Client: Firestore database client
    
    Raises:
        Exception: If Firebase is not initialized
    """
    global _db
    
    if not _db:
        initialize_firebase()
    
    if not _db:
        raise Exception("Firebase not initialized")
    
    return _db
