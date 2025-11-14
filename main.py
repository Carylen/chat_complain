import sys
from src.services.assistant_service import analyze_complaint_structured
from src.services.automation_service import handle_automation
from src.utils.context_manager import ConversationContext
from src.config import logger

def run_demo(total_usage_stats: dict):
    """Menjalankan demo dengan beberapa contoh komplain."""
    logger.info("="*50)
    logger.info(" Using Demo Mode...")
    logger.info("="*50)
    
    context = ConversationContext(max_messages=5)
    
    complaints = [
        ("Hi, I sent 100rb mobile credit to 0812111 by mistake. Should be 081999. ID: T5566", "[1] Komplain Salah Nomor"),
        ("My 50rb mobile credit failed, please refund.", "[2] Permintaan Refund"),
        ("The TRX ID is T9988", "[3] Follow-up (dengan konteks)")
    ]
    
    for text, title in complaints:
        logger.info("\n" + "="*50)
        logger.info(title)
        
        analysis_result = analyze_complaint_structured(text, context)
        
        if analysis_result:
            analysis, token_usage = analysis_result
            handle_automation(analysis, token_usage)
            
            new_costs = token_usage.cost_estimate("gpt-5-mini")
            for key in total_usage_stats:
                total_usage_stats[key] += new_costs[key]
    
    logger.info("\n" + "="*50)
    logger.info("📊 Context Summary\t:")
    logger.info(f"Total complaints processed: {len(context.complaint_history)}")
    logger.info(f"Summary\t: {context.complaint_history}")

def run_interactive(total_usage_stats: dict):
    """Menjalankan mode interaktif di terminal."""
    
    logger.info("="*50)
    logger.info(" Using Interactive Mode...")
    logger.info("="*50)
    
    context = ConversationContext(max_messages=5)

    while True:
        try:
            user_text = input("Anda: ")
            if user_text.lower() in ['exit', 'quit']:
                logger.info("Thank You! Exit Interactive Mode..")
                break
            
            if not user_text:
                continue

            analysis_result = analyze_complaint_structured(user_text, context)
            
            if analysis_result:
                analysis, token_usage = analysis_result
                handle_automation(analysis, token_usage)
                
                # Akumulasi biaya dan token
                new_costs = token_usage.cost_estimate("gpt-5-mini")
                for key in total_usage_stats:
                    total_usage_stats[key] += new_costs.get(key, 0.0)
            
            logger.info("-" * 20) # Pemisah
            
        except KeyboardInterrupt:
            logger.info("\nThank You! Exit Interactive Mode..")
            break
        except Exception as e:
            logger.error(e)

if __name__ == "__main__":
    total_usage_stats = {
        "input_token": 0, "output_token": 0, "total_token": 0,
        "input_cost": 0.0, "output_cost": 0.0, "total_cost": 0.0
    }
    
    mode = "demo" # Default, can change to "interactive"
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == "interactive":
            mode = "interactive"
    
    if mode == "demo":
        run_demo(total_usage_stats)
    else:
        run_interactive(total_usage_stats)
    
    # Cetak laporan total biaya di akhir
    logger.info("\n" + "="*50)
    logger.info("📊 Session Summary")
    logger.info(f"  Total Input Tokens\t: {total_usage_stats['input_token']}")
    logger.info(f"  Total Output Tokens: {total_usage_stats['output_token']}")
    logger.info(f"  Total Tokens\t: {total_usage_stats['total_token']}")
    logger.info("-" * 20)
    logger.info(f"  Total Input Cost\t: ${total_usage_stats['input_cost']:.6f}")
    logger.info(f"  Total Output Cost\t: ${total_usage_stats['output_cost']:.6f}")
    logger.info(f"  Total Cost\t: ${total_usage_stats['total_cost']:.6f}")