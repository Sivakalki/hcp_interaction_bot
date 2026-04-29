import uuid
from datetime import date, time, datetime
from typing import Optional, List
from sqlalchemy import Column, JSON, DateTime, func
from sqlmodel import Field, SQLModel

class HCPInteractionBase(SQLModel):
    hcp_name: str = Field(index=True)
    interaction_type: str = Field(default="Meeting")
    interaction_date: date = Field(default_factory=date.today)
    interaction_time: time = Field(default_factory=lambda: datetime.now().time())
    attendees: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    topics_discussed: Optional[str] = Field(default=None)
    materials_shared: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    samples_distributed: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    sentiment: Optional[str] = Field(default="Neutral")  # Positive, Neutral, Negative
    outcomes: Optional[str] = Field(default=None)
    follow_up_actions: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    dos: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    donts: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    future_tasks: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: str = Field(default="Draft") # Draft, Submitted

class HCPInteraction(HCPInteractionBase, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
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
    summary: Optional[str] = None
    dos: Optional[List[str]] = None
    donts: Optional[List[str]] = None
    future_tasks: Optional[List[str]] = None
    status: Optional[str] = None
