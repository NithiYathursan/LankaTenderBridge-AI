import json
from pathlib import Path
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[3]

CONFIG_PATH = PROJECT_ROOT / "configs" / "tender_sources.json"


def load_sources(config_path=CONFIG_PATH):
    """Load and validate tender source configuration."""

    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}"
        )

    with config_path.open("r", encoding="utf-8-sig") as file:
        configuration = json.load(file)

    sources = configuration.get("sources")

    if not isinstance(sources, list):
        raise ValueError("'sources' must be a list.")

    required_fields = {
        "id",
        "name",
        "base_url",
        "source_type",
        "status",
        "collection_enabled"
    }

    seen_ids = set()

    for source in sources:

        if not isinstance(source, dict):
            raise ValueError("Each source must be an object.")

        missing_fields = required_fields - source.keys()

        if missing_fields:
            raise ValueError(
                f"Missing required fields: {sorted(missing_fields)}"
            )

        if not isinstance(source["id"], str) or not source["id"].strip():
            raise ValueError("Source ID must be a non-empty string.")

        if source["id"] in seen_ids:
            raise ValueError(
                f"Duplicate source ID: {source['id']}"
            )

        seen_ids.add(source["id"])

        for field in ("name", "source_type", "status"):
            if not isinstance(source[field], str) or not source[field].strip():
                raise ValueError(f"Invalid value for {field}")

        url = source["base_url"]

        if not isinstance(url, str):
            raise ValueError("base_url must be a string.")

        parsed_url = urlparse(url)

        if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
            raise ValueError(f"Invalid source URL: {url}")

        if not isinstance(source["collection_enabled"], bool):
            raise ValueError(
                "collection_enabled must be true or false."
            )

    return sources


def display_sources(sources):
    """Display registered tender sources."""

    print("\nLankaTenderBridge AI")
    print("Government Tender Source Registry")
    print("-" * 50)

    for source in sources:

        print(f"\nSource ID: {source['id']}")
        print(f"Organization: {source['name']}")
        print(f"Website: {source['base_url']}")
        print(f"Type: {source['source_type']}")
        print(f"Status: {source['status']}")
        print(f"Collection Enabled: {source['collection_enabled']}")

    print("\n" + "-" * 50)
    print(f"Total registered sources: {len(sources)}")


if __name__ == "__main__":
    tender_sources = load_sources()
    display_sources(tender_sources)