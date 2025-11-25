"""
Unit tests for notification service.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from services.notification_service import NotificationService, send_alert_notification


@pytest.mark.unit
class TestNotificationService:
    """Test suite for notification service."""
    
    @pytest.fixture
    def service(self):
        """Create notification service instance."""
        return NotificationService()
    
    def test_service_initialization(self, service):
        """Test service initializes with templates."""
        assert service is not None
        assert 'alert' in service.templates
        assert 'new_item' in service.templates
        assert 'claim_verified' in service.templates
    
    @pytest.mark.asyncio
    async def test_send_email_notification(self, service):
        """Test email notification sending."""
        notification_data = {
            'type': 'alert',
            'channels': ['email'],
            'recipients': ['test@example.com'],
            'data': {
                'severity': 'high',
                'message': 'Test alert'
            }
        }
        
        with patch.object(service, '_send_email', return_value=True) as mock_email:
            result = await service.send_notification(notification_data)
            
            assert result is True
            mock_email.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_multi_channel_notification(self, service):
        """Test sending to multiple channels."""
        notification_data = {
            'type': 'alert',
            'channels': ['email', 'sms', 'push'],
            'recipients': ['test@example.com'],
            'data': {'severity': 'critical'}
        }
        
        with patch.object(service, '_send_email', return_value=True), \
             patch.object(service, '_send_sms', return_value=True), \
             patch.object(service, '_send_push', return_value=True):
            
            result = await service.send_notification(notification_data)
            assert result is True
    
    @pytest.mark.asyncio
    async def test_send_notification_missing_recipients(self, service):
        """Test handling of missing recipients."""
        notification_data = {
            'type': 'alert',
            'channels': ['email'],
            'recipients': [],
            'data': {}
        }
        
        result = await service.send_notification(notification_data)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_send_notification_invalid_template(self, service):
        """Test handling of invalid template type."""
        notification_data = {
            'type': 'nonexistent',
            'channels': ['email'],
            'recipients': ['test@example.com'],
            'data': {}
        }
        
        result = await service.send_notification(notification_data)
        assert result is False
    
    def test_template_rendering(self, service):
        """Test notification template rendering."""
        template = service.templates['alert']
        data = {
            'severity': 'high',
            'message': 'Test message',
            'timestamp': '2024-01-01T00:00:00Z'
        }
        
        from jinja2 import Template
        rendered = Template(template.body).render(**data)
        
        assert 'high' in rendered.lower()
        assert 'Test message' in rendered
    
    @pytest.mark.asyncio
    async def test_convenience_function(self):
        """Test send_alert_notification convenience function."""
        alert_data = {
            'severity': 'high',
            'message': 'Test alert'
        }
        recipients = ['test@example.com']
        
        with patch('services.notification_service.get_notification_service') as mock_get:
            mock_service = AsyncMock()
            mock_service.send_notification.return_value = True
            mock_get.return_value = mock_service
            
            await send_alert_notification(alert_data, recipients)
            
            assert mock_service.send_notification.called
