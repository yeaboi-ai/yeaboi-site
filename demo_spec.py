"""What this repo's README GIF shows: the site it serves.

Recorded against `make serve` on :8899, which serves the repo root exactly as
GitHub Pages does — so what is filmed is what merging publishes.
"""

_HOME = "http://localhost:8899/"

SPEC = {
    "kind": "page",
    "gif": "demo-site.gif",
    "url": _HOME,
    "width": 1440,
    "height": 900,
    # A scrolling page changes every pixel in every frame, which is the worst
    # case for GIF. Fewer frames and a tighter palette keep it loadable; the
    # boards and the app window, which are mostly static, need neither.
    "gif_fps": 10,
    "gif_colors": 96,
    "serve": ["make", "serve"],
    "serve_cwd": ".",
    "serve_ready": _HOME,
    "steps": [
        ("goto", _HOME),
        ("pause", 1.8),
        # Down the landing page. Scrolled in small increments rather than
        # jumped, so the frame loop has motion to capture.
        ("scroll", 850),
        ("pause", 1.6),
        ("scroll", 850),
        ("pause", 1.6),
        # Then into the docs, which are the other half of what this repo holds.
        ("goto", "http://localhost:8899/docs/index.html"),
        ("pause", 2.0),
        ("scroll", 700),
        ("pause", 2.0),
    ],
    "verify": {
        "duration_s": (6.0, 45.0),
    },
}
