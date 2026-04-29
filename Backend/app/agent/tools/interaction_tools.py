import json
import uuid
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from langchain_core.tools import tool
from sqlmodel import Session, select
from app.core.database import engine
from app.models.interaction import HCPInteraction, HCPInteractionCreate
from app.schemas.form import FormData
from app.core.logging import get_logger

logger = get_logger(__name__)

@tool
def upsert_form_draft(
    hcp_name: Optional[str] = None,
    interaction_type: Optional[str] = None,
    interaction_date: Optional[str] = None,
    interaction_time: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    topics_discussed: Optional[str] = None,
    materials_shared: Optional[List[str]] = None,
    samples_distributed: Optional[List[str]] = None,
    sentiment: Optional[str] = None,
    outcomes: Optional[str] = None,
    follow_up_actions: Optional[str] = None,
    summary: Optional[str] = None,
    dos: Optional[List[str]] = None,
    donts: Optional[List[str]] = None,
    future_tasks: Optional[List[str]] = None,
    interaction_id: Optional[str] = None
) -> str:
    """
    Update or create a local draft of the HCP interaction form.
    Pass only the fields that need updating.
    """
    logger.debug(f"upsert_form_draft called with ID: {interaction_id}")
    try:
        # Filter out None values to only include provided updates
        updates = {
            k: v for k, v in {
                "hcp_name": hcp_name,
                "interaction_type": interaction_type,
                "interaction_date": interaction_date,
                "interaction_time": interaction_time,
                "attendees": attendees,
                "topics_discussed": topics_discussed,
                "materials_shared": materials_shared,
                "samples_distributed": samples_distributed,
                "sentiment": sentiment,
                "outcomes": outcomes,
                "follow_up_actions": follow_up_actions,
                "summary": summary,
                "dos": dos,
                "donts": donts,
                "future_tasks": future_tasks,
            }.items() if v is not None
        }
        
        return json.dumps({
            "status": "draft_updated",
            "interaction_id": interaction_id or str(uuid.uuid4()),
            "updates": updates
        })
    except Exception as e:
        logger.error(f"Error in upsert_form_draft: {e}")
        return json.dumps({"status": "error", "message": str(e)})

@tool
def save_interaction_to_db(
    hcp_name: str,
    interaction_type: Optional[str] = "Meeting",
    interaction_date: Optional[str] = None,
    interaction_time: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    topics_discussed: Optional[str] = None,
    materials_shared: Optional[List[str]] = None,
    samples_distributed: Optional[List[str]] = None,
    sentiment: Optional[str] = "Neutral",
    outcomes: Optional[str] = None,
    follow_up_actions: Optional[str] = None,
    summary: Optional[str] = None,
    dos: Optional[List[str]] = None,
    donts: Optional[List[str]] = None,
    future_tasks: Optional[List[str]] = None,
    interaction_id: Optional[str] = None
) -> str:
    """
    Finalizes and saves the interaction log to the database.
    Pass all fields individually. interaction_id is optional if updating.
    """
    logger.info(f"save_interaction_to_db called for HCP: {hcp_name}")
    try:
        data = {
            "hcp_name": hcp_name,
            "interaction_type": interaction_type or "Meeting",
            "interaction_date": interaction_date or str(date.today()),
            "interaction_time": interaction_time or datetime.now().strftime("%H:%M"),
            "attendees": attendees or [],
            "topics_discussed": topics_discussed or "",
            "materials_shared": materials_shared or [],
            "samples_distributed": samples_distributed or [],
            "sentiment": sentiment or "Neutral",
            "outcomes": outcomes or "",
            "follow_up_actions": follow_up_actions or "",
            "summary": summary or "",
            "dos": dos or [],
            "donts": donts or [],
            "future_tasks": future_tasks or [],
            "status": "Submitted"
        }
        
        with Session(engine) as session:
            target_id = interaction_id
            if target_id:
                db_item = session.get(HCPInteraction, uuid.UUID(target_id))
                if db_item:
                    logger.debug(f"Updating existing interaction: {target_id}")
                    for key, value in data.items():
                        if hasattr(db_item, key):
                            setattr(db_item, key, value)
                    session.add(db_item)
                    session.commit()
                    session.refresh(db_item)
                    return json.dumps({"status": "saved", "id": str(db_item.id)})

            logger.debug("Creating new interaction record")
            db_item = HCPInteraction.model_validate(data)
            session.add(db_item)
            session.commit()
            session.refresh(db_item)
            logger.info(f"Interaction saved with ID: {db_item.id}")
            return json.dumps({"status": "saved", "id": str(db_item.id)})
    except Exception as e:
        logger.error(f"Error in save_interaction_to_db: {e}")
        return json.dumps({"status": "error", "message": str(e)})

@tool
def list_recent_interactions() -> str:
    """
    Fetches a list of the 10 most recent HCP interaction logs.
    """
    logger.debug("list_recent_interactions called")
    try:
        with Session(engine) as session:
            statement = select(HCPInteraction).order_by(HCPInteraction.interaction_date.desc()).limit(10)
            results = session.exec(statement).all()
            return json.dumps({"status": "success", "interactions": [{"id": str(r.id), "hcp_name": r.hcp_name, "date": str(r.interaction_date)} for r in results]})
    except Exception as e:
        logger.error(f"Error in list_recent_interactions: {e}")
        return json.dumps({"status": "error", "message": str(e)})

@tool
def load_interaction_detail(interaction_id: str) -> str:
    """
    Loads the full details of a specific interaction by its ID.
    """
    logger.debug(f"load_interaction_detail called for ID: {interaction_id}")
    try:
        with Session(engine) as session:
            item = session.get(HCPInteraction, uuid.UUID(interaction_id))
            if not item:
                return json.dumps({"status": "error", "message": "Not found"})
            return json.dumps({"status": "loaded", "data": item.model_dump(mode='json')})
    except Exception as e:
        logger.error(f"Error in load_interaction_detail: {e}")
        return json.dumps({"status": "error", "message": str(e)})

@tool
def search_interactions(sentiment: Optional[str] = None, interaction_date: Optional[str] = None) -> str:
    """
    Search for interaction logs based on sentiment or date.
    sentiment: "Positive", "Neutral", or "Negative".
    interaction_date: Date string in "YYYY-MM-DD" format.
    """
    logger.debug(f"search_interactions called with sentiment={sentiment}, date={interaction_date}")
    try:
        with Session(engine) as session:
            statement = select(HCPInteraction)
            if sentiment:
                statement = statement.where(HCPInteraction.sentiment == sentiment)
            if interaction_date:
                # Convert string to date object for comparison
                search_date = date.fromisoformat(interaction_date)
                statement = statement.where(HCPInteraction.interaction_date == search_date)
            
            results = session.exec(statement).all()
            summary = [
                {"id": str(r.id), "hcp_name": r.hcp_name, "date": str(r.interaction_date), "sentiment": r.sentiment} 
                for r in results
            ]
            return json.dumps({"status": "success", "count": len(summary), "interactions": summary})
    except Exception as e:
        logger.error(f"Error in search_interactions: {e}")
        return json.dumps({"status": "error", "message": str(e)})

@tool
def analyze_interaction(text: str) -> str:
    """
    Analyzes the interaction text to extract sentiment, topics, and a structured summary 
    including recommended actions (dos), what to avoid (donts), and future tasks.
    """
    logger.debug("analyze_interaction called")
    # For now, this returns a structured response that the agent can use to suggest form updates.
    # In a production environment, this would call a specialized analysis model.
    return json.dumps({
        "sentiment": "Positive",
        "topics": ["Product Discussion", "Research Collaboration"],
        "summary": "The interaction was professional and focused on potential research synergy.",
        "dos": ["Provide follow-up technical documentation", "Clarify timeline for next phase"],
        "donts": ["Do not mention pricing at this early stage", "Avoid over-promising on delivery dates"],
        "future_tasks": ["Send research whitepaper", "Coordinate with the medical affairs team"]
    })

@tool
def reset_current_form() -> str:
    """
    Clears all fields in the current local draft and generates a new interaction ID.
    Use this if the user wants to start a completely new log.
    """
    logger.info("reset_current_form called")
    return json.dumps({
        "status": "reset", 
        "interaction_id": str(uuid.uuid4()), 
        "message": "Form cleared."
    })

@tool
def validate_and_compare_fields(proposed_updates: str, current_fields: str) -> str:
    """
    Compares AI-extracted fields with existing form data to detect 
    contradictions before updating the draft.
    proposed_updates: JSON string of new field values.
    current_fields: JSON string of existing form data.
    """
    logger.info("validate_and_compare_fields called")
    try:
        proposed = json.loads(proposed_updates)
        current = json.loads(current_fields)
        
        conflicts = []
        for key, new_val in proposed.items():
            if key in current and current[key]:
                old_val = current[key]
                # Simple equality check for strings/numbers/bools
                # For lists, check if the new list is completely different or just adding?
                # Usually, we want to flag if a field is being OVERWRITTEN with a DIFFERENT value.
                if old_val != new_val:
                    # Special check for lists to see if it's a subset or extension
                    if isinstance(old_val, list) and isinstance(new_val, list):
                        if not all(item in new_val for item in old_val):
                            conflicts.append(key)
                    else:
                        conflicts.append(key)
        
        if conflicts:
            logger.warning(f"Conflicts detected in fields: {conflicts}")
            return json.dumps({"status": "review_required", "conflicts": conflicts})
        
        return json.dumps({"status": "validated", "message": "No major contradictions found."})
    except Exception as e:
        logger.error(f"Error in validate_and_compare_fields: {e}")
        return json.dumps({"status": "error", "message": str(e)})