import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from src.middleware.security import setup_security_middleware


class TestSecurityMiddleware:
    @pytest.fixture
    def app(self):
        app = FastAPI()
        setup_security_middleware(app)
        
        @app.get("/")
        async def root():
            return {"status": "ok"}
        
        return app
    
    @pytest.fixture
    def client(self, app):
        return TestClient(app)
    
    def test_security_headers_present(self, client):
        response = client.get("/")
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert "Strict-Transport-Security" in response.headers
    
    def test_cors_headers_present(self, client):
        response = client.get("/")
        assert "access-control-allow-origin" in response.headers
