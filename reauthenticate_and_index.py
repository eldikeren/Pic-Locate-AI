"""
Re-authenticate and start V4 indexing
"""

import requests
import webbrowser
import time

def reauthenticate_and_index():
    """Re-authenticate and start indexing"""
    try:
        print("V4 Backend Authentication & Indexing")
        print("=" * 50)
        
        # Step 1: Get OAuth URL
        print("Step 1: Getting OAuth URL...")
        try:
            response = requests.get("http://localhost:8000/auth", timeout=10)
            if response.status_code == 200:
                auth_data = response.json()
                if auth_data.get('status') == 'oauth_required':
                    auth_url = auth_data.get('auth_url')
                    print("OAuth URL generated successfully!")
                    print("=" * 60)
                    print("COPY THIS URL AND OPEN IT IN YOUR BROWSER:")
                    print("=" * 60)
                    print(auth_url)
                    print("=" * 60)
                    
                    # Try to open browser automatically
                    try:
                        webbrowser.open(auth_url)
                        print("Browser opened automatically")
                    except:
                        print("Please copy the URL above and open it manually")
                    
                    print("\nAfter authenticating in the browser:")
                    print("1. You'll be redirected to a success page")
                    print("2. Come back here and press Enter to continue")
                    input("Press Enter after completing authentication...")
                    
                    # Step 2: Check auth status
                    print("\nStep 2: Checking authentication status...")
                    time.sleep(2)  # Give it a moment
                    
                    auth_check = requests.get("http://localhost:8000/auth/status", timeout=10)
                    if auth_check.status_code == 200:
                        status_data = auth_check.json()
                        if status_data.get('status') == 'authenticated':
                            print("Authentication successful!")
                            print(f"Target folder: {status_data.get('target_folder')}")
                            
                            # Step 3: Start indexing
                            print("\nStep 3: Starting V4 indexing...")
                            print("This will process all images with the advanced V4 pipeline...")
                            
                            try:
                                index_response = requests.post("http://localhost:8000/index", 
                                                            json={}, 
                                                            timeout=60)
                                
                                if index_response.status_code == 200:
                                    result = index_response.json()
                                    print("Indexing started successfully!")
                                    print(f"Response: {result}")
                                else:
                                    print(f"Failed to start indexing: {index_response.status_code}")
                                    print(f"Response: {index_response.text}")
                                    
                            except requests.exceptions.Timeout:
                                print("Indexing request timed out - this is normal")
                                print("The indexing process is starting in the background")
                                print("Check the backend terminal for progress updates")
                            except Exception as e:
                                print(f"Error starting indexing: {e}")
                                
                        else:
                            print(f"Authentication failed: {status_data}")
                    else:
                        print("Could not check authentication status")
                        
                else:
                    print(f"Unexpected response: {auth_data}")
            else:
                print(f"Failed to get OAuth URL: {response.status_code}")
                
        except Exception as e:
            print(f"Error: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reauthenticate_and_index()
