"""
Load testing scenarios using Locust.
"""
from locust import HttpUser, task, between
import random


class CrisisLensUser(HttpUser):
    """Simulated user for load testing."""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login on start."""
        # Simulate authentication
        self.token = "test-token-123"
        self.client.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def view_items(self):
        """View items list - most common action."""
        self.client.get("/items?limit=20")
    
    @task(2)
    def search_items(self):
        """Search for items."""
        queries = ["crisis", "earthquake", "flood", "fire", "emergency"]
        query = random.choice(queries)
        self.client.get(f"/items?search={query}")
    
    @task(1)
    def view_item_detail(self):
        """View specific item details."""
        item_id = f"test-{random.randint(1, 100)}"
        self.client.get(f"/items/{item_id}")
    
    @task(1)
    def view_claims(self):
        """View claims list."""
        self.client.get("/claims")
    
    @task(1)
    def get_stats(self):
        """Get statistics."""
        self.client.get("/stats")


class WebSocketUser(HttpUser):
    """WebSocket load testing."""
    
    wait_time = between(2, 5)
    
    @task
    def connect_websocket(self):
        """Test WebSocket connection load."""
        # Note: Locust doesn't directly support WebSocket
        # This would need websocket-client library
        pass


class AdminUser(HttpUser):
    """Admin user scenarios."""
    
    wait_time = between(3, 6)
    
    def on_start(self):
        """Admin login."""
        self.client.headers = {"Authorization": "Bearer admin-token"}
    
    @task(2)
    def review_pending_items(self):
        """Review pending items."""
        self.client.get("/items?status=pending_review")
    
    @task(1)
    def verify_claim(self):
        """Verify a claim."""
        claim_id = f"claim-{random.randint(1, 50)}"
        self.client.post(
            f"/claims/{claim_id}/verify",
            json={"verdict": "true", "evidence": []}
        )
    
    @task(1)
    def update_item_status(self):
        """Update item status."""
        item_id = f"test-{random.randint(1, 100)}"
        self.client.patch(
            f"/items/{item_id}",
            json={"status": "verified"}
        )


# Run with: locust -f locustfile.py --host=http://localhost:8000
# Web UI: http://localhost:8089
