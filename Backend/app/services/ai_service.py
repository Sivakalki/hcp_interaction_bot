"""
AI Service — thin orchestration layer between the FastAPI endpoint and LangGraph.
Converts API-level schemas into graph inputs and graph outputs back into API schemas.
"""
from datetime import datetime
import json
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
1. upsert_form_draft: Use this whenever the user provides information for the form. Pass all extracted fields as individual arguments.
2. save_interaction_to_db: Use this when the user confirms they want to save/submit the log. Pass all form fields individually.
3. list_recent_interactions: Use this if the user asks to see previous logs.
4. load_interaction_detail: Use this if the user wants to view or edit a specific previous log.
5. analyze_interaction: Use this to get a comprehensive analysis of the interaction including sentiment, topics, a summary, recommended actions (dos), things to avoid (donts), and future tasks.
6. search_interactions: Use this to filter logs.
7. reset_current_form: Use this if the user explicitly wants to clear the form or start a new log from scratch.
8. validate_and_compare_fields: Use this to compare proposed updates with existing form data if there might be contradictions.

### CONTEXT:
- **Current Date**: {current_date}
- **Current Interaction ID**: {interaction_id}
- **Current Form Data**: {form_data}

### DATA HANDLING RULES:
- **Interaction ID**: If a 'Current Interaction ID' is provided above, you MUST use it for `upsert_form_draft` and other tools unless the user explicitly refers to a DIFFERENT interaction. If no ID is provided, tools will create a new one.
- **Sentiment Update**: If the user asks to update sentiment or any field without specifying which interaction, assume they mean the one currently in the form (see 'Current Form Data').
- **Dates**: Always resolve relative dates (today, yesterday, tomorrow) using the current date provided. Output in YYYY-MM-DD format.
- **Time**: Format as HH:mm (24-hour).
- **Participants (attendees)**: Extract as a LIST of strings.
- **Materials/Samples**: Always extract as LISTS of strings.
- **Formatting Lists**: When listing interactions, ALWAYS present them as a Markdown table with columns: **Doctor Name** (hcp_name), **Interaction ID** (id), and **Date** (interaction_date).

Fields you can fill: hcp_name, interaction_type, interaction_date, interaction_time, attendees (list), topics_discussed, materials_shared (list), samples_distributed (list), sentiment (Positive/Neutral/Negative), outcomes, follow_up_actions.

- **Analysis Section**: When you use the `analyze_interaction` tool, you MUST include a professional summary of the analysis in your chat response. Use the following format:
  - **Summary**: [Concise summary]
  - **Strategic Dos**: [List]
  - **Strategic Don'ts**: [List]
  - **Future Pipeline**: [List]

Always respond with a concise, helpful message after performing a tool call.
"""


async def process_chat(request: AIChatRequest) -> AIChatResponse:
    """
    Invoke the LangGraph agent and return a structured AIChatResponse.
    """
    session_id = request.session_id or str(uuid.uuid4())
    interaction_id = request.interaction_id
    form_data_str = json.dumps(request.form_data, indent=2) if request.form_data else "None"

    # Build initial state messages
    current_date_str = datetime.now().strftime("%Y-%m-%d")
    prompt_with_context = (
        SYSTEM_PROMPT.replace("{current_date}", current_date_str)
        .replace("{interaction_id}", interaction_id or "None")
        .replace("{form_data}", form_data_str)
    )
    
    # We only take the last user message as per request (no history)
    last_user_message = next((msg for msg in reversed(request.messages) if msg.role == "user"), None)
    
    messages: list[Any] = [SystemMessage(content=prompt_with_context)]
    if last_user_message:
        messages.append(HumanMessage(content=last_user_message.content))

    try:
        result = await agent_graph.ainvoke(
            {
                "messages": messages,
                "form_updates": [],
                "session_id": session_id,
                "interaction_id": interaction_id,
                "current_date": current_date_str,
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
