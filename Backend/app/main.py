import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.v1.endpoints.ai import router as ai_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.interactions import router as interaction_router
from app.core.database import init_db
from app.core.logging import setup_logging

def create_app() -> FastAPI:
    # Initialize Logging
    setup_logging()
    
    # Initialize DB tables
    init_db()
    
    settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(ai_router, prefix="/api/v1")
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(interaction_router, prefix="/api/v1")
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")
