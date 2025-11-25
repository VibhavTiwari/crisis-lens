#!/usr/bin/env python3
"""
Script to initialize Kafka topics from YAML configuration.
"""
import yaml
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_topics():
    """Create Kafka topics from YAML configuration."""
    # Load topics configuration
    with open('infrastructure/kafka/topics.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Connect to Kafka
    admin_client = KafkaAdminClient(
        bootstrap_servers=['localhost:29092'],
        client_id='topic-creator'
    )
    
    # Create topics
    topics = []
    for topic_config in config['topics']:
        topic = NewTopic(
            name=topic_config['name'],
            num_partitions=topic_config['partitions'],
            replication_factor=topic_config['replication_factor'],
            topic_configs=topic_config.get('config', {})
        )
        topics.append(topic)
        logger.info(f"Prepared topic: {topic_config['name']}")
    
    try:
        admin_client.create_topics(new_topics=topics, validate_only=False)
        logger.info(f"Successfully created {len(topics)} topics")
    except TopicAlreadyExistsError:
        logger.warning("Some topics already exist, skipping...")
    except Exception as e:
        logger.error(f"Error creating topics: {e}")
        raise
    finally:
        admin_client.close()

if __name__ == '__main__':
    create_topics()
