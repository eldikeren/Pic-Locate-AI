#!/usr/bin/env python3
"""
Test network connectivity to Google APIs
"""

import requests
import socket
import time

def test_google_connectivity():
    """Test connectivity to Google services"""
    
    print("🌐 Testing Network Connectivity to Google APIs")
    print("=" * 50)
    
    # Test basic connectivity
    test_urls = [
        "https://www.google.com",
        "https://accounts.google.com",
        "https://oauth2.googleapis.com",
        "https://www.googleapis.com",
        "https://drive.googleapis.com"
    ]
    
    for url in test_urls:
        try:
            print(f"Testing: {url}")
            response = requests.get(url, timeout=10)
            print(f"✅ {url} - Status: {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"❌ {url} - TIMEOUT")
        except requests.exceptions.ConnectionError as e:
            print(f"❌ {url} - CONNECTION ERROR: {e}")
        except Exception as e:
            print(f"❌ {url} - ERROR: {e}")
    
    # Test DNS resolution
    print(f"\n🔍 Testing DNS Resolution:")
    google_hosts = [
        "www.google.com",
        "accounts.google.com", 
        "oauth2.googleapis.com",
        "www.googleapis.com",
        "drive.googleapis.com"
    ]
    
    for host in google_hosts:
        try:
            ip = socket.gethostbyname(host)
            print(f"✅ {host} -> {ip}")
        except socket.gaierror as e:
            print(f"❌ {host} - DNS ERROR: {e}")
    
    # Test specific Google Drive API endpoint
    print(f"\n🔍 Testing Google Drive API Endpoint:")
    try:
        # Test the discovery endpoint
        url = "https://www.googleapis.com/discovery/v1/apis/drive/v3/rest"
        response = requests.get(url, timeout=15)
        print(f"✅ Drive API Discovery - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   API Name: {data.get('name')}")
            print(f"   API Version: {data.get('version')}")
            
    except Exception as e:
        print(f"❌ Drive API Discovery - ERROR: {e}")

def test_firewall_proxy():
    """Test for firewall/proxy issues"""
    
    print(f"\n🔧 Testing for Firewall/Proxy Issues:")
    
    # Test with different timeouts
    timeouts = [5, 10, 30]
    
    for timeout in timeouts:
        try:
            print(f"Testing with {timeout}s timeout...")
            response = requests.get("https://www.google.com", timeout=timeout)
            print(f"✅ Google.com reachable with {timeout}s timeout")
            break
        except requests.exceptions.Timeout:
            print(f"❌ Google.com timeout with {timeout}s")
        except Exception as e:
            print(f"❌ Google.com error with {timeout}s: {e}")

if __name__ == "__main__":
    test_google_connectivity()
    test_firewall_proxy()
    
    print(f"\n💡 Network Diagnosis:")
    print(f"1. If all tests fail -> Network/Firewall issue")
    print(f"2. If some tests pass -> Specific API issue")
    print(f"3. If DNS fails -> DNS/Network configuration issue")
    print(f"4. If timeouts -> Firewall blocking outbound connections")
