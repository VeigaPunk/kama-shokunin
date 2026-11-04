import json, os, subprocess, sys
from pathlib import Path
S = Path("/fast/scratch/hyaku/kama-r71/MT01MutantGates")
HOST = S/"host"; F = S/"fixtures/c3"; P = S/"pristine"
env = dict(os.environ); env["TMPDIR"] = str(S/"tmp")
base_rev = (S/"tmp"/"c3-rewritten-base.txt").read_text().split("=",1)[1].strip()
MUTS = sorted((HOST/"tools").glob("round71-province-host-claims-m*.py"))
CASES = {"base": ["--repo", str(F/"base")], "corrected": ["--repo", str(F/"corrected")],
         "flipped": ["--repo", str(F/"flipped")], "wrongtag": ["--repo", str(F/"wrongtag")],
         "rewritten": ["--repo", str(F/"rewritten"), "--base", base_rev]}
def run(argv, timeout=600):
    p = subprocess.run(argv, cwd=str(HOST), capture_output=True, text=True, env=env, timeout=timeout)
    return p.returncode, p.stdout, p.stderr
res = {}
for mut in MUTS:
    tag = mut.stem; rec = {}
    scratch = S/"tmp"/f"c3-{tag}"; scratch.mkdir(parents=True, exist_ok=True)
    rc, out, err = run([sys.executable, str(mut), "--selftest", "--scratch", str(scratch)], 900)
    line = next((l for l in out.splitlines() if l.startswith("PROVINCE_HOST_CLAIMS_SELFTEST ")), "<none>")
    fails = [l for l in out.splitlines() if l.startswith("[FAIL]")]
    rec["ST"] = {"exit": rc, "line": line, "fails": fails[:8]}
    rec["FIX"] = {}
    for name, extra in CASES.items():
        rc, out, err = run([sys.executable, str(mut)] + extra)
        line = next((l for l in out.splitlines() if l.startswith("PROVINCE_HOST_CLAIMS ")), "<none>")
        rew = [l for l in out.splitlines() if l.startswith("PROVINCE_HOST_CLAIMS_REWRITTEN")]
        rec["FIX"][name] = {"exit": rc, "line": line, "rewritten": rew,
                            "stderr": err.strip().splitlines()[:1]}
    res[tag] = rec
    print(tag, rec["ST"]["line"], "| base", rec["FIX"]["base"]["exit"],
          "| corrected", rec["FIX"]["corrected"]["exit"],
          "| flipped", rec["FIX"]["flipped"]["exit"],
          "| wrongtag", rec["FIX"]["wrongtag"]["exit"],
          "| rewritten", rec["FIX"]["rewritten"]["exit"], flush=True)
(S/"logs"/"c3-matrix.json").write_text(json.dumps(res, indent=1))
print("WROTE", S/"logs"/"c3-matrix.json")
