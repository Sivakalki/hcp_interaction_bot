from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
import uuid
from app.core.database import get_session
from app.models.interaction import HCPInteraction, HCPInteractionCreate, HCPInteractionRead
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/interactions", tags=["Interactions"])

@router.post("/", response_model=HCPInteractionRead, status_code=status.HTTP_201_CREATED)
def create_interaction(interaction: HCPInteractionCreate, session: Session = Depends(get_session)):
    logger.info(f"Creating new interaction for HCP: {interaction.hcp_name}")
    try:
        db_interaction = HCPInteraction.model_validate(interaction)
        session.add(db_interaction)
        session.commit()
        session.refresh(db_interaction)
        logger.info(f"Interaction created with ID: {db_interaction.id}")
        return db_interaction
    except Exception as e:
        logger.error(f"Failed to create interaction: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/", response_model=List[HCPInteractionRead])
def list_interactions(session: Session = Depends(get_session)):
    logger.debug("Listing all interactions")
    interactions = session.exec(select(HCPInteraction)).all()
    return interactions

@router.get("/{interaction_id}", response_model=HCPInteractionRead)
def get_interaction(interaction_id: uuid.UUID, session: Session = Depends(get_session)):
    logger.debug(f"Fetching interaction with ID: {interaction_id}")
    interaction = session.get(HCPInteraction, interaction_id)
    if not interaction:
        logger.warning(f"Interaction not found: {interaction_id}")
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction

@router.patch("/{interaction_id}", response_model=HCPInteractionRead)
def update_interaction(interaction_id: uuid.UUID, interaction_update: dict, session: Session = Depends(get_session)):
    logger.info(f"Updating interaction: {interaction_id}")
    db_interaction = session.get(HCPInteraction, interaction_id)
    if not db_interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    
    try:
        for key, value in interaction_update.items():
            if hasattr(db_interaction, key):
                setattr(db_interaction, key, value)
        
        session.add(db_interaction)
        session.commit()
        session.refresh(db_interaction)
        return db_interaction
    except Exception as e:
        logger.error(f"Failed to update interaction: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
