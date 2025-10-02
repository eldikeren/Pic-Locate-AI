"""
Additional FastAPI endpoints for V4
Search, analytics, and image retrieval
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
import io
from typing import List, Optional

# Import search engine
from search_engine import search_images
from fastapi_drive_ai_v4_production import supabase, drive_service

def add_search_endpoints(app: FastAPI):
    """Add all V4 endpoints to FastAPI app"""
    
    @app.post("/search")
    def search(
        query: str = Query(..., description="Search query in Hebrew or English"),
        top_k: int = Query(20, description="Number of results to return"),
        room_filter: Optional[str] = Query(None, description="Filter by room type"),
        min_score: float = Query(0.0, description="Minimum similarity score")
    ):
        """
        Advanced search with hybrid ranking
        
        Examples:
            - "מטבח עם שולחן שחור" (Hebrew: kitchen with black table)
            - "modern kitchen with black dining table and marble countertops"
            - "סלון עם ספה כחולה" (Hebrew: living room with blue sofa)
        
        Returns:
            List of images with scores and explanations
        """
        try:
            results = search_images(query, top_k=top_k)
            
            # Apply additional filters
            if room_filter:
                results = [r for r in results if r.get('room_type') == room_filter]
            
            if min_score > 0:
                results = [r for r in results if r.get('final_score', 0) >= min_score]
            
            # Format response
            formatted_results = []
            for r in results:
                formatted_results.append({
                    "image_id": r['image_id'],
                    "drive_id": r['drive_id'],
                    "file_name": r['file_name'],
                    "folder_path": r['folder_path'],
                    "room_type": r['room_type'],
                    "caption": r['caption'],
                    "score": r['final_score'],
                    "semantic_score": r['semantic_score'],
                    "objects": [
                        {
                            "label": obj['label'],
                            "color": obj.get('color_name'),
                            "material": obj.get('material'),
                            "confidence": obj.get('label_confidence')
                        }
                        for obj in r.get('objects', [])
                    ],
                    "explanation": r.get('explanation', {})
                })
            
            return {
                "query": query,
                "total_results": len(formatted_results),
                "results": formatted_results
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/image/{drive_id}")
    def get_image(drive_id: str):
        """Download image from Google Drive by ID"""
        try:
            if not drive_service:
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            request = drive_service.files().get_media(fileId=drive_id)
            fh = io.BytesIO()
            
            from googleapiclient.http import MediaIoBaseDownload
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            fh.seek(0)
            return StreamingResponse(fh, media_type="image/jpeg")
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/image/details/{image_id}")
    def get_image_details(image_id: str):
        """Get detailed information about an image"""
        try:
            # Get image data
            image_result = supabase.table("images").select("*").eq("id", image_id).execute()
            if not image_result.data:
                raise HTTPException(status_code=404, detail="Image not found")
            
            image_data = image_result.data[0]
            
            # Get objects
            objects_result = supabase.table("image_objects").select("*").eq("image_id", image_id).execute()
            objects = objects_result.data if objects_result.data else []
            
            # Get caption
            caption_result = supabase.table("image_captions").select("*").eq("image_id", image_id).execute()
            caption_data = caption_result.data[0] if caption_result.data else {}
            
            # Get tags
            tags_result = supabase.table("image_tags").select("tag").eq("image_id", image_id).execute()
            tags = [t['tag'] for t in tags_result.data] if tags_result.data else []
            
            return {
                "image": image_data,
                "objects": objects,
                "caption": caption_data,
                "tags": tags
            }
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/stats")
    def get_statistics():
        """Get database statistics"""
        try:
            # Count images by room
            images_count = supabase.table("images").select("room_type", count="exact").execute()
            
            # Count objects
            objects_count = supabase.table("image_objects").select("id", count="exact").execute()
            
            # Get room distribution
            room_dist_result = supabase.table("images").select("room_type").execute()
            room_dist = {}
            for row in room_dist_result.data:
                room = row.get('room_type', 'unknown')
                room_dist[room] = room_dist.get(room, 0) + 1
            
            return {
                "total_images": images_count.count if hasattr(images_count, 'count') else 0,
                "total_objects": objects_count.count if hasattr(objects_count, 'count') else 0,
                "room_distribution": room_dist
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/rooms")
    def list_rooms():
        """List all unique room types"""
        try:
            result = supabase.table("images").select("room_type").execute()
            rooms = list(set(row['room_type'] for row in result.data if row.get('room_type')))
            rooms.sort()
            
            return {"rooms": rooms}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/objects/list")
    def list_detected_objects():
        """List all detected object types"""
        try:
            result = supabase.table("image_objects").select("label").execute()
            objects = list(set(row['label'] for row in result.data if row.get('label')))
            objects.sort()
            
            return {"objects": objects}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/materials/list")
    def list_materials():
        """List all detected materials"""
        try:
            result = supabase.table("image_objects").select("material").execute()
            materials = list(set(row['material'] for row in result.data if row.get('material') and row['material'] != 'unknown'))
            materials.sort()
            
            return {"materials": materials}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/colors/list")
    def list_colors():
        """List all detected colors"""
        try:
            result = supabase.table("image_objects").select("color_name").execute()
            colors = list(set(row['color_name'] for row in result.data if row.get('color_name') and row['color_name'] != 'unknown'))
            colors.sort()
            
            return {"colors": colors}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/reindex/{drive_id}")
    def reindex_single_image(drive_id: str):
        """Re-index a single image (useful for corrections)"""
        try:
            if not drive_service:
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            # Get image from Drive
            from fastapi_drive_ai_v4_production import process_and_index_image
            
            file_info = drive_service.files().get(fileId=drive_id, fields="name").execute()
            file_name = file_info.get('name', 'unknown')
            
            request = drive_service.files().get_media(fileId=drive_id)
            fh = io.BytesIO()
            
            from googleapiclient.http import MediaIoBaseDownload
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            image_data = fh.getvalue()
            
            # Re-index
            result = process_and_index_image(drive_id, file_name, "Manual Reindex", image_data)
            
            return result
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return app

