#!/usr/bin/env python3
"""Reference C2 instrument for the round-57 E03 selftest.

Wraps the committed `tools/round42-selfdesc-reconcile.py` unchanged and appends
the witnesses the selftest's --require-witness mode demands: the sha256 of the
SCORECARD blob it read, and the declared-versus-observed spotcheck count that
the stale self-description fact is about.  This is the minimal integration
shape: the counter's derivation stays the single source of the verdict; the
witness only proves which bytes produced it.
"""
import hashlib
import importlib.util
import os
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
SELFDESC = HERE / "round42-selfdesc-reconcile.py"
SELFDESC_M = "round42-selfdesc-reconcile.py"
SPOT = re.compile(r"corpus/lessons/[^/]*verifier-spotcheck\.md")
COUNT_RE = re.compile(r"run\s+`([^`]+)`\s*(?:\u2192|->)\s*`([^`]+)`")
ENV = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1", "PATH": "/usr/bin:/bin"}


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, env=ENV)


def main():
    argv = sys.argv[1:]
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    tip = git(a.repo, "rev-parse", "--verify", a.tip + "^{commit}").stdout.decode().strip()
    sc = git(a.repo, "cat-file", "-p", f"{tip}:SCORECARD.md")
    if sc.returncode:
        print("could-not-evaluate: SCORECARD.md missing at tip", file=sys.stderr)
        return 2
    text = sc.stdout.decode(errors="replace")
    spec = importlib.util.spec_from_file_location("selfdesc", SELFDESC)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    try:
        tip, c, mism, d, maxn = m.evaluate(os.path.abspath(a.repo), a.tip, str(HERE))
    except (RuntimeError, subprocess.CalledProcessError, AttributeError, ValueError) as e:
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        return 2
    line = " ".join(f"{k}={v}" for k, v in c.items()) + f" mismatches={mism} maxN={maxn} met={mism == 0}"
    declared = None
    for ln in text.split("\n"):
        if "capability-repertoire-audit" in ln:
            for cmd, want in COUNT_RE.findall(ln):
                if "verifier-spotcheck" in cmd:
                    declared = want
            break
    files = git(a.repo, "ls-tree", "-r", "--name-only", tip).stdout.decode().split("\n")
    observed = len([p for p in files if SPOT.fullmatch(p)])
    out = "\n".join([f"tip={tip}", line, *d,
                     f"sc_sha256={hashlib.sha256(sc.stdout).hexdigest()}",
                     f"declared_spotcheck={declared} observed_spotcheck={observed}"]) + "\n"
    sys.stdout.write(out)
    if a.out:
        pathlib.Path(a.out).write_text(out)
    return 0 if mism == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
