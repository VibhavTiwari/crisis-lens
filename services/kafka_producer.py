"""
Kafka Producer Service for CrisisLens.

Handles publishing events to Kafka topics with error handling and retry logic.
"""
from typing import Any, Dict, Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import logging
from datetime import datetime
import asyncio
from functools import lru_cache

logger = logging.getLogger(__name__)


class CrisisKafkaProducer:
    """Kafka producer with connection pooling and error handling."""
    
    def __init__(
        self,
        bootstrap_servers: list[str] = None,
        client_id: str = "crisis-lens-producer"
    ):
        """
        Initialize Kafka producer.
        
        Args:
            bootstrap_servers: List of Kafka broker addresses
            client_id: Client identifier for this producer
        """
        self.bootstrap_servers = bootstrap_servers or ['localhost:29092']
        self.client_id = client_id
        self._producer: Optional[KafkaProducer] = None
        
    def _get_producer(self) -> KafkaProducer:
        """Get or create Kafka producer instance."""
        if self._producer is None:
            self._producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=self.client_id,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Wait for all replicas
                retries=3,
                max_in_flight_requests_per_connection=5,
                compression_type='lz4',
                linger_ms=10,  # Batch messages for 10ms
                batch_size=16384,  # 16KB batch size
            )
            logger.info(f"Kafka producer initialized: {self.bootstrap_servers}")
        return self._producer
    
    async def send_event(
        self,
        topic: str,
        value: Dict[str, Any],
        key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Send an event to Kafka topic asynchronously.
        
        Args:
            topic: Kafka topic name
            value: Event data (will be JSON serialized)
            key: Optional partition key
            headers: Optional message headers
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add metadata
            enriched_value = {
                **value,
                '_timestamp': datetime.utcnow().isoformat(),
                '_producer': self.client_id
            }
            
            # Prepare headers
            kafka_headers = []
            if headers:
                kafka_headers = [(k, v.encode('utf-8')) for k, v in headers.items()]
            
            # Send message
            producer = self._get_producer()
            future = producer.send(
                topic,
                value=enriched_value,
                key=key,
                headers=kafka_headers
            )
            
            # Wait for send to complete
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"Message sent to {topic} "
                f"[partition: {record_metadata.partition}, "
                f"offset: {record_metadata.offset}]"
            )
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error sending to {topic}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending to {topic}: {e}")
            return False
    
    def send_event_sync(
        self,
        topic: str,
        value: Dict[str, Any],
        key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Send an event to Kafka topic synchronously.
        
        Args:
            topic: Kafka topic name
            value: Event data (will be JSON serialized)
            key: Optional partition key
            headers: Optional message headers
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add metadata
            enriched_value = {
                **value,
                '_timestamp': datetime.utcnow().isoformat(),
                '_producer': self.client_id
            }
            
            # Prepare headers
            kafka_headers = []
            if headers:
                kafka_headers = [(k, v.encode('utf-8')) for k, v in headers.items()]
            
            # Send message
            producer = self._get_producer()
            future = producer.send(
                topic,
                value=enriched_value,
                key=key,
                headers=kafka_headers
            )
            
            # Wait for send to complete
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"Message sent to {topic} "
                f"[partition: {record_metadata.partition}, "
                f"offset: {record_metadata.offset}]"
            )
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error sending to {topic}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending to {topic}: {e}")
            return False
    
    async def send_batch(
        self,
        topic: str,
        messages: list[Dict[str, Any]]
    ) -> int:
        """
        Send multiple messages to a topic.
        
        Args:
            topic: Kafka topic name
            messages: List of message dictionaries
            
        Returns:
            Number of successfully sent messages
        """
        success_count = 0
        for msg in messages:
            if await self.send_event(topic, msg):
                success_count += 1
        return success_count
    
    def flush(self, timeout: Optional[float] = None):
        """Flush pending messages."""
        if self._producer:
            self._producer.flush(timeout=timeout)
    
    def close(self):
        """Close the producer and release resources."""
        if self._producer:
            self._producer.close()
            self._producer = None
            logger.info("Kafka producer closed")


# Singleton instance
@lru_cache(maxsize=1)
def get_kafka_producer() -> CrisisKafkaProducer:
    """Get singleton Kafka producer instance."""
    return CrisisKafkaProducer()


# Convenience functions for common topics
async def publish_raw_item(item_data: Dict[str, Any]) -> bool:
    """Publish a raw item to the raw-items topic."""
    producer = get_kafka_producer()
    return await producer.send_event('raw-items', item_data, key=item_data.get('id'))


async def publish_normalized_item(item_data: Dict[str, Any]) -> bool:
    """Publish a normalized item to the normalized-items topic."""
    producer = get_kafka_producer()
    return await producer.send_event('normalized-items', item_data, key=item_data.get('id'))


async def publish_claim(claim_data: Dict[str, Any]) -> bool:
    """Publish a claim to the claims topic."""
    producer = get_kafka_producer()
    return await producer.send_event('claims', claim_data, key=claim_data.get('id'))


async def publish_alert(alert_data: Dict[str, Any]) -> bool:
    """Publish an alert to the alerts topic."""
    producer = get_kafka_producer()
    return await producer.send_event('alerts', alert_data, key=alert_data.get('id'))


async def publish_notification(notification_data: Dict[str, Any]) -> bool:
    """Publish a notification event."""
    producer = get_kafka_producer()
    return await producer.send_event('notifications', notification_data)


async def publish_user_activity(activity_data: Dict[str, Any]) -> bool:
    """Publish user activity event."""
    producer = get_kafka_producer()
    return await producer.send_event('user-activity', activity_data)
