"""
Vector Database Service
Pinecone integration for pattern storage and similarity matching.
"""

from typing import List, Optional, Dict, Any
from loguru import logger

try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except (ImportError, Exception) as e:
    PINECONE_AVAILABLE = False
    # Pinecone package raises Exception if pinecone-client is installed
    logger.warning(f"Pinecone not available: {e}. Install with: pip install pinecone (and remove pinecone-client)")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_CONFIG, PINECONE_INDEX_NAME


class VectorService:
    """Service for Pinecone vector database operations."""
    
    def __init__(self):
        self.index_name = PINECONE_INDEX_NAME
        self.pc: Optional[Any] = None
        self.index: Optional[Any] = None
        
        if PINECONE_AVAILABLE and PINECONE_API_KEY:
            try:
                self.pc = Pinecone(api_key=PINECONE_API_KEY)
                self._ensure_index()
            except Exception as e:
                logger.error(f"Failed to initialize Pinecone: {e}")
                self.pc = None
    
    def _ensure_index(self):
        """Ensure Pinecone index exists."""
        if not self.pc:
            return
        
        try:
            # Check if index exists
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=PINECONE_CONFIG['dimension'],
                    metric=PINECONE_CONFIG['metric'],
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=PINECONE_ENVIRONMENT
                    )
                )
                logger.info(f"Index {self.index_name} created")
            else:
                logger.info(f"Index {self.index_name} already exists")
            
            self.index = self.pc.Index(self.index_name)
        except Exception as e:
            logger.error(f"Failed to ensure index: {e}")
            self.index = None
    
    def is_available(self) -> bool:
        """Check if vector service is available."""
        return self.index is not None
    
    def upsert_provider_pattern(self, npi: str, embedding: List[float], metadata: Dict[str, Any]):
        """Store provider fraud pattern in vector database."""
        if not self.is_available():
            logger.warning("Vector service not available")
            return False
        
        try:
            vector_id = f"provider_{npi}"
            self.index.upsert(vectors=[(vector_id, embedding, metadata)])
            logger.info(f"Stored pattern for provider {npi}")
            return True
        except Exception as e:
            logger.error(f"Failed to upsert provider pattern: {e}")
            return False
    
    def find_similar_patterns(self, embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Find similar fraud patterns."""
        if not self.is_available():
            logger.warning("Vector service not available")
            return []
        
        try:
            results = self.index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            similar_patterns = []
            for match in results.get('matches', []):
                similar_patterns.append({
                    'id': match['id'],
                    'score': match['score'],
                    'metadata': match.get('metadata', {})
                })
            
            return similar_patterns
        except Exception as e:
            logger.error(f"Failed to find similar patterns: {e}")
            return []
    
    def delete_provider_pattern(self, npi: str) -> bool:
        """Delete provider pattern from vector database."""
        if not self.is_available():
            return False
        
        try:
            vector_id = f"provider_{npi}"
            self.index.delete(ids=[vector_id])
            logger.info(f"Deleted pattern for provider {npi}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete provider pattern: {e}")
            return False
