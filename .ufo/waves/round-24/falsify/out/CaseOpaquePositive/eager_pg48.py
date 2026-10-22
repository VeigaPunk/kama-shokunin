#!/usr/bin/env python3
"""PG48 discriminating power against an EAGER blanket-closure precondition.

PM11 (the shipped any-hole mutant) patches RepoStore.missing to raise.
On PG48 the candidate never consults the hole set (every citation
resolves), so PM11 is inert there -- which is why the shipped PM11 run
does not list PG48 among its failed rows even though PG48 is in PM11's
expect_rows.

This probe builds the behaviour the amendment actually forbids: a
candidate that computes the hole set EAGERLY (both audited stores) and
refuses whenever any hole exists -- a blanket closure precondition.
PG48 must kill it (exit 2 instead of exit 0).  If it does, PG48 has real
discriminating power and the gap is confined to the PM11 mutant's
lazy-call-site wiring (a fixture/inventory accuracy issue, not a source
defect).

Offline, benign, local fixtures only; production is never edited.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive/repo")
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaquePositive")
AUDIT = REPO / "tools/report-landing-audit.py"
EAGER = SCRATCH / "eager-blanket-audit.py"

source = AUDIT.read_text(encoding="utf-8")
ANCHOR = 'if __name__ == "__main__":'
assert source.count(ANCHOR) == 1

EAGER_MUT = '''# --- eager blanket-closure precondition mutation (PROBE ONLY) ---
def _probe_install_eager_blanket():
    _cls = globals()["RepoStore"]
    _original_build = globals()["build_store"]

    def _patched_build(repo, root):
        store = _original_build(repo, root)
        missing, opaque = store.missing()
        if missing or opaque:
            raise EvalError(
                f"{repo}: unknown: unavailable required object: "
                f"{len(missing) + len(opaque)} hole(s) in the store")
        return store

    globals()["build_store"] = _patched_build


_probe_install_eager_blanket()
# --- end eager blanket-closure precondition mutation ---'''

mutated = source.replace(ANCHOR, EAGER_MUT + "\n" + ANCHOR)
compile(mutated, str(EAGER), "exec")
EAGER.write_text(mutated, encoding="utf-8")

env = dict(os.environ)
env["TMPDIR"] = str(SCRATCH / "tmp")
p = subprocess.run(
    [sys.executable, str(REPO / "tests/report-audit/promisor-grid.py"),
     "--arm", "current", "--current", str(EAGER),
     "--case", "PG48-opaque-unused-tree-no-unresolved-token", "--json"],
    capture_output=True, env=env, cwd=str(REPO), timeout=600)
doc = json.loads(p.stdout.decode())
row = doc["arms"]["current"]["rows"][0]
print(json.dumps({
    "probe_mutant": "eager-blanket-closure-precondition",
    "production_auditor_sha256": hashlib.sha256(
        AUDIT.read_bytes()).hexdigest(),
    "probe_copy_sha256": hashlib.sha256(EAGER.read_bytes()).hexdigest(),
    "grid_exit": p.returncode,
    "mutated_exit": row["exit"],
    "mutated_met_amended": row["met_amended"],
    "mutated_stderr_tail": row["stderr_tail"][:300],
    "grid_violations": doc["arms"]["current"]["violations"],
    "violating_cases": doc["arms"]["current"]["violating_cases"],
    "PG48_kills_eager_blanket_precondition": (
        row["exit"] != 0 or not row["met_amended"]),
}, indent=1))
