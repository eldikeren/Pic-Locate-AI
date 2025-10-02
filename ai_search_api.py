"""
AI Search API Endpoints for PicLocate
Integrates AI vision analysis with search functionality
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from ai_search_engine import AISearchEngine, ConversationalSearch, SearchResult
from supabase import create_client

# Initialize Supabase client
SUPABASE_URL = "https://gezmablgrepoaamtizts.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdlem1hYmxncmVwb2FhbXRpenRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxNzg2MzMsImV4cCI6MjA3NDc1NDYzM30.lJjaubEzeET8OwcHWJ_x_pOAXd8Bc1yDbpdvKianLM0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize AI Search Engine
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not found. AI search will not work.")
    ai_search_engine = None
    conversational_search = None
else:
    ai_search_engine = AISearchEngine(OPENAI_API_KEY, supabase)
    conversational_search = ConversationalSearch(ai_search_engine)

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 20
    context: Optional[List[str]] = None

class SearchResponse(BaseModel):
    query: str
    enhanced_query: Optional[str] = None
    results: List[Dict[str, Any]]
    total_results: int
    response: str
    processing_time: float

class ImageAnalysisRequest(BaseModel):
    image_id: str
    analysis_prompt: str

class ImageAnalysisResponse(BaseModel):
    image_id: str
    analysis: str
    room_type: str
    objects_detected: List[str]
    colors: List[str]
    style: str
    confidence: float

@router.post("/search/ai", response_model=SearchResponse)
async def ai_search(request: SearchRequest):
    """
    AI-powered search that analyzes images and provides intelligent results
    
    This endpoint uses AI vision models to understand images and match them
    to natural language queries, similar to how ChatGPT analyzes uploaded images.
    """
    if not ai_search_engine:
        raise HTTPException(status_code=503, detail="AI search not available - OpenAI API key required")
    
    import time
    start_time = time.time()
    
    try:
        if request.context:
            # Conversational search with context
            result = conversational_search.search_conversation(request.query, request.context)
            results = [result_to_dict(r) for r in result['results']]
            enhanced_query = result['enhanced_query']
            response_text = result['response']
        else:
            # Direct AI search
            results_objects = ai_search_engine.search_with_ai(request.query, request.limit)
            results = [result_to_dict(r) for r in results_objects]
            enhanced_query = None
            response_text = f"Found {len(results)} images matching your query"
        
        processing_time = time.time() - start_time
        
        return SearchResponse(
            query=request.query,
            enhanced_query=enhanced_query,
            results=results,
            total_results=len(results),
            response=response_text,
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI search failed: {str(e)}")

@router.post("/search/analyze", response_model=ImageAnalysisResponse)
async def analyze_image(request: ImageAnalysisRequest):
    """
    Analyze a specific image with AI vision model
    
    This endpoint provides detailed AI analysis of a single image,
    similar to uploading an image to ChatGPT for analysis.
    """
    if not ai_search_engine:
        raise HTTPException(status_code=503, detail="AI analysis not available - OpenAI API key required")
    
    try:
        # Get image data from database
        image_result = supabase.table("images").select("*").eq("id", request.image_id).execute()
        if not image_result.data:
            raise HTTPException(status_code=404, detail="Image not found")
        
        image_data = image_result.data[0]
        
        # Analyze with AI
        analysis = ai_search_engine._analyze_image_with_ai(image_data, request.analysis_prompt)
        
        return ImageAnalysisResponse(
            image_id=request.image_id,
            analysis=analysis.get('analysis', 'Analysis failed'),
            room_type=analysis.get('room_type', 'unknown'),
            objects_detected=analysis.get('objects_detected', []),
            colors=analysis.get('colors', []),
            style=analysis.get('style', 'unknown'),
            confidence=analysis.get('confidence', 0)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

@router.get("/search/suggestions")
async def get_search_suggestions(q: str = Query("", description="Partial query for suggestions")):
    """
    Get AI-powered search suggestions based on partial query
    """
    if not q:
        return {"suggestions": []}
    
    # Get suggestions from database based on common queries
    try:
        # Get popular room types
        room_result = supabase.table("images").select("room_type").execute()
        room_types = list(set([r['room_type'] for r in room_result.data if r['room_type']]))
        
        # Get popular objects
        object_result = supabase.table("image_objects").select("label").execute()
        objects = list(set([r['label'] for r in object_result.data if r['label']]))
        
        # Get popular colors
        color_result = supabase.table("image_objects").select("color_name").execute()
        colors = list(set([r['color_name'] for r in color_result.data if r['color_name']]))
        
        # Filter suggestions based on query
        suggestions = []
        query_lower = q.lower()
        
        for room in room_types:
            if query_lower in room.lower():
                suggestions.append(f"Show me {room}s")
        
        for obj in objects[:10]:  # Top 10 objects
            if query_lower in obj.lower():
                suggestions.append(f"Find {obj}s")
        
        for color in colors[:5]:  # Top 5 colors
            if query_lower in color.lower():
                suggestions.append(f"Show me {color} items")
        
        return {"suggestions": suggestions[:10]}
        
    except Exception as e:
        return {"suggestions": []}

@router.get("/search/trending")
async def get_trending_searches():
    """
    Get trending search queries and popular content
    """
    try:
        # Get most common room types
        room_result = supabase.table("images").select("room_type").execute()
        room_counts = {}
        for r in room_result.data:
            room = r['room_type']
            room_counts[room] = room_counts.get(room, 0) + 1
        
        trending_rooms = sorted(room_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Get most common objects
        object_result = supabase.table("image_objects").select("label").execute()
        object_counts = {}
        for r in object_result.data:
            obj = r['label']
            object_counts[obj] = object_counts.get(obj, 0) + 1
        
        trending_objects = sorted(object_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "trending_rooms": [{"room": room, "count": count} for room, count in trending_rooms],
            "trending_objects": [{"object": obj, "count": count} for obj, count in trending_objects],
            "total_images": len(room_result.data)
        }
        
    except Exception as e:
        return {"trending_rooms": [], "trending_objects": [], "total_images": 0}

def result_to_dict(result: SearchResult) -> Dict[str, Any]:
    """Convert SearchResult to dictionary for JSON response"""
    return {
        "image_id": result.image_id,
        "file_name": result.file_name,
        "folder_path": result.folder_path,
        "ai_analysis": result.ai_analysis,
        "relevance_score": result.relevance_score,
        "match_reasons": result.match_reasons,
        "room_type": result.room_type,
        "objects_detected": result.objects_detected,
        "colors": result.colors,
        "style": result.style,
        "confidence": result.confidence
    }

# Health check endpoint
@router.get("/search/health")
async def search_health():
    """Check if AI search is available"""
    return {
        "ai_search_available": ai_search_engine is not None,
        "openai_configured": OPENAI_API_KEY is not None,
        "supabase_connected": True
    }
