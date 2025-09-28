#!/usr/bin/env python3
"""
Setup script for Google Drive AI Visual Search
This script helps set up the complete environment
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_backend_dependencies():
    """Install Python dependencies"""
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )

def setup_frontend():
    """Setup React frontend"""
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    os.chdir(frontend_dir)
    
    # Install Node.js dependencies
    if not run_command("npm install", "Installing Node.js dependencies"):
        return False
    
    os.chdir("..")
    return True

def create_credentials_template():
    """Create credentials template if it doesn't exist"""
    if os.path.exists("credentials.json"):
        print("✅ credentials.json already exists")
        return True
    
    if os.path.exists("credentials_template.json"):
        print("📋 Please copy credentials_template.json to credentials.json and fill in your Google Cloud credentials")
        print("   Instructions:")
        print("   1. Go to https://console.cloud.google.com/")
        print("   2. Create a new project or select existing")
        print("   3. Enable Google Drive API")
        print("   4. Create OAuth 2.0 credentials")
        print("   5. Download JSON and save as credentials.json")
        return True
    
    print("❌ credentials_template.json not found")
    return False

def create_directories():
    """Create necessary directories"""
    directories = ["logs", "temp", "uploads"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Created necessary directories")
    return True

def check_gpu_support():
    """Check for GPU support"""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ GPU support detected: {torch.cuda.get_device_name(0)}")
            return True
        else:
            print("⚠️  No GPU detected. Processing will be slower on CPU")
            return True
    except ImportError:
        print("⚠️  PyTorch not installed yet. GPU check will be done after installation")
        return True

def create_env_file():
    """Create environment configuration file"""
    env_content = """# Google Drive AI Visual Search Configuration
# Backend Configuration
BACKEND_PORT=6000
BACKEND_HOST=0.0.0.0

# Frontend Configuration
FRONTEND_PORT=3000
FRONTEND_HOST=localhost

# AI Model Configuration
CLIP_MODEL=ViT-B/32
YOLO_MODEL=yolov8n.pt
DEVICE=auto

# Search Configuration
DEFAULT_TOP_K=10
SEMANTIC_WEIGHT=0.6
OBJECT_WEIGHT=0.2
COLOR_WEIGHT=0.2

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Created .env configuration file")
    return True

def main():
    """Main setup function"""
    print("🚀 Google Drive AI Visual Search Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Install backend dependencies
    if not install_backend_dependencies():
        print("❌ Backend setup failed")
        sys.exit(1)
    
    # Check GPU support
    check_gpu_support()
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed")
        sys.exit(1)
    
    # Create credentials template
    if not create_credentials_template():
        print("❌ Credentials setup failed")
        sys.exit(1)
    
    # Create environment file
    create_env_file()
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("=" * 50)
    
    print("\n📋 Next Steps:")
    print("1. Copy credentials_template.json to credentials.json")
    print("2. Fill in your Google Cloud credentials in credentials.json")
    print("3. Start the backend server:")
    print("   python start_server.py")
    print("4. Start the frontend (in another terminal):")
    print("   cd frontend && npm run dev")
    print("5. Open http://localhost:3000 in your browser")
    
    print("\n🔧 Alternative: Use Swagger UI")
    print("   Start backend and visit http://localhost:6000/docs")
    
    print("\n🧪 Run Demo:")
    print("   python demo_scenarios.py")
    
    print("\n📖 Documentation:")
    print("   - README.md: Complete setup guide")
    print("   - QUICK_START.md: 5-minute setup")
    print("   - demo_scenarios.py: Usage examples")

if __name__ == "__main__":
    main()

