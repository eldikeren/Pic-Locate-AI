#!/usr/bin/env python3
"""
Simple Google Drive test
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

def test_basic_access():
    service_account_file = "secret-spark-432817-r3-e78bdaac1d51.json"

    print("🔍 Checking service account file...")
    if os.path.exists(service_account_file):
        print("✅ Service account file found")
    else:
        print("❌ Service account file NOT found")
        return

    try:
        print("🔐 Loading credentials...")
        creds = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        print("✅ Credentials loaded")

        print("🔌 Building Drive service...")
        drive = build('drive', 'v3', credentials=creds)
        print("✅ Drive service created")

        print("📡 Testing connection...")
        # Simple about call
        about = drive.about().get(fields="user(displayName)").execute()
        print(f"✅ Connected as: {about['user']['displayName']}")

        print("\n🗂️ Testing file listing...")
        results = drive.files().list(pageSize=5).execute()
        files = results.get('files', [])
        print(f"✅ Found {len(files)} files")

        if files:
            print("📋 Sample files:")
            for f in files:
                print(f"   - {f['name']} ({f.get('mimeType', 'unknown')})")
        else:
            print("📭 No files found in Drive")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 This usually means:")
        print("   - Service account lacks permissions")
        print("   - Drive API not enabled")
        print("   - Invalid service account key")

if __name__ == "__main__":
    test_basic_access()
