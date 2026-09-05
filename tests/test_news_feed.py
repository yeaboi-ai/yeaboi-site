"""Guards for news/feed.json — the posts and videos the desktop's front page reads.

The yeaboi backend fetches this file (``src/yeaboi/news/sources.py``, source
``yeaboi-site``) and parses it as JSON Feed 1.1 with one extension,
``_yeaboi.kind``. A malformed item is silently skipped there, so this is the
only place a typo in a hand-written entry is ever noticed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FEED = ROOT / "news" / "feed.json"

KINDS = {"post", "video", "release"}
REQUIRED_ITEM_KEYS = {"id", "url", "title", "date_published", "_yeaboi"}


@pytest.fixture(scope="module")
def feed() -> dict:
    return json.loads(FEED.read_text(encoding="utf-8"))


def test_the_feed_is_json_feed_1_1(feed):
    assert feed["version"] == "https://jsonfeed.org/version/1.1"
    assert feed["title"].strip()
    assert feed["home_page_url"] == "https://yeaboi.ai/"
    assert feed["feed_url"] == "https://yeaboi.ai/news/feed.json"
    assert isinstance(feed["items"], list)


def test_every_item_is_complete(feed):
    for item in feed["items"]:
        missing = REQUIRED_ITEM_KEYS - set(item)
        assert not missing, f"{item.get('id')}: missing {sorted(missing)}"
        assert item["title"].strip()
        assert item["url"].startswith("https://"), item["url"]
        assert item["_yeaboi"]["kind"] in KINDS, item["id"]


def test_dates_parse_and_carry_an_offset(feed):
    for item in feed["items"]:
        parsed = datetime.fromisoformat(item["date_published"].replace("Z", "+00:00"))
        assert parsed.tzinfo is not None, item["id"]


def test_items_are_newest_first(feed):
    stamps = [datetime.fromisoformat(item["date_published"].replace("Z", "+00:00")) for item in feed["items"]]
    assert stamps == sorted(stamps, reverse=True)


def test_ids_are_unique(feed):
    ids = [item["id"] for item in feed["items"]]
    assert len(ids) == len(set(ids))


def test_images_are_https_when_given(feed):
    for item in feed["items"]:
        if "image" in item:
            assert item["image"].startswith("https://"), item["id"]


def test_a_video_links_to_youtube(feed):
    for item in feed["items"]:
        if item["_yeaboi"]["kind"] == "video":
            assert "youtube.com/watch?v=" in item["url"] or "youtu.be/" in item["url"], item["id"]
