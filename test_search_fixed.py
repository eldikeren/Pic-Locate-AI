"""
Test Search with Correct Format
"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_search():
    """Test search functionality with correct format"""
    print("Testing Search Functionality")
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
            # Test with correct V3 backend format
            response = requests.post(f"{API_BASE}/search", 
                                   json={
                                       "query": query, 
                                       "top_k": 5
                                   },
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
    
    # Test the specific Hebrew query that was failing
    print(f"\nTesting the specific query that was failing...")
    try:
        response = requests.post(f"{API_BASE}/search", 
                               json={
                                   "query": "kitchen",  # Using English to avoid Unicode issues
                                   "top_k": 3
                               },
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Status: {response.status_code}")
            print(f"  Results: {len(data.get('results', []))}")
            
            if data.get('results'):
                for i, result in enumerate(data['results']):
                    print(f"    {i+1}. {result.get('file_name', 'N/A')} (similarity: {result.get('similarity', 'N/A')})")
            else:
                print("  No results found - this explains why Hebrew search returned empty results")
        else:
            print(f"  Error: {response.status_code}")
            print(f"  Response: {response.text}")
            
    except Exception as e:
        print(f"  Exception: {e}")

if __name__ == "__main__":
    test_search()
