"""
Start V4 drive crawling
"""

import requests
import time

def start_crawling():
    try:
        print("Starting V4 drive crawling...")
        print("This will use the new advanced features:")
        print("- Multi-pass vision pipeline")
        print("- Room classification")
        print("- Per-object colors & materials")
        print("- Structured captions")
        print("- Advanced embeddings")
        print()
        
        response = requests.post('http://localhost:8000/index', timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("Crawling started successfully!")
            print("Response:", result)
        else:
            print(f"Error: {response.status_code}")
            print("Response:", response.text)
            
    except requests.exceptions.Timeout:
        print("Request timed out - crawling is likely in progress")
        print("Check the backend terminal for progress updates")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_crawling()
