#!/usr/bin/env python3
"""Re-derive the SCR02SourceRow quotes from the retained pytest exit-codes bytes.

Usage: python3 verify-quote.py [retained.html]
Default path resolves next to this file: source/pytest-exit-codes.html.

Prints one line per quote: MATCH|MISS <n> words: <quote>
Exits 0 only if the retained bytes hash to the recorded sha256 and every quote
is found byte-exact after HTML tag stripping (tags removed, whitespace collapsed).
"""
import hashlib
import html
import os
import re
import sys

EXPECTED_SHA = "a403306a1d763fc8123749544905dd64e8e0cfa5ed46a416679001c3142e3977"
QUOTES = [
    "Exit code 5: No tests were collected",
    "Exit code 0: All tests were collected and passed successfully",
    "The exit codes being a part of the public API",
]


def strip_tags(raw: str) -> str:
    text = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", raw)
    text = re.sub(r"(?s)<!--.*?-->", " ", text)
    text = re.sub(r"(?s)<[^>]+>", "", text)
    return re.sub(r"\s+", " ", html.unescape(text))


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "source", "pytest-exit-codes.html")
    raw = open(path, "rb").read()
    digest = hashlib.sha256(raw).hexdigest()
    print(f"PATH {path}")
    print(f"SHA256 {digest}")
    if digest != EXPECTED_SHA:
        print(f"SHA256_MISMATCH expected {EXPECTED_SHA}")
        return 1
    text = strip_tags(raw.decode("utf-8"))
    failed = 0
    for quote in QUOTES:
        words = len(quote.split())
        if words > 25:
            print(f"TOO_LONG {words} words: {quote}")
            failed += 1
        if quote in text:
            print(f"MATCH {words} words: {quote}")
        else:
            print(f"MISS  {words} words: {quote}")
            failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
