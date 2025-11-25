"""
Shared pytest fixtures and configuration.
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient
import redis
from unittest.mock import Mock, AsyncMock

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    
    # Create tables
    from models import Base
    Base.metadata.create_all(bind=db_engine)
    
    yield session
    
    session.rollback()
    session.close()
    
    # Drop tables
    Base.metadata.drop_all(bind=db_engine)


@pytest.fixture
def api_client():
    """Create FastAPI test client."""
    from apps.api.main import app
    return TestClient(app)


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    mock = Mock(spec=redis.Redis)
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = True
    return mock


@pytest.fixture
def mock_kafka_producer():
    """Mock Kafka producer."""
    mock = AsyncMock()
    mock.send.return_value = AsyncMock()
    mock.send.return_value.get.return_value = Mock(partition=0, offset=123)
    return mock


@pytest.fixture
def mock_kafka_consumer():
    """Mock Kafka consumer."""
    mock = Mock()
    mock.poll.return_value = {}
    mock.subscribe.return_value = None
    return mock


@pytest.fixture
def sample_crisis_item():
    """Sample crisis item for testing."""
    return {
        "id": "test-001",
        "title": "Test Crisis Event",
        "content": "This is a test crisis event for testing purposes.",
        "source": "test",
        "url": "https://test.example.com/crisis",
        "published_at": "2024-01-01T00:00:00Z",
        "risk_score": 0.75,
        "status": "pending_review",
        "location": "Test City, Test Country",
        "latitude": 35.6762,
        "longitude": 139.6503,
    }


@pytest.fixture
def sample_claim():
    """Sample claim for testing."""
    return {
        "id": "claim-001",
        "text": "Test claim statement",
        "item_id": "test-001",
        "verdict": None,
        "confidence": 0.0,
        "evidence": [],
    }


@pytest.fixture
def sample_user():
    """Sample user for testing."""
    return {
        "id": "user-001",
        "email": "test@example.com",
        "name": "Test User",
        "role": "analyst",
    }


@pytest.fixture
def auth_headers(sample_user):
    """Authentication headers for API requests."""
    # Simple token for testing
    token = "test-token-123"
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def async_mock_kafka():
    """Async mock for Kafka operations."""
    mock = AsyncMock()
    mock.send_event.return_value = True
    mock.send_batch.return_value = 10
    return mock


@pytest.fixture
def mock_opensearch():
    """Mock OpenSearch client."""
    mock = Mock()
    mock.index.return_value = {"result": "created"}
    mock.search.return_value = {
        "hits": {
            "total": {"value": 0},
            "hits": []
        }
    }
    mock.get.return_value = {"_source": {}}
    return mock


@pytest.fixture
def mock_notification_service():
    """Mock notification service."""
    mock = AsyncMock()
    mock.send_notification.return_value = True
    return mock
