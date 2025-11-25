"""
Notification Schemas for CrisisLens.

Pydantic models for notification data structures.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


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


class NotificationStatus(str, Enum):
    """Notification delivery status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class NotificationBase(BaseModel):
    """Base notification schema."""
    type: str = Field(..., description="Notification type/template")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Additional data")
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM)
    channels: List[NotificationChannel] = Field(default=[NotificationChannel.EMAIL])


class NotificationCreate(NotificationBase):
    """Schema for creating a notification."""
    recipients: List[str] = Field(..., description="List of recipient identifiers")


class NotificationResponse(NotificationBase):
    """Schema for notification response."""
    id: str
    recipients: List[str]
    status: NotificationStatus
    created_at: datetime
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True


class UserNotificationPreferences(BaseModel):
    """User notification preferences."""
    email_enabled: bool = Field(default=True, description="Enable email notifications")
    sms_enabled: bool = Field(default=False, description="Enable SMS notifications")
    push_enabled: bool = Field(default=True, description="Enable push notifications")
    
    # Notification types
    notify_new_items: bool = Field(default=True, description="Notify on new items")
    notify_high_risk: bool = Field(default=True, description="Notify on high-risk items")
    notify_claims: bool = Field(default=True, description="Notify on claim verifications")
    notify_alerts: bool = Field(default=True, description="Notify on system alerts")
    notify_mentions: bool = Field(default=True, description="Notify when mentioned")
    
    # Delivery preferences
    digest_mode: bool = Field(default=False, description="Send digest instead of individual notifications")
    digest_frequency: str = Field(default="daily", description="Digest frequency: hourly, daily, weekly")
    quiet_hours_start: Optional[int] = Field(default=None, description="Quiet hours start (0-23)")
    quiet_hours_end: Optional[int] = Field(default=None, description="Quiet hours end (0-23)")

    class Config:
        from_attributes = True
