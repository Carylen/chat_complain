# src/services/whatsapp_service.py
"""
WhatsApp Service for generating department-specific contact links.
Routes users to the correct support team based on issue category.
"""

from typing import Dict, Optional
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.schemas import ComplaintAnalysis
from src.config import WhatsAppConfig, settings
from src.utils.logger import get_logger


logger = get_logger(__name__, settings.log_level)


class WhatsAppContact:
    """Represents a WhatsApp contact with routing info"""
    
    def __init__(
        self,
        department: str,
        phone: str,
        message: str,
        url: str,
        priority: str
    ):
        self.department = department
        self.phone = phone
        self.message = message
        self.url = url
        self.priority = priority
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "department": self.department,
            "phone": self.phone,
            "message": self.message,
            "url": self.url,
            "priority": self.priority
        }


class WhatsAppService:
    """Service for WhatsApp routing and contact generation"""
    
    def __init__(self):
        """Initialize WhatsApp service"""
        self.config = WhatsAppConfig()
        logger.info("WhatsApp service initialized")
    
    def generate_contact(
        self,
        analysis: ComplaintAnalysis
    ) -> Optional[WhatsAppContact]:
        """
        Generate WhatsApp contact for the complaint.
        
        Args:
            analysis: Complaint analysis object
            
        Returns:
            WhatsAppContact object or None if disabled
        """
        if not settings.whatsapp_enabled:
            logger.info("WhatsApp integration is disabled")
            return None
        
        logger.info(f"Generating WhatsApp contact for: {analysis.issue_category}")
        
        # Get department info
        dept_info = self.config.get_department_info(analysis.issue_category)
        
        # Prepare message variables
        message_vars = self._extract_message_variables(analysis)
        
        # Generate WhatsApp URL
        url = self.config.generate_whatsapp_url(
            analysis.issue_category,
            **message_vars
        )
        
        # Get formatted message
        try:
            formatted_message = dept_info["message_template"].format(**message_vars)
        except KeyError:
            formatted_message = dept_info["message_template"]
        
        contact = WhatsAppContact(
            department=dept_info["department"],
            phone=dept_info["phone"],
            message=formatted_message,
            url=url,
            priority=dept_info["priority"]
        )
        
        logger.info(f"WhatsApp contact generated for department: {contact.department}")
        
        return contact
    
    def _extract_message_variables(self, analysis: ComplaintAnalysis) -> Dict:
        """
        Extract variables from analysis for message template.
        
        Args:
            analysis: Complaint analysis
            
        Returns:
            Dictionary of variables
        """
        entities = analysis.entities.model_dump()
        
        variables = {
            "trx_id": entities.get("transaction_id", "N/A"),
            "wrong_number": entities.get("wrong_number", "N/A"),
            "correct_number": entities.get("correct_number", "N/A"),
            "amount": entities.get("amount", "N/A"),
            "details": analysis.brief_summary
        }
        
        return variables
    
    def format_contact_message(self, contact: WhatsAppContact) -> str:
        """
        Format contact info into user-friendly message.
        
        Args:
            contact: WhatsAppContact object
            
        Returns:
            Formatted message string
        """
        priority_emoji = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }
        
        emoji = priority_emoji.get(contact.priority, "🔵")
        
        message = f"""
            📞 **Need Further Assistance?**

            {emoji} **Department:** {contact.department}
            📱 **Contact via WhatsApp**

            Click the link below to chat with our support team:
            {contact.url}

            Your message will be pre-filled with relevant information to help us assist you faster!
        """.strip()
        
        return message
    
    def get_all_departments(self) -> Dict[str, Dict]:
        """
        Get information about all departments.
        
        Returns:
            Dictionary of all departments
        """
        return self.config.DEPARTMENTS


def create_whatsapp_service() -> WhatsAppService:
    """
    Factory function to create WhatsApp service.
    
    Returns:
        WhatsAppService instance
    """
    return WhatsAppService()