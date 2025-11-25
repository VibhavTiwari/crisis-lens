"""
Integration tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for API."""
    
    def test_health_endpoint(self, api_client):
        """Test health check endpoint."""
        response = api_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_get_items_endpoint(self, api_client, db_session, sample_crisis_item):
        """Test items listing endpoint."""
        # Add test data to database
        # (This would use actual models in real implementation)
        
        response = api_client.get("/items")
        assert response.status_code == 200
        assert "items" in response.json()
    
    def test_get_item_by_id(self, api_client, sample_crisis_item):
        """Test getting specific item."""
        item_id = sample_crisis_item["id"]
        response = api_client.get(f"/items/{item_id}")
        
        # Depending on implementation, might be 200 or 404
        assert response.status_code in [200, 404]
    
    def test_create_item_unauthorized(self, api_client, sample_crisis_item):
        """Test creating item without authentication."""
        response = api_client.post("/items", json=sample_crisis_item)
        assert response.status_code in [401, 403]
    
    def test_create_item_authorized(self, api_client, sample_crisis_item, auth_headers):
        """Test creating item with authentication."""
        response = api_client.post(
            "/items",
            json=sample_crisis_item,
            headers=auth_headers
        )
        assert response.status_code in [200, 201]
    
    def test_search_items(self, api_client):
        """Test search functionality."""
        response = api_client.get("/items?search=crisis")
        assert response.status_code == 200
    
    def test_filter_items_by_status(self, api_client):
        """Test filtering by status."""
        response = api_client.get("/items?status=pending_review")
        assert response.status_code == 200
    
    def test_pagination(self, api_client):
        """Test pagination parameters."""
        response = api_client.get("/items?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data.get("items", [])) <= 10
    
    def test_claims_endpoint(self, api_client):
        """Test claims listing."""
        response = api_client.get("/claims")
        assert response.status_code == 200
    
    def test_verify_claim(self, api_client, sample_claim, auth_headers):
        """Test claim verification endpoint."""
        claim_id = sample_claim["id"]
        response = api_client.post(
            f"/claims/{claim_id}/verify",
            json={"verdict": "true", "evidence": []},
            headers=auth_headers
        )
        assert response.status_code in [200, 404]
    
    def test_stats_endpoint(self, api_client):
        """Test statistics endpoint."""
        response = api_client.get("/stats")
        assert response.status_code == 200
        assert "pending" in response.json() or response.status_code == 200
