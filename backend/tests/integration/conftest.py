import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def static_dir(tmp_path_factory):
    """Create test static directory with files."""
    static_dir = tmp_path_factory.mktemp("static")
    
    # Create index.html
    (static_dir / "index.html").write_text("<html><body>Test</body></html>")
    
    # Create css directory and file
    css_dir = static_dir / "css"
    css_dir.mkdir()
    (css_dir / "style.css").write_text("body { color: red; }")
    
    return static_dir
