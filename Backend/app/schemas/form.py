from pydantic import BaseModel, EmailStr, Field
from datetime import date, time
from typing import Optional, List

class FormData(BaseModel):
    interaction_id: Optional[str] = None
    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = None
    interaction_date: Optional[date] = None
    interaction_time: Optional[time] = None
    attendees: List[str] = Field(default_factory=list)
    topics_discussed: Optional[str] = None
    materials_shared: List[str] = Field(default_factory=list)
    samples_distributed: List[str] = Field(default_factory=list)
    sentiment: Optional[str] = None # Positive, Neutral, Negative
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    status: str = "Draft"
