"""
Multi-channel Notification Service for CrisisLens.

Supports email, SMS, and push notifications with templating and delivery tracking.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
from enum import Enum
from dataclasses import dataclass
import asyncio
from jinja2 import Template

logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class NotificationTemplate:
    """Notification template configuration."""
    subject: str
    body: str
    html_body: Optional[str] = None


class NotificationService:
    """Multi-channel notification delivery service."""
    
    def __init__(self):
        self.templates: Dict[str, NotificationTemplate] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load notification templates."""
        # Alert template
        self.templates['alert'] = NotificationTemplate(
            subject="CrisisLens Alert: {{ severity|upper }}",
            body="""
Alert Notification

Severity: {{ severity }}
Message: {{ message }}

Timestamp: {{ timestamp }}
            """.strip(),
            html_body="""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2 style="color: #dc2626;">CrisisLens Alert</h2>
    <p><strong>Severity:</strong> <span style="color: #dc2626;">{{ severity|upper }}</span></p>
    <p><strong>Message:</strong> {{ message }}</p>
    <p style="color: #6b7280; font-size: 12px;">{{ timestamp }}</p>
</body>
</html>
            """.strip()
        )
        
        # New item template
        self.templates['new_item'] = NotificationTemplate(
            subject="New Crisis Item: {{ item.title }}",
            body="""
New Crisis Item Detected

Title: {{ item.title }}
Risk Score: {{ item.risk_score }}
Status: {{ item.status }}

View: {{ base_url }}/items/{{ item.id }}
            """.strip(),
            html_body="""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>New Crisis Item</h2>
    <h3>{{ item.title }}</h3>
    <p><strong>Risk Score:</strong> {{ item.risk_score }}</p>
    <p><strong>Status:</strong> {{ item.status }}</p>
    <a href="{{ base_url }}/items/{{ item.id }}" style="display: inline-block; padding: 10px 20px; background-color: #3b82f6; color: white; text-decoration: none; border-radius: 5px;">View Details</a>
</body>
</html>
            """.strip()
        )
        
        # Claim verification template
        self.templates['claim_verified'] = NotificationTemplate(
            subject="Claim Verification Complete: {{ claim.title }}",
            body="""
Claim Verification Complete

Claim: {{ claim.title }}
Verdict: {{ claim.verdict }}
Confidence: {{ claim.confidence }}%

View: {{ base_url }}/claims/{{ claim.id }}
            """.strip(),
            html_body="""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>Claim Verification Complete</h2>
    <h3>{{ claim.title }}</h3>
    <p><strong>Verdict:</strong> <span style="color: {% if claim.verdict == 'true' %}#10b981{% elif claim.verdict == 'false' %}#dc2626{% else %}#f59e0b{% endif %};">{{ claim.verdict|upper }}</span></p>
    <p><strong>Confidence:</strong> {{ claim.confidence }}%</p>
    <a href="{{ base_url }}/claims/{{ claim.id }}" style="display: inline-block; padding: 10px 20px; background-color: #3b82f6; color: white; text-decoration: none; border-radius: 5px;">View Details</a>
</body>
</html>
            """.strip()
        )
    
    async def send_notification(
        self,
        notification_data: Dict[str, Any]
    ) -> bool:
        """
        Send notification via specified channels.
        
        Args:
            notification_data: Notification configuration
                - type: Template type
                - channels: List of delivery channels
                - recipients: List of recipient identifiers
                - data: Template data
                - priority: Optional priority level
        
        Returns:
            True if sent successfully, False otherwise
        """
        notification_type = notification_data.get('type')
        channels = notification_data.get('channels', [NotificationChannel.EMAIL])
        recipients = notification_data.get('recipients', [])
        data = notification_data.get('data', {})
        priority = notification_data.get('priority', NotificationPriority.MEDIUM)
        
        if not recipients:
            logger.warning("No recipients specified for notification")
            return False
        
        # Get template
        template = self.templates.get(notification_type)
        if not template:
            logger.warning(f"Unknown notification type: {notification_type}")
            return False
        
        # Add timestamp and base URL
        data['timestamp'] = datetime.utcnow().isoformat()
        data['base_url'] = 'http://localhost:3000'  # TODO: Get from config
        
        # Send via each channel
        results = []
        for channel in channels:
            if channel == NotificationChannel.EMAIL:
                result = await self._send_email(recipients, template, data)
                results.append(result)
            
            elif channel == NotificationChannel.SMS:
                result = await self._send_sms(recipients, template, data)
                results.append(result)
            
            elif channel == NotificationChannel.PUSH:
                result = await self._send_push(recipients, template, data)
                results.append(result)
        
        return all(results)
    
    async def _send_email(
        self,
        recipients: List[str],
        template: NotificationTemplate,
        data: Dict[str, Any]
    ) -> bool:
        """
        Send email notification.
        
        Args:
            recipients: Email addresses
            template: Email template
            data: Template data
        
        Returns:
            True if sent successfully
        """
        try:
            # Render templates
            subject = Template(template.subject).render(**data)
            body = Template(template.body).render(**data)
            html_body = None
            if template.html_body:
                html_body = Template(template.html_body).render(**data)
            
            # TODO: Integrate with SendGrid or AWS SES
            # For now, just log
            logger.info(
                f"Sending email to {recipients}\n"
                f"Subject: {subject}\n"
                f"Body preview: {body[:100]}..."
            )
            
            # Simulated email sending
            # In production, use:
            # import sendgrid
            # from sendgrid.helpers.mail import Mail, Email, To, Content
            # sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
            # for recipient in recipients:
            #     message = Mail(
            #         from_email=Email("alerts@crisislens.ai"),
            #         to_emails=To(recipient),
            #         subject=subject,
            #         plain_text_content=Content("text/plain", body),
            #         html_content=Content("text/html", html_body) if html_body else None
            #     )
            #     response = sg.client.mail.send.post(request_body=message.get())
            
            return True
        
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    async def _send_sms(
        self,
        recipients: List[str],
        template: NotificationTemplate,
        data: Dict[str, Any]
    ) -> bool:
        """
        Send SMS notification.
        
        Args:
            recipients: Phone numbers
            template: SMS template
            data: Template data
        
        Returns:
            True if sent successfully
        """
        try:
            # Render template (use plain text body for SMS)
            body = Template(template.body).render(**data)
            
            # Truncate if too long (SMS limit ~160 chars)
            if len(body) > 160:
                body = body[:157] + "..."
            
            # TODO: Integrate with Twilio
            # For now, just log
            logger.info(
                f"Sending SMS to {recipients}\n"
                f"Body: {body}"
            )
            
            # Simulated SMS sending
            # In production, use:
            # from twilio.rest import Client
            # client = Client(account_sid, auth_token)
            # for recipient in recipients:
            #     message = client.messages.create(
            #         body=body,
            #         from_='+1234567890',
            #         to=recipient
            #     )
            
            return True
        
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    async def _send_push(
        self,
        recipients: List[str],
        template: NotificationTemplate,
        data: Dict[str, Any]
    ) -> bool:
        """
        Send push notification.
        
        Args:
            recipients: Device tokens
            template: Push template
            data: Template data
        
        Returns:
            True if sent successfully
        """
        try:
            # Render templates
            title = Template(template.subject).render(**data)
            body = Template(template.body).render(**data)
            
            # Truncate for push notifications
            if len(body) > 200:
                body = body[:197] + "..."
            
            # TODO: Integrate with Firebase Cloud Messaging
            # For now, just log
            logger.info(
                f"Sending push to {recipients}\n"
                f"Title: {title}\n"
                f"Body: {body}"
            )
            
            # Simulated push sending
            # In production, use:
            # import firebase_admin
            # from firebase_admin import messaging
            # firebase_admin.initialize_app()
            # for token in recipients:
            #     message = messaging.Message(
            #         notification=messaging.Notification(
            #             title=title,
            #             body=body
            #         ),
            #         token=token
            #     )
            #     response = messaging.send(message)
            
            return True
        
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            return False


# Singleton instance
_notification_service: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    """Get singleton notification service instance."""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service


# Convenience functions
async def send_alert_notification(alert_data: Dict[str, Any], recipients: List[str]):
    """Send alert notification to specified recipients."""
    service = get_notification_service()
    await service.send_notification({
        'type': 'alert',
        'channels': [NotificationChannel.EMAIL, NotificationChannel.PUSH],
        'recipients': recipients,
        'data': alert_data,
        'priority': NotificationPriority.HIGH
    })


async def send_item_notification(item_data: Dict[str, Any], recipients: List[str]):
    """Send new item notification to specified recipients."""
    service = get_notification_service()
    await service.send_notification({
        'type': 'new_item',
        'channels': [NotificationChannel.EMAIL],
        'recipients': recipients,
        'data': {'item': item_data},
        'priority': NotificationPriority.MEDIUM
    })


async def send_claim_notification(claim_data: Dict[str, Any], recipients: List[str]):
    """Send claim verification notification to specified recipients."""
    service = get_notification_service()
    await service.send_notification({
        'type': 'claim_verified',
        'channels': [NotificationChannel.EMAIL, NotificationChannel.PUSH],
        'recipients': recipients,
        'data': {'claim': claim_data},
        'priority': NotificationPriority.MEDIUM
    })
