"""
LLM Response Generator
"""
from typing import Optional, Dict, Any, List
import hashlib
from .config import LLMConfig, PromptTemplates
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

class ResponseGenerator:
    """Generates responses using LLM"""
    
    def __init__(self):
        self.config = LLMConfig()
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Generative AI client"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.config.api_key)
            self.client = genai
        except ImportError:
            print("Warning: google-generativeai not installed")
    
    def generate(self, prompt: str) -> str:
        """
        Generate response using LLM
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated response
        """
        if not self.client:
            return "LLM client not initialized"
        
        try:
            model = self.client.GenerativeModel(self.config.model)
            response = model.generate_content(
                prompt,
                generation_config={
                    'temperature': self.config.temperature,
                    'top_k': self.config.top_k,
                    'top_p': self.config.top_p,
                    'max_output_tokens': self.config.max_output_tokens,
                }
            )
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def generate_with_context(self, query: str, context: str, 
                             query_type: str = "qa") -> str:
        """
        Generate response with context
        
        Args:
            query: User query
            context: Retrieved context
            query_type: Type of query (qa, comparison, summary, advice)
            
        Returns:
            Generated response
        """
        if query_type == "qa":
            prompt = PromptTemplates.get_qa_prompt(query, context)
        elif query_type == "comparison":
            prompt = PromptTemplates.get_comparison_prompt(context)
        elif query_type == "summary":
            prompt = PromptTemplates.get_summary_prompt(context)
        elif query_type == "advice":
            prompt = PromptTemplates.get_advice_prompt(query, context)
        else:
            prompt = PromptTemplates.get_qa_prompt(query, context)
        
        return self.generate(prompt)
    
    @staticmethod
    def create_query_hash(query: str) -> str:
        """Create hash of query for caching"""
        return hashlib.md5(query.encode()).hexdigest()
