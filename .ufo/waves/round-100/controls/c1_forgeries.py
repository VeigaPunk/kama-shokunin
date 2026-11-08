#!/usr/bin/env python3
"""Round-100 C1 forgery controls: run the frozen counter through its public path (--repo/--rev)
on a scratch clone whose candidate commit carries the lane working-tree correction (positive) or a
single forged edit of it. Every forgery must exit 1; the positive must exit 0.

usage: c1_forgeries.py --lane <lane repo> --scratch <dir> [--counter tools/round100-record-audit.py]
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FILES = ["SCORECARD.md", "LOG.md", ".ufo/waves/round-100/r99-measured.json"]


def forge_text(s, a, b):
    if s.count(a) != 1:
        raise SystemExit(f"forgery anchor not unique ({s.count(a)}): {a!r}")
    return s.replace(a, b, 1)


FORGERIES = {
    "F1-stray-58pct": ("SCORECARD.md", "6 of 12 (50%): the four", "6 of 12 (50%), 58% with the scribe: the four"),
    "F2-unbound-pointer": ("LOG.md", "The LOG twin did not\n  move:", "The LOG twin (LOG.md:4040) did not\n  move:"),
    "F3-wrong-line": ("SCORECARD.md", "`SCORECARD.md@6776c667:6446`", "`SCORECARD.md@6776c667:6447`"),
    "F4-measured-edit": (".ufo/waves/round-100/r99-measured.json", "mismatches=0 met=True", "mismatches=0  met=True"),
    "F5-log-old-share": ("LOG.md", "6 of 12 (50%): the four", "7 of 12 (58%): the four"),
    "F6-dead-count": ("SCORECARD.md", "had 12 seats, 0 dead", "had 12 seats, 2 dead"),
    "F7-empty-phrase-pointer": ("LOG.md", "`LOG.md@6776c667:4040` (\"10 reported, 2 dead\")", "`LOG.md@6776c667:4040` (\" \")"),
}


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--counter", default="tools/round100-record-audit.py")
    a = ap.parse_args()
    lane = Path(a.lane).resolve()
    Path(a.scratch).mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="c1-forge-", dir=a.scratch)).resolve()
    counter = (lane / a.counter).resolve()
    bad = 0
    try:
        cases = [("P0-positive", None)] + list(FORGERIES.items())
        for name, forg in cases:
            d = root / name
            r = run(["git", "clone", "-q", "--shared", "--no-checkout", str(lane), str(d)])
            if r.returncode:
                raise SystemExit(f"clone failed: {r.stderr}")
            top = run(["git", "-C", str(d), "rev-parse", "--show-toplevel"]).stdout.strip()
            if Path(top).resolve() != d:
                raise SystemExit(f"toplevel mismatch {top} != {d}")
            run(["git", "-C", str(d), "checkout", "-q", "6776c667372a0da8635ebfbda6cbc92d8fb17304"])
            for f in FILES:
                (d / f).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(lane / f, d / f)
            if forg:
                f, x, y = forg
                (d / f).write_text(forge_text((d / f).read_text(), x, y))
            env = dict(os.environ, GIT_AUTHOR_NAME="fixture", GIT_AUTHOR_EMAIL="fixture@scratch.invalid",
                       GIT_COMMITTER_NAME="fixture", GIT_COMMITTER_EMAIL="fixture@scratch.invalid")
            run(["git", "-C", str(d), "add", "--", *FILES])
            c = run(["git", "-C", str(d), "commit", "-q", "-m", name], env=env)
            if c.returncode:
                raise SystemExit(f"commit failed {name}: {c.stderr}")
            p = run([sys.executable, str(counter), "--repo", str(d), "--rev", "HEAD"])
            last = [ln for ln in p.stdout.splitlines() if ln.startswith("RECORD_AUDIT100 ")]
            mm = [ln.split()[1] for ln in p.stdout.splitlines() if ln.startswith("RECORD_AUDIT100_MISMATCH")]
            want = 0 if forg is None else 1
            ok = p.returncode == want
            bad += 0 if ok else 1
            print(f"C1_FORGERY {name} rc={p.returncode} want={want} ok={int(ok)} "
                  f"mismatched={','.join(mm) or '-'} :: {last[0] if last else p.stdout[-200:]!r}")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print(f"C1_FORGERIES cases={len(FORGERIES) + 1} wrong={bad} met={bad == 0}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
