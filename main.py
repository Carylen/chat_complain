import os
import json
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

try:
    client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
except Exception as e:
    print(f"Error: Unable to initialize OpenAI client.")
    print("Make sure you have set OPENAI_API_KEY in your .env file")
    exit()

class Entities(BaseModel):
    """Entities extracted from the complaint"""
    amount: Optional[int] = None
    wrong_number: Optional[str] = None
    correct_number: Optional[str] = None
    transaction_id: Optional[str] = None

class ComplaintAnalysis(BaseModel):
    """Structure for complaint analysis output"""
    product_category: str
    issue_category: str
    entities: Entities
    brief_summary: str

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

def analyze_complaint_structured(
    user_text: str, 
    context: ConversationContext
) -> ComplaintAnalysis | None:
    """
    Analyze complaint using Structured Outputs.
    More efficient and type-safe compared to regular JSON.
    """
    
    system_prompt = f"""
        You are an AI Customer Service agent that analyzes customer complaints.

        Product Categories: Mobile Credit, Data Package, PLN Electricity, E-Wallet, Other
        Issue Categories: Product Not Received, Wrong Destination Number, Transaction Failed, Request Refund, Other

        Extract important information and create a brief summary (max 10 words).
        {context.get_context_summary()}
    """
    
    print(f"\n💬 Analyzing: '{user_text}'")
    
    try:
        # Using Structured Outputs with parse()
        completion = client.beta.chat.completions.parse(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            response_format=ComplaintAnalysis,
        )
        
        # Get parsed object directly (not JSON string)
        analysis = completion.choices[0].message.parsed
        
        # Save summary to context
        context.add_complaint_summary(analysis.brief_summary)
        
        return analysis
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def handle_automation(analysis: ComplaintAnalysis):
    """Execute business logic based on analysis"""
    
    print("\n--- 🤖 Analysis Result ---")
    print(f"Product: {analysis.product_category}")
    print(f"Issue: {analysis.issue_category}")
    print(f"Summary: {analysis.brief_summary}")
    print(f"Entities: {analysis.entities.model_dump()}")
    
    print("\n--- 🚀 Logic Execution ---")
    
    issue = analysis.issue_category
    entities = analysis.entities
    
    # Scenario 1: Wrong Destination Number
    if issue == "Wrong Destination Number":
        if entities.correct_number and entities.amount:
            print(f"✅ [ACTION]: Retry transaction {analysis.product_category} ${entities.amount:,}")
            print(f"   From: {entities.wrong_number or 'N/A'} → To: {entities.correct_number}")
            print(f"   [REPLY]: Transaction is being processed to {entities.correct_number}.")
        else:
            print("⚠️  [ACTION]: Escalate - Incomplete data")
            print("   [REPLY]: Please provide the correct destination number.")
    
    # Scenario 2: Request Refund
    elif issue == "Request Refund":
        if entities.transaction_id:
            print(f"✅ [ACTION]: Process refund for TRX {entities.transaction_id}")
            print(f"   [REPLY]: Refund for transaction {entities.transaction_id} is being processed.")
        else:
            print("⚠️  [ACTION]: Escalate - Transaction ID not found")
            print("   [REPLY]: Please provide the transaction number for refund.")
    
    # Scenario 3: Product Not Received
    elif issue == "Product Not Received":
        trx_id = entities.transaction_id or "N/A"
        print(f"✅ [ACTION]: Check transaction status {trx_id}")
        print(f"   [REPLY]: We are checking your transaction status.")
    
    # Other scenarios
    else:
        print("⚠️  [ACTION]: Escalate to CS agent")
        print(f"   [REPLY]: Our CS team will assist you shortly.")


if __name__ == "__main__":
    
    # Initialize context manager
    context = ConversationContext(max_messages=5)
    
    print("="*50)
    print("DEMO: Customer Service with Structured Outputs")
    print("="*50)
    
    # Example 1: Complete complaint
    print("\n[1] Wrong Number Complaint")
    complaint_1 = "Hi, I sent $100 mobile credit to 0812111 by mistake. Should be 081999. ID: T5566"
    
    analysis_1 = analyze_complaint_structured(complaint_1, context)
    if analysis_1:
        handle_automation(analysis_1)
    
    # Example 2: Refund complaint
    print("\n" + "="*50)
    print("\n[2] Refund Request")
    complaint_2 = "My $50 mobile credit failed, please refund."
    
    analysis_2 = analyze_complaint_structured(complaint_2, context)
    if analysis_2:
        handle_automation(analysis_2)
    
    # Example 3: Follow-up with context
    print("\n" + "="*50)
    print("\n[3] Follow-up (with context)")
    complaint_3 = "The TRX ID is T9988"
    
    analysis_3 = analyze_complaint_structured(complaint_3, context)
    if analysis_3:
        handle_automation(analysis_3)
    
    # Display context summary
    print("\n" + "="*50)
    print("\n📊 Context Summary:")
    print(f"Total complaints processed: {len(context.complaint_history)}")
    print(f"Summary: {context.complaint_history}")
    
    # Demo clear context
    print("\n🧹 Clearing context...")
    context.clear()
    print(f"Context after clear: {len(context.complaint_history)} complaints")