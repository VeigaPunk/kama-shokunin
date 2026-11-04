import json, os, re, subprocess, sys
from pathlib import Path
S = Path("/fast/scratch/hyaku/kama-r71/MT01MutantGates")
HOST = S / "host"
F = S / "fixtures"
TMP = S / "tmp"
tool = sys.argv[1]
tag = sys.argv[2] if len(sys.argv) > 2 else "run"
FIX = ["c1-green", "fx-uncommitted", "fx-stale", "fx-missing", "fx-dirty", "fx-crlf"]
env = dict(os.environ); env["TMPDIR"] = str(TMP)
res = {}
for name in FIX:
    argv = [sys.executable, tool, "--repo", str(F/name), "--round", "71", "--tip", "master"]
    p = subprocess.run(argv, cwd=str(HOST), capture_output=True, text=True, env=env, timeout=300)
    line = next((l for l in p.stdout.splitlines() if l.startswith("PRE_REPORT ")), "<none>")
    arms = {m.group(1): m.group(2) for l in p.stdout.splitlines()
            if (m := re.match(r"PRE_REPORT_ARM (\S+) exit=\S+ (ok|FAIL) (.*)", l))}
    res[name] = {"exit": p.returncode, "line": line, "arms": arms,
                 "stdout": p.stdout, "stderr": p.stderr}
out = S/"logs"/f"c1-{tag}.json"
out.write_text(json.dumps(res, indent=1))
for name, r in res.items():
    print(f"{name:16s} exit={r['exit']} {r['line']}")
    for a in ("round-clean", "worktree-landing", "newest-closure", "selfdesc", "receipt-audit"):
        st = r["arms"].get(a, "")
        if st != "ok":
            print(f"    {a}: {st[:150]}")
