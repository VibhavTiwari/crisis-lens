"""
Database initialization script
Run this to set up all databases with required schemas
"""
import asyncio
from services.opensearch_service import opensearch_service
from services.qdrant_service import qdrant_service
from services.clickhouse_service import clickhouse_service
from services.iceberg_service import iceberg_service
from services.observability import observability_service
from models.base import Base, engine

async def init_databases():
    """Initialize all databases"""
    print("=" * 60)
    print("CRISISLEN DATABASE INITIALIZATION")
    print("=" * 60)
    
    # 1. PostgreSQL tables
    print("\n1. Creating PostgreSQL tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("   ✓ PostgreSQL tables created")
    except Exception as e:
        print(f"   ✗ PostgreSQL failed: {e}")
    
    # 2. OpenSearch indexes
    print("\n2. Creating OpenSearch indexes...")
    try:
        await opensearch_service.ensure_indexes()
        print("   ✓ OpenSearch indexes created")
    except Exception as e:
        print(f"   ✗ OpenSearch failed: {e}")
    
    # 3. Qdrant collections
    print("\n3. Creating Qdrant collections...")
    try:
        await qdrant_service.ensure_collections()
        print("   ✓ Qdrant collections created")
    except Exception as e:
        print(f"   ✗ Qdrant failed: {e}")
    
    # 4. ClickHouse tables
    print("\n4. Creating ClickHouse tables...")
    try:
        await clickhouse_service.ensure_tables()
        print("   ✓ ClickHouse tables created")
    except Exception as e:
        print(f"   ✗ ClickHouse failed: {e}")
    
    # 5. Iceberg tables (optional)
    print("\n5. Creating Iceberg tables...")
    try:
        if iceberg_service:
            await iceberg_service.ensure_tables()
            print("   ✓ Iceberg tables created")
        else:
            print("   ⚠ Iceberg not available (optional)")
    except Exception as e:
        print(f"   ⚠ Iceberg failed (optional): {e}")
    
    print("\n" + "=" * 60)
    print("DATABASE INITIALIZATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(init_databases())
