#!/usr/bin/env python3
"""
Test the crawl function directly
"""

import os
import sys
sys.path.append('.')

# Import the crawl function from the FastAPI app
from fastapi_drive_ai_v3 import crawl_drive_images
from google.oauth2 import service_account
from googleapiclient.discovery import build

def test_crawl_function():
    """Test the crawl function directly"""
    service_account_file = "secret-spark-432817-r3-e78bdaac1d51.json"
    shared_folder_id = "11kSHWn47cQqeRhtlVQ-4Uask7jr2fqjW"
    
    if not os.path.exists(service_account_file):
        print(f"❌ Service account file not found: {service_account_file}")
        return

    try:
        print("🔐 Loading service account credentials...")
        creds = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )

        drive_service = build('drive', 'v3', credentials=creds)
        print("✅ Drive service created")

        print(f"\n🎯 Testing crawl function on shared folder...")
        print(f"Folder ID: {shared_folder_id}")
        print(f"Folder Path: תיקיית ה בתים")
        
        # Call the crawl function directly
        crawl_drive_images(drive_service, folder_id=shared_folder_id, folder_path="תיקיית ה בתים")
        
        print(f"\n✅ Crawl function completed!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_crawl_function()
