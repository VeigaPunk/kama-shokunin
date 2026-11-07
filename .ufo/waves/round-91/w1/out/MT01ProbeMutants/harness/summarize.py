#!/usr/bin/env python3
"""Summarize mutant receipts: counter cells killed + check.py rows killed."""
import json, pathlib, sys

SC = pathlib.Path("/fast/scratch/hyaku/kama-r91/MT01ProbeMutants/receipts")
ORDER = [
    "baseline",
    "m01-norm-no-gguf-strip", "m02-norm-strip-all-gguf", "m03-norm-L-ge-5-to-gt-5",
    "m04-norm-drop-string-coercion", "m05-awk-v-instead-of-environ", "m06-hit-never-set",
    "m07-end-exit-1-2-swapped", "m08-router-match-prints-all", "m09-router-refine-no-early-return",
    "m10-paste-to-tr-no-strip", "m11-router-match-default-fs", "m12-model-matches-no-shortcircuit",
    "m13-model-matches-empty-id-counted", "m14-router-refine-wildcard-inverted",
    "m15-environ-no-string-coercion",
]


def rd(p):
    try:
        return p.read_text()
    except OSError:
        return ""


for mid in ORDER:
    d = SC / mid
    if not d.is_dir():
        continue
    cout = rd(d / "counter.out")
    cells = [ln.split()[1] for ln in cout.splitlines()
             if ln.startswith("ANSWER_TIME_CELL ") and " ok=0 " in ln]
    total = sum(1 for ln in cout.splitlines() if ln.startswith("ANSWER_TIME_CELL "))
    summ = [ln for ln in cout.splitlines() if ln.startswith("ANSWER_TIME cells=")]
    crc = rd(d / "counter.rc").strip()
    chk_rc = rd(d / "check.rc").strip()
    fails = []
    js = rd(d / "check.json")
    if js:
        try:
            doc = json.loads(js[js.index("{"):])
            fails = [r["name"] + "/" + str(r.get("reason")) for r in doc["records"] if not r["passed"]]
        except Exception as e:
            fails = [f"<unparsed {e}>"]
    print(f"== {mid} rev={rd(d/'rev').strip()[:12]} probe_sha={rd(d/'probe.sha256').strip()[:12]} "
          f"bash_n={rd(d/'bash-n.rc').strip()} restored={rd(d/'restored.sha256').strip()[:12]}")
    print(f"   counter {crc} cells={total} killed_cells={len(cells)} {sorted(cells)}")
    if summ:
        print(f"   {summ[-1]}")
    print(f"   check   {chk_rc} failures={len(fails)} {fails[:8]}")
