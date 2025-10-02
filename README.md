# PicLocate V4 - AI-Powered Image Search

A complete end-to-end solution for intelligent image search with ChatGPT-like accuracy, featuring advanced AI pipeline, V4 indexing, and production-ready search engine.

## 🚀 Features

- **AI-First Search**: ChatGPT-like image understanding with VLM verification
- **V4 Indexing**: Advanced AI pipeline with object detection, room classification, and embeddings
- **Multilingual Support**: Hebrew ↔ English with comprehensive translation
- **Real-time Monitoring**: Live indexing progress and system health
- **Production Ready**: Optimized for speed, cost, and scalability

## 🏗️ Architecture

```
User Query → Frontend → Integrated Backend
                           |
                    V4 Indexing System
                    ├── Object Detection (YOLO)
                    ├── Room Classification
                    ├── Color/Material Analysis
                    ├── Structured Captions
                    └── Vector Embeddings
                           |
                    Production Search Engine
                    ├── Stage A: Fast Retrieval (SQL + pgvector)
                    ├── Stage B: VLM Verification (GPT-4o-mini)
                    └── Stage C: Re-rank & Filter
                           |
                    Supabase Database
                    ├── images (10,000+ records)
                    ├── image_objects (detected objects)
                    ├── image_captions (structured captions)
                    └── image_tags (searchable tags)
```

## 📁 Project Structure

```
PicLocate/
├── fastapi_drive_ai_v4_integrated.py    # Integrated backend
├── production_search_engine.py          # AI-first search engine
├── production_search_api.py             # Search API endpoints
├── start_integrated_system.py           # System startup script
├── frontend/
│   ├── pages/index.js                   # React frontend
│   ├── styles/Home.module.css           # Modern styling
│   ├── package.json                     # Frontend dependencies
│   └── next.config.js                   # Next.js configuration
├── requirements.txt                     # Python dependencies
├── vercel.json                          # Vercel deployment config
└── README.md                            # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Node.js 18+
- Google Drive API credentials
- Supabase account
- OpenAI API key (for production search)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PicLocate
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Set up environment variables**
   ```bash
   export SUPABASE_URL="your-supabase-url"
   export SUPABASE_KEY="your-supabase-key"
   export OPENAI_API_KEY="your-openai-key"
   ```

5. **Start the integrated system**
   ```bash
   python start_integrated_system.py
   ```

## 🚀 Deployment

### Vercel Deployment

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Deploy to Vercel**
   ```bash
   vercel --prod
   ```

3. **Set environment variables in Vercel dashboard**
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `OPENAI_API_KEY`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`

### Manual Deployment

1. **Build the frontend**
   ```bash
   cd frontend
   npm run build
   cd ..
   ```

2. **Deploy backend to your preferred platform**
   - Heroku
   - Railway
   - DigitalOcean
   - AWS

## 📊 API Endpoints

### V4 Indexing
- `POST /v4/index` - Start V4 indexing
- `GET /indexing/status` - Check indexing progress
- `GET /stats/overview` - System statistics

### Production Search
- `POST /api/search/production` - AI-powered search
- `POST /api/search/analyze` - Single image analysis
- `GET /api/search/suggestions` - Search suggestions
- `GET /api/search/trending` - Trending searches

### System
- `GET /health` - System health check
- `GET /docs` - API documentation

## 🔍 Usage

### Basic Search

```javascript
// Search for images
const response = await fetch('/api/search/production', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'kitchen with black table',
    lang: 'en',
    limit: 24
  })
});

const results = await response.json();
```

### Hebrew Search

```javascript
// Hebrew search (automatically translated)
const response = await fetch('/api/search/production', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'מטבח עם שולחן שחור',
    lang: 'he',
    limit: 24
  })
});
```

## 🎯 Key Features

### AI-First Search
- **VLM Verification**: AI analyzes images pixel by pixel
- **Explainable Results**: Confidence scores and match reasons
- **ChatGPT-like Accuracy**: Only returns images AI confirms match

### V4 Indexing Pipeline
- **Object Detection**: YOLO-based object recognition
- **Room Classification**: Intelligent room type inference
- **Color Analysis**: Per-object color extraction
- **Material Detection**: Texture and material classification
- **Structured Captions**: English and Hebrew descriptions

### Production Optimizations
- **Batch Processing**: 12 images per VLM call
- **Result Caching**: Avoid repeated API calls
- **Image Downscaling**: 1024px max for speed/cost
- **Fast Retrieval**: SQL + pgvector search

## 📈 Performance

- **Indexing Speed**: ~3 images/minute (with AI processing)
- **Search Speed**: ~2-6 seconds/query (with VLM verification)
- **Cost**: ~$0.02-0.03/search (with OpenAI API)
- **Accuracy**: ChatGPT-like precision with explainable results

## 🔧 Configuration

### Environment Variables

```bash
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Optional (for production search)
OPENAI_API_KEY=your-openai-api-key

# Google Drive (for indexing)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Search Engine Settings

```python
# In production_search_engine.py
TOP_K = 120          # Candidates from Stage A
BATCH_SIZE = 12      # Images per VLM call
CUTOFF = 0.7         # VLM confidence threshold
FINAL_LIMIT = 24     # Final results to return
```

## 🧪 Testing

```bash
# Run end-to-end tests
python test_simple_end_to_end.py

# Test individual components
python test_search_components.py

# Test production search
python test_production_search.py
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API docs at `/docs`

## 🎉 Acknowledgments

- OpenAI for GPT-4o-mini vision capabilities
- Supabase for database and vector search
- Google Drive API for image storage
- YOLO for object detection
- FastAPI for the backend framework
- Next.js for the frontend framework