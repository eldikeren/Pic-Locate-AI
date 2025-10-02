# 🚀 PicLocate V4 - Quick Start (5 Minutes)

## ✅ Prerequisites

- [x] Python 3.8+ installed
- [x] Google Drive OAuth credentials (`client_secret_*.json`)
- [x] Supabase account (already configured)
- [x] OpenAI API key

## 📥 Step 1: Install Dependencies (2 min)

```bash
# Install requirements
pip install -r requirements_v4.txt

# If you get errors, try upgrading pip first:
python -m pip install --upgrade pip
```

## 🗄️ Step 2: Setup Database (1 min)

1. Go to your Supabase dashboard
2. Navigate to **SQL Editor**
3. Open `supabase_schema_v2.sql`
4. Copy & paste the entire content
5. Click **Run**

✅ You should now have 5 new tables created!

## 🔑 Step 3: Configure Environment (30 sec)

Create `.env` file in project root:

```bash
# OpenAI API Key (required for embeddings)
OPENAI_API_KEY=sk-your-key-here

# Supabase (already configured, but verify)
SUPABASE_URL=https://gezmablgrepoaamtizts.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

## 🚀 Step 4: Start Server (30 sec)

### Option A: Windows
Double-click `start_backend_v4.bat`

### Option B: Command Line
```bash
python start_server_v4.py
```

You should see:
```
========================================================
🚀 PicLocate V4 - Production Visual Search Engine
========================================================

📍 URLs:
   API: http://localhost:8000
   Docs: http://localhost:8000/docs
   Interactive: http://localhost:8000/redoc

Starting server...
```

## 🔐 Step 5: Authenticate & Index (1 min)

1. **Open browser:** http://localhost:8000/docs
2. **Authenticate:**
   - Try `GET /auth` endpoint
   - Click the OAuth URL in response
   - Complete Google sign-in
   - You'll be redirected back

3. **Index images:**
   - Try `POST /index` endpoint
   - Wait for completion (console shows progress)
   - You should see: "Indexed X images from folder..."

## 🔍 Step 6: Test Search!

### Test 1: Simple English Search
```bash
POST /search
{
  "query": "kitchen with black table",
  "top_k": 10
}
```

### Test 2: Hebrew Search
```bash
POST /search
{
  "query": "מטבח עם שולחן שחור",
  "top_k": 10
}
```

### Test 3: Complex Search
```bash
POST /search
{
  "query": "modern kitchen with black dining table and marble countertops",
  "top_k": 20
}
```

## 📊 Step 7: Verify Results

Check that you get:
- ✅ `total_results` count
- ✅ Each result has `score`, `room_type`, `objects`
- ✅ Each result has `explanation` with score breakdown
- ✅ Results are ranked by relevance

Example response:
```json
{
  "query": "מטבח עם שולחן שחור",
  "total_results": 15,
  "results": [
    {
      "image_id": "...",
      "file_name": "kitchen_modern.jpg",
      "room_type": "kitchen",
      "score": 0.92,
      "objects": [
        {
          "label": "dining_table",
          "color": "black",
          "material": "wood",
          "confidence": 0.95
        }
      ],
      "explanation": {
        "semantic_contribution": 0.484,
        "room_contribution": 0.135,
        "object_contribution": 0.190,
        "material_contribution": 0.090
      }
    }
  ]
}
```

## 🎉 Success!

You now have a fully functional production-grade visual search engine!

## 📚 Next Steps

### Explore Other Endpoints:
```bash
GET /stats              # Database statistics
GET /rooms              # List all room types
GET /objects/list       # List detected objects
GET /materials/list     # List materials
GET /colors/list        # List colors
GET /image/{drive_id}   # Download specific image
```

### Integration with Frontend:
1. Update frontend to call http://localhost:8000/search
2. Display results with images
3. Show explainability scores
4. Add filters (room, colors, materials)

### Performance Tuning:
1. Monitor query latency (should be <300ms)
2. Check Supabase metrics
3. Optimize if needed (see DEPLOYMENT_V4.md)

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements_v4.txt --upgrade
```

### "OpenAI API key not set"
Add to `.env`:
```
OPENAI_API_KEY=sk-your-key-here
```

### "No images found"
1. Check Google Drive authentication
2. Verify folder ID: `11kSHWn47cQqeRhtlVQ-4Uask7jr2fqjW`
3. Re-run POST /index

### "Search returns empty"
1. Verify images were indexed (check console output)
2. Try simpler query first: "kitchen"
3. Check Supabase has data:
   ```sql
   SELECT COUNT(*) FROM images;
   SELECT COUNT(*) FROM image_objects;
   ```

### "Slow performance"
1. Check Supabase plan (free tier has limits)
2. Reduce `top_k` to 10
3. Add more specific filters (room_type)

## 📞 Support

For detailed information, see:
- **`V4_IMPLEMENTATION_SUMMARY.md`** - Complete technical overview
- **`DEPLOYMENT_V4.md`** - Full deployment guide
- **`http://localhost:8000/docs`** - Interactive API documentation

## ⚡ Quick Reference

### Essential Commands:
```bash
# Start server
python start_server_v4.py

# Install dependencies
pip install -r requirements_v4.txt

# Run schema migration
# (In Supabase SQL Editor)
# Copy & paste supabase_schema_v2.sql
```

### Essential Endpoints:
```bash
GET  /auth        # Authenticate
POST /index       # Index all images
POST /search      # Search images
GET  /stats       # Statistics
GET  /docs        # API documentation
```

### Test Queries:
```
English: "modern kitchen with black dining table"
Hebrew:  "מטבח מודרני עם שולחן שחור"
Complex: "living room with blue sofa and wooden coffee table"
Hebrew:  "סלון עם ספה כחולה ושולחן קפה מעץ"
```

---

**🎉 You're all set! Happy searching!** 🔍✨

