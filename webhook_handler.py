import os
import anthropic
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def explain_bounce(email_data):
    prompt = f"""An email bounce occurred with the following details:
- To: {email_data.get('to')}
- Subject: {email_data.get('subject')}
- Email ID: {email_data.get('email_id')}

In 2-3 sentences, explain what likely caused this bounce and what the developer should do next. Be specific and practical."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    event_type = data.get("type")
    email_data = data.get("data", {})

    print("\n── Webhook Event Received ──")
    print(f"  Event:    {event_type}")
    print(f"  Email ID: {email_data.get('email_id')}")
    print(f"  To:       {email_data.get('to')}")
    print(f"  Subject:  {email_data.get('subject')}")

    if event_type == "email.bounced":
        print("\n── AI Bounce Analysis ──")
        explanation = explain_bounce(email_data)
        print(f"  {explanation}")
        print("────────────────────────")
    else:
        print("───────────────────────────")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)