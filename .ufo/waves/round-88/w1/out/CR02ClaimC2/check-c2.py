#!/usr/bin/env python3
"""CR02ClaimC2 corroboration checker for round-88 C2.

Read-only: derives every fact from git blobs at the named revisions.
Usage: check-c2.py --repo <clone> [--json]
Checks, in order:
  H  sha256 of seven instruments at B, F, I, M, T (C2 predicate conjunct 3)
  V  every `| calibration |` row of B found verbatim (exact string) at M, with
     its occurrence count, plus the number of live-table rows at B and M
  C  M content: live axes rows/vector, canon round/rows/unique names,
     saturation vector + first-working rounds, retired counts, Planned heading,
     and the depth/adjacency hash anchors against observed blobs
Exit 0 iff every check passes; 1 otherwise.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys

B = "9b4c7af16fdd4bba9e4815f4615f4b003f340747"
F = "fb76e7f26d6582bd087935a00f8dc43af4db912f"
I = "68ab526ee64795e52afd8c34ec7252e36d0a42e2"
M = "138a75437bcd11b72446087e970f5dfc5abf9ccd"
T = "f77d2ae9f2797a19e7548989fb9e64d8f9411d3f"
REVS = (("B", B), ("F", F), ("I", I), ("M", M), ("T", T))
INSTRUMENTS = (
    "tools/round42-selfdesc-reconcile.py",
    "tools/round41-scorecard-reconcile.py",
    "tools/round69-newest-closure-counter.py",
    "tools/round74-selfdesc-canon.py",
    "tools/round86-rendered-cells.py",
    "tools/round84-selfrecord-round83.py",
    "tools/round72-round-scope.py",
)


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout


def blob(repo, rev, path):
    return git(repo, "cat-file", "-p", f"{rev}:{path}").decode(errors="replace")


def axes_rows(text):
    lines = text.split("\n")
    try:
        start = lines.index("## Axes")
    except ValueError:
        return []
    rows, inb = [], False
    for ln in lines[start + 1:]:
        if ln.startswith("## "):
            break
        if ln.startswith("|"):
            inb = True
            rows.append([c.strip() for c in ln.strip().strip("|").split("|")])
        elif inb:
            break
    return rows[2:]


def canon(text):
    best, start = -1, None
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        m = re.search(r"canonical list as of round\s+(\d+)\*\*", ln, re.I)
        if m and int(m.group(1)) > best:
            best, start = int(m.group(1)), i
    rows = []
    for ln in lines[start + 1:]:
        if ln.startswith("|"):
            rows.append([c.strip() for c in ln.strip().strip("|").split("|")])
        elif rows:
            break
    return best, rows[2:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    a = ap.parse_args()
    repo = a.repo
    fail = 0

    print("== H instruments B..T")
    for path in INSTRUMENTS:
        digests = []
        for name, rev in REVS:
            digests.append(hashlib.sha256(blob(repo, rev, path).encode()).hexdigest()[:16])
        same = len(set(digests)) == 1
        fail += 0 if same else 1
        print(f"H {'ok ' if same else 'BAD'} {path} {' '.join(f'{n}={d}' for (n, _), d in zip(REVS, digests))}")

    print("== V moved rows")
    tb, tm = blob(repo, B, "SCORECARD.md"), blob(repo, M, "SCORECARD.md")
    mb = tm.split("\n")
    brows = [r for r in axes_rows(tb) if r and r[0].strip("* ").lower().startswith("calibration")]
    mrows = axes_rows(tm)
    print(f"V live-table rows B={len(axes_rows(tb))} M={len(mrows)} calibration-rows-B={len(brows)}")
    moved = 0
    for r in brows:
        # exact source line: rebuild from the blob, not the cell split
        line = next(l for l in tb.split("\n") if l.startswith("| calibration |") and r[2] in l)
        cnt = mb.count(line)
        ok = cnt == 1
        moved += 1 if ok else 0
        fail += 0 if ok else 1
        print(f"V {'ok ' if ok else 'BAD'} calibration row ({line[15:60]}...) verbatim at M count={cnt} len={len(line)}")
    print(f"V moved_rows={moved} (B has {len(brows)} calibration rows in the live table)")

    print("== C M content")
    lines = tm.split("\n")
    vec = []
    for r in mrows:
        ax = r[0].replace("*", "").strip().split(" ")[0].lower()
        ints = re.findall(r"\d+", r[1])
        vec.append((ax, int(ints[-1]) if ints else -1))
    years = "\n".join(lines)
    firsts_line = years.split("first-working rounds ")
    cn, crows = canon(tm)
    names = [r[0].strip("` *") for r in crows if r]
    firsts = sorted({int(re.findall(r"\d+", r[3])[-1]) for r in crows if len(r) >= 4 and re.findall(r"\d+", r[3])})
    sat = years.split("## Saturation", 1)[1].split("\n## ", 1)[0]
    ret = years.split("## Retired", 1)[1].split("\n## ", 1)[0]
    checks = [
        ("vector_rows", f"{len(mrows)} live rows, vector " + ", ".join(f"{a} {s}" for a, s in vec),
         ", ".join(f"{a} {s}" for a, s in vec) in sat),
        ("vector_duplicate_free", f"axes={len({a for a, _ in vec})}", len({a for a, _ in vec}) == len(vec)),
        ("canon", f"round={cn} rows={len(crows)} unique={len(set(names))}", cn == 88 and len(names) == 55 == len(set(names))),
        ("firsts", f"{len(firsts)} rounds, has 87/88", "first-working rounds " + ", ".join(map(str, firsts)) in sat and 87 in firsts and 88 in firsts),
        ("retired", f"'6 axes' {'6 axes' in ret}, '55 capabilities' {'55 capabilities' in ret}", "6 axes" in ret and "55 capabilities" in ret),
        ("planned", "'### Planned (round 89)'", "### Planned (round 89)" in lines),
    ]
    for name, detail, ok in checks:
        fail += 0 if ok else 1
        print(f"C {'ok ' if ok else 'BAD'} {name}: {detail}")
    live_row_text = "\n".join("|".join(r) for r in mrows)  # live axes rows only; historical rows keep their old anchors
    for path, algo in (("SKILL.md", "sha256"), ("corpus/knowledge/cross-lane-scope.md", "sha256")):
        blob_txt = blob(repo, M, path)
        obs = hashlib.sha256(blob_txt.encode()).hexdigest()
        cited = re.findall(rf"`{re.escape(path)}`\s+{algo}\s+`([0-9a-f]{{64}})`(?:\s+\((\d+) lines\))?", live_row_text)
        for hexd, nl in cited:
            n_obs = len(blob_txt.splitlines())
            ok = hexd == obs
            fail += 0 if ok else 1
            print(f"C {'ok ' if ok else 'BAD'} anchor {path} cited={hexd[:12]} observed={obs[:12]} cited_lines={nl} file_lines={n_obs}")
    print(f"RESULT fail={fail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
