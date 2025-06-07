from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
from datetime import datetime

from .transcription import transcribe_audio
from .nlp_module import summarize_text, analyze_sentiment, extract_action_items
from .database import save_meeting, get_all_meetings, get_meeting_by_id

app = FastAPI(title="SpeakInsights API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
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
    return {"message": "SpeakInsights API is running!", "version": "1.0"}

@app.post("/api/meetings/upload")
async def upload_meeting(
    title: str,
    audio_file: UploadFile = File(...)
):
    """Process and save a new meeting"""
    
    # Save audio file
    os.makedirs("data/audio", exist_ok=True)
    audio_path = f"data/audio/{audio_file.filename}"
    
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)
    
    try:
        # Process the meeting
        transcript = transcribe_audio(audio_path)
        
        if transcript.startswith("Error"):
            raise HTTPException(status_code=500, detail=transcript)
        
        # Generate insights
        summary = summarize_text(transcript)
        sentiment = analyze_sentiment(transcript)
        action_items = extract_action_items(transcript)
        
        # Save to database
        meeting_data = {
            "title": title,
            "date": datetime.now().isoformat(),
            "transcript": transcript,
            "summary": summary,
            "sentiment": sentiment,
            "action_items": action_items,
            "audio_filename": audio_file.filename
        }
        
        meeting_id = save_meeting(meeting_data)
        meeting_data["id"] = meeting_id
        
        return meeting_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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