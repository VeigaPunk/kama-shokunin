#!/usr/bin/env python3
"""E01CounterRepair fixture driver (fx1): frozen base -> one-token repair.

Scratch-only. Creates a throwaway clone of the lane, checks out the frozen
round-57 base b89bdab2, runs the frozen counter, applies the single
self-description count repair (42 -> 43) and re-runs the same counter.
No writes outside /fast/scratch/hyaku/kama-r57/E01CounterRepair.
"""
import os
import shutil
import subprocess
import sys

SCRATCH = "/fast/scratch/hyaku/kama-r57/E01CounterRepair"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
BASE = "b89bdab2cc114735ec5d331c6c610134258f7864"
TOOL = os.path.join(LANE, "tools/round42-selfdesc-reconcile.py")
FX = os.path.join(SCRATCH, "fx1")
OUT = os.path.join(SCRATCH, "receipts-fx1")


def run(cmd, cwd=None, env=None, capture=True):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    return p


def sh(cmd, cwd, check=True):
    p = run(cmd, cwd=cwd)
    if check and p.returncode != 0:
        sys.exit(f"FAILED {cmd}: {p.returncode}\n{p.stdout}\n{p.stderr}")
    return p


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    if os.path.isdir(FX):
        shutil.rmtree(FX)
    env = dict(os.environ, TMPDIR=SCRATCH)  # never /tmp for scratch exports

    sh(["git", "clone", "-q", "--no-hardlinks", LANE, FX], SCRATCH)
    sh(["git", "checkout", "-q", BASE], FX)
    top = sh(["git", "rev-parse", "--show-toplevel"], FX).stdout.strip()
    assert os.path.realpath(top) == os.path.realpath(FX), (top, FX)
    sh(["git", "config", "user.email", "e01@scratch.local"], FX)
    sh(["git", "config", "user.name", "E01CounterRepair"], FX)

    def counter(tip, name):
        p = run([sys.executable, TOOL, "--repo", FX, "--tip", tip],
                cwd=SCRATCH, env=env)
        body = p.stdout
        with open(os.path.join(OUT, name), "w") as f:
            f.write(f"$ python3 {TOOL} --repo <fx1> --tip {tip}   (TMPDIR={SCRATCH})\n")
            f.write(body)
            f.write(f"exit={p.returncode}\n")
            if p.stderr:
                f.write("stderr:\n" + p.stderr)
        return p.returncode, body

    # 1. frozen base, before any repair
    rc0, out0 = counter(BASE, "base-b89bdab2-repro.out")
    print("BASE", rc0, out0.splitlines()[1])

    # 2. smallest isolated repair: one token 42 -> 43 on the calibration row
    sc = os.path.join(FX, "SCORECARD.md")
    src = open(sc).read()
    needle = "glob.glob('corpus/lessons/*verifier-spotcheck.md')))\"` \u2192 `42`"
    assert src.count(needle) == 1, src.count(needle)
    open(sc, "w").write(src.replace(needle, needle[:-3] + "43`"))
    diff = sh(["git", "diff", "--stat", "--", "SCORECARD.md"], FX).stdout
    diff_full = sh(["git", "diff", "--word-diff=porcelain", "--", "SCORECARD.md"], FX).stdout
    with open(os.path.join(OUT, "repair-diff.txt"), "w") as f:
        f.write(diff + "\n" + diff_full)
    sh(["git", "add", "SCORECARD.md"], FX)
    sh(["git", "commit", "-q", "-m", "fixture: repro stale calibration count 42->43"], FX)
    rep = sh(["git", "rev-parse", "HEAD"], FX).stdout.strip()

    rc1, out1 = counter(rep, "repaired-42to43.out")
    print("REPAIRED", rc1, out1.splitlines()[1])

    # 3. canonical heading selection + report format preserved
    sys.path.insert(0, os.path.join(LANE, "tools"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("r42", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sc_text = subprocess.run(["git", "-C", FX, "cat-file", "-p", f"{rep}:SCORECARD.md"],
                             capture_output=True, text=True).stdout
    cn, crows = mod.canon(sc_text)
    names = [r[0].strip("` *") for r in crows if r]
    firsts = sorted({int(__import__("re").findall(r"\d+", r[3])[-1])
                     for r in crows if len(r) >= 4 and __import__("re").findall(r"\d+", r[3])})
    head = "\n".join(mod.sections(sc_text, "Capabilities")[:1].pop().split("\n"))
    hnames = [r[0].strip("` *") for r in mod.table_rows(head.split("\n")) if r]
    rounds = [int(m.group(1)) for l in sc_text.split("\n")
              for m in [__import__("re").match(r"^## Round (\d+)", l)] if m]
    auth = [int(m.group(1)) for l in sc_text.split("\n")
            for m in [__import__("re").match(r"\*\*Current authority \(round (\d+)\)", l)] if m]
    with open(os.path.join(OUT, "canon-selection.out"), "w") as f:
        f.write(f"tip={rep}\n")
        f.write(f"canon_round={cn} canon_rows={len(crows)}\n")
        f.write(f"canon_names={names}\n")
        f.write(f"head_capability_names={hnames}\n")
        f.write(f"names_equal={sorted(names)==sorted(hnames)}\n")
        f.write(f"canonical_firsts={firsts}\n")
        f.write(f"max_round_heading={max(rounds)} round_headings={len(rounds)}\n")
        f.write(f"authority_rounds_max={max(auth)}\n")
    print(open(os.path.join(OUT, "canon-selection.out")).read())

    # 4. report line shape: same fields, same order before/after
    def keys(body):
        line = body.splitlines()[1]
        return [t.split("=")[0] for t in line.split() if "=" in t]
    with open(os.path.join(OUT, "report-shape.out"), "w") as f:
        f.write(f"base_fields={keys(out0)}\n")
        f.write(f"repaired_fields={keys(out1)}\n")
        f.write(f"same_field_order={keys(out0)==keys(out1)}\n")
        f.write(f"base_line={out0.splitlines()[0:2]}\n")
        f.write(f"repaired_line={out1.splitlines()[0:2]}\n")
    print(open(os.path.join(OUT, "report-shape.out")).read())


if __name__ == "__main__":
    main()
