"""
Tutor Agent
Handles user-initiated questions about the learning material (RAG)
"""

from src.agents.base_agent import BaseAgent
from src.models.agent_io import TutorInput, TutorOutput
from src.opik_integration.tracing import opik_integration
import logging
import json

logger = logging.getLogger(__name__)


class TutorAgent(BaseAgent):
    """
    Intelligent Tutor Agent for Q&A
    
    Responsibility:
    - Answer student questions based ONLY on source material
    - Provide clear, pedagogical explanations
    - Cite sources/chunks used
    """
    
    def __init__(self):
        super().__init__(
            role="Personal Learning Assistant",
            goal="Answer student questions accurately using provided learning materials and suggest deeper inquiries",
            backstory=(
                "You are a helpful, patient, and knowledgeable Personal Learning Assistant. "
                "Your goal is to help students understand the material they are studying by answering their questions "
                "clearly and pedagogically. You ALWAYS answer based on the provided context chunks (RAG). "
                "You are honest: if the information is not in the context, you admit it. "
                "You also encourage curiosity by suggesting relevant follow-up questions."
            ),
            tools=[],
            verbose=True,
            allow_delegation=False,
        )
    
    @opik_integration.track_agent(name="Tutor", metadata={"agent_type": "qa_tutor"})
    def execute(self, input_data: TutorInput) -> TutorOutput:
        """
        Answer user question using RAG
        """
        try:
            print(f"\n🎓 TUTOR: Parsing question...")
            print(f"   Question: {input_data.user_question}")
            
            # Step 1: Embed question
            print(f"   Generating embedding for retrieval...")
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            query_embedding = model.encode(input_data.user_question).tolist()
            
            # Step 2: Retrieve from Pinecone
            print(f"   Searching Pinecone...")
            from src.db.pinecone_client import pinecone_client
            api_key_status = "Available" if pinecone_client.enabled else "Missing"
            print(f"   Pinecone Status: {api_key_status}")
            
            context_chunks = []
            
            if pinecone_client.enabled:
                matches = pinecone_client.search(
                    query_embedding=query_embedding,
                    session_id=input_data.session_id,
                    top_k=5
                )
                
                print(f"   Found {len(matches)} matches")
                
                for match in matches:
                    if match['score'] > 0.25:  # Relevance threshold
                        text = match['text']
                        context_chunks.append(text)
                        print(f"   - Context (score {match['score']:.2f}): {text[:50]}...")
            else:
                print("⚠️  Pinecone not configured, cannot retrieve context.")
            
            # Step 3: Generate Answer
            context_text = "\n\n".join(context_chunks) if context_chunks else "No specific context found."
            
            system_prompt = """You are a helpful AI Tutor. Answer the student's question using ONLY the provided context.
            
If the answer is found in the context:
- Explain it clearly and simply.
- Be encouraging and pedagogical.
- Keep answers concise (2-3 paragraphs max).

If the answer is NOT in the context:
- Say "I don't see that information in the material you provided."
- Do not make up facts.

Format your response in JSON:
{
    "answer": "your explanation here",
    "confidence": "high/medium/low",
    "follow_up": "a suggested follow-up question for the student"
}"""

            user_prompt = f"""Context from learning material:
{context_text}

Student Question: {input_data.user_question}

Provide your answer in JSON format."""

            print("🤖 Calling LLM for tutor response...")
            response = self.llm.generate(prompt=user_prompt, system_prompt=system_prompt)
            
            # Parse response
            clean_response = response.replace("```json", "").replace("```", "").strip()
            
            try:
                data = json.loads(clean_response)
                
                answer = data['answer']
                confidence = data.get('confidence', 'high')
                follow_up = data.get('follow_up')
                
                print(f"✅ Tutor Response Generated")
                return TutorOutput(
                    answer=answer,
                    sources_used=[c[:100]+"..." for c in context_chunks],
                    confidence=confidence,
                    follow_up_suggestion=follow_up
                )
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse Tutor response: {response}")
                return TutorOutput(
                    answer=clean_response,
                    sources_used=[],
                    confidence="medium",
                    follow_up_suggestion=None
                )

        except Exception as e:
            logger.error(f"Tutor Agent failed: {e}", exc_info=True)
            return TutorOutput(
                answer="I'm sorry, I encountered an error while trying to answer your question.",
                sources_used=[],
                confidence="low",
                follow_up_suggestion=None
            )
