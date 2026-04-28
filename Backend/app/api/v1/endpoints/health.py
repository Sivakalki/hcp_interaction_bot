"""
Health-check endpoint — useful for load balancers and container probes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, text
from app.core.database import get_session
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", summary="Liveness and Readiness probe")
async def health_check(session: Session = Depends(get_session)) -> dict[str, str]:
    """
    Check if the API is alive and the database is reachable.
    """
    logger.debug("Health check requested")
    try:
        session.exec(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "error", "database": "disconnected", "detail": str(e)}
