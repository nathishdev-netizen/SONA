"""
Embedding Tool - Real embeddings using sentence-transformers
Works with Python 3.14 (no langchain dependency)
"""

from src.tools.base_tool import TracedTool, ToolArguments
from pydantic import Field, BaseModel
from typing import Type, List
import logging

logger = logging.getLogger(__name__)


class EmbeddingArgs(ToolArguments):
    """Arguments for embedding generation"""
    texts: List[str] = Field(..., description="List of text chunks to embed")
    model_name: str = Field(default="all-MiniLM-L6-v2", description="Sentence transformer model")


class EmbeddingTool(TracedTool):
    """
    Generate embeddings using sentence-transformers
    
    Uses all-MiniLM-L6-v2 by default (384 dimensions, fast, good quality)
    Alternative: all-mpnet-base-v2 (768 dimensions, better quality, slower)
    """
    
    name: str = "embedding_generator"
    description: str = "Generates vector embeddings from text chunks using sentence-transformers"
    args_schema: Type[BaseModel] = EmbeddingArgs
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.model_name = None
    
    def _load_model(self, model_name: str = "all-MiniLM-L6-v2"):
        """Lazy load the embedding model"""
        if self.model is None or self.model_name != model_name:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {model_name}")
                self.model = SentenceTransformer(model_name)
                self.model_name = model_name
                logger.info(f"✅ Embedding model loaded: {model_name}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise
    
    def _execute(self, texts: List[str], model_name: str = "all-MiniLM-L6-v2") -> dict:
        """
        Generate embeddings for text chunks
        
        Args:
            texts: List of text chunks
            model_name: Sentence transformer model to use
        
        Returns:
            {
                "embeddings": List of vectors,
                "dimension": int,
                "model": str,
                "success": bool
            }
        """
        try:
            # Load model if needed
            self._load_model(model_name)
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(texts)} chunks")
            embeddings = self.model.encode(texts, show_progress_bar=False)
            
            # Convert to list for JSON serialization
            embeddings_list = [emb.tolist() for emb in embeddings]
            
            logger.info(f"✅ Generated {len(embeddings_list)} embeddings, dimension: {len(embeddings_list[0])}")
            
            # Print preview of first embedding (first 10 dimensions)
            if embeddings_list:
                preview = embeddings_list[0][:10]
                print(f"   First embedding preview (10/{len(embeddings_list[0])} dims): {preview}")
                print(f"   Sample values: min={min(embeddings_list[0]):.4f}, max={max(embeddings_list[0]):.4f}, mean={sum(embeddings_list[0])/len(embeddings_list[0]):.4f}")
            
            return {
                "embeddings": embeddings_list,
                "dimension": len(embeddings_list[0]),
                "model": model_name,
                "count": len(embeddings_list),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return {
                "embeddings": [],
                "success": False,
                "error": str(e)
            }


# Tool instance
embedding_tool = EmbeddingTool()
