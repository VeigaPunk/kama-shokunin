#!/usr/bin/env python3
"""Newline-exactness probe for round-86 C3: drive grade()/check_anchor() directly
with an injected fetcher (same mechanism as the instrument's --selftest) to test
how the byte comparison treats line boundaries.

Arms:
  blank-line-end-verified   upstream range ending on a blank line, stored body
                            includes that blank line -> expect verified
  blank-line-end-extra      stored body has one extra trailing blank line -> expect
                            mismatch (comparison is sensitive to trailing blanks)
  crlf-upstream-lf-stored   upstream CRLF, stored LF -> measured (is CRLF normalized?)
  crlf-upstream-crlf-stored upstream CRLF, stored CRLF -> measured
  formfeed-upstream         upstream contains a form feed inside the range -> measured
"""
import hashlib
import importlib.util
import pathlib
import tempfile

SPEC = importlib.util.spec_from_file_location(
    "po", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round86-pin-origin.py")
po = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(po)

URL = "https://example.invalid/fixture/newline-probe.md"


def run(name, upstream_bytes, stored_body, start, end):
    with tempfile.TemporaryDirectory(prefix="r86-newline-") as directory:
        root = pathlib.Path(directory)
        digest = hashlib.sha256(stored_body.encode("utf-8", "surrogateescape")).hexdigest()
        rel = "corpus/anchors/nl.txt"
        path = root / rel
        path.parent.mkdir(parents=True)
        path.write_text(f"# url={URL} sha256={digest} ref=nl lines={start}-{end}\n{stored_body}",
                        encoding="utf-8")
        rows = root / po.ROWS
        rows.parent.mkdir(parents=True, exist_ok=True)
        cells = ["fixture", "nl", "v2", "holds", "2026-11-04", "q", "3", "q", "3", rel, rel, "n"]
        rows.write_text("\t".join(po.HEADER) + "\n" + "\t".join(cells) + "\n", encoding="utf-8")
        result = po.grade(root, "worktree", po.ROWS,
                          fetch=lambda u, _b=upstream_bytes: _b)
        verdict = result["results"][0]["verdict"]
        detail = result["results"][0]["detail"]
        print(f"ARM {name}: verdict={verdict} :: {detail}")


# A: range 1-2 ends on the blank line 2; stored body keeps it.
run("blank-line-end-verified", b"line-one\n\nline-three\n", "line-one\n\n", 1, 2)
# B: same upstream, stored body has one extra trailing blank line.
run("blank-line-end-extra", b"line-one\n\nline-three\n", "line-one\n\n\n", 1, 2)
# C: upstream CRLF, stored LF.
run("crlf-upstream-lf-stored", b"line-one\r\nline-two\r\n", "line-one\nline-two\n", 1, 2)
# D: upstream CRLF, stored CRLF.
run("crlf-upstream-crlf-stored", b"line-one\r\nline-two\r\n", "line-one\r\nline-two\r\n", 1, 2)
# E: form feed inside the upstream range.
run("formfeed-upstream", b"line-one\n\x0cline-two\n", "line-one\n\x0cline-two\n", 1, 2)
