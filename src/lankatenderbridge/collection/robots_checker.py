import requests

from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

from source_registry import load_sources


USER_AGENT = "LankaTenderBridgeResearch/0.1"


# Candidate procurement pages for verification
PROCUREMENT_PATHS = {
    "gov_gazette": "/",
    "railways": (
        "/web/index.php?option=com_content"
        "&view=category&layout=blog&id=51&lang=en"
    ),
    "ceb": "/tender-notice/en",
    "waterboard": "/tenders/",
}


def check_robots(source):
    """Check robots rules for a candidate procurement URL."""

    base_url = source["base_url"].rstrip("/")

    procurement_path = PROCUREMENT_PATHS.get(
        source["id"]
    )

    if procurement_path is None:
        print(f"\nNo procurement path configured for {source['id']}")
        return

    robots_url = urljoin(base_url + "/", "robots.txt")

    procurement_url = urljoin(
        base_url + "/",
        procurement_path.lstrip("/")
    )

    print(f"\nOrganization: {source['name']}")
    print(f"Robots URL: {robots_url}")
    print(f"Procurement URL: {procurement_url}")

    try:
        response = requests.get(
            robots_url,
            headers={"User-Agent": USER_AGENT},
            timeout=10,
            allow_redirects=True,
        )

        print(f"HTTP Status: {response.status_code}")

        if response.status_code != 200:
            print("Robots Status: UNVERIFIED")
            return

        parser = RobotFileParser()
        parser.parse(response.text.splitlines())

        allowed = parser.can_fetch(
            USER_AGENT,
            procurement_url
        )

        if allowed:
            print("Robots Status: ALLOWED")
        else:
            print("Robots Status: DISALLOWED")

        print(
            "Note: This checks robots rules only, "
            "not legal permission or website terms."
        )

    except requests.RequestException as error:
        print(f"Robots Status: UNVERIFIED ({error})")


def main():

    sources = load_sources()

    print("\nLankaTenderBridge AI")
    print("Procurement Page Robots Verification")
    print("=" * 55)

    for source in sources:
        check_robots(source)


if __name__ == "__main__":
    main()