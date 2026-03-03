import os
import base64
import resend
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()

resend.api_key = os.environ["RESEND_API_KEY"]

print("\n── resend-notify demo ──────────────────")
print("A developer notification system built with Resend\n")

# Step 1: Send notification with attachment
print("Step 1: Sending deploy notification with log attachment...")

with open("sample_deploy_log.txt", "rb") as f:
    log_content = base64.b64encode(f.read()).decode("utf-8")

notification = resend.Emails.send({
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
    "attachments": [{"filename": "deploy_log.txt", "content": log_content}],
})
print(f"✓ Notification sent: {notification['id']}\n")

# Step 2: Schedule follow-up digest
print("Step 2: Scheduling follow-up digest for 24 hours from now...")

scheduled_time = datetime.now(timezone.utc) + timedelta(hours=24)

digest = resend.Emails.send({
    "from": os.environ["FROM_EMAIL"],
    "to": [os.environ["TO_EMAIL"]],
    "subject": "Reminder: Review your deploy log",
    "html": "<p>You haven't reviewed yesterday's deploy log yet.</p>",
    "scheduled_at": scheduled_time.isoformat(),
})
print(f"✓ Digest scheduled for: {scheduled_time.strftime('%Y-%m-%d %H:%M UTC')}")
print(f"  Email ID: {digest['id']}\n")

# Step 3: Webhook instructions
print("Step 3: Webhook handler")
print("  Run in a separate terminal: python3 webhook_handler.py")
print("  Then simulate an event:     python3 simulate_webhook.py")
print("\n────────────────────────────────────────\n")
