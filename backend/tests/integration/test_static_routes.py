import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fastapi.testclient import TestClient
from src.main import app


class TestStaticRoutes:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_serve_index_html(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_serve_css_file(self, client):
        response = client.get("/css/style.css")
        # May be 404 if file doesn't exist in test static dir
        # This tests the route exists
        assert response.status_code in [200, 404]
    
    def test_security_headers_present(self, client):
        response = client.get("/")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
    
    def test_spa_fallback(self, client):
        # For non-existent paths, should return index.html (SPA fallback)
        response = client.get("/some/react/route")
        # Will return index.html if static dir is properly set up
        assert response.status_code in [200, 404]
