from typing import List, Dict, Any, Optional
from src.core.rag_pipeline import RAGPipeline
from src.utils import setup_logger, InvalidQueryException

logger = setup_logger(__name__)

class LegalAdvisorBot:
    """
    RAG-based Legal Advisor Chatbot.
    Main interface for user interactions.
    """
    
    def __init__(self):
        """Initialize the Legal Advisor Bot"""
        self.pipeline = RAGPipeline()
        self.sessions = {}  # Store active sessions
        logger.info("Legal Advisor Bot initialized")
    
    def ingest_legal_documents(self, documents: List[str], 
                               metadata_list: List[Dict[str, Any]] = None):
        """
        Ingest legal documents
        
        Args:
            documents: List of document texts
            metadata_list: Optional metadata
        """
        self.pipeline.ingest_documents(documents, metadata_list)
        logger.info(f"Ingested {len(documents)} documents")
    
    def query(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a legal query
        
        Args:
            query: User query
            session_id: Optional session ID
            
        Returns:
            Response dictionary
        """
        try:
            response = self.pipeline.process_query(query, session_id)
            return response
        except InvalidQueryException as e:
            logger.warning(f"Invalid query: {e}")
            return {
                'query': query,
                'response': f"I'm sorry, but your query doesn't appear to be related to legal matters. "
                           f"Please ask a legal question and I'll be happy to help.",
                'error': True,
                'error_message': str(e)
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'query': query,
                'response': "I encountered an error processing your query. Please try again.",
                'error': True,
                'error_message': str(e)
            }
    
    def start_session(self, session_id: str):
        """Start a new session"""
        self.sessions[session_id] = {
            'created_at': __import__('datetime').datetime.now().isoformat(),
            'queries': 0
        }
        logger.info(f"Started session: {session_id}")
    
    def end_session(self, session_id: str):
        """End a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Ended session: {session_id}")
    
    def get_session_context(self, session_id: str = None) -> str:
        """Get conversation context from session"""
        return self.pipeline.stm.get_context()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bot statistics"""
        stats = self.pipeline.get_pipeline_stats()
        stats['active_sessions'] = len(self.sessions)
        return stats
    
    def reset(self):
        """Reset the bot"""
        self.pipeline = RAGPipeline()
        self.sessions = {}
        logger.info("Bot reset successfully")


# Example usage helper
def demo_usage():
    """
    Example usage of the Legal Advisor Bot
    """
    # Initialize bot
    bot = LegalAdvisorBot()
    
    # Sample legal documents
    sample_docs = [
        "Indian Penal Code Section 420: Whoever cheats and thereby dishonestly induces "
        "the person deceived to deliver any property to any person, or to make, alter "
        "or destroy the whole or any part of a valuable security, or anything which is "
        "signed or sealed, with the intent that it may be used as a valuable security...",
        
        "Criminal Procedure Code Section 154: Any person can lodge a First Information Report "
        "with the police station for cognizable offences. The FIR must contain the basic details "
        "of the alleged crime and the names of the accused if known...",
    ]
    
    # Ingest documents
    bot.ingest_legal_documents(sample_docs)
    
    # Process queries
    queries = [
        "What is cheating under Indian law?",
        "How do I file an FIR?"
    ]
    
    for query in queries:
        response = bot.query(query)
        print(f"\nQuery: {query}")
        print(f"Response: {response['response']}")
        print(f"Category: {response['category']}")


if __name__ == "__main__":
    demo_usage()
