"""
Base Tool - Simplified (no CrewAI dependency)
All SONA tools inherit from this for consistency
"""

from pydantic import BaseModel
from typing import Any


class ToolArguments(BaseModel):
    """Base class for tool arguments schemas"""
    pass


class TracedTool:
    """
    Simple base tool class
    
    Provides consistent interface for all tools
    Note: Opik tracing disabled for Python 3.14 compatibility
    """
    
    name: str = "base_tool"
    description: str = "Base tool"
    
    def _run(self, *args, **kwargs) -> Any:
        """Execute tool - calls _execute"""
        return self._execute(*args, **kwargs)
    
    def _execute(self, *args, **kwargs) -> Any:
        """
        Override this method in subclasses
        """
        raise NotImplementedError(f"Tool {self.name} must implement _execute()")
