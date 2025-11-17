"""
Main application entry point with FAQ and WhatsApp integration.
Orchestrates complaint processing workflow using service layer.
"""

import sys
import os
from typing import Optional

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.config import settings
from src.schemas import ComplaintAnalysis, TokenUsage
from src.utils.context_manager import ConversationContext
from src.utils.logger import get_logger
from src.services.openai_service import create_openai_service
from src.services.automation_service import create_automation_service
from src.services.faq_service import create_faq_service
from src.services.whatsapp_service import create_whatsapp_service


# Initialize logger
logger = get_logger(__name__, settings.log_level)


class ComplaintProcessor:
    """Main application class for processing complaints with FAQ and WhatsApp"""
    
    def __init__(self):
        """Initialize complaint processor with all services"""
        logger.info("Initializing Complaint Processor")
        
        # Initialize services
        self.openai_service = create_openai_service()
        self.automation_service = create_automation_service()
        self.faq_service = create_faq_service()
        self.whatsapp_service = create_whatsapp_service()
        
        # Initialize context
        self.context = ConversationContext(
            max_messages=settings.max_context_messages,
            max_history=settings.max_complaint_history
        )
        
        logger.info("Complaint Processor initialized successfully")
    
    def process_complaint(self, user_text: str) -> Optional[dict]:
        """
        Process a customer complaint end-to-end with FAQ and WhatsApp.
        
        Workflow:
        1. Analyze complaint with AI
        2. Retrieve relevant FAQs
        3. Check if FAQ resolves issue
        4. If not resolved, provide WhatsApp contact
        5. Execute automation action
        
        Args:
            user_text: Customer complaint text
            
        Returns:
            Dictionary with processing results or None if error
        """
        logger.info(f"Processing complaint: '{user_text[:50]}...'")
        
        # Step 1: Analyze complaint with OpenAI
        result = self.openai_service.analyze_complaint(user_text, self.context)
        
        if not result:
            logger.error("Failed to analyze complaint")
            return None
        
        analysis, usage = result
        
        # Step 2: Display analysis results
        self._display_analysis(analysis, usage)
        
        # Step 3: Retrieve relevant FAQs
        faqs = self.faq_service.get_relevant_faqs(analysis, top_k=3)
        self._display_faqs(faqs)
        
        # Step 4: Check if FAQ resolves the issue
        faq_resolved = self.faq_service.check_if_faq_resolves_issue(analysis, faqs)
        
        # Step 5: Generate WhatsApp contact (if needed)
        whatsapp_contact = None
        if not faq_resolved:
            whatsapp_contact = self.whatsapp_service.generate_contact(analysis)
            if whatsapp_contact:
                self._display_whatsapp_contact(whatsapp_contact)
        
        # Step 6: Process automation logic
        action = self.automation_service.process_complaint(analysis, usage)
        
        # Step 7: Execute action
        execution_result = self.automation_service.execute_action(action)
        
        # Step 8: Display action results
        self._display_action(action, execution_result, faq_resolved)
        
        return {
            "analysis": analysis.model_dump(),
            "usage": usage.model_dump(),
            "faqs": [faq.to_dict() for faq in faqs],
            "faq_resolved": faq_resolved,
            "whatsapp_contact": whatsapp_contact.to_dict() if whatsapp_contact else None,
            "action": action.to_dict(),
            "result": execution_result
        }
    
    def _display_analysis(self, analysis: ComplaintAnalysis, usage: TokenUsage):
        """Display analysis results"""
        print("\n" + "="*70)
        print("🤖 COMPLAINT ANALYSIS")
        print("="*70)
        print(f"Product Category: {analysis.product_category}")
        print(f"Issue Category:   {analysis.issue_category}")
        print(f"Brief Summary:    {analysis.brief_summary}")
        print(f"\nExtracted Information:")
        for key, value in analysis.entities.model_dump().items():
            if value is not None:
                print(f"  - {key}: {value}")
        
        print(f"\n💰 TOKEN USAGE")
        print(f"Input:  {usage.input_token:,} tokens")
        print(f"Output: {usage.output_token:,} tokens")
        print(f"Total:  {usage.total_token:,} tokens")
        
        # Calculate cost
        costs = self.openai_service.estimate_cost(usage)
        print(f"Estimated Cost: ${costs['total_cost']:.6f}")
    
    def _display_faqs(self, faqs):
        """Display retrieved FAQs"""
        print("\n" + "="*70)
        print("📚 RELEVANT FAQs")
        print("="*70)
        
        if not faqs:
            print("No relevant FAQs found.")
            return
        
        for i, faq in enumerate(faqs, 1):
            print(f"\n❓ Q{i}: {faq.question}")
            print(f"   Relevance: {faq.score:.0f}%")
            print(f"\n💡 Answer:")
            # Indent the answer
            for line in faq.answer.split('\n'):
                print(f"   {line}")
            
            if i < len(faqs):
                print("\n" + "-"*70)
    
    def _display_whatsapp_contact(self, contact):
        """Display WhatsApp contact information"""
        print("\n" + "="*70)
        print("📱 WHATSAPP SUPPORT")
        print("="*70)
        
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        emoji = priority_emoji.get(contact.priority, "🔵")
        
        print(f"\n{emoji} Priority: {contact.priority.upper()}")
        print(f"📞 Department: {contact.department}")
        print(f"\n🔗 Click to chat:")
        print(f"   {contact.url}")
        print(f"\n📝 Pre-filled message:")
        print(f"   \"{contact.message}\"")
    
    def _display_action(self, action, result, faq_resolved):
        """Display action results"""
        print(f"\n" + "="*70)
        print("🚀 RESOLUTION STATUS")
        print("="*70)
        
        if faq_resolved:
            print("✅ Issue likely resolved with FAQ")
            print("   No further action required")
        else:
            print(f"Action Type: {action.action_type}")
            print(f"Status:      {result['status'].upper()}")
            
            if action.requires_escalation:
                print(f"⚠️  ESCALATION: Contact support via WhatsApp above")
            else:
                print(f"✅ AUTOMATED: {result['message']}")
    
    def reset_context(self):
        """Reset conversation context"""
        self.context.clear()
        logger.info("Context reset")
    
    def get_context_info(self) -> dict:
        """Get current context information"""
        return {
            "messages_count": len(self.context),
            "complaint_history": self.context.complaint_history,
            "context_repr": repr(self.context)
        }


def run_demo():
    """Run demonstration of the complaint processing system"""
    
    print("\n" + "="*70)
    print(" "*10 + "CUSTOMER SERVICE AUTOMATION WITH FAQ & WHATSAPP")
    print(" "*25 + "Powered by AI")
    print("="*70)
    
    # Initialize processor
    processor = ComplaintProcessor()
    
    # Test cases
    test_complaints = [
        {
            "name": "Product Not Received",
            "text": "My PLN token hasn't arrived yet. It's been 20 minutes. TRX ID: L7766"
        },
        {
            "name": "Wrong Destination Number",
            "text": "Hi, I sent $100 mobile credit to 0812111 by mistake. Should be 081999. ID: T5566"
        },
        {
            "name": "Transaction Failed",
            "text": "My transaction failed but money was deducted. TRX ID: F9988"
        },
        {
            "name": "Refund Request",
            "text": "I want a refund for my failed transaction T4455. When will I get my money back?"
        }
    ]
    
    # Process each complaint
    for i, complaint in enumerate(test_complaints, 1):
        print(f"\n\n{'='*70}")
        print(f"TEST CASE {i}: {complaint['name']}")
        print(f"{'='*70}")
        print(f"Customer: {complaint['text']}")
        
        result = processor.process_complaint(complaint['text'])
        
        if not result:
            print("\n❌ Failed to process complaint")
        
        # Add separator between test cases
        # if i < len(test_complaints):
        #     input("\n\nPress Enter to continue to next test case...")
    
    # Display final summary
    print("\n\n" + "="*70)
    print("📊 SESSION SUMMARY")
    print("="*70)
    context_info = processor.get_context_info()
    token_usage = processor.automation_service.token_usage
    print(f"Total complaints processed: {len(context_info['complaint_history'])}")
    print(f"Context state: {context_info['context_repr']}")
    print("\n\n" + "="*70)
    print(f"\n💰 TOKEN USAGE")
    print(f"Input:  {token_usage.get("input_token")} tokens")
    print(f"Output: {token_usage.get("output_token")} tokens")
    print(f"Total:  {token_usage.get("total_token")} tokens")
    
    print("\n" + "="*70)
    print(" "*25 + "DEMO COMPLETED")
    print("="*70)


def interactive_mode():
    """Run in interactive mode for manual testing"""
    print("\n" + "="*70)
    print(" "*20 + "INTERACTIVE MODE")
    print("="*70)
    print("\nCommands:")
    print("  - Type your complaint to process")
    print("  - 'quit' or 'exit' to exit")
    print("  - 'reset' to clear context")
    print("  - 'help' to show this help")
    
    processor = ComplaintProcessor()
    
    while True:
        try:
            user_input = input("\n🙋 Customer: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit']:
                print("\n👋 Thank you for using our service!")
                break
            
            if user_input.lower() == 'reset':
                processor.reset_context()
                print("✅ Context reset")
                continue
            
            if user_input.lower() == 'help':
                print("\nCommands:")
                print("  - Type your complaint to process")
                print("  - 'quit' or 'exit' to exit")
                print("  - 'reset' to clear context")
                print("  - 'help' to show this help")
                continue
            
            processor.process_complaint(user_input)
            
        except KeyboardInterrupt:
            print("\n\n👋 Exiting...")
            break
        except Exception as e:
            logger.error(f"Error in interactive mode: {e}", exc_info=True)
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    import sys
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        run_demo()