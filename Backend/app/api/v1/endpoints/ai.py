"""
AI chat endpoint — accepts user messages, invokes the LangGraph agent,
and returns both a text reply and structured form-field updates.
"""
import logging

from fastapi import APIRouter, status, HTTPException

from app.schemas.ai import AIChatRequest, AIChatResponse
from app.services.ai_service import process_chat
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post(
    "/chat",
    response_model=AIChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with the HCPFiller AI assistant",
)
async def chat(request: AIChatRequest) -> AIChatResponse:
    """
    Send one or more user messages and receive:
    - A natural-language **reply** from the assistant.
    - An optional list of **form_updates** to auto-populate the frontend form.
    """
    logger.info(f"AI Chat request received. Session ID: {request.session_id}")
    try:
        response = await process_chat(request)
        logger.info(f"AI Chat response generated. Form updates: {len(response.form_updates)}")
        return response
    except Exception as e:
        logger.error(f"AI Chat failed: {e}")
        raise HTTPException(status_code=500, detail="AI Service Error")
