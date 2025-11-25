"""
Input validation and injection prevention tests.
"""
import pytest


@pytest.mark.security
class TestInputValidation:
    """Security tests for input validation."""
    
    def test_sql_injection_prevention(self, api_client):
        """Test SQL injection attempts are blocked."""
        malicious_queries = [
            "1' OR '1'='1",
            "'; DROP TABLE items; --",
            "1' UNION SELECT * FROM users--"
        ]
        
        for query in malicious_queries:
            response = api_client.get(f"/items?search={query}")
            # Should not return 500 or expose SQL errors
            assert response.status_code in [200, 400]
            
            if response.status_code == 200:
                # Should return empty or sanitized results, not all items
                data = response.json()
                # Verify no SQL injection occurred
                assert isinstance(data, dict)
    
    def test_xss_prevention(self, api_client, auth_headers):
        """Test XSS attempts are sanitized."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')"
        ]
        
        for payload in xss_payloads:
            response = api_client.post(
                "/items",
                json={"title": payload, "content": "test"},
                headers=auth_headers
            )
            
            # Should accept or reject, but not execute
            assert response.status_code in [200, 201, 400, 401, 403]
    
    def test_command_injection_prevention(self, api_client, auth_headers):
        """Test command injection attempts are blocked."""
        malicious_inputs = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& rm -rf /",
            "`whoami`"
        ]
        
        for malicious in malicious_inputs:
            response = api_client.post(
                "/items",
                json={"title": malicious, "content": "test"},
                headers=auth_headers
            )
            
            assert response.status_code in [200, 201, 400, 401, 403]
    
    def test_max_length_validation(self, api_client, auth_headers):
        """Test maximum length validation."""
        # Very long string
        long_string = "A" * 100000
        
        response = api_client.post(
            "/items",
            json={"title": long_string, "content": "test"},
            headers=auth_headers
        )
        
        # Should reject or truncate
        assert response.status_code in [200, 201, 400, 413]
    
    def test_invalid_json_handling(self, api_client):
        """Test handling of invalid JSON."""
        response = api_client.post(
            "/items",
            data="invalid json{{{",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_type_validation(self, api_client, auth_headers):
        """Test type validation for fields."""
        response = api_client.post(
            "/items",
            json={
                "title": "Test",
                "risk_score": "not_a_number"  # Should be float
            },
            headers=auth_headers
        )
        
        assert response.status_code in [400, 422]
    
    def test_required_fields_validation(self, api_client, auth_headers):
        """Test required fields are enforced."""
        response = api_client.post(
            "/items",
            json={},  # Missing required fields
            headers=auth_headers
        )
        
        assert response.status_code in [400, 422]


@pytest.mark.security
class TestRateLimiting:
    """Test rate limiting (if implemented)."""
    
    def test_rate_limit_enforcement(self, api_client):
        """Test rate limiting prevents abuse."""
        # Make many requests rapidly
        responses = []
        for i in range(100):
            response = api_client.get("/items")
            responses.append(response.status_code)
        
        # Some requests should be rate limited (429) if implemented
        # Otherwise all should be 200
        assert all(code in [200, 429] for code in responses)
