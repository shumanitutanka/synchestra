from flask import Flask, request, jsonify
from synchestra.supervisor import supervisor as sup

app = Flask(__name__)

@app.route("/synchestra", methods=["POST"])
def synchestra_api():
    data = request.json

    query = data.get("query")
    session_id = data.get("session_id", "default")
    chat_id = data.get("chat_id", "default")

    # 🔥 Chiamata diretta al supervisor (orchestrator eliminato)
    result = sup(query, session_id, chat_id)

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6001)
