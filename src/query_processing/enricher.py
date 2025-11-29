"""
Query Enricher - Enriches queries with context and metadata
"""
from typing import Dict, Any

class QueryEnricher:
    """Enriches queries with additional context and metadata"""
    
    def __init__(self):
        self.jurisdiction_keywords = {
            'indian', 'india', 'us', 'uk', 'indian penal', 'ipc',
            'united states', 'united kingdom', 'england', 'australia',
            'canada', 'common law', 'civil law'
        }
        
        self.legal_domain_keywords = {
            'criminal': ['crime', 'criminal', 'penal', 'conviction', 'sentence'],
            'civil': ['civil', 'tort', 'contract', 'damages', 'liability'],
            'constitutional': ['constitutional', 'fundamental', 'rights', 'amendment'],
            'corporate': ['corporate', 'company', 'business', 'shareholder', 'director'],
            'intellectual_property': ['patent', 'trademark', 'copyright', 'ip'],
            'family': ['marriage', 'divorce', 'custody', 'inheritance', 'succession'],
            'labor': ['employment', 'labor', 'wage', 'discrimination', 'strike']
        }
    
    def enrich(self, query: str, session_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enrich query with context and metadata
        
        Args:
            query: User query string
            session_context: Optional session context dictionary
            
        Returns:
            Dictionary with enriched query information
        """
        enriched = {
            'original_query': query,
            'query_length': len(query),
            'jurisdiction': self._detect_jurisdiction(query),
            'legal_domain': self._detect_legal_domain(query),
            'entities': self._extract_entities(query),
            'key_terms': self._extract_key_terms(query),
            'session_context': session_context or {}
        }
        
        return enriched
    
    def _detect_jurisdiction(self, query: str) -> str:
        """Detect jurisdiction from query"""
        query_lower = query.lower()
        for keyword in self.jurisdiction_keywords:
            if keyword in query_lower:
                if 'indian' in keyword or 'india' in keyword or 'ipc' in keyword:
                    return 'India'
                elif 'us' in keyword or 'united states' in keyword:
                    return 'United States'
                elif 'uk' in keyword or 'united kingdom' in keyword or 'england' in keyword:
                    return 'United Kingdom'
                elif 'australia' in keyword:
                    return 'Australia'
                elif 'canada' in keyword:
                    return 'Canada'
        return 'General'
    
    def _detect_legal_domain(self, query: str) -> list:
        """Detect legal domains from query"""
        query_lower = query.lower()
        domains = []
        
        for domain, keywords in self.legal_domain_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                domains.append(domain)
        
        return domains if domains else ['general_legal']
    
    def _extract_entities(self, query: str) -> Dict[str, list]:
        """
        Extract named entities from query
        (Basic implementation - can be enhanced with NER models)
        """
        entities = {
            'acts': [],
            'cases': [],
            'persons': [],
            'organizations': []
        }
        
        # Simple pattern matching for acts/sections
        import re
        
        # Match section/article references (e.g., "Section 420", "Article 21")
        section_pattern = r'(?:section|article|sec|art)\s*\.?\s*(\d+[a-z]*)'
        entities['acts'] = re.findall(section_pattern, query, re.IGNORECASE)
        
        # Match case citations (e.g., "John v. Smith")
        case_pattern = r'([A-Z][a-z]+)\s+(?:v\.|versus)\s+([A-Z][a-z]+)'
        matches = re.findall(case_pattern, query)
        entities['cases'] = matches
        
        return entities
    
    def _extract_key_terms(self, query: str) -> list:
        """Extract key legal terms from query"""
        query_lower = query.lower()
        
        legal_terms = [
            'plaintiff', 'defendant', 'appellant', 'respondent', 'petitioner',
            'liability', 'damages', 'injunction', 'subpoena', 'deposition',
            'discovery', 'summary judgment', 'negligence', 'breach', 'contract',
            'tort', 'defamation', 'slander', 'libel', 'fraud', 'misrepresentation',
            'conviction', 'acquittal', 'appeal', 'rehearing', 'writ'
        ]
        
        found_terms = []
        for term in legal_terms:
            if term in query_lower:
                found_terms.append(term)
        
        return found_terms
