#!/usr/bin/env python3
"""
Simple test to see what's happening with indexing
"""

import requests
import time

def test_simple_index():
    print('🧪 Simple Index Test')
    print('=' * 20)
    
    try:
        # Test auth first
        print('1. Testing auth...')
        r = requests.get('http://127.0.0.1:8000/auth', timeout=10)
        if r.status_code != 200:
            print('❌ Auth failed')
            return
        print('✅ Auth OK')
        
        # Test indexing with very short timeout to see if it starts
        print('2. Testing indexing (10s timeout)...')
        start_time = time.time()
        try:
            r = requests.post('http://127.0.0.1:8000/index', timeout=10)
            print(f'✅ Indexing completed in {time.time() - start_time:.1f}s')
            print('Status:', r.status_code)
            if r.status_code == 200:
                data = r.json()
                print('Total images:', data.get('total_images', 0))
        except requests.exceptions.Timeout:
            print(f'⏰ Indexing timed out after {time.time() - start_time:.1f}s')
            print('   This means the indexing is taking too long')
        except Exception as e:
            print('❌ Indexing error:', str(e))
            
    except Exception as e:
        print('❌ Error:', str(e))

if __name__ == "__main__":
    test_simple_index()
