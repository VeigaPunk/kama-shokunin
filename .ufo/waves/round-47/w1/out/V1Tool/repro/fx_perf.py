#!/usr/bin/env python3
# F7: performance on a long window: 85 files x 600 commits, two real events.
import os, random, subprocess, sys, time, tempfile
S = "/fast/scratch/hyaku/kama-r47/V1Tool"
TOOL = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py"
D = tempfile.mkdtemp(prefix="perf-", dir=S)
ENV = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
def git(*args, inp=None):
    subprocess.run(["git", "-C", D, *args], input=inp, check=True, capture_output=True, env=ENV)
def gtext(*args):
    return subprocess.run(["git", "-C", D, *args], capture_output=True, env=ENV).stdout.decode()
git("init", "-q"); git("config", "user.name", "fx"); git("config", "user.email", "fx@fx")
rnd = random.Random(7)
NFILES, NCOMMITS = 85, 600
n = [f"f{i:03d}.md" for i in range(NFILES)]
body = {}
for i, f in enumerate(n):
    body[f] = [f"f{i:03d} line {j} {os.urandom(4).hex()}" for j in range(150)]
for f, ls in body.items():
    with open(os.path.join(D, f), "w") as fh:
        fh.write("\n".join(ls) + "\n")
git("add", "-A"); git("commit", "-qm", "root")
log = body["f000.md"]
t0 = time.time()
for c in range(1, NCOMMITS):
    if c % 150 == 100:                 # event 1: delete 25 lines from f000
        gone = log[:25]; log = log[25:]
    elif c % 150 == 130:               # restore exactly those 25 lines
        log = log + gone
    if c % 100 == 50:                  # event 2: delete 21 lines from f001
        gone2 = body["f001.md"][:21]; body["f001.md"] = body["f001.md"][21:]
    elif c % 100 == 75:
        body["f001.md"] = body["f001.md"] + gone2
    with open(os.path.join(D, "f000.md"), "w") as fh:
        fh.write("\n".join(log) + "\n")
    spot = n[c % NFILES]
    if spot != "f000.md":
        body[spot].append(f"{spot} extra {c}")
        with open(os.path.join(D, spot), "w") as fh:
            fh.write("\n".join(body[spot]) + "\n")
    git("add", "-A"); git("commit", "-qm", f"c{c}", "--allow-empty")
build = time.time() - t0
tip = gtext("rev-parse", "HEAD").strip()
t1 = time.time()
p = subprocess.run([sys.executable, TOOL, "--repo", D, "--to", tip,
                   "--files", "f000.md,f001.md", "--json"],
                   capture_output=True, text=True)
tool = time.time() - t1
print(f"fixture: {NFILES} files, {NCOMMITS} commits, build={build:.1f}s")
print(f"tool run: {tool:.1f}s, exit={p.returncode}")
import json
out = json.loads(p.stdout)
for e in out["events"]:
    print(f"  {e['commit'][:12]} {e['file']} deleted={e['deleted']} max={e['restored_max']} status={e['status']}")
print("summary:", out["summary"])
