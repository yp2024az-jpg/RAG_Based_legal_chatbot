"""
Short-Term Memory - Session-based conversation context
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

class ConversationTurn:
    """Represents a single turn in conversation"""
    
    def __init__(self, query: str, response: str, category: str = None, timestamp: datetime = None):
        self.query = query
        self.response = response
        self.category = category
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'query': self.query,
            'response': self.response,
            'category': self.category,
            'timestamp': self.timestamp.isoformat()
        }


class ShortTermMemory:
    """
    Short-Term Memory (STM) for session context.
    Maintains conversation history with TTL expiration.
    """
    
    def __init__(self, max_size: int = 10, ttl_seconds: int = 3600):
        """
        Initialize STM
        
        Args:
            max_size: Maximum number of turns to keep
            ttl_seconds: Time-to-live for memory entries
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.history: List[ConversationTurn] = []
        self.session_metadata: Dict[str, Any] = {}
    
    def add_turn(self, query: str, response: str, category: str = None):
        """
        Add a conversation turn to memory
        
        Args:
            query: User query
            response: Bot response
            category: Query category
        """
        turn = ConversationTurn(query, response, category)
        self.history.append(turn)
        
        # Maintain max size
        if len(self.history) > self.max_size:
            self.history.pop(0)
    
    def get_context(self, lookback: int = 5) -> str:
        """
        Get recent conversation context
        
        Args:
            lookback: Number of turns to include
            
        Returns:
            Formatted context string
        """
        recent_turns = self.history[-lookback:] if len(self.history) > lookback else self.history
        
        context = []
        for turn in recent_turns:
            context.append(f"User: {turn.query}")
            context.append(f"Assistant: {turn.response}")
        
        return "\n".join(context)
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get full conversation history"""
        return [turn.to_dict() for turn in self.history]
    
    def clear(self):
        """Clear all history"""
        self.history.clear()
        self.session_metadata.clear()
    
    def set_metadata(self, key: str, value: Any):
        """Set session metadata"""
        self.session_metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get session metadata"""
        return self.session_metadata.get(key, default)
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        if not self.history:
            return False
        
        last_turn_time = self.history[-1].timestamp
        expiration_time = last_turn_time + timedelta(seconds=self.ttl_seconds)
        
        return datetime.now() > expiration_time
