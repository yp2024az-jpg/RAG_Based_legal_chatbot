"""
Query Validator - Validates if queries are legal domain relevant
"""

class QueryValidator:
    """Validates user queries for legal domain relevance"""
    
    def __init__(self):
        self.legal_keywords = {
            'case', 'law', 'act', 'statute', 'judgment', 'ruling', 'legal',
            'court', 'attorney', 'lawyer', 'contract', 'agreement', 'tort',
            'crime', 'criminal', 'civil', 'constitutional', 'penalty', 'penalties',
            'clause', 'liability', 'damages', 'defendant', 'plaintiff', 'appeal', 'verdict',
            'subpoena', 'testimony', 'evidence', 'precedent', 'jurisdiction',
            'regulation', 'compliance', 'rights', 'duty', 'obligation', 'breach',
            'section', 'sections', 'ipc'
        }
        
    def is_valid(self, query: str) -> bool:
        """
        Check if query is legal domain relevant
        
        Args:
            query: User query string
            
        Returns:
            bool: True if valid legal query, False otherwise
        """
        if not query or len(query.strip()) < 5:
            return False

        query_lower = query.lower()
        legal_score = sum(1 for keyword in self.legal_keywords if keyword in query_lower)

        # Require at least one legal keyword or a long-form query
        return legal_score >= 1 or len(query) > 50
    
    def get_validity_score(self, query: str) -> float:
        """
        Get confidence score for query validity (0-1)
        
        Args:
            query: User query string
            
        Returns:
            float: Validity score between 0 and 1
        """
        if not query or len(query.strip()) < 5:
            return 0.0
            
        query_lower = query.lower()
        words = query_lower.split()
        legal_score = sum(1 for keyword in self.legal_keywords if keyword in query_lower)
        
        # Calculate based on keyword density
        if len(words) == 0:
            return 0.0
            
        score = min(legal_score / len(words), 1.0)
        return score
