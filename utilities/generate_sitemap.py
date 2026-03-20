"""Generate a sitemap for the Russian Course static site.

This script scans the site root for HTML pages that should be indexable and
prints a sitemap.xml document to stdout. It intentionally skips support,
utility, and experimental directories that may contain HTML files but should
not be indexed as site pages.
"""

import os
from datetime import datetime
from pathlib import Path

BASE_URL = "https://ellablac.github.io/RussianCourse/"
# Skip rules
SKIP_DIR = [
    ".venv",         # skip the local virtual environment
    "venv",          # skip any directory named 'venv'
    "assets",        # skip shared assets and HTML fragments/test files
    "utilities",     # skip developer utilities and tool pages
    "sandbox",       # skip experimental pages
]
SKIP_SUFFIXES = [
    "_noix.html",    # skip any file ending with this suffix
    "BAK.html",
    "draft.html"
]
SKIP_FILES = [
    "googleec267fe20a254d80.html",  # Google Search Console verification file
    "test.html",                    # ad hoc test page
    "test2.html",                   # ad hoc test page
]

print('<?xml version="1.0" encoding="UTF-8"?>')
print('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

root_dir = Path(__file__).resolve().parents[1]
for root, dirs, files in os.walk(root_dir):
    # Prevent os.walk from descending into non-indexable directories.
    dirs[:] = [directory for directory in dirs if directory not in SKIP_DIR]

    for file in files:
        if not file.endswith(".html"):
            continue

        # Skip files with excluded suffixes
        if any(file.endswith(suffix) for suffix in SKIP_SUFFIXES):
            continue
        if file in SKIP_FILES:
            continue

        # Build relative path
        full_path = Path(root) / file
        rel_path = full_path.relative_to(root_dir).as_posix()

        if rel_path == "index.html":
            loc = BASE_URL
        else:
            loc = BASE_URL + rel_path
        lastmod = datetime.fromtimestamp(full_path.stat().st_mtime).date()

        print(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lastmod}</lastmod>\n  </url>")

print('</urlset>')
