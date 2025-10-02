#!/usr/bin/env python3
"""
Test script for Google Drive AI Search API
Run this after starting the FastAPI server to test all endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:6000"

def test_health():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_auth():
    """Test authentication endpoint"""
    print("🔐 Testing authentication...")
    response = requests.get(f"{BASE_URL}/auth")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_index():
    """Test indexing endpoint"""
    print("📁 Testing Drive indexing...")
    response = requests.post(f"{BASE_URL}/index")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_search_semantic():
    """Test semantic search"""
    print("🔍 Testing semantic search...")
    payload = {
        "query": "modern kitchen",
        "top_k": 3
    }
    response = requests.post(f"{BASE_URL}/search", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_search_with_objects():
    """Test search with object requirements"""
    print("🪑 Testing search with objects...")
    payload = {
        "query": "bedroom design",
        "required_objects": ["bed", "lamp"],
        "top_k": 3
    }
    response = requests.post(f"{BASE_URL}/search", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_search_with_colors():
    """Test search with color requirements"""
    print("🎨 Testing search with colors...")
    payload = {
        "query": "living room",
        "required_colors": [[255, 0, 0], [0, 0, 255]],  # Red and Blue
        "top_k": 3
    }
    response = requests.post(f"{BASE_URL}/search", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_complex_search():
    """Test complex search with all features"""
    print("🚀 Testing complex search...")
    payload = {
        "query": "modern kitchen with island",
        "required_objects": ["island", "stove"],
        "required_colors": [[128, 0, 128]],  # Purple
        "top_k": 5
    }
    response = requests.post(f"{BASE_URL}/search", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_stats():
    """Test statistics endpoint"""
    print("📊 Testing statistics...")
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def main():
    """Run all tests"""
    print("🧪 Starting Google Drive AI Search API Tests")
    print("=" * 50)
    
    # Test health first
    test_health()
    
    # Test authentication
    test_auth()
    
    # Wait for user to complete OAuth if needed
    input("Press Enter after completing Google OAuth authentication...")
    
    # Test indexing
    test_index()
    
    # Wait a bit for indexing to complete
    print("⏳ Waiting for indexing to complete...")
    time.sleep(2)
    
    # Test various search scenarios
    test_search_semantic()
    test_search_with_objects()
    test_search_with_colors()
    test_complex_search()
    
    # Test statistics
    test_stats()
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()

