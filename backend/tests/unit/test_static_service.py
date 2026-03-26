import pytest
from pathlib import Path
from src.services.static_service import StaticFileService
from src.exceptions import FileNotFoundError, DirectoryTraversalError


class TestStaticFileService:
    @pytest.fixture
    def service(self, tmp_path):
        (tmp_path / "index.html").write_text("<html></html>")
        (tmp_path / "css").mkdir()
        (tmp_path / "css" / "style.css").write_text("body {}")
        return StaticFileService(tmp_path)
    
    def test_get_file_success(self, service):
        result = service.get_file("index.html")
        assert result.exists()
        assert result.name == "index.html"
    
    def test_get_file_not_found(self, service):
        with pytest.raises(FileNotFoundError):
            service.get_file("nonexistent.html")
    
    def test_directory_traversal_blocked(self, service):
        with pytest.raises(DirectoryTraversalError):
            service.get_file("../etc/passwd")
    
    def test_absolute_path_blocked(self, service):
        with pytest.raises(DirectoryTraversalError):
            service.get_file("/etc/passwd")
    
    def test_path_normalization(self, service):
        result = service.get_file("./index.html")
        assert result.exists()
    
    def test_file_exists_true(self, service):
        assert service.file_exists("index.html") is True
    
    def test_file_exists_false(self, service):
        assert service.file_exists("nonexistent.html") is False
    
    def test_file_exists_traversal(self, service):
        assert service.file_exists("../etc/passwd") is False
