#!/usr/bin/env python3
"""R42A14 extension 2: does C1's canon() resolve to the round-42 canonical list or to
the head mirror table? Probe + a head-table mutant that keeps every other leg true."""
import importlib.util, os, re, shutil, subprocess, sys, tempfile

LANE = "/fast/scratch/kama-r42/seats/R42A14/clone"
SEAT = "/fast/scratch/kama-r42/seats/R42A14"
OUT = os.path.join(SEAT, "exp")
os.makedirs(OUT, exist_ok=True)
TIP = "3d9bd8d72366e281fab291874524130428ee423d"
ID = ["-c", "user.name=r42a14-fixture", "-c", "user.email=r42a14@fixture.invalid"]

spec = importlib.util.spec_from_file_location("c1", os.path.join(LANE, "tools/round42-selfdesc-reconcile.py"))
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)

text = subprocess.run(["git", "-C", LANE, "show", f"{TIP}:SCORECARD.md"],
                      capture_output=True, text=True, check=True).stdout
lines = text.split("\n")
hits = [(i + 1, m.group(1), lines[i][:110]) for i, l in enumerate(lines)
        for m in [re.search(r"canonical list as of round\s+(\d+)\*\*", l, re.I)] if m]
print("== canon() regex hits in SCORECARD.md at tip (line, round, text)")
for h in hits:
    print(h)
cn, rows = c1.canon(text)
print(f"== canon() chose round {cn} with {len(rows)} rows: {[r[0].strip('` *') for r in rows]}")
head_start = next(i for i, l in enumerate(lines) if l.strip() == "## Capabilities")
head_rows = c1.table_rows(lines[head_start + 1:])
print(f"== head ## Capabilities has {len(head_rows)} rows: {[r[0].strip('` *') for r in head_rows]}")
print(f"== canon rows identical to head rows: {rows == head_rows}")


def g(d, *a):
    return subprocess.run(["git", "-C", d, *a], check=True, capture_output=True, text=True).stdout


d = tempfile.mkdtemp(prefix="r42a14-mut-", dir=SEAT)
subprocess.run(["git", "clone", "-q", "--no-local", LANE, d], check=True)
assert os.path.realpath(g(d, "rev-parse", "--show-toplevel").strip()) == os.path.realpath(d), d
g(d, "checkout", "-q", "--detach", TIP)
sc = os.path.join(d, "SCORECARD.md")
src = open(sc).read()
before = src.count("| sources-registry | Curate where kama learns")
src = src.replace("| sources-registry | Curate where kama learns",
                  "| ghost-registry | Curate where kama learns", 1)  # head table only (first occurrence)
open(sc, "w").write(src)
print(f"== mutant: renamed first occurrence of sources-registry ({before} occurrences in tree text)")
g(d, "add", "-A")
subprocess.run(["git", "-C", d, *ID, "commit", "-q", "-m", "mutant: head names ghost-registry"], check=True)
rev = g(d, "rev-parse", "HEAD").strip()
out = os.path.join(OUT, "M1-head-ghost.c1.out")
p = subprocess.run([sys.executable, os.path.join(LANE, "tools/round42-selfdesc-reconcile.py"),
                    "--repo", d, "--tip", rev, "--out", out], capture_output=True, text=True, cwd=LANE)
with open(out, "a") as f:
    f.write(f"exit={p.returncode}\n")
print(f"== M1 tip={rev} exit={p.returncode}")
print(open(out).read())
print("sandboxM1", d)
