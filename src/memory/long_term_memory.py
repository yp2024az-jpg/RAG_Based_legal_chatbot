"""
Long-Term Memory - Persistent vector database storage
"""
from typing import Dict, List, Any, Optional
import numpy as np
from datetime import datetime
import json

class LongTermMemory:
    """
    Long-Term Memory (LTM) for persistent storage.
    Stores document embeddings, past responses, and legal insights.
    """
    
    def __init__(self, vector_db_path: str = "./data/embeddings"):
        """
        Initialize LTM
        
        Args:
            vector_db_path: Path to vector database
        """
        self.vector_db_path = vector_db_path
        self.embeddings_store = {}  # In-memory store (can be replaced with persistent DB)
        self.response_cache = {}    # Cache of past responses
        self.document_metadata = {} # Metadata about documents
    
    def store_embedding(self, doc_id: str, embedding: np.ndarray, metadata: Dict[str, Any] = None):
        """
        Store document embedding
        
        Args:
            doc_id: Unique document identifier
            embedding: Vector embedding
            metadata: Optional metadata about document
        """
        self.embeddings_store[doc_id] = {
            'embedding': embedding,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
    
    def store_response(self, query_hash: str, response: str, sources: List[str] = None, 
                       confidence: float = 0.0):
        """
        Cache a past response
        
        Args:
            query_hash: Hash of the query
            response: Generated response
            sources: List of source documents
            confidence: Confidence score of response
        """
        self.response_cache[query_hash] = {
            'response': response,
            'sources': sources or [],
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
    
    def retrieve_embedding(self, doc_id: str) -> Optional[np.ndarray]:
        """Retrieve stored embedding"""
        if doc_id in self.embeddings_store:
            return self.embeddings_store[doc_id]['embedding']
        return None
    
    def retrieve_response(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached response"""
        return self.response_cache.get(query_hash)
    
    def store_document_metadata(self, doc_id: str, metadata: Dict[str, Any]):
        """Store document metadata"""
        self.document_metadata[doc_id] = {
            **metadata,
            'stored_at': datetime.now().isoformat()
        }
    
    def get_document_metadata(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document metadata"""
        return self.document_metadata.get(doc_id)
    
    def get_all_embeddings_count(self) -> int:
        """Get count of stored embeddings"""
        return len(self.embeddings_store)
    
    def get_response_cache_size(self) -> int:
        """Get size of response cache"""
        return len(self.response_cache)
    
    def clear_old_cache(self, days: int = 30):
        """
        Clear cached responses older than specified days
        
        Args:
            days: Number of days to keep cache
        """
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        keys_to_remove = []
        for key, value in self.response_cache.items():
            cached_time = datetime.fromisoformat(value['timestamp'])
            if cached_time < cutoff_date:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.response_cache[key]
    
    def export_state(self) -> Dict[str, Any]:
        """Export LTM state for persistence"""
        return {
            'embeddings_store': {
                k: {
                    'metadata': v['metadata'],
                    'timestamp': v['timestamp']
                } for k, v in self.embeddings_store.items()
            },
            'response_cache': self.response_cache,
            'document_metadata': self.document_metadata
        }
    
    def import_state(self, state: Dict[str, Any]):
        """Import LTM state from persistence"""
        self.embeddings_store = state.get('embeddings_store', {})
        self.response_cache = state.get('response_cache', {})
        self.document_metadata = state.get('document_metadata', {})
