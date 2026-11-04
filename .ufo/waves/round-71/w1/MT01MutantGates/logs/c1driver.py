import json, os, re, shutil, subprocess, sys
from pathlib import Path
S = Path("/fast/scratch/hyaku/kama-r71/MT01MutantGates")
HOST = S/"host"; F = S/"fixtures"
env = dict(os.environ); env["TMPDIR"] = str(S/"tmp")
TOOLS = [HOST/"tools/pre-report-gate.py"] + sorted((HOST/"tools").glob("pre-report-gate-m*.py"))
FIX = ["c1-green", "fx-uncommitted", "fx-stale", "fx-missing", "fx-dirty", "fx-crlf"]
def run(argv, timeout=300):
    p = subprocess.run(argv, cwd=str(HOST), capture_output=True, text=True, env=env, timeout=timeout)
    return p.returncode, p.stdout, p.stderr
res = {}
for mut in TOOLS:
    tag = "pristine" if mut.name == "pre-report-gate.py" else mut.stem; rec = {}
    work = S/"tmp"/f"st2-{tag}"; shutil.rmtree(work, ignore_errors=True); work.mkdir(parents=True)
    rc, out, err = run([sys.executable, str(mut), "--selftest", "--work", str(work)], 900)
    line = next((l for l in out.splitlines() if l.startswith("PRE_REPORT_SELFTEST pass=")), "<none>")
    rec["ST"] = {"exit": rc, "line": line, "fails": [l for l in out.splitlines() if l.startswith("FAIL ")][:8]}
    rec["FIX"] = {}
    for name in FIX:
        rc, out, err = run([sys.executable, str(mut), "--repo", str(F/name), "--round", "71", "--tip", "master"])
        v = next((l for l in out.splitlines() if l.startswith("PRE_REPORT ")), "<none>")
        bad = {m.group(1): m.group(3)[:120] for l in out.splitlines()
               if (m := re.match(r"PRE_REPORT_ARM (\S+) exit=(\d+) (FAIL .*)", l))}
        rec["FIX"][name] = {"exit": rc, "line": v, "failing_arms": bad}
    res[tag] = rec
    print(tag, rec["ST"]["line"], "| green", rec["FIX"]["c1-green"]["line"],
          "| uncommitted", rec["FIX"]["fx-uncommitted"]["line"],
          "| stale", rec["FIX"]["fx-stale"]["line"],
          "| missing", rec["FIX"]["fx-missing"]["line"],
          "| dirty", rec["FIX"]["fx-dirty"]["line"],
          "| crlf", rec["FIX"]["fx-crlf"]["line"], flush=True)
(S/"logs"/"c1-matrix-v2.json").write_text(json.dumps(res, indent=1))
print("WROTE", S/"logs"/"c1-matrix-v2.json")
