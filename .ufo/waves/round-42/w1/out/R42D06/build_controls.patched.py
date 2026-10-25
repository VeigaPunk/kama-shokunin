#!/usr/bin/env python3
"""Round-42 freeze controls: build sandbox revisions and score the three frozen counters.

Usage: build_controls.py <lane clone> <base commit> <out dir> <claim-source dir>
Every git write happens in a fresh mktemp sandbox clone (git -C "$D"); the
sandbox identity is fixture-only and never used outside it. <claim-source dir>
holds the working-tree copies of tools/digest-ledger.py (used only to build
shortcut controls that need a real tool).
"""
import os, re, shutil, subprocess, sys, tempfile

lane, base, out, src = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3]), sys.argv[4]
os.makedirs(out, exist_ok=True)
D = tempfile.mkdtemp(prefix="r42-controls-", dir=os.environ.get("R42_SANDBOX_PARENT", "/fast/scratch/kama-r42"))
def g(*a):
    return subprocess.run(["git", "-C", D, *a], check=True, capture_output=True, text=True).stdout
subprocess.run(["git", "clone", "-q", "--no-local", lane, D], check=True)
assert g("rev-parse", "--show-toplevel").strip() == os.path.realpath(D), "sandbox toplevel mismatch"
g("checkout", "-q", "--detach", base)
ID = ["-c", "user.name=r42-control", "-c", "user.email=r42-control@fixture.invalid"]
CTR = {"c1": "tools/round42-selfdesc-reconcile.py", "c2": "tools/round42-digest-audit.py",
       "c3": "tools/round42-capacity-audit.py"}

def commit(msg):
    g("add", "-A")
    subprocess.run(["git", "-C", D, *ID, "commit", "-q", "--allow-empty", "-m", msg], check=True)
    return g("rev-parse", "HEAD").strip()

def rd(p):
    return open(os.path.join(D, p)).read()

def wr(p, s):
    os.makedirs(os.path.dirname(os.path.join(D, p)) or D, exist_ok=True)
    open(os.path.join(D, p), "w").write(s)

def score(name, rev):
    for tag, rel in CTR.items():
        # run each counter from the lane's committed bytes, against the sandbox revision
        args = [sys.executable, os.path.join(lane, rel), "--repo", D, "--tip", rev, "--out", os.path.join(out, f"{name}.{tag}.out")]
        if tag == "c2":
            args += ["--seed", "42"]
        if tag == "c3":
            args += ["--base", base]
        p = subprocess.run(args, capture_output=True, text=True, cwd=lane)
        with open(os.path.join(out, f"{name}.{tag}.out"), "a") as f:
            f.write(f"exit={p.returncode}\n")
        print(name, tag, (p.stdout.splitlines() + [p.stderr.strip()])[1][:160], "exit", p.returncode)

def set_section(sc, name, body):
    lines = sc.split("\n")
    i = next(k for k, l in enumerate(lines) if l.strip() == f"## {name}")
    j = i + 1
    while j < len(lines) and not lines[j].startswith("## "):
        j += 1
    lines[i + 1:j] = [""] + body.split("\n") + [""]
    return "\n".join(lines)

score("base", base)
g("checkout", "-q", "--detach", base)
for rel in CTR.values():
    shutil.copy(os.path.join(lane, rel), os.path.join(D, rel))
FREEZE = commit("freeze stand-in: counters")
score("freeze", FREEZE)

# ---- C1 shortcut controls (each starts from the freeze stand-in)
g("checkout", "-q", "--detach", FREEZE)
sc = rd("SCORECARD.md")
head, rest = sc.split("\n## ", 1)
head = "# kama-shokunin - SCORECARD\n\nLatest measured round: 41. Assigned axes: operability + calibration.\n"
sc2 = head + "\n## " + rest
sc2 = set_section(sc2, "Planned", "Superseded by `### Planned (round 42)` below.")
sc2 = set_section(sc2, "Retired", "None. 6 axes and 7 capabilities remain active.")
sc2 = set_section(sc2, "Saturation", "Vector operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7; first-working rounds 10, 14, 16, 20, 25, 30, 41; nudge inactive.")
wr("SCORECARD.md", sc2 + "\n### Planned (round 42)\n\n1. control\n")
score("junk-c1-textonly", commit("junk: four text sections fixed, caps/readme/province/rel untouched"))
g("checkout", "-q", "--detach", FREEZE)
rd_ = rd("README.md") + "\n" + "\n".join(f"- `{n}`" for n in g("ls-tree", "--name-only", "HEAD").split("\n") if n and not n.startswith("."))
wr("README.md", rd_)
wr("PROVINCE.md", rd("PROVINCE.md") + "\n`tools/kama-ollama-evidence.py` `tools/gguf-identity.py` `tools/kama-context-capacity.py` `tools/pin-watch.py` `registry/engine-pins.tsv`\n")
score("junk-c1-sidefilesonly", commit("junk: README and PROVINCE fixed, SCORECARD untouched"))
g("checkout", "-q", "--detach", FREEZE)
sc = rd("SCORECARD.md")
lines = sc.split("\n")
for i, l in enumerate(lines):
    if l.startswith("| calibration |"):
        cells = l.split("|")
        cells[3] = cells[3].rstrip() + " run `python3 -c \"print(1)\"` → `2` (verifier-spotcheck) "
        lines[i] = "|".join(cells)
wr("SCORECARD.md", "\n".join(lines))
score("junk-c1-falserel", commit("junk: calibration row carries a false run fact naming the needle"))

# ---- C2 shortcut controls
g("checkout", "-q", "--detach", FREEZE)
wr("tools/digest-ledger.py", "import sys\nprint('tokens=94 blob=94 external_ok=4 external_absent=0 unverifiable=0 wrong_flagged=0 ledger_bad=0 wrong_unflagged=0 unknown=0')\nsys.exit(0)\n")
sc = rd("SCORECARD.md") + ("\n**Capabilities — canonical list as of round 42**\n\n| Capability | What it can now do | Evidence pointer | First-working round |\n|---|---|---|---|\n"
                          "| digest-ledger | control | `tools/digest-ledger.py` | 42 |\n")
wr("SCORECARD.md", sc)
score("junk-c2-stub", commit("junk: stub tool printing a clean summary"))
g("checkout", "-q", "--detach", FREEZE)
shutil.copy(os.path.join(src, "tools/digest-ledger.py"), os.path.join(D, "tools/digest-ledger.py"))
toks = subprocess.run([sys.executable, "tools/digest-ledger.py", "scan", "--repo", D, "--rev", FREEZE, "--details"], cwd=D,
                      capture_output=True, text=True).stdout
rows = []
for l in toks.split("\n"):
    m = re.match(r"detail: (unknown|wrong_unflagged) ([0-9a-f]{64})", l)
    if m:
        rows.append(f"{m.group(2)}\tunverifiable\tshortcut\t\t\t\tnot checked")
wr("registry/digest-ledger.tsv", "digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n" + "\n".join(rows) + "\n")
wr("SCORECARD.md", sc)
score("junk-c2-allunverifiable", commit("junk: real tool, every unexplained token declared unverifiable"))

# ---- C3 shortcut controls
g("checkout", "-q", "--detach", FREEZE)
ENTRY = "corpus/knowledge/context-capacity-engine-sides.md"
wr(ENTRY, "source: S478 S479 control\nverified-at: 2026-10-25\nrecheck: 90d\n\nnothing\n")
srcs = rd("corpus/SOURCES.md").split("\n")
last = max(i for i, l in enumerate(srcs) if re.match(r"^ {0,3}\| *S\d{3,} *\|", l))
for sid in ("S478", "S479"):
    srcs.insert(last + 1, f"| {sid} | control — https://example.invalid/{sid} | code | A | control | anchor | control | mined | 2026-10-25 | 90d | {ENTRY} |")
wr("corpus/SOURCES.md", "\n".join(srcs))
wr("corpus/README.md", rd("corpus/README.md") + f"\n- `{ENTRY}` control\n")
score("junk-c3-rowsonly", commit("junk: entry stub, fabricated rows, README line; no copies, no gate"))
g("checkout", "-q", "--detach", FREEZE)
staged = "/home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus/knowledge/context-capacity-amendment-2026-10-23-r5.md"
shutil.copy(staged, os.path.join(D, ENTRY))
wr("corpus/README.md", rd("corpus/README.md") + f"\n- `{ENTRY}` staged amendment\n")
score("junk-c3-stagedverbatim", commit("junk: staged amendment copied byte-exact, no rows, no copies, no gate"))
print("sandbox", D)
