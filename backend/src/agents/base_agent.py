"""
Base Agent - Simplified (No Opik/CrewAI due to Python 3.14 Pydantic issues)
All SONA agents inherit from this base class
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, List
from src.core.llm_config import llm_config


class BaseAgent(ABC):
    """
    Base class for all SONA agents
    
    Provides:
    - LLM configuration  
    - Common agent patterns
    
    Note: CrewAI and Opik temporarily disabled for Python 3.14 compatibility
    Both use langchain-core which has Pydantic v1/v2 conflicts with Python 3.14
    """
    
    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str,
        tools: Optional[List] = None,
        llm_provider: Optional[str] = None,
        verbose: bool = True,
        allow_delegation: bool = False
    ):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools or []
        self.verbose = verbose
        
        # Get LLM client (mock for now)
        self.llm = llm_config.get_llm(provider=llm_provider)
    
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """
        Execute the agent's main task
        
        Must be implemented by subclasses
        """
        pass
