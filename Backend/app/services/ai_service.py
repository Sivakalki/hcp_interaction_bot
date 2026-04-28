"""
AI Service — thin orchestration layer between the FastAPI endpoint and LangGraph.
Converts API-level schemas into graph inputs and graph outputs back into API schemas.
"""
from datetime import datetime
import logging
import uuid
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.agent.graph import agent_graph
from app.core.exceptions import AIServiceError
from app.schemas.ai import AIChatRequest, AIChatResponse, FormFieldUpdate
from app.core.logging import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are HCPFiller AI, an intelligent assistant that helps users
log Healthcare Professional (HCP) interactions.

Your primary goal is to help the user complete the 'Log HCP Interaction' form.
Use the following tools:
1. upsert_form_draft: Use this whenever the user provides information for the form.
2. save_interaction_to_db: Use this when the user confirms they want to save/submit the log.
3. list_recent_interactions: Use this if the user asks to see previous logs.
4. load_interaction_detail: Use this if the user wants to view or edit a specific previous log.
5. analyze_sentiment_and_topics: Use this to help auto-suggest sentiment or topics.
6. search_interactions: Use this to filter logs.

### DATA HANDLING RULES:
- **Dates**: Always resolve relative dates (today, yesterday, tomorrow) using the current date provided in the state: {current_date}. Output in YYYY-MM-DD format.
- **Time**: Format as HH:mm (24-hour).
- **Participants (attendees)**: Extract as a LIST of strings. If the user mentions themselves as "Me" or "Me (Name)", prioritize extracting the name in parentheses (e.g., "Kalki") if provided; otherwise, use "Me".
- **Materials/Samples**: Always extract as LISTS of strings.
- **Outcomes & Follow-up**: Be thorough in extracting outcomes and specific follow-up actions mentioned.
- **Formatting Lists**: When listing interactions (from `list_recent_interactions` or `search_interactions`), ALWAYS present them as a Markdown table with columns: **Doctor Name** (hcp_name), **Interaction ID** (id), and **Date** (interaction_date).

Fields you can fill: hcp_name, interaction_type, interaction_date, interaction_time, attendees (list), topics_discussed, materials_shared (list), samples_distributed (list), sentiment (Positive/Neutral/Negative), outcomes, follow_up_actions.

Always respond with a concise, helpful message after performing a tool call.
"""


async def process_chat(request: AIChatRequest) -> AIChatResponse:
    """
    Invoke the LangGraph agent and return a structured AIChatResponse.

    Args:
        request: Validated AIChatRequest containing conversation history.

    Returns:
        AIChatResponse with the assistant's reply and any form field updates.

    Raises:
        AIServiceError: On any LangGraph / LLM failure.
    """
    session_id = request.session_id or str(uuid.uuid4())

    # Build initial state messages
    current_date_str = datetime.now().strftime("%Y-%m-%d")
    prompt_with_date = SYSTEM_PROMPT.replace("{current_date}", current_date_str)
    
    messages: list[Any] = [SystemMessage(content=prompt_with_date)]
    for msg in request.messages:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))

    try:
        result = await agent_graph.ainvoke(
            {
                "messages": messages,
                "form_updates": [],
                "session_id": session_id,
                "current_date": datetime.now().strftime("%Y-%m-%d"),
            }
        )
    except Exception as exc:
        logger.exception("LangGraph invocation failed: %s", exc)
        raise AIServiceError(f"LangGraph agent error: {exc}") from exc

    # Extract the final human-facing reply
    final_message = result["messages"][-1]
    reply: str = getattr(final_message, "content", "I'm sorry, something went wrong.")

    # Map harvested form updates → Pydantic schema
    form_updates = [
        FormFieldUpdate(field=upd["field"], value=upd["value"])
        for upd in result.get("form_updates", [])
    ]

    return AIChatResponse(
        reply=reply,
        form_updates=form_updates,
        session_id=session_id,
    )
