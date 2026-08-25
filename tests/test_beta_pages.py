"""The beta caveat, as this site states it.

Pages that describe a beta mode carry a hand-written copy of wording that lives
in the package's `yeaboi.beta`, and `.beta-pill` carries a hand-written copy of
its colour. HTML cannot import Python, so both arrive through the vendored
contract — and `test_site_contract.py` upstream is what keeps that contract
equal to the constants.

Assertions use the SHORT phrase, never the full sentence: HTML re-wraps at
whatever width the author's editor chose, so a whole-sentence match would fail
for a purely cosmetic reformat.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BETA = json.loads((ROOT / "contracts" / "site.json").read_text(encoding="utf-8"))["beta"]

# Pages that describe Performance to a reader and must carry the caveat.
BETA_DOC_PAGES = (
    ROOT / "index.html",
    ROOT / "docs" / "modes" / "index.html",
    ROOT / "docs" / "modes" / "performance.html",
)

SITE_CSS = ROOT / "assets" / "site.css"


class TestHandWrittenCopies:
    @pytest.mark.parametrize("page", BETA_DOC_PAGES, ids=lambda p: p.name)
    def test_page_carries_the_phrase(self, page: Path) -> None:
        assert BETA["performance_phrase"] in page.read_text(encoding="utf-8")


class TestBetaPill:
    def test_the_class_is_defined(self) -> None:
        assert ".beta-pill{" in SITE_CSS.read_text(encoding="utf-8")

    def test_its_colour_matches_the_terminal_chip(self) -> None:
        pill = SITE_CSS.read_text(encoding="utf-8").split(".beta-pill{", 1)[1].split("}", 1)[0]
        r, g, b = BETA["rgb"]
        assert f"rgb({r},{g},{b})" in pill

    def test_it_is_not_the_live_badge(self) -> None:
        """`.badge::before` injects a green "live" dot, which says the opposite
        of what a beta marker means. The pill must stay its own class."""
        pill = SITE_CSS.read_text(encoding="utf-8").split(".beta-pill{", 1)[1].split("}", 1)[0]
        assert "var(--success)" not in pill

    def test_every_page_using_it_links_site_css(self) -> None:
        for page in ROOT.rglob("*.html"):
            if ".tooling" in page.parts or "tests" in page.parts:
                continue
            text = page.read_text(encoding="utf-8")
            if 'class="beta-pill"' in text:
                assert "/assets/site.css" in text, page


class TestCacheBust:
    def test_all_pages_share_one_cache_bust_version(self) -> None:
        """A new CSS class behind a stale cached stylesheet is an invisible badge.

        That failure mode is silent — the page renders, the pill just doesn't —
        so a half-finished `?v=` sweep is exactly the kind of mistake that ships.
        """
        versions: dict[str, set[str]] = {}
        for page in ROOT.rglob("*.html"):
            if ".tooling" in page.parts or "tests" in page.parts:
                continue
            found = set(re.findall(r"\?v=(\d+)", page.read_text(encoding="utf-8")))
            if found:
                versions[page.relative_to(ROOT).as_posix()] = found

        assert versions, "no cache-busted asset links found — did the convention change?"
        all_versions = set().union(*versions.values())
        assert len(all_versions) == 1, f"mixed cache-bust versions: {versions}"
