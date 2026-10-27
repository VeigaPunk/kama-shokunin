#!/usr/bin/env python3
"""X8Rows (round 52, lane kama): recover the exact deleted line each remaining
registry/append-only-disclosures.tsv row names, from the lane's git history alone.

For a row (commit c, file f, line_sha256 h, count n) this reads the -U0
first-parent diff of c against c^ for f, takes the deleted ('-') lines, and
matches sha256(key(line)) == h, key = bytes with one trailing CR stripped
(the same key tools/append-only-audit.py uses, lines 316-320).

Usage: recover_rows.py <repo> <tip> <out-json>
Exit 0 when every row matched exactly `count` deleted lines.
"""
import hashlib
import json
import re
import subprocess
import sys

LEDGER = "registry/append-only-disclosures.tsv"
HUNK = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True,
                          check=True).stdout


def key(ln):
    return ln[:-1] if ln.endswith(b"\r") else ln


def deleted_lines(repo, commit, path):
    """[(old_lineno, bytes)] deleted from path by commit vs its first parent."""
    out = []
    diff = git(repo, "diff", "--no-color", "--no-ext-diff", "-U0",
               "--src-prefix=a/", "--dst-prefix=b/", commit + "^", commit,
               "--", path)
    old = None
    for ln in diff.split(b"\n"):
        m = HUNK.match(ln)
        if m:
            old = int(m.group(1))
            continue
        if old is None:
            continue
        if ln.startswith(b"-") and not ln.startswith(b"---"):
            out.append((old, ln[1:]))
            old += 1
        elif ln.startswith(b"+"):
            pass
        elif ln.startswith(b" "):
            old += 1
    return out


def main(repo, tip, outp):
    rows = []
    text = git(repo, "show", f"{tip}:{LEDGER}").decode()
    for num, line in enumerate(text.split("\n"), 1):
        if not line.strip() or num == 1:
            continue
        c, f, h, n, cls, note = line.split("\t")
        rows.append({"ledger_line": num, "commit": c, "file": f,
                     "line_sha256": h, "count": int(n), "class": cls,
                     "note": note})
    ok = True
    for r in rows:
        dl = deleted_lines(repo, r["commit"], r["file"])
        hits = [(pos, ln) for pos, ln in dl
                if hashlib.sha256(key(ln)).hexdigest() == r["line_sha256"]]
        r["deleted_lines_in_commit"] = len(dl)
        r["matches"] = [{"parent_line": pos,
                         "bytes_hex": ln.hex(),
                         "text": ln.decode("utf-8", "backslashreplace")}
                        for pos, ln in hits]
        r["match_count"] = len(hits)
        if len(hits) != r["count"]:
            ok = False
    with open(outp, "w") as fh:
        json.dump({"tip": tip, "rows": rows}, fh, indent=1)
    print(f"rows={len(rows)} all_matched={ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
