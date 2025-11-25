"""
Test authentication and authorization
Run with: pytest tests/integration/test_auth.py
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apps.api.main import app
from models.base import Base, get_db
from models.user import User, Role
from apps.api.auth.jwt import get_password_hash

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Setup and teardown
@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(client):
    """Create a test user"""
    db = TestingSessionLocal()
    
    # Create role
    role = Role(name="verifier", description="Test role")
    db.add(role)
    db.commit()
    
    # Create user
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        is_active=True
    )
    user.roles.append(role)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    db.close()
    
    return user

def test_register(client):
    """Test user registration"""
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword123",
            "full_name": "New User"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "id" in data

def test_register_duplicate(client, test_user):
    """Test registering with existing email"""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",  # Same as test_user
            "username": "different",
            "password": "password123"
        }
    )
    
    assert response.status_code == 400

def test_login(client, test_user):
    """Test login"""
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    """Test login with wrong password"""
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401

def test_get_current_user(client, test_user):
    """Test getting current user info"""
    # Login first
    login_response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"

def test_get_current_user_no_token(client):
    """Test getting current user without token"""
    response = client.get("/auth/me")
    
    assert response.status_code == 403  # Forbidden (no credentials)

def test_refresh_token(client, test_user):
    """Test token refresh"""
    # Login first
    login_response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    
    refresh_token = login_response.json()["refresh_token"]
    
    # Refresh
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_create_api_key(client, test_user):
    """Test API key creation"""
    # Login first
    login_response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Create API key
    response = client.post(
        "/auth/api-keys",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test API Key",
            "expires_in_days": 90
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test API Key"
    assert "key" in data  # Plaintext key returned only once
    assert "id" in data

def test_list_api_keys(client, test_user):
    """Test listing API keys"""
    # Login and create a key
    login_response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Create API key
    client.post(
        "/auth/api-keys",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Test Key"}
    )
    
    # List keys
    response = client.get(
        "/auth/api-keys",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Test Key"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
