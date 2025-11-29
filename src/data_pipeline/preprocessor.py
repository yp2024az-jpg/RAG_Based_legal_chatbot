"""
Data Preprocessor - Cleans and normalizes legal documents
"""
import re
from typing import List

class DataPreprocessor:
    """Preprocesses legal documents"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep legal punctuation
        text = re.sub(r'[^\w\s\.\,\:\;\-\(\)\/]', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def normalize_case_citations(text: str) -> str:
        """
        Normalize case citations
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        # Normalize "v." to "v"
        text = re.sub(r'\bv\.\b', 'v', text)
        
        # Normalize section references
        text = re.sub(r'Sec\.?\s*(\d+)', r'Section \1', text)
        text = re.sub(r'Art\.?\s*(\d+)', r'Article \1', text)
        
        return text
    
    @staticmethod
    def extract_case_name(text: str) -> str:
        """
        Extract case name from text
        
        Args:
            text: Input text
            
        Returns:
            Case name if found
        """
        # Pattern: Name v. Name
        match = re.search(r'([A-Z][a-zA-Z\s]+)\s+v\s+([A-Z][a-zA-Z\s]+)', text)
        if match:
            return f"{match.group(1).strip()} v {match.group(2).strip()}"
        return ""
    
    @staticmethod
    def remove_duplicate_spaces(text: str) -> str:
        """Remove duplicate spaces"""
        return re.sub(r' +', ' ', text)
