"""
AI-First Search Engine for PicLocate
Uses AI vision models to analyze images and provide intelligent search results
"""

import requests
import base64
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import openai
from PIL import Image
import io

@dataclass
class SearchResult:
    """Search result with AI analysis"""
    image_id: str
    file_name: str
    folder_path: str
    ai_analysis: str
    relevance_score: float
    match_reasons: List[str]
    room_type: str
    objects_detected: List[str]
    colors: List[str]
    style: str
    confidence: float

class AISearchEngine:
    """AI-powered search engine that analyzes images like ChatGPT"""
    
    def __init__(self, openai_api_key: str, supabase_client):
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.supabase = supabase_client
        self.vision_model = "gpt-4o"  # Latest vision model
        
    def search_with_ai(self, query: str, limit: int = 20) -> List[SearchResult]:
        """
        AI-powered search that analyzes images and provides intelligent results
        
        Args:
            query: Natural language search query
            limit: Maximum number of results
            
        Returns:
            List of SearchResult objects with AI analysis
        """
        print(f"🔍 AI Search: '{query}'")
        
        # Step 1: Get candidate images from database
        candidates = self._get_candidate_images(query, limit * 3)  # Get 3x for AI filtering
        
        if not candidates:
            return []
        
        # Step 2: AI analyzes each candidate image
        results = []
        for candidate in candidates[:limit * 2]:  # Analyze top candidates
            try:
                ai_analysis = self._analyze_image_with_ai(candidate, query)
                if ai_analysis['relevant']:
                    result = SearchResult(
                        image_id=candidate['id'],
                        file_name=candidate['file_name'],
                        folder_path=candidate['folder_path'],
                        ai_analysis=ai_analysis['analysis'],
                        relevance_score=ai_analysis['relevance_score'],
                        match_reasons=ai_analysis['match_reasons'],
                        room_type=ai_analysis['room_type'],
                        objects_detected=ai_analysis['objects_detected'],
                        colors=ai_analysis['colors'],
                        style=ai_analysis['style'],
                        confidence=ai_analysis['confidence']
                    )
                    results.append(result)
            except Exception as e:
                print(f"Error analyzing image {candidate['file_name']}: {e}")
                continue
        
        # Step 3: Sort by AI relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]
    
    def _get_candidate_images(self, query: str, limit: int) -> List[Dict]:
        """Get candidate images from database using basic filters"""
        try:
            # Extract basic keywords from query
            keywords = self._extract_keywords(query)
            
            # Build SQL query with basic filters
            where_conditions = []
            params = {}
            
            # Room type filter
            room_keywords = ['kitchen', 'bathroom', 'bedroom', 'living room', 'dining room', 'office']
            for room in room_keywords:
                if room in query.lower():
                    where_conditions.append("room_type = :room_type")
                    params['room_type'] = room.replace(' ', '_')
                    break
            
            # Object filter
            object_keywords = ['table', 'chair', 'sofa', 'bed', 'sink', 'toilet', 'tv', 'refrigerator']
            for obj in object_keywords:
                if obj in query.lower():
                    where_conditions.append("EXISTS (SELECT 1 FROM image_objects WHERE image_id = images.id AND label ILIKE :object_label)")
                    params['object_label'] = f'%{obj}%'
                    break
            
            # Build final query
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            query_sql = f"""
                SELECT id, file_name, folder_path, room_type, width, height
                FROM images 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT {limit}
            """
            
            result = self.supabase.rpc('execute_sql', {
                'query': query_sql,
                'params': params
            }).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error getting candidate images: {e}")
            return []
    
    def _analyze_image_with_ai(self, image_data: Dict, query: str) -> Dict[str, Any]:
        """
        Use AI vision model to analyze image and determine relevance to query
        
        This is the core AI analysis - like ChatGPT analyzing an uploaded image
        """
        try:
            # Get image from Google Drive
            image_url = self._get_image_url(image_data['id'])
            if not image_url:
                return {'relevant': False, 'analysis': 'Could not load image'}
            
            # Prepare AI prompt
            prompt = f"""
            Analyze this image and determine if it's relevant to the search query: "{query}"
            
            Please provide:
            1. Is this image relevant to the query? (yes/no)
            2. If yes, what makes it relevant?
            3. What room type is this? (kitchen, bathroom, bedroom, living_room, dining_room, office, etc.)
            4. What objects do you see?
            5. What are the main colors?
            6. What style is this? (modern, traditional, industrial, etc.)
            7. Relevance score (0-100)
            8. Confidence in your analysis (0-100)
            
            Respond in JSON format:
            {{
                "relevant": true/false,
                "analysis": "detailed description",
                "room_type": "room_name",
                "objects_detected": ["object1", "object2"],
                "colors": ["color1", "color2"],
                "style": "style_name",
                "relevance_score": 85,
                "confidence": 90,
                "match_reasons": ["reason1", "reason2"]
            }}
            """
            
            # Call OpenAI Vision API
            response = self.openai_client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url}
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            try:
                analysis = json.loads(ai_response)
                return analysis
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    'relevant': 'yes' in ai_response.lower(),
                    'analysis': ai_response,
                    'room_type': 'unknown',
                    'objects_detected': [],
                    'colors': [],
                    'style': 'unknown',
                    'relevance_score': 50,
                    'confidence': 50,
                    'match_reasons': ['AI analysis completed']
                }
                
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return {'relevant': False, 'analysis': f'Error: {str(e)}'}
    
    def _get_image_url(self, image_id: str) -> Optional[str]:
        """Get public URL for image from Google Drive"""
        try:
            # This would need to be implemented based on your Google Drive setup
            # For now, return a placeholder
            return f"https://drive.google.com/uc?id={image_id}"
        except Exception as e:
            print(f"Error getting image URL: {e}")
            return None
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from search query"""
        # Simple keyword extraction
        keywords = []
        
        # Room types
        room_types = ['kitchen', 'bathroom', 'bedroom', 'living room', 'dining room', 'office']
        for room in room_types:
            if room in query.lower():
                keywords.append(room)
        
        # Objects
        objects = ['table', 'chair', 'sofa', 'bed', 'sink', 'toilet', 'tv', 'refrigerator', 'oven', 'stove']
        for obj in objects:
            if obj in query.lower():
                keywords.append(obj)
        
        # Colors
        colors = ['black', 'white', 'gray', 'brown', 'blue', 'green', 'red', 'yellow']
        for color in colors:
            if color in query.lower():
                keywords.append(color)
        
        return keywords

class ConversationalSearch:
    """Enable conversational search with AI understanding"""
    
    def __init__(self, ai_search_engine: AISearchEngine):
        self.ai_search = ai_search_engine
        
    def search_conversation(self, query: str, context: List[str] = None) -> Dict[str, Any]:
        """
        Handle conversational search with context awareness
        
        Args:
            query: Current search query
            context: Previous queries/results for context
            
        Returns:
            Search results with conversational context
        """
        # Enhance query with context
        enhanced_query = self._enhance_query_with_context(query, context)
        
        # Get AI search results
        results = self.ai_search.search_with_ai(enhanced_query)
        
        # Generate conversational response
        response = self._generate_conversational_response(query, results)
        
        return {
            'query': query,
            'enhanced_query': enhanced_query,
            'results': results,
            'response': response,
            'context': context
        }
    
    def _enhance_query_with_context(self, query: str, context: List[str]) -> str:
        """Enhance query with conversational context"""
        if not context:
            return query
        
        context_str = " ".join(context[-3:])  # Last 3 queries
        return f"{context_str} {query}"
    
    def _generate_conversational_response(self, query: str, results: List[SearchResult]) -> str:
        """Generate natural language response about search results"""
        if not results:
            return f"I couldn't find any images matching '{query}'. Try different keywords or be more specific."
        
        top_result = results[0]
        response = f"I found {len(results)} images matching '{query}'. "
        
        if top_result.relevance_score > 80:
            response += f"The best match is {top_result.file_name} - it shows a {top_result.room_type} with {', '.join(top_result.objects_detected[:3])}. "
        else:
            response += f"The closest match is {top_result.file_name} - it's a {top_result.room_type}. "
        
        response += f"Confidence: {top_result.confidence}%"
        return response

# Example usage and testing
def test_ai_search():
    """Test the AI search functionality"""
    print("Testing AI Search Engine...")
    
    # This would be initialized with actual API keys and Supabase client
    # ai_search = AISearchEngine(openai_api_key="your-key", supabase_client=supabase)
    
    test_queries = [
        "Show me modern kitchens with black appliances",
        "Find bathrooms with marble countertops",
        "I need a living room with a large sofa",
        "Show me bedrooms with wooden furniture",
        "Find images with blue colors"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        # results = ai_search.search_with_ai(query)
        # print(f"Found {len(results)} results")
        # if results:
        #     print(f"Top result: {results[0].file_name} (score: {results[0].relevance_score})")

if __name__ == "__main__":
    test_ai_search()
