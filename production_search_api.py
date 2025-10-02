"""
Production Search API Endpoints
Implements retrieval + verification pipeline with AI final verdict
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import time
from production_search_engine import ProductionSearchEngine, FinalResult
from supabase import create_client

# Initialize Supabase client
SUPABASE_URL = "https://gezmablgrepoaamtizts.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdlem1hYmxncmVwb2FhbXRpenRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxNzg2MzMsImV4cCI6MjA3NDc1NDYzM30.lJjaubEzeET8OwcHWJ_x_pOAXd8Bc1yDbpdvKianLM0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Production Search Engine
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not found. Production search will not work.")
    search_engine = None
else:
    search_engine = ProductionSearchEngine(OPENAI_API_KEY, supabase)

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    lang: Optional[str] = "en"  # he|en
    limit: Optional[int] = 24
    top_k: Optional[int] = 120  # Candidates from Stage A

class SearchResponse(BaseModel):
    query: str
    lang: str
    results: List[Dict[str, Any]]
    total_results: int
    processing_time: float
    stage_a_candidates: int
    stage_b_verified: int
    stage_c_final: int

class ImageAnalysisRequest(BaseModel):
    image_id: str
    analysis_prompt: str

class ImageAnalysisResponse(BaseModel):
    image_id: str
    analysis: str
    room: str
    evidence: Dict[str, Any]
    confidence: float
    notes: str

@router.post("/search/production", response_model=SearchResponse)
async def production_search(request: SearchRequest):
    """
    Production search with AI final verdict
    
    This endpoint implements the retrieval + verification pipeline:
    1. Stage A: Fast candidate retrieval (SQL + pgvector)
    2. Stage B: VLM verification with AI looking at pixels
    3. Stage C: Re-rank and filter by AI confidence
    
    Returns only images that the AI confirms match the query.
    """
    if not search_engine:
        raise HTTPException(status_code=503, detail="Production search not available - OpenAI API key required")
    
    start_time = time.time()
    
    try:
        # Update search engine configuration
        search_engine.TOP_K = request.top_k
        search_engine.FINAL_LIMIT = request.limit
        
        # Perform search
        results = await search_engine.search(
            query=request.query,
            lang=request.lang,
            limit=request.limit
        )
        
        processing_time = time.time() - start_time
        
        # Convert results to response format
        results_data = [result_to_dict(r) for r in results]
        
        return SearchResponse(
            query=request.query,
            lang=request.lang,
            results=results_data,
            total_results=len(results),
            processing_time=processing_time,
            stage_a_candidates=request.top_k,  # This would be actual count from search engine
            stage_b_verified=len(results),  # This would be actual count from search engine
            stage_c_final=len(results)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Production search failed: {str(e)}")

@router.post("/search/analyze", response_model=ImageAnalysisResponse)
async def analyze_single_image(request: ImageAnalysisRequest):
    """
    Analyze a single image with AI vision model
    
    This endpoint provides detailed AI analysis of a specific image,
    similar to uploading an image to ChatGPT for analysis.
    """
    if not search_engine:
        raise HTTPException(status_code=503, detail="AI analysis not available - OpenAI API key required")
    
    try:
        # Get image data from database
        image_result = supabase.table("images").select("*").eq("id", request.image_id).execute()
        if not image_result.data:
            raise HTTPException(status_code=404, detail="Image not found")
        
        image_data = image_result.data[0]
        
        # Get signed URL
        signed_url = await search_engine._get_signed_url(request.image_id)
        if not signed_url:
            raise HTTPException(status_code=500, detail="Could not get image URL")
        
        # Create candidate for analysis
        from production_search_engine import CandidateImage
        candidate = CandidateImage(
            id=request.image_id,
            file_name=image_data['file_name'],
            folder_path=image_data['folder_path'],
            room_type=image_data.get('room_type', 'unknown'),
            room_confidence=image_data.get('room_confidence', 0.0),
            sem_score=0.0,
            signed_url=signed_url
        )
        
        # Analyze with VLM
        verdicts = await search_engine._verify_batch(request.analysis_prompt, [candidate])
        
        if not verdicts:
            raise HTTPException(status_code=500, detail="AI analysis failed")
        
        verdict = verdicts[0]
        
        return ImageAnalysisResponse(
            image_id=request.image_id,
            analysis=verdict.notes,
            room=verdict.room,
            evidence=verdict.evidence,
            confidence=verdict.confidence,
            notes=verdict.notes
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
    
    try:
        # Get suggestions from database
        room_result = supabase.table("images").select("room_type").execute()
        room_types = list(set([r['room_type'] for r in room_result.data if r['room_type']]))
        
        object_result = supabase.table("image_objects").select("label").execute()
        objects = list(set([r['label'] for r in object_result.data if r['label']]))
        
        color_result = supabase.table("image_objects").select("color_name").execute()
        colors = list(set([r['color_name'] for r in color_result.data if r['color_name']]))
        
        # Filter suggestions based on query
        suggestions = []
        query_lower = q.lower()
        
        # Room suggestions
        for room in room_types:
            if query_lower in room.lower():
                suggestions.append(f"Show me {room}s")
        
        # Object suggestions
        for obj in objects[:10]:
            if query_lower in obj.lower():
                suggestions.append(f"Find {obj}s")
        
        # Color suggestions
        for color in colors[:5]:
            if query_lower in color.lower():
                suggestions.append(f"Show me {color} items")
        
        # Hebrew suggestions
        hebrew_suggestions = [
            "מטבח עם שולחן שחור",
            "סלון עם ספה גדולה",
            "שירותים עם שיש",
            "חדר שינה עם מיטה",
            "משרד עם שולחן עבודה"
        ]
        
        for he_suggestion in hebrew_suggestions:
            if any(word in q for word in he_suggestion.split()):
                suggestions.append(he_suggestion)
        
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
        
        # Get most common colors
        color_result = supabase.table("image_objects").select("color_name").execute()
        color_counts = {}
        for r in color_result.data:
            color = r['color_name']
            if color:
                color_counts[color] = color_counts.get(color, 0) + 1
        
        trending_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "trending_rooms": [{"room": room, "count": count} for room, count in trending_rooms],
            "trending_objects": [{"object": obj, "count": count} for obj, count in trending_objects],
            "trending_colors": [{"color": color, "count": count} for color, count in trending_colors],
            "total_images": len(room_result.data)
        }
        
    except Exception as e:
        return {"trending_rooms": [], "trending_objects": [], "trending_colors": [], "total_images": 0}

@router.get("/search/stats")
async def get_search_stats():
    """
    Get search engine statistics and performance metrics
    """
    try:
        # Get database stats
        image_count = supabase.table("images").select("id", count="exact").execute().count
        object_count = supabase.table("image_objects").select("id", count="exact").execute().count
        caption_count = supabase.table("image_captions").select("id", count="exact").execute().count
        
        # Get room type distribution
        room_result = supabase.table("images").select("room_type").execute()
        room_distribution = {}
        for r in room_result.data:
            room = r['room_type']
            room_distribution[room] = room_distribution.get(room, 0) + 1
        
        return {
            "total_images": image_count,
            "total_objects": object_count,
            "total_captions": caption_count,
            "room_distribution": room_distribution,
            "search_engine_available": search_engine is not None,
            "openai_configured": OPENAI_API_KEY is not None,
            "supabase_connected": True
        }
        
    except Exception as e:
        return {
            "total_images": 0,
            "total_objects": 0,
            "total_captions": 0,
            "room_distribution": {},
            "search_engine_available": False,
            "openai_configured": False,
            "supabase_connected": False,
            "error": str(e)
        }

def result_to_dict(result: FinalResult) -> Dict[str, Any]:
    """Convert FinalResult to dictionary for JSON response"""
    return {
        "image_id": result.image_id,
        "file_name": result.file_name,
        "folder_path": result.folder_path,
        "vlm_confidence": result.vlm_confidence,
        "retrieval_score": result.retrieval_score,
        "final_score": result.final_score,
        "room": result.room,
        "evidence": result.evidence,
        "match_reasons": result.match_reasons,
        "ai_notes": result.ai_notes,
        "confidence_badge": get_confidence_badge(result.vlm_confidence)
    }

def get_confidence_badge(confidence: float) -> str:
    """Get confidence badge color based on confidence score"""
    if confidence >= 0.9:
        return "green"  # High confidence
    elif confidence >= 0.7:
        return "yellow"  # Medium confidence
    else:
        return "red"  # Low confidence

# Health check endpoint
@router.get("/search/health")
async def search_health():
    """Check if production search is available"""
    return {
        "production_search_available": search_engine is not None,
        "openai_configured": OPENAI_API_KEY is not None,
        "supabase_connected": True,
        "vlm_model": "gpt-4o-mini" if search_engine else None,
        "cache_enabled": True if search_engine else False
    }
