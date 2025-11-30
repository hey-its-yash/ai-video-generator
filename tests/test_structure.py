"""
Basic Tests
"""
import pytest
from pathlib import Path


def test_project_structure():
    """Test that key directories exist"""
    base_dir = Path(__file__).parent.parent
    
    required_dirs = [
        "app",
        "app/services",
        "app/api",
        "app/models",
        "app/utils",
        "outputs",
        "assets",
        "tests",
    ]
    
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        assert dir_path.exists(), f"Directory {dir_name} does not exist"


def test_config_file_exists():
    """Test that configuration file exists"""
    base_dir = Path(__file__).parent.parent
    config_file = base_dir / "app" / "config.py"
    assert config_file.exists(), "config.py not found"


def test_requirements_file_exists():
    """Test that requirements.txt exists"""
    base_dir = Path(__file__).parent.parent
    req_file = base_dir / "requirements.txt"
    assert req_file.exists(), "requirements.txt not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
