from typing import Tuple
from app.message.ai_helper.LLM_Shared import chatbot

reported_reason = "Offensive language in the chat"
additional_details = "The user called other members offensive names"



CLASSIFICATION_SYSTEM_PROMPT = """You are a content moderation classifier. Analyze the given message and classify it into exactly ONE of these categories:

1. **Spam** - User is sending unsolicited promotional content, repetitive messages, or irrelevant links
2. **Abuse** - Abusive language, insults, verbal attacks, or profanity directed at others



Respond ONLY in this exact format:
Content Category: Abuse/Safe


Be strict with classifications. When in doubt between Safe and another category, lean towards the concerning category for safety."""





def report_checking(reported_reason: str, additional_details: str) -> Tuple[str, str]:
    
    user_message = f"Reported Reason: {reported_reason}\nAdditional Details: {additional_details}"

    response = chatbot(
        user_message,
        system_prompt=CLASSIFICATION_SYSTEM_PROMPT,
        temperature=0.0
    )

    if "Abuse" in response:
        return "Offensive Content Detected", "high"
    elif "spam" in reported_reason.lower():
        return "Spam Behavior", "medium"
    else:
        return "Normal Behavior", "low"
    
a = report_checking(reported_reason, additional_details)
print(a)