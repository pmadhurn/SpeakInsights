from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class Meeting(BaseModel):
    id: Optional[int] = None
    title: str
    date: datetime
    audio_path: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    action_items: Optional[List[str]] = []
    