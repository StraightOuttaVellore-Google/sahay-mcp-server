import os
from dotenv import load_dotenv

load_dotenv()

print(os.getenv('SERVICE_ACCOUNT_KEY_PATH'))
print(os.getenv('FIREBASE_PROJECT_ID'))

class Config:
    SERVICE_ACCOUNT_KEY_PATH = os.getenv('SERVICE_ACCOUNT_KEY_PATH', '')
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', '')
    SERVER_NAME = "study-mcp-server"
    SERVER_VERSION = "1.0.0"

config = Config()
