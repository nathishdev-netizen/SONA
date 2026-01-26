"""
Evaluator Agent
Assesses answer quality across correctness, depth, and transfer dimensions
"""

from src.agents.base_agent import BaseAgent
from src.models.agent_io import EvaluatorInput, EvaluatorOutput
import logging
import json

logger = logging.getLogger(__name__)


class EvaluatorAgent(BaseAgent):
    """
    Answer evaluation agent with three-dimensional scoring
    
    Uses LLM-as-Judge approach to evaluate:
    - Correctness (factual accuracy vs. source)
    - Depth (contextual understanding relative to difficulty)
    - Transfer (application to new situations)
    """
    
    def __init__(self):
        super().__init__(
            role="Understanding Assessment Specialist",
            goal=(
                "Evaluate learner answers across three critical dimensions: "
                "correctness (factual accuracy), depth (contextual understanding), "
                "and transfer (application ability). Provide fair, objective scores "
                "with clear reasoning grounded in the source material."
            ),
            backstory=(
                "You are an expert evaluator trained in educational assessment and "
                "cognitive science. You understand that true comprehension goes beyond "
                "reciting facts—it requires depth of understanding and the ability to "
                "apply knowledge in new contexts. You are meticulous, fair, and always "
                "justify your scores with evidence."
            ),
            tools=[],
            verbose=True,
            allow_delegation=False,
        )
    
    def execute(self, input_data: EvaluatorInput) -> EvaluatorOutput:
        """
        Evaluate answer across three dimensions using LLM-as-Judge
        """
        try:
            print(f"\n📊 EVALUATING ANSWER")
            print(f"   Question: {input_data.question_text[:50]}...")
            print(f"   Answer: {input_data.answer_text[:50]}...")
            
            # Build context from reference chunks
            context_text = "\n".join(input_data.reference_chunks[:3]) if input_data.reference_chunks else "No context available"
            
            # System prompt for evaluator
            system_prompt = """You are an expert educational evaluator. Your task is to score a student's answer across three dimensions:

1. **Correctness (0-100)**: Is the answer factually accurate based on the source material? 
   - 90-100: Fully correct, no errors
   - 70-89: Mostly correct with minor issues
   - 50-69: Partially correct with significant gaps
   - Below 50: Largely incorrect or contains fabrications

2. **Depth (0-100)**: Does the answer show deep understanding relative to the question difficulty?
   - Consider the difficulty level when scoring
   - For easy questions: concise correct answers score high
   - For hard questions: detailed explanations expected

3. **Transfer (0-100)**: Can the student apply this knowledge to new situations?
   - Does the answer show connections to broader concepts?
   - Does it demonstrate understanding beyond memorization?

Return ONLY valid JSON with this exact structure:
{
    "correctness": {"score": <0-100>, "reasoning": "<explanation>"},
    "depth": {"score": <0-100>, "reasoning": "<explanation>"},
    "transfer": {"score": <0-100>, "reasoning": "<explanation>"},
    "hallucination_detected": <true/false>,
    "overall_feedback": "<brief constructive feedback for the learner>"
}"""

            # User prompt with context
            user_prompt = f"""Evaluate this answer:

**Question**: {input_data.question_text}
**Difficulty**: {input_data.difficulty}
**Expected Answer Type**: {input_data.expected_answer_type}

**Student's Answer**: 
{input_data.answer_text}

**Reference Material (Source of Truth)**:
{context_text}

Provide your evaluation in JSON format."""

            # Call LLM
            print("🤖 Calling LLM for answer evaluation...")
            response = self.llm.generate(prompt=user_prompt, system_prompt=system_prompt)
            
            # Parse response
            clean_response = response.replace("```json", "").replace("```", "").strip()
            
            try:
                data = json.loads(clean_response)
                
                correctness = data['correctness']['score']
                depth = data['depth']['score']
                transfer = data['transfer']['score']
                
                # Calculate weighted overall score: 50% correctness, 30% depth, 20% transfer
                overall_score = 0.5 * correctness + 0.3 * depth + 0.2 * transfer
                
                print(f"✅ Evaluation complete:")
                print(f"   Correctness: {correctness}/100")
                print(f"   Depth: {depth}/100")
                print(f"   Transfer: {transfer}/100")
                print(f"   Overall: {overall_score:.1f}/100")
                
                # Log to Opik
                try:
                    from src.opik_integration.tracing import opik_integration
                    opik_integration.log_evaluation(
                        session_id=str(input_data.session_id),
                        question_id=input_data.question_id,
                        answer_text=input_data.answer_text,
                        correctness=correctness,
                        depth=depth,
                        transfer=transfer,
                        overall_score=overall_score
                    )
                except Exception as opik_error:
                    logger.debug(f"Opik logging skipped: {opik_error}")
                
                return EvaluatorOutput(
                    correctness_score=correctness,
                    correctness_reasoning=data['correctness']['reasoning'],
                    depth_score=depth,
                    depth_reasoning=data['depth']['reasoning'],
                    transfer_score=transfer,
                    transfer_reasoning=data['transfer']['reasoning'],
                    overall_score=overall_score,
                    hallucination_detected=data.get('hallucination_detected', False),
                    feedback=data.get('overall_feedback', 'Good effort!')
                )
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse evaluation response: {response}")
                # Return fallback scores
                return EvaluatorOutput(
                    correctness_score=50.0,
                    correctness_reasoning="Unable to parse LLM response",
                    depth_score=50.0,
                    depth_reasoning="Unable to parse LLM response",
                    transfer_score=50.0,
                    transfer_reasoning="Unable to parse LLM response",
                    overall_score=50.0,
                    hallucination_detected=False,
                    feedback="We had trouble evaluating your answer. Please try again."
                )
                
        except Exception as e:
            logger.error(f"Evaluator failed: {e}", exc_info=True)
            return EvaluatorOutput(
                correctness_score=0.0,
                correctness_reasoning=f"Evaluation error: {str(e)}",
                depth_score=0.0,
                depth_reasoning="",
                transfer_score=0.0,
                transfer_reasoning="",
                overall_score=0.0,
                hallucination_detected=False,
                feedback="An error occurred during evaluation."
            )
