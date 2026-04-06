"""
API Blueprint — Chatbot.

L'intégration du modèle de langage sera ajoutée ici à la dernière étape.
Pour l'instant le blueprint est enregistré et l'endpoint retourne un message
d'état afin de valider que la route est bien montée.
"""
from flask import Blueprint, jsonify

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat/status")
def status():
    return jsonify({"status": "chatbot not yet integrated"})


# TODO (dernière étape) : ajouter POST /api/chat/message
# @chat_bp.route("/chat/message", methods=["POST"])
# def message():
#     ...
