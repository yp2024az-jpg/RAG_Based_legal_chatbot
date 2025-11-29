"""
Document Embedder - Generates embeddings for documents
"""
from typing import List, Union
import numpy as np

class DocumentEmbedder:
    """Generates embeddings for documents"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize Document Embedder
        
        Args:
            model_name: HuggingFace model name
        """
        self.model_name = model_name
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
        except ImportError:
            print("Warning: sentence-transformers not installed")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        if not self.model:
            return np.zeros(384)
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts
            batch_size: Batch size for processing
            
        Returns:
            List of embeddings
        """
        if not self.model:
            return [np.zeros(384) for _ in texts]
        
        embeddings = self.model.encode(texts, batch_size=batch_size, convert_to_numpy=True)
        return [emb for emb in embeddings]
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension"""
        if self.model:
            return self.model.get_sentence_embedding_dimension()
        return 384
