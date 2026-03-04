import os
import base64
import resend
import anthropic
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.environ["RESEND_API_KEY"]
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def generate_subject(version, environment, status, duration):
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=50,
        messages=[{"role": "user", "content": f"""Generate a concise, professional email subject line for a deployment notification.
Details:
- Version: {version}
- Environment: {environment}
- Status: {status}
- Duration: {duration}

Reply with only the subject line, nothing else. No quotes."""}]
    )
    return message.content[0].text.strip()

# Deploy details
version = "v2.1.4"
environment = "production"
status = "success"
duration = "43s"

print("Generating subject line...")
subject = generate_subject(version, environment, status, duration)
print(f"Subject: {subject}")

with open("sample_deploy_log.txt", "rb") as f:
    log_content = base64.b64encode(f.read()).decode("utf-8")

params = {
    "from": os.environ["FROM_EMAIL"],
    "to": [os.environ["TO_EMAIL"]],
    "subject": subject,
    "html": f"""
        <h2>Deployment Successful ✓</h2>
        <p>Your deployment to <strong>{environment}</strong> completed successfully.</p>
        <ul>
            <li><strong>Version:</strong> {version}</li>
            <li><strong>Environment:</strong> {environment}</li>
            <li><strong>Duration:</strong> {duration}</li>
        </ul>
        <p>See the attached log for full details.</p>
    """,
    "attachments": [{"filename": "deploy_log.txt", "content": log_content}],
}

email = resend.Emails.send(params)
print(f"Email sent: {email['id']}")