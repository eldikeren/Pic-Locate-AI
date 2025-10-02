"""
Manual OAuth flow and indexing
"""

import requests
import webbrowser
import time

def manual_oauth_indexing():
    """Manually complete OAuth and start indexing"""
    try:
        print("Manual OAuth Flow & Indexing")
        print("=" * 40)
        
        # Step 1: Get OAuth URL
        print("Getting OAuth URL...")
        response = requests.get("http://localhost:8000/auth", timeout=15)
        
        if response.status_code == 200:
            auth_data = response.json()
            print(f"Status: {auth_data.get('status')}")
            
            if auth_data.get('status') == 'oauth_required':
                auth_url = auth_data.get('auth_url')
                print(f"\nOAuth URL generated successfully!")
                print("=" * 60)
                print("COPY THIS URL AND OPEN IT IN YOUR BROWSER:")
                print("=" * 60)
                print(auth_url)
                print("=" * 60)
                
                # Try to open browser
                try:
                    webbrowser.open(auth_url)
                    print("Browser opened automatically")
                except:
                    print("Please copy the URL above and open it manually")
                
                print("\nIMPORTANT: After completing authentication:")
                print("1. You'll be redirected to a success page")
                print("2. The URL will contain 'code=' parameter")
                print("3. Come back here and press Enter")
                input("\nPress Enter after completing authentication...")
                
                # Step 2: Check authentication
                print("\nChecking authentication status...")
                time.sleep(3)  # Give it time to process
                
                status_response = requests.get("http://localhost:8000/auth/status", timeout=15)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"Auth status: {status_data.get('status')}")
                    
                    if status_data.get('status') == 'authenticated':
                        print("SUCCESS: Authentication completed!")
                        print(f"Target folder: {status_data.get('target_folder')}")
                        
                        # Step 3: Start indexing
                        print("\nStarting V4 indexing...")
                        print("This will process all images with the advanced pipeline...")
                        
                        try:
                            index_response = requests.post("http://localhost:8000/index", 
                                                        json={}, 
                                                        timeout=120)  # 2 minute timeout
                            
                            if index_response.status_code == 200:
                                result = index_response.json()
                                print("Indexing started successfully!")
                                print(f"Response: {result}")
                            else:
                                print(f"Indexing failed: {index_response.status_code}")
                                print(f"Response: {index_response.text}")
                                
                        except requests.exceptions.Timeout:
                            print("Indexing request timed out - this is normal")
                            print("The indexing process is starting in the background")
                            print("Check the backend terminal for progress updates")
                        except Exception as e:
                            print(f"Indexing error: {e}")
                            
                    else:
                        print(f"Authentication not completed: {status_data}")
                        print("Please try the OAuth process again")
                else:
                    print(f"Status check failed: {status_response.status_code}")
                    print(f"Response: {status_response.text}")
            else:
                print(f"Unexpected response: {auth_data}")
        else:
            print(f"Failed to get OAuth URL: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    manual_oauth_indexing()
