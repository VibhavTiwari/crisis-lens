"""
Unit tests for Kafka producer service.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from services.kafka_producer import CrisisKafkaProducer, publish_raw_item


@pytest.mark.unit
class TestKafkaProducer:
    """Test suite for Kafka producer."""
    
    @pytest.fixture
    def producer(self):
        """Create Kafka producer instance."""
        return CrisisKafkaProducer(bootstrap_servers=['localhost:9092'])
    
    def test_producer_initialization(self, producer):
        """Test producer initializes correctly."""
        assert producer is not None
        assert producer.bootstrap_servers == ['localhost:9092']
    
    @pytest.mark.asyncio
    async def test_send_event_success(self, producer):
        """Test successful event sending."""
        test_event = {
            "id": "test-001",
            "title": "Test Event",
            "content": "Test content"
        }
        
        with patch.object(producer, '_get_producer') as mock_get_producer:
            mock_kafka_producer = Mock()
            mock_future = Mock()
            mock_future.get.return_value = Mock(partition=0, offset=123)
            mock_kafka_producer.send.return_value = mock_future
            mock_get_producer.return_value = mock_kafka_producer
            
            result = await producer.send_event('test-topic', test_event)
            
            assert result is True
            mock_kafka_producer.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_event_with_key(self, producer):
        """Test sending event with partition key."""
        test_event = {"id": "test-001"}
        test_key = "test-key"
        
        with patch.object(producer, '_get_producer') as mock_get_producer:
            mock_kafka_producer = Mock()
            mock_future = Mock()
            mock_future.get.return_value = Mock(partition=0, offset=123)
            mock_kafka_producer.send.return_value = mock_future
            mock_get_producer.return_value = mock_kafka_producer
            
            await producer.send_event('test-topic', test_event, key=test_key)
            
            call_args = mock_kafka_producer.send.call_args
            assert call_args[1]['key'] == test_key
    
    @pytest.mark.asyncio
    async def test_send_event_failure(self, producer):
        """Test handling of send failures."""
        with patch.object(producer, '_get_producer') as mock_get_producer:
            mock_kafka_producer = Mock()
            mock_kafka_producer.send.side_effect = Exception("Send failed")
            mock_get_producer.return_value = mock_kafka_producer
            
            result = await producer.send_event('test-topic', {})
            assert result is False
    
    @pytest.mark.asyncio
    async def test_send_batch(self, producer):
        """Test batch sending."""
        messages = [
            {"id": "1"},
            {"id": "2"},
            {"id": "3"}
        ]
        
        with patch.object(producer, 'send_event', return_value=True) as mock_send:
            count = await producer.send_batch('test-topic', messages)
            
            assert count == 3
            assert mock_send.call_count == 3
    
    @pytest.mark.asyncio
    async def test_publish_raw_item_convenience_function(self, mock_kafka_producer):
        """Test convenience function for publishing raw items."""
        item_data = {
            "id": "test-001",
            "title": "Test Item"
        }
        
        with patch('services.kafka_producer.get_kafka_producer', return_value=mock_kafka_producer):
            result = await publish_raw_item(item_data)
            
            assert mock_kafka_producer.send_event.called
            call_args = mock_kafka_producer.send_event.call_args
            assert call_args[0][0] == 'raw-items'
            assert call_args[0][1] == item_data
