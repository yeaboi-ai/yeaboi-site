#!/usr/bin/env bash
# scripts/provision.sh — what a fresh worktree of THIS repo needs. wt.sh runs it
# from the new worktree's root. Every yeaboi repo has one (or deliberately does
# not): it is the seam where a shared script stops and a toolchain begins.
#
# The site itself has no toolchain — it is flat HTML. This installs the runner
# for the generator and its guards.

set -euo pipefail

UV="$(command -v uv 2>/dev/null || echo "$HOME/.local/bin/uv")"
"$UV" sync --quiet
echo "[provision] test runner ready"
