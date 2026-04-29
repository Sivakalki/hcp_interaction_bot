"""
Pydantic v2 schemas for AI request/response contracts.
"""
from typing import Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Single message in a conversation turn."""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)


class AIChatRequest(BaseModel):
    """Request body for POST /api/v1/ai/chat."""
    messages: list[ChatMessage] = Field(..., min_length=1)
    session_id: str | None = Field(default=None, description="Optional session ID for continuity")
    interaction_id: str | None = Field(default=None, description="Current interaction ID being edited")
    form_data: dict[str, Any] | None = Field(default=None, description="Current state of the form fields")


class FormFieldUpdate(BaseModel):
    """A single field update suggested by the AI."""
    field: str = Field(..., description="Form field name, e.g. 'name', 'email'")
    value: Any = Field(..., description="Suggested value for the field")


class AIChatResponse(BaseModel):
    """Response body returned from POST /api/v1/ai/chat."""
    reply: str = Field(..., description="Human-readable assistant reply")
    form_updates: list[FormFieldUpdate] = Field(
        default_factory=list,
        description="Structured field updates to auto-populate the form",
    )
    session_id: str | None = None
