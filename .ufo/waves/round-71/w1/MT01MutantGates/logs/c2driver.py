import json, os, re, shutil, subprocess, sys
from pathlib import Path
S = Path("/fast/scratch/hyaku/kama-r71/MT01MutantGates")
HOST = S/"host"; LIGHT = S/"hostlight"; LB = S/"landedbad"; P = S/"pristine"
env = dict(os.environ); env["TMPDIR"] = str(S/"tmp")
TOOLS = [HOST/"tools/census-waiver-boundary.py"] + sorted((HOST/"tools").glob("census-waiver-boundary-m*.py"))
def run(argv, cwd, timeout=1200):
    p = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, env=env, timeout=timeout)
    return p.returncode, p.stdout, p.stderr
def summ(out):
    line = next((l for l in out.splitlines() if l.startswith("BOUNDARY ")), "<none>")
    cases = {m.group(1): m.group(2) for l in out.splitlines()
             if (m := re.match(r"BOUNDARY_CASE (\d) (held|FAIL)", l))}
    shims = {m.group(1): m.group(2) for l in out.splitlines()
             if (m := re.match(r"BOUNDARY_SHIM (\S+) (rejected|SURVIVED)", l))}
    return line, cases, shims
res = {}
for mut in TOOLS:
    tag = "pristine" if mut.name == "census-waiver-boundary.py" else mut.stem
    rec = {}
    rc, out, err = run([sys.executable, str(mut), "--selftest"], HOST)
    st = next((l for l in out.splitlines() if l.startswith("BOUNDARY_SELFTEST pass=")), "<none>")
    rec["ST"] = {"exit": rc, "line": st,
                 "fails": [l for l in out.splitlines() if l.startswith("BOUNDARY_SELFTEST_FAIL")][:8]}
    rc, out, err = run([sys.executable, str(mut), "--census", "tools/round65-host-census.py"], HOST)
    line, cases, shims = summ(out)
    rec["R"] = {"exit": rc, "line": line, "case7": cases.get("7")}
    shutil.copy2(mut, LIGHT/"tools"/f"cwb-{tag}.py")
    shutil.copy2(mut, LB/"tools"/f"cwb-{tag}.py")
    rc, out, err = run([sys.executable, str(LIGHT/"tools"/f"cwb-{tag}.py"),
                        "--census", str(P/"shims/s4-refusal-as-fail.py")], LIGHT, 300)
    line, cases, shims = summ(out)
    rec["BAD"] = {"exit": rc, "line": line, "cases": cases}
    rc, out, err = run([sys.executable, str(LIGHT/"tools"/f"cwb-{tag}.py"),
                        "--shims", str(S/"shims-hole")], LIGHT, 300)
    line, cases, shims = summ(out)
    rec["HOLE"] = {"exit": rc, "line": line, "shims": shims, "case6": cases.get("6")}
    rc, out, err = run([sys.executable, str(LB/"tools"/f"cwb-{tag}.py"),
                        "--census", str(P/"round65-host-census.py")], LB, 300)
    line, cases, shims = summ(out)
    rec["LB"] = {"exit": rc, "line": line, "case7": cases.get("7")}
    res[tag] = rec
    print(tag, "| ST", rec["ST"]["exit"], rec["ST"]["line"],
          "| R", rec["R"]["exit"], rec["R"]["line"],
          "| BAD", rec["BAD"]["exit"], rec["BAD"]["line"],
          "| HOLE", rec["HOLE"]["exit"], rec["HOLE"]["line"],
          "| LB", rec["LB"]["exit"], rec["LB"]["line"], flush=True)
(S/"logs"/"c2-matrix-v2.json").write_text(json.dumps(res, indent=1))
print("WROTE", S/"logs"/"c2-matrix-v2.json")
