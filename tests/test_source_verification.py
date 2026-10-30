import sys
from pathlib import Path
from unittest.mock import Mock

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]

COLLECTION_DIR = (
    PROJECT_ROOT / "src" / "lankatenderbridge" / "collection"
)

sys.path.insert(0, str(COLLECTION_DIR))


from page_checker import check_page
from robots_checker import check_robots


@pytest.fixture
def sample_source():
    return {
        "id": "ceb",
        "name": "Ceylon Electricity Board",
        "base_url": "https://www.ceb.lk",
        "source_type": "utility_procurement",
        "status": "pending_verification",
        "collection_enabled": False,
    }


def test_page_reachable(monkeypatch, capsys, sample_source):
    """Test successful HTML page response."""

    response = Mock()

    response.status_code = 200
    response.url = "https://www.ceb.lk/tender-notice/en"
    response.headers = {
        "Content-Type": "text/html; charset=UTF-8"
    }

    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)

    monkeypatch.setattr(
        "page_checker.requests.get",
        lambda *args, **kwargs: response
    )

    check_page(sample_source)

    output = capsys.readouterr().out

    assert "REACHABLE HTML PAGE" in output


def test_page_forbidden(monkeypatch, capsys, sample_source):
    """Test HTTP 403 response."""

    response = Mock()

    response.status_code = 403
    response.url = "https://www.ceb.lk/tender-notice/en"
    response.headers = {"Content-Type": "text/html"}

    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)

    monkeypatch.setattr(
        "page_checker.requests.get",
        lambda *args, **kwargs: response
    )

    check_page(sample_source)

    output = capsys.readouterr().out

    assert "ACCESS FORBIDDEN" in output


def test_robots_allowed(monkeypatch, capsys, sample_source):
    """Test an allowed procurement page."""

    response = Mock()

    response.status_code = 200

    response.text = (
        "User-agent: *\n"
        "Disallow: /private/\n"
        "Allow: /tender-notice/\n"
    )

    monkeypatch.setattr(
        "robots_checker.requests.get",
        lambda *args, **kwargs: response
    )

    check_robots(sample_source)

    output = capsys.readouterr().out

    assert "Robots Status: ALLOWED" in output


def test_robots_missing(monkeypatch, capsys, sample_source):
    """Test missing robots.txt."""

    response = Mock()
    response.status_code = 404

    monkeypatch.setattr(
        "robots_checker.requests.get",
        lambda *args, **kwargs: response
    )

    check_robots(sample_source)

    output = capsys.readouterr().out

    assert "Robots Status: UNVERIFIED" in output