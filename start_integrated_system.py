"""
Start Integrated PicLocate V4 System
Complete end-to-end solution with V4 indexing and AI search
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def start_integrated_system():
    """Start the complete integrated system"""
    print("Starting PicLocate V4 Integrated System")
    print("=" * 60)
    print("Features:")
    print("V4 indexing with advanced AI pipeline")
    print("Production search engine with VLM verification")
    print("Supabase integration")
    print("Google Drive OAuth")
    print("Complete frontend with real-time status")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("fastapi_drive_ai_v4_integrated.py"):
        print("Error: fastapi_drive_ai_v4_integrated.py not found")
        print("Please run this script from the PicLocate directory")
        return
    
    # Check for required files
    required_files = [
        "fastapi_drive_ai_v4_integrated.py",
        "production_search_engine.py",
        "production_search_api.py",
        "frontend/pages/index.js",
        "frontend/styles/Home.module.css"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return
    
    print("All required files found")
    
    # Check environment variables
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("Warning: OPENAI_API_KEY not set")
        print("   Production search will not be available")
        print("   Set OPENAI_API_KEY environment variable to enable AI search")
    else:
        print("OpenAI API key found")
    
    # Start the integrated backend
    print("\nStarting integrated backend...")
    try:
        # Start the backend in a subprocess
        backend_process = subprocess.Popen([
            sys.executable, "fastapi_drive_ai_v4_integrated.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for the backend to start
        time.sleep(3)
        
        # Check if the backend is running
        if backend_process.poll() is None:
            print("Backend started successfully")
            print("   Backend URL: http://localhost:8000")
            print("   API Docs: http://localhost:8000/docs")
        else:
            print("Backend failed to start")
            stdout, stderr = backend_process.communicate()
            print(f"Error: {stderr.decode()}")
            return
            
    except Exception as e:
        print(f"Error starting backend: {e}")
        return
    
    # Start the frontend
    print("\nStarting frontend...")
    frontend_dir = Path("frontend")
    if frontend_dir.exists():
        try:
            # Check if node_modules exists
            if not (frontend_dir / "node_modules").exists():
                print("Installing frontend dependencies...")
                subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            
            # Start the frontend
            frontend_process = subprocess.Popen([
                "npm", "run", "dev"
            ], cwd=frontend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for frontend to start
            time.sleep(5)
            
            if frontend_process.poll() is None:
                print("Frontend started successfully")
                print("   Frontend URL: http://localhost:3000")
            else:
                print("Frontend failed to start")
                stdout, stderr = frontend_process.communicate()
                print(f"Error: {stderr.decode()}")
                
        except Exception as e:
            print(f"Error starting frontend: {e}")
            print("   You can manually start the frontend with: cd frontend && npm run dev")
    else:
        print("Frontend directory not found")
        print("   You can create a simple HTML frontend or use the API directly")
    
    # Open browser
    print("\nOpening browser...")
    try:
        webbrowser.open("http://localhost:3000")
        time.sleep(1)
        webbrowser.open("http://localhost:8000/docs")
    except Exception as e:
        print(f"Could not open browser: {e}")
        print("   Please manually open: http://localhost:3000")
    
    # System status
    print("\nSystem Status:")
    print("   Backend: http://localhost:8000")
    print("   Frontend: http://localhost:3000")
    print("   API Docs: http://localhost:8000/docs")
    print("   Health Check: http://localhost:8000/health")
    
    print("\nAvailable Endpoints:")
    print("   POST /v4/index - Start V4 indexing")
    print("   GET /indexing/status - Check indexing progress")
    print("   POST /api/search/production - AI-powered search")
    print("   GET /stats/overview - System statistics")
    
    print("\nNext Steps:")
    print("   1. Authenticate with Google Drive (if not already done)")
    print("   2. Start V4 indexing to process 10,000+ images")
    print("   3. Use AI search to find images with ChatGPT-like accuracy")
    print("   4. Monitor progress in the frontend")
    
    print("\nTo stop the system:")
    print("   Press Ctrl+C in this terminal")
    print("   Or close the terminal window")
    
    try:
        # Keep the script running
        print("\nSystem is running... Press Ctrl+C to stop")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping system...")
        
        # Stop backend
        if 'backend_process' in locals():
            backend_process.terminate()
            print("Backend stopped")
        
        # Stop frontend
        if 'frontend_process' in locals():
            frontend_process.terminate()
            print("Frontend stopped")
        
        print("System stopped successfully")

if __name__ == "__main__":
    start_integrated_system()
