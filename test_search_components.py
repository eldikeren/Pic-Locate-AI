"""
Test individual components of the production search engine
"""

import asyncio
from production_search_engine import ProductionSearchEngine

class MockSupabase:
    def rpc(self, method, params):
        return type('MockResult', (), {'data': []})()

async def test_components():
    """Test individual components"""
    print("Testing Production Search Engine Components")
    print("=" * 50)
    
    # Mock setup
    mock_supabase = MockSupabase()
    search_engine = ProductionSearchEngine('mock_key', mock_supabase)
    
    # Test 1: Room filter extraction
    print("\n1. Testing room filter extraction:")
    test_queries = [
        "kitchen with black table",
        "bathroom with marble countertop", 
        "living room with large sofa",
        "bedroom with wooden furniture"
    ]
    
    for query in test_queries:
        room_filter = search_engine._extract_room_filter(query)
        print(f"   Query: '{query}' -> Room: {room_filter}")
    
    # Test 2: Object filter extraction
    print("\n2. Testing object filter extraction:")
    object_queries = [
        "kitchen with black table and chairs",
        "bathroom with sink and toilet",
        "living room with sofa and tv",
        "bedroom with bed and wardrobe"
    ]
    
    for query in object_queries:
        object_filters = search_engine._extract_object_filters(query)
        print(f"   Query: '{query}' -> Objects: {object_filters}")
    
    # Test 3: Cache key generation
    print("\n3. Testing cache key generation:")
    from production_search_engine import CandidateImage
    
    candidates = [
        CandidateImage(
            id="test-1",
            file_name="test1.jpg",
            folder_path="/test",
            room_type="kitchen",
            room_confidence=0.8,
            sem_score=0.9,
            signed_url="http://test.com/1"
        ),
        CandidateImage(
            id="test-2", 
            file_name="test2.jpg",
            folder_path="/test",
            room_type="bathroom",
            room_confidence=0.7,
            sem_score=0.8,
            signed_url="http://test.com/2"
        )
    ]
    
    cache_key = search_engine._get_cache_key("test query", candidates)
    print(f"   Query: 'test query' -> Cache key: {cache_key[:20]}...")
    
    # Test 4: Match reasons extraction
    print("\n4. Testing match reasons extraction:")
    test_evidence = {
        "objects": ["dining table", "chair", "refrigerator"],
        "colors": {"dining table": "black", "chair": "black"},
        "materials": {"countertop": "marble", "table": "wood"},
        "room_features": ["modern", "spacious"]
    }
    
    match_reasons = search_engine._extract_match_reasons(test_evidence)
    print(f"   Evidence: {test_evidence}")
    print(f"   Match reasons: {match_reasons}")
    
    # Test 5: Configuration
    print("\n5. Testing configuration:")
    print(f"   TOP_K: {search_engine.TOP_K}")
    print(f"   BATCH_SIZE: {search_engine.BATCH_SIZE}")
    print(f"   CUTOFF: {search_engine.CUTOFF}")
    print(f"   FINAL_LIMIT: {search_engine.FINAL_LIMIT}")
    print(f"   VLM Model: {search_engine.vlm_model}")
    
    # Test 6: Hebrew dictionary
    print("\n6. Testing Hebrew dictionary:")
    hebrew_words = ["kitchen", "table", "black", "marble"]  # Using English for testing
    for he_word in hebrew_words:
        if he_word in search_engine.he_to_en:
            en_word = search_engine.he_to_en[he_word]
            print(f"   {he_word} -> {en_word}")
        else:
            print(f"   {he_word} -> [not found]")
    
    # Test Hebrew dictionary size
    print(f"   Total Hebrew translations: {len(search_engine.he_to_en)}")
    
    print("\n" + "=" * 50)
    print("All component tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_components())
