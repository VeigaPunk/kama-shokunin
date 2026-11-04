import json, os, re, subprocess, sys
from pathlib import Path
S = Path("/fast/scratch/hyaku/kama-r71/MT01MutantGates")
HOST = S / "host"; F = S / "fixtures/c3"; TMP = S / "tmp"
tool = sys.argv[1]; tag = sys.argv[2] if len(sys.argv) > 2 else "run"
base_rev = (S/"tmp"/"c3-rewritten-base.txt").read_text().split("=",1)[1].strip()
CASES = {
 "base": ["--repo", str(F/"base")],
 "corrected": ["--repo", str(F/"corrected")],
 "flipped": ["--repo", str(F/"flipped")],
 "wrongtag": ["--repo", str(F/"wrongtag")],
 "rewritten": ["--repo", str(F/"rewritten"), "--base", base_rev],
}
env = dict(os.environ); env["TMPDIR"] = str(TMP)
res = {}
for name, extra in CASES.items():
    argv = [sys.executable, tool] + extra
    p = subprocess.run(argv, cwd=str(HOST), capture_output=True, text=True, env=env, timeout=600)
    line = next((l for l in p.stdout.splitlines() if l.startswith("PROVINCE_HOST_CLAIMS ")), "<none>")
    rew = [l for l in p.stdout.splitlines() if l.startswith("PROVINCE_HOST_CLAIMS_REWRITTEN")]
    res[name] = {"exit": p.returncode, "line": line, "rewritten": rew,
                 "stdout": p.stdout, "stderr": p.stderr}
(S/"logs"/f"c3-{tag}.json").write_text(json.dumps(res, indent=1))
for name, r in res.items():
    print(f"{name:11s} exit={r['exit']} {r['line']}" + (f" REWRITTEN={r['rewritten']}" if r['rewritten'] else ""))
