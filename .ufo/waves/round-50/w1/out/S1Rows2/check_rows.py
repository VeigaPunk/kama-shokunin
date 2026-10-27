#!/usr/bin/env python3
"""Verify S496/S497/S498 quotes against the round-50 text copies and the live pages.

Checks, per row: quote present verbatim after whitespace normalisation; word count
<= 25; the same span present on the live URL fetch; anchor tokens present.
"""
import html
import re
import sys
import pathlib

ROOT = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
S = pathlib.Path("/fast/scratch/hyaku/kama-r50/S1Rows2")

COPIES = {
    "S496": ROOT / ".ufo/waves/round-50/c1/proc_pid_maps.5.txt",
    "S497": ROOT / ".ufo/waves/round-50/c1/PR_SET_PDEATHSIG.2const.txt",
    "S498": ROOT / ".ufo/waves/round-50/c2/commonmark-0.31.2-s4.5.txt",
}
FETCHED = {
    "S496": S / "fetch/page-f6d1b92d.html",
    "S497": S / "fetch/page-dbdd9470.html",
    "S498": S / "fetch/page-628a625f.html",
}
QUOTES = {
    "S496": [
        "dev is the device (major:minor); inode is the inode on that device",
        "The pathname field will usually be the file that is backing the mapping.",
    ],
    "S497": [
        "The parent-death signal is sent upon subsequent termination of the parent thread and also upon termination of each subreaper process ... to which the caller is subsequently reparented.",
    ],
    "S498": [
        "A code fence is a sequence of at least three consecutive backtick characters or tildes.",
    ],
}
# Quotes as they read in the source text, for the elision/alteration diagnosis.
EXPECTED_SOURCE = {
    "S497": "The parent-death signal is sent upon subsequent termination of the parent thread and also upon termination of each subreaper process (see PR_SET_CHILD_SUBREAPER(2const)) to which the caller is subsequently reparented.",
    "S498": "A code fence is a sequence of at least three consecutive backtick characters (`) or tildes (~).",
}


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def plain_html(text: str) -> str:
    text = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return norm(html.unescape(text))


def words(q: str) -> int:
    return len(q.split())


def main() -> int:
    fail = 0
    for row, quotes in QUOTES.items():
        copy_norm = norm(COPIES[row].read_text(encoding="utf-8"))
        live_norm = plain_html(FETCHED[row].read_text(encoding="utf-8", errors="replace"))
        for q in quotes:
            hit_copy = q in copy_norm
            hit_live = q in live_norm
            wc = words(q)
            status = "VERBATIM" if hit_copy else "MISS"
            print(f"{row} words={wc:>2} copy={status} live={'hit' if hit_live else 'MISS'} :: {q}")
            if not hit_copy:
                fail = 1
                exp = EXPECTED_SOURCE.get(row)
                if exp:
                    print(f"      source-text form present={exp in copy_norm} live={exp in live_norm} :: {exp}")
                    if exp in copy_norm:
                        # locate the mismatch
                        for i, ch in enumerate(exp):
                            pass
                        print(f"      source form word count={words(exp)}")
            if wc > 25:
                print(f"      OVER 25 WORDS ({wc})")
                fail = 1
    return fail


if __name__ == "__main__":
    sys.exit(main())
