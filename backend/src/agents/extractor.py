"""
Extractor Agent - Content Extraction with CrewAI
Processes learning materials from various sources
"""

from typing import List
# from crewai import Task  # Temporarily commented - Pydantic v1/v2 conflict
from src.agents.base_agent import BaseAgent
from src.models.agent_io import ExtractorInput, ExtractorOutput
# from src.opik_integration.tracing import opik_integration  # Disabled for Python 3.14
import logging

logger = logging.getLogger(__name__)


class ExtractorAgent(BaseAgent):
    """
    Extracts and processes learning materials
    
    Agent that:
    - Extracts content from various sources (text, YouTube, PDF, web)
    - Chunks content semantically
    - Prepares for question generation
    
    Note: Opik tracing temporarily disabled due to Python 3.14 Pydantic conflict
    """
    
    def __init__(self):
        # Initialize with Agent pattern
        super().__init__(
            role="Content Extraction Specialist",
            goal="Extract and structure learning materials from various sources into semantic chunks",
            backstory=(
                "You are an expert at processing educational content. "
                "You excel at extracting key information from documents, videos, and websites, "
                "and organizing it into digestible chunks that preserve context and meaning."
            ),
            tools=[],
            llm_provider="groq",
            verbose=True,
            allow_delegation=False
        )
    
    # @opik_integration.track_agent(name="Extractor", metadata={"agent_type": "content_extraction"})
    def execute(self, input_data: ExtractorInput) -> ExtractorOutput:
        """
        Extract and process content from source
        
        Args:
            input_data: Extractor input with source details
        
        Returns:
            ExtractorOutput with processed content and chunks
        """
        try:
            from src.tools import (
                text_extractor,
                youtube_extractor,
                pdf_extractor,
                web_scraper,
                chunker
            )
            
            logger.info(f"Extracting content from {input_data.source_type} source")
            
            # Step 1: Extract raw content based on source type
            extraction_result = None
            
            # Opik Tracking Wrapper
            from src.opik_integration.tracing import opik_integration
            
            # Step 1: Extract
            @opik_integration.track(name="extract_source_content")
            def _extract_content(source_type, raw_text, source_url, file_path):
                if source_type == "text":
                    return text_extractor._execute(text=raw_text)
                elif source_type == "youtube":
                    return youtube_extractor._execute(url=source_url)
                elif source_type == "pdf":
                    return pdf_extractor._execute(file_path=file_path)
                elif source_type in ["web", "website"]:
                    return web_scraper._execute(url=source_url)
                return {"success": False, "error": f"Unsupported: {source_type}"}

            extraction_result = _extract_content(
                input_data.source_type, 
                input_data.raw_text, 
                input_data.source_url, 
                input_data.file_path
            )
            
            if not extraction_result.get("success"):
                return ExtractorOutput(
                    success=False, raw_content="", chunks=[],
                    error=extraction_result.get("error", "Extraction failed")
                )
            
            raw_content = extraction_result["content"]
            
            # SAVE TRANSCRIPT (Debug)
            try:
                import os
                transcript_dir = "data/transcripts"
                os.makedirs(transcript_dir, exist_ok=True)
                transcript_file = f"{transcript_dir}/{input_data.session_id}_{input_data.source_type}_transcript.txt"
                with open(transcript_file, "w") as f:
                    f.write(raw_content)
                logger.info(f"Saved raw transcript to {transcript_file}")
            except Exception:
                pass
            
            # Step 2: Chunk
            @opik_integration.track(name="semantic_chunking")
            def _chunk_content(text):
                return chunker._execute(text=text, chunk_size=500, overlap=50)
                
            chunking_result = _chunk_content(raw_content)
            
            if not chunking_result.get("success"):
                return ExtractorOutput(
                    success=False, raw_content=raw_content, chunks=[], error="Chunking failed"
                )
            chunks = chunking_result["chunks"]

            # Step 3: Embed
            @opik_integration.track(name="generate_embeddings")
            def _generate_embeddings(texts):
                from src.tools.embedding_tool import embedding_tool
                return embedding_tool._execute(texts=texts)

            embedding_result = _generate_embeddings(chunks)
            
            embeddings = []
            embeddings_stored = False
            dimension = 0
            
            if embedding_result.get("success"):
                embeddings = embedding_result["embeddings"]
                dimension = embedding_result['dimension']
                
                # Step 4: Store
                @opik_integration.track(name="pinecone_storage")
                def _store_vectors(sid, cks, embs, meta):
                    from src.db.pinecone_client import pinecone_client
                    return pinecone_client.store_embeddings(
                        session_id=sid, chunks=cks, embeddings=embs, metadata=meta
                    )

                embeddings_stored = _store_vectors(
                    input_data.session_id, chunks, embeddings, 
                    {"source_type": input_data.source_type}
                )
            
            # Step 5: Evaluate Quality (New Opik Feature)
            try:
                opik_integration.evaluate_content_quality(
                    source=input_data.source_url or "text_input",
                    content=raw_content[:1000] # Sample
                )
            except Exception:
                pass

            # Return Success... (existing return logic)
            return ExtractorOutput(
                success=True,
                raw_content=raw_content,
                title=extraction_result.get("title"),
                metadata={
                    "word_count": extraction_result.get("word_count", 0),
                    "chunk_count": len(chunks),
                    "source_type": input_data.source_type,
                    "embedding_dimension": dimension,
                    "embeddings_count": len(embeddings)
                },
                chunks=chunks,
                embeddings_stored=embeddings_stored,
                error=None
            )
            
        except Exception as e:
            logger.error(f"Extractor agent failed: {e}", exc_info=True)
            return ExtractorOutput(
                success=False,
                raw_content="",
                chunks=[],
                error=str(e)
            )
