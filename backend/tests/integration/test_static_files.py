import pytest
import requests

BASE_URL = "http://localhost:80"

class TestStaticFileServing:
    
    def test_health_endpoint_returns_200(self):
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        assert "healthy" in response.text

    def test_index_html_served(self):
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        assert "text/html" in response.headers["Content-Type"]
        assert response.headers.get("Cache-Control") == "no-cache"

    def test_css_files_have_correct_mime_type(self):
        response = requests.get(f"{BASE_URL}/styles.css")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/css"

    def test_js_files_have_correct_mime_type(self):
        response = requests.get(f"{BASE_URL}/app.js")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/javascript"

    def test_static_assets_have_caching_headers(self):
        response = requests.get(f"{BASE_URL}/app.js")
        assert response.status_code == 200
        cache_control = response.headers.get("Cache-Control")
        assert "public" in cache_control
        assert "immutable" in cache_control

    def test_spa_routing_fallback(self):
        response = requests.get(f"{BASE_URL}/nonexistent-route")
        assert response.status_code == 200
        assert "text/html" in response.headers["Content-Type"]

    def test_security_headers_present(self):
        response = requests.get(f"{BASE_URL}/")
        assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"

    def test_gzip_enabled(self):
        headers = {"Accept-Encoding": "gzip"}
        response = requests.get(f"{BASE_URL}/app.js", headers=headers)
        assert response.headers.get("Content-Encoding") == "gzip"
