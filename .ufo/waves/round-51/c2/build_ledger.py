#!/usr/bin/env python3
"""Round 51 (C2 build): write registry/append-only-disclosures.tsv from append-only-audit v6
JSON - one row per (event, line key) the tool lists as `undisclosed`, its mechanical class and
the deleting commit's subject as the note. Usage: build_ledger.py <aoa.json> <repo> <out.tsv>"""
import json
import subprocess
import sys

DHEADER = "commit\tfile\tline_sha256\tcount\tclass\tnote"


def main(src, repo, out):
    d = json.load(open(src))
    rows = [DHEADER]
    for e in d["events"]:
        if not e.get("undisclosed"):
            continue
        subj = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%s", e["commit"]],
                              capture_output=True, text=True, check=True).stdout.strip()
        note = ("deleted in place by: " + subj).replace("\t", " ")[:160]
        for u in e["undisclosed"]:
            if len(u["classes"]) != 1:
                raise SystemExit(f"{e['commit'][:12]} {e['file']}: classes {u['classes']}")
            rows.append("\t".join([e["commit"], e["file"], u["line_sha256"], str(u["count"]),
                                   u["classes"][0], note]))
    with open(out, "w") as fh:
        fh.write("\n".join(rows) + "\n")
    print(f"rows={len(rows) - 1} lines={sum(int(r.split(chr(9))[3]) for r in rows[1:])}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
