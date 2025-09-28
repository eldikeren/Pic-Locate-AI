#!/usr/bin/env python3
"""
Fix Google Drive access for shared folders
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def test_shared_folder_access():
    """Test access to the specific shared folder"""
    service_account_file = "secret-spark-432817-r3-e78bdaac1d51.json"
    
    # The shared folder ID from the URL
    shared_folder_id = "11kSHWn47cQqeRhtlVQ-4Uask7jr2fqjW"
    
    if not os.path.exists(service_account_file):
        print(f"❌ Service account file not found: {service_account_file}")
        return False

    try:
        print("🔐 Loading service account credentials...")
        creds = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )

        drive_service = build('drive', 'v3', credentials=creds)
        print("✅ Drive service created")

        # Test 1: Try to access the shared folder directly
        print(f"\n📁 Testing access to shared folder: {shared_folder_id}")
        try:
            folder_info = drive_service.files().get(
                fileId=shared_folder_id,
                fields="id,name,mimeType,parents,shared"
            ).execute()
            
            print(f"✅ Folder found: {folder_info['name']}")
            print(f"   ID: {folder_info['id']}")
            print(f"   Shared: {folder_info.get('shared', False)}")
            
        except HttpError as e:
            print(f"❌ Cannot access shared folder: {e}")
            print("💡 The service account needs to be granted access to this folder")
            return False

        # Test 2: List files in the shared folder
        print(f"\n📋 Listing files in shared folder...")
        try:
            results = drive_service.files().list(
                q=f"'{shared_folder_id}' in parents",
                pageSize=10,
                fields="files(id,name,mimeType,parents),nextPageToken"
            ).execute()

            files = results.get('files', [])
            print(f"✅ Found {len(files)} items in shared folder")

            # Count images
            images = [f for f in files if f['mimeType'].startswith('image/')]
            print(f"📸 Images: {len(images)}")

            # Show sample files
            for file in files[:5]:
                print(f"   - {file['name']} ({file['mimeType']})")

        except HttpError as e:
            print(f"❌ Cannot list files in shared folder: {e}")
            return False

        return True

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def main():
    print("🔧 Fixing Google Drive Access")
    print("=" * 40)
    print("📁 Target folder: https://drive.google.com/drive/folders/11kSHWn47cQqeRhtlVQ-4Uask7jr2fqjW")
    print()

    success = test_shared_folder_access()

    if success:
        print("\n✅ SUCCESS! Service account can access the shared folder")
        print("🎉 Your application should now find images!")
    else:
        print("\n❌ ISSUE: Service account cannot access the shared folder")
        print("\n🔧 SOLUTION:")
        print("1. Go to: https://drive.google.com/drive/folders/11kSHWn47cQqeRhtlVQ-4Uask7jr2fqjW")
        print("2. Right-click on the folder")
        print("3. Select 'Share'")
        print("4. Add this email: ilocation@secret-spark-432817-r3.iam.gserviceaccount.com")
        print("5. Give it 'Viewer' permissions")
        print("6. Click 'Send'")
        print("\n💡 After sharing, restart your application!")

if __name__ == "__main__":
    main()
