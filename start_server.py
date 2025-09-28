#!/usr/bin/env python3
"""
Startup script for Google Drive AI Search API
This script handles the server startup with proper configuration
"""

import uvicorn
import os
import sys

def check_requirements():
    """Check if all required files exist"""
    required_files = ["credentials.json"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n📋 Setup instructions:")
        print("1. Go to Google Cloud Console")
        print("2. Enable Google Drive API")
        print("3. Create OAuth 2.0 credentials")
        print("4. Download credentials.json to this directory")
        print("5. Copy credentials_template.json to credentials.json and fill in your values")
        return False
    
    return True

def main():
    """Start the FastAPI server"""
    print("🚀 Starting Google Drive AI Search API")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check if credentials.json is properly configured
    try:
        import json
        with open("credentials.json", "r") as f:
            creds = json.load(f)
            if "YOUR_CLIENT_ID" in str(creds):
                print("⚠️  Warning: credentials.json appears to be a template")
                print("   Please update it with your actual Google Cloud credentials")
                sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading credentials.json: {e}")
        sys.exit(1)
    
    print("✅ All requirements met")
    print("🌐 Starting server on http://localhost:6000")
    print("📖 API documentation: http://localhost:6000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print()
    
    # Start the server
    try:
        uvicorn.run(
            "fastapi_drive_ai_v3:app",
            host="0.0.0.0",
            port=6000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

