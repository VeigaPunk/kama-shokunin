#!/usr/bin/env python3
"""S01SourcesReopen distinct-case-6 independent re-open check for SOURCES row S515.

Binds the claim to the live page content, not to a self-description:
  * parses the registry row and the round-56 lesson bullet,
  * extracts the URL, anchor section, quoted sentence and declared word count,
  * asserts the sentence occurs verbatim (quote-glyph normalised) inside the
    GIT_CONFIG_COUNT definition of the fetched HTML,
  * asserts the page revision marker named by the row,
  * runs four mutants that must be REJECTED (a check that passes a doctored
    page would be the round-56 C2 vacuous-target failure mode).

exit 0 iff every base check passes AND every mutant is rejected.
"""
import argparse
import hashlib
import html
import re
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
SOURCES = f"{LANE}/corpus/SOURCES.md"
LESSON = f"{LANE}/corpus/lessons/round-56.md"
ANCHOR_ID = "Documentation/git-config.txt-GITCONFIGCOUNT"
EXPECTED_URL = "https://git-scm.com/docs/git-config#" + ANCHOR_ID
WORD_LIMIT = 25

GLYPHS = {"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"', "\u00a0": " "}


def norm(s: str) -> str:
    for a, b in GLYPHS.items():
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def strip_punct(url: str) -> str:
    return url.rstrip(",.;:)")


def row_field(line: str, idx: int) -> str:
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells[idx]


def parse_registry():
    line = None
    with open(SOURCES, encoding="utf-8") as fh:
        for ln in fh:
            if ln.startswith("| S515 |"):
                line = ln
                break
    if line is None:
        raise SystemExit("registry row S515 not found")
    title = row_field(line, 1)
    anchor_cell = row_field(line, 5)
    quote_cell = row_field(line, 6)
    url = strip_punct(re.search(r"https?://\S+", title).group(0))
    anchor = re.search(r"§\S+", anchor_cell).group(0)
    rev = re.search(r"git (\d+\.\d+\.\d+)", anchor_cell)
    quote = re.search(r'"([^"]+)"', quote_cell).group(1)
    declared = re.search(r"\((\d+) words?\)", quote_cell)
    return {
        "url": url,
        "anchor": anchor,
        "revision": rev.group(1) if rev else None,
        "quote": quote,
        "declared_words": int(declared.group(1)) if declared else None,
        "status": row_field(line, 7),
    }


def parse_lesson():
    with open(LESSON, encoding="utf-8") as fh:
        text = fh.read()
    bullet = None
    for ln in text.splitlines():
        if ln.startswith("- **S515"):
            bullet = ln
            break
    if bullet is None:
        raise SystemExit("lesson bullet S515 not found")
    url = strip_punct(re.search(r"https?://\S+", bullet).group(0))
    quote = re.search(r"\u201c(.+?)\u201d", bullet).group(1)
    declared = re.search(r"\((\d+) words?\)", bullet)
    rev = re.search(r"git (\d+\.\d+\.\d+)", bullet)
    return {
        "url": url,
        "quote": quote,
        "declared_words": int(declared.group(1)) if declared else None,
        "revision": rev.group(1) if rev else None,
    }


def dd_text_for_anchor(raw: str):
    """Plain text of the <dd> that immediately follows the anchor's <dt> group."""
    m = re.search(r'id="%s"' % re.escape(ANCHOR_ID), raw)
    if not m:
        return None
    seg = raw[m.start():m.start() + 6000]
    dd = re.search(r"<dd>(.*?)</dd>", seg, re.S)
    if not dd:
        return None
    text = re.sub(r"<[^>]+>", "", dd.group(1))
    return norm(html.unescape(text))


def checks(raw_page: str, base: bool, registry, lesson, label):
    """Return (name, ok, detail) list."""
    page = norm(html.unescape(re.sub(r"<[^>]+>", " ", raw_page)))
    dd = dd_text_for_anchor(raw_page)
    out = []

    anchor_present = 'id="%s"' % ANCHOR_ID in raw_page
    out.append(("anchor_present", anchor_present, f"id={ANCHOR_ID}"))

    dt_ok = bool(re.search(
        r'id="%s"[^>]*>.*?</a>GIT_CONFIG_COUNT\s*</dt>' % re.escape(ANCHOR_ID),
        raw_page, re.S))
    out.append(("dt_names_config_count", dt_ok, "dt text == GIT_CONFIG_COUNT"))

    q = norm(registry["quote"])
    dd_ok = dd is not None and dd.count(q) == 1
    out.append(("quote_in_git_config_count_dd", dd_ok,
                f"occurrences={0 if dd is None else dd.count(q)}"))

    words = len(q.split())
    out.append(("quote_word_count_matches_declared",
                registry["declared_words"] == words,
                f"declared={registry['declared_words']} counted={words}"))
    out.append(("quote_word_count_under_limit", 0 < words <= WORD_LIMIT,
                f"counted={words} limit={WORD_LIMIT}"))

    rev_ok = bool(registry["revision"]) and (
        f"git-config last updated in {registry['revision']}" in page)
    out.append(("revision_marker_present", rev_ok,
                f"marker=git-config last updated in {registry['revision']}"))

    lesson_agrees = norm(lesson["quote"]) == q and lesson["declared_words"] == words
    out.append(("lesson_quote_agrees_with_registry", lesson_agrees,
                f"lesson_words={lesson['declared_words']}"))

    url_ok = registry["url"] == lesson["url"] == EXPECTED_URL
    out.append(("url_matches_expected_anchor", url_ok, registry["url"]))

    if not base:
        # mutating the page must break the binding; report only the binding checks
        return [c for c in out if c[0] in
                ("anchor_present", "dt_names_config_count",
                 "quote_in_git_config_count_dd", "revision_marker_present")]
    return out


def mutate_quote(raw: str) -> str:
    return raw.replace(
        "all environment pairs", "all the environment pairs", 1)


def mutate_order(raw: str) -> str:
    return raw.replace(
        "will be\nadded to the process&#8217;s runtime configuration",
        "added will be to the process&#8217;s runtime configuration", 1)


def blank_dd(raw: str) -> str:
    i = raw.find('id="%s"' % ANCHOR_ID)
    j = raw.find("<dd>", i)
    k = raw.find("</dd>", j)
    return raw[:j] + "<dd>no pairs are processed.</dd>" + raw[k + 5:]


def drop_section(raw: str) -> str:
    i = raw.find('id="%s"' % ANCHOR_ID)
    return raw[:i] + "</dl></div>" + raw[i + 4000:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--label", default="live")
    args = ap.parse_args()

    raw = open(args.html, encoding="utf-8").read()
    sha = hashlib.sha256(open(args.html, "rb").read()).hexdigest()
    registry, lesson = parse_registry(), parse_lesson()

    print(f"label={args.label}")
    print(f"html={args.html}")
    print(f"sha256={sha} bytes={len(raw.encode())}")

    base = checks(raw, True, registry, lesson, args.label)
    for name, ok, detail in base:
        print(f"check={name} ok={ok} detail={detail}")

    mutants = [
        ("mutant_insert_word", mutate_quote(raw)),
        ("mutant_reorder_clause", mutate_order(raw)),
        ("mutant_blank_dd", blank_dd(raw)),
        ("mutant_drop_section", drop_section(raw)),
    ]
    rejected = 0
    for name, page in mutants:
        applied = page != raw
        mc = checks(page, False, registry, lesson, name)
        failed = [n for n, ok, _ in mc if not ok]
        is_red = applied and bool(failed)
        rejected += is_red
        print(f"{name} applied={applied} rejected={is_red} "
              f"failed_checks={','.join(failed) or 'none'}")

    # limit-predicate negative control: a 26-word quote must fail the <=25 check
    padded = norm(registry["quote"]) + " " + " ".join(["pad"] * 8)
    padded_words = len(padded.split())
    limit_red = not (0 < padded_words <= WORD_LIMIT)
    print(f"control_word_limit_26 rejected={limit_red} "
          f"counted={padded_words} limit={WORD_LIMIT}")

    base_ok = all(ok for _, ok, _ in base) and limit_red
    print(f"base_checks_ok={base_ok}")
    print(f"mutants_rejected={rejected}/{len(mutants)}")
    met = base_ok and rejected == len(mutants)
    print(f"met={met}")
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
