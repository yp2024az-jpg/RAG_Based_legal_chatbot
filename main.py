"""
Main Application Entry Point
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core import LegalAdvisorBot
from src.utils import setup_logger

logger = setup_logger(__name__)

def main():
    """Main application entry point"""
    
    print("=" * 60)
    print("RAG-Based Legal Advisor Bot")
    print("=" * 60)
    
    # Initialize bot
    bot = LegalAdvisorBot()
    
    # Sample legal documents for demonstration
    sample_documents = [
        """
        Indian Penal Code - Section 420 (Cheating and Dishonestly Inducing Delivery of Property):
        Whoever cheats and thereby dishonestly induces the person deceived to deliver any 
        property to any person, or to make, alter or destroy the whole or any part of a valuable 
        security, or anything which is signed or sealed, with the intent that it may be used as 
        a valuable security, shall be punished with imprisonment of either description for a term 
        which may extend to seven years, and shall also be liable to fine.
        """,
        
        """
        Criminal Procedure Code - Section 154 (Registration of FIR):
        (1) Any person can lodge a First Information Report (FIR) regarding any cognizable offence 
        at the nearest police station.
        (2) The FIR must contain the basic facts and details of the alleged crime and names of 
        the accused if known.
        (3) If the police refuse to register an FIR, the person can approach the Magistrate.
        """,
        
        """
        Indian Penal Code - Section 302 (Punishment for Murder):
        Whoever commits murder shall be punished with imprisonment of either description for a 
        term which may extend to life, or with rigorous imprisonment for a term which may extend 
        to ten years, and shall also be liable to fine, or to both.
        """,
    ]
    
    # Ingest documents
    print("\n[*] Ingesting legal documents...")
    bot.ingest_legal_documents(sample_documents)
    
    # Interactive query loop
    print("\n[*] Legal Advisor Bot is ready. Type 'quit' to exit.\n")
    
    session_id = "demo_session"
    bot.start_session(session_id)
    
    while True:
        try:
            query = input("You: ").strip()
            
            if query.lower() in ['quit', 'exit', 'bye']:
                print("Bot: Thank you for using the Legal Advisor Bot. Goodbye!")
                bot.end_session(session_id)
                break
            
            if not query:
                continue
            
            # Process query
            response = bot.query(query, session_id)
            
            # Print response
            print(f"\nBot: {response['response']}")
            print(f"Category: {response['category']}")
            print(f"Confidence: {response['category_confidence']:.2f}\n")
            
        except KeyboardInterrupt:
            print("\n\nBot: Session interrupted. Goodbye!")
            bot.end_session(session_id)
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Bot: I encountered an error. Please try again.\n")


if __name__ == "__main__":
    main()
