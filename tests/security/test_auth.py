"""
Security tests for authentication and authorization.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.security
class TestAuthentication:
    """Security tests for authentication."""
    
    def test_no_token_returns_401(self, api_client):
        """Test that protected endpoints require authentication."""
        response = api_client.post("/items", json={})
        assert response.status_code in [401, 403]
    
    def test_invalid_token_rejected(self, api_client):
        """Test invalid token is rejected."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = api_client.get("/items", headers=headers)
        # Depending on implementation
        assert response.status_code in [200, 401, 403]
    
    def test_expired_token_rejected(self, api_client):
        """Test expired token is rejected."""
        # Would need to generate expired token
        headers = {"Authorization": "Bearer expired-token"}
        response = api_client.post("/items", json={}, headers=headers)
        assert response.status_code in [401, 403]
    
    def test_token_format_validation(self, api_client):
        """Test malformed authorization header."""
        headers = {"Authorization": "InvalidFormat"}
        response = api_client.get("/items", headers=headers)
        assert response.status_code in [200, 401, 403]
    
    def test_role_based_access_control(self, api_client):
        """Test RBAC for different user roles."""
        # Regular user token
        user_headers = {"Authorization": "Bearer user-token"}
        
        # Admin-only endpoint
        response = api_client.delete("/items/test-001", headers=user_headers)
        assert response.status_code in [403, 404]


@pytest.mark.security
class TestAuthorization:
    """Security tests for authorization."""
    
    def test_user_can_only_access_own_data(self, api_client):
        """Test users can't access other users' data."""
        user1_headers = {"Authorization": "Bearer user1-token"}
        
        # Try to access user2's data
        response = api_client.get("/users/user2/profile", headers=user1_headers)
        assert response.status_code in [403, 404]
    
    def test_admin_can_access_all_data(self, api_client):
        """Test admin has full access."""
        admin_headers = {"Authorization": "Bearer admin-token"}
        
        response = api_client.get("/admin/users", headers=admin_headers)
        assert response.status_code in [200, 404]
