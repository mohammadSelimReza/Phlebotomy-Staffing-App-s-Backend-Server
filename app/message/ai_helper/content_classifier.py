"""Content classification module for categorizing user queries."""

from typing import Dict, Optional
from app.message.ai_helper.LLM_Shared import chatbot


CLASSIFICATION_SYSTEM_PROMPT = """You are a content moderation classifier. Analyze the given message and classify it into exactly ONE of these categories:

1. **Harassment** - Bullying, intimidation, stalking, or targeted personal attacks
2. **NSFW** - Explicit sexual content, nudity, or adult material
3. **Abuse** - Abusive language, insults, verbal attacks, or profanity directed at others
4. **Violence** - Threats of violence, graphic violent content, or promotion of physical harm
5. **Hate Speech** - Discriminatory content targeting race, religion, ethnicity, gender, sexual orientation, or other protected characteristics
6. **Self-Harm** - Content promoting self-injury, suicide, or eating disorders
7. **Safe** - Appropriate, clean content that doesn't fit the above categories

Also determine the sentiment as either:
- **Positive** - Constructive, friendly, optimistic, or neutral-to-positive tone
- **Negative** - Hostile, pessimistic, angry, or harmful tone

Respond ONLY in this exact format:
Content Category: [category name]
Sentiment: [positive/negative]
Confidence: [high/medium/low]

Be strict with classifications. When in doubt between Safe and another category, lean towards the concerning category for safety."""


def _parse_classification_response(response_text: str) -> Dict[str, str]:
    """Parse the classification response into structured data."""
    result = {
        'content_category': 'Safe',
        'sentiment': 'positive',
        'confidence': 'medium'
    }

    for line in response_text.split('\n'):
        line = line.strip()
        if line.startswith('Content Category:'):
            result['content_category'] = line.split(':', 1)[1].strip()
        elif line.startswith('Sentiment:'):
            result['sentiment'] = line.split(':', 1)[1].strip().lower()
        elif line.startswith('Confidence:'):
            result['confidence'] = line.split(':', 1)[1].strip().lower()

    return result


def classify_content(
    message: str,
    *,
    model: str = "gpt-4.1-nano",
    temperature: float = 0.3,
    api_key: Optional[str] = None,
) -> Dict[str, str]:
    """
    Classify a message into content categories and sentiment.

    Args:
        message: The user message to classify.
        model: OpenAI model identifier. Defaults to "gpt-3.5-turbo".
        temperature: Sampling temperature (lower for more consistent results). Defaults to 0.3.
        api_key: OpenAI API key. Defaults to None (uses OPENAI_API_KEY from .env file).

    Returns:
        Dict[str, str]: A dictionary containing:
            - 'content_category': One of the 7 content categories
            - 'sentiment': Either 'positive' or 'negative'
            - 'confidence': Confidence level of the classification

    Content Categories:
        - Harassment: Bullying, intimidation, or targeted attacks
        - NSFW: Not safe for work, explicit sexual content
        - Abuse: Abusive language, insults, or verbal attacks
        - Violence: Threats, violent content, or promotion of harm
        - Hate Speech: Discriminatory content based on race, religion, etc.
        - Self-Harm: Content promoting self-injury or suicide
        - Safe: Clean, appropriate content
    """
    response_text = chatbot(
        user_message=f"Classify this message: {message}",
        system_prompt=CLASSIFICATION_SYSTEM_PROMPT,
        model=model,
        temperature=temperature,
        api_key=api_key
    )

    return _parse_classification_response(response_text)


FLAGGED_REASON_MAP = {
    "Harassment": ("Harassment detected", "Harassment"),
    "NSFW": ("Adult content detected", "NSFW Content"),
    "Abuse": ("Profanity detected", "Inappropriate Language"),
    "Violence": ("Threat or violence detected", "Violent Content"),
    "Hate Speech": ("Hate speech detected", "Hate Speech"),
    "Self-Harm": ("Self-harm content detected", "Self-Harm"),
}

PROFANITY_KEYWORDS = {
    "idiot",
    "hate",
    "stupid",
    "kill you",
    "dumb",
    "bitch",
}


def message_checker(
    text_message: str,
    *,
    model: str = "gpt-4.1-nano",
    temperature: float = 0.3,
    api_key: Optional[str] = None,
) -> Dict[str, str]:
    """Return approval status for a given message using lightweight heuristics + LLM."""
    normalized = text_message.lower()

    if any(keyword in normalized for keyword in PROFANITY_KEYWORDS):
        return {
            "ai_approval_status": "inappropriate",
            "reported_reason": "Profanity detected",
            "reported_title": "Inappropriate Language",
        }

    classification = classify_content(
        text_message,
        model=model,
        temperature=temperature,
        api_key=api_key,
    )

    category = classification.get("content_category", "Safe")
    reason = FLAGGED_REASON_MAP.get(category)

    if reason:
        reported_reason, reported_title = reason
        return {
            "ai_approval_status": "inappropriate",
            "reported_reason": reported_reason,
            "reported_title": reported_title,
            "sentiment": classification.get("sentiment", "unknown"),
        }

    return {
        "ai_approval_status": "approved",
    }


