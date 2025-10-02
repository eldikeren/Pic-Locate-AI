#!/usr/bin/env python3
"""
Test Google Drive access and permissions
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def test_drive_access():
    """Test what the service account can access"""
    service_account_file = "secret-spark-432817-r3-e78bdaac1d51.json"

    if not os.path.exists(service_account_file):
        print(f"❌ Service account file not found: {service_account_file}")
        return False

    try:
        print("🔐 Loading service account credentials...")
        creds = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )

        print("✅ Credentials loaded successfully")

        drive_service = build('drive', 'v3', credentials=creds)
        print("✅ Drive service created")

        # Test 1: List root files
        print("\n📁 Testing root directory access...")
        try:
            results = drive_service.files().list(
                pageSize=10,
                fields="files(id,name,mimeType,parents),nextPageToken"
            ).execute()

            files = results.get('files', [])
            print(f"✅ Found {len(files)} items in root")

            images = [f for f in files if f['mimeType'].startswith('image/')]
            print(f"📸 Images: {len(images)}")

            for file in files[:5]:  # Show first 5 items
                print(f"   - {file['name']} ({file['mimeType']})")

        except HttpError as e:
            print(f"❌ Root access failed: {e}")

        # Test 2: Check permissions
        print("\n🔑 Testing permissions...")
        try:
            about = drive_service.about().get(fields="user(displayName,emailAddress),storageQuota").execute()
            print(f"✅ Connected as: {about['user']['displayName']}")
            print(f"   Email: {about['user']['emailAddress']}")

            quota = about.get('storageQuota', {})
            if quota:
                print(f"   Storage: {quota.get('limit', 'Unknown')} bytes limit")
                print(f"   Used: {quota.get('usage', '0')} bytes")

        except HttpError as e:
            print(f"❌ About failed: {e}")

        return True

    except Exception as e:
        print(f"❌ Service account test failed: {str(e)}")
        return False

def main():
    print("🧪 Testing Google Drive Access")
    print("=" * 40)

    success = test_drive_access()

    if success:
        print("\n✅ Service account is working!")
        print("💡 If no images found, your Google Drive might be empty")
        print("   or the service account needs access to specific folders")
    else:
        print("\n💥 Service account has issues")
        print("🔧 Solutions:")
        print("   1. Check service account permissions in Google Cloud Console")
        print("   2. Verify the service account key is valid")
        print("   3. Make sure Drive API is enabled")

if __name__ == "__main__":
    main()
