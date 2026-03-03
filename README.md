# resend-notify

A developer notification system built with [Resend](https://resend.com). Simulates real-world transactional email workflows triggered by deployment events — including attachments, scheduled follow-ups, and webhook event tracking.

Built as a practical demonstration of Resend's core API capabilities using Python.

---

## What This Does

When a deployment completes, `resend-notify` automatically:

1. **Sends a notification email** to the developer with a deploy log attached
2. **Schedules a follow-up digest** if no action is taken within 24 hours
3. **Listens for webhook events** (delivered, opened, bounced) and logs them in real time

This mirrors how engineering teams use transactional email in production — not for marketing, but for reliable, event-driven communication.

---

## Prerequisites

- Python 3.8+
- A [Resend account](https://resend.com/signup) (free tier works)
- A [Resend API key](https://resend.com/api-keys)
- A verified sending domain, or use `onboarding@resend.dev` for testing

---

## Quickstart

Get from zero to a sent email in under 5 minutes.

### 1. Clone the repo

```bash
git clone https://github.com/reem-sab/resend-notify.git
cd resend-notify
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your environment variables

```bash
cp .env.example .env
```

Open `.env` and add your Resend API key:

```
RESEND_API_KEY=re_your_api_key_here
FROM_EMAIL=onboarding@resend.dev
TO_EMAIL=you@yourdomain.com
```

> **Note:** `onboarding@resend.dev` works without a verified domain and is ideal for testing. To send from your own domain, [verify it in the Resend dashboard](https://resend.com/domains) first.
>
> **Security:** Never commit your `.env` file. It is already in `.gitignore`, but double-check before pushing.

### 4. Send your first notification

```bash
python send_notification.py
```

You should receive an email with a deploy log attached within seconds.

---

## How-To Guides

### Send a notification with an attachment

`send_notification.py` sends a transactional email triggered by a simulated deploy event. It attaches `sample_deploy_log.txt` as a base64-encoded file.

```python
import resend
import base64

resend.api_key = os.environ["RESEND_API_KEY"]

with open("sample_deploy_log.txt", "rb") as f:
    log_content = base64.b64encode(f.read()).decode("utf-8")

params = {
    "from": os.environ["FROM_EMAIL"],
    "to": [os.environ["TO_EMAIL"]],
    "subject": "Deploy Complete: production-v2.1.4",
    "html": "<p>Your deployment completed successfully. See the attached log for details.</p>",
    "attachments": [
        {
            "filename": "deploy_log.txt",
            "content": log_content,
        }
    ],
}

email = resend.Emails.send(params)
print(f"Email sent: {email['id']}")
```

Resend accepts attachments as base64-encoded strings. Supported file types include `.txt`, `.pdf`, `.csv`, and more.

---

### Schedule a follow-up email

`schedule_digest.py` sends a follow-up digest email 24 hours after the initial notification. Resend supports natural language scheduling via the `scheduled_at` parameter.

```python
from datetime import datetime, timedelta, timezone

scheduled_time = datetime.now(timezone.utc) + timedelta(hours=24)

params = {
    "from": os.environ["FROM_EMAIL"],
    "to": [os.environ["TO_EMAIL"]],
    "subject": "Reminder: Review your deploy log",
    "html": "<p>You haven't reviewed yesterday's deploy log yet. Here's a quick summary.</p>",
    "scheduled_at": scheduled_time.isoformat(),
}

email = resend.Emails.send(params)
print(f"Scheduled email ID: {email['id']}")
```

You can verify scheduled emails in the [Resend dashboard](https://resend.com/emails) under the **Scheduled** tab.

---

### Handle webhook events

`webhook_handler.py` runs a local Flask server that receives and logs real-time event notifications from Resend.

#### Start the server

```bash
python3 webhook_handler.py
```

#### Test it locally with curl

In a separate terminal tab, send a simulated webhook event:

```bash
curl -X POST http://127.0.0.1:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email.delivered",
    "data": {
      "email_id": "test123",
      "to": ["you@yourdomain.com"],
      "subject": "Deploy Complete: production-v2.1.4"
    }
  }'
```

You should see this in the Flask terminal:

```
── Webhook Event Received ──
  Event:    email.delivered
  Email ID: test123
  To:       ['you@yourdomain.com']
  Subject:  Deploy Complete: production-v2.1.4
───────────────────────────
```

#### Register a live endpoint

In production, expose your server using a tool like [ngrok](https://ngrok.com) and register the public URL in the [Resend Webhooks dashboard](https://resend.com/webhooks):

```
https://your-ngrok-url.ngrok-free.dev/webhook
```

Resend will then send real-time POST requests to your endpoint for every email event.

**Webhook payload example (email.delivered):**

```json
{
  "type": "email.delivered",
  "created_at": "2025-03-01T12:00:00.000Z",
  "data": {
    "email_id": "abc123",
    "from": "onboarding@resend.dev",
    "to": ["you@yourdomain.com"],
    "subject": "Deploy Complete: production-v2.1.4"
  }
}
```

**Supported event types:**

| Event | Description |
|---|---|
| `email.sent` | Email accepted by Resend |
| `email.delivered` | Email delivered to recipient's server |
| `email.opened` | Recipient opened the email |
| `email.clicked` | Recipient clicked a link |
| `email.bounced` | Email could not be delivered |
| `email.complained` | Recipient marked email as spam |

---

## Reference

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `RESEND_API_KEY` | Yes | Your Resend API key |
| `FROM_EMAIL` | Yes | Verified sender address |
| `TO_EMAIL` | Yes | Recipient address |
| `WEBHOOK_SECRET` | No | Secret for verifying webhook signatures |

### Project Files

| File | Description |
|---|---|
| `demo.py` | Runs the full demo sequence — send, schedule, and webhook instructions |
| `send_notification.py` | Sends a deploy notification email with an attached log file |
| `schedule_digest.py` | Schedules a follow-up email 24 hours later |
| `webhook_handler.py` | Flask server that receives and logs Resend webhook events |
| `sample_deploy_log.txt` | Sample deploy log used as an email attachment |
| `templates/notification.html` | HTML email template |

---

## Why Webhooks Matter

Most email APIs are fire-and-forget. You send an email and hope it arrives.

Webhooks change that. Instead of polling an API to check whether your email was delivered, Resend pushes an event to your server the moment something happens. This lets you:

- **React to bounces immediately** — remove bad addresses before they hurt your sender reputation
- **Trigger follow-up logic** — if an email wasn't opened after 24 hours, send a reminder
- **Build audit trails** — log every delivery event for compliance or debugging
- **Monitor deliverability** — catch spam complaints before they become a pattern

In production, webhooks are the difference between email infrastructure you can observe and email infrastructure that runs blind.

---

## Why Scheduling Matters

Scheduling decouples *when you trigger an email* from *when it should be sent*. This is useful for:

- **Reminders** — notify users before a subscription expires or a trial ends
- **Digests** — batch activity into a single daily or weekly summary
- **Time zone awareness** — queue emails to arrive during business hours regardless of when the event fired

Resend's `scheduled_at` parameter accepts an ISO 8601 timestamp, keeping implementation simple without requiring a separate job queue.

---

## Resources

- [Resend Python SDK](https://github.com/resend/resend-python)
- [Resend API Reference](https://resend.com/docs/api-reference/introduction)
- [Webhook Events Reference](https://resend.com/docs/webhooks/introduction)
- [Resend Dashboard](https://resend.com)

---

## License

MIT
