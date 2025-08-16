#!/usr/bin/env python3
"""Simple API server for external access to SpeakInsights data"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.database import get_all_meetings, get_meeting_by_id, get_database_connection

app = FastAPI(title="SpeakInsights API", version="1.0.0")

# Enable CORS for external access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "SpeakInsights API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    try:
        conn, db_type = get_database_connection()
        conn.close()
        return {
            "status": "healthy",
            "database": db_type,
            "message": "Database connection successful"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.get("/meetings")
async def get_meetings():
    """Get all meetings from database"""
    try:
        meetings = get_all_meetings()
        return {
            "count": len(meetings),
            "meetings": meetings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching meetings: {str(e)}")

@app.get("/meetings/{meeting_id}")
async def get_meeting(meeting_id: int):
    """Get specific meeting by ID"""
    try:
        meeting = get_meeting_by_id(meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        return meeting
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching meeting: {str(e)}")

@app.get("/database/info")
async def database_info():
    """Get database connection information"""
    try:
        conn, db_type = get_database_connection()
        
        # Get basic stats
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM meetings")
        meeting_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "database_type": db_type,
            "meeting_count": meeting_count,
            "connection_info": {
                "host": "localhost" if db_type == "sqlite" else "postgres",
                "port": 5432 if db_type == "postgresql" else None,
                "database": "speakinsights" if db_type == "postgresql" else "speakinsights.db"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
