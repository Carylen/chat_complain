# src/utils/context_manager.py

"""
Context management utilities for conversation handling.
Provides memory-efficient conversation tracking with automatic trimming.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    """Represents a single conversation message"""
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to OpenAI message format"""
        return {"role": self.role, "content": self.content}


class ConversationContext:
    """
    Manages conversation context with automatic memory management.
    Implements sliding window approach for memory efficiency.
    """
    
    def __init__(self, max_messages: int = 5, max_history: int = 3):
        """
        Initialize conversation context.
        
        Args:
            max_messages: Maximum number of messages to keep in memory
            max_history: Maximum number of complaint summaries to track
        """
        self.messages: List[Message] = []
        self.max_messages = max_messages
        self.complaint_history: List[str] = []
        self.max_history = max_history
        self._system_message: Optional[Message] = None
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add message to context with automatic trimming.
        
        Args:
            role: Message role (system, user, assistant)
            content: Message content
        """
        message = Message(role=role, content=content)
        
        # Handle system message separately
        if role == "system":
            self._system_message = message
        else:
            self.messages.append(message)
            self._trim_context()
    
    def add_complaint_summary(self, summary: str) -> None:
        """
        Store complaint summary for reference.
        
        Args:
            summary: Brief summary of the complaint
        """
        self.complaint_history.append(summary)
        if len(self.complaint_history) > self.max_history:
            self.complaint_history.pop(0)
    
    def _trim_context(self) -> None:
        """Trim old messages to save memory using sliding window"""
        if len(self.messages) > self.max_messages:
            # Keep only the most recent messages
            self.messages = self.messages[-self.max_messages:]
    
    def get_messages(self) -> List[Dict[str, str]]:
        """
        Get messages formatted for OpenAI API.
        
        Returns:
            List of message dictionaries
        """
        result = []
        
        # Add system message first if exists
        if self._system_message:
            result.append(self._system_message.to_dict())
        
        # Add conversation messages
        result.extend([msg.to_dict() for msg in self.messages])
        
        return result
    
    def get_context_summary(self) -> str:
        """
        Get formatted context summary for prompts.
        
        Returns:
            Formatted string of previous complaints or empty string
        """
        if not self.complaint_history:
            return ""
        
        return f"\nPrevious complaints: {'; '.join(self.complaint_history)}"
    
    def get_last_n_messages(self, n: int) -> List[Message]:
        """
        Get the last N messages.
        
        Args:
            n: Number of recent messages to retrieve
            
        Returns:
            List of recent messages
        """
        return self.messages[-n:] if n <= len(self.messages) else self.messages
    
    def clear(self) -> None:
        """Clear all context and history"""
        self.messages = []
        self.complaint_history = []
        self._system_message = None
    
    def clear_messages_only(self) -> None:
        """Clear messages but keep complaint history"""
        self.messages = []
    
    def export_conversation(self) -> Dict:
        """
        Export conversation for logging or analysis.
        
        Returns:
            Dictionary containing full conversation state
        """
        return {
            "system_message": self._system_message.to_dict() if self._system_message else None,
            "messages": [
                {
                    **msg.to_dict(),
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in self.messages
            ],
            "complaint_history": self.complaint_history,
            "stats": {
                "total_messages": len(self.messages),
                "total_complaints": len(self.complaint_history)
            }
        }
    
    def __len__(self) -> int:
        """Return number of messages in context"""
        return len(self.messages)
    
    def __repr__(self) -> str:
        """String representation of context state"""
        return (
            f"ConversationContext("
            f"messages={len(self.messages)}/{self.max_messages}, "
            f"history={len(self.complaint_history)}/{self.max_history})"
        )


class ContextManager:
    """
    Factory for managing multiple conversation contexts.
    Useful for multi-user scenarios.
    """
    
    def __init__(self):
        """Initialize context manager"""
        self._contexts: Dict[str, ConversationContext] = {}
    
    def get_or_create_context(
        self, 
        user_id: str, 
        max_messages: int = 5,
        max_history: int = 3
    ) -> ConversationContext:
        """
        Get existing context or create new one for user.
        
        Args:
            user_id: Unique user identifier
            max_messages: Maximum messages to keep
            max_history: Maximum complaint history
            
        Returns:
            ConversationContext for the user
        """
        if user_id not in self._contexts:
            self._contexts[user_id] = ConversationContext(
                max_messages=max_messages,
                max_history=max_history
            )
        return self._contexts[user_id]
    
    def remove_context(self, user_id: str) -> bool:
        """
        Remove context for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if context was removed, False if not found
        """
        if user_id in self._contexts:
            del self._contexts[user_id]
            return True
        return False
    
    def clear_all_contexts(self) -> None:
        """Clear all user contexts"""
        self._contexts.clear()
    
    def get_active_users(self) -> List[str]:
        """Get list of active user IDs"""
        return list(self._contexts.keys())
    
    def __len__(self) -> int:
        """Return number of active contexts"""
        return len(self._contexts)