#!/usr/bin/env python3
"""KamaR21.SrcReproducibleBuildsArchive-6 - S066 draft verification (stdlib only).

Reads the bytes saved under fetched/ beside this file and checks:
  1. each saved Salsa source blob has the git blob id the Salsa API reported
     (git's blob hash: sha1 of b"blob <len>\\0" + bytes);
  2. each candidate quote is a verbatim run of the rendered live HTML and of the
     source markdown blob (markup and whitespace normalised; backticks and link
     syntax removed), is at most 25 words, and sits under the heading named in
     both the rendered page and the source.
The source blob's Jekyll front matter `title:` names the page-title section.
Prints the sha256 of each saved live page for the record.
Exit 0: all checks pass. Exit 1: a check fails. Exit 2: an input cannot be read.
"""
import hashlib
import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
FETCHED = HERE / "fetched"

# git blob ids from GET repository/tree?path=_docs on
# salsa.debian.org reproducible-builds/reproducible-website (branch master)
BLOB_IDS = {
    "blob-archives.md": "81587c1c4308b6c30655c8da9208869d690fd963",       # _docs/archives.md
    "blob-stable_inputs.md": "97d60745b113a977b3b3e2d742fe9ce85043564e",  # _docs/stable_inputs.md
    "blob-stable_outputs.md": "a8f345b1241b3c92c785d60496c3da7adeb1b15c", # _docs/stable_outputs.md
}
PAGE_SOURCE = {
    "archives.html": "blob-archives.md",
    "stable-inputs.html": "blob-stable_inputs.md",
    "stable-outputs.html": "blob-stable_outputs.md",
}
# (live page, quote as rendered, heading the row cites)
QUOTES = [
    ("stable-inputs.html",
     "When sorting inputs, one must ensure that the sorting order is not affected by the system locale settings.",
     "Stable order for inputs"),
    ("stable-inputs.html",
     "Most filesystems do not guarantee that listing files in a directory always results in the same order.",
     "Stable order for inputs"),
    ("stable-inputs.html",
     "The locale used to sort files must be specified to avoid any surprises:",
     "Example: tar"),
    ("archives.html",
     "most archive formats will read their content in the order returned by the filesystem",
     "File ordering"),
    ("archives.html",
     "Care must be taken to ensure that sort is called in the context of the C locale to avoid any surprises related to collation order.",
     "File ordering"),
    ("archives.html",
     "With version 1.28, GNU Tar has gained the --sort=name option which will sort filenames in a locale independent manner:",
     "File ordering"),
    ("stable-outputs.html",
     "Beware that the locale settings might affect the output of some sorting functions or the sort command.",
     "General"),
]

HEADING_RE = re.compile(
    r"(?m)^(?:#{1,6}[ \t]+(?P<atx>.+?)[ \t]*$"
    r"|(?P<setext>[^\n]*\S[^\n]*)\n(?:-{3,}|={3,})[ \t]*$)")


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def html_text(raw):
    raw = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return norm(html.unescape(raw))


def md_text(raw):
    raw = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", raw)
    raw = raw.replace("`", "")
    return norm(raw)


def html_sections(raw):
    parts = re.split(r"(?is)(<h[1-6][^>]*>.*?</h[1-6]>)", raw)
    secs = [("(preamble)", parts[0])]
    for i in range(1, len(parts), 2):
        body = parts[i + 1] if i + 1 < len(parts) else ""
        secs.append((html_text(parts[i]), body))
    return secs


def md_sections(raw):
    title = None
    fm = re.match(r"(?s)\A---\n(.*?)\n---\n", raw)
    if fm:
        t = re.search(r"(?m)^title:\s*(.+?)\s*$", fm.group(1))
        title = t.group(1) if t else None
        raw = raw[fm.end():]
    raw = re.sub(r"(?ms)^\{%\s*highlight\b.*?^\{%\s*endhighlight\s*%\}[ \t]*$", "", raw)
    raw = re.sub(r"(?ms)^```.*?^```[ \t]*$", "", raw)
    matches = list(HEADING_RE.finditer(raw))
    secs = [(title or "(preamble)", raw[:matches[0].start()] if matches else raw)]
    for i, m in enumerate(matches):
        name = (m.group("atx") or m.group("setext")).strip()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        secs.append((name, raw[m.end():end]))
    return secs


def main():
    try:
        blobs = {n: (FETCHED / n).read_bytes() for n in BLOB_IDS}
        pages = {n: (FETCHED / n).read_bytes() for n in PAGE_SOURCE}
    except OSError as e:
        print(f"could not read input: {e}")
        return 2
    ok = True
    report = {"blobs": {}, "pages": {}, "quotes": []}
    for name, data in blobs.items():
        gid = hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()
        match = gid == BLOB_IDS[name]
        ok = ok and match
        report["blobs"][name] = {"git_blob_id": gid, "expected": BLOB_IDS[name],
                                 "match": match, "bytes": len(data)}
    for name, data in pages.items():
        report["pages"][name] = {"sha256": hashlib.sha256(data).hexdigest(),
                                 "bytes": len(data), "source_blob": PAGE_SOURCE[name]}
    for page, quote, heading in QUOTES:
        words = len(quote.split())
        html_raw = pages[page].decode("utf-8")
        md_raw = blobs[PAGE_SOURCE[page]].decode("utf-8")
        in_html = [h for h, body in html_sections(html_raw) if quote in html_text(body)]
        in_md = [h for h, body in md_sections(md_raw) if quote in md_text(body)]
        good = (bool(in_html) and bool(in_md) and words <= 25
                and heading in in_html and heading in in_md)
        ok = ok and good
        report["quotes"].append({"page": page, "words": words, "heading": heading,
                                 "found_in_html_under": in_html,
                                 "found_in_source_under": in_md,
                                 "pass": good, "quote": quote})
    print(json.dumps(report, indent=1, ensure_ascii=False))
    print("RESULT", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
