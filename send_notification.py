import os
import base64
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.environ["RESEND_API_KEY"]

# Load the deploy log attachment
with open("sample_deploy_log.txt", "rb") as f:
    log_content = base64.b64encode(f.read()).decode("utf-8")

params: resend.Emails.SendParams = {
    "from": os.environ["FROM_EMAIL"],
    "to": [os.environ["TO_EMAIL"]],
    "subject": "Deploy Complete: production-v2.1.4",
    "html": """
        <h2>Deployment Successful ✓</h2>
        <p>Your deployment to <strong>production</strong> completed successfully.</p>
        <ul>
            <li><strong>Version:</strong> v2.1.4</li>
            <li><strong>Environment:</strong> production</li>
            <li><strong>Duration:</strong> 43s</li>
        </ul>
        <p>See the attached log for full details.</p>
    """,
    "attachments": [
        {
            "filename": "deploy_log.txt",
            "content": log_content,
        }
    ],
}

email = resend.Emails.send(params)
print(f"✓ Notification sent: {email['id']}")