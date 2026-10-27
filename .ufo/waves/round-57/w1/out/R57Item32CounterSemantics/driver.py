import os, re, subprocess, sys, shutil
S = "/fast/scratch/hyaku/kama-r57/R57Item32CounterSemantics"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
COUNTER = f"{LANE}/tools/round42-selfdesc-reconcile.py"
FX = f"{S}/fx"
env = dict(os.environ, TMPDIR=f"{S}/tmp")
ENV_ID = ["-c", "user.name=r57-fixture", "-c", "user.email=r57-fixture@example.invalid"]

def sh(*a, cwd=None):
    return subprocess.run(a, capture_output=True, text=True, cwd=cwd, env=env)

def assert_top(d):
    top = sh("git", "rev-parse", "--show-toplevel", cwd=d).stdout.strip()
    assert top == d, (top, d)

def clone(src, dst):
    if os.path.exists(dst): shutil.rmtree(dst)
    r = sh("git", "clone", "-q", src, dst); assert r.returncode == 0, r.stderr
    assert_top(dst)

def mutate_commit(d, msg, fn):
    assert_top(d)
    p = f"{d}/SCORECARD.md"
    t = open(p, encoding="utf-8").read()
    t2 = fn(t)
    assert t2 != t, "mutation was a no-op"
    open(p, "w", encoding="utf-8").write(t2)
    assert_top(d)
    r = sh("git", *ENV_ID, "commit", "-qam", msg, cwd=d); assert r.returncode == 0, r.stderr

def run_counter(d):
    p = subprocess.run(["python3", COUNTER, "--repo", d, "--tip", "HEAD"], capture_output=True, text=True, env=env)
    return p.returncode, p.stdout + p.stderr

def report(name, d):
    code, out = run_counter(d)
    print(f"### {name}  exit={code}")
    print(out.rstrip())
    print()
    return code, out

if __name__ == "__main__":
    which = sys.argv[1:] or ["base"]
    base = f"{FX}/base"
    if not os.path.exists(base):
        clone(LANE, base)
    for name in which:
        pass
