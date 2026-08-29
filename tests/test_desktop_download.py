"""Guards for the macOS download links — the only links on this site that point at
a binary.

Everything else the site offers is a command a visitor types. These two are files a
visitor runs, and three ways that goes wrong are all silent:

1. **Wrong repo.** ``yeaboi-ai/yeaboi-desktop`` is private — every link into it is a
   404 for everyone outside the org, and it looks fine in review.
2. **A versioned asset name.** ``releases/latest/download/<asset>`` resolves only
   while ``<asset>`` is identical across releases, so a name carrying the version
   404s both links the day after the next release. This repo has no build step, no
   deploy job and no link checker, so nothing else would ever notice.
3. **Two variants that look interchangeable.** The two disk images differ only by an
   arch token, so the page has to carry the words that tell them apart.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location("gen_site_seo", ROOT / "scripts" / "gen_site_seo.py")
seo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(seo)

#: The two pages that offer a download.
DOWNLOAD_PAGES = (ROOT / "index.html", ROOT / "desktop.html")
IDS = [p.name for p in DOWNLOAD_PAGES]

PRIVATE_REPO = "github.com/yeaboi-ai/yeaboi-desktop/"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestReleaseHost:
    @pytest.mark.parametrize("page", DOWNLOAD_PAGES, ids=IDS)
    def test_every_dmg_link_uses_the_public_releases_repo(self, page: Path) -> None:
        links = re.findall(r'href="([^"]+\.dmg)"', _read(page))
        assert links, f"{page.name} offers no download at all"
        for link in links:
            assert link.startswith(seo.DESKTOP_DOWNLOAD), f"{page.name} links {link}"

    def test_the_private_source_repo_is_linked_from_nowhere(self) -> None:
        """Its releases 404 for anyone outside the org, including every visitor."""
        for page in seo.pages():
            assert PRIVATE_REPO not in _read(page), f"{page.name} links the private desktop repo"


class TestAssetNames:
    def test_the_pages_reference_exactly_the_declared_assets(self) -> None:
        found = {
            link.rsplit("/", 1)[-1]
            for page in DOWNLOAD_PAGES
            for link in re.findall(r'href="([^"]+\.dmg)"', _read(page))
        }
        assert found == set(seo.DESKTOP_ASSETS.values())

    @pytest.mark.parametrize("asset", sorted(seo.DESKTOP_ASSETS.values()))
    def test_no_asset_name_carries_a_version(self, asset: str) -> None:
        assert not re.search(r"\d+\.\d+\.\d+", asset), (
            f"{asset} embeds a version — keep electron-builder's mac.artifactName at "
            f"'${{productName}}-${{arch}}.${{ext}}' so latest/download keeps resolving"
        )

    def test_each_architecture_is_named_in_its_filename(self) -> None:
        assert "arm64" in seo.DESKTOP_ASSETS["arm64"]
        assert "x64" in seo.DESKTOP_ASSETS["x64"], (
            "electron-builder omits the arch token on the default arch, leaving a bare "
            "name that reads like the one everybody should take"
        )


class TestBothVariantsArePresented:
    @pytest.mark.parametrize("page", DOWNLOAD_PAGES, ids=IDS)
    def test_both_are_offered_and_labelled(self, page: Path) -> None:
        text = _read(page)
        assert 'data-arch="arm64"' in text and 'data-arch="x64"' in text
        assert "Apple silicon" in text and "Intel" in text

    @pytest.mark.parametrize("page", DOWNLOAD_PAGES, ids=IDS)
    def test_exactly_one_default_is_marked_in_the_static_html(self, page: Path) -> None:
        """JS is an enhancement, never a requirement.

        initDesktopDownload() only MOVES the emphasis, and only when a Chromium
        browser resolves architecture 'x86'. With JS off, or in Safari, the default
        has to already be right in the bytes.
        """
        assert _read(page).count("dl-btn is-recommended") == 1

    @pytest.mark.parametrize("page", DOWNLOAD_PAGES, ids=IDS)
    def test_the_which_one_instruction_is_present(self, page: Path) -> None:
        assert "About This Mac" in _read(page)

    def test_the_enhancement_runs_on_both_init_paths(self) -> None:
        """navigateTo swaps #page-content via outerHTML, so a function called once on
        DOMContentLoaded stops running after the first client-side nav."""
        js = seo.SITE_JS.read_text(encoding="utf-8")
        assert js.count("initDesktopDownload();") == 2


class TestNoShellPromptLeaks:
    """``.codeblock code::before`` and ``.step-cmd::before`` both inject ``content:"$ "``.

    A .dmg filename rendered with a shell prompt in front of it is a lie about what
    the visitor is looking at, and it is invisible in a diff — the ``"$ "`` is in the
    CSS, not the HTML.
    """

    @pytest.mark.parametrize("page", DOWNLOAD_PAGES, ids=IDS)
    def test_the_download_row_uses_neither_command_class(self, page: Path) -> None:
        text = _read(page)
        row = text[text.index('<div class="dl-row"') : text.index("</section>", text.index('<div class="dl-row"'))]
        assert "codeblock" not in row
        assert "step-cmd" not in row


class TestPlatformHonesty:
    def test_no_installer_is_offered_for_a_platform_that_does_not_ship(self) -> None:
        for page in DOWNLOAD_PAGES:
            text = _read(page)
            for ext in (".exe", ".msi", ".AppImage", ".deb", ".rpm", ".snap"):
                assert ext not in text, f"{page.name} offers a {ext} the product does not ship"

    @pytest.mark.parametrize("page", DOWNLOAD_PAGES, ids=IDS)
    def test_the_download_size_is_stated(self, page: Path) -> None:
        """A third of a gigabyte is a surprise worth naming; dropping it is silent."""
        assert re.search(r"~\s*\d{2,4}\s*MB", _read(page))

    def test_the_desktop_page_does_not_promise_a_gatekeeper_workaround(self) -> None:
        """The builds are signed and notarized, so the page says the app just opens.

        If that ever stops being true this is where the xattr instructions go — but
        adding them pre-emptively teaches people a habit they should not have.
        """
        text = _read(ROOT / "docs" / "desktop.html")
        assert "xattr" in text, "the docs should at least name the thing you should NOT need"
        assert "should <em>not</em> need" in text


def test_the_hero_offers_the_mac_app_before_a_visitor_has_to_scroll() -> None:
    """The download section sits below the modes; the hero is what most people see.

    Without a link up here the whole launch is invisible above the fold: the hero
    offered the curl install and the docs, and nothing else, so a visitor looking
    for the app had to scroll past every mode card to find it.
    """
    landing = (ROOT / "index.html").read_text(encoding="utf-8")
    hero = landing[: landing.index('<section id="modes"')]
    assert "/desktop.html" in hero, "nothing above the modes points at the Mac app"
