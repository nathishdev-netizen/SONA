"""
Custom Opik Evaluators for SONA's 3-Dimensional Scoring
Uses LLM-as-Judge approach with Opik integration
"""

from typing import Dict, Any, Optional
import json
import logging
from src.core.llm_config import llm_config
from src.opik_integration import prompt_manager, is_opik_enabled

logger = logging.getLogger(__name__)


class BaseEvaluator:
    """Base evaluator with common functionality"""
    
    def __init__(self, name: str, llm_provider: str = "groq"):
        self.name = name
        self.llm = llm_config.get_llm(provider=llm_provider, temperature=0.3)
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response"""
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            
            # Fallback: try parsing entire response
            return json.loads(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            logger.debug(f"Response was: {response}")
            return {"score": 50, "reasoning": "Failed to parse evaluation"}


class CorrectnessEvaluator(BaseEvaluator):
    """
    Evaluates factual correctness using LLM-as-Judge
    Compares answer against source material
    """
    
    def __init__(self, llm_provider: str = "groq"):
        super().__init__(name="correctness", llm_provider=llm_provider)
    
    def evaluate(
        self,
        question: str,
        answer: str,
        reference_chunks: list[str]
    ) -> Dict[str, Any]:
        """
        Score answer on factual correctness (0-100)
        
        Args:
            question: The question asked
            answer: User's answer
            reference_chunks: Relevant content from source material
        
        Returns:
            {
                "score": 0-100,
                "reasoning": "explanation",
                "name": "correctness"
            }
        """
        
        # Get prompt from Opik library
        prompt = prompt_manager.get_prompt(
            name="evaluator_correctness_v1",
            variables={
                "question": question,
                "answer": answer,
                "reference": "\n\n".join(reference_chunks[:3])  # Top 3 chunks
            }
        )
        
        # Call LLM
        response = self.llm.invoke(prompt)
        result = self._parse_llm_response(response.content)
        
        return {
            "score": float(result.get("score", 50)),
            "reasoning": result.get("reasoning", "No reasoning provided"),
            "name": "correctness"
        }


class DepthEvaluator(BaseEvaluator):
    """
    Evaluates depth of understanding
    Context-aware: depth expectations vary by question difficulty
    """
    
    def __init__(self, llm_provider: str = "groq"):
        super().__init__(name="depth", llm_provider=llm_provider)
    
    def evaluate(
        self,
        question: str,
        answer: str,
        difficulty: str,
        expected_answer_type: str
    ) -> Dict[str, Any]:
        """
        Score depth of understanding (0-100)
        
        Depth is contextual:
        - Easy question + short answer = potentially high depth
        - Hard question + short answer = likely low depth
        
        Args:
            question: The question asked
            answer: User's answer
            difficulty: Question difficulty (easy/medium/hard)
            expected_answer_type: Expected answer length/type
        
        Returns:
            {
                "score": 0-100,
                "reasoning": "explanation",
                "name": "depth"
            }
        """
        
        prompt = prompt_manager.get_prompt(
            name="evaluator_depth_v1",
            variables={
                "question": question,
                "answer": answer,
                "difficulty": difficulty,
                "expected_answer_type": expected_answer_type
            }
        )
        
        response = self.llm.invoke(prompt)
        result = self._parse_llm_response(response.content)
        
        return {
            "score": float(result.get("score", 50)),
            "reasoning": result.get("reasoning", "No reasoning provided"),
            "name": "depth"
        }


class TransferEvaluator(BaseEvaluator):
    """
    Evaluates ability to apply concepts to new situations
    Looks for implications, connections, applications
    """
    
    def __init__(self, llm_provider: str = "groq"):
        super().__init__(name="transfer", llm_provider=llm_provider)
    
    def evaluate(
        self,
        question: str,
        answer: str
    ) -> Dict[str, Any]:
        """
        Score transfer ability (0-100)
        
        Looks for:
        - Application to new contexts
        - Connections to other concepts
        - Understanding of implications
        
        Args:
            question: The question asked
            answer: User's answer
        
        Returns:
            {
                "score": 0-100,
                "reasoning": "explanation",
                "name": "transfer"
            }
        """
        
        prompt = prompt_manager.get_prompt(
            name="evaluator_transfer_v1",
            variables={
                "question": question,
                "answer": answer
            }
        )
        
        response = self.llm.invoke(prompt)
        result = self._parse_llm_response(response.content)
        
        return {
            "score": float(result.get("score", 50)),
            "reasoning": result.get("reasoning", "No reasoning provided"),
            "name": "transfer"
        }


class ComprehensiveEvaluator:
    """
    Combines all three evaluators for complete assessment
    Implements SONA's 50-30-20 scoring formula
    """
    
    def __init__(self, llm_provider: str = "groq"):
        self.correctness_evaluator = CorrectnessEvaluator(llm_provider)
        self.depth_evaluator = DepthEvaluator(llm_provider)
        self.transfer_evaluator = TransferEvaluator(llm_provider)
    
    def evaluate_answer(
        self,
        question: str,
        answer: str,
        reference_chunks: list[str],
        difficulty: str,
        expected_answer_type: str
    ) -> Dict[str, Any]:
        """
        Complete 3-dimensional evaluation
        
        Returns:
            {
                "correctness": {"score": 0-100, "reasoning": "..."},
                "depth": {"score": 0-100, "reasoning": "..."},
                "transfer": {"score": 0-100, "reasoning": "..."},
                "answer_score": 0-100  # Weighted average
            }
        """
        
        # Evaluate all three dimensions
        correctness = self.correctness_evaluator.evaluate(
            question, answer, reference_chunks
        )
        
        depth = self.depth_evaluator.evaluate(
            question, answer, difficulty, expected_answer_type
        )
        
        transfer = self.transfer_evaluator.evaluate(
            question, answer
        )
        
        # Calculate weighted score: 50-30-20
        answer_score = (
            0.5 * correctness["score"] +
            0.3 * depth["score"] +
            0.2 * transfer["score"]
        )
        
        return {
            "correctness": correctness,
            "depth": depth,
            "transfer": transfer,
            "answer_score": round(answer_score, 1)
        }


# Global evaluator instance
comprehensive_evaluator = ComprehensiveEvaluator()
