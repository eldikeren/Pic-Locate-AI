"""
Test OAuth URL generation
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow

def test_oauth():
    try:
        SCOPES = [
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'openid'
        ]
        
        oauth_file = "client_secret_1012576941399-515ln173s773sbrrpn3gtmek0d5vc0u5.apps.googleusercontent.com.json"
        
        if not os.path.exists(oauth_file):
            print("OAuth file not found:", oauth_file)
            return
        
        print("OAuth file found")
        
        flow = InstalledAppFlow.from_client_secrets_file(oauth_file, scopes=SCOPES)
        flow.redirect_uri = 'http://localhost:8000/auth/callback'
        
        auth_url, _ = flow.authorization_url(
            prompt='consent',
            access_type='offline',
            include_granted_scopes='true'
        )
        
        print("OAuth URL generated successfully!")
        print("=" * 80)
        print("COPY THIS URL AND OPEN IT IN YOUR BROWSER:")
        print("=" * 80)
        print(auth_url)
        print("=" * 80)
        print()
        print("After completing OAuth, you'll be redirected to:")
        print("http://localhost:8000/auth/callback?code=...")
        print()
        print("Copy the 'code' parameter from the URL and use it to complete authentication.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_oauth()
