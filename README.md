<div align="center">

<img src="https://yeaboi.ai/banner.jpg" alt="yeaboi.ai" width="800"/>

# 🤙 yeaboi-site

**[yeaboi.ai](https://yeaboi.ai) — the marketing site, the docs and the install script. Flat HTML, no build step, served off `main` by GitHub Pages.**

[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![Live](https://img.shields.io/badge/live-yeaboi.ai-8caaff?style=for-the-badge)](https://yeaboi.ai)
[![Part of yeaboi](https://img.shields.io/badge/part%20of-yeaboi-ff6600?style=for-the-badge)](https://github.com/yeaboi-ai/yeaboi.ai)

[![CI](https://img.shields.io/github/actions/workflow/status/yeaboi-ai/yeaboi-site/ci.yml?style=for-the-badge&label=CI&logo=github)](https://github.com/yeaboi-ai/yeaboi-site/actions)

</div>

---

<div align="center">
<img src="https://yeaboi.ai/demo-site.gif" alt="The yeaboi.ai landing page scrolling through its sections, then the documentation index" width="800"/>

*What merging publishes. `make demo` re-records this from `demo_spec.py`.*
</div>

---

## What this is

The site for [yeaboi](https://github.com/yeaboi-ai/yeaboi.ai), an AI Scrum Master for your terminal,
and one of **five repos that make one product** — the other four being the Python itself,
[yeaboi-frontend](https://github.com/yeaboi-ai/yeaboi-frontend),
[yeaboi-desktop](https://github.com/yeaboi-ai/yeaboi-desktop) and
[yeaboi-tooling](https://github.com/yeaboi-ai/yeaboi-tooling).

It also hosts the brand art and every demo GIF the other four READMEs point at — `banner.jpg`,
`demo.gif`, and the `demo-*.gif` each repo records with its own `make demo`.

Flat HTML. No framework, no bundler, no build step. GitHub Pages serves this repo's root off `main`,
so **merging a PR publishes it.**

```
index.html          the landing page
404.html            the error page
docs/               the documentation subtree
assets/             CSS, JS, and the brand art the whole site loads
install.sh          served at yeaboi.ai/install.sh — the `curl | sh` installer
CNAME               the custom domain
contracts/          vendored facts about the package (see below)
scripts/            the SEO generator, the OG card renderer, a no-cache dev server
tests/              the guards — this repo's only gate
```

## Working on it

```bash
make install     # one-time: the venv the generator and guards run in
make serve       # http://localhost:8899, served exactly as Pages would
make site-seo    # regenerate the head block, footer, ?v=, sitemap.xml, robots.txt
make test        # the guards
make ship-gate   # what /ship runs: lint, format, tests, both pins
```

**Run `make site-seo` and commit the result whenever you touch a page.** Every page's `<head>`
block, the crawlable footer, the asset cache-bust, `sitemap.xml` and `robots.txt` are generated;
the tests fail page by page when what is committed is stale. Adding a page needs a `KINDS` entry in
`scripts/gen_site_seo.py` and a `NAV_GROUPS` entry in `assets/site.js` — a parity test names
whichever one you forgot.

The words are not generated. Each page's `<title>` and `<meta name="description">` are hand-written
where an author would look for them; the generator parses them out and reuses them everywhere else.

## Two pins

Neither directory below is edited in this repo.

- **`.tooling-rev`** → [yeaboi-tooling](https://github.com/yeaboi-ai/yeaboi-tooling), cloned to a
  gitignored `.tooling/` at Makefile parse time. It supplies the shared `make` targets and the
  `yeaboi-devkit` Claude Code plugin (`/ship`, `/sync-main`, `/wt`). Bump with `make tooling-bump`.
- **`.contracts-rev`** → the `yeaboi` repo. `contracts/site.json` carries the facts this site states
  about the package: the Python floor it advertises, the repo URL in its JSON-LD, the install
  target. Change them upstream, then `make contracts-sync` here.

`make ship-gate` runs both checks. `contracts-check` fails on a copy edited in place and prints a
note when the pin is merely behind upstream.

## Things generated elsewhere

`graph.png` and `demo.gif`/`demo.cast.gz` are produced by scripts in the `yeaboi` repo — they have
to import it — and written into a checkout of this one. `assets/duck-*.png` is the master brand art,
read back the other way by that repo's sprite and icon generators. Both directions are rare and
manual; see `yeaboi`'s CLAUDE.md.

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
