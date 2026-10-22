#!/usr/bin/env python3
"""Differential probes inside the UnrelatedFakeNotes family.

Same fixture family (lane with one dropped unrelated blob + a Notes-section
citation), three report bodies:

  A  as-built                     -> the graded PG41/PG42 body
  B  the citation replaced by the OID of the missing blob
     (same hole, token now names unavailable content) -> expect refusal
  C  the citation removed entirely (only the unrelated hole remains)
     -> expect the clean verdict

The probes change nothing in the repository: they build their own offline
fixture and only rewrite the scratch fleet report.
"""
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

GRID = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseUnrelatedFakeNotes/repo"
            "/tests/report-audit/promisor-grid.py")
ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseUnrelatedFakeNotes"
            "/probe-root2")
REPO = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseUnrelatedFakeNotes/repo")
AUDIT = REPO / "tools/report-landing-audit.py"

spec = importlib.util.spec_from_file_location("pg", GRID)
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)


def git(repo, *args):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       env=pg.env())
    if p.returncode:
        raise SystemExit(f"git {' '.join(args)}: {p.stderr.decode()}")
    return p.stdout.decode()


def inventory(repo):
    return set(git(repo, "cat-file", "--batch-all-objects",
                   "--batch-check=%(objectname)").split())


def build(tag, body):
    tmp = ROOT / tag
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    built = pg.BUILDERS["c_unused_missing_blob_fabricated_notes_promisor"](
        ROOT, tmp)
    lane, fleet, shas = built["lane"], built["fleet"], built["shas"]
    if body is not None:
        pg.commit(fleet, "fleet", 2000, "round-1: report v2", pg.REL, body)
    before = {"lane": inventory(lane), "fleet": inventory(fleet)}
    code, out, err, to = pg.run_auditor(AUDIT, lane, fleet, tmp, False)
    after = {"lane": inventory(lane), "fleet": inventory(fleet)}
    return {
        "tag": tag,
        "missing_oids": built["premise"]["lane_missing"],
        "unused_blob_oid": shas.get("unused_blob"),
        "exit": code,
        "stderr": err.strip(),
        "stdout_is_json": bool(out.strip()) and out.strip().startswith("{"),
        "stdout_len": len(out),
        "timed_out": to,
        "objects_acquired": {k: sorted(after[k] - before[k]) for k in after},
        "defects": pg.observed_defects(out)[0],
        "summary": (json.loads(out)["summary"] if out.strip().startswith("{")
                    else None),
    }


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    body_a = None
    # read the as-built body from a fresh fixture so that A is the graded body
    tmp = ROOT / "asbuilt"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    built = pg.BUILDERS["c_unused_missing_blob_fabricated_notes_promisor"](
        ROOT, tmp)
    body_a = (Path(built["fleet"]) / pg.REL).read_text(encoding="utf-8")
    hole = built["shas"]["unused_blob"]
    body_b = body_a.replace(pg.FAKE, hole)
    body_c = "\n".join(l for l in body_a.split("\n")
                       if pg.FAKE not in l)
    out = {
        "A_as_built": build("A", None),
        "B_token_is_missing_blob_oid": build("B", body_b),
        "C_citation_removed": build("C", body_c),
    }
    print(json.dumps(out, indent=1, sort_keys=True))
    (ROOT / "differential.json").write_text(
        json.dumps(out, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
