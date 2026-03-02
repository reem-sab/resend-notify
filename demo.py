import os
import base64
import resend
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()

resend.api_key = os.environ["RESEND_API_KEY"]

scheduled_time = datetime.now(timezone.utc) + timedelta(minutes=5)

with open("sample_deploy_log.txt", "rb") as f:
    log_content = base64.b64encode(f.read()).decode("utf-8")

params: resend.Emails.SendParams = {
    "from": os.environ["FROM_EMAIL"],
    "to": [os.environ["TO_EMAIL"]],
    "subject": "DX Demo: Scheduled Deploy Log with Attachment",
    "html": """
        <h2>Deployment Status: Pending Review</h2>
        <p>This is a <strong>transactional email</strong> demo for the Resend challenge.</p>
        <ul>
            <li><strong>Feature 1:</strong> Scheduled Delivery</li>
            <li><strong>Feature 2:</strong> Base64 Attachment</li>
        </ul>
        <p>Please see the attached log for details.</p>
    """,
    "scheduled_at": scheduled_time.isoformat(),
    "attachments": [
        {
            "filename": "deploy_log.txt",
            "content": log_content,
        }
    ],
}

email = resend.Emails.send(params)

print(f"Success! Demo email scheduled for: {scheduled_time.strftime('%Y-%m-%d %H:%M UTC')}")
print(f"   Email ID: {email['id']}")