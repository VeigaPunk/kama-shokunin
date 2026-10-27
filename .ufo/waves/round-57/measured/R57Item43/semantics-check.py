#!/usr/bin/env python3
"""Compare canonical heading semantics between the frozen and repaired counter.

Both modules are imported unmodified; the frozen module's `canon()` is reused and
its inline maxN expression is replicated literally, so the comparison is between
the counter's own selection rules, not between two hand-written expectations.

Usage: semantics-check.py <lane> <tip> <fixtures-dir>
"""
import importlib.util
import os
import re
import subprocess
import sys


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def frozen_maxn(text):
    # verbatim expression from tools/round42-selfdesc-reconcile.py (frozen)
    lines = text.split("\n")
    rounds = [int(m.group(1)) for l in lines for m in [re.match(r"^## Round (\d+)", l)] if m]
    return max(rounds), rounds


def show(repo, tip, path):
    p = subprocess.run(["git", "-C", repo, "cat-file", "-p", f"{tip}:{path}"], capture_output=True)
    return p.stdout.decode(errors="replace") if p.returncode == 0 else None


def main():
    lane, tip, fixdir = sys.argv[1], sys.argv[2], sys.argv[3]
    here = os.path.dirname(os.path.abspath(__file__))
    base = load(os.path.join(here, "round42-selfdesc-reconcile.py"), "frozen")
    rep = load(os.path.join(here, "round42-selfdesc-reconcile.repaired.py"), "repaired")
    texts = {}
    for label, t in (("tip:b89bdab2", "b89bdab2cc114735ec5d331c6c610134258f7864"), (f"tip:{tip[:8]}", tip)):
        sc = show(lane, t, "SCORECARD.md")
        if sc is None:
            print(f"could-not-evaluate: SCORECARD.md missing at {t}")
            return 2
        texts[label] = sc
    for name in ("canonical-noop", "no-canonical"):
        p = os.path.join(fixdir, name, "SCORECARD.md")
        with open(p, encoding="utf-8", errors="replace") as f:
            texts[f"fixture:{name}"] = f.read()
    stale = re.sub(r"^## Round (\d+)", lambda m: f"## Retained round {m.group(1)}" if int(m.group(1)) >= 47 else m.group(0),
                   texts["tip:b89bdab2"], flags=re.M)
    texts["mutation:stale46"] = stale
    bad = 0
    for label, text in texts.items():
        fmax, rounds = frozen_maxn(text)
        rmax, headings = rep.derive_maxn(text)
        fround, frows = base.canon(text)
        rround, rrows = rep.canon(text)
        fnames = sorted(r[0].strip("` *") for r in frows if r)
        rnames = sorted(r[0].strip("` *") for r in rrows if r)
        ok = (fmax == rmax and len(rounds) == headings and fround == rround and fnames == rnames)
        bad += 0 if ok else 1
        print(f"{label}: frozen_maxN={fmax} repaired_maxN={rmax} headings={headings} "
              f"frozen_canon_round={fround} repaired_canon_round={rround} "
              f"canon_rows={len(rnames)} same_names={int(fnames == rnames)} same={ok}")
        if label == "mutation:stale46":
            print(f"  stale46 headings>=47 renamed: frozen_maxN={fmax} "
                  f"head_declares=56 banner_consistent={int(fmax == 56)}")
    print(f"semantics: cases={len(texts)} divergent={bad} met={bad == 0}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
