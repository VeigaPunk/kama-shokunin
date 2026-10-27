#!/usr/bin/env python3
"""Probe the frozen C2 counter's `superseded` class for base-line anchoring.

Claim under test: the preregistration predicate (round-55/preregistration.json,
claims.C2.predicate) requires "`superseded` rows disclosing a LIVE BASE CITATION
RE-POINTED to a cited, resolving replacement" and "no citation dropped on any of the
three surfaces since the base".

The `fixed` class is anchored: check_row() requires the replacement to be cited at the
BASE CITATION LINE of the token (M15 fixture: "fixed replacement cited away from the
base line is bad"). The `superseded` class is NOT anchored: it requires only that
(a) the token is not cited at tip, (b) the replacement is cited SOMEWHERE in the same
surface at tip and resolves, (c) the token was cited at base.

This driver builds three scratch fixture repos and calls the counter's own evaluate():
  A  honest re-point    : base line 2 cites live.py; tip line 2 cites new.py  (row superseded)
  B  UNANCHORED re-point: base line 2 cites live.py; tip DROPS it and cites new.py
                           on an unrelated line 7                     (row superseded)
  C  live-vs-dead base  : base line 2 cites a path that does NOT exist (so the base
                           citation was DEAD, not live); tip cites new.py on line 2
                                                                    (row superseded)

No lane file is touched; the fixtures live under the scratch dir only.
Usage: probe_superseded_anchor.py <counter-path> <scratch-dir>
"""
import importlib.util
import os
import shutil
import subprocess
import sys

counter_path, scratch = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("r54c2", counter_path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

os.makedirs(scratch, exist_ok=True)
env = m.clean_env({"GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@invalid",
                   "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@invalid",
                   "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"})


def run(D, *a):
    p = subprocess.run(["git", "-C", D, *a], capture_output=True, env=env)
    if p.returncode:
        raise SystemExit(f"git {a}: {p.stderr.decode()[:300]}")
    return p.stdout.decode().strip()


def write(D, path, text):
    full = os.path.join(D, path)
    os.makedirs(os.path.dirname(full) or D, exist_ok=True)
    with open(full, "w") as fh:
        fh.write(text)


def build(name, base_scard, tip_scard, ledger=None):
    D = os.path.join(scratch, name)
    shutil.rmtree(D, ignore_errors=True)
    os.makedirs(D)
    run(D, "init", "-q")
    if os.path.realpath(run(D, "rev-parse", "--show-toplevel")) != os.path.realpath(D):
        raise SystemExit("fixture repo is not its own toplevel")
    write(D, "tools/live.py", "live\n")
    write(D, "tools/new.py", "new\n")
    write(D, "tools/dead.py", "dead\n")
    write(D, "SKILL.md", "x\n")
    write(D, "SHONEN.md", "x\n")
    write(D, "SCORECARD.md", base_scard)
    run(D, "add", "-A")
    run(D, "commit", "-q", "--allow-empty", "-m", "base")
    base_rev = run(D, "rev-parse", "HEAD")
    write(D, "SCORECARD.md", tip_scard)
    if ledger is None:
        if os.path.exists(os.path.join(D, m.LEDGER)):
            os.unlink(os.path.join(D, m.LEDGER))
    else:
        write(D, m.LEDGER, "surface\ttoken\tclass\tevidence\tnote\n" + ledger)
    run(D, "add", "-A")
    run(D, "commit", "-q", "--allow-empty", "-m", "tip")
    tip_rev = run(D, "rev-parse", "HEAD")
    return D, base_rev, tip_rev


ROW = "SCORECARD.md\ttools/live.py\tsuperseded\ttools/new.py\t\n"

CASES = {
    "A_honest_repoint_at_base_line": (
        "hdr\n`tools/live.py`\ntail\n",
        "hdr\n`tools/new.py`\ntail\n",
        ROW),
    "B_UNANCHORED_repoint_elsewhere": (
        "hdr\n`tools/live.py`\ntail\n",
        "hdr\nnothing here\nx\ny\nz\nw\n`tools/new.py`\ntail\n",
        ROW),
    "C_DEAD_base_citation": (
        "hdr\n`tools/dead.py`\ntail\n",
        "hdr\n`tools/new.py`\ntail\n",
        "SCORECARD.md\ttools/dead.py\tsuperseded\ttools/new.py\t\n"),
}

for name, (bs, ts, ledger) in CASES.items():
    D, brev, trev = build(name, bs, ts, ledger)
    detail = []
    ok, c = m.evaluate(m.Repo(D, trev), None, m.Repo(D, brev), detail, verbose=True)
    print(f"--- {name}: met={ok} counts={c}")
    for d in detail:
        print("      ", d)
    shutil.rmtree(D, ignore_errors=True)
