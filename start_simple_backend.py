"""
Simple backend startup for testing OAuth
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Create a simple FastAPI app for testing
app = FastAPI(title="PicLocate V4 - Simple Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "app": "PicLocate V4 - Simple Backend",
        "version": "4.0.0",
        "status": "operational"
    }

@app.get("/auth")
def auth_drive():
    """Start OAuth authentication"""
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        
        SCOPES = [
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'openid'
        ]
        
        oauth_file = "client_secret_1012576941399-515ln173s773sbrrpn3gtmek0d5vc0u5.apps.googleusercontent.com.json"
        
        if not os.path.exists(oauth_file):
            return {
                "status": "oauth_required",
                "message": "OAuth file not found"
            }
        
        flow = InstalledAppFlow.from_client_secrets_file(oauth_file, scopes=SCOPES)
        flow.redirect_uri = 'http://localhost:8000/auth/callback'
        
        auth_url, _ = flow.authorization_url(
            prompt='consent',
            access_type='offline',
            include_granted_scopes='true'
        )
        
        return {
            "status": "oauth_required",
            "auth_url": auth_url
        }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/auth/callback")
def auth_callback(code: str = None, error: str = None):
    """Handle OAuth callback"""
    if error:
        return {"status": "error", "error": f"OAuth error: {error}"}
    
    if not code:
        return {"status": "error", "error": "No authorization code received"}
    
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        
        SCOPES = [
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'openid'
        ]
        
        oauth_file = "client_secret_1012576941399-515ln173s773sbrrpn3gtmek0d5vc0u5.apps.googleusercontent.com.json"
        
        flow = InstalledAppFlow.from_client_secrets_file(oauth_file, scopes=SCOPES)
        flow.redirect_uri = 'http://localhost:8000/auth/callback'
        
        # Exchange code for credentials
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Build the service
        drive_service = build('drive', 'v3', credentials=credentials)
        
        return {
            "status": "success",
            "message": "Authentication successful",
            "redirect_url": "http://localhost:4000"
        }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    print("=" * 60)
    print("PicLocate V4 - Simple Backend (OAuth Testing)")
    print("=" * 60)
    print()
    print("URLs:")
    print("   API: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    print()
    print("Key Endpoints:")
    print("   GET  /auth - Start OAuth")
    print("   GET  /auth/callback - OAuth callback")
    print()
    print("=" * 60)
    print("Starting server...")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )
