from locust import HttpUser, task, between

class CrisisLensUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def get_items(self):
        """Simulate fetching items from the API"""
        self.client.get("/api/items")
    
    @task(1)
    def get_single_item(self):
        """Simulate fetching a specific item"""
        self.client.get("/api/items/item1")
    
    @task(1)
    def verify_item(self):
        """Simulate verification action"""
        self.client.post("/api/items/item1/verify?status=verified_true")
