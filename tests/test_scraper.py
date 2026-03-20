"""Tests for the NCCN scraper module."""

from pathlib import Path

from nccn_monitor.scraper import (
    parse_category_page,
    parse_recently_published,
    parse_detail_page_for_pdf,
    slugify,
    format_pdf_filename,
    ScrapeError,
)
from nccn_monitor.guideline_names import GUIDELINE_ZH

FIXTURES = Path(__file__).parent / "fixtures"


# ── Category page tests (primary data source) ───────────────────────


def test_parse_category_page_extracts_all_items():
    html = (FIXTURES / "category_page.html").read_text()
    results = parse_category_page(html, "Cancer by Type")

    assert len(results) == 5
    names = [g.name for g in results]
    assert "Non-Small Cell Lung Cancer" in names
    assert "Breast Cancer" in names
    assert "Prostate Cancer" in names


def test_parse_category_page_extracts_versions():
    html = (FIXTURES / "category_page.html").read_text()
    results = parse_category_page(html, "Cancer by Type")

    by_name = {g.name: g for g in results}
    assert by_name["Non-Small Cell Lung Cancer"].version == "5.2026"
    assert by_name["Colon Cancer"].version == "1.2026"


def test_parse_category_page_builds_detail_urls():
    html = (FIXTURES / "category_page.html").read_text()
    results = parse_category_page(html, "Cancer by Type")

    by_name = {g.name: g for g in results}
    assert by_name["Gastric Cancer"].detail_url == (
        "https://www.nccn.org/guidelines/guidelines-detail?category=1&id=1003"
    )


def test_parse_category_page_sets_category():
    html = (FIXTURES / "category_page.html").read_text()
    results = parse_category_page(html, "Supportive Care")

    assert all(g.category == "Supportive Care" for g in results)


def test_parse_category_page_both_columns():
    """Ensure items from both col-md-6 columns are extracted."""
    html = (FIXTURES / "category_page.html").read_text()
    results = parse_category_page(html, "Cancer by Type")

    # Items from left column (3) and right column (2)
    assert len(results) == 5


def test_parse_category_page_empty_raises():
    try:
        parse_category_page("<html><body></body></html>", "Test")
        assert False, "Should have raised ScrapeError"
    except ScrapeError:
        pass


# ── Recently Published page tests (secondary data source) ───────────


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
    assert by_name["Lung Cancer Screening"].version == "1.2026"


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


# ── Detail page PDF extraction tests ─────────────────────────────


def test_parse_detail_page_extracts_main_pdf():
    html = (FIXTURES / "detail_page.html").read_text()
    pdf_url = parse_detail_page_for_pdf(html)

    assert pdf_url == "https://www.nccn.org/professionals/physician_gls/pdf/gastric.pdf"


def test_parse_detail_page_skips_blocks_and_patient():
    """Should return the main guideline PDF, not Evidence Blocks or patient PDF."""
    html = (FIXTURES / "detail_page.html").read_text()
    pdf_url = parse_detail_page_for_pdf(html)

    assert "blocks" not in pdf_url
    assert "patient" not in pdf_url


def test_parse_detail_page_no_pdf():
    html = "<html><body><h4 class='GL'>Guidelines</h4><ul class='pdfList'></ul></body></html>"
    pdf_url = parse_detail_page_for_pdf(html)
    assert pdf_url is None


# ── Slugify tests ────────────────────────────────────────────────


def test_slugify_basic():
    assert slugify("Breast Cancer") == "breast-cancer"


def test_slugify_colon():
    assert slugify("Melanoma: Uveal") == "melanoma-uveal"


def test_slugify_slash():
    result = slugify("Ovarian Cancer/Fallopian Tube Cancer/Primary Peritoneal Cancer")
    assert result == "ovarian-cancer-fallopian-tube-cancer-primary-peritoneal-cancer"


def test_slugify_parentheses():
    assert slugify("Wilms Tumor (Nephroblastoma)") == "wilms-tumor-nephroblastoma"


def test_slugify_special_chars():
    result = slugify("Waldenström Macroglobulinemia/Lymphoplasmacytic Lymphoma")
    assert "/" not in result
    assert " " not in result


def test_slugify_all_92_guidelines_unique():
    """CRITICAL: All 92 guideline names must produce unique slugs."""
    slugs = [slugify(name) for name in GUIDELINE_ZH.keys()]
    assert len(slugs) == len(set(slugs)), (
        f"Duplicate slugs found! {len(slugs)} names → {len(set(slugs))} unique slugs"
    )


# ── PDF filename format tests ────────────────────────────────────


def test_format_pdf_filename_basic():
    assert format_pdf_filename("Gastric Cancer", "2.2026") == "NCCN_GastricCancer_2026.V2_EN.pdf"


def test_format_pdf_filename_multi_word():
    assert format_pdf_filename("Non-Small Cell Lung Cancer", "5.2026") == "NCCN_NonSmallCellLungCancer_2026.V5_EN.pdf"


def test_format_pdf_filename_colon():
    assert format_pdf_filename("Melanoma: Uveal", "2.2026") == "NCCN_MelanomaUveal_2026.V2_EN.pdf"


def test_format_pdf_filename_slash():
    result = format_pdf_filename("Ovarian Cancer/Fallopian Tube Cancer/Primary Peritoneal Cancer", "2.2026")
    assert result == "NCCN_OvarianCancerFallopianTubeCancerPrimaryPeritonealCancer_2026.V2_EN.pdf"


def test_format_pdf_filename_hyphen():
    assert format_pdf_filename("B-Cell Lymphomas", "3.2026") == "NCCN_BCellLymphomas_2026.V3_EN.pdf"


def test_format_pdf_filename_parentheses():
    result = format_pdf_filename("Wilms Tumor (Nephroblastoma)", "2.2025")
    assert result == "NCCN_WilmsTumorNephroblastoma_2025.V2_EN.pdf"
