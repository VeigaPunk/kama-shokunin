"""Does the landed candidate auditor (working tree) match the preregistered
rule for a citation that NO audited repository holds and that the store does
not reference?  Preregistration: "A missing citation in any promisor-backed
repository is unknown, not proved absent: exit2 unless resolved locally by
another audited repository."
"""
import importlib.util, sys, tempfile, subprocess, json
from pathlib import Path
spec = importlib.util.spec_from_file_location("grid", "tests/report-audit/repo-state-grid.py")
grid = importlib.util.module_from_spec(spec); sys.modules["grid"]=grid
spec.loader.exec_module(grid)
CAND = "/fast/scratch/hyaku/kama-r24/ConnDocs/scratch/cand-audit.py"

def run(fn, label, rounds="1"):
    with tempfile.TemporaryDirectory(prefix="cand-") as tmp:
        lane, fleet, extra, marker = fn(Path(tmp))
        argv=[sys.executable, CAND,"--lane-repo",str(lane),"--fleet-repo",str(fleet),
              "--json","--rounds",rounds,"--no-errata"]
        p=subprocess.run(argv, capture_output=True, env=grid.env(), cwd=tmp)
        kinds=""
        if p.returncode in (0,1):
            try:
                d=json.loads(p.stdout)
                kinds=sorted({x['kind'] for r_ in d['results'] for x in r_['defects']})
            except Exception: kinds="unparseable"
        print(f"{label}: exit={p.returncode} kinds={kinds}")
        print(f"   stderr: {p.stderr.decode(errors='replace').strip()[:220]}")

print("F27: filter-only promisor remote, report cites a fabricated 40-hex")
run(grid.f_filter_promisor, "F27")
print()
print("T01: complete blobless clone (metadata only), report cites a real commit")
run(grid.t_blobless, "T01")
print()
print("F23: promisor pack, one reachable blob genuinely absent")
run(grid.f_promisor_pack, "F23")
