"""
Local LLM backend: Gemma via Ollama.

Ollama exposes an OpenAI-compatible /api/chat endpoint on localhost:11434.
In Docker Compose, the Ollama service is reachable at http://ollama:11434.

Environment variables:
  OLLAMA_HOST   : default http://ollama:11434
  OLLAMA_MODEL  : default gemma2:2b
"""

import os
import requests

OLLAMA_HOST  = os.getenv("OLLAMA_HOST",  "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma2:2b")


def generate(messages: list[dict[str, str]]) -> str:
    """
    Send messages to Ollama and return the assistant's reply.
    Raises RuntimeError if Ollama is unreachable or returns an error.
    """
    url = f"{OLLAMA_HOST}/api/chat"

    payload = {
        "model":    OLLAMA_MODEL,
        "messages": messages,
        "stream":   False,
        "options": {
            "temperature": 0.3,
            "num_predict": 512,
        },
    }

    try:
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            f"Cannot reach Ollama at {OLLAMA_HOST}. "
            "Make sure the ollama service is running."
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("Ollama request timed out after 60 seconds.")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Ollama HTTP error: {e}")

    data = resp.json()

    # Ollama /api/chat response: {"message": {"role": "assistant", "content": "..."}}
    try:
        return data["message"]["content"].strip()
    except (KeyError, TypeError) as e:
        raise RuntimeError(f"Unexpected Ollama response format: {data}") from e


def is_available() -> bool:
    """Check whether the Ollama service is reachable."""
    try:
        resp = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False
