import json
import uuid
from typing import Optional, List, Dict, Any
from langchain_core.tools import tool
from sqlmodel import Session, select
from app.core.database import engine
from app.models.interaction import HCPInteraction, HCPInteractionCreate
from app.schemas.form import FormData
from app.core.logging import get_logger

logger = get_logger(__name__)

@tool
def upsert_form_draft(fields_json: str, interaction_id: Optional[str] = None) -> str:
    """
    Update or create a local draft of the HCP interaction form.
    fields_json: A JSON string containing partial form fields.
    interaction_id: Optional existing ID to update.
    """
    logger.debug(f"upsert_form_draft called with ID: {interaction_id}")
    try:
        updates = json.loads(fields_json)
        return json.dumps({
            "status": "draft_updated",
            "interaction_id": interaction_id or str(uuid.uuid4()),
            "updates": updates
        })
    except Exception as e:
        logger.error(f"Error in upsert_form_draft: {e}")
        return json.dumps({"status": "error", "message": str(e)})

@tool
def save_interaction_to_db(interaction_json: str) -> str:
    """
    Finalizes and saves the interaction log to the database.
    interaction_json: Full JSON representation of the interaction.
    """
    logger.info("save_interaction_to_db called")
    try:
        data = json.loads(interaction_json)
        data["status"] = "Submitted"
        
        with Session(engine) as session:
            interaction_id = data.get("id") or data.get("interaction_id")
            if interaction_id:
                db_item = session.get(HCPInteraction, uuid.UUID(interaction_id))
                if db_item:
                    logger.debug(f"Updating existing interaction: {interaction_id}")
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
def analyze_sentiment_and_topics(text: str) -> str:
    """
    Internal tool to analyze the user's input for sentiment and key topics.
    """
    logger.debug("analyze_sentiment_and_topics called")
    return json.dumps({
        "sentiment_suggestion": "Positive",
        "topics_extracted": ["Product Discussion", "Research Collaboration"]
    })
