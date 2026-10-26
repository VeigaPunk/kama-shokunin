#!/usr/bin/env python3
"""build_separability_r43.py - kama round-43 separability controls.

Each claim's own file set alone, applied to the freeze commit, scored by all
three frozen counters.  Usage:

    build_separability_r43.py <lane clone> <freeze commit> <tip commit> <out dir>

The lane clone is read-only; every write happens in a throwaway clone under
/tmp-seats with a fixture identity that is used nowhere else.

Why the freeze commit, not the round base: the three counters and the base
receipts are committed at the freeze, and the counters read the tree they are
run against.  A control built on the round base (6897ead) would score the
counters against a tree that lacks them, so `pop` drops to 28 and C1's `pins`
leg cannot see tools/round43-*.py at all (see controls/sep-c1-only-freeze.c1.out
against the same control built on the base: pins=3).

File sets (from preregistration.json `separability`):

  C1  SKILL.md, SCORECARD.md (calibration row + head text), README.md,
      corpus/SOURCES.md (the search-log correction line only)
  C2  tools/hexrun-census.py, registry/hexrun-ledger.tsv,
      .ufo/waves/round-43/c2/, the SCORECARD canonical-list row
  C3  corpus/knowledge/runtime-health-surface-processes.md, the two
      corpus/SOURCES.md rows, .ufo/waves/round-43/c3/, the lesson Gate,
      .ufo/waves/round-43/assimilation/, the corpus/README.md coverage line

C1 writes a registry row for the C2 counter that cites
`.ufo/waves/round-43/c2/base-unresolved.tsv`.  That file is frozen (committed
at the freeze commit), not a C2 deliverable, so a C1-only control keeps it.
Removing it is what controls/probe-c2dir.c1.out measures.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

LANE, FREEZE, TIP, OUT = sys.argv[1], sys.argv[2], sys.argv[3], os.path.abspath(sys.argv[4])
SEAT = os.environ.get("SEAT_DIR", "/fast/scratch/kama-r43/seats/W1K04")
os.makedirs(OUT, exist_ok=True)
os.makedirs(SEAT, exist_ok=True)

CTR = {
    "c1": "tools/round43-registry-audit.py",
    "c2": "tools/round43-hexrun-audit.py",
    "c3": "tools/round43-health-audit.py",
}
BASE = "6897ead55c24ba08c9ac0b09466d4fbfe005a459"


def show(repo, rev, path):
    p = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"show {rev}:{path} failed: {p.stderr.strip()}")
    return p.stdout


def table_extent(lines, start):
    """1-based inclusive extent of the markdown table starting at `start`."""
    i = start - 1
    while i + 1 < len(lines) and lines[i + 1].startswith("|"):
        i += 1
    return start, i


def score(d, rev, name):
    for tag, rel in CTR.items():
        args = [sys.executable, os.path.join(LANE, rel), "--repo", d,
                "--tip", rev, "--out", os.path.join(OUT, f"{name}.{tag}.out")]
        if tag == "c2":
            args += ["--seed", "42"]
        if tag == "c3":
            args += ["--base", BASE]
        p = subprocess.run(args, capture_output=True, text=True, cwd=LANE)
        with open(os.path.join(OUT, f"{name}.{tag}.out"), "a") as f:
            f.write(f"exit={p.returncode}\n")
        line = (p.stdout.splitlines() + [p.stderr.strip()])[1] if p.stdout.strip() else p.stderr.strip()
        print(f"{name:22} {tag}  {line[:130]}  exit={p.returncode}")


def new_clone(tag):
    d = tempfile.mkdtemp(prefix=f"r43sep-{tag}-", dir=SEAT)
    subprocess.run(["git", "clone", "-q", "--no-local", LANE, d], check=True)
    top = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True).stdout.strip()
    if os.path.realpath(top) != os.path.realpath(d):
        raise RuntimeError("sandbox toplevel mismatch")
    return d


def commit(d, msg):
    subprocess.run(["git", "-C", d, "add", "-A"], check=True)
    subprocess.run(["git", "-C", d, "-c", "user.name=r43-sep",
                    "-c", "user.email=r43-sep@fixture.invalid",
                    "commit", "-q", "-m", msg], check=True)
    return subprocess.run(["git", "-C", d, "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


# ---------------------------------------------------------------- C1 only
d = new_clone("c1")
subprocess.run(["git", "-C", d, "checkout", "-q", "--detach", FREEZE], check=True)
for path in ("SKILL.md", "README.md"):
    open(os.path.join(d, path), "w").write(show(LANE, TIP, path))
src = show(LANE, FREEZE, "corpus/SOURCES.md")
corr = [l for l in show(LANE, TIP, "corpus/SOURCES.md").split("\n")
        if l.startswith("- **2026-10-25 - correction to the round-42 entry")]
if len(corr) != 1:
    raise RuntimeError(f"expected exactly one C1 correction line, got {len(corr)}")
bl = src.split("\n")
k = max(i for i, l in enumerate(bl) if "round-42 K05 engine-side sources" in l)
open(os.path.join(d, "corpus/SOURCES.md"), "w").write("\n".join(bl[:k + 1] + [""] + corr + bl[k + 1:]))
sc = show(LANE, TIP, "SCORECARD.md")
sc = re.sub(r"^\| hexrun-census \|.*\n", "", sc, flags=re.M)          # C2's canonical row
i = sc.find("## Round 43 — instrument registry reconciled")
if i >= 0:
    sc = sc[:i]                                                          # C2/C3's measured-results section
open(os.path.join(d, "SCORECARD.md"), "w").write(sc)
score(d, commit(d, "sep: C1 file set only"), "sep-c1-only")

# ---------------------------------------------------------------- C2 only
d = new_clone("c2")
subprocess.run(["git", "-C", d, "checkout", "-q", "--detach", TIP], check=True)
for path in ("SKILL.md", "README.md", "corpus/SOURCES.md", "corpus/README.md"):
    subprocess.run(["git", "-C", d, "checkout", "-q", BASE, "--", path], check=True)
for path in ("corpus/knowledge/runtime-health-surface-processes.md",
             "corpus/lessons/round-43.md"):
    os.remove(os.path.join(d, path))
for sub in (".ufo/waves/round-43/c3", ".ufo/waves/round-43/assimilation"):
    shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
# C1's HEAD MIRROR capability table reverts to base; C2's round-43 canonical list stays.
land = show(LANE, TIP, "SCORECARD.md").split("\n")
base = show(LANE, BASE, "SCORECARD.md").split("\n")
b0, b1 = table_extent(base, 119)
l0, l1 = table_extent(land, 119)
open(os.path.join(d, "SCORECARD.md"), "w").write("\n".join(land[:l0 - 1] + base[b0 - 1:b1] + land[l1:]))
score(d, commit(d, "sep: C2 file set only"), "sep-c2-only")

# ---------------------------------------------------------------- C3 only
d = new_clone("c3")
subprocess.run(["git", "-C", d, "checkout", "-q", "--detach", BASE], check=True)
for path in ("corpus/knowledge/runtime-health-surface-processes.md",
             "corpus/lessons/round-43.md"):
    os.makedirs(os.path.join(d, os.path.dirname(path)), exist_ok=True)
    open(os.path.join(d, path), "w").write(show(LANE, TIP, path))
for sub in (".ufo/waves/round-43/c3", ".ufo/waves/round-43/assimilation"):
    os.makedirs(os.path.join(d, sub), exist_ok=True)
    p = subprocess.run(["git", "-C", LANE, "archive", TIP, sub],
                       capture_output=True)
    if p.returncode == 0:
        subprocess.run(["tar", "-x", "-C", d], input=p.stdout, check=True)
base_src = show(LANE, BASE, "corpus/SOURCES.md").split("\n")
rows = [l for l in show(LANE, TIP, "corpus/SOURCES.md").split("\n")
        if l.startswith("| S480 ") or l.startswith("| S481 ")]
if len(rows) != 2:
    raise RuntimeError(f"expected two C3 rows, got {len(rows)}")
last = max(i for i, l in enumerate(base_src) if l.startswith("| S"))
open(os.path.join(d, "corpus/SOURCES.md"), "w").write(
    "\n".join(base_src[:last + 1] + rows + base_src[last + 1:]))
base_readme = show(LANE, BASE, "corpus/README.md")
land_readme = show(LANE, TIP, "corpus/README.md")
i = land_readme.find("## Coverage map — round 43 addition")
open(os.path.join(d, "corpus/README.md"), "w").write(
    base_readme.rstrip("\n") + "\n\n" + land_readme[i:])
score(d, commit(d, "sep: C3 file set only"), "sep-c3-only")

print(f"controls written to {OUT}")
