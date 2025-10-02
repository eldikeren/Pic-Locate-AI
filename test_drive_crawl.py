#!/usr/bin/env python3
"""
Test Google Drive crawling directly
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def test_drive_crawl():
    """Test crawling the shared folder directly"""
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

        # Test 1: List all items in the shared folder
        print(f"\n📁 Listing all items in shared folder...")
        results = drive_service.files().list(
            q=f"'{shared_folder_id}' in parents",
            pageSize=20,
            fields="files(id,name,mimeType,parents),nextPageToken"
        ).execute()

        files = results.get('files', [])
        print(f"✅ Found {len(files)} items in shared folder")

        # Show all items
        for file in files:
            print(f"   - {file['name']} ({file['mimeType']})")

        # Test 2: Look for images specifically
        print(f"\n📸 Looking for images in shared folder...")
        image_query = f"'{shared_folder_id}' in parents and mimeType contains 'image/' and trashed=false"
        image_results = drive_service.files().list(
            q=image_query,
            fields="files(id,name,mimeType,parents)"
        ).execute()

        images = image_results.get('files', [])
        print(f"✅ Found {len(images)} images in shared folder")

        for image in images:
            print(f"   📸 {image['name']} ({image['mimeType']})")

        # Test 3: Look for images in subfolders
        print(f"\n🔍 Looking for images in subfolders...")
        total_images = 0
        
        for file in files:
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                folder_name = file['name']
                folder_id = file['id']
                
                print(f"\n   📁 Checking folder: {folder_name}")
                
                # Look for images in this subfolder
                subfolder_query = f"'{folder_id}' in parents and mimeType contains 'image/' and trashed=false"
                subfolder_results = drive_service.files().list(
                    q=subfolder_query,
                    fields="files(id,name,mimeType)"
                ).execute()
                
                subfolder_images = subfolder_results.get('files', [])
                print(f"      📸 Found {len(subfolder_images)} images")
                total_images += len(subfolder_images)
                
                # Show first few images
                for img in subfolder_images[:3]:
                    print(f"         - {img['name']}")
                if len(subfolder_images) > 3:
                    print(f"         ... and {len(subfolder_images) - 3} more")

        print(f"\n🎯 Total images found across all folders: {total_images}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_drive_crawl()
