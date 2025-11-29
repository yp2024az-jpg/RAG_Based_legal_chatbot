"""
BM25 Retriever - Lexical matching using BM25 algorithm
"""
from typing import List, Tuple, Optional
from collections import defaultdict
import math

class BM25Retriever:
    """
    BM25-based retriever for lexical matching.
    Uses term frequency and document frequency for ranking.
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 Retriever
        
        Args:
            k1: Term frequency saturation parameter
            b: Length normalization parameter
        """
        self.k1 = k1
        self.b = b
        self.doc_store = {}
        self.idf_scores = {}
        self.doc_length_avg = 0
        self.vocabulary = defaultdict(int)  # Token frequency in corpus
    
    def add_documents(self, documents: List[str], metadata: List[dict] = None):
        """
        Add documents for BM25 indexing
        
        Args:
            documents: List of document texts
            metadata: Optional metadata for each document
        """
        self.doc_store.clear()
        self.vocabulary.clear()
        self.idf_scores.clear()
        
        # Store documents and calculate statistics
        total_length = 0
        for idx, doc in enumerate(documents):
            tokens = self._tokenize(doc)
            self.doc_store[idx] = {
                'text': doc,
                'tokens': tokens,
                'length': len(tokens),
                'metadata': metadata[idx] if metadata and idx < len(metadata) else {}
            }
            total_length += len(tokens)
            
            # Update vocabulary
            for token in set(tokens):
                self.vocabulary[token] += 1
        
        # Calculate average document length
        if self.doc_store:
            self.doc_length_avg = total_length / len(self.doc_store)
        
        # Calculate IDF scores
        self._calculate_idf()
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        return text.lower().split()
    
    def _calculate_idf(self):
        """Calculate IDF (Inverse Document Frequency) for all terms"""
        num_docs = len(self.doc_store)
        
        for token in self.vocabulary:
            doc_freq = sum(1 for doc in self.doc_store.values() 
                          if token in doc['tokens'])
            
            # IDF formula: log(N / df + 1)
            idf = math.log((num_docs - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0)
            self.idf_scores[token] = idf
    
    def _get_bm25_score(self, tokens: List[str], doc_idx: int) -> float:
        """Calculate BM25 score for a document"""
        doc = self.doc_store[doc_idx]
        doc_tokens = doc['tokens']
        doc_length = doc['length']
        
        score = 0.0
        for token in tokens:
            if token not in self.idf_scores:
                continue
            
            # Term frequency in document
            term_freq = doc_tokens.count(token)
            
            # BM25 formula
            idf = self.idf_scores[token]
            normalized_tf = (term_freq * (self.k1 + 1)) / (
                term_freq + self.k1 * (1 - self.b + self.b * (doc_length / self.doc_length_avg))
            )
            
            score += idf * normalized_tf
        
        return score
    
    def search(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        """
        Search using BM25 algorithm
        
        Args:
            query: Query text
            k: Number of results to return
            
        Returns:
            List of (document, score) tuples
        """
        if not self.doc_store:
            return []
        
        query_tokens = self._tokenize(query)
        scores = {}
        
        # Calculate BM25 score for each document (include zeros to allow top-k)
        for doc_idx in self.doc_store:
            score = self._get_bm25_score(query_tokens, doc_idx)
            scores[doc_idx] = score
        
        # Sort and return top-k
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
        
        results = []
        for doc_idx, score in sorted_results:
            doc_text = self.doc_store[doc_idx]['text']
            results.append((doc_text, float(score)))
        
        return results
    
    def get_document_count(self) -> int:
        """Get number of indexed documents"""
        return len(self.doc_store)
    
    def reset(self):
        """Clear all data"""
        self.doc_store.clear()
        self.idf_scores.clear()
        self.vocabulary.clear()
        self.doc_length_avg = 0
