"""
LLM Configuration - Direct Client Implementation
Bypassing langchain due to Python 3.14 compatibility issues
"""

from typing import Literal, Optional
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

class DirectLLM:
    """
    Direct LLM client wrapper (no langchain)
    Supported providers: Groq, OpenAI
    """
    def __init__(self, provider: str, model: str, api_key: str, temperature: float = 0.7):
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.client = None
        
        try:
            if provider == "groq":
                from groq import Groq
                self.client = Groq(api_key=api_key)
            elif provider == "openai":
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
        except ImportError as e:
            logger.error(f"Failed to import client for {provider}: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize {provider} client: {e}")

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response from LLM with Opik tracing"""
        if not self.client:
            return "Error: LLM client not initialized"
        
        import time
        start_time = time.time()
            
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            
            response = completion.choices[0].message.content
            
            # Log to Opik
            latency_ms = (time.time() - start_time) * 1000
            try:
                from src.opik_integration.tracing import opik_integration
                if opik_integration.enabled:
                    tokens_used = getattr(completion.usage, 'total_tokens', None) if hasattr(completion, 'usage') else None
                    
                    # Calculate Cost
                    cost = 0.0
                    if tokens_used:
                        # Pricing (approximate per 1M tokens for consistency)
                        # Groq Llama 3.3 70B: ~$0.70 / 1M input, $0.90 / 1M output (using avg $0.80)
                        # OpenAI GPT-4o: ~$2.50 / 1M input, $10.00 / 1M output
                        
                        price_per_1k = 0.0000008 # Default low cost
                        
                        if "llama" in self.model.lower():
                            price_per_1k = 0.0000007 # $0.70 per 1M
                        elif "gpt-4" in self.model.lower():
                            price_per_1k = 0.005 # $5.00 per 1M avg
                        
                        cost = round((tokens_used * price_per_1k), 8)

                    opik_integration.track_llm_call(
                        name=f"llm_{self.provider}",
                        model=self.model,
                        input_messages=messages,
                        output=response,
                        tokens_used=tokens_used,
                        latency_ms=latency_ms,
                        cost=cost
                    )
            except Exception as opik_error:
                logger.debug(f"Opik tracking skipped: {opik_error}")
            
            return response
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return f"Error generating response: {str(e)}"

class LLMConfig:
    """LLM Configuration Manager"""
    
    def get_llm(
        self,
        provider: Optional[Literal["openai", "groq"]] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> DirectLLM:
        """Get configured LLM client"""
        provider = provider or settings.default_llm_provider
        
        if provider == "groq":
            model = model or settings.groq_model
            api_key = settings.groq_api_key
        else:
            model = model or settings.openai_model
            api_key = settings.openai_api_key
            
        print(f"🧠 Initializing Real LLM: {provider}/{model}")
        
        return DirectLLM(
            provider=provider,
            model=model,
            api_key=api_key,
            temperature=temperature
        )

# Global instance
llm_config = LLMConfig()
