# src/services/automation_service.py

"""
Automation service for handling business logic and actions.
Processes complaint analysis and triggers appropriate actions.
"""

from typing import Dict, Any, Optional
from uuid import uuid4
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.schemas import ComplaintAnalysis, TokenUsage
from src.utils.logger import get_logger
from src.config import AutomationRules, settings


logger = get_logger(__name__, settings.log_level)


class AutomationAction:
    """Represents an automation action to be executed"""
    
    def __init__(
        self,
        action_type: str,
        endpoint: str,
        payload: Dict[str, Any],
        requires_escalation: bool = False
    ):
        self.action_id = str(uuid4())
        self.action_type = action_type
        self.endpoint = endpoint
        self.payload = payload
        self.requires_escalation = requires_escalation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary"""
        return {
            "action_id": self.action_id,
            "action_type": self.action_type,
            "endpoint": self.endpoint,
            "payload": self.payload,
            "requires_escalation": self.requires_escalation
        }


class AutomationService:
    """Service for handling complaint automation logic"""
    
    def __init__(self):
        """Initialize automation service"""
        logger.info("Automation service initialized")
    
    def process_complaint(
        self,
        analysis: ComplaintAnalysis,
        usage: TokenUsage
    ) -> AutomationAction:
        """
        Process complaint and determine action.
        
        Args:
            analysis: Parsed complaint analysis
            usage: Token usage information
            
        Returns:
            AutomationAction to execute
        """
        logger.log_complaint(
            complaint_id=str(uuid4()),
            product=analysis.product_category,
            issue=analysis.issue_category,
            action_taken="Processing"
        )
        
        # Get automation configuration for this issue
        config = AutomationRules.get_action_config(analysis.issue_category)
        
        # Check if all required fields are present
        missing_fields = self._check_required_fields(
            analysis.entities.model_dump(),
            config.get("required_fields", [])
        )
        
        if missing_fields and config.get("escalate_if_missing", False):
            return self._create_escalation_action(
                analysis,
                missing_fields
            )
        
        # Route to appropriate handler
        if analysis.issue_category == "Wrong Destination Number":
            return self._handle_wrong_number(analysis, config)
        
        elif analysis.issue_category == "Request Refund":
            return self._handle_refund(analysis, config)
        
        elif analysis.issue_category == "Product Not Received":
            return self._handle_not_received(analysis, config)
        
        elif analysis.issue_category == "Transaction Failed":
            return self._handle_failed_transaction(analysis, config)
        
        else:
            return self._create_escalation_action(
                analysis,
                reason="Unhandled issue category"
            )
    
    def _check_required_fields(
        self,
        entities: Dict[str, Any],
        required_fields: list
    ) -> list:
        """
        Check which required fields are missing.
        
        Args:
            entities: Entity dictionary
            required_fields: List of required field names
            
        Returns:
            List of missing field names
        """
        missing = []
        for field in required_fields:
            if not entities.get(field):
                missing.append(field)
        return missing
    
    def _handle_wrong_number(
        self,
        analysis: ComplaintAnalysis,
        config: Dict
    ) -> AutomationAction:
        """Handle wrong destination number scenario"""
        entities = analysis.entities
        
        payload = {
            "product": analysis.product_category,
            "amount": entities.amount,
            "wrong_number": entities.wrong_number,
            "correct_number": entities.correct_number,
            "original_transaction_id": entities.transaction_id
        }
        
        logger.info(
            f"Retry transaction: {analysis.product_category} "
            f"${entities.amount} to {entities.correct_number}"
        )
        
        return AutomationAction(
            action_type="RETRY_TRANSACTION",
            endpoint=config["api_endpoint"],
            payload=payload,
            requires_escalation=False
        )
    
    def _handle_refund(
        self,
        analysis: ComplaintAnalysis,
        config: Dict
    ) -> AutomationAction:
        """Handle refund request scenario"""
        entities = analysis.entities
        
        payload = {
            "transaction_id": entities.transaction_id,
            "amount": entities.amount,
            "reason": analysis.brief_summary
        }
        
        logger.info(f"Processing refund for transaction: {entities.transaction_id}")
        
        return AutomationAction(
            action_type="PROCESS_REFUND",
            endpoint=config["api_endpoint"],
            payload=payload,
            requires_escalation=False
        )
    
    def _handle_not_received(
        self,
        analysis: ComplaintAnalysis,
        config: Dict
    ) -> AutomationAction:
        """Handle product not received scenario"""
        entities = analysis.entities
        
        payload = {
            "transaction_id": entities.transaction_id,
            "product": analysis.product_category
        }
        
        logger.info(f"Checking status for transaction: {entities.transaction_id}")
        
        return AutomationAction(
            action_type="CHECK_STATUS",
            endpoint=config["api_endpoint"],
            payload=payload,
            requires_escalation=False
        )
    
    def _handle_failed_transaction(
        self,
        analysis: ComplaintAnalysis,
        config: Dict
    ) -> AutomationAction:
        """Handle failed transaction scenario"""
        entities = analysis.entities
        
        payload = {
            "transaction_id": entities.transaction_id,
            "product": analysis.product_category,
            "amount": entities.amount
        }
        
        logger.info(f"Investigating failed transaction: {entities.transaction_id}")
        
        return AutomationAction(
            action_type="INVESTIGATE_FAILURE",
            endpoint=config["api_endpoint"],
            payload=payload,
            requires_escalation=False
        )
    
    def _create_escalation_action(
        self,
        analysis: ComplaintAnalysis,
        reason: Any
    ) -> AutomationAction:
        """Create escalation action for CS agent"""
        payload = {
            "product": analysis.product_category,
            "issue": analysis.issue_category,
            "summary": analysis.brief_summary,
            "reason": str(reason)
        }
        
        logger.warning(f"Escalating complaint: {reason}")
        
        return AutomationAction(
            action_type="ESCALATE",
            endpoint="/api/escalate",
            payload=payload,
            requires_escalation=True
        )
    
    def execute_action(self, action: AutomationAction) -> Dict[str, Any]:
        """
        Execute automation action (simulate API call).
        
        Args:
            action: AutomationAction to execute
            
        Returns:
            Execution result dictionary
        """
        logger.info(f"Executing action: {action.action_type} (ID: {action.action_id})")
        
        # In production, this would make actual API calls
        # For now, simulate the execution
        
        if settings.debug_mode:
            logger.debug(f"Action details: {action.to_dict()}")
        
        return {
            "action_id": action.action_id,
            "status": "success" if not action.requires_escalation else "escalated",
            "message": self._generate_response_message(action)
        }
    
    def _generate_response_message(self, action: AutomationAction) -> str:
        """Generate customer-facing response message"""
        messages = {
            "RETRY_TRANSACTION": f"Transaction is being processed to {action.payload.get('correct_number')}.",
            "PROCESS_REFUND": f"Refund for transaction {action.payload.get('transaction_id')} is being processed.",
            "CHECK_STATUS": "We are checking your transaction status.",
            "INVESTIGATE_FAILURE": "We are investigating the failed transaction.",
            "ESCALATE": "Our CS team will assist you shortly."
        }
        
        return messages.get(action.action_type, "Your request is being processed.")


def create_automation_service() -> AutomationService:
    """
    Factory function to create automation service.
    
    Returns:
        AutomationService instance
    """
    return AutomationService()