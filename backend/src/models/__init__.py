"""
Core Pydantic Models for SONA AI
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


# ===========================
# Source Models
# ===========================

class SourceType(str):
    """Source type enumeration"""
    PDF = "pdf"
    WEB = "web"
    YOUTUBE = "youtube"
    TEXT = "text"


class Source(BaseModel):
    """Learning material source"""
    source_id: UUID = Field(default_factory=uuid4)
    source_type: Literal["pdf", "web", "youtube", "text"]
    raw_content: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ===========================
# Claim Models
# ===========================

class Claim(BaseModel):
    """User's learning claim"""
    claim_id: UUID = Field(default_factory=uuid4)
    claim_text: str = Field(..., min_length=5, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ===========================
# Session Models
# ===========================

class SessionTone(str):
    """Session tone enumeration"""
    FRIENDLY = "friendly"
    STRICT = "strict"
    AGGRESSIVE = "aggressive"


class SessionDifficulty(str):
    """Initial difficulty preference"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Session(BaseModel):
    """Evaluation session"""
    session_id: UUID = Field(default_factory=uuid4)
    claim: Claim
    sources: list[Source]
    tone: Literal["friendly", "strict", "aggressive"] = "friendly"
    start_difficulty: Literal["easy", "medium", "hard"] = "medium"
    understanding_score: float = Field(default=50.0, ge=0.0, le=100.0)
    questions_asked: int = 0
    is_active: bool = True
    stopped_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ===========================
# Question Models
# ===========================

class QuestionType(str):
    """Question type enumeration"""
    FACT = "fact"
    REASONING = "reasoning"
    FAILURE = "failure"
    APPLICATION = "application"


class AnswerType(str):
    """Expected answer type"""
    SHORT = "short"
    EXPLANATION = "explanation"
    SCENARIO = "scenario"


class Question(BaseModel):
    """Generated question with metadata"""
    question_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    question_text: str
    difficulty: Literal["easy", "medium", "hard"]
    question_type: Literal["fact", "reasoning", "failure", "application"]
    expected_answer_type: Literal["short", "explanation", "scenario"]
    context_chunks: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ===========================
# Answer Models
# ===========================

class Answer(BaseModel):
    """User's answer to a question"""
    answer_id: UUID = Field(default_factory=uuid4)
    question_id: UUID
    answer_text: str
    is_voice: bool = False
    audio_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ===========================
# Evaluation Models
# ===========================

class EvaluationScores(BaseModel):
    """Evaluation scores for an answer"""
    correctness: float = Field(..., ge=0.0, le=100.0)
    depth: float = Field(..., ge=0.0, le=100.0)
    transfer: float = Field(..., ge=0.0, le=100.0)
    
    @property
    def answer_score(self) -> float:
        """Calculate final answer score"""
        return (
            0.5 * self.correctness +
            0.3 * self.depth +
            0.2 * self.transfer
        )


class Evaluation(BaseModel):
    """Complete answer evaluation"""
    evaluation_id: UUID = Field(default_factory=uuid4)
    answer_id: UUID
    scores: EvaluationScores
    reasoning: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
