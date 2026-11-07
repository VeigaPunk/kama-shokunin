#!/usr/bin/env python3
"""Round-92 C2 pre-freeze forgery controls for tools/round92-linear-paths.py.

Each forgery is the pre-freeze candidate probe (controls/c2-candidate-probe.sh) with ONE sabotage that keeps it
fast but wrong; each is scored with --probe-file (prints probe=override, can never meet the predicate) and must
fail the cell named:
  F1 jstr truncates every value to its first 1 MiB          -> L1/L2 served_scaled=0
  F2 router_refine reads only the first 1 000 router entries -> L4 misses the final loaded entry
  F3 served_persist keeps only the first 1 000 ids           -> L5 served_rule=0
Usage: c2-forgeries.py --lane DIR --work DIR --out-dir DIR
Writes <out-dir>/c2-f{1,2,3}.out; prints FORGERY lines; exit 0 when each forgery fails its named cell.
"""
import argparse, re, subprocess, sys
from pathlib import Path

SAB = {
    "F1": ("  local s=${1-} LC_ALL=C\n", "  local s=${1-} LC_ALL=C\n  s=${s:0:1048576}\n", ["L1-jstr-backslash", "L2-jstr-quote"]),
    "F2": ('router_match "$exp_n"; fi)', 'router_match "$exp_n"; fi | head -n 1000)', ["L4-router-same-id"]),
    "F3": ("      for (i = 1; i <= n; i++) {\n", "      if (n > 1000) n = 1000\n      for (i = 1; i <= n; i++) {\n", ["L5-snapshot-16000"]),
}

ap = argparse.ArgumentParser()
for x in ("--lane", "--work", "--out-dir"):
    ap.add_argument(x, required=True)
a = ap.parse_args()
lane = Path(a.lane).resolve()
cand = (lane / ".ufo/waves/round-92/controls/c2-candidate-probe.sh").read_text()
good = 0
for fid, (old, new, cells) in SAB.items():
    if cand.count(old) != 1:
        print(f"FORGERY {fid} SETUP-FAILED anchor count {cand.count(old)}")
        continue
    w = Path(a.work) / fid
    w.mkdir(parents=True, exist_ok=True)
    pf = w / "probe.sh"
    pf.write_text(cand.replace(old, new, 1))
    p = subprocess.run([sys.executable, str(lane / "tools/round92-linear-paths.py"), "--repo", str(lane),
                        "--rev", "HEAD", "--work", str(w), "--probe-file", str(pf)], capture_output=True, text=True)
    out = Path(a.out_dir) / f"c2-{fid.lower()}.out"
    out.write_text(f"# forgery {fid}: {new.strip()!r} cmd: tools/round92-linear-paths.py --probe-file <sabotaged candidate>\n"
                   + p.stdout + f"exit={p.returncode}\n")
    failed = {m.group(1) for m in re.finditer(r"^LINEAR_PATHS_CELL (\S+) ok=0", p.stdout, re.M)}
    ok = p.returncode == 1 and all(c in failed for c in cells) and "probe=override" in p.stdout
    good += ok
    print(f"FORGERY {fid} exit={p.returncode} failed_cells={sorted(failed)} named={cells} {'as-expected' if ok else 'UNEXPECTED'}")
print(f"C2_FORGERIES forgeries={len(SAB)} as_expected={good}")
sys.exit(0 if good == len(SAB) else 1)
