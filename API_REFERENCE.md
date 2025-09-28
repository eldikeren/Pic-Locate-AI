# API Reference - Google Drive AI Visual Search

## Base URL
```
http://localhost:6000
```

## Authentication
All endpoints require Google Drive authentication via `/auth` endpoint.

---

## Endpoints

### 🔐 Authentication

#### `GET /auth`
Authenticate with Google Drive using OAuth2.

**Response:**
```json
{
  "status": "authenticated",
  "message": "Successfully connected to Google Drive"
}
```

**Error Response:**
```json
{
  "error": "credentials.json not found. Please download it from Google Cloud Console"
}
```

---

### 📁 Indexing

#### `POST /index`
Crawl and index all images in Google Drive.

**Response:**
```json
{
  "status": "Drive indexed successfully",
  "total_images": 150,
  "message": "Indexed 150 images with CLIP embeddings, YOLO objects, and color data"
}
```

**Error Response:**
```json
{
  "error": "Not authenticated. Call /auth first."
}
```

---

### 🔍 Search

#### `POST /search`
Search images using AI-powered matching.

**Request Body:**
```json
{
  "query": "modern kitchen with purple island",
  "required_objects": ["island", "stove"],
  "required_colors": [[128, 0, 128]],
  "top_k": 5
}
```

**Parameters:**
- `query` (string, required): Natural language search query
- `required_objects` (array, optional): List of required objects
- `required_colors` (array, optional): List of RGB color values `[[r,g,b], ...]`
- `top_k` (integer, optional): Number of results to return (default: 5)

**Response:**
```json
[
  {
    "file_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    "name": "modern_kitchen_purple_island.jpg",
    "score": 0.8542,
    "objects": ["island", "stove", "sink"],
    "colors": [[128, 0, 128], [255, 255, 255], [200, 200, 200]],
    "semantic_score": 0.8234,
    "object_score": 1.0000,
    "color_score": 0.7891
  }
]
```

**Error Response:**
```json
{
  "error": "No images indexed. Call /index first."
}
```

---

### 📄 Document Parsing

#### `POST /parse_requirements`
Parse storyboard/PDF to extract design requirements.

**Request:**
- Content-Type: `multipart/form-data`
- Body: File upload (PDF, TXT, DOC, DOCX)

**Response:**
```json
{
  "status": "success",
  "filename": "kitchen_requirements.pdf",
  "requirements": {
    "location": "kitchen",
    "style": ["modern", "contemporary"],
    "required_objects": ["island", "stove", "sink"],
    "required_colors": [[128, 0, 128], [255, 255, 255]],
    "raw_text": "Client Requirements for Kitchen Renovation: We want a modern kitchen design..."
  }
}
```

**Error Response:**
```json
{
  "error": "Failed to parse file: Invalid file format"
}
```

---

### 📊 Statistics

#### `GET /stats`
Get indexing statistics and metadata.

**Response:**
```json
{
  "total_images": 150,
  "total_objects_detected": 25,
  "most_common_objects": {
    "chair": 45,
    "table": 38,
    "lamp": 32,
    "bed": 28,
    "sofa": 25
  },
  "most_common_colors": {
    "[255, 255, 255]": 89,
    "[200, 200, 200]": 67,
    "[128, 128, 128]": 45,
    "[0, 0, 0]": 34,
    "[255, 0, 0]": 23
  }
}
```

---

### 🏥 Health Check

#### `GET /health`
Check system health and status.

**Response:**
```json
{
  "status": "healthy",
  "device": "cuda",
  "authenticated": true,
  "images_indexed": 150
}
```

---

#### `GET /`
Root endpoint with API information.

**Response:**
```json
{
  "message": "Google Drive AI Search v3 with YOLOv8 running",
  "endpoints": {
    "auth": "/auth - Authenticate with Google Drive",
    "index": "/index - Index all Drive images",
    "search": "/search - Search images with AI",
    "parse": "/parse_requirements - Parse storyboard/PDF",
    "stats": "/stats - Get indexing statistics",
    "health": "/health - Health check"
  }
}
```

---

## Search Examples

### Basic Semantic Search
```bash
curl -X POST http://localhost:6000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "modern kitchen", "top_k": 3}'
```

### Object-Based Search
```bash
curl -X POST http://localhost:6000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "bedroom design",
    "required_objects": ["bed", "lamp"],
    "top_k": 5
  }'
```

### Color-Based Search
```bash
curl -X POST http://localhost:6000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "living room",
    "required_colors": [[255, 0, 0], [0, 0, 255]],
    "top_k": 3
  }'
```

### Complex Combined Search
```bash
curl -X POST http://localhost:6000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "modern kitchen with island",
    "required_objects": ["island", "stove"],
    "required_colors": [[128, 0, 128]],
    "top_k": 5
  }'
```

### File Upload
```bash
curl -X POST http://localhost:6000/parse_requirements \
  -F "file=@requirements.pdf"
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 400  | Bad Request - Invalid parameters |
| 401  | Unauthorized - Not authenticated |
| 404  | Not Found - Endpoint not found |
| 500  | Internal Server Error |

---

## Rate Limits

- **Authentication**: No limit
- **Indexing**: One concurrent operation
- **Search**: 100 requests/minute
- **File Parsing**: 10 requests/minute

---

## Data Formats

### Color Format
Colors are represented as RGB arrays:
```json
[128, 0, 128]  // Purple
[255, 255, 255]  // White
[0, 0, 0]  // Black
```

### Object Names
Common detected objects:
- `island`, `bed`, `sofa`, `table`, `chair`
- `stove`, `sink`, `lamp`, `cabinet`, `mirror`
- `rug`, `curtain`, `door`, `window`

### File IDs
Google Drive file IDs are used to reference images:
```
1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
```

---

## Interactive Documentation

Visit `http://localhost:6000/docs` for interactive Swagger UI documentation with:
- Live API testing
- Request/response examples
- Schema definitions
- Authentication testing

