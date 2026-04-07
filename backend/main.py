from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic_settings import BaseSettings
import os
import sys

# Ensure services module can be found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.gemini_extractor import configure_gemini, extract_meeting_intelligence

class Settings(BaseSettings):
    gemini_api_key: str = ""
    database_url: str = "postgresql://user:pass@localhost:5432/meetings_db"
    
    class Config:
        env_file = ".env"

settings = Settings()
if settings.gemini_api_key:
    configure_gemini(settings.gemini_api_key)

app = FastAPI(title="Meeting Intelligence Hub")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "message": "Meeting Intelligence Hub API is running"}

@app.post("/api/v1/transcripts/upload")
async def upload_transcript(file: UploadFile = File(...)):
    if file.content_type not in ["text/plain", "text/vtt"] and not file.filename.endswith(('.txt', '.vtt')):
        raise HTTPException(status_code=400, detail="Only .txt or .vtt allowed")
        
    content = await file.read()
    transcript_text = content.decode('utf-8')
    
    # Process with Gemini
    intelligence = await extract_meeting_intelligence(transcript_text)
    
    return {
        "transcript_id": "gemini-uuid-123",
        "status": "completed",
        "data": intelligence,
        "message": f"File {file.filename} processed successfully."
    }

# Mount static files (frontend)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
