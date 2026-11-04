#!/usr/bin/env python3
"""Build the clean seed fixture repo (committed baseline) for round-72 C1 attacks."""
import os, shutil, subprocess, sys

L = "/home/vgpnk/Projects/shokunin/kama-shokunin"
S = "/fast/scratch/hyaku/kama-r72/RVW01RoundScopeAttack"
SEED = os.path.join(S, "seed")

def run(*args, cwd):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr

if os.path.exists(SEED):
    shutil.rmtree(SEED)
os.makedirs(SEED)

# --- files (all committed => baseline clean) ---
files = {
    "SCORECARD.md": "# scorecard\n\n## round 72\n\nPlanned: C1 round-scope, C2 receipt-tip-binding.\n",
    "LOG.md": "# log\n",
    "corpus/README.md": "# corpus\n",
    "corpus/lessons/round-71.md": "# round 71 lesson\n",
    "SKILL.md": "# skill registry\n",
    "tools/placeholder.py": "x = 1\n",
}
for rel, content in files.items():
    p = os.path.join(SEED, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(content)

# claims plans copied from the lane (committed bytes preferred)
for rnd in (71, 72):
    src = os.path.join(L, f"plans/round-{rnd}-claims.md")
    if os.path.exists(src):
        dst = os.path.join(SEED, f"plans/round-{rnd}-claims.md")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)

# freeze control copy (wave-dir content)
fr = os.path.join(L, ".ufo/waves/round-72/controls/freeze.txt")
if os.path.exists(fr):
    dst = os.path.join(SEED, ".ufo/waves/round-72/controls/freeze.txt")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(fr, dst)

# --- git: init, assert toplevel, commit with throwaway identity ---
for args in (["git", "init", "-q", "-b", "master"], ["git", "add", "-A"]):
    rc, out, err = run(*args, cwd=SEED)
    assert rc == 0, (args, err)

rc, out, err = run("git", "rev-parse", "--show-toplevel", cwd=SEED)
assert rc == 0 and out.strip() == SEED, (out, err)

rc, out, err = run("git", "-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
                   "commit", "-q", "-m", "seed baseline", cwd=SEED)
assert rc == 0, err

rc, out, err = run("git", "status", "--porcelain", "-uall", cwd=SEED)
print("SEED_COMMIT_OK")
print("status_after_commit:", repr(out))
rc2, head, _ = run("git", "rev-parse", "master", cwd=SEED)
print("seed_master:", head.strip())
sys.exit(0)
