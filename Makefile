# --- shared tooling (yeaboi-tooling, pinned by .tooling-rev) ------------------
#
# Copied verbatim from the tooling repo's bootstrap/Makefile.head. It clones the
# tooling repo to `.tooling/` at the pinned sha and includes the shared targets
# (wt-*, tooling-*, contracts-*). The clone happens at parse time and only when
# the pin and the checkout disagree, so the steady state is two file reads and
# no network — and a fresh `git worktree add`, which never populates a
# submodule, provisions itself on the first `make`.
#
# Bump the pin with `make tooling-bump` and commit `.tooling-rev`.

TOOLING      := .tooling
TOOLING_REV  := $(shell cat .tooling-rev 2>/dev/null | tr -d '[:space:]')
TOOLING_HAVE := $(shell cat $(TOOLING)/.git/tooling-rev 2>/dev/null | tr -d '[:space:]')

ifeq ($(TOOLING_REV),)
$(error missing .tooling-rev — this repo pins the shared tooling by commit sha)
endif
ifneq ($(TOOLING_REV),$(TOOLING_HAVE))
TOOLING_SYNC := $(shell bash scripts/tooling-sync.sh >&2 && echo ok)
ifneq ($(TOOLING_SYNC),ok)
$(error shared tooling could not be synced — see the [tooling] lines above)
endif
endif

# The include brings targets with it, and the first target in a makefile is the
# default goal. Name the goal explicitly so `make` with no arguments still
# prints help rather than cutting a worktree.
.DEFAULT_GOAL := help

include $(TOOLING)/mk/common.mk

# --- end shared tooling ------------------------------------------------------

UV := $(or $(shell command -v uv 2>/dev/null),$(HOME)/.local/bin/uv)

# The facts this site states about the package it documents — the Python floor,
# the repo URL, the install target — belong to the yeaboi repo. They arrive here
# as a vendored snapshot pinned by sha in `.contracts-rev`; never edit
# contracts/site.json in this repo.
CONTRACTS_REPO  := https://github.com/yeaboi-ai/yeaboi.ai.git
CONTRACTS_DIR   := .
CONTRACTS_PATHS := contracts/site.json

.PHONY: help install lint format format-check test test-fast test-scoped ship-gate \
        site-seo site-check site-og serve

help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Create the venv and install the test dependencies
	$(UV) sync

lint: ## Lint the generator and the guards with ruff
	$(UV) run ruff check scripts/ tests/

format: ## Format with ruff (writes)
	$(UV) run ruff format scripts/ tests/
	$(UV) run ruff check --fix scripts/ tests/

format-check: ## What CI's format job runs — asserts, never writes
	$(UV) run ruff format --check scripts/ tests/

# There is no build step and no deploy job: GitHub Pages serves this repo's root
# off `main`. So the test suite IS the deploy gate — a stale SEO block or a
# dropped sitemap entry has nothing else standing between it and production.
test-fast: ## The guards — the whole suite is the fast lane here
	$(UV) run pytest tests/ -q

test-scoped: test-fast ## Everything; this repo is small enough that scoping it would be theatre

test: test-fast ## Everything

site-seo: ## Regenerate the SEO block, crawlable footer, ?v=, sitemap.xml and robots.txt
	$(UV) run python scripts/gen_site_seo.py

site-check: ## Fail if any generated page is stale (also asserted by make test)
	$(UV) run python scripts/gen_site_seo.py --check

site-og: ## Re-render the 1200x630 Open Graph card (needs Pillow — the `art` extra)
	$(UV) run --extra art python scripts/gen_og_card.py

serve: ## Serve the site on :8899 exactly as GitHub Pages would, to preview before merging
	@echo "→ http://localhost:8899  (Ctrl-C to stop)"
	$(UV) run python scripts/serve_docs.py

ship-gate: lint format-check test contracts-check tooling-check ## The full local gate /ship runs
	@echo "[ship-gate] ok"
