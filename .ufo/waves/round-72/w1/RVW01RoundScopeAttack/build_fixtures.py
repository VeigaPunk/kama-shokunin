#!/usr/bin/env python3
"""Build attack fixtures a1..a7 (plus sub-variants) as --shared clones of the seed repo.

Every fixture starts from a clean committed baseline; each mutation is recorded
(porcelain output) into fixtures-meta.json so the attack report cites observed bytes.
"""
import json, os, shutil, subprocess

S = "/fast/scratch/hyaku/kama-r72/RVW01RoundScopeAttack"
SEED = f"{S}/seed"
CHILD = f"{S}/childrepo"
FIX = f"{S}/fixtures"

def sh(args, cwd, check=True):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} in {cwd}: rc={r.returncode}\nSTDOUT:{r.stdout}\nSTDERR:{r.stderr}")
    return r

def porcelain(d, *extra):
    return sh(["git", "status", "--porcelain", "-uall", *extra], cwd=d).stdout

def commit_all(d, msg):
    r = sh(["git", "rev-parse", "--show-toplevel"], cwd=d)
    assert r.stdout.strip() == d, f"toplevel mismatch: {r.stdout!r} != {d}"
    sh(["git", "add", "-A"], cwd=d)
    sh(["git", "-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
        "commit", "-q", "-m", msg], cwd=d)

def clone(name):
    d = f"{FIX}/{name}"
    if os.path.exists(d):
        shutil.rmtree(d)
    sh(["git", "clone", "-q", "--shared", SEED, d], cwd=S)
    return d

def put(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

meta = {}
os.makedirs(FIX, exist_ok=True)

# ---------- A1: staged-but-uncommitted paths (index-column-only records) ----------
d = clone("a1")
put(f"{d}/stray-staged.txt", "staged new\n")
with open(f"{d}/SCORECARD.md", "a") as f:
    f.write("staged edit\n")
sh(["git", "add", "stray-staged.txt", "SCORECARD.md"], cwd=d)
meta["a1"] = {"fixture": d, "porcelain": porcelain(d)}

# ---------- A2: modified-but-staged deletion ----------
d = clone("a2")
sh(["git", "rm", "-q", "corpus/lessons/round-71.md"], cwd=d)
meta["a2"] = {"fixture": d, "porcelain": porcelain(d)}

# ---------- A3: path names with a space and a newline ----------
d = clone("a3")
put(f"{d}/sp ace\nname.txt", "untracked stray\n")          # ?? quoted
put(f"{d}/staged sp\nace.txt", "staged stray\n")
sh(["git", "add", "staged sp\nace.txt"], cwd=d)            # A  quoted
meta["a3"] = {"fixture": d, "porcelain": porcelain(d)}

d = clone("a3i")                                           # ignored + weird name inside wave dir
put(f"{d}/.gitignore", "*.ign\n")
commit_all(d, "add gitignore")
put(f"{d}/.ufo/waves/round-72/sp ace\nname.ign", "ignored\n")
meta["a3i"] = {"fixture": d,
               "porcelain_plain": porcelain(d),
               "porcelain_ignored_wave": porcelain(d, "--ignored", "--", ".ufo/waves/round-72")}

# ---------- A4: tracked file under the wave dir that is also git-ignored ----------
d = clone("a4")                                            # pure tracked+ignored (leak probe)
put(f"{d}/.ufo/waves/round-72/keep.txt", "receipt\n")
commit_all(d, "commit wave receipt")
put(f"{d}/.gitignore", ".ufo/waves/round-72/keep.txt\n")
commit_all(d, "ignore the tracked receipt")
ci = subprocess.run(["git", "check-ignore", "-v", ".ufo/waves/round-72/keep.txt"], cwd=d,
                    capture_output=True, text=True)
ci2 = subprocess.run(["git", "check-ignore", "-v", "--no-index", ".ufo/waves/round-72/keep.txt"], cwd=d,
                     capture_output=True, text=True)
meta["a4"] = {"fixture": d,
              "porcelain_plain": porcelain(d),
              "porcelain_ignored_wave": porcelain(d, "--ignored", "--", ".ufo/waves/round-72"),
              "check_ignore_default_rc": ci.returncode, "check_ignore_default_out": ci.stdout,
              "check_ignore_noidx_rc": ci2.returncode, "check_ignore_noidx_out": ci2.stdout}

d = clone("a4b")                                           # tracked+ignored AND untracked+ignored
put(f"{d}/.ufo/waves/round-72/keep.txt", "receipt\n")
commit_all(d, "commit wave receipt")
put(f"{d}/.gitignore", ".ufo/waves/round-72/keep.txt\n*.ign\n")
commit_all(d, "ignore rules")
put(f"{d}/.ufo/waves/round-72/ghost.ign", "untracked ignored\n")
meta["a4b"] = {"fixture": d,
               "porcelain_ignored_wave": porcelain(d, "--ignored", "--", ".ufo/waves/round-72")}

# ---------- A5: dirt hidden in a second worktree of the same repo ----------
d = clone("a5")
wt = f"{FIX}/a5-wt"
if os.path.exists(wt):
    shutil.rmtree(wt)
sh(["git", "worktree", "add", "-q", "-b", "side", wt, "master"], cwd=d)
with open(f"{wt}/LOG.md", "a") as f:
    f.write("dirty in linked worktree\n")
put(f"{wt}/stray-in-wt.txt", "untracked in linked worktree\n")
meta["a5"] = {"fixture": d, "worktree": wt,
              "primary_porcelain": porcelain(d),
              "wt_porcelain": porcelain(wt)}

# ---------- A6: label / prompt / wave-dir mismatches ----------
d = clone("a6")                                            # prompt present + plan present + clean
put(f"{d}/.ufo/prompts/kama-round-72.md", "# kama round 72 prompt\n")
commit_all(d, "add fleet prompt file")
meta["a6"] = {"fixture": d, "porcelain": porcelain(d)}

d = clone("a6b")                                           # prompt present, plan ABSENT at tip
put(f"{d}/.ufo/prompts/kama-round-72.md", "# kama round 72 prompt\n")
sh(["git", "rm", "-q", "plans/round-72-claims.md"], cwd=d)
commit_all(d, "prompt present, plan absent")
meta["a6b"] = {"fixture": d, "porcelain": porcelain(d)}

d = clone("a6c")                                           # the real lane shape: plan present, NO prompt, clean
meta["a6c"] = {"fixture": d, "porcelain": porcelain(d)}

d = clone("a6d")                                           # plan exists but heading names round 71
put(f"{d}/plans/round-72-claims.md", "# kama round 71 - mislabelled\n\nbody\n")
commit_all(d, "mislabelled heading")
meta["a6d"] = {"fixture": d, "porcelain": porcelain(d)}

d = clone("a6e")                                           # --round 71 probe: r71 plan present, no wave dir for 71
meta["a6e"] = {"fixture": d, "porcelain": porcelain(d)}

# ---------- A7: submodule + broad allow-list ----------
if os.path.exists(CHILD):
    shutil.rmtree(CHILD)
os.makedirs(CHILD)
put(f"{CHILD}/child.txt", "child\n")
sh(["git", "init", "-q", "-b", "master"], cwd=CHILD)
sh(["git", "add", "-A"], cwd=CHILD)
sh(["git", "-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
    "commit", "-q", "-m", "child base"], cwd=CHILD)
meta["childrepo"] = {"fixture": CHILD}

d = clone("a7sub")                                         # default config: untracked content inside submodule
sh(["git", "-c", "protocol.file.allow=always", "submodule", "add", CHILD, "sub"], cwd=d)
commit_all(d, "add submodule")
put(f"{d}/sub/leak.txt", "untracked inside submodule\n")
meta["a7sub"] = {"fixture": d, "porcelain": porcelain(d)}

d = clone("a7sub2")                                        # submodule.<name>.ignore=all in .gitmodules
sh(["git", "-c", "protocol.file.allow=always", "submodule", "add", CHILD, "sub"], cwd=d)
sh(["git", "config", "-f", ".gitmodules", "submodule.sub.ignore", "all"], cwd=d)
commit_all(d, "add submodule with ignore=all")
put(f"{d}/sub/leak.txt", "untracked inside submodule\n")
with open(f"{d}/sub/child.txt", "a") as f:
    f.write("dirty tracked file too\n")
meta["a7sub2"] = {"fixture": d, "porcelain": porcelain(d)}

d = clone("a7allow")                                       # allow-boundary probes (tool run with --allow)
put(f"{d}/corpus/lessons-backup/wip.md", "prefix-adjacent stray OUTSIDE allowed dir\n")
put(f"{d}/corpus/lessons/deep/uncommitted.md", "nested stray INSIDE allowed dir\n")
meta["a7allow"] = {"fixture": d, "porcelain": porcelain(d)}

with open(f"{S}/fixtures-meta.json", "w") as f:
    json.dump(meta, f, indent=1)
print("FIXTURES_BUILT")
for k, v in meta.items():
    print(f"== {k} fixture={v['fixture']}")
    for kk, vv in v.items():
        if kk != "fixture":
            print(f"  {kk}: {vv!r}")
