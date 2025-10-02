@echo off
echo Starting PicLocate AI servers...
echo.

echo Starting Backend server on port 8000...
start "Backend Server" cmd /k "cd /d C:\Users\user\Desktop\PicLocate && python -m uvicorn fastapi_drive_ai_v3:app --reload --port 8000 --host 127.0.0.1"

echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak > nul

echo Starting Frontend server on port 4000...
start "Frontend Server" cmd /k "cd /d C:\Users\user\Desktop\PicLocate && python -m http.server 4000"

echo.
echo Both servers are starting...
echo Backend: http://localhost:8000/
echo Frontend: http://localhost:4000/
echo.
echo Press any key to exit...
pause > nul
