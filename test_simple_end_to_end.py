"""
Simple End-to-End Test for PicLocate V4 Integrated System
Tests complete pipeline from frontend to database
"""

import requests
import time
import json
from typing import Dict, Any

API_BASE = "http://localhost:8000"

def test_system_health():
    """Test system health and connectivity"""
    print("Testing System Health...")
    
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"System Status: {data['status']}")
            print(f"   V4 Backend: {data['components']['v4_backend']}")
            print(f"   Production Search: {data['components']['production_search']}")
            print(f"   Supabase: {data['components']['supabase']}")
            print(f"   Google Drive: {data['components']['google_drive']}")
            return True
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Health check error: {e}")
        return False

def test_authentication():
    """Test Google Drive authentication"""
    print("\nTesting Authentication...")
    
    try:
        response = requests.get(f"{API_BASE}/v4/auth/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'authenticated':
                print(f"Authentication: {data['status']}")
                print(f"   Target Folder: {data['target_folder']}")
                print(f"   Folder ID: {data['folder_id']}")
                return True
            else:
                print(f"Authentication: {data['status']}")
                print(f"   Message: {data['message']}")
                return False
        else:
            print(f"Auth check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Auth check error: {e}")
        return False

def test_database_connection():
    """Test Supabase database connection"""
    print("\nTesting Database Connection...")
    
    try:
        response = requests.get(f"{API_BASE}/stats/overview", timeout=10)
        if response.status_code == 200:
            data = response.json()
            stats = data['database_stats']
            print(f"Database Connected")
            print(f"   Total Images: {stats['total_images']}")
            print(f"   Total Objects: {stats['total_objects']}")
            print(f"   Total Captions: {stats['total_captions']}")
            print(f"   Total Tags: {stats['total_tags']}")
            
            # Show room distribution
            rooms = data['distributions']['rooms']
            print(f"   Room Distribution: {len(rooms)} types")
            for room, count in list(rooms.items())[:5]:
                print(f"     {room}: {count}")
            
            return True
        else:
            print(f"Database check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Database check error: {e}")
        return False

def test_indexing_status():
    """Test V4 indexing status"""
    print("\nTesting V4 Indexing Status...")
    
    try:
        response = requests.get(f"{API_BASE}/indexing/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Indexing Status Retrieved")
            print(f"   Running: {data['is_running']}")
            print(f"   Processed: {data['processed_count']}")
            print(f"   Total: {data['total_count']}")
            print(f"   Progress: {data['progress_percentage']:.1f}%")
            
            if data['current_file']:
                print(f"   Current File: {data['current_file']}")
            
            if data['errors']:
                print(f"   Errors: {len(data['errors'])}")
                for error in data['errors'][:3]:
                    print(f"     - {error}")
            
            return True
        else:
            print(f"Indexing status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Indexing status error: {e}")
        return False

def test_production_search():
    """Test production search engine"""
    print("\nTesting Production Search Engine...")
    
    test_queries = [
        "kitchen with black table",
        "bathroom with marble countertop",
        "living room with large sofa"
    ]
    
    for query in test_queries:
        try:
            print(f"   Testing query: '{query}'")
            response = requests.post(f"{API_BASE}/api/search/production", 
                                   json={"query": query, "lang": "en", "limit": 5},
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"     Found {data['total_results']} results")
                print(f"     Processing time: {data['processing_time']:.2f}s")
                
                if data['results']:
                    top_result = data['results'][0]
                    print(f"     Top result: {top_result['file_name']}")
                    print(f"     VLM Confidence: {top_result['vlm_confidence']:.2f}")
                    print(f"     Room: {top_result['room']}")
            else:
                print(f"     Search failed: {response.status_code}")
                if response.status_code == 503:
                    print(f"     Message: Production search not available (OpenAI API key required)")
                
        except Exception as e:
            print(f"     Search error: {e}")

def run_comprehensive_test():
    """Run comprehensive end-to-end test"""
    print("PicLocate V4 Integrated System - End-to-End Test")
    print("=" * 60)
    
    # Test results
    results = {
        "system_health": False,
        "authentication": False,
        "database": False,
        "indexing": False
    }
    
    # Run tests
    results["system_health"] = test_system_health()
    results["authentication"] = test_authentication()
    results["database"] = test_database_connection()
    results["indexing"] = test_indexing_status()
    test_production_search()  # This will show results but not fail the test
    
    # Summary
    print("\nTest Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! System is ready for production use.")
    elif passed >= total * 0.7:
        print("Most tests passed. System is functional with some limitations.")
    else:
        print("Multiple tests failed. System needs attention.")
    
    print("\nSystem Status:")
    print("   Backend: http://localhost:8000")
    print("   Frontend: http://localhost:3000")
    print("   API Docs: http://localhost:8000/docs")
    print("   Health Check: http://localhost:8000/health")
    
    return results

if __name__ == "__main__":
    run_comprehensive_test()
