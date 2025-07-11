from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import subprocess
import sys
import os
import json
import logging
from typing import Optional
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Check multiple locations for .env file
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
env_locations = [
    current_dir / ".env",
    parent_dir / ".env",
    Path.cwd() / ".env"
]

env_loaded = False
for env_path in env_locations:
    if env_path.exists():
        load_dotenv(env_path)
        env_loaded = True
        print(f"[DEBUG] Loaded .env from: {env_path}")
        break

if not env_loaded:
    print("[DEBUG] No .env file found. Please create one using env.example as template.")
    load_dotenv()  # Load from system environment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Health Analysis API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AnalysisRequest(BaseModel):
    user_id: str
    archetype: str

class HealthCheckResponse(BaseModel):
    status: str
    message: str

# Store active analysis processes
active_processes = {}

@app.get("/", response_model=HealthCheckResponse)
async def root():
    return HealthCheckResponse(status="healthy", message="Health Analysis API is running")

@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check():
    return HealthCheckResponse(status="healthy", message="API is operational")

@app.post("/api/analyze")
async def start_analysis(request: AnalysisRequest):
    """Start health analysis and return real-time updates via Server-Sent Events"""
    
    # Validate inputs
    if not request.user_id.strip():
        raise HTTPException(status_code=400, detail="User ID is required")
    
    if not request.archetype.strip():
        raise HTTPException(status_code=400, detail="Archetype is required")
    
    # Set up environment variables - ensure they're passed to subprocess
    env = os.environ.copy()
    database_url = os.getenv("DATABASE_URL")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # Check for required environment variables
    if not database_url:
        raise HTTPException(status_code=500, detail="DATABASE_URL not configured. Please check your .env file.")
    
    if not openai_api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured. Please check your .env file.")
    
    env["DATABASE_URL"] = database_url
    env["OPENAI_API_KEY"] = openai_api_key
    
    # Log environment variables for debugging (without exposing sensitive data)
    logger.info(f"DATABASE_URL set: {'Yes' if database_url else 'No'}")
    logger.info(f"OPENAI_API_KEY set: {'Yes' if openai_api_key else 'No'}")
    
    async def generate_analysis_stream():
        process = None
        try:
            # Start the Python analysis process
            cmd = [sys.executable, "main_api.py", request.user_id, request.archetype]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env  # Pass environment variables to subprocess
            )
            
            # Store the process
            process_id = id(process)
            active_processes[process_id] = process
            
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'message': 'Analysis started', 'stage': 'initializing'})}\n\n"
            
            # Read output line by line
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    if line:
                        # Determine the stage based on output content
                        stage = determine_stage(line)
                        
                        # Send the output to frontend
                        yield f"data: {json.dumps({'type': 'output', 'message': line, 'stage': stage})}\n\n"
                        
                        # Add small delay to prevent overwhelming the frontend
                        await asyncio.sleep(0.1)
            
            # Wait for process to complete
            return_code = process.wait()
            
            if return_code == 0:
                yield f"data: {json.dumps({'type': 'complete', 'message': 'Analysis completed successfully', 'stage': 'completed'})}\n\n"
            else:
                # Get error output
                error_output = process.stderr.read()
                yield f"data: {json.dumps({'type': 'error', 'message': f'Analysis failed: {error_output}', 'stage': 'error'})}\n\n"
            
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': f'Server error: {str(e)}', 'stage': 'error'})}\n\n"
        
        finally:
            # Clean up
            if process:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    process.kill()
                
                process_id = id(process)
                active_processes.pop(process_id, None)
    
    return StreamingResponse(
        generate_analysis_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

def determine_stage(line: str) -> str:
    """Determine the analysis stage based on output content"""
    line_lower = line.lower()
    
    if "welcome to the health analysis system" in line_lower:
        return "initialization"
    elif "select your routine plan archetype" in line_lower:
        return "archetype_selection"
    elif "selected:" in line_lower:
        return "archetype_confirmed"
    elif "analyzing user profile" in line_lower or "profile analysis" in line_lower:
        return "profile_analysis"
    elif "health analysis" in line_lower:
        return "health_analysis"
    elif "behavior analysis" in line_lower:
        return "behavior_analysis"
    elif "nutrition plan" in line_lower:
        return "nutrition_planning"
    elif "routine plan" in line_lower:
        return "routine_planning"
    elif "generating" in line_lower:
        return "generating_plans"
    elif "completed" in line_lower or "finished" in line_lower:
        return "completed"
    elif "error" in line_lower:
        return "error"
    else:
        return "processing"

@app.get("/api/status")
async def get_status():
    """Get current API status and active processes"""
    return {
        "status": "running",
        "active_processes": len(active_processes),
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 