#!/usr/bin/env python3
"""Throwaway scanner (seat R42B12): the digest-ledger token scan, applied to the
population tools/digest-ledger.py excludes - tracked .ufo/**/*.md and *.tsv at a
revision. Same TOKEN regex, same blob set (sha256 of every blob reachable from
the rev), same ledger parse/classify. Read-only on --repo."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys

TOKEN = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
LEDGER = "registry/digest-ledger.tsv"


def git(repo, *a):
    p = subprocess.run(["git", "-C", repo, *a], capture_output=True)
    if p.returncode:
        raise SystemExit(f"git {' '.join(a)}: {p.stderr.decode()}")
    return p.stdout


def parse_ledger(text):
    rows = {}
    for i, line in enumerate(text.split("\n")):
        if not line or (i == 0 and line.startswith("digest\t")):
            continue
        c = line.split("\t") + [""] * 7
        rows[c[0]] = {"cls": c[1], "path": c[3], "correct": c[4], "note": c[6]}
    return rows


def main(repo, rev):
    rev = git(repo, "rev-parse", "--verify", rev + "^{commit}").decode().strip()
    ids = [l.split(" ", 1)[0] for l in git(repo, "rev-list", "--objects", rev).decode().split("\n") if l]
    p = subprocess.run(["git", "-C", repo, "cat-file", "--batch"],
                       input="".join(i + "\n" for i in ids).encode(), capture_output=True)
    blobs, buf, i = set(), p.stdout, 0
    while i < len(buf):
        j = buf.index(b"\n", i)
        _, typ, size = buf[i:j].decode().split()
        size = int(size)
        if typ == "blob":
            blobs.add(hashlib.sha256(buf[j + 1:j + 1 + size]).hexdigest())
        i = j + 1 + size + 1

    paths = [x for x in git(repo, "ls-tree", "-r", "--name-only", "-z", rev).decode().split("\0") if x]
    ledger = {}
    if LEDGER in paths:
        ledger = parse_ledger(git(repo, "cat-file", "-p", f"{rev}:{LEDGER}").decode(errors="replace"))

    def is_doc(path):
        return not path.startswith(".ufo/") and path != LEDGER and path.endswith((".md", ".tsv"))

    def scan(select):
        occ = {}          # token -> [(path, line, col)]
        for path in paths:
            if not select(path):
                continue
            text = git(repo, "cat-file", "-p", f"{rev}:{path}").decode(errors="replace")
            for lineno, line in enumerate(text.split("\n"), 1):
                for m in TOKEN.finditer(line):
                    occ.setdefault(m.group(0), []).append((path, lineno, m.start() + 1))
        return occ

    def classify(occ):
        n = dict(tokens=len(occ), blob=0, external_ok=0, external_absent=0, unverifiable=0,
                 wrong_flagged=0, ledger_bad=0, wrong_unflagged=0, unknown=0)
        pref = {b[:8] for b in blobs}
        rows = {}
        for t in sorted(occ):
            if t in blobs:
                n["blob"] += 1
                rows[t] = ("blob", "")
            elif t in ledger:
                r = ledger[t]
                cls = r["cls"]
                if cls == "external":
                    import os
                    if r["path"] and os.path.isfile(r["path"]):
                        h = hashlib.sha256(open(r["path"], "rb").read()).hexdigest()
                        k = "external_ok" if h == t else "ledger_bad"
                    else:
                        k = "external_absent"
                elif cls == "unverifiable":
                    k = "unverifiable" if r["note"].strip() else "ledger_bad"
                elif cls == "wrong":
                    c = r["correct"]
                    k = "wrong_flagged" if re.fullmatch(r"[0-9a-f]{64}", c) and c in blobs and c[:8] == t[:8] else "ledger_bad"
                else:
                    k = "ledger_bad"
                n[k] += 1
                rows[t] = (k, "ledger:" + cls)
            elif t[:8] in pref:
                n["wrong_unflagged"] += 1
                rows[t] = ("wrong_unflagged", "prefix")
            else:
                n["unknown"] += 1
                rows[t] = ("unknown", "")
        return n, rows

    out = {"rev": rev, "blobs": len(blobs), "ledger_rows": len(ledger),
           "ufo_files_total": sum(1 for x in paths if x.startswith(".ufo/")),
           "ufo_docs": sum(1 for x in paths if x.startswith(".ufo/") and x.endswith((".md", ".tsv")))}

    # population A: what the tool scans (sanity cross-check)
    occA = scan(is_doc)
    nA, _ = classify(occA)
    out["in_population"] = nA

    # population B: the excluded .ufo/ documents
    occB = scan(lambda p: p.startswith(".ufo/") and p.endswith((".md", ".tsv")))
    nB, rowsB = classify(occB)
    out["ufo"] = nB

    freq = sorted(occB.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    unexp = [(t, o) for t, o in freq if rowsB[t][0] in ("unknown", "wrong_unflagged", "ledger_bad")]
    out["ufo_unexplained"] = [
        {"token": t, "class": rowsB[t][0], "occurrences": len(o),
         "files": len({x[0] for x in o}),
         "first": [{"path": x[0], "line": x[1]} for x in o[:5]]}
        for t, o in unexp]
    out["ufo_top5_by_freq"] = [
        {"token": t, "class": rowsB[t][0], "occurrences": len(o), "files": len({x[0] for x in o}),
         "first": {"path": o[0][0], "line": o[0][1]}}
        for t, o in freq[:5]]
    out["ufo_all_tokens"] = [
        {"token": t, "class": rowsB[t][0], "occurrences": len(o),
         "first": {"path": o[0][0], "line": o[0][1]}} for t, o in freq]
    out["ufo_docs_with_tokens"] = len({x[0] for o in occB.values() for x in o})
    out["ufo_doc_ext_breakdown"] = {
        ext: sum(1 for x in paths if x.startswith(".ufo/") and x.endswith(ext))
        for ext in (".md", ".tsv")}
    out["tsv_outside_ufo_in_population"] = [x for x in paths if not x.startswith(".ufo/") and x.endswith(".tsv")]
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
