from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
from datetime import datetime
from pathlib import Path

from .transcription import transcribe_audio
from .nlp_module import summarize_text, analyze_sentiment, extract_action_items
from .database import save_meeting, get_all_meetings, get_meeting_by_id
from config import config

app = FastAPI(
    title=config.APP_TITLE,
    version=config.APP_VERSION,
    description="AI-powered meeting transcription and analysis"
)

# Enable CORS with specific origins for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

class MeetingResponse(BaseModel):
    id: int
    title: str
    date: str
    transcript: str
    summary: str
    sentiment: str
    action_items: List[str]
    audio_filename: Optional[str]

@app.get("/")
def read_root():
    return {
        "message": f"{config.APP_TITLE} API is running!", 
        "version": config.APP_VERSION,
        "status": "healthy"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        from .database import get_database_connection
        conn, db_type = get_database_connection()
        conn.close()
        return {
            "status": "healthy",
            "database": db_type,
            "version": config.APP_VERSION
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/api/meetings/upload")
async def upload_meeting(
    title: str,
    audio_file: UploadFile = File(...)
):
    """Process and save a new meeting"""
    
    # Validate input
    if not title or not title.strip():
        raise HTTPException(status_code=400, detail="Meeting title is required")
    
    if not audio_file.filename:
        raise HTTPException(status_code=400, detail="Audio file is required")
    
    # Validate file type
    allowed_extensions = {'.mp3', '.wav', '.m4a', '.mp4', '.avi', '.mov', '.flac'}
    file_extension = Path(audio_file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size
    if audio_file.size and audio_file.size > config.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size: {config.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    # Create upload directory
    upload_dir = Path(config.UPLOAD_FOLDER)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate safe filename
    safe_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{audio_file.filename}"
    audio_path = upload_dir / safe_filename
    
    try:
        # Save audio file
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        
        # Process the meeting
        transcript = transcribe_audio(str(audio_path))
        
        if transcript.startswith("Error"):
            # Clean up uploaded file on transcription error
            if audio_path.exists():
                audio_path.unlink()
            raise HTTPException(status_code=500, detail=transcript)
        
        # Generate insights
        try:
            summary = summarize_text(transcript)
            sentiment = analyze_sentiment(transcript)
            action_items = extract_action_items(transcript)
        except Exception as e:
            print(f"Warning: NLP processing failed: {e}")
            summary = "Summary generation failed"
            sentiment = "neutral"
            action_items = []
        
        # Save to database
        meeting_data = {
            "title": title.strip(),
            "date": datetime.now().isoformat(),
            "transcript": transcript,
            "summary": summary,
            "sentiment": sentiment,
            "action_items": action_items,
            "audio_filename": safe_filename
        }
        
        meeting_id = save_meeting(meeting_data)
        meeting_data["id"] = meeting_id
        
        return meeting_data
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up uploaded file on error
        if audio_path.exists():
            audio_path.unlink()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/api/meetings", response_model=List[MeetingResponse])
def get_meetings():
    """Get all meetings"""
    return get_all_meetings()

@app.get("/api/meetings/{meeting_id}", response_model=MeetingResponse)
def get_meeting(meeting_id: int):
    """Get specific meeting by ID"""
    meeting = get_meeting_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting