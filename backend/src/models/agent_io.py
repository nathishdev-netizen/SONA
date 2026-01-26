"""
Agent Input/Output Models
Standardized data structures for agent communication
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


# ===========================
# Extractor Agent I/O
# ===========================

class ExtractorInput(BaseModel):
    """Input for content extraction agent"""
    session_id: str  # For Pinecone storage
    source_type: str
    source_url: Optional[str] = None
    file_path: Optional[str] = None
    raw_text: Optional[str] = None


class ExtractorOutput(BaseModel):
    """Output from content extraction agent"""
    success: bool
    raw_content: str
    title: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    chunks: List[str] = Field(default_factory=list)
    embeddings_stored: bool = False
    error: Optional[str] = None


# ===========================
# Interrogator Agent I/O
# ===========================

class InterrogatorInput(BaseModel):
    """Input for question generation agent"""
    session_id: UUID
    claim_text: str
    relevant_chunks: List[str]
    tone: str
    current_difficulty: str
    understanding_score: float
    previous_questions: List[str] = Field(default_factory=list)


class InterrogatorOutput(BaseModel):
    """Output from question generation agent"""
    question_text: str
    difficulty: str
    question_type: str
    expected_answer_type: str
    reasoning: str
    context_used: List[str] = Field(default_factory=list)


# ===========================
# Evaluator Agent I/O
# ===========================

class EvaluatorInput(BaseModel):
    """Input for answer evaluation agent"""
    session_id: str
    question_id: str
    question_text: str
    answer_text: str
    expected_answer_type: str = "text"
    difficulty: str = "medium"
    reference_chunks: List[str] = Field(default_factory=list)


class EvaluatorOutput(BaseModel):
    """Output from answer evaluation agent"""
    correctness_score: float = Field(..., ge=0.0, le=100.0)
    correctness_reasoning: str = ""
    depth_score: float = Field(..., ge=0.0, le=100.0)
    depth_reasoning: str = ""
    transfer_score: float = Field(..., ge=0.0, le=100.0)
    transfer_reasoning: str = ""
    overall_score: float = Field(..., ge=0.0, le=100.0)
    hallucination_detected: bool = False
    feedback: str = ""


# ===========================
# Conductor Agent I/O
# ===========================

class ConductorInput(BaseModel):
    """Input for session orchestration agent"""
    session_id: UUID
    understanding_score: float
    questions_asked: int
    recent_scores: List[float] = Field(default_factory=list)
    score_variance: float = 0.0


class ConductorOutput(BaseModel):
    """Output from session conductor agent"""
    should_continue: bool
    reason: str
    next_difficulty: Optional[str] = None
    recommendation: str


# ===========================
# Tutor Agent I/O
# ===========================

class TutorInput(BaseModel):
    """Input for tutor QA agent"""
    session_id: str
    user_question: str
    chat_history: List[str] = Field(default_factory=list)


class TutorOutput(BaseModel):
    """Output from tutor QA agent"""
    answer: str
    sources_used: List[str] = Field(default_factory=list)
    confidence: str = "high"
    follow_up_suggestion: Optional[str] = None
