#!/usr/bin/env python3
"""round43-registry-audit.py - kama round-43 C1 (calibration) counter.

Question: at a revision, does the lane's written self-description of its own
instruments match what the tree contains? Six mismatch counts, each derived
from committed bytes; the claim is `mismatches == 0` with a non-vacuous
population.

Facts (frozen before data; every fact counts MISMATCHES, so 0 is clean):
  unreg     `tools/gate-registry-check.py --repo R --rev TIP` (the tool as
            committed at TIP) prints `registered R unregistered U defective D`;
            unreg = U.
  defect    D from the same line.
  flags     for each tracked counter the gate's population names (tools/round<N>-*.py
            and .ufo/waves/round-*/count-*.py) that is registered in a SKILL.md
            registry row (a 5-column row whose cells contain the path): the
            row's Kind/entry-command cell must name at least one `--flag`, and
            every `--flag` it names must occur in the counter's source at TIP.
            One mismatch per counter that fails either clause. A counter with
            no registry row is counted by `unreg`, not here.
  selftest  SKILL.md at TIP documents `GATE_SELFTEST pass=P fail=0`; the tool's
            `--selftest`, run in a throwaway clone of R with branch `master` set
            to TIP, must print exactly `GATE_SELFTEST pass=P fail=0` and exit 0.
            One mismatch when not.
  dc        corpus/SOURCES.md at TIP carries, after the round-42 search-log
            entry (the line containing `round-42 K05 engine-side sources`), a
            search-log line (starting `- **`) that names S401 and S424, the word
            `correction` and the text `opened`. One mismatch when absent
            (routed round-42 defect D-C).
  spot      SCORECARD.md at TIP has a `| calibration |` row stating
            `N` immediately before `(outside closures on record)` where N must
            equal the number of corpus/lessons/*verifier-spotcheck.md blobs at TIP.
            One mismatch when the figure is absent or different.
  hidden    README.md at TIP names `.gitignore` and `.ufo`; one mismatch per
            name absent.
  pop       number of counters in the gate's population at TIP; the claim
            needs pop >= POP_MIN (guards against a vacuous population).

met = (mismatches == 0 and pop >= POP_MIN and registered >= POP_MIN).
Output: `tip=<full>` then
  unreg=U defect=D flags=F selftest=S dc=C spot=P hidden=H pop=N registered=R mismatches=M met=True|False
then `detail:` lines. Exit 0 met, 1 not met, 2 could not evaluate.
Read-only on --repo; temporary directories are removed (also on SIGTERM).
"""
from __future__ import annotations

import argparse
import atexit
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile

POP_MIN = 28
COUNTER_RE = re.compile(r"^(?:\.ufo/waves/round-[^/]+/count-[^/]+|tools/round[0-9]+-[A-Za-z0-9._-]+)\.py$")
FLAG_RE = re.compile(r"(?<![\w-])--[a-z][a-z0-9-]*")
_tmp: list[str] = []


def _cleanup() -> None:
    while _tmp:
        shutil.rmtree(_tmp.pop(), ignore_errors=True)


atexit.register(_cleanup)
signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))


def git(repo: str, *args: str, binary: bool = False):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout if binary else p.stdout.decode(errors="replace")


def blob(repo: str, rev: str, path: str):
    p = subprocess.run(["git", "-C", repo, "cat-file", "-p", f"{rev}:{path}"], capture_output=True)
    return p.stdout if p.returncode == 0 else None


def mktmp(prefix: str) -> str:
    d = tempfile.mkdtemp(prefix=prefix)
    _tmp.append(d)
    return d


def evaluate(repo: str, tip: str):
    tip = git(repo, "rev-parse", "--verify", f"{tip}^{{commit}}").strip()
    d: list[str] = []
    files = [p for p in git(repo, "ls-tree", "-r", "--name-only", "-z", tip).split("\0") if p]
    pop = sorted(p for p in files if COUNTER_RE.match(p))
    skill = (blob(repo, tip, "SKILL.md") or b"").decode(errors="replace")
    # gate at TIP
    gate_src = blob(repo, tip, "tools/gate-registry-check.py")
    unreg = defect = registered = -1
    if gate_src is None:
        d.append("detail: tools/gate-registry-check.py absent at tip")
    else:
        ex = mktmp("r43c1-")
        gp = os.path.join(ex, "gate.py")
        open(gp, "wb").write(gate_src)
        p = subprocess.run([sys.executable, gp, "--repo", repo, "--rev", tip], capture_output=True, text=True, timeout=120)
        m = re.search(r"registered (\d+) unregistered (\d+) defective (\d+)", p.stdout)
        if not m:
            raise RuntimeError(f"gate printed no summary (exit {p.returncode}): {p.stderr[:200]}")
        registered, unreg, defect = int(m.group(1)), int(m.group(2)), int(m.group(3))
        for l in p.stdout.splitlines():
            if l.startswith(("unregistered ", "defective ")):
                d.append(f"detail: gate {l}")
    # flags
    rows = [l for l in skill.split("\n") if l.startswith("|") and len([c for c in l.strip().strip("|").split("|")]) >= 5]
    flags = 0
    for path in pop:
        hit = [l for l in rows if path in l]
        if not hit:
            continue
        src = (blob(repo, tip, path) or b"").decode(errors="replace")
        ok = False
        for l in hit:
            cells = [c.strip() for c in l.strip().strip("|").split("|")]
            named = FLAG_RE.findall(cells[1]) if len(cells) > 1 else []
            if named and all(f in src for f in named):
                ok = True
                break
        if not ok:
            flags += 1
            d.append(f"detail: flags: {path} row names no --flag or a flag absent from the source")
    # selftest
    selftest = 1
    m = re.search(r"`GATE_SELFTEST pass=(\d+) fail=0`", skill)
    if m and gate_src is not None:
        want = f"GATE_SELFTEST pass={m.group(1)} fail=0"
        ex = mktmp("r43c1s-")
        cl = os.path.join(ex, "c")
        subprocess.run(["git", "clone", "-q", "--no-hardlinks", repo, cl], check=True, capture_output=True)
        subprocess.run(["git", "-C", cl, "branch", "-f", "master", tip], check=True, capture_output=True)
        subprocess.run(["git", "-C", cl, "checkout", "-q", "--detach", tip], check=True, capture_output=True)
        p = subprocess.run([sys.executable, os.path.join(cl, "tools/gate-registry-check.py"), "--selftest"],
                           capture_output=True, text=True, cwd=cl, timeout=300)
        last = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ""
        if p.returncode == 0 and last == want:
            selftest = 0
        else:
            d.append(f"detail: selftest: documented {want!r}, run printed {last!r} exit {p.returncode}")
    else:
        d.append("detail: selftest: SKILL.md documents no `GATE_SELFTEST pass=N fail=0`")
    # dc
    src = (blob(repo, tip, "corpus/SOURCES.md") or b"").decode(errors="replace").split("\n")
    idx = next((i for i, l in enumerate(src) if "round-42 K05 engine-side sources" in l), None)
    dc = 1
    if idx is not None:
        for l in src[idx + 1:]:
            if l.startswith("- **") and "S401" in l and "S424" in l and "correction" in l.lower() and "opened" in l:
                dc = 0
                break
    if dc:
        d.append("detail: dc: no correction line for the round-42 search-log entry after it")
    # spot
    n_spot = sum(1 for p in files if re.match(r"^corpus/lessons/[^/]*verifier-spotcheck\.md$", p))
    sc = (blob(repo, tip, "SCORECARD.md") or b"").decode(errors="replace")
    spot = 1
    for l in sc.split("\n"):
        if l.startswith("| calibration |"):
            m = re.search(r"`(\d+)` \(outside closures on record\)", l)
            if m and int(m.group(1)) == n_spot:
                spot = 0
            else:
                d.append(f"detail: spot: calibration row states {m.group(1) if m else 'none'}, tree holds {n_spot}")
            break
    else:
        d.append("detail: spot: no `| calibration |` row")
    # hidden
    rd = (blob(repo, tip, "README.md") or b"").decode(errors="replace")
    hidden = sum(1 for n in (".gitignore", ".ufo") if n not in rd)
    if hidden:
        d.append(f"detail: hidden: README.md names {2 - hidden} of .gitignore, .ufo")
    mism = max(unreg, 0) + max(defect, 0) + flags + selftest + dc + spot + hidden
    met = mism == 0 and len(pop) >= POP_MIN and registered >= POP_MIN
    return tip, dict(unreg=unreg, defect=defect, flags=flags, selftest=selftest, dc=dc, spot=spot,
                     hidden=hidden, pop=len(pop), registered=registered, mismatches=mism), met, d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--tip", default="HEAD")
    ap.add_argument("--out")
    a = ap.parse_args()
    try:
        tip, f, met, d = evaluate(os.path.abspath(a.repo), a.tip)
    except (RuntimeError, subprocess.SubprocessError, OSError) as e:
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        return 2
    line = " ".join(f"{k}={v}" for k, v in f.items()) + f" met={met}"
    out = "\n".join([f"tip={tip}", line, *d]) + "\n"
    sys.stdout.write(out)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        open(a.out, "w").write(out)
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
