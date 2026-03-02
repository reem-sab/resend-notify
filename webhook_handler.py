import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    payload = request.get_json(force=True, silent=True)
    
    if not payload:
        return jsonify({"status": "error", "message": "invalid payload"}), 400

    event_type = payload.get("type", "unknown")
    data = payload.get("data", {})
    email_id = data.get("email_id", "unknown")
    to = data.get("to", [])
    subject = data.get("subject", "unknown")

    print(f"\n── Webhook Event Received ──")
    print(f"  Event:    {event_type}")
    print(f"  Email ID: {email_id}")
    print(f"  To:       {to}")
    print(f"  Subject:  {subject}")
    print(f"───────────────────────────\n")

    return jsonify({"status": "received"}), 200

@app.after_request
def add_headers(response):
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"✓ Webhook handler running on port {port}")
    print(f"  Webhook URL: https://avalyn-limitative-savingly.ngrok-free.dev/webhook")
    app.run(port=port, debug=True)