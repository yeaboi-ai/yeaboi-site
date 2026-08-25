"""Guards for scripts/gen_og_card.py.

The rendered PNG is checked by nothing — it is a 1200x630 image, and no test can
read the text out of it. So what is guarded is the *source* of every fact it
draws: a literal here rots silently, and search engines and social cards quote
it for as long as it takes somebody to notice.

Pillow and matplotlib live in the `art` extra and are imported lazily inside the
drawing helpers, so this module loads without them.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_MODULE_PATH = ROOT / "scripts" / "gen_og_card.py"

_spec = importlib.util.spec_from_file_location("gen_og_card", _MODULE_PATH)
og = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(og)

CONTRACT = json.loads((ROOT / "contracts" / "site.json").read_text(encoding="utf-8"))


class TestTheFloorIsDerived:
    def test_it_reads_the_vendored_contract(self) -> None:
        assert og._floor() == CONTRACT["requires_python"].lstrip(">=").split(",")[0].strip()

    def test_it_does_not_read_this_repo_s_own_pyproject(self) -> None:
        """The trap the repo split created, and the reason this test exists.

        `pyproject.toml` here declares what the *generator* runs on. It is a
        different number that happens to look like the right one, so reading it
        produces a card that is correct today and silently wrong the moment
        either floor moves. The package's floor arrives via contracts/site.json.
        """
        tree = ast.parse(_MODULE_PATH.read_text(encoding="utf-8"))
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_floor")
        # body[1:] skips the docstring, which names the trap on purpose.
        body = [n for stmt in fn.body[1:] for n in ast.walk(stmt)]
        reads = [
            n.value for n in body if isinstance(n, ast.Constant) and isinstance(n.value, str) and "pyproject" in n.value
        ]
        assert not reads, "the OG card must take the package floor from contracts/site.json"

    def test_no_python_version_is_spelled_out(self) -> None:
        source = _MODULE_PATH.read_text(encoding="utf-8")
        drawn = [line for line in source.splitlines() if "draw.text" in line]
        assert drawn, "no drawn text found — has the renderer changed?"
        for line in drawn:
            assert not re.search(r"Python 3\.\d", line), f"derive the version, do not spell it out: {line.strip()!r}"


class TestTheArtItReads:
    def test_the_duck_layers_it_composites_are_present(self) -> None:
        for layer in ("base", "wing", "glasses"):
            assert (og.ASSETS / f"duck-{layer}.png").is_file(), f"missing duck-{layer}.png"

    def test_it_writes_the_card_the_pages_reference(self) -> None:
        """Every page's og:image points at this path; test_site_seo asserts the
        file exists, and this asserts the generator is what puts it there."""
        assert og.OUT == ROOT / "assets" / "og-card.png"
