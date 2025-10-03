#  !/usr/bin/env python3
#  Generates a sitemap.xml for the static site by scanning for .html files.
#  Usage: python3 generate_sitemap.py > sitemap.xml
#  Adjust the base_url variable as needed.
#  This script needs to run periodically to update the sitemap as new pages are added.
#  sitemap.xml should be placed in the root directory of the site.
#  It is used by search engine crawlers for SEO purposes.
#  Don't need to urlencode paths since they are already URL-safe 
# (no spaces or special characters including cyrillic letters).

import os
from datetime import datetime

BASE_URL = "https://ellablac.github.io/RussianCourse/"
# Skip rules
SKIP_DIR = [
    "venv",          # skip any directory named 'venv'
]
SKIP_SUFFIXES = [
    "_noix.html",    # skip any file ending with this suffix
    "BAK.html",
    "draft.html"
]

print('<?xml version="1.0" encoding="UTF-8"?>')
print('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

root_dir = "../"  # Adjust if the script is run from a different directory
for root, dirs, files in os.walk(root_dir):
    # Skip unwanted directories (like venv)
    if any(skip in root.replace("\\", "/") for skip in SKIP_DIR):
        continue
    for file in files:
        if not file.endswith(".html"):
            continue

        # Skip files with excluded suffixes
        if any(file.endswith(suffix) for suffix in SKIP_SUFFIXES):
            continue

        # Build relative path
        rel_path = os.path.join(root, file).replace("\\", "/").lstrip("./")
        full_path = os.path.join(root, file)

        loc = BASE_URL + rel_path
        lastmod = datetime.fromtimestamp(os.path.getmtime(full_path)).date()

        print(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lastmod}</lastmod>\n  </url>")

print('</urlset>')