"""Tests for the NCCN scraper module."""

from pathlib import Path

from nccn_watcher.scraper import parse_recently_published, ScrapeError

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_recently_published_extracts_all_guidelines():
    html = (FIXTURES / "recently_published.html").read_text()
    results = parse_recently_published(html)

    assert len(results) == 5
    names = [g.name for g in results]
    assert "Non-Small Cell Lung Cancer" in names
    assert "Breast Cancer" in names
    assert "Antiemesis" in names


def test_parse_recently_published_extracts_versions():
    html = (FIXTURES / "recently_published.html").read_text()
    results = parse_recently_published(html)

    by_name = {g.name: g for g in results}
    assert by_name["Non-Small Cell Lung Cancer"].version == "5.2026"
    assert by_name["Breast Cancer"].version == "2.2026"
    assert by_name["Lung Cancer Screening"].version == "1.2026"


def test_parse_recently_published_builds_pdf_urls():
    html = (FIXTURES / "recently_published.html").read_text()
    results = parse_recently_published(html)

    by_name = {g.name: g for g in results}
    assert by_name["Gastric Cancer"].pdf_url == (
        "https://www.nccn.org/professionals/physician_gls/pdf/gastric.pdf"
    )


def test_parse_recently_published_tracks_categories():
    html = (FIXTURES / "recently_published.html").read_text()
    results = parse_recently_published(html)

    by_name = {g.name: g for g in results}
    assert by_name["Non-Small Cell Lung Cancer"].category == "Guidelines for Treatment of Cancer by Type"
    assert by_name["Antiemesis"].category == "Guidelines for Supportive Care"


def test_parse_empty_html_raises_scrape_error():
    try:
        parse_recently_published("<html><body><div class='content'></div></body></html>")
        assert False, "Should have raised ScrapeError"
    except ScrapeError:
        pass


def test_parse_html_with_no_content_div():
    """Even without a .content div, parser should try body."""
    html = """<html><body>
    <h2>Test</h2>
    <ul><li><a href="/test.pdf">Test Guide</a> Version 1.2026</li></ul>
    </body></html>"""
    results = parse_recently_published(html)
    assert len(results) == 1
    assert results[0].name == "Test Guide"
