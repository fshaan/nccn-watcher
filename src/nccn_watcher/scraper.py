"""Scrape NCCN Recently Published Guidelines page for version updates."""

import re
import logging
import httpx
from bs4 import BeautifulSoup
from dataclasses import dataclass

logger = logging.getLogger(__name__)

RECENTLY_PUBLISHED_URL = "https://www.nccn.org/guidelines/recently-published-guidelines"

# Version pattern: "Version X.YYYY" (e.g., "Version 5.2026")
VERSION_PATTERN = re.compile(r"Version\s+(\d+\.\d{4})")

# PDF URL base
PDF_BASE = "https://www.nccn.org"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass
class GuidelineInfo:
    """A single guideline's current version info from NCCN."""

    name: str
    version: str
    pdf_url: str
    category: str = ""


async def fetch_recently_published() -> list[GuidelineInfo]:
    """Fetch and parse the NCCN Recently Published Guidelines page.

    Returns a list of GuidelineInfo with name, version, and pdf_url
    for every guideline listed on the page.

    Raises ScrapeError if the page cannot be fetched or parsed.
    """
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        resp = await client.get(RECENTLY_PUBLISHED_URL, timeout=30)
        resp.raise_for_status()

    return parse_recently_published(resp.text)


def parse_recently_published(html: str) -> list[GuidelineInfo]:
    """Parse the Recently Published page HTML into GuidelineInfo list.

    The page structure (as of 2026-03):
      <h2>Category Title</h2>
      <ul>
        <li><a href="/professionals/physician_gls/pdf/xxx.pdf">Guideline Name</a> Version X.YYYY</li>
        ...
      </ul>
    """
    soup = BeautifulSoup(html, "html.parser")
    results: list[GuidelineInfo] = []
    current_category = ""

    # Walk through content looking for headers and list items
    content = soup.find("div", class_="content") or soup.find("main") or soup.body
    if not content:
        raise ScrapeError("Cannot find main content area on the page")

    for element in content.descendants:
        # Track category headers
        if element.name in ("h2", "h3"):
            current_category = element.get_text(strip=True)
            continue

        # Process list items containing guideline links
        if element.name == "li":
            link = element.find("a", href=True)
            if not link:
                continue

            href = link["href"]
            # Only care about PDF links
            if ".pdf" not in href:
                continue

            name = link.get_text(strip=True)
            if not name:
                continue

            # Extract version from the full <li> text
            li_text = element.get_text()
            version_match = VERSION_PATTERN.search(li_text)
            version = version_match.group(1) if version_match else ""

            # Build absolute PDF URL
            pdf_url = href if href.startswith("http") else PDF_BASE + href

            results.append(
                GuidelineInfo(
                    name=name,
                    version=version,
                    pdf_url=pdf_url,
                    category=current_category,
                )
            )

    if not results:
        raise ScrapeError(
            "No guidelines found on the page. "
            "The HTML structure may have changed."
        )

    logger.info("Scraped %d guidelines from NCCN Recently Published", len(results))
    return results


class ScrapeError(Exception):
    """Raised when scraping fails due to network or structural issues."""
