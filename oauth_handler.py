"""
Simple OAuth handler for testing
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def complete_oauth_with_code(auth_code):
    """Complete OAuth with authorization code"""
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
            return None
        
        flow = InstalledAppFlow.from_client_secrets_file(oauth_file, scopes=SCOPES)
        flow.redirect_uri = 'http://localhost:8000/auth/callback'
        
        # Exchange code for credentials
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        
        # Build the service
        drive_service = build('drive', 'v3', credentials=credentials)
        
        print("Authentication successful!")
        print("Testing Google Drive connection...")
        
        # Test the connection
        results = drive_service.files().list(
            q="'11kSHWn47cQqeRhtlVQ-4Uask7jr2fqjW' in parents and mimeType contains 'image/' and trashed=false",
            pageSize=1
        ).execute()
        
        files = results.get('files', [])
        print(f"Found {len(files)} images in target folder")
        
        if files:
            print("Sample file:", files[0]['name'])
        
        return drive_service
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("OAuth Code Handler")
    print("=" * 50)
    print("Paste the authorization code from the OAuth callback URL:")
    print("(The long string after 'code=' in the URL)")
    print()
    
    auth_code = input("Authorization code: ").strip()
    
    if auth_code:
        service = complete_oauth_with_code(auth_code)
        if service:
            print("OAuth completed successfully!")
            print("You can now use the Google Drive service.")
        else:
            print("OAuth failed. Please check the code and try again.")
    else:
        print("No code provided.")
