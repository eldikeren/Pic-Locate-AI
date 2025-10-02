"""
Test OAuth flow manually
"""

import requests
import webbrowser
import time

def test_oauth_flow():
    """Test the OAuth flow step by step"""
    try:
        print("Testing OAuth Flow...")
        print("=" * 40)
        
        # Step 1: Get OAuth URL
        print("Step 1: Getting OAuth URL...")
        response = requests.get("http://localhost:8000/auth", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            auth_data = response.json()
            print(f"Response: {auth_data}")
            
            if auth_data.get('status') == 'oauth_required':
                auth_url = auth_data.get('auth_url')
                print(f"\nOAuth URL: {auth_url}")
                
                # Open browser
                webbrowser.open(auth_url)
                print("\nBrowser opened. Please complete authentication...")
                print("After authentication, you should be redirected to:")
                print("http://localhost:8000/auth/callback?code=...")
                
                # Wait for user to complete auth
                input("\nPress Enter after completing authentication in browser...")
                
                # Step 2: Check auth status
                print("\nStep 2: Checking authentication status...")
                time.sleep(2)
                
                status_response = requests.get("http://localhost:8000/auth/status", timeout=10)
                print(f"Status check: {status_response.status_code}")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"Auth status: {status_data}")
                    
                    if status_data.get('status') == 'authenticated':
                        print("SUCCESS: Authentication completed!")
                        
                        # Step 3: Test indexing
                        print("\nStep 3: Testing indexing...")
                        try:
                            index_response = requests.post("http://localhost:8000/index", 
                                                        json={}, 
                                                        timeout=30)
                            print(f"Index response: {index_response.status_code}")
                            if index_response.status_code == 200:
                                print("Indexing started successfully!")
                            else:
                                print(f"Index error: {index_response.text}")
                        except requests.exceptions.Timeout:
                            print("Indexing request timed out (normal for startup)")
                        except Exception as e:
                            print(f"Index error: {e}")
                    else:
                        print("Authentication failed or not completed")
                else:
                    print(f"Status check failed: {status_response.text}")
            else:
                print(f"Unexpected auth response: {auth_data}")
        else:
            print(f"Failed to get OAuth URL: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_oauth_flow()