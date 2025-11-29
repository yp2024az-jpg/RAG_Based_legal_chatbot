"""
Unit Tests - Query Processing
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from src.query_processing import QueryValidator, QueryCategorizer, QueryCategory


class TestQueryValidator(unittest.TestCase):
    """Test query validator"""
    
    def setUp(self):
        self.validator = QueryValidator()
    
    def test_valid_legal_query(self):
        """Test valid legal query"""
        query = "What are the penalties under Section 420 of IPC?"
        self.assertTrue(self.validator.is_valid(query))
    
    def test_invalid_query_too_short(self):
        """Test invalid query - too short"""
        query = "abc"
        self.assertFalse(self.validator.is_valid(query))
    
    def test_non_legal_query(self):
        """Test non-legal query"""
        query = "What is the weather today?"
        # This should not be valid for legal domain
        self.assertFalse(self.validator.is_valid(query))
    
    def test_validity_score(self):
        """Test validity score"""
        query = "What is the law on contract breach?"
        score = self.validator.get_validity_score(query)
        self.assertGreater(score, 0.3)


class TestQueryCategorizer(unittest.TestCase):
    """Test query categorizer"""
    
    def setUp(self):
        self.categorizer = QueryCategorizer()
    
    def test_case_comparison(self):
        """Test case comparison detection"""
        query = "Compare Case A versus Case B"
        category, _ = self.categorizer.categorize(query)
        self.assertEqual(category, QueryCategory.CASE_COMPARISON)
    
    def test_case_summarization(self):
        """Test case summarization detection"""
        query = "Summarize the landmark ruling in this case"
        category, _ = self.categorizer.categorize(query)
        self.assertEqual(category, QueryCategory.CASE_SUMMARIZATION)
    
    def test_legal_data_retrieval(self):
        """Test legal data retrieval detection"""
        query = "What are the penalties under Section 420?"
        category, _ = self.categorizer.categorize(query)
        self.assertEqual(category, QueryCategory.LEGAL_DATA_RETRIEVAL)
    
    def test_legal_advice(self):
        """Test legal advice detection"""
        query = "Should I file a case in this situation?"
        category, _ = self.categorizer.categorize(query)
        self.assertEqual(category, QueryCategory.LEGAL_ADVICE)


if __name__ == '__main__':
    unittest.main()
