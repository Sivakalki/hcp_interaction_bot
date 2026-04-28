"""
LangGraph StateGraph definition for the HCPFiller AI agent.

Graph topology:
    START → llm_node → [tool_node (conditional)] → END
                 ↑_______________|

- llm_node  : Calls ChatGroq with tool-binding; produces an AI message.
- tool_node : Executes any requested tools (fill_form) and feeds results back.
- The graph loops until the LLM produces a final response with no tool calls.
"""
import json
import logging
from typing import Literal

from langchain_core.messages import AIMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.core.config import get_settings
from app.agent.state import AgentState
from app.agent.tools.interaction_tools import (
    upsert_form_draft,
    save_interaction_to_db,
    list_recent_interactions,
    load_interaction_detail,
    analyze_sentiment_and_topics,
    search_interactions,
)

logger = logging.getLogger(__name__)
settings = get_settings()

# ── Tool registry ──────────────────────────────────────────────────────────────
TOOLS = [
    upsert_form_draft,
    save_interaction_to_db,
    list_recent_interactions,
    load_interaction_detail,
    analyze_sentiment_and_topics,
    search_interactions,
]

# ── LLM with tool binding ──────────────────────────────────────────────────────
llm = ChatGroq(
    model=settings.GROQ_MODEL,
    api_key=settings.GROQ_API_KEY,
    temperature=0.1, # Lower temperature for tool accuracy
).bind_tools(TOOLS)


# ── Node: call the LLM ────────────────────────────────────────────────────────
def llm_node(state: AgentState) -> dict:
    """Invoke the LLM and append its response to messages."""
    logger.debug("llm_node called")
    response: AIMessage = llm.invoke(state["messages"])
    return {"messages": [response]}


# ── Edge: decide whether to call a tool or finish ─────────────────────────────
def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """Route to tools node if the LLM requested tool calls, else end."""
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "__end__"


# ── Node: execute tools & harvest form_updates ────────────────────────────────
tool_node = ToolNode(TOOLS)


def harvest_form_updates(state: AgentState) -> dict:
    """
    Parse results from interaction tools and accumulate form_updates.
    """
    form_updates: list[dict] = list(state.get("form_updates") or [])

    for msg in state["messages"]:
        if isinstance(msg, ToolMessage):
            try:
                result = json.loads(msg.content)
                if msg.name == "upsert_form_draft" and result.get("status") == "draft_updated":
                    updates = result.get("updates", {})
                    for k, v in updates.items():
                        form_updates.append({"field": k, "value": v})
                    # Also pass back the interaction_id if it was generated/updated
                    if "interaction_id" in result:
                        form_updates.append({"field": "interaction_id", "value": result["interaction_id"]})
                elif msg.name == "load_interaction_detail" and result.get("status") == "loaded":
                    data = result.get("data", {})
                    for k, v in data.items():
                        # Map backend 'id' to frontend 'interaction_id'
                        if k == "id":
                            form_updates.append({"field": "interaction_id", "value": v})
                        else:
                            form_updates.append({"field": k, "value": v})
            except Exception:
                continue

    return {"form_updates": form_updates}


# ── Build the graph ────────────────────────────────────────────────────────────
def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("llm", llm_node)
    graph.add_node("tools", tool_node)
    graph.add_node("harvest", harvest_form_updates)

    graph.add_edge(START, "llm")
    graph.add_conditional_edges("llm", should_continue, {"tools": "tools", "__end__": END})
    graph.add_edge("tools", "harvest")
    graph.add_edge("harvest", "llm")

    return graph.compile()


# Singleton compiled graph
agent_graph = build_graph()
