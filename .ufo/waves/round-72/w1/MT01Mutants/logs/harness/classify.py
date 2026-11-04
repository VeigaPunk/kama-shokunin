#!/usr/bin/env python3
"""Derive, from the saved observations, which detector actually killed each mutant.

A mutant killed by `selftest` is caught by the shipped instrument battery; a mutant
killed only by `fixture:<name>` is a behavior the shipped battery never exercises --
that is the calibration finding this seat exists to produce.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r72/MT01Mutants")
W = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-72/w1/MT01Mutants")
LOGS = S / "logs"

FAMILY = {
    "S": ("logs/scope-baseline.json", "scope"),
    "B": ("logs/bind-baseline.json", "bind"),
    "G": ("logs/gate-baseline.json", "gate"),
}
FIXTURE_KEYS = {
    "scope": ("clean", "label-missing", "label-wrong", "label-later", "stray", "stray-dir",
              "wave-uncommitted", "ignored", "ignored-root", "allow-exact", "allow-dir",
              "rename"),
    "bind": ("clean", "unbound", "shifted", "stale", "nonancestor", "brace", "late-header",
             "conflict"),
}


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def killed_by(mid: str, base: dict, obs: dict, family: str) -> str:
    hits = []
    if family == "gate":
        if obs["selftest"]["line"] != base["selftest"]["line"] or \
                obs["selftest"]["exit"] != base["selftest"]["exit"]:
            hits.append("selftest")
        if obs["probe"]["line"] != base["probe"]["line"] or obs["probe"]["calls"] != base["probe"]["calls"]:
            hits.append("argv-probe")
        if obs["buildfail"]["exit"] != base["buildfail"]["exit"]:
            hits.append("build-failure-probe")
        if obs["cleanprobe"]["line"] != base["cleanprobe"]["line"]:
            hits.append("round-clean-probe")
        return "+".join(hits) or "none"
    if obs["_selftest"]["exit"] != base["_selftest"]["exit"] or \
            obs["_selftest"]["line"] != base["_selftest"]["line"]:
        hits.append("selftest")
    bad_fixtures = [k for k in FIXTURE_KEYS[family]
                    if any(base[k][f] != obs[k][f] for f in ("exit", "counts", "classes")
                           if f in obs[k]) or (family == "scope" and any(
                               base[k][f] != obs[k][f] for f in ("findings", "cases")))]
    if bad_fixtures:
        hits.append("fixture:" + ",".join(bad_fixtures))
    return "+".join(hits) or "none"


def main() -> int:
    bases = {fam: load(S / rel) for fam, (rel, _) in FAMILY.items()}
    rows = []
    for src in ("rows-gate.jsonl", "rows-scope.jsonl", "rows-bind.jsonl"):
        for line in (S / src).read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    order = {"gate": 0, "round72-round-scope.py": 1, "round72-receipt-tip-binding.py": 2}
    rows.sort(key=lambda r: (order.get(r["tool"], 9), r["id"]))

    out, lines = [], []
    for r in rows:
        fam = r["id"][0]
        family = FAMILY[fam][1]
        obs = load(LOGS / f"{r['id']}.json")
        by = killed_by(r["id"], bases[fam], obs, family)
        r["killed_by"] = by
        out.append(r)
        lines.append(f"{r['id']}\t{r['tool']}\tkilled_by={by}\t{r['verdict']}")

    with (W / "mutants.tsv").open("w", encoding="utf-8") as fh:
        fh.write("id\ttool\tmutation\tverdict\tcommand\tevidence\n")
        for r in out:
            ev = f"killed_by={r['killed_by']}; {r['evidence']}"
            fh.write("\t".join(str(r[k]).replace("\t", " ") for k in
                               ("id", "tool", "mutation", "verdict", "command")) + f"\t{ev}\n")
    (W / "logs" / "kill-sources.tsv").write_text("id\ttool\tkilled_by\tverdict\n"
                                                 + "\n".join(lines) + "\n", encoding="utf-8")
    shipped_only = [r["id"] for r in out if r["killed_by"] == "selftest"]
    fixture_only = [r["id"] for r in out if r["killed_by"].startswith("fixture:")]
    both = [r["id"] for r in out if "+" in r["killed_by"]]
    print(f"killed={len(out)} selftest-only={shipped_only}")
    print(f"fixture-only={fixture_only}")
    print(f"both={both}")
    for r in out:
        print(f"  {r['id']} {r['killed_by']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
