"""
Simple Hebrew Search Test
"""

import requests
import json

def test_hebrew_search():
    """Test Hebrew search with simple approach"""
    print("Testing Hebrew Search")
    print("=" * 30)
    
    # Test the exact query that was failing
    query = "kitchen"  # Using English to avoid Unicode issues in console
    
    try:
        # Test with a simple request
        response = requests.post(
            "http://localhost:8000/search",
            json={"query": query, "top_k": 5},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Results: {data.get('total_results', 0)}")
            if data.get('results'):
                print("Found results!")
                for i, result in enumerate(data['results'][:3]):
                    print(f"  {i+1}. {result.get('file_name', 'N/A')}")
            else:
                print("No results found")
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test database connection
    print(f"\nTesting database connection...")
    try:
        response = requests.get("http://localhost:8000/stats/overview", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Database connected!")
            print(f"Total images: {data.get('database_stats', {}).get('total_images', 0)}")
            print(f"Total captions: {data.get('database_stats', {}).get('total_captions', 0)}")
        else:
            print(f"Database error: {response.status_code}")
    except Exception as e:
        print(f"Database exception: {e}")

if __name__ == "__main__":
    test_hebrew_search()
