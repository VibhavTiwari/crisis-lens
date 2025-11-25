#!/usr/bin/env python3
"""
Consumer runner script.

Starts all Kafka consumers for processing events.
"""
import asyncio
import logging
import signal
import sys
from services.kafka_consumer import (
    create_main_consumer,
    create_notifications_consumer,
    create_activity_consumer
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_consumers():
    """Run all Kafka consumers concurrently."""
    logger.info("Starting CrisisLens Kafka Consumers...")
    
    # Create consumers
    main_consumer = create_main_consumer()
    notifications_consumer = create_notifications_consumer()
    activity_consumer = create_activity_consumer()
    
    # Setup graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Shutdown signal received, stopping consumers...")
        main_consumer.stop()
        notifications_consumer.stop()
        activity_consumer.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start all consumers concurrently
        await asyncio.gather(
            main_consumer.start(),
            notifications_consumer.start(),
            activity_consumer.start()
        )
    except Exception as e:
        logger.error(f"Error running consumers: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_consumers())
