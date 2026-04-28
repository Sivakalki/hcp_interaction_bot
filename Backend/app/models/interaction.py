import uuid
from datetime import date, time, datetime
from typing import Optional, List
from sqlalchemy import Column, JSON, DateTime, func
from sqlmodel import Field, SQLModel

class HCPInteractionBase(SQLModel):
    hcp_name: str
    interaction_type: str
    interaction_date: date
    interaction_time: time
    attendees: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    topics_discussed: str
    materials_shared: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    samples_distributed: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    sentiment: str  # Positive, Neutral, Negative
    outcomes: str
    follow_up_actions: str
    status: str = Field(default="Draft") # Draft, Submitted

class HCPInteraction(HCPInteractionBase, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    )

class HCPInteractionCreate(HCPInteractionBase):
    pass

class HCPInteractionRead(HCPInteractionBase):
    id: uuid.UUID

class HCPInteractionUpdate(SQLModel):
    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = None
    interaction_date: Optional[date] = None
    interaction_time: Optional[time] = None
    attendees: Optional[List[str]] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[List[str]] = None
    samples_distributed: Optional[List[str]] = None
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    status: Optional[str] = None
