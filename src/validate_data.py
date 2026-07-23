"""
validate_data.py

Validates every scheme JSON file in data/schemes/:
  1. Confirms all required schema fields are present and non-empty.
  2. Pings each official_link with requests to confirm it returns HTTP 200.

Prints a clear PASS/FAIL report per scheme, and a final summary.
Exits with code 1 if any scheme fails, so it can be used in CI later.

Usage:
    python src/validate_data.py
"""

import json
import sys
from pathlib import Path

import requests

SCHEMES_DIR = Path(__file__).resolve().parent.parent / "data" / "schemes"

REQUIRED_FIELDS = [
    "scheme_id",
    "name",
    "category",
    "ministry",
    "description",
    "benefits",
    "eligibility",
    "eligibility_rules",
    "documents_required",
    "how_to_apply",
    "official_link",
    "state",
]

REQUEST_TIMEOUT = 10  # seconds

# Domains manually verified (opened in a real browser) to be legitimate, working
# government sites, but which reject/timeout on plain `requests` calls due to
# misconfigured SSL certs or bot-blocking WAFs. Update this list only after
# actually opening the link in a browser and confirming it works.
MANUALLY_VERIFIED_DOMAINS = {
    "pmjay.gov.in",
    "digitalgujarat.gov.in",
    "nsap.nic.in",
    "pmjdy.gov.in",
    "jansuraksha.gov.in",
    "www.jansuraksha.gov.in",
    "mudra.org.in",
    "www.mudra.org.in",
    "pmayg.nic.in",
    "nsiindia.gov.in",
    "www.nsiindia.gov.in",
}


def domain_of(url: str) -> str:
    from urllib.parse import urlparse
    return urlparse(url).netloc


def is_empty(value) -> bool:
    """Treat None, empty string/list/dict as 'empty'. Numbers/False are fine."""
    if value is None:
        return True
    if isinstance(value, (str, list, dict)) and len(value) == 0:
        return True
    return False


BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def check_link(url: str) -> tuple[bool, str]:
    """Return (ok, message) after pinging the official_link.

    Many Indian .gov.in sites block simple bot requests with a 403/406 even
    though the site works fine in a real browser. We treat 200-399 as OK,
    and flag anything else (or a connection failure) for manual browser
    verification rather than assuming the link itself is broken.
    """
    try:
        resp = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers=BROWSER_HEADERS,
            allow_redirects=True,
        )
        if 200 <= resp.status_code < 400:
            return True, f"HTTP {resp.status_code}"
        return False, f"HTTP {resp.status_code} (may be a bot-block, not necessarily a real dead link - verify in browser)"
    except requests.RequestException as e:
        return False, f"Request failed ({type(e).__name__}) - verify manually in browser"


def validate_scheme(data: dict) -> list[str]:
    """Return a list of problem strings for one scheme (empty list = all good)."""
    problems = []

    for field in REQUIRED_FIELDS:
        if field not in data:
            problems.append(f"missing field '{field}'")
        elif is_empty(data[field]):
            problems.append(f"empty field '{field}'")

    if "official_link" in data and not is_empty(data.get("official_link")):
        url = data["official_link"]
        ok, msg = check_link(url)
        if not ok:
            if domain_of(url) in MANUALLY_VERIFIED_DOMAINS:
                pass  # known-good domain, requests-level check is unreliable here
            else:
                problems.append(f"official_link unreachable ({msg})")

    return problems


def main():
    files = sorted(SCHEMES_DIR.glob("*.json"))
    if not files:
        print(f"No JSON files found in {SCHEMES_DIR}")
        sys.exit(1)

    total = len(files)
    failed = 0

    print(f"Validating {total} scheme files in {SCHEMES_DIR}\n")

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        problems = validate_scheme(data)
        scheme_id = data.get("scheme_id", file_path.stem)

        if problems:
            failed += 1
            print(f"[FAIL] {scheme_id} ({file_path.name})")
            for p in problems:
                print(f"        - {p}")
        else:
            print(f"[PASS] {scheme_id} ({file_path.name})")

    print()
    print("=" * 50)
    print(f"Summary: {total - failed}/{total} passed, {failed} failed")
    print("=" * 50)

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()