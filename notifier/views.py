import json
import base64
import os
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import resend
import anthropic
from .models import DeployEvent, WebhookEvent

resend.api_key = settings.RESEND_API_KEY


def get_ai_subject(version, environment, status, duration):
    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=60,
            messages=[{
                "role": "user",
                "content": f"Write a concise email subject line for a deploy notification. Version: {version}, Environment: {environment}, Status: {status}, Duration: {duration}s. Return only the subject line, nothing else."
            }]
        )
        return message.content[0].text.strip()
    except Exception:
        return f"Deploy {status.upper()}: {version} to {environment}"


def get_ai_bounce_analysis(event_data):
    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            messages=[{
                "role": "user",
                "content": f"An email bounced. Explain why in plain English and suggest a fix. Email data: {json.dumps(event_data)}. Be concise — 2-3 sentences max."
            }]
        )
        return message.content[0].text.strip()
    except Exception:
        return "Email bounced. Check the recipient address and try again."


def dashboard(request):
    deploys = DeployEvent.objects.order_by('-triggered_at')[:10]
    events = WebhookEvent.objects.order_by('-received_at')[:20]
    return render(request, 'notifier/dashboard.html', {
        'deploys': deploys,
        'events': events,
    })


@csrf_exempt
def trigger_deploy(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    version = f"v{datetime.now().strftime('%Y.%m.%d-%H%M')}"
    environment = 'production'
    status = 'success'
    duration = 47

    deploy = DeployEvent.objects.create(
        version=version,
        environment=environment,
        status=status,
        duration=duration,
    )

    subject = get_ai_subject(version, environment, status, duration)

    log_path = os.path.join(settings.BASE_DIR, 'sample_deploy_log.txt')
    try:
        with open(log_path, 'rb') as f:
            log_b64 = base64.b64encode(f.read()).decode('utf-8')
        attachment = [{"filename": "deploy_log.txt", "content": log_b64}]
    except FileNotFoundError:
        attachment = []

    try:
        response = resend.Emails.send({
            "from": "Resend Notify <onboarding@resend.dev>",
            "to": [settings.NOTIFICATION_EMAIL],
            "subject": subject,
            "html": f"""
                <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #1a1a2e;">Deploy Notification</h2>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr><td style="padding: 8px; color: #666;">Version</td><td style="padding: 8px; font-weight: bold;">{version}</td></tr>
                        <tr style="background: #f9f9f9;"><td style="padding: 8px; color: #666;">Environment</td><td style="padding: 8px; font-weight: bold;">{environment}</td></tr>
                        <tr><td style="padding: 8px; color: #666;">Status</td><td style="padding: 8px; font-weight: bold; color: #16a34a;">{status}</td></tr>
                        <tr style="background: #f9f9f9;"><td style="padding: 8px; color: #666;">Duration</td><td style="padding: 8px; font-weight: bold;">{duration}s</td></tr>
                    </table>
                    <p style="color: #666; font-size: 14px; margin-top: 20px;">Deploy log attached.</p>
                </div>
            """,
            "attachments": attachment,
        })
        email_id = response.get('id', 'unknown')
    except Exception as e:
        email_id = 'error'

    scheduled_at = (datetime.utcnow() + timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    try:
        resend.Emails.send({
            "from": "Resend Notify <onboarding@resend.dev>",
            "to": [settings.NOTIFICATION_EMAIL],
            "subject": f"24hr Digest: {version}",
            "html": f"<p>This is your 24-hour follow-up digest for deploy {version}.</p>",
            "scheduled_at": scheduled_at,
        })
    except Exception:
        pass

    return JsonResponse({
        'success': True,
        'version': version,
        'subject': subject,
        'email_id': email_id,
        'deploy_id': deploy.id,
    })


@csrf_exempt
def webhook_handler(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    event_type = data.get('type', 'unknown')
    event_data = data.get('data', {})
    recipient = event_data.get('to', ['unknown'])[0] if event_data.get('to') else 'unknown'
    email_id = event_data.get('email_id', 'unknown')

    ai_analysis = None
    if event_type == 'email.bounced':
        ai_analysis = get_ai_bounce_analysis(event_data)

    WebhookEvent.objects.create(
        event_type=event_type,
        email_id=email_id,
        recipient=recipient,
        ai_analysis=ai_analysis,
    )

    return JsonResponse({'status': 'received', 'type': event_type})