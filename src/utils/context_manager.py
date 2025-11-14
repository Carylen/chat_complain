# src/utils/context_manager.py

from typing import List

class ConversationContext:
    """Manages conversation context to save memory"""
    
    def __init__(self, max_messages: int = 5):
        self.messages: List[dict] = []
        self.max_messages = max_messages
        self.complaint_history: List[str] = []  # Summary of previous complaints
    
    def add_message(self, role: str, content: str):
        """Add message to context"""
        self.messages.append({"role": role, "content": content})
        self._trim_context()
    
    def add_complaint_summary(self, summary: str):
        """Store complaint summary for reference"""
        self.complaint_history.append(summary)
        if len(self.complaint_history) > 3:  # Keep max 3 recent complaints
            self.complaint_history.pop(0)
    
    def _trim_context(self):
        """Trim old messages to save memory"""
        if len(self.messages) > self.max_messages:
            # Always keep system message (index 0)
            system_msg = self.messages[0] if self.messages[0]["role"] == "system" else None
            
            # Get recent messages
            recent_messages = self.messages[-(self.max_messages-1):]
            
            # Recombine
            if system_msg:
                self.messages = [system_msg] + recent_messages
            else:
                self.messages = recent_messages
    
    def get_messages(self) -> List[dict]:
        """Get messages to send to API"""
        return self.messages
    
    def get_context_summary(self) -> str:
        """Get context summary to add to prompt"""
        if not self.complaint_history:
            return ""
        
        return f"\nPrevious complaints: {'; '.join(self.complaint_history)}"
    
    def clear(self):
        """Clear context"""
        self.messages = []
        self.complaint_history = []