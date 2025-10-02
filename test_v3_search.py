"""
Test V3 Search Functionality
"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_v3_search():
    """Test V3 search functionality"""
    print("Testing V3 Search Functionality")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        "kitchen",
        "black table",
        "bathroom",
        "living room"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        
        try:
            # Test with V3 backend format
            response = requests.post(f"{API_BASE}/search", 
                                   json={"query": query, "limit": 5},
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Status: {response.status_code}")
                print(f"  Results: {len(data.get('results', []))}")
                
                if data.get('results'):
                    print(f"  Top result: {data['results'][0].get('file_name', 'N/A')}")
                    print(f"  Similarity: {data['results'][0].get('similarity', 'N/A')}")
                else:
                    print("  No results found")
            else:
                print(f"  Error: {response.status_code}")
                print(f"  Response: {response.text}")
                
        except Exception as e:
            print(f"  Exception: {e}")
    
    # Test Hebrew search specifically
    print(f"\nTesting Hebrew Search...")
    hebrew_queries = [
        "kitchen",  # English
        "מטבח",     # Hebrew - kitchen
    ]
    
    for query in hebrew_queries:
        print(f"\nTesting Hebrew query: '{query}'")
        
        try:
            response = requests.post(f"{API_BASE}/search", 
                                   json={"query": query, "limit": 3},
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Status: {response.status_code}")
                print(f"  Results: {len(data.get('results', []))}")
                
                if data.get('results'):
                    for i, result in enumerate(data['results'][:2]):
                        print(f"    {i+1}. {result.get('file_name', 'N/A')} (similarity: {result.get('similarity', 'N/A')})")
                else:
                    print("  No results found")
            else:
                print(f"  Error: {response.status_code}")
                
        except Exception as e:
            print(f"  Exception: {e}")

if __name__ == "__main__":
    test_v3_search()
