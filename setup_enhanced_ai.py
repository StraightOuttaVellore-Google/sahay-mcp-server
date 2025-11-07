#!/usr/bin/env python3
"""
Quick Setup Script for Enhanced AI Analysis Tools

This script helps you quickly set up the enhanced analysis tools with Google's GenAI stack.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"   Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing Dependencies")
    print("-" * 30)
    
    # Core dependencies
    core_deps = [
        "mcp>=1.0.0",
        "firebase-admin>=6.0.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0"
    ]
    
    # Google GenAI dependencies
    genai_deps = [
        "google-cloud-aiplatform[agent_engines,adk,langchain,ag2,llama_index]>=1.112.0",
        "google-genai-haystack>=0.1.0",
        "vertexai>=1.0.0"
    ]
    
    # Visualization dependencies
    viz_deps = [
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0"
    ]
    
    # Additional AI/ML dependencies
    ml_deps = [
        "scikit-learn>=1.3.0",
        "plotly>=5.15.0"
    ]
    
    all_deps = core_deps + genai_deps + viz_deps + ml_deps
    
    for dep in all_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep.split('>=')[0]}"):
            print(f"⚠️  Failed to install {dep}, continuing...")
    
    return True


def create_env_file():
    """Create environment configuration file"""
    print("\n⚙️  Creating Environment Configuration")
    print("-" * 40)
    
    env_content = """# Firebase Configuration
SERVICE_ACCOUNT_KEY_PATH=/path/to/firebase-service-account-key.json
FIREBASE_PROJECT_ID=your-firebase-project-id

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Optional: Google AI Studio API Key (for additional features)
GOOGLE_API_KEY=your-google-ai-studio-api-key

# Optional: Vertex AI Model Configuration
VERTEX_AI_MODEL=gemini-2.0-flash-exp
TEXT_MODEL=gemini-2
"""
    
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists, skipping creation")
        print("   Please update the existing .env file with the required variables")
    else:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
        print("   Please update the values in .env file with your actual credentials")
    
    return True


def create_setup_instructions():
    """Create setup instructions file"""
    print("\n📚 Creating Setup Instructions")
    print("-" * 30)
    
    instructions = """# Quick Setup Instructions

## 1. Google Cloud Setup

### Create Project and Enable APIs
```bash
# Create new project
gcloud projects create your-project-id --name="Sahay AI Analytics"

# Set as default project
gcloud config set project your-project-id

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable storage.googleapis.com
```

### Authentication
```bash
# Authenticate with Google Cloud
gcloud auth login
gcloud auth application-default login
```

## 2. Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create new project or select existing
3. Enable Firestore Database
4. Go to Project Settings → Service Accounts
5. Generate new private key and download JSON file
6. Update `SERVICE_ACCOUNT_KEY_PATH` in `.env`

## 3. Environment Configuration

Update the `.env` file with your actual values:

```env
SERVICE_ACCOUNT_KEY_PATH=/path/to/your/firebase-key.json
FIREBASE_PROJECT_ID=your-firebase-project-id
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

## 4. Test the Setup

```bash
# Test the enhanced AI analysis tools
python demo_ai_analysis.py

# Run the MCP server
python src/main.py

# Test with MCP Inspector
mcp-inspector python src/main.py
```

## 5. Available Enhanced Tools

- `analyze_wellness_trends_ai` - AI-powered wellness analysis
- `analyze_study_patterns_ai` - AI-powered study analysis
- `generate_comprehensive_ai_report` - Complete AI report
- `save_ai_analysis_results` - Save with AI metadata

## Features Included

✅ Google Gemini 2.0 Flash Integration
✅ Automatic Data Visualization
✅ AI-Enhanced Analytics
✅ Comprehensive Reporting
✅ Firebase Integration
✅ Confidence Scoring
✅ Personalized Recommendations

## Troubleshooting

1. **Vertex AI Issues**: Check authentication and project permissions
2. **Firebase Issues**: Verify service account key and Firestore rules
3. **Visualization Issues**: Install matplotlib dependencies
4. **Import Errors**: Ensure all dependencies are installed

## Support

- Check Google Cloud documentation
- Verify Firebase configuration
- Review environment variables
- Test individual components
"""
    
    with open("SETUP_INSTRUCTIONS.md", 'w') as f:
        f.write(instructions)
    
    print("✅ Created SETUP_INSTRUCTIONS.md")
    return True


def test_imports():
    """Test if all required modules can be imported"""
    print("\n🧪 Testing Imports")
    print("-" * 20)
    
    test_modules = [
        ("mcp", "MCP framework"),
        ("firebase_admin", "Firebase Admin SDK"),
        ("pydantic", "Pydantic validation"),
        ("matplotlib", "Matplotlib plotting"),
        ("seaborn", "Seaborn styling"),
        ("pandas", "Pandas data analysis"),
        ("numpy", "NumPy numerical computing")
    ]
    
    optional_modules = [
        ("vertexai", "Vertex AI SDK"),
        ("google.cloud.aiplatform", "Google Cloud AI Platform"),
        ("plotly", "Plotly visualization")
    ]
    
    success_count = 0
    
    # Test required modules
    for module, description in test_modules:
        try:
            __import__(module)
            print(f"✅ {description} - OK")
            success_count += 1
        except ImportError as e:
            print(f"❌ {description} - FAILED: {e}")
    
    # Test optional modules
    for module, description in optional_modules:
        try:
            __import__(module)
            print(f"✅ {description} - OK (optional)")
            success_count += 1
        except ImportError:
            print(f"⚠️  {description} - Not available (optional)")
    
    print(f"\n📊 Import Test Results: {success_count}/{len(test_modules)} required modules available")
    
    if success_count >= len(test_modules):
        print("✅ All required modules are available!")
        return True
    else:
        print("❌ Some required modules are missing")
        return False


def main():
    """Main setup function"""
    print("🚀 Enhanced AI Analysis Tools Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("⚠️  Some dependencies failed to install, but continuing...")
    
    # Create environment file
    create_env_file()
    
    # Create setup instructions
    create_setup_instructions()
    
    # Test imports
    if test_imports():
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next Steps:")
        print("   1. Update .env file with your credentials")
        print("   2. Set up Google Cloud project and Firebase")
        print("   3. Run: python demo_ai_analysis.py")
        print("   4. Start the MCP server: python src/main.py")
        print("\n📚 Documentation:")
        print("   • SETUP_INSTRUCTIONS.md - Quick setup guide")
        print("   • ENHANCED_AI_SETUP_GUIDE.md - Detailed setup guide")
        print("   • FIREBASE_INTEGRATION_README.md - Firebase integration")
        return True
    else:
        print("\n❌ Setup completed with errors")
        print("   Please install missing dependencies and try again")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
