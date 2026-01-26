"""
Session API Endpoints
Handles session creation and management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# ===========================
# Request/Response Models
# ===========================

class SourceInput(BaseModel):
    """Source material input"""
    type: str = Field(..., description="Source type: text, pdf, web, youtube")
    content: Optional[str] = None
    url: Optional[str] = None
    file_path: Optional[str] = None  # For PDF uploads


class SessionCreateRequest(BaseModel):
    """Session creation request"""
    claim: str = Field(..., min_length=5, description="Learning claim")
    sources: List[SourceInput] = Field(..., min_items=1)
    tone: str = Field(default="friendly", description="Evaluation tone")
    difficulty: str = Field(default="medium", description="Starting difficulty")
    user_name: str = Field(default="Learner", description="User's name for personalization")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Initial confidence")


class SessionCreateResponse(BaseModel):
    """Session creation response"""
    session_id: str
    status: str
    message: str


class SessionStatusResponse(BaseModel):
    """Session status response"""
    session_id: str
    is_active: bool
    understanding_score: float
    questions_asked: int
    created_at: str


# ===========================
# Database Integration
# ===========================
from src.db.session import get_db
from src.db.models import Session
from sqlalchemy.orm import Session as DBSession
from fastapi import Depends

# ===========================
# Endpoints
# ===========================

@router.post("/session/create", response_model=SessionCreateResponse)
async def create_session(request: SessionCreateRequest, db: DBSession = Depends(get_db)):
    """
    Create a new evaluation session (Persisted in Postgres)
    """
    
    # Generate session ID
    session_id = str(uuid4())
    
    # Process sources with Extractor Agent (Unchanged logic)
    all_chunks = []
    extraction_metadata = []
    
    from src.agents.extractor import ExtractorAgent
    from src.models.agent_io import ExtractorInput
    
    extractor = ExtractorAgent()
    
    for source in request.sources:
        extractor_input = ExtractorInput(
            session_id=session_id,
            source_type=source.type,
            raw_text=source.content if source.type == "text" else None,
            source_url=source.url if source.type in ["youtube", "web", "website"] else None,
            file_path=source.file_path if source.type == "pdf" else None
        )
        
        result = extractor.execute(extractor_input)
        
        if result.success:
            all_chunks.extend(result.chunks)
            extraction_metadata.append({
                "source_type": source.type,
                "chunk_count": len(result.chunks),
                "word_count": result.metadata.get("word_count", 0)
            })
        else:
            logger.error(f"Extraction failed for {source.type}: {result.error}")
    
    # DB: Create Session Record
    db_session = Session(
        id=session_id,
        learning_claim=request.claim,
        user_name=request.user_name, 
        tone=request.tone,
        difficulty=request.difficulty,
        initial_confidence=request.confidence,
        understanding_score=50.0,
        questions_asked=0,
        is_active=True,
        created_at=datetime.utcnow(),
        metadata_json={
            "extraction_stats": extraction_metadata,
            "source_count": len(request.sources)
        }
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    logger.info(f"✅ Session {session_id} persisted to Postgres")
    
    return SessionCreateResponse(
        session_id=session_id,
        status="created",
        message=f"Session created. Processed {len(all_chunks)} chunks."
    )


@router.get("/session/{session_id}", response_model=SessionStatusResponse)
async def get_session_status(session_id: str, db: DBSession = Depends(get_db)):
    """Get session status from Postgres"""
    
    session = db.query(Session).filter(Session.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionStatusResponse(
        session_id=session.id,
        is_active=session.is_active,
        understanding_score=session.understanding_score,
        questions_asked=int(session.questions_asked),
        created_at=session.created_at.isoformat()
    )


@router.delete("/session/{session_id}")
async def end_session(session_id: str, db: DBSession = Depends(get_db)):
    """End an active session"""
    
    session = db.query(Session).filter(Session.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.is_active = False
    db.commit()
    
    return {
        "session_id": session_id,
        "status": "ended",
        "message": "Session ended successfully"
    }
