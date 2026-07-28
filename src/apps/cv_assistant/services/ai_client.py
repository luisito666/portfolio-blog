"""OpenAI-compatible AI client wrapper.

Works with any provider that implements the OpenAI API spec
(OpenAI, ZAI/GLM, DeepSeek, etc.) via configurable base_url.
"""
from openai import OpenAI
from django.conf import settings


def get_ai_client():
    """Return an OpenAI client configured with the project's AI_* settings."""
    return OpenAI(
        api_key=settings.AI_API_KEY,
        base_url=settings.AI_BASE_URL,
    )


def chat_completion(messages, model=None, temperature=None, max_tokens=None):
    """Send messages to the AI and return the response text.

    Args:
        messages: List of dicts with 'role' and 'content' keys.
        model: Model name override (defaults to settings.AI_MODEL).
        temperature: Sampling temperature override.
        max_tokens: Max output tokens override.

    Returns:
        The assistant's response content as a string.
    """
    client = get_ai_client()
    response = client.chat.completions.create(
        model=model or settings.AI_MODEL,
        messages=messages,
        temperature=temperature if temperature is not None else settings.AI_TEMPERATURE,
        max_tokens=max_tokens or settings.AI_MAX_TOKENS,
    )
    return response.choices[0].message.content