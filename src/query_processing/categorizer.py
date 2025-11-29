"""
Query Categorizer - Classifies queries into legal categories
"""
from enum import Enum
from typing import Tuple

class QueryCategory(Enum):
    """Legal query categories"""
    CASE_COMPARISON = "case_comparison"
    CASE_SUMMARIZATION = "case_summarization"
    LEGAL_DATA_RETRIEVAL = "legal_data_retrieval"
    SIMILAR_CASE_FINDING = "similar_case_finding"
    LEGAL_ADVICE = "legal_advice"
    INVALID = "invalid"


class QueryCategorizer:
    """Categorizes legal queries into predefined categories"""
    
    def __init__(self):
        self.category_keywords = {
            QueryCategory.CASE_COMPARISON: {
                'compare', 'versus', 'vs', 'difference', 'contrast', 'similar',
                'distinguish', 'comparison', 'different', 'like'
            },
            QueryCategory.CASE_SUMMARIZATION: {
                'summarize', 'summary', 'overview', 'explain', 'what is',
                'tell me about', 'describe', 'details', 'information'
            },
            QueryCategory.LEGAL_DATA_RETRIEVAL: {
                'penalty', 'punishment', 'fine', 'section', 'article',
                'provision', 'requirement', 'law', 'act', 'statute', 'data',
                'what are', 'list', 'define'
            },
            QueryCategory.SIMILAR_CASE_FINDING: {
                'similar', 'like', 'analogous', 'precedent', 'related',
                'same', 'comparable', 'find', 'search', 'look for'
            },
            QueryCategory.LEGAL_ADVICE: {
                'should', 'can i', 'am i', 'what should', 'how to',
                'advice', 'help', 'do', 'would', 'could', 'might',
                'liable', 'responsible', 'what if'
            }
        }
    
    def categorize(self, query: str) -> Tuple[QueryCategory, float]:
        """
        Categorize query into one of the predefined categories
        
        Args:
            query: User query string
            
        Returns:
            Tuple of (QueryCategory, confidence_score)
        """
        query_lower = query.lower()
        scores = {}
        
        for category, keywords in self.category_keywords.items():
            # Count keyword matches
            matches = sum(1 for keyword in keywords if keyword in query_lower)
            # Normalize by keywords count
            score = matches / len(keywords) if keywords else 0
            scores[category] = score
        
        # Get category with highest score
        best_category = max(scores, key=scores.get)
        confidence = scores[best_category]
        
        return best_category, confidence
    
    def multi_category_detect(self, query: str, threshold: float = 0.2) -> list:
        """
        Detect multiple potential categories for a query
        
        Args:
            query: User query string
            threshold: Minimum confidence threshold
            
        Returns:
            List of (QueryCategory, confidence) tuples
        """
        query_lower = query.lower()
        results = []
        
        for category, keywords in self.category_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in query_lower)
            score = matches / len(keywords) if keywords else 0
            
            if score >= threshold:
                results.append((category, score))
        
        # Sort by confidence descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results
