#!/usr/bin/env python3
"""SB01 C3 probes (offline; injected fetchers, no network).
    python3 probe_c3.py <root-of-git-archive-at-bafae7af>
P-G: row declares ref=b11755/newest=b12111 but both anchor headers name a b7200 URL and match upstream -> verified.
P-H: both headers name https://example.invalid/... and the fetcher serves the same fabricated body -> verified."""
import importlib.util
import pathlib
import sys
import tempfile

root = pathlib.Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("r86po", root / "tools" / "round86-pin-origin.py")
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)
UP = P.UPSTREAM


def build(hdr_url, row_ref, row_newest, body):
    """Write two anchors (body is the stored body) and a one-row register; grade with fetch -> body."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="sb01-c3-"))
    lines = body.splitlines()
    P.write_anchor(tmp, "corpus/anchors/a.txt", hdr_url, "b7200", 1, len(lines), lines, body_override=body)
    P.write_anchor(tmp, "corpus/anchors/b.txt", hdr_url, "b7200", 1, len(lines), lines, body_override=body)
    P.write_rows(tmp, "corpus/anchors/a.txt", "corpus/anchors/b.txt", ref=row_ref)
    reg = tmp / P.ROWS
    rows = reg.read_text().split("\n")
    cells = rows[1].split("\t")
    cells[2] = row_newest
    rows[1] = "\t".join(cells)
    reg.write_text("\n".join(rows))
    res = P.grade(tmp, "worktree", P.ROWS, fetch=lambda url: body.encode())
    return res["results"][0]["verdict"], res["results"][0]["detail"]


print("P-G:", build("https://raw.githubusercontent.com/ggml-org/llama.cpp/b7200/tools/server/README.md",
                    "b11755", "b12111", UP))
print("P-H:", build("https://example.invalid/fabricated/README.md", "fixture", "v2",
                    "FABRICATED line\n"))
