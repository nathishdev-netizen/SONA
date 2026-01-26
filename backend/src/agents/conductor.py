"""
Conductor Agent
Orchestrates evaluation sessions and determines when to stop questioning
"""

from typing import List
from src.agents.base_agent import BaseAgent
from src.models.agent_io import ConductorInput, ConductorOutput
from src.opik_integration.tracing import opik_integration
from src.core.config import settings


class ConductorAgent(BaseAgent):
    """
    Session orchestration and stopping logic agent
    
    Responsibilities:
    - Orchestrate question-answer-evaluation flow
    - Update understanding score using weighted formula
    - Determine when to stop questioning (confidence-based)
    - Manage session state and transitions
    - Provide final assessment and recommendations
    """
    
    def __init__(self):
        super().__init__(
            role="Session Orchestrator & Flow Controller",
            goal=(
                "Manage the evaluation session flow, update understanding scores, "
                "and determine the optimal stopping point based on confidence in "
                "the learner's understanding level. Ensure efficient evaluation "
                "without over-questioning or under-questioning."
            ),
            backstory=(
                "You are a master conductor who orchestrates complex evaluation sessions. "
                "You understand statistical confidence and know when you have enough evidence "
                "to make a reliable assessment. You balance thoroughness with efficiency, "
                "avoiding both premature conclusions and exhausting interrogations. "
                "You track patterns in performance, recognize when understanding is stable, "
                "and know when continued questioning would yield diminishing returns."
            ),
            tools=[],  # Tools: session management, scoring calculations
            verbose=True,
            allow_delegation=False,
        )
    
    @opik_integration.track_agent(
        name="Conductor",
        metadata={"agent_type": "session_orchestration"}
    )
    def execute(self, input_data: ConductorInput) -> ConductorOutput:
        """
        Determine whether to continue questioning
        
        Args:
            input_data: Conductor input with session state
        
        Returns:
            ConductorOutput with continuation decision and reasoning
        """
        # Decision logic based on:
        # 1. Understanding score confidence
        # 2. Score variance (stability)
        # 3. Number of questions asked
        # 4. Min/max question constraints
        pass
    
    def update_understanding_score(
        self,
        previous_score: float,
        answer_score: float
    ) -> float:
        """
        Update understanding score with weighted formula
        
        Formula:
        understanding_score = 0.6 × previous_understanding + 0.4 × answer_score
        
        This balances:
        - 60% stability (previous understanding)
        - 40% new evidence (current answer)
        
        Args:
            previous_score: Previous understanding score
            answer_score: Current answer score
        
        Returns:
            Updated understanding score
        """
        return 0.6 * previous_score + 0.4 * answer_score
    
    def calculate_score_variance(self, recent_scores: List[float]) -> float:
        """Calculate variance in recent answer scores"""
        if len(recent_scores) < 2:
            return 100.0  # High variance if insufficient data
        
        mean = sum(recent_scores) / len(recent_scores)
        variance = sum((x - mean) ** 2 for x in recent_scores) / len(recent_scores)
        return variance ** 0.5  # Standard deviation
    
    def should_stop(self, input_data: ConductorInput) -> tuple[bool, str]:
        """
        Determine if questioning should stop
        
        Stopping conditions:
        1. Reached confidence threshold with stable scores
        2. Hit maximum questions limit
        3. Score variance is low enough (consistent performance)
        
        Never stop before minimum questions.
        
        Returns:
            (should_stop, reason)
        """
        # Minimum questions not reached
        if input_data.questions_asked < settings.min_questions:
            return False, "Minimum questions not yet reached"
        
        # Maximum questions reached
        if input_data.questions_asked >= settings.max_questions:
            return True, "Maximum questions limit reached"
        
        # Check confidence and stability
        confidence_threshold = settings.confidence_threshold
        
        # High confidence in score AND low variance
        if (
            input_data.understanding_score > 70 and
            input_data.score_variance < 10 and
            input_data.questions_asked >= settings.min_questions + 2
        ):
            return True, "Sufficient confidence in understanding level"
        
        return False, "Continue questioning to build confidence"
    
    def generate_final_assessment(
        self,
        understanding_score: float,
        questions_asked: int,
        stopped_reason: str
    ) -> str:
        """Generate final assessment summary"""
        pass
