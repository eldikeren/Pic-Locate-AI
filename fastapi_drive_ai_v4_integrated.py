"""
Integrated V4 Backend with Production Search Engine
Combines V4 indexing with AI-first search capabilities
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import V4 components
from fastapi_drive_ai_v4_production import (
    app as v4_app,
    drive_service,
    TARGET_FOLDER_ID,
    TARGET_FOLDER_NAME,
    SCOPES
)

# Import production search engine
from production_search_engine import ProductionSearchEngine
from production_search_api import (
    router as search_router,
    SearchRequest,
    SearchResponse,
    ImageAnalysisRequest,
    ImageAnalysisResponse
)

# Import Supabase client
from supabase import create_client

# Initialize Supabase
SUPABASE_URL = "https://gezmablgrepoaamtizts.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdlem1hYmxncmVwb2FhbXRpenRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxNzg2MzMsImV4cCI6MjA3NDc1NDYzM30.lJjaubEzeET8OwcHWJ_x_pOAXd8Bc1yDbpdvKianLM0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize production search engine
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    production_search = ProductionSearchEngine(OPENAI_API_KEY, supabase)
    print("✅ Production search engine initialized")
else:
    production_search = None
    print("⚠️ Production search engine not available - OPENAI_API_KEY required")

# Create integrated FastAPI app
app = FastAPI(
    title="PicLocate V4 Integrated",
    description="V4 indexing + AI-first search engine",
    version="4.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:4000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include V4 routes
app.include_router(v4_app.router, prefix="/v4")

# Include production search routes
app.include_router(search_router, prefix="/api")

# Global variables for indexing status
indexing_status = {
    "is_running": False,
    "started_at": None,
    "processed_count": 0,
    "total_count": 0,
    "current_file": None,
    "errors": []
}

class IndexingStatusResponse(BaseModel):
    is_running: bool
    started_at: Optional[str]
    processed_count: int
    total_count: int
    current_file: Optional[str]
    errors: List[str]
    progress_percentage: float

@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "app": "PicLocate V4 Integrated",
        "version": "4.0.0",
        "status": "running",
        "features": {
            "v4_indexing": True,
            "production_search": production_search is not None,
            "supabase_connected": True
        },
        "endpoints": {
            "v4_indexing": "/v4/index",
            "production_search": "/api/search/production",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    try:
        # Check Supabase connection
        supabase_status = "connected"
        try:
            result = supabase.table("images").select("id").limit(1).execute()
        except Exception as e:
            supabase_status = f"error: {str(e)}"
        
        # Check Google Drive connection
        drive_status = "connected" if drive_service else "not_connected"
        
        # Check production search
        search_status = "available" if production_search else "unavailable"
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "supabase": supabase_status,
                "google_drive": drive_status,
                "production_search": search_status,
                "v4_backend": "running"
            },
            "indexing": indexing_status
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/indexing/status", response_model=IndexingStatusResponse)
async def get_indexing_status():
    """Get current indexing status"""
    progress = 0.0
    if indexing_status["total_count"] > 0:
        progress = (indexing_status["processed_count"] / indexing_status["total_count"]) * 100
    
    return IndexingStatusResponse(
        is_running=indexing_status["is_running"],
        started_at=indexing_status["started_at"],
        processed_count=indexing_status["processed_count"],
        total_count=indexing_status["total_count"],
        current_file=indexing_status["current_file"],
        errors=indexing_status["errors"],
        progress_percentage=progress
    )

@app.post("/indexing/start")
async def start_indexing():
    """Start V4 indexing process"""
    global indexing_status
    
    if indexing_status["is_running"]:
        return {"status": "already_running", "message": "Indexing is already in progress"}
    
    try:
        # Update status
        indexing_status.update({
            "is_running": True,
            "started_at": datetime.utcnow().isoformat(),
            "processed_count": 0,
            "total_count": 0,
            "current_file": None,
            "errors": []
        })
        
        # Start indexing in background
        asyncio.create_task(run_indexing_process())
        
        return {
            "status": "started",
            "message": "V4 indexing process started",
            "started_at": indexing_status["started_at"]
        }
        
    except Exception as e:
        indexing_status["is_running"] = False
        return {"status": "error", "error": str(e)}

async def run_indexing_process():
    """Run the V4 indexing process"""
    global indexing_status
    
    try:
        print("🚀 Starting V4 indexing process...")
        
        # Import V4 indexing function
        from fastapi_drive_ai_v4_production import crawl_drive_images
        
        # Start crawling
        await crawl_drive_images(drive_service, max_images=999999)
        
        print("✅ V4 indexing completed successfully!")
        
    except Exception as e:
        print(f"❌ V4 indexing failed: {e}")
        indexing_status["errors"].append(str(e))
    finally:
        indexing_status["is_running"] = False

@app.get("/stats/overview")
async def get_system_overview():
    """Get comprehensive system statistics"""
    try:
        # Get database stats
        image_count = supabase.table("images").select("id", count="exact").execute().count
        object_count = supabase.table("image_objects").select("id", count="exact").execute().count
        caption_count = supabase.table("image_captions").select("id", count="exact").execute().count
        tag_count = supabase.table("image_tags").select("id", count="exact").execute().count
        
        # Get room distribution
        room_result = supabase.table("images").select("room_type").execute()
        room_distribution = {}
        for r in room_result.data:
            room = r['room_type']
            room_distribution[room] = room_distribution.get(room, 0) + 1
        
        # Get object distribution
        object_result = supabase.table("image_objects").select("label").execute()
        object_distribution = {}
        for r in object_result.data:
            obj = r['label']
            object_distribution[obj] = object_distribution.get(obj, 0) + 1
        
        # Get color distribution
        color_result = supabase.table("image_objects").select("color_name").execute()
        color_distribution = {}
        for r in color_result.data:
            color = r['color_name']
            if color:
                color_distribution[color] = color_distribution.get(color, 0) + 1
        
        return {
            "database_stats": {
                "total_images": image_count,
                "total_objects": object_count,
                "total_captions": caption_count,
                "total_tags": tag_count
            },
            "distributions": {
                "rooms": room_distribution,
                "objects": dict(sorted(object_distribution.items(), key=lambda x: x[1], reverse=True)[:10]),
                "colors": dict(sorted(color_distribution.items(), key=lambda x: x[1], reverse=True)[:10])
            },
            "system_status": {
                "v4_backend": "running",
                "production_search": "available" if production_search else "unavailable",
                "indexing": indexing_status
            }
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/search/demo")
async def search_demo():
    """Demo endpoint showing search capabilities"""
    if not production_search:
        return {"error": "Production search not available"}
    
    demo_queries = [
        "kitchen with black table",
        "bathroom with marble countertop",
        "living room with large sofa",
        "bedroom with wooden furniture"
    ]
    
    return {
        "message": "Production search engine is ready",
        "demo_queries": demo_queries,
        "features": [
            "AI-first search with VLM verification",
            "Hebrew/English multilingual support",
            "Explainable results with confidence scores",
            "Fast retrieval + AI verification pipeline"
        ],
        "endpoints": {
            "search": "/api/search/production",
            "analyze": "/api/search/analyze",
            "suggestions": "/api/search/suggestions",
            "trending": "/api/search/trending"
        }
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "path": str(request.url)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)}
    )

if __name__ == "__main__":
    print("🚀 Starting PicLocate V4 Integrated Backend...")
    print("=" * 60)
    print("Features:")
    print("✅ V4 indexing with advanced AI pipeline")
    print("✅ Production search engine with VLM verification")
    print("✅ Supabase integration")
    print("✅ Google Drive OAuth")
    print("=" * 60)
    
    uvicorn.run(
        "fastapi_drive_ai_v4_integrated:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
