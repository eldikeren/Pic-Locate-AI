"""
PicLocate V4 - Production Server Startup Script
"""

import uvicorn
from fastapi_drive_ai_v4_production import app
from api_endpoints_v4 import add_search_endpoints

# Add all V4 search and management endpoints
add_search_endpoints(app)

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 PicLocate V4 - Production Visual Search Engine")
    print("=" * 60)
    print()
    print("📦 Features:")
    print("   ✅ Multi-pass vision pipeline")
    print("   ✅ Room classification")
    print("   ✅ Per-object colors & materials")
    print("   ✅ Structured captions")
    print("   ✅ Hybrid search (SQL + Vector + Ranking)")
    print("   ✅ Hebrew / English support")
    print("   ✅ Explainable results")
    print()
    print("📍 URLs:")
    print("   API: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    print("   Interactive: http://localhost:8000/redoc")
    print()
    print("🔑 Key Endpoints:")
    print("   GET  /auth - Start OAuth")
    print("   POST /index - Index all images")
    print("   POST /search - Hybrid search")
    print("   GET  /stats - Statistics")
    print()
    print("=" * 60)
    print("Starting server...")
    print("=" * 60)
    
    uvicorn.run(
        "start_server_v4:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

