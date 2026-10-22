#!/usr/bin/env python3
"""Apply the PM11 (any-hole-refusal) mutation to a SCRATCH COPY of the
auditor and re-run ONLY the PG48 grid case against it.

This proves PG48 is discriminating: the mutant (refuse whenever the store
has any hole) must make PG48 fail, so a candidate that passes PG48 cannot
be hiding a blanket hole-refusal behind a clean verdict.

Production is never edited; the mutant copy lives under scratch.
PM08 is never executed (static only) -- this touches PM11 only.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive/repo")
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive")
AUDIT = REPO / "tools/report-landing-audit.py"
MUT = SCRATCH / "pm11-audit.py"

source = AUDIT.read_text(encoding="utf-8")
ANCHOR = 'if __name__ == "__main__":'
assert source.count(ANCHOR) == 1, source.count(ANCHOR)

PM11 = '''# --- PM11 mutation: any hole refuses (over-refusal) ---
def _pm_install_any_hole():
    _cls = globals()["RepoStore"]
    _original = _cls.missing

    def _patched(self):
        missing, opaque = _original(self)
        if missing or opaque:
            raise EvalError(
                f"{self.path}: unknown: unavailable required object: "
                f"{len(missing) + len(opaque)} hole(s) in the store")
        return missing, opaque

    _cls.missing = _patched


_pm_install_any_hole()
# --- end PM11 mutation ---'''

mutated = source.replace(ANCHOR, PM11 + "\n" + ANCHOR)
compile(mutated, str(MUT), "exec")
MUT.write_text(mutated, encoding="utf-8")

env = dict(os.environ)
env["TMPDIR"] = str(SCRATCH / "tmp")
out = SCRATCH / "pm11-pg48.json"
p = subprocess.run(
    [sys.executable, str(REPO / "tests/report-audit/promisor-grid.py"),
     "--arm", "current", "--current", str(MUT),
     "--case", "PG48-opaque-unused-tree-no-unresolved-token", "--json"],
    capture_output=True, env=env, cwd=str(REPO), timeout=600)
doc = json.loads(p.stdout.decode())
row = doc["arms"]["current"]["rows"][0]
print(json.dumps({
    "mutant": "PM11-any-hole-refusal",
    "mutant_copy": str(MUT),
    "production_auditor_sha256_unchanged": __import__("hashlib").sha256(
        AUDIT.read_bytes()).hexdigest(),
    "grid_exit": p.returncode,
    "case": row["case"],
    "mutated_exit": row["exit"],
    "mutated_met_amended": row["met_amended"],
    "mutated_stderr_tail": row["stderr_tail"][:300],
    "grid_violations": doc["arms"]["current"]["violations"],
    "violating_cases": doc["arms"]["current"]["violating_cases"],
    "PG48_kills_PM11": (row["exit"] != 0 or not row["met_amended"]),
}, indent=1))
