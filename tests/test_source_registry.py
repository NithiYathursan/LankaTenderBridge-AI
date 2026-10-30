import json
import sys
from pathlib import Path

import pytest

# Add src directory to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from lankatenderbridge.collection.source_registry import load_sources


@pytest.fixture
def valid_source():
    """Create a valid example tender source."""
    return {
        "id": "test_source",
        "name": "Example Government Department",
        "base_url": "https://example.com",
        "source_type": "department_procurement",
        "status": "pending_verification",
        "collection_enabled": False
    }


def write_config(tmp_path, sources):
    """Create a temporary JSON configuration for testing."""

    config_path = tmp_path / "tender_sources.json"

    config_path.write_text(
        json.dumps({"sources": sources}),
        encoding="utf-8"
    )

    return config_path


def test_valid_source_loading(tmp_path, valid_source):
    """Test loading a valid tender source."""

    config_path = write_config(tmp_path, [valid_source])

    sources = load_sources(config_path)

    assert len(sources) == 1
    assert sources[0]["id"] == "test_source"


def test_missing_config_file(tmp_path):
    """Test handling of a missing configuration file."""

    missing_file = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_sources(missing_file)


def test_duplicate_source_ids(tmp_path, valid_source):
    """Test that duplicate source IDs are rejected."""

    sources = [valid_source, valid_source.copy()]

    config_path = write_config(tmp_path, sources)

    with pytest.raises(ValueError, match="Duplicate source ID"):
        load_sources(config_path)


def test_invalid_url(tmp_path, valid_source):
    """Test that invalid URLs are rejected."""

    invalid_source = valid_source.copy()
    invalid_source["base_url"] = "invalid-url"

    config_path = write_config(tmp_path, [invalid_source])

    with pytest.raises(ValueError, match="Invalid source URL"):
        load_sources(config_path)