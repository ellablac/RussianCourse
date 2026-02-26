#!/usr/bin/env python3
"""
Clean vocabulary list via OpenRussian.

Reads a list of Russian word forms, looks up each word via the OpenRussian
suggestions API, extracts the base form, de-duplicates, and writes the
resulting list to JSON.

Usage:
  python utilities/clean_vocabulary.py --in assets/json/vocabulary.json
  python utilities/clean_vocabulary.py word1 word2 --out assets/json/vocabulary_clean.json
"""

from __future__ import annotations

import argparse
import json
import unicodedata
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

API_BASE = "https://api.openrussian.org"
USER_AGENT = "RussianCourse/1.0 (+local)"
DEFAULT_TIMEOUT = 12


def _strip_stress(text: str) -> str:
    """Remove stress marks and combining characters from a string.

    Args:
        text: Input string that may include stress marks or combining accents.

    Returns:
        Normalized string with stress marks and combining characters removed.
    """
    if not text:
        return ""
    stress_chars = {"'", "\u2019", "`", "\u00b4", "\u02c8"}
    out: List[str] = []
    for ch in unicodedata.normalize("NFD", text):
        if unicodedata.combining(ch):
            continue
        if ch in stress_chars:
            continue
        out.append(ch)
    return "".join(out)


def _normalize_query(text: str) -> str:
    """Normalize a word for matching and de-duplication.

    Args:
        text: Input word.

    Returns:
        Lowercased, stress-stripped form of the word.
    """
    return _strip_stress(text).lower()


def _pick_entry(words: Any, query: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Pick the best matching entry for the query from suggestions.

    Args:
        words: Raw "words" list from the OpenRussian suggestions response.
        query: Original query word.

    Returns:
        A tuple of (entry, matched_form), or (None, None) if not found.
    """
    if not isinstance(words, list) or not words:
        return None, None

    q_norm = _normalize_query(query)
    for entry in words:
        if not isinstance(entry, dict):
            continue
        word_ru = (entry.get("word") or {}).get("ru")
        forms = entry.get("forms") if isinstance(entry.get("forms"), list) else []
        for form in forms:
            if isinstance(form, dict) and "ru" in form:
                form_ru = form["ru"]
                if _normalize_query(form_ru) == q_norm:
                    return entry, form_ru
        if isinstance(word_ru, str) and _normalize_query(word_ru) == q_norm:
            return entry, word_ru

    entry0 = words[0] if isinstance(words[0], dict) else None
    return entry0, None


def fetch_suggestions(word: str) -> Any:
    """Fetch suggestions for a word from OpenRussian.

    Args:
        word: Word to query.

    Returns:
        Parsed JSON response from the suggestions endpoint.
    """
    url = f"{API_BASE}/suggestions?q={urllib.parse.quote(word)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
        return json.load(resp)


def _extract_base_form(query: str, raw: Any) -> Optional[str]:
    """Extract the base form from an OpenRussian suggestions response.

    Args:
        query: Original query word.
        raw: Parsed JSON response from the suggestions endpoint.

    Returns:
        Base form as a string, or None if it cannot be determined.
    """
    result = raw.get("result") if isinstance(raw, dict) else None
    if not isinstance(result, dict):
        return None

    entry, _matched = _pick_entry(result.get("words"), query)
    if not entry or not isinstance(entry, dict):
        return None

    word_block = entry.get("word") if isinstance(entry.get("word"), dict) else {}
    base_form = None
    if isinstance(word_block, dict):
        base_form = word_block.get("ru") or word_block.get("bare")

    if not base_form:
        for key in ("ru", "word", "bare"):
            val = entry.get(key)
            if isinstance(val, str):
                base_form = val
                break

    return base_form if isinstance(base_form, str) and base_form.strip() else None


def _read_words(path: str) -> List[str]:
    """Read words from a JSON or text file.

    Args:
        path: Path to a JSON file or a newline-delimited text file.

    Returns:
        List of words from the file.
    """
    if path.lower().endswith(".json"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
        if isinstance(data, dict) and isinstance(data.get("words"), list):
            return [w for w in data["words"] if isinstance(w, str) and w.strip()]
        if isinstance(data, list):
            return [w for w in data if isinstance(w, str) and w.strip()]

    words: List[str] = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            word = line.strip()
            if word:
                words.append(word)
    return words


def main() -> None:
    """Run the CLI workflow."""
    parser = argparse.ArgumentParser(
        description="Extract base forms via OpenRussian suggestions API."
    )
    parser.add_argument("words", nargs="*", help="Word(s) to look up.")
    parser.add_argument("--in", dest="infile", help="Path to a file of words.")
    parser.add_argument(
        "--out",
        default="assets/json/vocabulary_clean.json",
        help="Output JSON path (default: assets/json/vocabulary_clean.json).",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    args = parser.parse_args()

    targets: List[str] = []
    if args.infile:
        targets.extend(_read_words(args.infile))
    targets.extend(args.words)

    if not targets:
        parser.error("Provide at least one word or --in file.")

    cleaned: List[str] = []
    seen_bare: set[str] = set()

    for word in targets:
        try:
            raw = fetch_suggestions(word)
        except Exception as exc:
            print(f"error: {word} ({exc})")
            continue

        base_form = _extract_base_form(word, raw)
        if not base_form:
            print(f"reject: {word} (no base form)")
            continue

        base_norm = _normalize_query(base_form)
        if base_norm in seen_bare:
            continue

        cleaned.append(base_form)
        seen_bare.add(base_norm)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2 if args.pretty else None)

    print(f"Wrote {len(cleaned)} base word(s) to {args.out}")


if __name__ == "__main__":
    main()
