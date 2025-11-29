"""
Hybrid Retriever - Combines FAISS and BM25 for optimal retrieval
"""
from typing import List, Tuple, Dict, Optional
import numpy as np
from .faiss_retriever import FAISSRetriever
from .bm25_retriever import BM25Retriever

class HybridRetriever:
    """
    Hybrid Retriever combining semantic (FAISS) and lexical (BM25) search.
    Uses weighted combination for final ranking.
    """
    
    def __init__(self, embedding_dim: int = 384, 
                 faiss_weight: float = 0.6, bm25_weight: float = 0.4):
        """
        Initialize Hybrid Retriever
        
        Args:
            embedding_dim: Dimension of embeddings
            faiss_weight: Weight for FAISS results (0-1)
            bm25_weight: Weight for BM25 results (0-1)
        """
        self.faiss_retriever = FAISSRetriever(dimension=embedding_dim)
        self.bm25_retriever = BM25Retriever()
        
        # Normalize weights
        total = faiss_weight + bm25_weight
        self.faiss_weight = faiss_weight / total
        self.bm25_weight = bm25_weight / total
        
        self.documents = []
    
    def add_documents(self, documents: List[str], embeddings: List[np.ndarray],
                      metadata: List[dict] = None):
        """
        Add documents to both retrievers
        
        Args:
            documents: List of document texts
            embeddings: List of embedding vectors
            metadata: Optional metadata
        """
        self.documents = documents
        self.faiss_retriever.add_documents(documents, embeddings, metadata)
        self.bm25_retriever.add_documents(documents, metadata)
    
    def search(self, query: str, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[str, float]]:
        """
        Hybrid search combining FAISS and BM25
        
        Args:
            query: Query text
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of (document, combined_score) tuples
        """
        # Get results from both retrievers
        faiss_results = self.faiss_retriever.search(query_embedding, k)
        bm25_results = self.bm25_retriever.search(query, k)
        
        # Combine scores
        combined_scores: Dict[str, float] = {}
        
        # Add FAISS scores
        for doc, score in faiss_results:
            # Normalize FAISS score to 0-1 range
            normalized_score = score
            combined_scores[doc] = combined_scores.get(doc, 0) + self.faiss_weight * normalized_score
        
        # Add BM25 scores
        for doc, score in bm25_results:
            # Normalize BM25 score (use min-max normalization if needed)
            # For simplicity, assume scores are already normalized
            combined_scores[doc] = combined_scores.get(doc, 0) + self.bm25_weight * score
        
        # Sort by combined score
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:k]
        
        return sorted_results
    
    def re_rank(self, documents: List[str], query: str, 
                query_embedding: np.ndarray, k: int = 5) -> List[Tuple[str, float]]:
        """
        Re-rank documents using both methods
        
        Args:
            documents: List of documents to re-rank
            query: Query text
            query_embedding: Query embedding
            k: Top-k to return
            
        Returns:
            Re-ranked list of documents with scores
        """
        # Create temporary retrievers with these documents
        embeddings = [query_embedding] * len(documents)  # Placeholder
        
        scores = {}
        for doc in documents:
            # Score using both methods
            faiss_score = 1.0 if doc in documents else 0.0
            bm25_score = 1.0 if doc in documents else 0.0
            
            combined_score = (self.faiss_weight * faiss_score + 
                            self.bm25_weight * bm25_score)
            scores[doc] = combined_score
        
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
        return sorted_results
    
    def get_document_count(self) -> int:
        """Get number of indexed documents"""
        return self.faiss_retriever.get_document_count()
