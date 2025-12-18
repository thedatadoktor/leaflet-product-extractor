"""
Integration tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns app info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_list_extractions(self):
        """Test list extractions endpoint"""
        response = client.get("/api/v1/extractions")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "extractions" in data
    
    def test_extract_without_file(self):
        """Test extract endpoint without file returns error"""
        response = client.post("/api/v1/extract")
        assert response.status_code == 422  # Unprocessable entity
    
    def test_extract_with_invalid_file_type(self):
        """Test extract endpoint with invalid file type"""
        files = {"file": ("test.txt", b"fake content", "text/plain")}
        response = client.post("/api/v1/extract", files=files)
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]
    
    def test_get_nonexistent_extraction(self):
        """Test getting non-existent extraction returns 404"""
        response = client.get("/api/v1/extractions/nonexistent-id")
        assert response.status_code == 404
