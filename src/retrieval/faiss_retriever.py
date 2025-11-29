"""
FAISS Retriever - Semantic similarity search using FAISS
"""
from typing import List, Tuple, Optional
import numpy as np

class FAISSRetriever:
    """
    FAISS-based retriever for semantic similarity search.
    Uses dense embeddings for fast nearest neighbor search.
    """
    
    def __init__(self, dimension: int = 384, metric: str = "L2"):
        """
        Initialize FAISS Retriever
        
        Args:
            dimension: Embedding dimension
            metric: Distance metric ("L2" or "IP")
        """
        self.dimension = dimension
        self.metric = metric
        self.faiss_index = None
        self.doc_store = {}  # Maps index to document
        self.embeddings = []
        
        # Initialize FAISS index (lazy loading)
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize FAISS index"""
        try:
            import faiss
            if self.metric == "L2":
                self.faiss_index = faiss.IndexFlatL2(self.dimension)
            else:  # IP (Inner Product)
                self.faiss_index = faiss.IndexFlatIP(self.dimension)
        except ImportError:
            raise ImportError("FAISS not installed. Install with: pip install faiss-cpu")
    
    def add_documents(self, documents: List[str], embeddings: List[np.ndarray], 
                      metadata: List[dict] = None):
        """
        Add documents with their embeddings to the index
        
        Args:
            documents: List of document texts
            embeddings: List of embedding vectors
            metadata: Optional metadata for each document
        """
        if len(documents) != len(embeddings):
            raise ValueError("Documents and embeddings must have same length")
        
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # Add to FAISS index
        self.faiss_index.add(embeddings_array)
        self.embeddings.extend(embeddings)
        
        # Store documents and metadata
        start_idx = len(self.doc_store)
        for idx, (doc, meta) in enumerate(zip(documents, metadata or [{}] * len(documents))):
            self.doc_store[start_idx + idx] = {
                'text': doc,
                'metadata': meta,
                'embedding_idx': start_idx + idx
            }
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of (document, similarity_score) tuples
        """
        if self.faiss_index.ntotal == 0:
            return []
        
        # Ensure query is float32 and 2D
        query_embedding = np.array([query_embedding], dtype=np.float32)
        
        # Search
        distances, indices = self.faiss_index.search(query_embedding, min(k, self.faiss_index.ntotal))
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx in self.doc_store:
                doc_info = self.doc_store[idx]
                # Convert distance to similarity (higher is better)
                if self.metric == "L2":
                    similarity = 1 / (1 + distance)
                else:
                    similarity = distance
                
                results.append((doc_info['text'], float(similarity)))
        
        return results
    
    def get_document_count(self) -> int:
        """Get number of indexed documents"""
        return self.faiss_index.ntotal
    
    def reset(self):
        """Clear all stored data"""
        self._initialize_index()
        self.doc_store.clear()
        self.embeddings.clear()
