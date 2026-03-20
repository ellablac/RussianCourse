"""Generate the Russian Course sitemap.xml file.

This utility scans the public site tree for indexable HTML pages, skips
support and draft content, and writes the resulting sitemap to the site root.
The script writes UTF-8 explicitly so the XML declaration matches the file
encoding on every platform.
"""

from __future__ import annotations

import os
from datetime import datetime, date
from pathlib import Path
from typing import Iterator

BASE_URL = "https://ellablac.github.io/RussianCourse/"
ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT_DIR / "sitemap.xml"

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
    "draft.html",
]
SKIP_FILES = [
    "googleec267fe20a254d80.html",  # Google Search Console verification file
    "test.html",                    # ad hoc test page
    "test2.html",                   # ad hoc test page
]


def iter_sitemap_entries(root_dir: Path) -> Iterator[tuple[str, date]]:
    """Yield sitemap URL and modification date pairs for indexable pages.

    Args:
        root_dir: Absolute path to the site root directory.

    Yields:
        tuple[str, date]: The canonical URL for a page and its last modified
        date.

    Raises:
        OSError: If filesystem traversal or metadata access fails.
    """
    for root, dirs, files in os.walk(root_dir):
        # Prevent os.walk from descending into non-indexable directories.
        dirs[:] = [directory for directory in dirs if directory not in SKIP_DIR]

        for file_name in files:
            if not file_name.endswith(".html"):
                continue
            if any(file_name.endswith(suffix) for suffix in SKIP_SUFFIXES):
                continue
            if file_name in SKIP_FILES:
                continue

            full_path = Path(root) / file_name
            rel_path = full_path.relative_to(root_dir).as_posix()

            if rel_path == "index.html":
                loc = BASE_URL
            else:
                loc = BASE_URL + rel_path

            lastmod = datetime.fromtimestamp(full_path.stat().st_mtime).date()
            yield loc, lastmod


def build_sitemap_xml(root_dir: Path) -> str:
    """Build the sitemap XML document for the current site tree.

    Args:
        root_dir: Absolute path to the site root directory.

    Returns:
        str: Complete sitemap XML content encoded logically as UTF-8 text.

    Raises:
        OSError: If reading the site tree or file metadata fails.
    """
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    for loc, lastmod in iter_sitemap_entries(root_dir):
        lines.extend(
            [
                "  <url>",
                f"    <loc>{loc}</loc>",
                f"    <lastmod>{lastmod}</lastmod>",
                "  </url>",
            ]
        )

    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def write_sitemap(output_path: Path, content: str) -> None:
    """Write sitemap content to disk using a UTF-8 text encoding.

    Args:
        output_path: Absolute path where the sitemap should be written.
        content: Full sitemap XML text to write.

    Returns:
        None

    Raises:
        OSError: If the output file cannot be written.
    """
    with output_path.open("w", encoding="utf-8", newline="\n") as output_file:
        output_file.write(content)


def main() -> int:
    """Generate and save the sitemap file for the public site.

    Args:
        None

    Returns:
        int: Process exit code, where 0 indicates success.

    Raises:
        OSError: If reading site files or writing the sitemap fails.
    """
    sitemap_xml = build_sitemap_xml(ROOT_DIR)
    write_sitemap(OUTPUT_PATH, sitemap_xml)
    print(f"Wrote sitemap to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
