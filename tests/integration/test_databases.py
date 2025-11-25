"""
Integration tests for database services
Run with: pytest tests/integration/test_databases.py
"""
import pytest
import asyncio
from services.opensearch_service import opensearch_service
from services.qdrant_service import qdrant_service
from services.neo4j_service import neo4j_service
from services.clickhouse_service import clickhouse_service
from services.redis_service import redis_service
from datetime import datetime

@pytest.mark.asyncio
async def test_opensearch_indexing():
    """Test OpenSearch indexing and search"""
    await opensearch_service.ensure_indexes()
    
    # Index a test item
    test_item = {
        "id": "test_item_1",
        "source": "test",
        "source_id": "1",
        "url": "http://test.com",
        "title": "Test Crisis Item",
        "text": "This is a test crisis event for searching",
        "timestamp": datetime.utcnow(),
        "risk_score": 0.8,
        "ingested_at": datetime.utcnow()
    }
    
    await opensearch_service.index_item(test_item)
    
    # Search for it
    await asyncio.sleep(1)  # Wait for indexing
    results = await opensearch_service.search_items("crisis event")
    
    assert len(results) > 0
    assert results[0]["id"] == "test_item_1"

@pytest.mark.asyncio
async def test_qdrant_similarity_search():
    """Test Qdrant vector similarity search"""
    await qdrant_service.ensure_collections()
    
    # Add a test embedding
    test_embedding = [0.1] * 384  # Mock embedding
    await qdrant_service.add_claim_embedding(
        claim_id="claim_1",
        embedding=test_embedding,
        metadata={"text": "Test claim"}
    )
    
    # Search for similar
    await asyncio.sleep(0.5)
    results = await qdrant_service.search_similar_claims(
        query_embedding=test_embedding,
        limit=5
    )
    
    assert len(results) > 0

@pytest.mark.asyncio
async def test_neo4j_graph_operations():
    """Test Neo4j entity and relationship creation"""
    # Create entities
    await neo4j_service.create_entity("Person", {"name": "John Doe", "role": "witness"})
    await neo4j_service.create_entity("Person", {"name": "Jane Smith", "role": "victim"})
    
    # Create relationship
    await neo4j_service.create_relationship(
        from_entity={"name": "John Doe"},
        to_entity={"name": "Jane Smith"},
        relationship_type="KNOWS"
    )
    
    # Find connected entities
    connected = await neo4j_service.find_connected_entities("John Doe")
    assert len(connected) > 0

@pytest.mark.asyncio
async def test_clickhouse_analytics():
    """Test ClickHouse event recording and queries"""
    await clickhouse_service.ensure_tables()
    
    # Record some events
    for i in range(5):
        await clickhouse_service.record_event(
            event_type="item_ingested",
            item_id=f"item_{i}",
            source="test",
            risk_score=0.5 + (i * 0.1)
        )
    
    # Query events
    from datetime import datetime, timedelta
    timeline = await clickhouse_service.get_event_timeline(
        start_time=datetime.utcnow() - timedelta(hours=1),
        end_time=datetime.utcnow()
    )
    
    assert len(timeline) > 0

@pytest.mark.asyncio
async def test_redis_caching():
    """Test Redis caching operations"""
    await redis_service.connect()
    
    # Test set/get
    await redis_service.set("test_key", {"data": "test_value"}, ttl=60)
    value = await redis_service.get("test_key")
    
    assert value["data"] == "test_value"
    
    # Test rate limiting
    is_allowed = await redis_service.check_rate_limit(
        key="test_user",
        max_requests=5,
        window_seconds=60
    )
    
    assert is_allowed == True
    
    await redis_service.disconnect()

@pytest.mark.asyncio
async def test_database_integration_flow():
    """Test complete flow across databases"""
    # 1. Index item in OpenSearch
    item = {
        "id": "flow_test_1",
        "source": "test",
        "source_id": "1",
        "url": "http://test.com",
        "title": "Integration Test Item",
        "text": "Testing full database integration",
        "timestamp": datetime.utcnow(),
        "risk_score": 0.9,
        "ingested_at": datetime.utcnow()
    }
    await opensearch_service.index_item(item)
    
    # 2. Record event in ClickHouse
    await clickhouse_service.record_event(
        event_type="item_verified",
        item_id="flow_test_1",
        source="test",
        risk_score=0.9
    )
    
    # 3. Cache in Redis
    await redis_service.connect()
    await redis_service.set(f"item:{item['id']}", item, ttl=300)
    
    # 4. Create entity in Neo4j
    await neo4j_service.create_entity("Crisis", {"name": "Mumbai Floods 2025"})
    
    # Verify all operations succeeded
    cached = await redis_service.get(f"item:{item['id']}")
    assert cached["id"] == "flow_test_1"
    
    await redis_service.disconnect()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
