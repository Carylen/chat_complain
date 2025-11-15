from fastapi import FastAPI, Request
from src.services.assistant_service import analyze_complaint_structured
from src.services.automation_service import handle_automation
from src.utils.context_manager import ConversationContext

app = FastAPI()
user_contexts = {}

def get_user_context(user_id: str) -> ConversationContext:
    if user_id not in user_contexts:
        user_contexts[user_id] = ConversationContext()
    return user_contexts[user_id]

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    data = await request.json()
    user_number = data["from"]
    message_text = data["text"]["body"]

    context = get_user_context(user_number)
    analysis = analyze_complaint_structured(message_text, context)
    if analysis:
        analysis, token_usage = analysis
        handle_automation(analysis, token_usage)

    return {"status": "ok"}