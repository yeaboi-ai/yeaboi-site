# yeaboi-site

[yeaboi.ai](https://yeaboi.ai) — the marketing and documentation site for
[yeaboi](https://github.com/yeaboi-ai/yeaboi.ai), an AI Scrum Master for your terminal.

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
