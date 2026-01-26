"""
Interrogator Agent
Generates adaptive questions to probe understanding depth
"""

from typing import List
from src.agents.base_agent import BaseAgent
from src.models.agent_io import InterrogatorInput, InterrogatorOutput

class InterrogatorAgent(BaseAgent):
    """
    Adaptive question generation agent
    """
    
    def __init__(self):
        super().__init__(
            role="Adaptive Question Generator",
            goal="Generate probing, adaptive questions that test deep understanding.",
            backstory="You are a master interrogator of knowledge, trained in Socratic questioning.",
            tools=[],
            verbose=True
        )
    
    def generate_greeting(self, session_id: str) -> str:
        """
        Generate a personalized greeting based on session context
        """
        try:
            import datetime
            from src.db.session import SessionLocal
            from src.db.models import Session
            from src.agents.prompts import PromptManager
            from src.core.llm_config import llm_config
            
            # 1. Fetch Context
            session_prefs = {}
            with SessionLocal() as db:
                db_session = db.query(Session).filter(Session.id == str(session_id)).first()
                if db_session:
                    session_prefs["tone"] = db_session.tone
                    session_prefs["user_name"] = db_session.user_name
                    session_prefs["topic"] = db_session.learning_claim
            
            # Time of day
            hour = datetime.datetime.now().hour
            if 5 <= hour < 12: time_str = "Morning"
            elif 12 <= hour < 18: time_str = "Afternoon"
            else: time_str = "Evening"
            
            # 2. Get Prompt
            system_prompt = PromptManager.get_system_prompt(
                agent_type="greeting",
                tone=session_prefs.get("tone", "friendly"),
                user_name=session_prefs.get("user_name", "Learner"),
                topic=session_prefs.get("topic", "something new"),
                time_of_day=time_str
            )
            
            user_prompt = PromptManager.get_user_prompt(agent_type="greeting")
            
            # 3. Generate
            llm_client = llm_config.get_llm(temperature=0.8) # Higher temp for diverse greetings
            response = llm_client.generate(prompt=user_prompt, system_prompt=system_prompt)
            
            return response.strip()

        except Exception as e:
            return f"Welcome! Ready to start exploring {session_prefs.get('topic', 'this topic')}?"
            
    def execute(self, input_data: InterrogatorInput) -> InterrogatorOutput:
        """
        Generate adaptive question based on session state
        """
        try:
            import logging
            logger = logging.getLogger(__name__)

            # 1. Fetch Session Preferences from DB
            from src.db.session import SessionLocal
            from src.db.models import Session
            
            session_prefs = {
                "tone": "friendly",
                "difficulty": "medium",
                "user_name": "Learner"
            }
            
            try:
                # Ensure Session ID is a string for query (SQLAlchemy handles UUID conversion but string is safer)
                sid = str(input_data.session_id)
                with SessionLocal() as db:
                    db_session = db.query(Session).filter(Session.id == sid).first()
                    if db_session:
                        session_prefs["tone"] = db_session.tone
                        session_prefs["difficulty"] = db_session.difficulty
                        session_prefs["user_name"] = db_session.user_name
            except Exception as e:
                logger.warning(f"Failed to fetch DB prefs: {e}")

            # 2. Get embeddings & Retrieval
            from src.tools.embedding_tool import embedding_tool
            from src.db.pinecone_client import pinecone_client
            
            # Embed Claim
            embedding_result = embedding_tool._execute([input_data.claim_text])
            if not embedding_result["success"]:
                raise Exception("Embedding failed")
                
            claim_vector = embedding_result["embeddings"][0]
            
            # Search Pinecone - FIXED: Using query_embedding
            retrieval_result = pinecone_client.search(
                session_id=str(input_data.session_id),
                query_embedding=claim_vector,
                top_k=3
            )
            
            context_text = "No specific source context available."
            context_chunks = []
            if retrieval_result:
                context_text = "\n".join([m['text'] for m in retrieval_result])
                context_chunks = [m['text'] for m in retrieval_result]

            # 3. Generate Question
            from src.agents.prompts import PromptManager
            
            system_prompt = PromptManager.get_system_prompt(
                agent_type="interrogator",
                tone=session_prefs['tone'],
                user_name=session_prefs['user_name'],
                difficulty=session_prefs['difficulty']
            )
            
            user_prompt = PromptManager.get_user_prompt(
                agent_type="interrogator",
                claim_text=input_data.claim_text,
                context_text=context_text
            )
            
            # Call LLM
            from src.core.llm_config import llm_config
            llm_client = llm_config.get_llm(temperature=0.7)
            
            logger.info("🤖 Calling LLM for customized question...")
            response = llm_client.generate(  # DirectLLM uses .generate not .chat
                prompt=user_prompt,
                system_prompt=system_prompt
            )
            
            # DirectLLM.generate returns string, not an object with content attribute
            question_text = response.strip()
            logger.info(f"✅ Question generated: {question_text}")
            
            # Log to Opik
            try:
                from src.opik_integration.tracing import opik_integration
                opik_integration.log_question_generation(
                    session_id=str(input_data.session_id),
                    question_text=question_text,
                    difficulty=session_prefs['difficulty'],
                    question_type="personalized_probe",
                    context_chunks_used=len(context_chunks)
                )
            except Exception as e:
                logger.warning(f"Opik log failed: {e}")
            
            return InterrogatorOutput(
                success=True,
                question_text=question_text,
                difficulty=session_prefs['difficulty'],
                question_type="personalized_probe",
                expected_answer_type="text",
                reasoning="Generated based on context", # FIXED: Added missing field
                context_used=context_chunks
            )

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Interrogator failed: {e}", exc_info=True)
            return InterrogatorOutput(
                success=False,
                question_text=f"Could you explain '{input_data.claim_text}' in your own words?",
                difficulty="recovery",
                question_type="recovery",
                expected_answer_type="text",
                reasoning=f"Error occurred: {str(e)}", # FIXED: Added missing field
                context_used=[]
            )
