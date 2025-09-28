@echo off
echo Setting up environment and starting server...
echo.
echo Please set your OPENAI_API_KEY environment variable before running this script
echo Example: set OPENAI_API_KEY=your_key_here
echo.
echo Starting FastAPI server...
python -m uvicorn fastapi_drive_ai_v3:app --reload --port 8000 --host 127.0.0.1
