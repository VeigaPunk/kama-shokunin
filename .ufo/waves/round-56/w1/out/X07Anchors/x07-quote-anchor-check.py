#!/usr/bin/env python3
"""X07Anchors bounded test, round 56.

Two mandatory checks, both read-only:
  A. the S512 quote written in corpus/lessons/round-56.md occurs in the opened
     snapshot .ufo/waves/round-56/sources/rtld-audit.7.html (HTML tags stripped,
     entities decoded, whitespace collapsed), inside the DESCRIPTION section;
  B. that lesson quote's word count is <= 25.

Secondary observation (not part of the bound): the lesson's declared
"(N words)" equals the measured count.

Negative controls prove the test can fail: deleting a token from the quote must
make the occurrence check fail, and a 26-word span must be rejected by the bound.

Exit 0 only if A and B and every negative control behave as required.
"""
import html
import re
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
LESSON = LANE / "corpus/lessons/round-56.md"
SNAPSHOT = LANE / ".ufo/waves/round-56/sources/rtld-audit.7.html"
MAX_WORDS = 25

TAG_RE = re.compile(r"<[^>]*>")
WS_RE = re.compile(r"\s+")


def normalize(text: str) -> str:
    return WS_RE.sub(" ", text).strip()


def snapshot_text(raw: str) -> str:
    """Strip tags, decode entities, collapse whitespace; keep <pre> text flow."""
    return normalize(html.unescape(TAG_RE.sub("", raw)))


def words(text: str) -> list[str]:
    return text.split()


def lesson_quote(lesson: str) -> tuple[str, int | None]:
    """First curly-quoted span of the S512 bullet, plus its declared word count."""
    line = next(
        (ln for ln in lesson.splitlines() if ln.lstrip().startswith("- **S512")),
        None,
    )
    if line is None:
        raise SystemExit("unable to locate the S512 bullet in the lesson")
    m = re.search(r"\u201c(.+?)\u201d", line)
    if not m:
        raise SystemExit("S512 bullet carries no U+201C..U+201D quote")
    declared = re.search(r"\((\d+) words\)", line)
    return m.group(1), int(declared.group(1)) if declared else None


def section_of(raw: str, needle: str) -> str:
    """Name of the last <h2> heading at or before the located quote.

    The needle must be a tag-free substring of the raw snapshot, so the position
    is not shifted by markup inside the quoted span.
    """
    pos = raw.find(needle)
    if pos < 0:
        return "<not found>"
    headings = [(m.start(), normalize(html.unescape(TAG_RE.sub("", m.group(1)))))
                for m in re.finditer(r"<h2>(.*?)</h2>", raw, re.S)]
    current = "<none>"
    for start, name in headings:
        if start <= pos:
            current = name
        else:
            break
    return current


def main() -> int:
    lesson_raw = LESSON.read_text(encoding="utf-8")
    snap_raw = SNAPSHOT.read_text(encoding="utf-8")
    snap = snapshot_text(snap_raw)
    quote, declared = lesson_quote(lesson_raw)

    failures: list[str] = []

    # A: occurrence in the opened snapshot.
    hits = snap.count(quote)
    # Tag-free raw anchor: the quote is interrupted by </b> after LD_AUDIT, so
    # the full quote is not a raw substring; this tail is.
    section = section_of(snap_raw, "must be defined to contain a colon-separated list of")
    print(f"A1 quote_occurrences={hits} section={section!r}")
    if hits < 1:
        failures.append("A1 quote absent from snapshot")
    if hits and "DESCRIPTION" not in section:
        failures.append(f"A1 quote outside DESCRIPTION (section={section!r})")

    # B: word bound on the lesson's quote.
    wc = len(words(quote))
    print(f"B1 quote_words={wc} bound={MAX_WORDS} ok={wc <= MAX_WORDS}")
    if wc > MAX_WORDS:
        failures.append(f"B1 quote is {wc} words > {MAX_WORDS}")

    # Secondary observation, reported only.
    print(f"O1 declared_words={declared} measured_words={wc} "
          f"consistent={declared == wc}")

    # Negative controls: the checks must be able to fail.
    drop = quote.replace("LD_AUDIT", "LD_AUDITX", 1)
    neg_hits = snap.count(drop)
    print(f"N1 mutated_quote_occurrences={neg_hits} expected=0")
    if neg_hits != 0:
        failures.append("N1 mutated quote still found; occurrence check is vacuous")

    long_quote = quote + " " + " ".join(f"w{i}" for i in range(11))
    assert len(words(long_quote)) == 26, len(words(long_quote))
    print(f"N2 long_span_words={len(words(long_quote))} "
          f"bound_rejects={len(words(long_quote)) > MAX_WORDS}")
    if len(words(long_quote)) <= MAX_WORDS:
        failures.append("N2 word counter failed to reject a >25-word span")

    if failures:
        print("RESULT=FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("RESULT=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
