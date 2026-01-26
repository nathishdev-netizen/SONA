"""
Chat API Endpoints
Handles question-answer flow during evaluation sessions
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Import DB session management
from src.db.session import get_db
from src.db.models import Session
from sqlalchemy.orm import Session as DBSession
from fastapi import Depends

# ===========================
# Request/Response Models
# ===========================

class QuestionResponse(BaseModel):
    """Question response"""
    question_id: str
    question_text: str
    difficulty: str
    question_type: str
    session_continues: bool
    source_context: Optional[str] = None # Added for hallucination check


class AnswerRequest(BaseModel):
    """Answer submission request"""
    question_id: str
    answer: str
    is_voice: bool = False


class EvaluationResponse(BaseModel):
    """Answer evaluation response"""
    answer_id: str
    scores: dict
    understanding_score: float
    should_continue: bool
    next_difficulty: Optional[str] = None
    feedback: Optional[str] = None


# ===========================
# Mock Question Bank (Deprecated but kept for reference)
# ===========================
MOCK_QUESTIONS = {
    "easy": ["What is the main concept?"],
    "medium": ["How does this work?"],
    "hard": ["What if this failed?"]
}


# ===========================
# Endpoints
# ===========================

@router.get("/session/greeting/{session_id}")
async def start_session_greeting(session_id: str):
    """
    Generate the initial greeting for the session
    """
    try:
        from src.agents.interrogator import InterrogatorAgent
        agent = InterrogatorAgent()
        
        greeting = agent.generate_greeting(session_id)
        
        return {
            "greeting": greeting,
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/question/{session_id}", response_model=QuestionResponse)
async def get_next_question(session_id: str, db: DBSession = Depends(get_db)):
    """
    Get next question for the session
    Uses Interrogator Agent to generate adaptive questions
    """
    
    # Fetch Session from DB
    session = db.query(Session).filter(Session.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.is_active:
        raise HTTPException(status_code=400, detail="Session is not active")
    
    try:
        # Initialize Interrogator Agent
        from src.agents.interrogator import InterrogatorAgent
        from src.models.agent_io import InterrogatorInput
        
        agent = InterrogatorAgent()
        
        # Extract previous questions from messages (stored in metadata_json or separate table in future)
        # For MVP Phase 1 (Postgres Migration), we will parse JSON metadata or assume empty history
        # TODO: Move messages to separate Message table for full history
        previous_questions = []
        # if session.metadata_json and "messages" in session.metadata_json:
        #    ... (Logic to parse history)
        
        # Prepare input for agent
        # Note: session.learning_claim, session.tone etc are now available on the object
        input_data = InterrogatorInput(
            session_id=session_id,
            claim_text=session.learning_claim,
            # Chunks are stored in metadata_json in create_session currently
            relevant_chunks=(session.metadata_json or {}).get("chunks", []),
            tone=session.tone,
            current_difficulty=session.difficulty,
            understanding_score=session.understanding_score,
            previous_questions=previous_questions
        )
        
        # Execute agent
        result = agent.execute(input_data)
        
        # Generate question ID
        questions_asked = int(session.questions_asked)
        question_id = f"q{questions_asked + 1}"
        
        # We don't have a messages table yet, so we won't persist the question until answered
        # or we could store temporary state in metadata_json
        
        return QuestionResponse(
            question_id=question_id,
            question_text=result.question_text,
            difficulty=result.difficulty,
            question_type=result.question_type,
            session_continues=True,
            source_context="\n\n".join(result.context_used) if result.context_used else "No specific context retrieved."
        )
        
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error generating question: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Question generation failed: {str(e)}")


@router.post("/chat/answer/{session_id}", response_model=EvaluationResponse)
async def submit_answer(session_id: str, request: AnswerRequest, db: DBSession = Depends(get_db)):
    """
    Submit answer and get evaluation
    """
    session = db.query(Session).filter(Session.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.is_active:
        raise HTTPException(status_code=400, detail="Session is not active")
    
    # Generate answer ID
    answer_id = str(uuid4())
    
    # Use real Evaluator Agent for scoring
    from src.agents.evaluator import EvaluatorAgent
    from src.models.agent_io import EvaluatorInput
    
    evaluator = EvaluatorAgent()
    
    # Get context chunks from session metadata
    metadata = session.metadata_json or {}
    reference_chunks = metadata.get("chunks", [])[:5]  # Top 5 chunks
    
    # Find question text - basic logic for MVP
    # Ideally should query a Message table
    question_text = "Unknown question"
    difficulty = session.difficulty
    
    # Prepare evaluator input
    evaluator_input = EvaluatorInput(
        session_id=session_id,
        question_id=request.question_id,
        question_text=question_text, # Passed from frontend in request ideally, or stored in temp state
        answer_text=request.answer,
        expected_answer_type="text",
        difficulty=difficulty,
        reference_chunks=reference_chunks
    )
    
    # Execute evaluation
    eval_result = evaluator.execute(evaluator_input)
    
    correctness = eval_result.correctness_score
    depth = eval_result.depth_score
    transfer = eval_result.transfer_score
    answer_score = eval_result.overall_score
    
    # Update understanding score (60-40 formula)
    previous_score = session.understanding_score
    new_understanding = 0.6 * previous_score + 0.4 * answer_score
    session.understanding_score = new_understanding
    
    # Increment questions asked
    session.questions_asked += 1
    
    # Determine if should continue
    should_continue = int(session.questions_asked) < 5
    
    # Persist changes
    db.commit()
    
    # Determine next difficulty
    next_difficulty = None
    if should_continue:
        if new_understanding > 75:
            next_difficulty = "hard"
        elif new_understanding > 50:
            next_difficulty = "medium"
        else:
            next_difficulty = "easy"
            
    # For MVP: Update difficulty in DB for next question
    if next_difficulty:
        session.difficulty = next_difficulty
        db.commit()
    
    return EvaluationResponse(
        answer_id=answer_id,
        scores={
            "correctness": correctness,
            "depth": depth,
            "transfer": transfer,
            "answer_score": round(answer_score, 1)
        },
        understanding_score=round(new_understanding, 1),
        should_continue=should_continue,
        next_difficulty=next_difficulty,
        feedback=None
    )


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str, db: DBSession = Depends(get_db)):
    """Get full conversation history for a session"""
    session = db.query(Session).filter(Session.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # history = [] # Fetch from Message table later
    
    return {
        "session_id": session.id,
        "messages": [], # Placeholder until Message table is implemented
        "questions_asked": int(session.questions_asked),
        "understanding_score": session.understanding_score
    }


# ===========================
# Tutor Endpoint (Phase 6)
# ===========================

class TutorRequest(BaseModel):
    """Request to ask the tutor a question"""
    question: str = Field(..., min_length=2)


class TutorResponse(BaseModel):
    """Response from the tutor"""
    answer: str
    sources: List[str]
    confidence: str
    follow_up: Optional[str] = None


@router.post("/chat/ask/{session_id}", response_model=TutorResponse)
async def ask_tutor(session_id: str, request: TutorRequest, db: DBSession = Depends(get_db)):
    """
    Ask the tutor a question about the material (RAG)
    """
    
    session = db.query(Session).filter(Session.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Initialize Tutor Agent
    try:
        from src.agents.tutor import TutorAgent
        from src.models.agent_io import TutorInput
        
        agent = TutorAgent()
        
        tutor_input = TutorInput(
            session_id=session_id,
            user_question=request.question,
            chat_history=[]  # Can add history later if needed
        )
        
        result = agent.execute(tutor_input)
        
        return TutorResponse(
            answer=result.answer,
            sources=result.sources_used,
            confidence=result.confidence,
            follow_up=result.follow_up_suggestion
        )
        
    except Exception as e:
        logger.error(f"Tutor error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Tutor failed: {str(e)}")
class FeedbackRequest(BaseModel):
    session_id: str
    score: float
    comment: Optional[str] = None

@router.post("/chat/feedback")
async def log_session_feedback(request: FeedbackRequest):
    """Log user feedback to Opik"""
    try:
        from src.opik_integration.tracing import opik_integration
        # Uses session_id as trace_id proxy for now to link feedback to the session stream
        opik_integration.log_feedback(
            trace_id=request.session_id, 
            score=request.score,
            comment=request.comment
        )
        return {"status": "success", "message": "Feedback logged"}
    except Exception as e:
        logger.error(f"Feedback logging failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
