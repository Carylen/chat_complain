# src/services/assistant_service.py

from ..schemas import ComplaintAnalysis, TokenUsage
from ..config import client
from ..schemas import ComplaintAnalysis, TokenUsage
from ..utils.context_manager import ConversationContext

def analyze_complaint_structured(
    user_text: str, 
    context: ConversationContext
) -> tuple[ComplaintAnalysis, TokenUsage] | None:
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
        response = client.responses.parse(
            model="gpt-4o-mini",
            instructions=system_prompt,
            input=user_text,
            text_format=ComplaintAnalysis
        )
        
        analysis = response.output_parsed
        
        # Save summary to context
        context.add_complaint_summary(analysis.brief_summary)
        usage = TokenUsage(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            total_tokens=response.usage.total_tokens
        )
        
        return analysis, usage
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None