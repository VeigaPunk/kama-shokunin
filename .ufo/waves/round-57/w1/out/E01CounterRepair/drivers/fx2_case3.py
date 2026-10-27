#!/usr/bin/env python3
"""E01CounterRepair independent case-3 fixture (fx2).

Fresh clone (independent of fx1), frozen base b89bdab2. Probes that the
counter's maxN comes from committed SCORECARD bytes, not a literal, that 46
is reachable only from the no-op fixture / the stale round-46 canonical table,
that canonical heading selection and row content bind, and that the r41 leg is
the one that flips. Scratch-only; fixture commits stay inside fx2.
"""
import importlib.util
import os
import re
import shutil
import subprocess
import sys

SCRATCH = "/fast/scratch/hyaku/kama-r57/E01CounterRepair"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
BASE = "b89bdab2cc114735ec5d331c6c610134258f7864"
TOOL = os.path.join(LANE, "tools/round42-selfdesc-reconcile.py")
R41 = os.path.join(LANE, "tools/round41-scorecard-reconcile.py")
CONTROLS = os.path.join(LANE, ".ufo/waves/round-57/controls")
FX = os.path.join(SCRATCH, "fx2")
OUT = os.path.join(SCRATCH, "receipts-fx2")
ENV = dict(os.environ, TMPDIR=SCRATCH)


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=ENV)


def sh(cmd, cwd, check=True):
    p = run(cmd, cwd=cwd)
    if check and p.returncode != 0:
        sys.exit(f"FAILED {cmd}: {p.returncode}\n{p.stdout}\n{p.stderr}")
    return p


def record(name, cmdline, p, extra=""):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(f"$ {cmdline}\n")
        f.write(extra)
        f.write(p.stdout)
        if p.stderr:
            f.write("stderr:\n" + p.stderr)
        f.write(f"exit={p.returncode}\n")


def counter(tip, name, tool=TOOL, repo=FX):
    cmd = f"python3 {tool} --repo <fx2> --tip {tip}   (TMPDIR={SCRATCH})"
    p = run([sys.executable, tool, "--repo", repo, "--tip", tip], cwd=SCRATCH)
    record(name, cmd, p)
    return p


def r41(tip, name):
    p = run([sys.executable, R41, "--repo", FX, "--tip", tip], cwd=SCRATCH)
    record(name, f"python3 {R41} --repo <fx2> --tip {tip}", p)
    return p


def commit(msg):
    sh(["git", "add", "-A"], FX)
    sh(["git", "commit", "-q", "-m", msg], FX)
    return sh(["git", "rev-parse", "HEAD"], FX).stdout.strip()


def main():
    os.makedirs(OUT, exist_ok=True)
    if os.path.isdir(FX):
        shutil.rmtree(FX)
    sh(["git", "clone", "-q", "--no-hardlinks", LANE, FX], SCRATCH)
    sh(["git", "checkout", "-q", BASE], FX)
    top = sh(["git", "rev-parse", "--show-toplevel"], FX).stdout.strip()
    assert os.path.realpath(top) == os.path.realpath(FX)
    sh(["git", "config", "user.email", "e01-case3@scratch.local"], FX)
    sh(["git", "config", "user.name", "E01CounterRepair-case3"], FX)

    # --- derivation census at the frozen base (committed bytes only) ---
    spec = importlib.util.spec_from_file_location("r42x", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sc = sh(["git", "show", f"{BASE}:SCORECARD.md"], FX).stdout
    lines = sc.split("\n")
    rounds = [int(m.group(1)) for l in lines for m in [re.match(r"^## Round (\d+)", l)] if m]
    auth = [int(m.group(1)) for l in lines
            for m in [re.match(r"\*\*Current authority \(round (\d+)\)", l)] if m]
    latest = [int(m.group(1)) for l in lines
              for m in [re.search(r"Latest measured round: (\d+)", l)] if m]
    cn, crows = mod.canon(sc)
    firsts = sorted({int(re.findall(r"\d+", r[3])[-1]) for r in crows if len(r) >= 4})
    # the stale round-46 canonical table, read directly (not selected by canon())
    stale46 = None
    for i, l in enumerate(lines):
        if re.search(r"canonical list as of round\s+46\*\*", l, re.I):
            rows = mod.table_rows(lines[i + 1:])
            stale46 = sorted({int(re.findall(r"\d+", r[3])[-1]) for r in rows if len(r) >= 4})
    noop_py = os.path.join(CONTROLS, "c1-noop.py")
    noop_src = open(noop_py).read()
    with open(os.path.join(OUT, "derivations.out"), "w") as f:
        f.write("frozen base = %s (committed SCORECARD bytes)\n" % BASE)
        f.write("max(^## Round N headings) = %d (headings=%d)\n" % (max(rounds), len(rounds)))
        f.write("max(**Current authority (round N)**) = %d\n" % max(auth))
        f.write("head 'Latest measured round: N' = %s\n" % latest)
        f.write("highest canonical-list heading round = %d (rows=%d)\n" % (cn, len(crows)))
        f.write("canonical first-working rounds = %s (max=%d)\n" % (firsts, max(firsts)))
        f.write("stale round-46 canonical first-working rounds = %s (max=%d)\n" % (stale46, max(stale46)))
        f.write("no-op control literal maxN = 46 (source: %s)\n" % noop_py)
        f.write("no-op source:\n" + noop_src)
        f.write("=> 46 is reachable only from the no-op literal and the stale round-46 table; "
                "the live tree-derived round maximum is %d.\n" % max(rounds))

    # --- no-op control executed ---
    p = run([sys.executable, noop_py], cwd=SCRATCH)
    record("noop-c1-executed.out", f"python3 {noop_py} (no --repo, no reads)", p,
           extra="source: " + noop_src.replace("\n", " | ") + "\n")

    # --- r41 leg at base, then after the one-token count repair ---
    r41(BASE, "r41-base.out")
    scpath = os.path.join(FX, "SCORECARD.md")
    src = open(scpath).read()
    needle = "glob.glob('corpus/lessons/*verifier-spotcheck.md')))\"` \u2192 `42`"
    assert src.count(needle) == 1
    open(scpath, "w").write(src.replace(needle, needle[:-3] + "43`"))
    rep = commit("case3: 42->43 stale calibration count")
    counter(rep, "counter-repaired.out")
    r41(rep, "r41-repaired.out")

    # --- maxN is live: adding a ## Round 57 heading moves it to 57 ---
    scpath = os.path.join(FX, "SCORECARD.md")
    with open(scpath, "a") as f:
        f.write("\n## Round 57 \u2014 E01 probe heading (fixture only)\n\nprobe\n")
    probe = commit("case3: ## Round 57 probe heading")
    counter(probe, "counter-round57-heading.out")

    # restore the repaired state before content probes
    sh(["git", "reset", "-q", "--hard", rep], FX)

    # --- canonical ROW content binds: rename one row in the round-49 canonical table ---
    scpath = os.path.join(FX, "SCORECARD.md")
    lines = open(scpath).read().split("\n")
    start = next(i for i, l in enumerate(lines)
                 if re.search(r"canonical list as of round\s+49\*\*", l, re.I))
    hit = None
    for i in range(start + 1, min(start + 30, len(lines))):
        if lines[i].startswith("| hexrun-census |"):
            lines[i] = lines[i].replace("| hexrun-census |", "| hexrun-censusX |", 1)
            hit = i
            break
    assert hit is not None, "canonical row not found"
    open(scpath, "w").write("\n".join(lines))
    mut = commit("case3: rename one canonical capability row")
    counter(mut, "counter-canonical-row-renamed.out")

    # --- copy the frozen tools for the forced-46 probe (edit next, separately) ---
    tool46 = os.path.join(SCRATCH, "tool-maxn46")
    if os.path.isdir(tool46):
        shutil.rmtree(tool46)
    shutil.copytree(os.path.join(LANE, "tools"), tool46)


if __name__ == "__main__":
    main()
