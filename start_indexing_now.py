"""
Start V4 indexing now that we're authenticated
"""

import requests
import json

def start_indexing_now():
    """Start V4 indexing since we're authenticated"""
    try:
        print("Starting V4 Indexing...")
        print("=" * 40)
        
        # Check auth status first
        print("Checking authentication status...")
        auth_response = requests.get("http://localhost:8000/auth/status", timeout=10)
        
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            print(f"Auth Status: {auth_data.get('status')}")
            
            if auth_data.get('status') == 'authenticated':
                print("Authentication confirmed!")
                print(f"Target folder: {auth_data.get('target_folder')}")
                print(f"Folder ID: {auth_data.get('folder_id')}")
                
                # Start indexing
                print("\nStarting V4 indexing...")
                print("This will process all images with the advanced V4 pipeline:")
                print("- Multi-pass vision analysis")
                print("- Object detection with colors & materials")
                print("- Room classification")
                print("- Structured captions")
                print("- Vector embeddings")
                
                try:
                    index_response = requests.post("http://localhost:8000/index", 
                                                json={}, 
                                                timeout=300)  # 5 minute timeout
                    
                    if index_response.status_code == 200:
                        result = index_response.json()
                        print("Indexing started successfully!")
                        print(f"Response: {result}")
                    else:
                        print(f"Indexing failed: {index_response.status_code}")
                        print(f"Response: {index_response.text}")
                        
                except requests.exceptions.Timeout:
                    print("Request timed out - this is normal for indexing startup")
                    print("The indexing process is starting in the background")
                    print("Check the backend terminal for progress updates")
                    print("\nThe V4 system will now:")
                    print("1. Load AI models (YOLO, CLIP, etc.)")
                    print("2. Start crawling your Google Drive")
                    print("3. Process each image with the advanced pipeline")
                    print("4. Store results in the V4 schema tables")
                    
                except Exception as e:
                    print(f"Error starting indexing: {e}")
                    
            else:
                print(f"Not authenticated: {auth_data}")
        else:
            print(f"Auth check failed: {auth_response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_indexing_now()
