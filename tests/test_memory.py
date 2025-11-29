"""
Unit Tests - Memory Systems
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from src.memory import ShortTermMemory, LongTermMemory


class TestShortTermMemory(unittest.TestCase):
    """Test short-term memory"""
    
    def setUp(self):
        self.memory = ShortTermMemory(max_size=5)
    
    def test_add_turn(self):
        """Test adding conversation turn"""
        self.memory.add_turn("What is the law?", "The law is...", "qa")
        self.assertEqual(len(self.memory.history), 1)
    
    def test_max_size(self):
        """Test max size enforcement"""
        for i in range(10):
            self.memory.add_turn(f"Query {i}", f"Response {i}")
        
        self.assertLessEqual(len(self.memory.history), 5)
    
    def test_get_context(self):
        """Test getting context"""
        self.memory.add_turn("Q1", "A1")
        self.memory.add_turn("Q2", "A2")
        
        context = self.memory.get_context()
        self.assertIn("Q1", context)
        self.assertIn("A1", context)


class TestLongTermMemory(unittest.TestCase):
    """Test long-term memory"""
    
    def setUp(self):
        self.memory = LongTermMemory()
    
    def test_store_response(self):
        """Test storing response"""
        self.memory.store_response(
            "query_hash_123",
            "This is a cached response",
            sources=["doc1", "doc2"],
            confidence=0.95
        )
        
        cached = self.memory.retrieve_response("query_hash_123")
        self.assertIsNotNone(cached)
        self.assertEqual(cached['confidence'], 0.95)
    
    def test_store_metadata(self):
        """Test storing metadata"""
        metadata = {
            'source': 'Case Law Database',
            'year': 2023,
            'jurisdiction': 'India'
        }
        
        self.memory.store_document_metadata("doc_1", metadata)
        retrieved = self.memory.get_document_metadata("doc_1")
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['source'], 'Case Law Database')


if __name__ == '__main__':
    unittest.main()
