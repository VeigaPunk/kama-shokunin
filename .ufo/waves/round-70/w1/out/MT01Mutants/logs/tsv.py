#!/usr/bin/env python3
"""MT01Mutants: render mutants.tsv from the two matrices plus the frozen counter probes.

Columns: tool | mutant | killed? | counter output | why
"""
import json
import os
import sys

S = "/fast/scratch/hyaku/kama-r70/MT01Mutants"
OUT = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-70/w1/out/MT01Mutants"

C1_WHY = {
    "landed": ("baseline: the landed bytes at the landed tip",
               "counter at the landed tip 73597158 prints mismatches=0 met=True, exit 0; "
               "selftest pass=5 fail=0 — the green premise the mutants are measured against"),
    "base-harness": ("the pre-repair harness (git archive) at the landed tip",
                     "the two git-dependent run facts fail without repository metadata"),
    "L-c1a": ("delete the `banner` check",
              "green fixture stays green (a disabled check cannot fail); only the planted "
              "banner violation discriminates. Selftest: no arm — it plants closure pointers only"),
    "L-c1b": ("delete the `province` check",
              "green fixture stays green; only the planted province violation discriminates. "
              "Selftest: no arm"),
    "L-c1c": ("make `closure_ptr` always return True",
              "green fixture stays green; the planted stale pointer discriminates, and the "
              "selftest's stale_ptr/stale_both/stale_incl/no_ptr arms fail"),
    "L-c1d": ("keep the metadata-free export, special-case the two failing commands",
              "on the landed tree the verdict is byte-identical to the repair (both git facts "
              "pass); only a THIRD git-dependent fact the special-case does not name discriminates. "
              "Selftest: no arm"),
    "L-c1e": ("make `mismatches` always 0",
              "the red base tree and every planted fixture read met=True; the selftest's four "
              "planted arms all collapse to ok_m, so fail=4"),
}


def jload(p):
    rows = {}
    for line in open(p):
        line = line.strip()
        if line:
            r = json.loads(line)
            rows[r["variant"]] = r
    return rows


def fmt_c1(r):
    parts = []
    for k in ("G", "NB", "NP", "NC", "NH", "BASE", "TIP"):
        if k in r:
            parts.append(f"{k}=exit{r[k]['exit']}/mism={r[k]['mismatches']}")
    st = r["ST"]
    parts.append(f"ST=exit{st['exit']}/pass={st['pass']} fail={st['fail']}")
    return "; ".join(parts)


def main():
    c1a = jload(os.path.join(S, "c1-matrix.jsonl"))
    c1b = jload(os.path.join(S, "matrix2.jsonl")) if os.path.exists(os.path.join(S, "matrix2.jsonl")) else {}
    c1 = {**c1a, **c1b}
    c2 = {}
    for line in open(os.path.join(S, "c2-matrix.jsonl")):
        r = json.loads(line)
        c2[r["candidate"]] = r

    rows = [("tool", "mutant", "killed?", "counter output", "why")]
    order = ["landed", "base-harness", "L-c1a", "L-c1b", "L-c1c", "L-c1d", "L-c1e"]
    for name in order:
        r = c1.get(name)
        if not r:
            continue
        verdict = "n/a (substrate)"
        if name == "landed":
            verdict = "baseline"
        elif name == "base-harness":
            verdict = "red (control)"
        else:
            # killed if any detector deviates from the landed baseline on a fixture
            base = c1.get("landed", {})
            dev = [k for k in ("G", "NB", "NP", "NC", "NH", "TIP", "BASE")
                   if k in r and k in base and (r[k]["exit"], r[k]["mismatches"]) != (base[k]["exit"], base[k]["mismatches"])]
            if r["ST"]["exit"] != base["ST"]["exit"]:
                dev.append("ST")
            verdict = "KILLED (" + ",".join(dev) + ")" if dev else "SURVIVES the unplanted counter"
        why = C1_WHY.get(name, ("", ""))[1]
        rows.append(("round42-selfdesc-reconcile", name, verdict, fmt_c1(r), why))

    c2why = {
        "base-bytes": ("frozen pre-repair bytes", "do-nothing control: a refused member reads as exit 0"),
        "ex02": ("EX02CensusVerdict candidate (== the landed bytes)", "baseline green on the frozen control"),
        "c2a": ("count refusals as passes", "refused fixture exits 0, so the frozen control is red"),
        "c2b": ("always exit 1", "the all-pass fixture exits 1, so the frozen control is red"),
        "c2c": ("drop the `not_evaluated` field", "the control reads only the exit pair; the verdict line loses "
                                                   "the field the frozen TARGET requires, so only a line-content check kills it"),
        "c2d": ("drop one member", "the control replaces MEMBERS, so the registered population is invisible to it; "
                                   "the module count 21 != 22 kills it"),
        "c2e": ("let a failing member be waived", "the control's fixtures contain no failing member; the "
                                                  "fail-waiver probe (fail + --waive) exits 0 and kills it"),
    }
    for name in ("base-bytes", "ex02", "c2a", "c2b", "c2c", "c2d", "c2e"):
        r = c2.get(name)
        if not r:
            continue
        if name in ("base-bytes", "ex02"):
            verdict = "baseline"
        elif name in ("c2a", "c2b"):
            verdict = "KILLED"
        elif name == "c2c":
            verdict = "SURVIVES control; killed by verdict-line check"
        elif name == "c2d":
            verdict = "SURVIVES control; killed by member-count check"
        else:
            verdict = "SURVIVES control; killed by fail-waiver probe"
        out = (f"{r['control_line']}; refused_verdict={r['refused_verdict']!r}; "
               f"members={r['members']}; probe_exit={r['probe_exit']}")
        rows.append(("round65-host-census", name, verdict, out, c2why[name][1]))

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "mutants.tsv"), "w") as f:
        for row in rows:
            f.write("\t".join(str(x).replace("\t", " ") for x in row) + "\n")
    print(f"wrote {len(rows) - 1} rows to {OUT}/mutants.tsv")


if __name__ == "__main__":
    main()
