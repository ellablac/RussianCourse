#!/usr/bin/env python3
"""
Build structured vocabulary records from a word list.

Reads a list of Russian word forms (default: assets/json/vocabulary_clean.json),
looks up each word via OpenRussian, and writes/extends
assets/json/vocabulary_words.json with a structured record for each word.
If the output file exists, it is read first and de-duplicated before writing.
"""

from __future__ import annotations

import argparse
import json
import os
import unicodedata
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

API_BASE = "https://api.openrussian.org"
USER_AGENT = "RussianCourse/1.0 (+local)"
DEFAULT_TIMEOUT = 12

COMBINING_ACUTE = "\u0301"
STRESS_SYMBOLS = {"'", "\u2019", "`", "\u00b4", "\u02c8"}
VOWELS = set("аеёиоуыэюяАЕЁИОУЫЭЮЯ")


def _strip_stress(text: str) -> str:
    """Remove stress marks and combining characters from a string.

    Args:
        text: Input string that may include stress marks or combining accents.

    Returns:
        Normalized string with stress marks and combining characters removed.
    """
    if not text:
        return ""
    out: List[str] = []
    for ch in unicodedata.normalize("NFD", text):
        if unicodedata.combining(ch):
            continue
        if ch in STRESS_SYMBOLS:
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


def _apply_stress_marks(text: str) -> str:
    """Convert apostrophe-style stress marks to combining accents.

    Args:
        text: Input word with stress markers such as apostrophes.

    Returns:
        Word with stress rendered using combining acute accents.
    """
    if not text:
        return ""
    out: List[str] = []
    last_vowel_index: Optional[int] = None

    for ch in text:
        if ch in STRESS_SYMBOLS:
            if last_vowel_index is not None:
                has_accent = (
                    last_vowel_index + 1 < len(out)
                    and out[last_vowel_index + 1] == COMBINING_ACUTE
                )
                if not has_accent:
                    out.insert(last_vowel_index + 1, COMBINING_ACUTE)
            continue

        out.append(ch)
        if ch in VOWELS:
            last_vowel_index = len(out) - 1

    return "".join(out)


def _flatten_tls(tls: Any) -> List[str]:
    """Flatten translation lists from OpenRussian into a list of strings.

    Args:
        tls: Raw translation list structure from the API.

    Returns:
        Flat list of translation strings.
    """
    out: List[str] = []
    if isinstance(tls, list):
        for item in tls:
            if isinstance(item, list):
                out.extend([x for x in item if isinstance(x, str)])
            elif isinstance(item, str):
                out.append(item)
    return out


def _pick_entry(words: Any, query: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Pick the best matching entry for a query from suggestions.

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


def fetch_base_info(bare: str) -> Tuple[Optional[int], Optional[str]]:
    """Fetch rank and level for a base form from OpenRussian.

    Args:
        bare: Stress-stripped base form.

    Returns:
        Tuple of (rank, level), with None values if not found.
    """
    url = f"{API_BASE}/api/words?bare={urllib.parse.quote(bare)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
        raw = json.load(resp)

    result = raw.get("result") if isinstance(raw, dict) else None
    words = result.get("words") if isinstance(result, dict) else None
    if not isinstance(words, list) or not words:
        return None, None

    chosen = None
    for item in words:
        if not isinstance(item, dict):
            continue
        if item.get("bare") == bare or item.get("word") == bare or item.get("ru") == bare:
            chosen = item
            break
    if not chosen:
        chosen = words[0] if isinstance(words[0], dict) else None
    if not chosen:
        return None, None

    rank = chosen.get("rank")
    level = chosen.get("level")
    if isinstance(rank, str) and rank.isdigit():
        rank = int(rank)
    return rank if isinstance(rank, int) else None, level if isinstance(level, str) else None


def _extract_entry_data(query: str, raw: Any) -> Dict[str, Any]:
    """Extract data from a suggestions response.

    Args:
        query: Original query word.
        raw: Parsed JSON response from the suggestions endpoint.

    Returns:
        Dict with pos, translation, example_ru, example_en.
    """
    result = raw.get("result") if isinstance(raw, dict) else None
    if not isinstance(result, dict):
        return {
            "pos": None,
            "translation": [],
            "example_ru": None,
            "example_en": None,
        }

    entry, _matched = _pick_entry(result.get("words"), query)
    word_block = entry.get("word") if isinstance(entry, dict) else {}

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
        "pos": pos,
        "translation": translations,
        "example_ru": example_ru,
        "example_en": example_en,
    }


def _read_words(path: str) -> List[str]:
    """Read words from a JSON or text file.

    Args:
        path: Path to a JSON file or a newline-delimited text file.

    Returns:
        List of words from the file.
    """
    if path.lower().endswith(".json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"Failed to read JSON: {path} ({exc})") from exc

        if isinstance(data, dict) and isinstance(data.get("words"), list):
            return [w for w in data["words"] if isinstance(w, str) and w.strip()]
        if isinstance(data, list):
            return [w for w in data if isinstance(w, str) and w.strip()]
        raise SystemExit(f"Unexpected JSON structure in {path}")

    words: List[str] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip()
                if word:
                    words.append(word)
    except OSError as exc:
        raise SystemExit(f"Failed to read file: {path} ({exc})") from exc
    return words


def _read_existing_output(path: str) -> List[Dict[str, Any]]:
    """Read existing output records if present.

    Args:
        path: Output file path.

    Returns:
        List of existing records.
    """
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Failed to read existing output: {path} ({exc})") from exc

    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict) and isinstance(data.get("results"), list):
        return [item for item in data["results"] if isinstance(item, dict)]
    raise SystemExit(f"Unexpected output structure in {path}")


def _existing_keys(records: List[Dict[str, Any]]) -> set[str]:
    """Build a set of normalized keys for existing records.

    Args:
        records: Existing records.

    Returns:
        Set of normalized word keys.
    """
    keys: set[str] = set()
    for item in records:
        for field in ("word", "word_stressed", "word_stressed_2"):
            val = item.get(field)
            if isinstance(val, str) and val.strip():
                keys.add(_normalize_query(val))
                break
    return keys


def main() -> None:
    """Run the CLI workflow."""
    parser = argparse.ArgumentParser(
        description="Build structured vocabulary records via OpenRussian."
    )
    parser.add_argument(
        "--in",
        dest="infile",
        default="assets/json/vocabulary_clean.json",
        help="Input word list (default: assets/json/vocabulary_clean.json).",
    )
    parser.add_argument(
        "--out",
        dest="outfile",
        default="assets/json/vocabulary_words.json",
        help="Output JSON path (default: assets/json/vocabulary_words.json).",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    args = parser.parse_args()

    targets = _read_words(args.infile)
    if not targets:
        raise SystemExit("No words found in input.")

    existing = _read_existing_output(args.outfile)
    seen_keys = _existing_keys(existing)
    records = list(existing)

    print(
        f"Loaded {len(existing)} existing record(s). Processing {len(targets)} input word(s)."
    )

    for word in targets:
        key = _normalize_query(word)
        if key in seen_keys:
            continue

        try:
            raw = fetch_suggestions(word)
        except Exception as exc:
            print(f"error: {word} ({exc})")
            continue

        data = _extract_entry_data(word, raw)
        bare = _normalize_query(word)

        rank = None
        level = None
        try:
            rank, level = fetch_base_info(bare)
        except Exception as exc:
            print(f"warn: {word} (rank/level lookup failed: {exc})")

        record = {
            "word": _strip_stress(word),
            "word_stressed": _apply_stress_marks(word),
            "word_stressed_2": word,
            "pos": data.get("pos"),
            "translation": data.get("translation", []),
            "rank": rank,
            "level": level,
            "example_ru": data.get("example_ru"),
            "example_en": data.get("example_en"),
            "source": "openrussian.org suggestions",
        }

        records.append(record)
        seen_keys.add(key)

    records.sort(
        key=lambda item: (
            item.get("rank") is None,
            item.get("rank") if isinstance(item.get("rank"), int) else 10**9,
            item.get("word") or "",
        )
    )

    try:
        with open(args.outfile, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2 if args.pretty else None)
    except OSError as exc:
        raise SystemExit(f"Failed to write output: {args.outfile} ({exc})") from exc

    print(f"Wrote {len(records)} record(s) to {args.outfile}")


if __name__ == "__main__":
    main()
