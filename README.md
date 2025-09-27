# PicLocate AI 🖼️🔍

AI-powered Google Drive image search application with semantic query, object detection, and color analysis.

## Features

- **🔍 Semantic Search**: Find images using natural language descriptions
- **🎯 Object Detection**: YOLOv8-powered object recognition
- **🎨 Color Analysis**: Extract dominant colors from images
- **📄 PDF Parsing**: Upload storyboards and extract requirements
- **🌐 Multi-language**: Support for English and Hebrew search
- **📤 Export Options**: PDF, Word, and PowerPoint export with AI-generated proposals

## Tech Stack

- **Backend**: FastAPI with Python
- **AI Models**: CLIP, YOLOv8, OpenAI GPT
- **Frontend**: HTML/CSS/JavaScript with Tailwind CSS
- **Cloud**: Google Drive API integration
- **Deployment**: Vercel (Frontend) + Railway/Render (Backend)

## Quick Start

### Prerequisites

- Python 3.8+
- Google Drive API credentials
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/eldikeren/Pic-Locate-AI.git
cd Pic-Locate-AI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

4. Add your Google Drive credentials:
   - Place your service account JSON file in the root directory
   - Or configure OAuth2 client credentials

5. Start the backend server:
```bash
python -m uvicorn fastapi_drive_ai_v3:app --reload --port 8000
```

6. Start the frontend server:
```bash
python -m http.server 4000
```

7. Open your browser to `http://localhost:4000`

## Usage

1. **Connect to Google Drive**: Click "Connect to Google Drive" and authenticate
2. **Index Images**: Click "Index Drive" to scan and analyze your images
3. **Search**: Use natural language to find images (e.g., "modern kitchen with island")
4. **Upload Storyboards**: Upload PDF storyboards to extract requirements and find matching images
5. **Export Results**: Select images and export to PDF, Word, or PowerPoint

## API Endpoints

- `POST /auth` - Authenticate with Google Drive
- `POST /index` - Index images in Google Drive
- `POST /search` - Search images using semantic similarity
- `POST /parse_requirements` - Parse PDF storyboards
- `POST /analyze_storyboard` - Analyze uploaded storyboard images
- `GET /image/{file_id}` - Serve images from Google Drive
- `POST /export/pdf` - Export selected images to PDF
- `POST /export/word` - Export selected images to Word document
- `POST /export/ppt` - Export selected images to PowerPoint

## Deployment

### Frontend (Vercel)
The frontend is deployed automatically to Vercel when you push to the main branch.

### Backend
For production deployment, consider:
- **Railway**: Easy Python deployment
- **Render**: Free tier available
- **Heroku**: Traditional option
- **Google Cloud Run**: Serverless container deployment

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key for AI features
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account JSON file

### Google Drive Setup
1. Create a Google Cloud Project
2. Enable Google Drive API
3. Create service account credentials
4. Share your Google Drive folder with the service account email

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.

---

Made with ❤️ by [Eldikeren](https://github.com/eldikeren)