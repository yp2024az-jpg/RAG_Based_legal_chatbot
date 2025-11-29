"""
Unit Tests - Retrieval System
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
import numpy as np
from src.retrieval import FAISSRetriever, BM25Retriever, HybridRetriever


class TestFAISSRetriever(unittest.TestCase):
    """Test FAISS retriever"""
    
    def setUp(self):
        try:
            self.retriever = FAISSRetriever(dimension=384)
        except ImportError:
            self.skipTest("FAISS not installed")
    
    def test_add_documents(self):
        """Test adding documents"""
        docs = ["Legal document 1", "Legal document 2"]
        embeddings = [np.random.randn(384) for _ in docs]
        
        self.retriever.add_documents(docs, embeddings)
        self.assertEqual(self.retriever.get_document_count(), 2)
    
    def test_search(self):
        """Test search functionality"""
        docs = ["Section 420 deals with cheating", "Contract law is important"]
        embeddings = [np.random.randn(384) for _ in docs]
        
        self.retriever.add_documents(docs, embeddings)
        query_embedding = np.random.randn(384)
        
        results = self.retriever.search(query_embedding, k=1)
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], tuple)


class TestBM25Retriever(unittest.TestCase):
    """Test BM25 retriever"""
    
    def setUp(self):
        self.retriever = BM25Retriever()
    
    def test_add_documents(self):
        """Test adding documents"""
        docs = ["Indian Penal Code Section 420", "Criminal Procedure Code"]
        self.retriever.add_documents(docs)
        self.assertEqual(self.retriever.get_document_count(), 2)
    
    def test_search(self):
        """Test BM25 search"""
        docs = ["Section 420 deals with cheating", "Contract law is important"]
        self.retriever.add_documents(docs)
        
        query = "Section 420 cheating"
        results = self.retriever.search(query, k=2)
        
        self.assertGreater(len(results), 0)
        self.assertEqual(len(results), 2)


class TestHybridRetriever(unittest.TestCase):
    """Test hybrid retriever"""
    
    def setUp(self):
        try:
            self.retriever = HybridRetriever(embedding_dim=384)
        except ImportError:
            self.skipTest("FAISS not installed")
    
    def test_hybrid_search(self):
        """Test hybrid search"""
        docs = ["Section 420 IPC", "Contract law basics"]
        embeddings = [np.random.randn(384) for _ in docs]
        
        self.retriever.add_documents(docs, embeddings)
        query_embedding = np.random.randn(384)
        
        results = self.retriever.search("Section 420", query_embedding, k=2)
        self.assertEqual(len(results), 2)


if __name__ == '__main__':
    unittest.main()
