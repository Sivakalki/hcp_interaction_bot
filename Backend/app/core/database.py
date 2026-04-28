"""
Async PostgreSQL connection utility using SQLAlchemy 2.x + asyncpg.
Usage:
    async with get_db() as session:
        result = await session.execute(...)
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlmodel import SQLModel, create_engine, Session
from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DB_URL.replace("+asyncpg", ""), # SQLModel/SQLAlchemy sync for simpler boilerplate or keep async if desired. 
    # Let's stick to sync for simpler tool implementation in LangGraph for now, or use async if preferred.
    # User asked for SQLModel + Postgres.
    echo=settings.DEBUG,
)

def init_db():
    from app.models.interaction import HCPInteraction # Import to ensure registered
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
