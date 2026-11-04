import json, os, re, subprocess, sys
from pathlib import Path
S = Path("/fast/scratch/hyaku/kama-r71/MT01MutantGates"); LIGHT = S/"hostlight"; P = S/"pristine"
env = dict(os.environ); env["TMPDIR"] = str(S/"tmp")
jf = S/"logs/c2-matrix-v2.json"; d = json.loads(jf.read_text())
def summ(out):
    line = next((l for l in out.splitlines() if l.startswith("BOUNDARY ")), "<none>")
    cases = {m.group(1): m.group(2) for l in out.splitlines() if (m := re.match(r"BOUNDARY_CASE (\d) (held|FAIL)", l))}
    shims = {m.group(1): m.group(2) for l in out.splitlines() if (m := re.match(r"BOUNDARY_SHIM (\S+) (rejected|SURVIVED)", l))}
    return line, cases, shims
for tag in ["pristine"] + [t for t in d if t != "pristine"]:
    f = LIGHT/"tools"/(f"cwb-{tag}.py" if tag != "pristine" else "census-waiver-boundary.py")
    p = subprocess.run([sys.executable, str(f), "--census", str(P/"round65-host-census.py"),
                        "--shims", str(S/"shims-hole")], cwd=str(LIGHT), capture_output=True, text=True, env=env)
    line, cases, shims = summ(p.stdout)
    d[tag]["HOLE"] = {"exit": p.returncode, "line": line, "shims": shims, "case6": cases.get("6")}
    print(tag, p.returncode, line, "| survivors:", [k for k,v in shims.items() if v=="SURVIVED"], "|", p.stderr.strip().splitlines()[:1])
jf.write_text(json.dumps(d, indent=1)); print("updated", jf)
