#!/usr/bin/env python3
"""RV01C1Attack — attacks 1/2/3/5(parser half) on tools/round81-selfrecord-round80.py.

Drives the production score()/derive()/corrections() functions against REAL lane blobs
(sealed a2af1af5…, tip 1b96317f…), the same Fixture mechanism the counter's own --selftest
uses. No git command runs here; no lane tree is touched. CLI-level git-show binding is
proven separately by the worktree-plant runs (attack 4).
"""
import importlib.util
import json
import pathlib
import sys

CTR = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round81-selfrecord-round80.py"
S = pathlib.Path("/fast/scratch/hyaku/kama-r81/RV01C1Attack")
SEALED_DIR = S / "sealed"
TIP_DIR = S / "blobs"

spec = importlib.util.spec_from_file_location("ctr", CTR)
ctr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ctr)

SEALED = ctr.SEALED
TIPKEY = "1b96317f690dbe9f42675099a004e150aaa54419"
LESSON = ctr.LESSON


def rd(p):
    return pathlib.Path(p).read_text()


sealed_blobs = {
    ctr.SCORECARD: rd(SEALED_DIR / "SCORECARD.md"),
    ctr.LOG: rd(SEALED_DIR / "LOG.md"),
    ctr.C1_RECEIPT: rd(SEALED_DIR / "c1-selftest.out"),
    ctr.C3_RECEIPT: rd(SEALED_DIR / "c3-selftest.out"),
}
tip_base = {
    ctr.SCORECARD: rd(TIP_DIR / "SCORECARD.md"),
    ctr.LOG: rd(TIP_DIR / "LOG.md"),
    LESSON: rd(TIP_DIR / "round-81.md"),
}

F1_LINE = ("`corrected F1 old=c1-selftest=pass=9 new=c1-selftest=pass=11 at="
           + SEALED + " date=2026-11-04`")


def lesson_real():
    t = tip_base[LESSON]
    assert F1_LINE in t, "F1 correction line not found verbatim in tip lessons blob"
    return t


def run(lesson_text=None, closures_tip="corpus/lessons/round-80-verifier-spotcheck.md"):
    lesson_text = lesson_real() if lesson_text is None else lesson_text
    blobs = {SEALED: sealed_blobs, TIPKEY: {**tip_base, LESSON: lesson_text}}
    closures = {TIPKEY: closures_tip,
                SEALED: "corpus/lessons/round-79-verifier-spotcheck.md"}
    fx = ctr.Fixture(blobs, closures)
    return ctr.score(fx, SEALED, TIPKEY, LESSON)[1]


cases = []


def check(name, expect, got, note):
    keys = ("stale", "mismatches", "corrected", "unbacked")
    observed = {k: got[k] for k in keys}
    ok = all(observed[k] == expect[k] for k in expect)
    cases.append({
        "case": name,
        "expected": expect,
        "observed": observed,
        "errors": got.get("errors"),
        "unbacked_detail": got.get("unbacked_detail"),
        "verdict": "CAUGHT" if ok else "ESCAPED",
        "note": note,
    })


# A0 — harness equivalence: real blobs, no mutation
check("A0-baseline-real-blobs",
      {"stale": 6, "mismatches": 0, "corrected": 6, "unbacked": 0}, run(),
      "harness must reproduce the CLI green receipt before any mutation means anything")

# Attack 1 — F1 correction refiled under ## Mistakes (round-80 RV01 defect class)
t = lesson_real().replace(F1_LINE + "\n", "", 1)
assert F1_LINE not in t
t = t.replace("## Mistakes\n",
              "## Mistakes\n\nrefiled under the wrong container: " + F1_LINE + "\n", 1)
check("A1-correction-block-under-Mistakes",
      {"stale": 6, "mismatches": 1, "corrected": 5, "unbacked": 0}, run(t),
      "a corrected-F1 block outside ## Corrections must be prose and leave F1 unanswered")

# Attack 2a — new does not re-derive at the tip (pass=99 vs receipt pass=11)
check("A2a-new-value-does-not-rederive",
      {"stale": 6, "mismatches": 0, "corrected": 5, "unbacked": 1},
      run(lesson_real().replace("new=c1-selftest=pass=11", "new=c1-selftest=pass=99")),
      "F1 must go unbacked with new=… != observed")

# Attack 2b — at names the record tip instead of the sealed revision
check("A2b-at-names-tip-not-sealed",
      {"stale": 6, "mismatches": 0, "corrected": 5, "unbacked": 1},
      run(lesson_real().replace("at=" + SEALED, "at=" + TIPKEY, 1)),
      "F1 must go unbacked with at=… != sealed")

# Attack 3 — old is not the sealed declared value
check("A3-old-not-sealed-declared-value",
      {"stale": 6, "mismatches": 0, "corrected": 5, "unbacked": 1},
      run(lesson_real().replace("old=c1-selftest=pass=9", "old=c1-selftest=pass=7")),
      "F1 must go unbacked with old=… != declared")

# Attack 5 (parser half) — F6 is tip-bound: with only a round-79 closure at the tip,
# F6 re-derives and its correction must flip to unbacked.
check("A5-f6-not-stale-when-tip-closure-is-round-79",
      {"stale": 5, "mismatches": 0, "corrected": 5, "unbacked": 1},
      run(closures_tip="corpus/lessons/round-79-verifier-spotcheck.md"),
      "F6 correction must become unbacked once F6 re-derives at the tip")

out = S / "receipts" / "parser-attacks.json"
out.write_text(json.dumps({"cases": cases}, indent=2) + "\n")
print(json.dumps({"cases": cases}, indent=2))
escaped = [c["case"] for c in cases if c["verdict"] != "CAUGHT"]
print("ESCAPED:", escaped if escaped else "none", file=sys.stderr)
sys.exit(1 if escaped else 0)
