import json
import os
import sys
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(__file__))

from rag import chat
from config import DATA_DIR

app = Flask(__name__, static_folder="../frontend")
CORS(app)

LOG_FILE = os.path.join(DATA_DIR, "conversations.jsonl")
os.makedirs(DATA_DIR, exist_ok=True)

conversation_history = {}


def log_conversation(session_id, query, answer):
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "query": query,
            "answer": answer,
        }) + "\n")


@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json()
    query = data.get("query", "").strip()
    session_id = data.get("session_id", "default")

    if not query:
        return jsonify({"error": "Query is required"}), 400

    history = conversation_history.get(session_id, [])
    answer, chunks = chat(query, history)

    history.append({"role": "user", "content": query})
    history.append({"role": "assistant", "content": answer})
    conversation_history[session_id] = history[-10:]

    log_conversation(session_id, query, answer)

    return jsonify({
        "answer": answer,
        "sources": [{"url": c["url"], "section": c["section"]} for c in chunks],
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
