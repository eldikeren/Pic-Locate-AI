# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Google Drive API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "Google Drive API"
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Choose "Desktop application"
6. Download the JSON file and rename it to `credentials.json`
7. Place `credentials.json` in this directory

### 3. Start the Server
```bash
python start_server.py
```
Or manually:
```bash
uvicorn fastapi_drive_ai_v3:app --reload --port 6000
```

### 4. Test the API
```bash
python test_api.py
```

## 🔗 Key URLs
- **API**: http://localhost:6000
- **Documentation**: http://localhost:6000/docs
- **Health Check**: http://localhost:6000/health

## 📋 Basic Usage Flow

1. **Authenticate**: `GET /auth` (opens browser)
2. **Index Images**: `POST /index` (crawls your Drive)
3. **Search**: `POST /search` with your query

## 🎯 Example Search
```bash
curl -X POST http://localhost:6000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "modern kitchen with purple island",
    "required_objects": ["island"],
    "required_colors": [[128, 0, 128]],
    "top_k": 5
  }'
```

## ⚠️ Important Notes
- First indexing may take time for large Drives
- GPU recommended for faster processing
- Images are processed locally (privacy-friendly)
- Index is stored in memory (restart server to re-index)

## 🆘 Need Help?
- Check the full [README.md](README.md) for detailed instructions
- Ensure `credentials.json` is properly configured
- Check console output for error messages

