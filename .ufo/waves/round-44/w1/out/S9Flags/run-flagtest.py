#!/usr/bin/env python3
"""S9Flags: exercise the flag placement in a throwaway clone and score it with
the frozen round-44 C1 counter.

Inserts the drafted flag sentence after each anchor's enclosing block in every
entry of flag-map.tsv, flips the draft-ledger rows whose draft verdict is
`holds` (the only rows the draft already gives both ranges for) to `drifted`,
appends the SOURCES.md round-44 section the counter needs, commits inside the
clone, and runs tools/round44-release-recheck-audit.py on it. Every
`not flagged in <entry>` detail is therefore a real defect in flag-map.tsv.

Usage: run-flagtest.py <clone> <out dir>
"""
import json
import os
import re
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
UP = "/fast/scratch/hyaku/kama-r44/shared/llama.cpp"
USER = ["-c", "user.name=S9Flags", "-c", "user.email=s9flags@fixture.invalid"]
TEMPLATE = ("Release recheck (round 44, b11889): {sid} <what changed, release lines>"
            " - the statement above holds at b11755 (704366d76), not at b11889.")


def git(d, *a, **kw):
    return subprocess.run(["git", "-C", d, *a], capture_output=True,
                          text=True, check=kw.pop("check", True))


def main():
    clone, out = sys.argv[1], sys.argv[2]
    top = git(clone, "rev-parse", "--show-toplevel").stdout.strip()
    assert os.path.realpath(top) == os.path.realpath(clone), top
    fm = os.path.join(out, "flag-map.tsv")
    plan = {}
    for line in open(fm, encoding="utf-8").read().splitlines()[1:]:
        sid, entry, n = line.split("\t")
        plan.setdefault(entry, []).append((int(n), sid))

    for entry, items in plan.items():
        path = os.path.join(clone, entry)
        src = open(path, encoding="utf-8").read().split("\n")
        after = {}
        for n, sid in items:
            b = n
            while b <= len(src) and src[b - 1].strip():
                b += 1
            after.setdefault(b - 1, []).append(sid)      # insert after block end
        new = []
        for i, line in enumerate(src, 1):
            new.append(line)
            for sid in sorted(after.get(i, [])):
                new.append("")
                new.append(TEMPLATE.format(sid=sid))
        if new and new[-1] == "" and not after.get(len(src)):
            pass
        open(path, "w", encoding="utf-8").write("\n".join(new))

    # ledger: draft rows, holds -> drifted (test verdict), SOURCES section
    draft = os.path.join(LANE, ".ufo/waves/round-44/c1/draft-ledger.tsv")
    rows = open(draft, encoding="utf-8").read().splitlines()
    head, body = rows[0], rows[1:]
    mapids = {sid for items in plan.values() for _, sid in items}
    outrows, drifted = [head], []
    for r in body:
        f = r.split("\t")
        if f[0] in mapids and f[9] == "holds":
            f[9] = "drifted"
            f[10] = ("S9Flags flag-placement test: treated as drifted so the "
                     "frozen counter exercises this row's used-by flag")
            drifted.append(f[0])
        outrows.append("\t".join(f))
    os.makedirs(os.path.join(clone, "registry"), exist_ok=True)
    open(os.path.join(clone, "registry/release-recheck-b11889.tsv"),
         "w", encoding="utf-8").write("\n".join(outrows) + "\n")

    srcp = os.path.join(clone, "corpus/SOURCES.md")
    src = open(srcp, encoding="utf-8").read().rstrip("\n")
    src += ("\n\n## Round-44 release re-verification (b11889 = d854d98b)\n\n"
            "| id | verdict |\n|---|---|\n")
    src += "".join(f"| {s} | drifted |\n" for s in drifted)
    open(srcp, "w", encoding="utf-8").write(src)

    git(clone, "add", "-A")
    git(clone, *USER, "commit", "-q", "-m", "S9Flags flag placement test")
    tip = git(clone, "rev-parse", "HEAD").stdout.strip()
    print(f"clone={clone}\ntip={tip}\ndrifted_rows={len(drifted)} rows_with_flag={len(mapids)}")
    r = subprocess.run([sys.executable,
                        os.path.join(LANE, "tools/round44-release-recheck-audit.py"),
                        "--repo", clone, "--tip", tip, "--upstream", UP,
                        "--out", os.path.join(out, "flagtest-c1.out")],
                       capture_output=True, text=True)
    print("counter exit", r.returncode)
    txt = open(os.path.join(out, "flagtest-c1.out"), encoding="utf-8").read()
    print("\n".join(l for l in txt.splitlines()
                    if l.startswith("pop=") or "not flagged" in l or "not listed" in l))
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
