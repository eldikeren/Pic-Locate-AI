"""
Simple Search Test
"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_search():
    """Test search functionality"""
    print("Testing Search Functionality")
    print("=" * 50)
    
    # Test queries (English only to avoid Unicode issues)
    test_queries = [
        "kitchen",
        "black table",
        "bathroom",
        "living room"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        
        try:
            # Test with the current backend
            response = requests.post(f"{API_BASE}/search", 
                                   json={"query": query, "limit": 5},
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Status: {response.status_code}")
                print(f"  Results: {len(data.get('results', []))}")
                
                if data.get('results'):
                    print(f"  Top result: {data['results'][0].get('file_name', 'N/A')}")
                else:
                    print("  No results found")
            else:
                print(f"  Error: {response.status_code}")
                print(f"  Response: {response.text}")
                
        except Exception as e:
            print(f"  Exception: {e}")
    
    # Test database connection
    print(f"\nTesting Database Connection...")
    try:
        response = requests.get(f"{API_BASE}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  Backend Status: {data.get('status', 'Unknown')}")
            print(f"  App: {data.get('app', 'Unknown')}")
            print(f"  Version: {data.get('version', 'Unknown')}")
        else:
            print(f"  Backend Error: {response.status_code}")
    except Exception as e:
        print(f"  Backend Exception: {e}")

if __name__ == "__main__":
    test_search()
