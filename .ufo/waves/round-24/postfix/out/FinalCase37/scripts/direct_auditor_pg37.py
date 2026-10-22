import importlib.util, json, subprocess, sys, os
from pathlib import Path
CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase37/clone")
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
grid = load("promisor_grid", CLONE / "tests/report-audit/promisor-grid.py")
root = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase37/tmp-direct")
root.mkdir(parents=True, exist_ok=True)
tmp = root / "000"; tmp.mkdir(parents=True, exist_ok=True)
built = grid.BUILDERS["c_unused_missing_blob_fabricated_plain"](root, tmp)
lane, fleet = built["lane"], built["fleet"]
print("REMOTES lane:", repr(grid.git(lane, "remote", "-v")))
print("REMOTES fleet:", repr(grid.git(fleet, "remote", "-v")))
print("REPORT TEXT:\n" + grid.git(fleet, "show", "HEAD:.ufo/reports/round-1/kama.md"))
argv = [sys.executable, str(CLONE / "tools/report-landing-audit.py"),
        "--lane-repo", str(lane), "--fleet-repo", str(fleet),
        "--rounds", "1", "--json", "--no-errata"]
print("ARGV:", json.dumps(argv))
env = grid.env()
p = subprocess.run(argv, capture_output=True, env=env, cwd=str(tmp))
print("AUDITOR EXIT:", p.returncode)
print("AUDITOR STDERR:", repr(p.stderr.decode()))
print("AUDITOR STDOUT:", p.stdout.decode())
