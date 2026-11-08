#!/usr/bin/env python3
"""Per-check discriminating power of the round-96 C3 disclosure audit AT THE NEW TIP (amendment 2)."""
import re
import subprocess
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
BASE = "5d43528badc31ad6c0ca1848c00561f531924e4d"
HEAD = "HEAD"


def show(rev, path):
    p = subprocess.run(["git", "-C", str(LANE), "show", f"{rev}:{path}"], capture_output=True)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def checks(rev):
    probe = show(rev, "tools/kama-probe.sh") or ""
    counter = show(rev, "tools/round96-router-budget.py") or ""
    score = show(rev, "SCORECARD.md") or ""
    out = []
    m = re.search(r"^MAX_STEPS = ([0-9_]+)", probe, re.M)
    ms = int(m.group(1).replace("_", "")) if m else None

    out.append(("c1 max_steps==5M and '6 steps per tensor header' present in probe",
                ms == 5_000_000 and "6 steps per tensor header" in probe))
    out.append(("c2 old 'MAX_TENSORS = 1_000_000' + 'the ceiling is 1,000,000' both present",
                ("MAX_TENSORS = 1_000_000" in probe) and ("the ceiling is 1,000,000" in probe)))
    out.append(("c3 counter docstring '20 + 25 * npaths' and not '20 + 15 * ncand'",
                ("20 + 25 * npaths" in counter) and ("20 + 15 * ncand" not in counter)))
    parts = counter.split('"""')
    doc = parts[1] if len(parts) >= 3 else counter
    want = "{:,}".format(ms).replace(",", " ") if ms else None
    out.append((f"c4 counter docstring states MAX_STEPS ({want})",
                want is not None and want in doc.replace(",", " ")))
    row = None
    for line in score.splitlines():
        if "router-byte-decided" in line and line.startswith("|"):
            row = line
    m2 = re.search(r"`([0-9a-f]{4,40})`", row or "")
    ev = m2.group(1) if m2 else None
    ok = anc = False
    if ev:
        ok = subprocess.run(["git", "-C", str(LANE), "cat-file", "-e", f"{ev}^{{commit}}"],
                            capture_output=True).returncode == 0
        anc = subprocess.run(["git", "-C", str(LANE), "merge-base", "--is-ancestor", ev, rev],
                             capture_output=True).returncode == 0
    out.append((f"c5 capability evidence pointer ({ev}) resolves AND ancestor of rev",
                bool(ev) and ok and anc))
    out.append(("c6 probe contains '20 + 25 * npaths'", "20 + 25 * npaths" in probe))
    return out, ev


for rev in (BASE, HEAD):
    rows, ev = checks(rev)
    print(f"\n--- {rev} (pointer {ev}) ---")
    for name, ok in rows:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")

b, _ = checks(BASE)
h, _ = checks(HEAD)
print("\n=== DISCRIMINATION ===")
for (n, bv), (_, hv) in zip(b, h):
    tag = ("DISCRIMINATES" if (not bv and hv)
           else "NO DISCRIMINATION (true of base)" if bv
           else "REGRESSED" if hv else "both fail")
    print(f"  {tag:38s} {n}")

# Does the probe comment still contradict SKILL.md at HEAD?
probe = show(HEAD, "tools/kama-probe.sh") or ""
skill = show(HEAD, "SKILL.md") or ""
print("\n=== probe comment vs SKILL table at HEAD ===")
print("  probe says '6 steps per tensor header':", "6 steps per tensor header" in probe)
print("  probe says '~833 333 tensor headers'   :", "~833 333 tensor headers" in probe)
print("  SKILL says '`5 + nd` steps'            :", "`5 + nd` steps" in skill)
print("  SKILL says '833,332'                   :", "833,332" in skill)
print("  SKILL says '833,333'                   :", "833,333" in skill)
print("  -> the C3 audit REQUIRES the probe to keep the string '6 steps per tensor header':",
      '"6 steps per tensor header" not in probe' in show(HEAD, "tools/round96-disclosure-audit.py"))
