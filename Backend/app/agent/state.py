"""
LangGraph agent state definition.
TypedDict keeps the state strictly typed and serializable.
"""
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    State that flows through the LangGraph graph.

    Attributes:
        messages: Accumulated conversation messages (managed by add_messages reducer).
        form_updates: Structured field updates extracted by the fill_form tool.
        session_id: Optional identifier to track multi-turn conversations.
        interaction_id: Current interaction ID being edited.
        current_date: To help LLM resolve "today", "yesterday", etc.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    form_updates: list[dict]   # list of {"field": str, "value": str}
    session_id: str | None
    interaction_id: str | None
    current_date: str | None
