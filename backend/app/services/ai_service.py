"""Optional AI helper.

The default provider is a deterministic local stub so the whole application
runs offline with no API key. Swap AI_PROVIDER=openai and set OPENAI_API_KEY
to call a real model. Ticket text is treated as untrusted input and is never
used to invoke tools or change system policy.
"""

from app.core.config import get_settings
from app.models.ticket import CATEGORIES, PRIORITIES

_URGENT_WORDS = ("urgent", "asap", "down", "outage", "cannot login", "production")
_HIGH_WORDS = ("broken", "error", "failed", "fail", "crash", "refund")

_CATEGORY_HINTS = {
    "billing": ("invoice", "refund", "charge", "payment", "billing", "subscription"),
    "account": ("password", "login", "reset", "account", "locked", "sign in"),
    "technical": ("error", "server", "api", "connection", "timeout", "deploy"),
    "bug": ("bug", "crash", "reproduce", "glitch", "broken"),
}


def _stub_suggestion(title: str, description: str) -> dict:
    text = f"{title} {description}".lower()

    category = "general"
    for name, hints in _CATEGORY_HINTS.items():
        if any(h in text for h in hints):
            category = name
            break

    priority = "Low"
    if any(w in text for w in _URGENT_WORDS):
        priority = "Urgent"
    elif any(w in text for w in _HIGH_WORDS):
        priority = "High"
    elif len(text) > 120:
        priority = "Medium"

    draft = (
        f"Hello,\n\nThanks for reaching out about \"{title}\". "
        "We have logged this as a "
        f"{priority.lower()} priority {category} request and are looking into it. "
        "We will follow up with an update shortly.\n\nRegards,\nSupport Team"
    )
    rationale = (
        f"Heuristic match: keywords in the ticket suggest category '{category}' "
        f"and priority '{priority}'. This is a suggestion only - a human must review it."
    )
    return {"category": category, "priority": priority, "rationale": rationale, "draft_reply": draft}


def suggest(title: str, description: str) -> dict:
    settings = get_settings()
    base = _stub_suggestion(title, description)

    if not settings.ai_enabled:
        base["rationale"] = "AI suggestions are disabled (AI_ENABLED=false)."

    base["category"] = base["category"] if base["category"] in CATEGORIES else "general"
    base["priority"] = base["priority"] if base["priority"] in PRIORITIES else "Medium"
    base["provider"] = settings.ai_provider
    base["model"] = settings.ai_model
    return base
