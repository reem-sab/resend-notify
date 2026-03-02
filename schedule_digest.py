import os
import resend
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()

resend.api_key = os.environ["RESEND_API_KEY"]

# Schedule a follow-up digest 24 hours from now
scheduled_time = datetime.now(timezone.utc) + timedelta(hours=24)

params: resend.Emails.SendParams = {
    "from": os.environ["FROM_EMAIL"],
    "to": [os.environ["TO_EMAIL"]],
    "subject": "Reminder: Review your deploy log from yesterday",
    "html": """
        <h2>Daily Deploy Digest</h2>
        <p>You haven't reviewed yesterday's deployment log yet.</p>
        <ul>
            <li><strong>Version:</strong> v2.1.4</li>
            <li><strong>Environment:</strong> production</li>
            <li><strong>Status:</strong> Successful</li>
        </ul>
        <p>Log into your dashboard to review and close out this deployment.</p>
    """,
    "scheduled_at": scheduled_time.isoformat(),
}

email = resend.Emails.send(params)
print(f"✓ Digest scheduled for: {scheduled_time.strftime('%Y-%m-%d %H:%M UTC')}")
print(f"  Email ID: {email['id']}")