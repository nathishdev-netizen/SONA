"""
SONA AI - FastAPI Backend Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.core.logging import setup_logging

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered learning evaluation system",
    debug=settings.debug,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================
# Routes
# ===========================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "opik_enabled": bool(settings.opik_api_key),
        "pinecone_enabled": bool(settings.pinecone_api_key),
    }


# ===========================
# API Routes
# ===========================

from src.api.v1 import session, chat

app.include_router(session.router, prefix="/api/v1", tags=["sessions"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )
