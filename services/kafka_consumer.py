"""
Kafka Consumer Service for CrisisLens.

Consumes events from Kafka topics and triggers appropriate workflows.
"""
from typing import Callable, Dict, Any, Optional
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
import logging
import asyncio
from datetime import datetime
import signal
import sys

logger = logging.getLogger(__name__)


class CrisisKafkaConsumer:
    """Kafka consumer with event processing and error handling."""
    
    def __init__(
        self,
        topics: list[str],
        group_id: str,
        bootstrap_servers: list[str] = None,
        auto_offset_reset: str = 'earliest',
        enable_auto_commit: bool = True
    ):
        """
        Initialize Kafka consumer.
        
        Args:
            topics: List of topics to subscribe to
            group_id: Consumer group identifier
            bootstrap_servers: List of Kafka broker addresses
            auto_offset_reset: Where to start reading ('earliest' or 'latest')
            enable_auto_commit: Whether to auto-commit offsets
        """
        self.topics = topics
        self.group_id = group_id
        self.bootstrap_servers = bootstrap_servers or ['localhost:29092']
        self.auto_offset_reset = auto_offset_reset
        self.enable_auto_commit = enable_auto_commit
        self._consumer: Optional[KafkaConsumer] = None
        self._running = False
        self._handlers: Dict[str, Callable] = {}
        
    def _get_consumer(self) -> KafkaConsumer:
        """Get or create Kafka consumer instance."""
        if self._consumer is None:
            self._consumer = KafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset=self.auto_offset_reset,
                enable_auto_commit=self.enable_auto_commit,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                max_poll_records=100,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000
            )
            logger.info(
                f"Kafka consumer initialized: group={self.group_id}, "
                f"topics={self.topics}"
            )
        return self._consumer
    
    def register_handler(self, topic: str, handler: Callable[[Dict[str, Any]], None]):
        """
        Register a handler function for a specific topic.
        
        Args:
            topic: Topic name
            handler: Async function to handle messages from this topic
        """
        self._handlers[topic] = handler
        logger.info(f"Registered handler for topic: {topic}")
    
    async def start(self):
        """Start consuming messages."""
        self._running = True
        consumer = self._get_consumer()
        
        # Setup graceful shutdown
        def signal_handler(sig, frame):
            logger.info("Received shutdown signal")
            self._running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("Starting Kafka consumer loop...")
        
        try:
            while self._running:
                # Poll for messages
                messages = consumer.poll(timeout_ms=1000, max_records=100)
                
                for topic_partition, records in messages.items():
                    topic = topic_partition.topic
                    handler = self._handlers.get(topic)
                    
                    if not handler:
                        logger.warning(f"No handler registered for topic: {topic}")
                        continue
                    
                    for record in records:
                        try:
                            # Process message
                            await self._process_message(
                                topic=topic,
                                message=record.value,
                                key=record.key,
                                offset=record.offset,
                                partition=record.partition,
                                handler=handler
                            )
                        except Exception as e:
                            logger.error(
                                f"Error processing message from {topic}: {e}",
                                exc_info=True
                            )
                            # Send to DLQ
                            await self._send_to_dlq(topic, record, e)
                
                # Allow other tasks to run
                await asyncio.sleep(0.01)
        
        finally:
            consumer.close()
            logger.info("Kafka consumer closed")
    
    async def _process_message(
        self,
        topic: str,
        message: Dict[str, Any],
        key: Optional[str],
        offset: int,
        partition: int,
        handler: Callable
    ):
        """
        Process a single message.
        
        Args:
            topic: Topic name
            message: Message data
            key: Message key
            offset: Message offset
            partition: Partition number
            handler: Handler function
        """
        logger.debug(
            f"Processing message from {topic} "
            f"[partition: {partition}, offset: {offset}]"
        )
        
        # Call handler
        if asyncio.iscoroutinefunction(handler):
            await handler(message)
        else:
            handler(message)
    
    async def _send_to_dlq(self, topic: str, record: Any, error: Exception):
        """
        Send failed message to dead letter queue.
        
        Args:
            topic: Original topic
            record: Failed message record
            error: Exception that occurred
        """
        try:
            from services.kafka_producer import get_kafka_producer
            
            dlq_message = {
                'original_topic': topic,
                'original_key': record.key,
                'original_value': record.value,
                'original_partition': record.partition,
                'original_offset': record.offset,
                'error': str(error),
                'error_type': type(error).__name__,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            producer = get_kafka_producer()
            await producer.send_event('dlq', dlq_message)
            
            logger.info(f"Sent failed message to DLQ: {topic}")
        except Exception as e:
            logger.error(f"Failed to send to DLQ: {e}")
    
    def stop(self):
        """Stop consuming messages."""
        self._running = False


# Message handlers for different topics
async def handle_raw_item(message: Dict[str, Any]):
    """Handle raw item messages."""
    from workflows.orchestrator import trigger_item_processing
    
    logger.info(f"Processing raw item: {message.get('id')}")
    
    try:
        # Trigger item processing workflow
        await trigger_item_processing(message)
        
        # Publish to normalized-items topic after processing
        from services.kafka_producer import publish_normalized_item
        await publish_normalized_item(message)
        
    except Exception as e:
        logger.error(f"Error processing raw item: {e}")
        raise


async def handle_normalized_item(message: Dict[str, Any]):
    """Handle normalized item messages."""
    from services.opensearch_service import index_item
    
    logger.info(f"Indexing normalized item: {message.get('id')}")
    
    try:
        # Update OpenSearch index
        await index_item(message)
        
        # Check for alerts
        if message.get('risk_score', 0) > 0.8:
            from services.kafka_producer import publish_alert
            alert_data = {
                'item_id': message.get('id'),
                'type': 'high_risk',
                'severity': 'critical',
                'message': f"High risk item detected: {message.get('title')}",
                'data': message
            }
            await publish_alert(alert_data)
    
    except Exception as e:
        logger.error(f"Error handling normalized item: {e}")
        raise


async def handle_claim(message: Dict[str, Any]):
    """Handle claim messages."""
    from workflows.claim_verification import start_verification
    
    logger.info(f"Processing claim: {message.get('id')}")
    
    try:
        # Start claim verification workflow
        await start_verification(message)
    except Exception as e:
        logger.error(f"Error processing claim: {e}")
        raise


async def handle_alert(message: Dict[str, Any]):
    """Handle alert messages."""
    from services.kafka_producer import publish_notification
    
    logger.info(f"Processing alert: {message.get('type')}")
    
    try:
        # Create notification from alert
        notification_data = {
            'type': 'alert',
            'severity': message.get('severity', 'medium'),
            'title': message.get('message'),
            'data': message.get('data'),
            'channels': ['email', 'push']  # Send via multiple channels
        }
        await publish_notification(notification_data)
    
    except Exception as e:
        logger.error(f"Error processing alert: {e}")
        raise


async def handle_notification(message: Dict[str, Any]):
    """Handle notification messages."""
    from services.notification_service import send_notification
    
    logger.info(f"Sending notification: {message.get('type')}")
    
    try:
        await send_notification(message)
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        raise


async def handle_user_activity(message: Dict[str, Any]):
    """Handle user activity messages."""
    from apps.api.collaboration import broadcast_activity
    
    logger.info(f"Broadcasting user activity: {message.get('action')}")
    
    try:
        # Broadcast to WebSocket clients
        await broadcast_activity(message)
    except Exception as e:
        logger.error(f"Error broadcasting activity: {e}")
        raise


# Consumer groups
def create_main_consumer() -> CrisisKafkaConsumer:
    """Create main consumer for item processing."""
    consumer = CrisisKafkaConsumer(
        topics=['raw-items', 'normalized-items', 'claims'],
        group_id='crisis-lens-main'
    )
    
    consumer.register_handler('raw-items', handle_raw_item)
    consumer.register_handler('normalized-items', handle_normalized_item)
    consumer.register_handler('claims', handle_claim)
    
    return consumer


def create_notifications_consumer() -> CrisisKafkaConsumer:
    """Create consumer for notifications and alerts."""
    consumer = CrisisKafkaConsumer(
        topics=['alerts', 'notifications'],
        group_id='crisis-lens-notifications'
    )
    
    consumer.register_handler('alerts', handle_alert)
    consumer.register_handler('notifications', handle_notification)
    
    return consumer


def create_activity_consumer() -> CrisisKafkaConsumer:
    """Create consumer for user activity."""
    consumer = CrisisKafkaConsumer(
        topics=['user-activity'],
        group_id='crisis-lens-activity'
    )
    
    consumer.register_handler('user-activity', handle_user_activity)
    
    return consumer
