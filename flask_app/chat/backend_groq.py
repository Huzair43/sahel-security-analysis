"""
Groq API backend: Gemma 2 9B (or any Groq-hosted model).

Groq free tier: ~6,000 requests/day, ~500,000 tokens/day.
We use gemma2-9b-it to stay consistent with the local Gemma setup.

Environment variables:
  GROQ_API_KEY  : required
  GROQ_MODEL    : default gemma2-9b-it
"""

import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = os.getenv("GROQ_MODEL",   "gemma2-9b-it")
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"


def generate(messages: list[dict[str, str]]) -> str:
    """
    Send messages to Groq and return the assistant's reply.
    Uses the OpenAI-compatible Groq endpoint.
    Raises RuntimeError on failure.
    """
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. "
            "Add it to your .env file or environment variables."
        )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json",
    }

    payload = {
        "model":       GROQ_MODEL,
        "messages":    messages,
        "temperature": 0.3,
        "max_tokens":  512,
    }

    try:
        resp = requests.post(GROQ_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError("Groq API request timed out after 30 seconds.")
    except requests.exceptions.HTTPError as e:
        try:
            detail = resp.json().get("error", {}).get("message", str(e))
        except Exception:
            detail = str(e)
        raise RuntimeError(f"Groq API error: {detail}")
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Cannot reach Groq API. Check your internet connection.")

    data = resp.json()

    # OpenAI-compatible response: choices[0].message.content
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"Unexpected Groq response format: {data}") from e


def is_available() -> bool:
    """Check whether GROQ_API_KEY is configured."""
    return bool(GROQ_API_KEY)
