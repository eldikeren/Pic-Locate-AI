"""
Test V4 backend endpoints
"""

import requests
import json

def test_v4_backend():
    """Test if V4 backend is working"""
    try:
        print("Testing V4 Backend...")
        print("=" * 30)
        
        # Test basic connectivity
        try:
            response = requests.get("http://localhost:8000/", timeout=10)
            print(f"Root endpoint: {response.status_code}")
        except Exception as e:
            print(f"Root endpoint error: {e}")
        
        # Test auth status
        try:
            response = requests.get("http://localhost:8000/auth/status", timeout=10)
            print(f"Auth status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Status: {data.get('status')}")
                print(f"  Target folder: {data.get('target_folder')}")
        except Exception as e:
            print(f"Auth status error: {e}")
        
        # Test if /index endpoint exists
        try:
            response = requests.get("http://localhost:8000/index", timeout=10)
            print(f"Index GET: {response.status_code}")
        except Exception as e:
            print(f"Index GET error: {e}")
        
        # Test docs endpoint
        try:
            response = requests.get("http://localhost:8000/docs", timeout=10)
            print(f"Docs endpoint: {response.status_code}")
        except Exception as e:
            print(f"Docs endpoint error: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_v4_backend()
