"""
Start V4 indexing with longer timeout
"""

import requests
import json
import time

def start_indexing_long_timeout():
    """Start indexing with longer timeout"""
    try:
        print("Starting V4 Indexing with Long Timeout...")
        print("=" * 50)
        
        # Test auth status first
        try:
            response = requests.get("http://localhost:8000/auth/status", timeout=10)
            if response.status_code == 200:
                status_data = response.json()
                print(f"Auth Status: {status_data.get('status')}")
                if status_data.get('status') != 'authenticated':
                    print("Not authenticated - cannot start indexing")
                    return
            else:
                print("Cannot check auth status")
                return
        except Exception as e:
            print(f"Auth check error: {e}")
            return
        
        # Start indexing with very long timeout
        print("\nStarting indexing (this may take a while to initialize)...")
        try:
            response = requests.post("http://localhost:8000/index", 
                                   json={}, 
                                   timeout=300)  # 5 minute timeout
            
            if response.status_code == 200:
                result = response.json()
                print("Indexing started successfully!")
                print(f"Response: {result}")
            else:
                print(f"Failed to start indexing: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print("Request timed out - this is normal for indexing startup")
            print("The indexing process may have started in the background")
            print("Check the backend terminal for progress")
        except requests.exceptions.RequestException as e:
            print(f"Error starting indexing: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_indexing_long_timeout()
