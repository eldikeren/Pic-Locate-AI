"""
Start V4 indexing process
"""

import requests
import json

def start_v4_indexing():
    """Start the V4 indexing process"""
    try:
        print("Starting V4 Indexing Process...")
        print("=" * 50)
        
        # Check if backend is running
        try:
            response = requests.get("http://localhost:8000/auth/status", timeout=5)
            if response.status_code == 200:
                print("Backend is running")
                status_data = response.json()
                print(f"   Status: {status_data.get('status', 'unknown')}")
                if status_data.get('status') == 'authenticated':
                    print(f"   Target folder: {status_data.get('target_folder', 'unknown')}")
                else:
                    print("   Not authenticated - you may need to authenticate first")
            else:
                print("Backend not responding properly")
                return
        except requests.exceptions.RequestException as e:
            print(f"Cannot connect to backend: {e}")
            print("   Make sure the V4 backend is running on port 8000")
            return
        
        # Start indexing
        print("\nStarting V4 indexing...")
        try:
            response = requests.post("http://localhost:8000/index", 
                                   json={}, 
                                   timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print("Indexing started successfully!")
                print(f"   Response: {result}")
            else:
                print(f"Failed to start indexing: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Error starting indexing: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_v4_indexing()
