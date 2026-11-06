#!/usr/bin/env python3
"""make-candidates.py - derive the candidate late-register variants for R4.

Read-only against the lane. Reads the audit JSON at the lane tip (saved by the caller at
<out>/audit-head.json), the committed registers at the same tip, and the frozen generator
tools/round81-late-rows.py (imported, not re-implemented).

  A  append-only-late.minus-spurious.tsv : the committed register minus every row whose
     (commit, file, line_sha256) triple the audit at the tip no longer reports as undisclosed
     (deletions only; no other cell changes).
  B  append-only-late.corrected-r88.tsv  : A plus one generated row (round 89 accepting round 86)
     for every triple missing from the round-88 population (plans/round-88-claims.md base).
  C  append-only-late.corrected-r89.tsv  : A plus one generated row for every triple missing from
     the round-89 population (plans/round-89-claims.md base) -- the shape the pre-report gate
     runs at round close (`round81-append-debt.py --round 89`).

Usage: make-candidates.py --repo LANE --out OUTDIR --audit-json FILE
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

LATE = "registry/append-only-late.tsv"
FROZEN = "registry/append-only-accepted.tsv"
HEADER = "commit\tfile\tline_sha256\tcount\tclass\tnote"
PLAN = "plans/round-{round}-claims.md"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} exit={proc.returncode}: {proc.stderr.strip()}")
    return proc.stdout


def rows_of(text: str) -> list[tuple[str, ...]]:
    return [tuple(line.split("\t")) for line in text.splitlines()[1:] if line.strip()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--audit-json", required=True)
    ap.add_argument("--accepting-round", type=int, default=89)
    ap.add_argument("--base-rounds", default="88,89")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    out = Path(args.out).resolve()
    data = json.loads(Path(args.audit_json).read_text(encoding="utf-8"))
    to = data["to"]
    generator = load_module(repo / "tools/round81-late-rows.py", "late_rows")
    population = {(e["commit"], e["file"]): e for e in data["events"]
                  if e["undisclosed"] and e["status"] != "restored"}
    live = {(c, f, u["line_sha256"]) for (c, f), e in population.items() for u in e["undisclosed"]}
    committed = rows_of(git(repo, "show", f"{to}:{LATE}"))
    frozen = {(r[0], r[1], r[2]) for r in rows_of(git(repo, "show", f"{to}:{FROZEN}"))}
    have = {(r[0], r[1], r[2]) for r in committed}
    spurious = [r for r in committed if (r[0], r[1], r[2]) not in live]
    kept = [r for r in committed if (r[0], r[1], r[2]) in live]

    def missing_for(base_round: int) -> list[tuple[str, str, str]]:
        base = generator.BASE_RE.search((repo / PLAN.format(round=base_round)).read_text()).group(1)

        def ancestor(commit: str) -> bool:
            return subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor",
                                   commit, base], capture_output=True).returncode == 0

        return sorted((c, f, u["line_sha256"])
                      for (c, f), e in population.items() if ancestor(c) for u in e["undisclosed"]
                      if (c, f, u["line_sha256"]) not in frozen
                      and (c, f, u["line_sha256"]) not in have)

    def render(rows: list[tuple[str, ...]]) -> str:
        return HEADER + "\n" + "".join("\t".join(r) + "\n" for r in rows)

    def rows_for(base_round: int) -> list[tuple[str, ...]]:
        base = generator.BASE_RE.search((repo / PLAN.format(round=base_round)).read_text()).group(1)
        generated = generator.generate(repo, args.accepting_round, to, base, population)
        want = set(missing_for(base_round))
        picked = [r for r in generated if (r[0], r[1], r[2]) in want]
        if sorted(r[:3] for r in picked) != sorted(want):
            raise SystemExit(f"GENERATOR_MISMATCH at base round {base_round}")
        return picked

    (out / "append-only-late.minus-spurious.tsv").write_text(render(kept), encoding="utf-8")
    report = {"to": to, "committed_rows": len(committed), "spurious": len(spurious),
              "kept": len(kept), "spurious_rows": [list(r) for r in spurious], "variants": {}}
    for base_round in (int(x) for x in args.base_rounds.split(",")):
        picked = rows_for(base_round)
        name = f"append-only-late.corrected-r{base_round}.tsv"
        (out / name).write_text(render(kept + picked), encoding="utf-8")
        report["variants"][f"r{base_round}"] = {"rows": len(kept) + len(picked),
                                                "added": len(picked),
                                                "added_rows": [list(r) for r in picked]}
    (out / "candidate-rows.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"MAKE_CANDIDATES to={to[:12]} committed={len(committed)} spurious={len(spurious)} "
          f"kept={len(kept)} " + " ".join(f"{k}+{v['added']}={v['rows']}"
                                          for k, v in report["variants"].items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
