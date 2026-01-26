from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    learning_claim = Column(Text, nullable=False)
    user_name = Column(String, default="Learner")
    tone = Column(String, default="friendly")
    difficulty = Column(String, default="medium")
    initial_confidence = Column(Float, default=0.5)
    
    # Metrics
    understanding_score = Column(Float, default=50.0)
    questions_asked = Column(Float, default=0)
    
    # State
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Metadata
    metadata_json = Column(JSON, nullable=True)  # Store source info/chunk counts here
