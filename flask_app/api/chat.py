"""
Chat API blueprint.

POST /api/chat/message
  Body  : {"question": "How many incidents in Mali in 2023?"}
  Reply : {"answer": "...", "backend": "groq|local", "context": {...}}

GET /api/chat/status
  Reply : {"backend": "groq|local|unavailable", "model": "..."}

Backend selection via CHAT_BACKEND environment variable:
  "groq"  : Groq API (default, recommended for deployment)
  "local" : Gemma via Ollama (local Docker setup)
"""

import os
from flask import Blueprint, request, jsonify

from flask_app.chat.rag import get_rag_prompt

chat_bp = Blueprint("chat", __name__)

CHAT_BACKEND = os.getenv("CHAT_BACKEND", "groq")


def _get_backend():
    if CHAT_BACKEND == "local":
        from flask_app.chat import backend_local as backend
    else:
        from flask_app.chat import backend_groq as backend
    return backend


# ── Status ─────────────────────────────────────────────────────────────────────

@chat_bp.route("/chat/status")
def status():
    backend = _get_backend()
    available = backend.is_available()

    if CHAT_BACKEND == "local":
        model = os.getenv("OLLAMA_MODEL", "gemma2:2b")
    else:
        model = os.getenv("GROQ_MODEL", "gemma2-9b-it")

    return jsonify({
        "backend":   CHAT_BACKEND if available else "unavailable",
        "model":     model,
        "available": available,
    })


# ── Chat ───────────────────────────────────────────────────────────────────────

@chat_bp.route("/chat/message", methods=["POST"])
def message():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"error": "No question provided."}), 400

    if len(question) > 500:
        return jsonify({"error": "Question too long (max 500 characters)."}), 400

    try:
        messages, context = get_rag_prompt(question)
        backend = _get_backend()
        answer  = backend.generate(messages)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500

    return jsonify({
        "answer":  answer,
        "backend": CHAT_BACKEND,
        "context": {
            "total_incidents":  context.get("total_incidents"),
            "total_fatalities": context.get("total_fatalities"),
            "date_range":       context.get("date_range"),
        },
    })
