#!/usr/bin/env python3
"""Distinct case 24: independent check of the assigned stale-maxN case.

Deliberately does not import, copy or reuse run.sh, maxn-cases.py, or the
patched counter's helper. It derives maxN twice from the pinned git blobs with
two independent scanners, tests the frozen claim's literal against tree and
control bytes, and builds its own fixture to compare the frozen counter with
the scratch prototype.
"""
import os
import re
import shutil
import subprocess

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
HERE = os.path.dirname(os.path.abspath(__file__))
S = os.environ.get("S", "/fast/scratch/hyaku/kama-r57/R57Item03CounterRepair")
BASE = "b89bdab2cc114735ec5d331c6c610134258f7864"
TIP = "8640e34cad02adcd247ba0862da63f6fb2aab0df"
R46 = "4340cf2f68ebbfb618086e16825c2e7effd7fa58"
COUNTER_BASE = f"{LANE}/tools/round42-selfdesc-reconcile.py"
COUNTER_BUILD = f"{HERE}/prototype/build/round42-selfdesc-reconcile.py"


def blob(rev):
    return subprocess.run(["git", "-C", LANE, "show", f"{rev}:SCORECARD.md"],
                          capture_output=True, text=True, check=True).stdout


def maxn_regex(text):
    hits = [int(m.group(1)) for m in re.finditer(r"(?m)^## Round (\d+)", text)]
    return max(hits)


def maxn_state_machine(text):
    # Independent scanner: only the first token of a line decides fence state.
    live, state, width, comment = [], None, 0, False
    for line in text.splitlines():
        s = line.lstrip(" ")
        if comment:
            if "-->" in line:
                comment = False
            continue
        if state is None:
            if s[:4] == "<!--":
                comment = "-->" not in s[4:]
                continue
            if s[:3] in ("```", "~~~"):
                state = s[0]
                width = len(s) - len(s.lstrip(s[0]))
                continue
            live.append(line)
        else:
            run = len(s) - len(s.lstrip(s[0])) if s[:1] == state else 0
            if run >= width and s[run:].strip() == "":
                state = None
    return max(int(m.group(1)) for line in live
               for m in [re.match(r"## Round (\d+)", line)] if m)


texts = {rev: blob(rev) for rev in (R46, BASE, TIP)}
print("rev|regex_maxN|state_machine_maxN")
for rev, text in texts.items():
    print(f"{rev}|{maxn_regex(text)}|{maxn_state_machine(text)}")

noop = open(f"{LANE}/.ufo/waves/round-57/controls/c1-noop.py").read()
print("noop_literal_46=", "maxN=46" in noop)
print("noop_reads_tree=", any(k in noop for k in ("open(", "subprocess", "SCORECARD", "git ")))

# Own fixture: base blob + a fenced restored block carrying a stale heading.
fx = f"{S}/fixtures-case24"
os.makedirs(f"{S}/tmp", exist_ok=True)
shutil.rmtree(fx, ignore_errors=True)
os.makedirs(fx, exist_ok=True)
with open(f"{fx}/SCORECARD.md", "w") as f:
    f.write(texts[BASE])
    f.write("\n`````\nDeleted by `feedface` (case-24 fixture:\n\n`````text\n"
            "## Round 99 — stale restored heading (never measured)\n`````\n")
subprocess.run(["git", "-C", fx, "init", "-q"], check=True)
subprocess.run(["git", "-C", fx, "add", "SCORECARD.md"], check=True)
subprocess.run(["git", "-C", fx, "-c", "user.name=kama-seat",
                "-c", "user.email=seat@example.invalid", "commit", "-q",
                "-m", "case24 fixture"], check=True)
top = subprocess.run(["git", "-C", fx, "rev-parse", "--show-toplevel"],
                     capture_output=True, text=True, check=True).stdout.strip()
print("fixture_toplevel_matches=", top == fx)

env = dict(os.environ, TMPDIR=f"{S}/tmp")
out = {}
for label, counter in (("base", COUNTER_BASE), ("build", COUNTER_BUILD)):
    p = subprocess.run(["python3", counter, "--repo", fx, "--tip", "HEAD"],
                       capture_output=True, text=True, env=env)
    line = next(l for l in p.stdout.splitlines() if "maxN=" in l)
    out[label] = (line, p.returncode)
    print(f"fixture_{label}_exit={p.returncode}")
    print(f"fixture_{label}_summary={line}")

base_n = int(re.search(r"maxN=(\d+)", out["base"][0]).group(1))
build_n = int(re.search(r"maxN=(\d+)", out["build"][0]).group(1))
print(f"stale_fixture_base_maxN={base_n} stale_fixture_build_maxN={build_n}")
ok = (maxn_regex(texts[BASE]) == 56 and maxn_state_machine(texts[BASE]) == 56
      and maxn_regex(texts[TIP]) == 57 and maxn_state_machine(texts[TIP]) == 57
      and maxn_regex(texts[R46]) == 46 and maxn_state_machine(texts[R46]) == 46
      and "maxN=46" in noop and base_n == 99 and build_n == 56)
print("case24_ok=", ok)
raise SystemExit(0 if ok else 1)
