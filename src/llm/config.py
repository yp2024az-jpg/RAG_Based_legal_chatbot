"""
LLM Configuration and utilities
"""
import os
from typing import Optional

class LLMConfig:
    """Configuration for LLM"""
    
    def __init__(self):
        self.api_key = os.getenv('google_api_key', '')
        self.model = 'gemini-2.5-pro'
        self.temperature = 0.7
        self.max_output_tokens = 2048
        self.top_k = 40
        self.top_p = 0.95


class PromptTemplates:
    """Prompt templates for different query types"""
    
    @staticmethod
    def get_qa_prompt(query: str, context: str) -> str:
        """Get QA prompt"""
        return f"""You are a legal expert AI assistant. Answer the following legal query based on the provided context.

Context:
{context}

Query: {query}

Provide a comprehensive, accurate answer citing relevant legal principles and case law where applicable."""
    
    @staticmethod
    def get_comparison_prompt(context: str) -> str:
        """Get case comparison prompt"""
        return f"""You are a legal expert. Analyze and compare the following legal cases or laws.

{context}

Provide a detailed comparison highlighting key similarities, differences, and implications."""
    
    @staticmethod
    def get_summary_prompt(context: str) -> str:
        """Get summarization prompt"""
        return f"""You are a legal expert. Summarize the following legal case or information concisely.

{context}

Provide a clear, concise summary highlighting key points, holdings, and implications."""
    
    @staticmethod
    def get_advice_prompt(query: str, context: str) -> str:
        """Get legal advice prompt"""
        return f"""You are a legal advisor. Based on the following information, provide legal guidance.

Query: {query}

Relevant Information:
{context}

Provide practical legal guidance while noting that this is not substitute for professional legal counsel."""
