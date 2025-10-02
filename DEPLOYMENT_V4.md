# PicLocate V4 - Production Deployment Guide

## 🚀 Quick Start

### 1. Database Migration

First, run the new schema in Supabase:

```bash
# In Supabase SQL Editor, run:
cat supabase_schema_v2.sql
```

This creates 5 new tables:
- `images` - Main image metadata
- `image_objects` - Detected objects per image
- `image_room_scores` - Room classification probabilities
- `image_captions` - Structured captions + embeddings
- `image_tags` - Fast-filter denormalized tags

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv_v4
source venv_v4/bin/activate  # On Windows: venv_v4\Scripts\activate

# Install requirements
pip install -r requirements_v4.txt
```

### 3. Environment Configuration

Create `.env` file:

```bash
# Supabase
SUPABASE_URL=https://gezmablgrepoaamtizts.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# OpenAI (for embeddings)
OPENAI_API_KEY=your_openai_api_key_here

# Google Drive OAuth
# (Keep existing client_secret JSON files)
```

### 4. Start the V4 Backend

Create `start_backend_v4.bat`:

```batch
@echo off
echo Starting PicLocate V4 Production Backend...
cd /d C:\Users\user\Desktop\PicLocate
python start_server_v4.py
pause
```

Create `start_server_v4.py`:

```python
import uvicorn
from fastapi_drive_ai_v4_production import app
from api_endpoints_v4 import add_search_endpoints

# Add all V4 endpoints
add_search_endpoints(app)

if __name__ == "__main__":
    print("="*60)
    print("🚀 PicLocate V4 - Production Visual Search Engine")
    print("="*60)
    print()
    print("📍 API: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print()
    print("Starting server...")
    print("="*60)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
```

Run it:

```bash
python start_server_v4.py
```

### 5. First-Time Indexing

1. Navigate to http://localhost:8000
2. Click "Connect Google Drive" → Complete OAuth
3. Click "Index Drive Images"
4. Wait for complete indexing (progress shown in console)

**Expected results:**
- All images from folder `11kSHWn47cQqeRhtlVQ-4Uask7jr2fqjW` indexed
- Subfolders crawled recursively
- Room types detected
- Objects detected with colors and materials
- Captions generated
- Embeddings stored in Supabase

## 📊 What's New in V4?

### Phase 1: Smart Indexing
✅ **Perceptual hashing** - Automatic duplicate detection  
✅ **Room classification** - Kitchen, living room, bedroom, bathroom, etc.  
✅ **Object-based inference** - Uses detected objects to improve room accuracy

### Phase 2: Per-Object Analysis
✅ **Color extraction** - K-means clustering in CIELAB space  
✅ **Material detection** - Marble, granite, wood, metal, glass, etc.  
✅ **Detailed object data** - Every object has its own color/material

### Phase 3: Semantic Layer
✅ **Structured captions** - "Kitchen with black dining table and marble countertops"  
✅ **Text embeddings** - OpenAI text-embedding-3-large (1536 dimensions)  
✅ **Structured facts** - JSON with room, objects, materials, colors

### Phase 4: Advanced Search
✅ **Hebrew support** - Full Hebrew ↔ English translation  
✅ **Query parsing** - Extracts room, objects, colors, materials  
✅ **Hybrid ranking** - SQL filters + vector similarity + weighted scoring  
✅ **Explainability** - See why each result matched

## 🔍 Search Examples

### English:
```
POST /search
{
  "query": "modern kitchen with black dining table and marble countertops",
  "top_k": 20
}
```

### Hebrew:
```
POST /search
{
  "query": "מטבח מודרני עם שולחן שחור ושיש",
  "top_k": 20
}
```

### Complex:
```
POST /search
{
  "query": "סלון עם ספה כחולה ושולחן קפה מעץ",  // Living room with blue sofa and wooden coffee table
  "top_k": 20
}
```

## 📈 API Endpoints

### Core
- `GET /` - Health check
- `GET /auth` - Start OAuth flow
- `POST /index` - Index all images
- `POST /search` - Hybrid search

### Image Management
- `GET /image/{drive_id}` - Download image
- `GET /image/details/{image_id}` - Get full details
- `POST /reindex/{drive_id}` - Re-index single image

### Analytics
- `GET /stats` - Database statistics
- `GET /rooms` - List all room types
- `GET /objects/list` - List detected objects
- `GET /materials/list` - List materials
- `GET /colors/list` - List colors

## 🎯 Search Response Format

```json
{
  "query": "מטבח עם שולחן שחור",
  "total_results": 15,
  "results": [
    {
      "image_id": "uuid-here",
      "drive_id": "google-drive-id",
      "file_name": "kitchen_modern.jpg",
      "folder_path": "Shared Locations Drive/אתי הרצליה",
      "room_type": "kitchen",
      "caption": "Kitchen with black dining table, four chairs; gray cabinets; stainless fridge",
      "score": 0.92,
      "semantic_score": 0.88,
      "objects": [
        {
          "label": "dining_table",
          "color": "black",
          "material": "wood",
          "confidence": 0.95
        },
        {
          "label": "chair",
          "color": "black",
          "material": "wood",
          "confidence": 0.89
        }
      ],
      "explanation": {
        "semantic_contribution": 0.484,
        "room_contribution": 0.135,
        "object_contribution": 0.190,
        "material_contribution": 0.090,
        "matched_constraints": {
          "room": true,
          "objects": 1,
          "materials": 0
        }
      }
    }
  ]
}
```

## 🔧 Performance Tips

### Indexing Speed
- **First run**: ~5-10 images/second (depends on image sizes)
- **Re-indexing**: Skips duplicates automatically
- **Batch size**: Processes 1000 images per folder scan

### Search Speed
- **SQL filtering**: <50ms (with indexes)
- **Vector search**: <200ms for 10K images
- **Total**: Typically <300ms per query

### Database Optimization
```sql
-- Run periodically (weekly)
VACUUM ANALYZE images;
VACUUM ANALYZE image_objects;
VACUUM ANALYZE image_captions;

-- Reindex vectors (monthly)
REINDEX INDEX idx_captions_embed_en;
```

## 🐛 Troubleshooting

### "OpenAI API key not set"
- Add `OPENAI_API_KEY` to `.env`
- Restart server

### "No images found"
- Check Google Drive permissions
- Verify folder ID: `11kSHWn47cQqeRhtlVQ-4Uask7jr2fqjW`
- Re-authenticate with OAuth

### "Vector index slow"
- Check Supabase plan (free tier has limits)
- Reduce `top_k` in queries
- Add more IVFFLAT lists (for >100K images)

### "Hebrew search not working"
- Verify query parser is detecting Hebrew
- Check synonym mappings in `HEBREW_ENGLISH_SYNONYMS`
- Test with English first to isolate issue

## 🔄 Migration from V3 to V4

If you have existing data in the old schema:

1. **Backup first!**
   ```sql
   -- In Supabase SQL Editor
   CREATE TABLE image_embeddings_backup AS SELECT * FROM image_embeddings;
   ```

2. **Run new schema** (creates new tables, doesn't touch old ones)
   ```bash
   # Run supabase_schema_v2.sql
   ```

3. **Re-index** (V4 will populate new tables)
   ```
   POST /index
   ```

4. **Verify** both schemas coexist
   ```sql
   SELECT COUNT(*) FROM image_embeddings;  -- Old
   SELECT COUNT(*) FROM images;  -- New
   ```

5. **Optional**: Drop old table once verified
   ```sql
   DROP TABLE image_embeddings;
   ```

## 📞 Support

For issues or questions:
1. Check logs in console
2. Verify Supabase connection
3. Test with simple English queries first
4. Check OpenAI API quota

## ✅ Production Checklist

Before deploying to production:

- [ ] Supabase schema created
- [ ] All dependencies installed
- [ ] `.env` configured
- [ ] Google Drive OAuth working
- [ ] OpenAI API key valid
- [ ] Initial indexing complete
- [ ] Test search (English)
- [ ] Test search (Hebrew)
- [ ] Verify explainability
- [ ] Check performance (<500ms queries)
- [ ] Setup database backups
- [ ] Monitor API quotas (OpenAI, Supabase)

