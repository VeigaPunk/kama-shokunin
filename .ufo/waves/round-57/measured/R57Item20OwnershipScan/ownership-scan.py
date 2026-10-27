#!/usr/bin/env python3
"""Distinct case 41 independent test: counterpart-lane boundary for the canonical
self-assessment gate.

Read-only. No repo writes, no network. Every check must be able to fail.
Instrument and control bytes are read through git at HEAD, not from the mutable
working tree (a concurrent seat moved the control artifacts during this wave);
the working-tree churn is recorded in the C3 detail. Exit 0 iff every check passes.
"""
from __future__ import annotations

import glob
import os
import re
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
BASE = "b89bdab2cc114735ec5d331c6c610134258f7864"
REV = "HEAD"
rows = []


def check(name, ok, detail):
    rows.append((name, bool(ok), detail))


def git(*args):
    p = subprocess.run(["git", "-C", LANE, *args], capture_output=True)
    return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace")


def blob(path, rev=REV):
    rc, out, _ = git("cat-file", "-p", f"{rev}:{path}")
    return out.decode("utf-8", "replace") if rc == 0 else None


def read(path, rev=None):
    if rev:
        return blob(path, rev)
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


# A. The gate's source is lane-local: --repo defaults to ".", no sibling/home path.
gate = blob("tools/round42-selfdesc-reconcile.py")
check("A1_gate_repo_default_dot", 'ap.add_argument("--repo", default=".")' in gate,
      f'--repo default "." present at {REV}')
sib = re.findall(r"(home/vgpnk/|tsukuroi|souji|tameshi|kumitate|aggregator|protocol)",
                 gate)
check("A2_gate_no_sibling_ref", not sib, f"sibling refs={sorted(set(sib)) or 'none'}")

# B. The canonical-list heading exists only in kama's SCORECARD.
others = [d for d in sorted(glob.glob(os.path.join(FLEET, "*-shokunin")))
          if d != LANE]
for root in [FLEET, *others]:
    sc = os.path.join(root, "SCORECARD.md")
    n = 0
    if os.path.exists(sc):
        with open(sc, encoding="utf-8", errors="replace") as f:
            n = len(re.findall(r"canonical list as of round\s+\d+\*\*", f.read()))
    if n:
        check("B_canonical_heading_exclusive", False, f"{sc} carries {n}")
        break
else:
    check("B_canonical_heading_exclusive", True,
          f"canonical heading in 0 of {len(others) + 1} non-kama roots")

# C. maxN is derived from ^## Round N; 46 is a frozen-control literal only.
base_sc = blob("SCORECARD.md", BASE)
nums = [int(m.group(1)) for l in base_sc.split("\n")
        for m in [re.match(r"^## Round (\d+)", l)] if m]
check("C1_maxn_derived", max(nums) == 56 and "## Round 57" not in base_sc,
      f"base ^## Round N max={max(nums)}; Round 57 present={'## Round 57' in base_sc}")
check("C2_counter_has_no_46", "46" not in gate, "literal 46 absent from the gate source")

literal = "maxN=46"
ctrl_dir = ".ufo/waves/round-57/controls"
EXPECTED = {ctrl_dir + "/c1-noop.py", ctrl_dir + "/noop-c1.out",
            ctrl_dir + "/noop-c2.out", ctrl_dir + "/canonical-noop/SCORECARD.md",
            ctrl_dir + "/no-canonical/SCORECARD.md"}
rc, out, _ = git("grep", "-l", literal, REV, "--", ctrl_dir)
head_ctrls = {p.split(":", 1)[1] for p in out.decode().splitlines() if ":" in p}
rc, churn, _ = git("status", "--porcelain", ctrl_dir)
churn_s = " ".join(churn.decode().split()) or "clean"
rc, sc_hit, _ = git("grep", "-n", literal, REV, "--", "SCORECARD.md")
sc_parts = sc_hit.decode().split(":", 2)
sc_s = sc_parts[2].split(":", 1)[0] if len(sc_parts) == 3 else "none"
check("C3_46_only_in_frozen_artifacts",
      head_ctrls == EXPECTED,
      f"{REV} control carriers={sorted(p[len(ctrl_dir) + 1:] for p in head_ctrls)} "
      f"lane SCORECARD historical carrier line={sc_s} worktree_churn={churn_s}")

# D. A lane-owned canonical-row audit already passes at the frozen base.
p = subprocess.run([sys.executable, os.path.join(LANE, "tools/capability-repertoire-audit.py"),
                    "--repo", LANE, "--tip", BASE], capture_output=True, text=True)
line = (p.stdout.strip().splitlines() or [""])[-1]
check("D_canonical_audit_green", p.returncode == 0 and "met True" in line, line)

# E. Same-shaped sibling gates are lane-local (no kama reference).
for tool in ("tsukuroi-shokunin/tools/check-self-assessment.py",
             "souji-shokunin/tools/souji-capability-agreement.py",
             "souji-shokunin/tools/souji-capability-cells.py"):
    with open(os.path.join(FLEET, tool), encoding="utf-8", errors="replace") as f:
        body = f.read()
    check("E_sibling_scoped:" + os.path.basename(tool), "kama" not in body,
          "no kama reference" if "kama" not in body else "references kama")

# F. Counterpart owners are named in fleet docs.
protocol = open(os.path.join(FLEET, "PROTOCOL.md"), encoding="utf-8").read()
axes = open(os.path.join(FLEET, "AXES.md"), encoding="utf-8").read()
tameshi = open(os.path.join(FLEET, "tameshi-shokunin/PROVINCE.md"),
               encoding="utf-8").read()
check("F1_gate_is_lane_owned",
      "a committed, re-runnable verdict script a lane owns" in protocol,
      "PROTOCOL.md §Gate standard")
check("F2_fleet_axes_owner",
      "the protocol and aggregator lanes own the" in axes,
      "AXES.md line 4")
check("F3_tameshi_refuses_product_gate",
      "every lane's gate remains its own" in tameshi
      and "TWO\nindependent lanes" in tameshi,
      "tameshi PROVINCE Owns/Refuses")

# G. The verdict owner is a non-author integrator.
spot = blob("corpus/lessons/round-56-verifier-spotcheck.md")
check("G_verdict_non_author",
      "author: hyaku closure (non-author integrator" in spot,
      "round-56 spot-check author line")

failed = [r for r in rows if not r[1]]
for name, ok, detail in rows:
    print(f"{'PASS' if ok else 'FAIL'} {name} :: {detail}")
print(f"OWNERSHIP_SCAN pass={len(rows) - len(failed)} fail={len(failed)}")
sys.exit(0 if not failed else 1)
