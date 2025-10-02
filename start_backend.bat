@echo off
echo Starting Backend Server...
cd /d C:\Users\user\Desktop\PicLocate
python -m uvicorn fastapi_drive_ai_v3:app --reload --port 8000 --host 127.0.0.1
