from django.db import models

class DeployEvent(models.Model):
    version = models.CharField(max_length=50)
    environment = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    duration = models.IntegerField()
    triggered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.version} - {self.environment} - {self.status}"

class WebhookEvent(models.Model):
    event_type = models.CharField(max_length=50)
    email_id = models.CharField(max_length=100)
    recipient = models.CharField(max_length=100)
    ai_analysis = models.TextField(blank=True, null=True)
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} - {self.recipient}"
