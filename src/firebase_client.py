import firebase_admin
from firebase_admin import credentials, firestore
from .config import config
import json

_app = None
_db = None

def initialize_firebase():
    global _app, _db
    
    if _app:
        return _app
    
    try:
        # Read service account key
        with open(config.SERVICE_ACCOUNT_KEY_PATH, 'r') as f:
            service_account_info = json.load(f)
        
        cred = credentials.Certificate(service_account_info)
        _app = firebase_admin.initialize_app(cred)
        _db = firestore.client()
        
        return _app
    except Exception as e:
        raise Exception(f"Firebase initialization failed: {e}")

def get_firestore():
    if not _db:
        raise Exception("Firebase not initialized")
    return _db
