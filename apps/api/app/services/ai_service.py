import logging

import google.generativeai as genai

from app.core.config import settings

logger = logging.getLogger(__name__)

_configured = False


def _ensure_configured() -> bool:
    global _configured
    if not settings.gemini_api_key:
        return False
    if not _configured:
        genai.configure(api_key=settings.gemini_api_key)
        _configured = True
    return True


def get_embedding(text: str, *, task_type: str = "retrieval_document") -> list[float]:
    """Return a Gemini embedding for the given text.

    Falls back to a zero vector if no API key is configured so the rest of the
    pipeline keeps working in local/dev without credentials.
    """
    if not _ensure_configured():
        return [0.0] * settings.embedding_dimensions

    response = genai.embed_content(
        model=settings.embedding_model,
        content=text[:8000],
        task_type=task_type,
        output_dimensionality=settings.embedding_dimensions,
    )
    return response["embedding"]


def _generate_text_groq(prompt: str, *, system: str | None = None) -> str:
    from groq import Groq

    client = Groq(api_key=settings.groq_api_key)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    completion = client.chat.completions.create(
        model=settings.groq_text_model,
        messages=messages,
        temperature=0.4,
    )
    return completion.choices[0].message.content or ""


def _generate_text_gemini(prompt: str) -> str:
    if not _ensure_configured():
        return ""
    try:
        model = genai.GenerativeModel(settings.gemini_text_model)
        response = model.generate_content(prompt)
        return response.text or ""
    except Exception as exc:  # noqa: BLE001 - never crash the request on provider errors
        logger.warning("Gemini generation failed: %s", exc)
        return ""


def generate_text(prompt: str, *, system: str | None = None) -> str:
    """Generate text, preferring Groq (fast, free) and falling back to Gemini."""
    if settings.groq_api_key:
        try:
            return _generate_text_groq(prompt, system=system)
        except Exception as exc:  # noqa: BLE001 - fall back to Gemini on Groq failure
            logger.warning("Groq generation failed, falling back to Gemini: %s", exc)

    result = _generate_text_gemini(prompt)
    if result:
        return result
    return (
        "AI text generation is temporarily unavailable (provider quota reached). "
        "Add a free GROQ_API_KEY from https://console.groq.com/keys for fast, reliable generation."
    )
