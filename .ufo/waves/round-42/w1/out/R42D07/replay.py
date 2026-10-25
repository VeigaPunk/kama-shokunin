#!/usr/bin/env python3
"""R42D07: reconstruct the round-42 shortcut/separability control states whose
sandbox commits are unreachable, following the committed recipes
.ufo/waves/round-42/controls/build_controls.py and build_separability.py.
Fixture identity is used ONLY inside this sandbox. Emits replay.rev (shell
sourceable STATE=sha lines)."""
import os, re, shutil, subprocess, sys

SEAT = "/fast/scratch/kama-r42/seats/R42D07"
CLONE = f"{SEAT}/clone"
D = f"{SEAT}/fixtures/replay"
BASE = "0b606b03bf0b2a87b791aa537f6c72c941624cf0"
TIP = "3d9bd8d72366e281fab291874524130428ee423d"
CTR = ["tools/round42-selfdesc-reconcile.py", "tools/round42-digest-audit.py",
       "tools/round42-capacity-audit.py"]
ENTRY = "corpus/knowledge/context-capacity-engine-sides.md"
TABLE = ("\n**Capabilities — canonical list as of round 42**\n\n"
         "| Capability | What it can now do | Evidence pointer | First-working round |\n|---|---|---|---|\n")

def g(*a):
    return subprocess.run(["git", "-C", D, *a], check=True, capture_output=True, text=True).stdout

def show(rev, p):
    return subprocess.run(["git", "-C", CLONE, "cat-file", "-p", f"{rev}:{p}"],
                          check=True, capture_output=True).stdout

def commit(msg):
    g("add", "-A")
    subprocess.run(["git", "-C", D, "-c", "user.name=r42-control",
                    "-c", "user.email=r42-control@fixture.invalid",
                    "commit", "-q", "--allow-empty", "-m", msg], check=True)
    return g("rev-parse", "HEAD").strip()

def rd(p):
    return open(os.path.join(D, p)).read()

def wr(p, s):
    fp = os.path.join(D, p)
    os.makedirs(os.path.dirname(fp) or D, exist_ok=True)
    open(fp, "w").write(s)

def wf(p):
    """copy a counter from the seat-clone worktree (verified == tip bytes)"""
    wr(p, open(os.path.join(CLONE, p)).read())

def main():
    st = subprocess.run(["git", "-C", CLONE, "status", "--porcelain"],
                        capture_output=True, text=True).stdout.strip()
    if st:
        print(f"FATAL seat clone worktree dirty:\n{st}", file=sys.stderr)
        return 1
    shutil.rmtree(D, ignore_errors=True)
    os.makedirs(f"{SEAT}/fixtures", exist_ok=True)
    subprocess.run(["git", "clone", "-q", "--no-local", CLONE, D], check=True)
    assert g("rev-parse", "--show-toplevel").strip() == os.path.realpath(D), "toplevel"
    rev = {}

    # freeze stand-in: base + the three round-42 counters (recipe: build_controls.py)
    g("checkout", "-q", "--detach", BASE)
    for rel in CTR:
        wf(rel)
    rev["R-FREEZE"] = commit("freeze stand-in: counters")

    # junk-c2-stub
    g("checkout", "-q", "--detach", rev["R-FREEZE"])
    wr("tools/digest-ledger.py",
       "import sys\n"
       "print('tokens=94 blob=94 external_ok=4 external_absent=0 unverifiable=0 "
       "wrong_flagged=0 ledger_bad=0 wrong_unflagged=0 unknown=0')\nsys.exit(0)\n")
    sc = rd("SCORECARD.md") + TABLE + "| digest-ledger | control | `tools/digest-ledger.py` | 42 |\n"
    wr("SCORECARD.md", sc)
    rev["R-STUB"] = commit("junk: stub tool printing a clean summary")

    # junk-c2-allunverifiable
    g("checkout", "-q", "--detach", rev["R-FREEZE"])
    wr("tools/digest-ledger.py", open(os.path.join(CLONE, "tools/digest-ledger.py")).read())
    toks = subprocess.run([sys.executable, "tools/digest-ledger.py", "scan",
                           "--repo", D, "--rev", rev["R-FREEZE"], "--details"],
                          cwd=D, capture_output=True, text=True).stdout
    rows = []
    for l in toks.split("\n"):
        m = re.match(r"detail: (unknown|wrong_unflagged) ([0-9a-f]{64})", l)
        if m:
            rows.append(f"{m.group(2)}\tunverifiable\tshortcut\t\t\t\tnot checked")
    wr("registry/digest-ledger.tsv",
       "digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n" + "\n".join(rows) + "\n")
    wr("SCORECARD.md", sc)
    rev["R-ALLUNV"] = commit("junk: real tool, every unexplained token declared unverifiable")
    if not rows:
        print("FATAL: allunverifiable recipe produced no rows (--details scan empty?)", file=sys.stderr)
        return 1

    # junk-c3-rowsonly
    g("checkout", "-q", "--detach", rev["R-FREEZE"])
    wr(ENTRY, "source: S478 S479 control\nverified-at: 2026-10-25\nrecheck: 90d\n\nnothing\n")
    srcs = rd("corpus/SOURCES.md").split("\n")
    last = max(i for i, l in enumerate(srcs) if re.match(r"^ {0,3}\| *S\d{3,} *\|", l))
    for sid in ("S478", "S479"):
        srcs.insert(last + 1, f"| {sid} | control — https://example.invalid/{sid} | code | A | control | "
                              f"anchor | control | mined | 2026-10-25 | 90d | {ENTRY} |")
    wr("corpus/SOURCES.md", "\n".join(srcs))
    wr("corpus/README.md", rd("corpus/README.md") + f"\n- `{ENTRY}` control\n")
    rev["R-ROWSONLY"] = commit("junk: entry stub, fabricated rows, README line; no copies, no gate")

    # junk-c3-stagedverbatim
    g("checkout", "-q", "--detach", rev["R-FREEZE"])
    staged = "/home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus/knowledge/context-capacity-amendment-2026-10-23-r5.md"
    shutil.copy(staged, os.path.join(D, ENTRY))
    wr("corpus/README.md", rd("corpus/README.md") + f"\n- `{ENTRY}` staged amendment\n")
    rev["R-STAGEDVERBATIM"] = commit("junk: staged amendment copied byte-exact, no rows, no copies, no gate")

    # sep-c1-only: claim tip minus every C2 and C3 file (build_separability.py)
    g("checkout", "-q", "--detach", TIP)
    for p in ["tools/digest-ledger.py", "registry/digest-ledger.tsv", ENTRY,
              "corpus/lessons/round-42.md"]:
        os.remove(os.path.join(D, p))
    for d in (".ufo/waves/round-42/c3", ".ufo/waves/round-42/assimilation"):
        shutil.rmtree(os.path.join(D, d))
    for p in ("corpus/SOURCES.md", "corpus/README.md"):
        open(os.path.join(D, p), "w").write(show(BASE, p).decode())
    rev["R-SEPC1"] = commit("sep: C1 files only")

    # sep-c2-only: base + C2 files + canonical list row
    g("checkout", "-q", "--detach", BASE)
    for rel in CTR:
        wf(rel)
    for p in ["tools/digest-ledger.py", "registry/digest-ledger.tsv",
              "tools/round41-scorecard-reconcile.py", "tools/round41-pinwatch-audit.py"]:
        wr(p, show(TIP, p).decode())
    wr("SCORECARD.md", show(BASE, "SCORECARD.md").decode() + TABLE +
       "| digest-ledger | classify cited digests | `tools/digest-ledger.py`; "
       "`registry/digest-ledger.tsv` | 42 |\n")
    rev["R-SEPC2"] = commit("sep: C2 files only")

    # sep-c3-only: base + C3 files + SOURCES rows + README block
    g("checkout", "-q", "--detach", BASE)
    for rel in CTR:
        wf(rel)
    for p in [ENTRY, "corpus/lessons/round-42.md", "corpus/SOURCES.md", "corpus/README.md"]:
        wr(p, show(TIP, p).decode())
    for d in (".ufo/waves/round-42/c3", ".ufo/waves/round-42/assimilation"):
        dst = os.path.join(D, d)
        shutil.copytree(os.path.join(CLONE, d), dst)
    rev["R-SEPC3"] = commit("sep: C3 files only")

    rev["BASE"] = BASE
    rev["CAND"] = "c8c92db4bdf1c64357b995e0fe8d2a4f481fe995"
    rev["TIP"] = TIP
    with open(f"{SEAT}/replay.rev", "w") as f:
        for k, v in rev.items():
            f.write(f"{k}={v}\n")
            print(k, v)
    return 0

if __name__ == "__main__":
    sys.exit(main())
