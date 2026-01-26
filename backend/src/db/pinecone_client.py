"""
Pinecone Vector Database Integration
Stores and retrieves embeddings
"""

from typing import List, Dict, Optional
import logging
from src.core.config import settings

logger = logging.getLogger(__name__)


class PineconeClient:
    """
    Pinecone vector database client
    
    Handles:
    - Storing embeddings with metadata
    - Similarity search
    - Index management
    """
    
    def __init__(self):
        self.enabled = False
        self.index = None
        
        # Check if Pinecone is configured
        if not settings.pinecone_api_key or settings.pinecone_api_key == "your_pinecone_api_key":
            logger.warning("⚠️  Pinecone API key not configured. Vector storage disabled.")
            logger.warning("   Get your free key at: https://www.pinecone.io/")
            return
        
        try:
            from pinecone import Pinecone, ServerlessSpec
            
            # Initialize Pinecone
            pc = Pinecone(api_key=settings.pinecone_api_key)
            
            index_name = settings.pinecone_index_name
            
            # Check if index exists, create if not
            if index_name not in pc.list_indexes().names():
                logger.info(f"Creating Pinecone index: {index_name}")
                pc.create_index(
                    name=index_name,
                    dimension=settings.pinecone_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.pinecone_environment or "us-east-1"
                    )
                )
                logger.info(f"✅ Created Pinecone index: {index_name}")
            
            # Connect to index
            self.index = pc.Index(index_name)
            self.enabled = True
            
            logger.info(f"✅ Connected to Pinecone index: {index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            logger.warning("Continuing without vector storage")
            self.enabled = False
    
    def store_embeddings(
        self,
        session_id: str,
        chunks: List[str],
        embeddings: List[List[float]],
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Store embeddings in Pinecone
        
        Args:
            session_id: Session identifier
            chunks: Text chunks
            embeddings: Vector embeddings
            metadata: Additional metadata
        
        Returns:
            Success boolean
        """
        if not self.enabled:
            logger.warning("Pinecone not enabled, skipping vector storage")
            return False
        
        try:
            # Prepare vectors for upsert
            vectors = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = f"{session_id}_chunk_{i}"
                vector_metadata = {
                    "session_id": session_id,
                    "chunk_index": i,
                    "text": chunk[:1000],  # Store first 1000 chars
                    **(metadata or {})
                }
                vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": vector_metadata
                })
            
            # Upsert to Pinecone
            self.index.upsert(vectors=vectors)
            
            logger.info(f"✅ Stored {len(vectors)} vectors in Pinecone for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store embeddings in Pinecone: {e}")
            return False
    
    def search(
        self,
        query_embedding: List[float],
        session_id: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Search for similar chunks
        
        Args:
            query_embedding: Query vector
            session_id: Optional session filter
            top_k: Number of results
        
        Returns:
            List of matches with text and scores
        """
        if not self.enabled:
            return []
        
        try:
            # Build filter
            filter_dict = {"session_id": session_id} if session_id else None
            
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                filter=filter_dict,
                include_metadata=True
            )
            
            # Extract matches
            matches = []
            for match in results.matches:
                matches.append({
                    "text": match.metadata.get("text", ""),
                    "score": match.score,
                    "chunk_index": match.metadata.get("chunk_index", 0)
                })
            
            logger.info(f"Found {len(matches)} matches for query")
            return matches
            
        except Exception as e:
            logger.error(f"Pinecone search failed: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Delete all vectors for a session"""
        if not self.enabled:
            return False
        
        try:
            # Delete by session_id filter
            self.index.delete(filter={"session_id": session_id})
            logger.info(f"Deleted vectors for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete session vectors: {e}")
            return False


# Global Pinecone client
pinecone_client = PineconeClient()
