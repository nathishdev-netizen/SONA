"""
Opik Prompt Library Integration
Manages prompts stored in Opik for version control and A/B testing
"""

from typing import Dict, Optional, Any
import logging
from src.opik_integration.client import opik_client, is_opik_enabled

logger = logging.getLogger(__name__)


class OpikPromptManager:
    """
    Manage prompts via Opik Prompt Library
    
    Benefits:
    - Version control for prompts
    - A/B testing different prompt strategies
    - Hot-swappable prompts without code changes
    - Centralized prompt management
    """
    
    def __init__(self):
        self.client = opik_client.client if is_opik_enabled() else None
        self.enabled = is_opik_enabled()
        self.cache = {}  # Local cache for performance
        
        if self.enabled:
            logger.info("✅ Opik Prompt Manager initialized")
            # Ensure base prompts exist
            self._ensure_base_prompts()
        else:
            logger.warning("⚠️  Opik Prompt Manager disabled (no API key)")
    
    def _ensure_base_prompts(self):
        """Create base prompts if they don't exist"""
        base_prompts = self._get_default_prompts()
        
        for prompt_name, prompt_data in base_prompts.items():
            try:
                # Try to get existing prompt
                self.client.get_prompt(name=prompt_name)
                logger.debug(f"Prompt '{prompt_name}' already exists")
            except:
                # Create new prompt
                try:
                    self.client.create_prompt(
                        name=prompt_name,
                        prompt=prompt_data["template"],
                        description=prompt_data["description"]
                    )
                    logger.info(f"✅ Created prompt: {prompt_name}")
                except Exception as e:
                    logger.error(f"Failed to create prompt '{prompt_name}': {e}")
    
    def _get_default_prompts(self) -> Dict[str, Dict[str, str]]:
        """Default prompt templates"""
        return {
            "interrogator_question_v1": {
                "template": """You are a Socratic interrogator evaluating a learner's understanding.

Learning Claim: {claim}
Relevant Content: {context}

Generate a {difficulty} question that tests understanding of this concept.
Question Type: {question_type}
Expected Answer: {expected_answer_type}

Tone: {tone}

Generate only the question, nothing else.""",
                "description": "Question generation for adaptive interrogation"
            },
            
            "evaluator_correctness_v1": {
                "template": """Evaluate the factual correctness of this answer.

Question: {question}
User Answer: {answer}
Reference Material: {reference}

Score the answer on factual correctness (0-100):
- 90-100: Completely accurate, no errors
- 70-89: Mostly accurate, minor issues
- 50-69: Partially accurate, some errors
- 30-49: Mostly inaccurate
- 0-29: Completely wrong or hallucinated

Return JSON:
{{
    "score": <0-100>,
    "reasoning": "<explanation>"
}}""",
                "description": "Evaluates factual correctness against source material"
            },
            
            "evaluator_depth_v1": {
                "template": """Evaluate the depth of understanding shown in this answer.

Question: {question}
Difficulty: {difficulty}
Expected Answer Type: {expected_answer_type}
User Answer: {answer}

Score depth of understanding (0-100):
- Context: For {difficulty} questions expecting {expected_answer_type}
- High (80-100): Shows nuanced understanding
- Medium (50-79): Basic understanding
- Low (0-49): Surface level or missing context

Return JSON:
{{
    "score": <0-100>,
    "reasoning": "<explanation>"
}}""",
                "description": "Evaluates depth contextual to question difficulty"
            },
            
            "evaluator_transfer_v1": {
                "template": """Evaluate the learner's ability to apply concepts to new situations.

Question: {question}
User Answer: {answer}

Score transfer ability (0-100):
- 80-100: Shows application, implications, connections
- 50-79: Some transfer, limited connections  
- 0-49: No transfer, pure recall

Return JSON:
{{
    "score": <0-100>,
    "reasoning": "<explanation>"
}}""",
                "description": "Evaluates application and transfer ability"
            },
            
            "extractor_chunking_v1": {
                "template": """Analyze this content and suggest semantic chunking strategy.

Content: {content}
Target chunk size: {chunk_size} words

Suggest how to chunk this content while preserving meaning.
Focus on natural topic boundaries.

Return JSON with chunk boundaries.""",
                "description": "Guides semantic chunking of content"
            }
        }
    
    def get_prompt(
        self,
        name: str,
        variables: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None
    ) -> str:
        """
        Get prompt from Opik library and render with variables
        
        Args:
            name: Prompt name (e.g., 'interrogator_question_v1')
            variables: Template variables to fill in
            version: Specific version (default: latest)
        
        Returns:
            Rendered prompt string
        """
        if not self.enabled:
            # Fallback to local defaults if Opik not available
            return self._get_local_prompt(name, variables)
        
        cache_key = f"{name}:{version or 'latest'}"
        
        try:
            # Check cache
            if cache_key not in self.cache:
                # Fetch from Opik
                prompt_obj = self.client.get_prompt(name=name, version=version)
                template = prompt_obj.prompt
                self.cache[cache_key] = template
            else:
                template = self.cache[cache_key]
            
            # Render with variables
            if variables:
                return template.format(**variables)
            return template
            
        except Exception as e:
            logger.error(f"Failed to get prompt '{name}' from Opik: {e}")
            # Fallback to local
            return self._get_local_prompt(name, variables)
    
    def _get_local_prompt(self, name: str, variables: Optional[Dict] = None) -> str:
        """Fallback to local prompt if Opik unavailable"""
        defaults = self._get_default_prompts()
        
        if name in defaults:
            template = defaults[name]["template"]
            if variables:
                return template.format(**variables)
            return template
        
        logger.error(f"Prompt '{name}' not found in local defaults")
        return ""
    
    def update_prompt(self, name: str, template: str, description: str = None):
        """Create new version of existing prompt"""
        if not self.enabled:
            logger.warning("Cannot update prompt: Opik not enabled")
            return
        
        try:
            self.client.update_prompt(
                name=name,
                prompt=template,
                description=description
            )
            # Clear cache for this prompt
            self.cache = {k: v for k, v in self.cache.items() if not k.startswith(name)}
            logger.info(f"✅ Updated prompt: {name}")
        except Exception as e:
            logger.error(f"Failed to update prompt: {e}")
    
    def list_prompts(self) -> list:
        """List all available prompts"""
        if not self.enabled:
            return list(self._get_default_prompts().keys())
        
        try:
            return self.client.list_prompts()
        except Exception as e:
            logger.error(f"Failed to list prompts: {e}")
            return []


# Global prompt manager instance
prompt_manager = OpikPromptManager()
