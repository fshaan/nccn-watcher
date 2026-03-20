"""Tests for the version archive module."""

import json
from pathlib import Path

from nccn_monitor.downloader import get_archived_versions


def test_get_archived_versions_empty(tmp_path: Path):
    """No archive directory → empty list."""
    result = get_archived_versions("gastric-cancer", archive_dir=tmp_path)
    assert result == []


def test_get_archived_versions_with_meta(tmp_path: Path):
    """Versions with meta.json are returned with all fields."""
    archive = tmp_path / "gastric-cancer" / "v2.2026"
    archive.mkdir(parents=True)
    (archive / "guideline.pdf").write_bytes(b"fake pdf content")
    (archive / "meta.json").write_text(json.dumps({
        "version": "2.2026",
        "slug": "gastric-cancer",
        "downloaded_at": "2026-03-20T08:00:00Z",
        "size_bytes": 1234,
    }))

    result = get_archived_versions("gastric-cancer", archive_dir=tmp_path)
    assert len(result) == 1
    assert result[0]["version"] == "2.2026"
    assert result[0]["size_bytes"] == 1234


def test_get_archived_versions_multiple(tmp_path: Path):
    """Multiple versions returned in reverse order (newest first)."""
    for ver in ["v1.2026", "v2.2026"]:
        d = tmp_path / "breast-cancer" / ver
        d.mkdir(parents=True)
        (d / "guideline.pdf").write_bytes(b"pdf")
        (d / "meta.json").write_text(json.dumps({
            "version": ver.lstrip("v"),
            "downloaded_at": "2026-03-20T08:00:00Z",
            "size_bytes": 100,
        }))

    result = get_archived_versions("breast-cancer", archive_dir=tmp_path)
    assert len(result) == 2
    # v2 should come before v1 (reverse sorted)
    assert result[0]["version"] == "2.2026"
    assert result[1]["version"] == "1.2026"


def test_get_archived_versions_pdf_only_no_meta(tmp_path: Path):
    """PDF without meta.json still returned with basic info."""
    d = tmp_path / "lung-cancer" / "v5.2026"
    d.mkdir(parents=True)
    (d / "guideline.pdf").write_bytes(b"pdf data here")

    result = get_archived_versions("lung-cancer", archive_dir=tmp_path)
    assert len(result) == 1
    assert result[0]["version"] == "5.2026"
    assert result[0]["size_bytes"] > 0
