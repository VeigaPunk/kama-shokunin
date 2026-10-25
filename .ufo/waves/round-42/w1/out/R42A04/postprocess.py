#!/usr/bin/env python3
"""R42A04 - post-process the mutant matrix receipts with correct tip-line normalization.

The rebuilt control stand-in commits have different hashes than the originals,
so every receipt's `tip=` line differs; comparisons must drop it. For
sep-c1-only the committed receipt is stale (see report F1), so the reference is
the rebuilt pristine receipt. Writes analysis.json.
"""
from __future__ import annotations

import json
import os

SEAT = "/fast/scratch/kama-r42/seats/R42A04"
OUT = os.path.join(SEAT, "out")
CTRLDIR = "/fast/scratch/kama-r42/clone/.ufo/waves/round-42/controls"
CAND = "/fast/scratch/kama-r42/clone/.ufo/waves/round-42/c1/candidate.out"

# ref -> (path, drop_tip, use_pristine)
REFS = {
    "base.c1": (os.path.join(CTRLDIR, "base.c1.out"), False, False),
    "freeze.c1": (os.path.join(CTRLDIR, "freeze.c1.out"), True, False),
    "junk-c1-textonly.c1": (os.path.join(CTRLDIR, "junk-c1-textonly.c1.out"), True, False),
    "junk-c1-sidefilesonly.c1": (os.path.join(CTRLDIR, "junk-c1-sidefilesonly.c1.out"), True, False),
    "junk-c1-falserel.c1": (os.path.join(CTRLDIR, "junk-c1-falserel.c1.out"), True, False),
    "sep-c1-only.c1": (os.path.join(CTRLDIR, "sep-c1-only.c1.out"), True, True),
    "sep-c2-only.c1": (os.path.join(CTRLDIR, "sep-c2-only.c1.out"), True, False),
    "sep-c3-only.c1": (os.path.join(CTRLDIR, "sep-c3-only.c1.out"), True, False),
    "candidate": (CAND, False, False),
}


def drop_tip(text: str) -> str:
    return "\n".join(text.split("\n")[1:])


def counter_line(text: str):
    for l in text.split("\n"):
        if "mismatches=" in l:
            return l
    return None


def compare(mut_text: str, ref_text: str) -> dict:
    mcount, rcount = counter_line(mut_text), counter_line(ref_text)
    mexit = mut_text.rstrip("\n").split("\n")[-1] if mut_text.strip() else ""
    rexit = ref_text.rstrip("\n").split("\n")[-1] if ref_text.strip() else ""
    if mcount is None or rcount is None:
        kind = "crash"
    elif mut_text == ref_text:
        kind = "equal"
    elif mcount != rcount or mexit != rexit:
        kind = "count/exit"
    else:
        kind = "detail-lines"
    return dict(kind=kind, count=mcount, exit=mexit)


def main() -> None:
    analysis = {}
    pristine_checks = {}
    # pristine sanity vs committed refs
    for ref, (path, drop, use_pris) in REFS.items():
        pris_path = os.path.join(OUT, "pristine", f"PRISTINE-freeze.{ref}.out")
        pris = open(pris_path).read()
        committed = open(path).read()
        r = committed if not drop else drop_tip(committed)
        p = pris if not drop else drop_tip(pris)
        pristine_checks[ref] = compare(p, r)
    # tipq pristine
    tipq_pris = open(os.path.join(OUT, "pristine", "PRISTINE-freeze.tipq.out")).read()

    mutdir = os.path.join(OUT, "mut")
    mids = sorted({f.split(".")[0] for f in os.listdir(mutdir)})
    for mid in mids:
        per = {}
        for ref, (path, drop, use_pris) in REFS.items():
            mut_path = os.path.join(mutdir, f"{mid}.{ref}.out")
            mut = open(mut_path).read()
            if use_pris:  # stale committed receipt: rebuilt pristine is the reference
                ref_text = open(os.path.join(OUT, "pristine", f"PRISTINE-freeze.{ref}.out")).read()
            else:
                ref_text = open(path).read()
            if drop:
                ref_text, mut = drop_tip(ref_text), drop_tip(mut)
            per[ref] = compare(mut, ref_text)
        # tipq vs pristine tipq (same commit hash, full compare)
        mut = open(os.path.join(mutdir, f"{mid}.tipq.out")).read()
        per["tipq"] = compare(mut, tipq_pris)
        analysis[mid] = per

    # classify verdicts
    CONTROL_REFS = ["base.c1", "freeze.c1", "junk-c1-textonly.c1", "junk-c1-sidefilesonly.c1",
                    "junk-c1-falserel.c1", "sep-c1-only.c1", "sep-c2-only.c1", "sep-c3-only.c1"]
    for mid, per in analysis.items():
        killed_by = [r for r in CONTROL_REFS if per[r]["kind"] != "equal"]
        pos = per["candidate"]["kind"] != "equal"
        tipq_changed = per["tipq"]["kind"] != "equal"
        verdict = "SURVIVES-ALL-CONTROLS" if not killed_by and not pos else f"killed by {','.join(killed_by)}" + ("+candidate" if pos else "")
        per["verdict"] = dict(killed_by=killed_by, candidate_changed=pos, tipq_changed=tipq_changed, verdict=verdict)

    with open(os.path.join(OUT, "analysis.json"), "w") as f:
        json.dump(dict(pristine_checks=pristine_checks, mutants=analysis), f, indent=1)

    print("== pristine vs committed (equal expected everywhere except sep-c1-only staleness):")
    for ref, c in pristine_checks.items():
        print(f"  {ref:26s} {c['kind']:12s} {c['count']}")
    print("== mutant verdicts:")
    for mid, per in analysis.items():
        v = per["verdict"]
        print(f"  {mid:5s} {v['verdict']}")


if __name__ == "__main__":
    main()
