# src/services/automation_service.py

from ..schemas import ComplaintAnalysis, TokenUsage

def handle_automation(analysis: ComplaintAnalysis, usage: TokenUsage):
    """Execute business logic based on analysis"""
    
    print("\n--- 🤖 Analysis Result ---")
    print(f"Product\t: {analysis.product_category}")
    print(f"Issue\t: {analysis.issue_category}")
    print(f"Summary\t: {analysis.brief_summary}")
    print(f"Entities\t: {analysis.entities.model_dump()}")

    print("\n--- 💰 Token Usage ---")
    print(f"Input\t: {usage.input_tokens} | Output: {usage.output_tokens} | Total: {usage.total_tokens}")
    costs = usage.cost_estimate("gpt-5-mini")
    print(f"Estimated Cost: ${costs['total_cost']:.6f} (Input: ${costs['input_cost']:.6f} + Output: ${costs['output_cost']:.6f})")
    
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