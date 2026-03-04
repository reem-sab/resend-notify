import os
import resend
import anthropic
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()

resend.api_key = os.environ["RESEND_API_KEY"]
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def summarize_log(log_content):
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": f"""You are summarizing a deployment log for a developer who hasn't reviewed it yet.

Log:
{log_content}

Write a 2-3 sentence plain-English summary of what happened in this deployment. Focus on what succeeded, any warnings, and whether action is needed. Be direct and practical."""}]
    )
    return message.content[0].text.strip()

with open("sample_deploy_log.txt", "r") as f:
    log_content = f.read()

print("Summarizing deploy log...")
summary = summarize_log(log_content)
print(f"Summary: {summary}")

scheduled_time = datetime.now(timezone.utc) + timedelta(hours=24)

params = {
    "from": os.environ["FROM_EMAIL"],
    "to": [os.environ["TO_EMAIL"]],
    "subject": "Reminder: Your deploy log needs review",
    "html": f"""
        <h2>You haven't reviewed your deploy log yet.</h2>
        <p><strong>AI Summary:</strong></p>
        <blockquote style="border-left: 4px solid #000; padding-left: 16px; color: #444;">
            {summary}
        </blockquote>
        <p>Review the full log in your dashboard or check the original email attachment.</p>
    """,
    "scheduled_at": scheduled_time.isoformat(),
}

email = resend.Emails.send(params)
print(f"Scheduled digest: {email['id']}")
print(f"Delivery time: {scheduled_time.strftime('%Y-%m-%d %H:%M UTC')}")