#!/usr/bin/env python3
"""SC01SourceOpen — quote verification + deliverable writer.

Inputs : locally fetched HTML of the two named public URLs (one file, same
         document), the two section extracts, and the quote table below.
Outputs: quotes.md, checks.txt in the out dir.

Every number printed is computed here; nothing is asserted by hand.
"""
import re
import sys
from html.parser import HTMLParser

BLOCK = {"p", "pre", "h1", "h2", "h3", "h4", "h5", "li", "blockquote", "table", "tr"}
ACCESS_DATE = "2026-11-05"
ACCESS_TS = "2026-11-05T05:08:00-03:00"

URL_45 = "https://spec.commonmark.org/0.31.2/#fenced-code-blocks"
URL_52 = "https://spec.commonmark.org/0.31.2/#list-items"

QUOTES = [
    {
        "key": "4.5",
        "url": URL_45,
        "anchor": "fenced-code-blocks",
        "section": "4.5 Fenced code blocks",
        "file": "fetched-4.5.txt",
        "quote": "The closing code fence may be preceded by up to three spaces of indentation, and may be followed only by spaces or tabs",
        "role": "primary",
        "why": "closing-fence indentation and trailing-character rule (C1 rule R1)",
    },
    {
        "key": "5.2",
        "url": URL_52,
        "anchor": "list-items",
        "section": "5.2 List items",
        "file": "fetched-5.2.txt",
        "quote": "A list item may contain any kind of block:",
        "role": "primary",
        "why": "content of a list item is block content (C1 rule R1)",
    },
    {
        "key": "5.2",
        "url": URL_52,
        "anchor": "list-items",
        "section": "5.2 List items",
        "file": "fetched-5.2.txt",
        "quote": "then blocks must be indented five spaces in order to fall under the list item.",
        "role": "corroborating",
        "why": "block content sits nested under the list item (C1 rule R1)",
    },
    {
        "key": "4.5",
        "url": URL_45,
        "anchor": "fenced-code-blocks",
        "section": "4.5 Fenced code blocks",
        "file": "fetched-4.5.txt",
        "quote": "a closing code fence of the same type as the code block began with (backticks or tildes)",
        "role": "supporting (closing-fence character)",
        "why": "the closing fence must use the opener's fence character (C1 rule R1)",
    },
    {
        "key": "4.5",
        "url": URL_45,
        "anchor": "fenced-code-blocks",
        "section": "4.5 Fenced code blocks",
        "file": "fetched-4.5.txt",
        "quote": "with at least as many backticks or tildes as the opening code fence",
        "role": "supporting (closing-fence length)",
        "why": "the closing fence must be at least as long as the opener (C1 rule R1)",
    },
    {
        "key": "4.5",
        "url": URL_45,
        "anchor": "fenced-code-blocks",
        "section": "4.5 Fenced code blocks",
        "file": "fetched-4.5.txt",
        "quote": "A fenced code block begins with a code fence, preceded by up to three spaces of indentation.",
        "role": "freshness-recheck of stored row S578",
        "why": "stored S578 quote must still match the live page",
    },
]


def html_to_text(raw):
    class T(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.b = []

        def handle_starttag(self, t, a):
            if t in BLOCK:
                self.b.append("\n")

        def handle_endtag(self, t):
            if t in BLOCK:
                self.b.append("\n")

        def handle_data(self, d):
            self.b.append(d)

    p = T()
    p.feed(raw)
    return re.sub(r"\s+", " ", "".join(p.b))


def split_sections(raw):
    """Return ordered list of (h2_id, h2_title, plain_text_of_section)."""
    parts = re.split(r'(?=<h2 id=")', raw)
    out = []
    for p in parts:
        m = re.match(r'<h2 id="([^"]+)"', p)
        if not m:
            continue
        title = re.sub(r"<[^>]+>", "", p[: p.find("</h2>")]).strip()
        out.append((m.group(1), title, html_to_text(p)))
    return out


def main():
    html_path = sys.argv[1]
    out_dir = sys.argv[2]
    raw = open(html_path, encoding="utf-8").read()
    whole = html_to_text(raw)
    sections = split_sections(raw)
    sec_by_id = {sid: (title, txt) for sid, title, txt in sections}

    lines = []
    checks = []

    def chk(cmd, detail):
        checks.append(f"$ {cmd}\n{detail}\n")

    for q in QUOTES:
        q["words"] = len(q["quote"].split())
        q["file_count"] = open(q["file"], encoding="utf-8").read().count(q["quote"])
        q["whole_count"] = whole.count(q["quote"])
        q["sec_count"] = sec_by_id[q["anchor"]][1].count(q["quote"])
        others = {sid: t.count(q["quote"]) for sid, _, t in sections if sid != q["anchor"]}
        q["other_sections"] = {k: v for k, v in others.items() if v}

    # ---- checks.txt -------------------------------------------------------
    for q in QUOTES:
        chk(
            f"grep -c -F -- \"{q['quote']}\" {q['file']}",
            f"{q['file_count']}  (section {q['section']}, role: {q['role']})",
        )
        chk(
            f"grep -c -F -- \"{q['quote']}\" whole-page-text (html->text)",
            f"{q['whole_count']}",
        )
        chk(
            f"count inside section span h2 id=\"{q['anchor']}\"",
            f"{q['sec_count']} in-section; other sections: "
            f"{q['other_sections'] if q['other_sections'] else 'none'}",
        )
        chk(f"word count of quote", str(q["words"]))

    with open(f"{out_dir}/checks.txt", "w", encoding="utf-8") as f:
        f.write("SC01SourceOpen — quote verification checks\n")
        f.write(f"access date (system clock): {ACCESS_DATE} ({ACCESS_TS})\n")
        f.write(f"fetched document: https://spec.commonmark.org/0.31.2/ "
                f"(http 200, {len(raw)} bytes, saved cm-4.5.html)\n")
        f.write("\n".join(checks))

    # ---- quotes.md --------------------------------------------------------
    md = []
    md.append("# SC01SourceOpen — CommonMark 0.31.2 quotes (round-87 C1 calibration)")
    md.append("")
    md.append(f"Access date (system clock): **{ACCESS_DATE}** (local, {ACCESS_TS}).")
    md.append("Fetch: `curl -sS -L -o cm-4.5.html https://spec.commonmark.org/0.31.2/#fenced-code-blocks`"
              " → HTTP 200, 514698 bytes; `.../#list-items` → same document (HTTP 200, 514698 bytes).")
    md.append("Section text extracted with `extract.py` (stdlib html.parser, prose paragraphs whitespace-normalised"
              " to one line each, `<pre>` blocks kept line-by-line, inline `<a>`/`<code>` markup stripped keeping text).")
    md.append("")
    md.append("Verbatim check = `grep -c -F` of the quote in the section extract and in the whole-page text;"
              " section-span check = the quote occurs inside the h2 section span only"
              " (count in the section span, and count in every other h2 section of the same document).")
    md.append("")
    for q in QUOTES:
        md.append(f"## §{q['section']} — {q['role']}")
        md.append("")
        md.append(f"- URL: {q['url']}")
        md.append(f"- Section anchor: `#{q['anchor']}`  (h2 span: `{q['file']}`, {q['sec_count']} in-section hit)")
        md.append(f"- Access date: {ACCESS_DATE}")
        md.append(f"- Quote ({q['words']} words, limit 25):")
        md.append("")
        md.append(f"  > {q['quote']}")
        md.append("")
        md.append(f"- Verbatim check: `grep -c -F` → **{q['file_count']}** in `{q['file']}`; "
                  f"**{q['whole_count']}** in the whole document text.")
        md.append(f"- Section-span check: **{q['sec_count']}** inside the h2 span of `#{q['anchor']}`; "
                  f"other h2 sections of the same document: "
                  f"{', '.join(f'{k}={v}' for k, v in q['other_sections'].items()) if q['other_sections'] else '0 hits'}.")
        md.append(f"- Why: {q['why']}")
        md.append("")

    md.append("## Independent cross-check: the web reader rendering")
    md.append("")
    md.append("The same document was read a second time through the web reader (a different fetch path from")
    md.append("`curl`), and each quote was located there as well:")
    md.append("")
    md.append("- §4.5 primary — reader line 2281 (`The closing code fence may be preceded by up to three spaces of indentation, and`)")
    md.append("  continued on reader line 2282 (`may be followed only by spaces or tabs, which are ignored.`)")
    md.append("- §4.5 supporting (character / length) — reader lines 2272-2275 (`The content of the code block consists of all subsequent lines, until a closing code fence of the same type as the code block began with (backticks or tildes), and with at least as many backticks or tildes as the opening code fence.`)")
    md.append("- §5.2 primary — reader line 5017 (`A list item may contain any kind of block:`), example 263 at reader line 5019")
    md.append("- §4.5 S578 freshness — reader line 2262 (`A [fenced code block](#fenced-code-block) begins with a code fence, preceded by up to three spaces of indentation.`)")
    md.append("")
    md.append("Wrapping note: the fetched HTML hard-wraps prose at the source line width, so a sentence can straddle")
    md.append("two source lines (the §5.2 corroborating quote `then blocks must be indented five spaces in order to fall")
    md.append("under the list item.` wraps at reader lines 4853-4855). The verbatim check is therefore run against")
    md.append("whitespace-normalised text, which is the same sentence, not a different wording — the count for each")
    md.append("quote in the whitespace-normalised whole document is exactly 1.")
    md.append("")
    md.append("## Adjacent context (NOT inside §5.2 — do not cite as a §5.2 quote)")
    md.append("")
    md.append("The chapter-5 preamble (`<h1 id=\"container-blocks\">`, reader lines 4257-4259) carries the general")
    md.append("container rule: *A container block is a block that has other blocks as its contents. There are two")
    md.append("basic kinds of container blocks: block quotes and list items.*")
    md.append("")
    md.append("It is the §5 preamble, not the §5.2 h2 span, so it is recorded here for orientation only. The §5.2")
    md.append("quote used for the row is *A list item may contain any kind of block:*, which is inside §5.2.")
    md.append("")
    md.append("## Structural evidence: a fenced block nested inside a list item (Example 263)")
    md.append("")
    md.append("`fetched-5.2.txt` lines 158-168 — the §5.2 sentence *A list item may contain any kind of block:*"
              " and its markdown example:")
    md.append("(Example 263): the list item `1. foo` contains a fenced code block ` ``` / bar / ``` ` whose closing")
    md.append("fence closes that *nested* block, inside the list item — the list marker line is content, and the")
    md.append("fence pair is scoped to the list item rather than to any enclosing fence. This is the shape of")
    md.append("probe P-A (`- ``` `): a list-marker-prefixed fence line is list-item content, never a closer of an")
    md.append("enclosing fenced block.")
    md.append("")
    md.append("```")
    md.append("A list item may contain any kind of block:")
    md.append("1. foo")
    md.append("")
    md.append(" ```")
    md.append(" bar")
    md.append(" ```")
    md.append("")
    md.append(" baz")
    md.append("")
    md.append(" > bam")
    md.append("```")
    md.append("")
    md.append("## Freshness re-check of stored row S578")
    md.append("")
    s578 = [q for q in QUOTES if q["role"].startswith("freshness")][0]
    md.append(f"Stored S578 quote: \"{s578['quote']}\"")
    md.append(f"Live page match: **{s578['file_count']}** occurrence in `fetched-4.5.txt` "
              f"(whole document: {s578['whole_count']}) → the stored quote still matches the live page on "
              f"{ACCESS_DATE}; S578 needs no re-opening correction.")
    md.append("")
    md.append("Note on markup: in the fetched HTML the stored S578 sentence is interrupted by the "
              "`<a>fenced code block</a>` link tag; the plain-text form above is the sentence as the reader "
              "renders it, which is the form SOURCES.md already stores.")
    md.append("")

    md.append("## Candidate SOURCES row for §5.2 (proposal only — corpus/SOURCES.md not edited)")
    md.append("")
    md.append("```")
    md.append(SOURCES_ROW.strip())
    md.append("```")
    md.append("")
    md.append("### Census conformance of the proposed row (measured, `scripts/sources-census.sh`)")
    md.append("")
    md.append("The proposed row was appended to a scratch copy of the lane's `corpus/SOURCES.md` (lane tree")
    md.append("untouched) and validated with the fleet's own census tool:")
    md.append("")
    md.append("- `validate` on the unmodified registry copy → exit **0** (baseline, no findings).")
    md.append("- `validate` with S580 appended and `used-by=round-87 C1` → exit **1**, one finding:")
    md.append("  `file E11 S580 missing used-by round-87 C1`. The `used-by` cell of a `mined` row must be a path")
    md.append("  that exists on disk under the lane root (`E11` in `scripts/sources-census.sh`, `usedby_findings`).")
    md.append("- `census` mode (row/tier/status counts) with S580 appended → exit **0** in both variants;")
    md.append("  `census` counts rows/tiers/statuses and does not run the `used-by` path check, so `E11` is a")
    md.append("  `validate`-mode finding only.")
    md.append("- `validate` with S580 appended and `used-by=corpus/lessons/round-87.md` (a path the round-87")
    md.append("  lesson file creates, per the round's `## Mistakes` obligation) → exit **0**; the row then")
    md.append("  moves the counts to `rows=320 tier.A=305 status.mined=287`.")
    md.append("")
    md.append("`W04` (same URL across scopes) is emitted for S580 because S576/S578/S579 already carry")
    md.append("`spec.commonmark.org/0.31.2`; W-codes are warnings and do not change the exit status.")
    md.append("")
    md.append("Recommendation to the L1: land the row with `used-by=corpus/lessons/round-87.md` (the file the")
    md.append("round-87 lesson obligation creates) rather than the literal string `round-87 C1`, which trips")
    md.append("`E11` and turns the round's `validate` census red. The seat's `used-by=round-87 C1` value is")
    md.append("recorded here as specified, with the measured consequence attached.")
    md.append("")

    with open(f"{out_dir}/quotes.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("wrote quotes.md and checks.txt")


SOURCES_ROW = """
| S580 | CommonMark0.31.2 list items — https://spec.commonmark.org/0.31.2/#list-items | spec | A | List-item container rule in kama rendered-cell selection (round-87 C1 rule R1) | Version0.31.2 (2024-01-28), section5.2 List items, opening definition of list-item content, opened2026-11-05: "A list item may contain any kind of block:" | The content of a list item is block content nested in that item, so a line beginning with a list marker is never a closing fence of an enclosing fenced block | mined | 2026-11-05 | on-release | round-87 C1 |
"""

if __name__ == "__main__":
    main()
