import requests

from urllib.parse import urljoin

from source_registry import load_sources


USER_AGENT = "LankaTenderBridgeResearch/0.1"


PROCUREMENT_PATHS = {
    "gov_gazette": "/",
    "railways": (
        "/web/index.php?option=com_content"
        "&view=category&layout=blog&id=51&lang=en"
    ),
    "ceb": "/tender-notice/en",
    "waterboard": "/tenders/",
}


def check_page(source):
    """Check whether a candidate procurement page is reachable."""

    source_id = source["id"]
    base_url = source["base_url"].rstrip("/")

    path = PROCUREMENT_PATHS.get(source_id)

    if path is None:
        print(f"\nNo procurement path configured: {source_id}")
        return

    page_url = urljoin(
        base_url + "/",
        path.lstrip("/")
    )

    print(f"\nOrganization: {source['name']}")
    print(f"Requested URL: {page_url}")

    try:
        with requests.get(
            page_url,
            headers={"User-Agent": USER_AGENT},
            timeout=15,
            allow_redirects=True,
            stream=True,
        ) as response:

            print(f"HTTP Status: {response.status_code}")
            print(f"Final URL: {response.url}")

            content_type = response.headers.get(
                "Content-Type",
                "Unknown"
            )

            print(f"Content Type: {content_type}")

            if response.status_code == 200:

                if "text/html" in content_type.lower():
                    print("Result: REACHABLE HTML PAGE")
                else:
                    print("Result: REACHABLE NON-HTML RESOURCE")

            elif response.status_code == 403:
                print("Result: ACCESS FORBIDDEN")

            elif response.status_code == 404:
                print("Result: PAGE NOT FOUND")

            else:
                print("Result: REQUIRES INVESTIGATION")

    except requests.RequestException as error:
        print(f"Result: CONNECTION ERROR ({error})")


def main():

    sources = load_sources()

    print("\nLankaTenderBridge AI")
    print("Procurement Page Availability Checker")
    print("=" * 55)

    for source in sources:
        check_page(source)


if __name__ == "__main__":
    main()