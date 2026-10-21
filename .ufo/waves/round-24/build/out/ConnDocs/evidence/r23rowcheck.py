"""Bounded check: what does the landed candidate do to the r23 grid's
promisor-relevant rows?  These are exactly the 'policy rows' whose
expectations the round-24 documents must record as changed."""
import importlib.util, sys, tempfile, subprocess, json
from pathlib import Path
spec = importlib.util.spec_from_file_location("grid", "tests/report-audit/repo-state-grid.py")
grid = importlib.util.module_from_spec(spec); sys.modules["grid"]=grid
spec.loader.exec_module(grid)
CAND = "/fast/scratch/hyaku/kama-r24/ConnDocs/scratch/cand-audit.py"
BASE = "/fast/scratch/hyaku/kama-r24/ConnDocs/scratch/tools/report-landing-audit.py"

ROWS = [("F06-lazy-fetch-command", grid.f_lazy_fetch, 2, None),
        ("F23-promisor-pack-without-config", grid.f_promisor_pack, 2, None),
        ("F27-filter-only-promisor-remote", grid.f_filter_promisor, 1,
         ["landed-unresolved", "unresolved-full-hash"]),
        ("C09-promisor-false-config", grid.c_promisor_false, 0, []),
        ("C10-orphan-promisor-marker", grid.c_orphan_marker, 0, []),
        ("T01-blobless-partial-clone", grid.t_blobless, 0, [])]

def run(aud, fn):
    with tempfile.TemporaryDirectory(prefix="r23row-") as tmp:
        lane, fleet, extra, marker = fn(Path(tmp))
        argv=[sys.executable, aud,"--lane-repo",str(lane),"--fleet-repo",str(fleet),
              "--json","--rounds","1","--no-errata"]
        p=subprocess.run(argv, capture_output=True, env=grid.env(), cwd=tmp)
        kinds=None
        if p.returncode in (0,1):
            try:
                d=json.loads(p.stdout)
                kinds=sorted({x['kind'] for r_ in d['results'] for x in r_['defects']})
            except Exception: kinds="unparseable"
        return p.returncode, kinds, p.stderr.decode(errors='replace').strip(), (marker.exists() if marker else False)

print(f"{'row':38s} {'r23 exp':9s} {'base':9s} {'candidate':10s} marker")
for name, fn, exp, kinds in ROWS:
    be, bk, berr, bm = run(BASE, fn)
    ce, ck, cerr, cm = run(CAND, fn)
    print(f"{name:38s} {str(exp)+' '+str(kinds):9s} {str(be):9s} {str(ce):10s} cand_marker={cm}")
    if ce == 2:
        print(f"    cand stderr: {cerr[:170]}")
    elif ck not in (None, kinds):
        print(f"    cand kinds : {ck}  (r23 expected {kinds})")
