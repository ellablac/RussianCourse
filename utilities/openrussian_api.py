#!/usr/bin/env python3
"""
OpenRussian lookup CLI.
Usage:
  python utilities/openrussian_api.py word
  Multiple words
  python utilities/openrussian_api.py word1 word2 --out assets/json/openrussian_lookup.json
  From a file (one word per line)
  python utilities/openrussian_api.py --in assets/json/vocabulary.txt --out assets/json/openrussian_lookup.json
  To see raw API response in browser: https://api.openrussian.org/suggestions?q=мама
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
    if not text:
        return ""
    stress_chars = {"'", "\u2019", "`", "\u00b4", "\u02c8"}
    out = []
    for ch in unicodedata.normalize("NFD", text):
        if unicodedata.combining(ch):
            continue
        if ch in stress_chars:
            continue
        out.append(ch)
    return "".join(out)


def _normalize_query(text: str) -> str:
    return _strip_stress(text).lower()


def _flatten_tls(tls: Any) -> List[str]:
    out: List[str] = []
    if isinstance(tls, list):
        for item in tls:
            if isinstance(item, list):
                out.extend([x for x in item if isinstance(x, str)])
            elif isinstance(item, str):
                out.append(item)
    return out


def _pick_entry(words: Any, query: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    if not isinstance(words, list) or not words:
        return None, None

    q_norm = _normalize_query(query)
    for entry in words:
        if not isinstance(entry, dict):
            continue
        word_ru = (entry.get("word") or {}).get("ru")
        forms = entry.get("forms") if isinstance(entry.get("forms"), list) else []
        for f in forms:
            if isinstance(f, dict) and "ru" in f:
                form_ru = f["ru"]
                if _normalize_query(form_ru) == q_norm:
                    return entry, form_ru
        if isinstance(word_ru, str) and _normalize_query(word_ru) == q_norm:
            return entry, word_ru

    entry0 = words[0] if isinstance(words[0], dict) else None
    return entry0, None


def fetch_suggestions(word: str) -> Any:
    url = f"{API_BASE}/suggestions?q={urllib.parse.quote(word)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
        return json.load(resp)


def build_response(query: str, raw: Any) -> Dict[str, Any]:
    result = raw.get("result") if isinstance(raw, dict) else None
    if not isinstance(result, dict):
        return {
            "query": query,
            "found": False,
            "word": None,
            "word_stressed": None,
            "base_form": None,
            "pos": None,
            "translation": None,
            "example_ru": None,
            "example_en": None,
            "source": "openrussian.org suggestions",
        }

    term = result.get("term")
    entry, stressed_form = _pick_entry(result.get("words"), query)
    if not entry:
        return {
            "query": query,
            "found": False,
            "word": term,
            "word_stressed": None,
            "base_form": None,
            "pos": None,
            "translation": None,
            "example_ru": None,
            "example_en": None,
            "source": "openrussian.org suggestions",
        }

    word_block = entry.get("word") if isinstance(entry, dict) else {}
    base_form = word_block.get("ru") if isinstance(word_block, dict) else None
    pos = word_block.get("type") if isinstance(word_block, dict) else None
    translations = _flatten_tls(word_block.get("tls")) if isinstance(word_block, dict) else []

    example_ru = None
    example_en = None
    sentences = result.get("sentences")
    if isinstance(sentences, list) and sentences:
        ex = sentences[0] if isinstance(sentences[0], dict) else None
        if ex:
            example_ru = ex.get("ru")
            example_en = ex.get("tl")

    return {
        "query": query,
        "found": True,
        "word": term,
        "word_stressed": stressed_form or base_form or term,
        "base_form": base_form,
        "pos": pos,
        "translation": translations,
        "example_ru": example_ru,
        "example_en": example_en,
        "source": "openrussian.org suggestions",
    }


def _read_words(path: str) -> List[str]:
    words: List[str] = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.strip()
            if w:
                words.append(w)
    return words


def main() -> None:
    parser = argparse.ArgumentParser(description="Lookup words via OpenRussian suggestions API.")
    parser.add_argument("words", nargs="*", help="Word(s) to look up.")
    parser.add_argument("--in", dest="infile", help="Path to a file with one word per line.")
    parser.add_argument(
        "--out",
        default="assets/json/openrussian_lookup.json",
        help="Output JSON path (default: assets/json/openrussian_lookup.json).",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    args = parser.parse_args()

    targets: List[str] = []
    if args.infile:
        targets.extend(_read_words(args.infile))
    targets.extend(args.words)

    if not targets:
        parser.error("Provide at least one word or --in file.")

    results: List[Dict[str, Any]] = []
    for w in targets:
        raw = fetch_suggestions(w)
        results.append(build_response(w, raw))

    payload = {"count": len(results), "results": results}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2 if args.pretty else None)

    print(f"Wrote {len(results)} result(s) to {args.out}")


if __name__ == "__main__":
    main()
