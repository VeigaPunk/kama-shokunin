#!/usr/bin/env python3
"""Reconcile the fixture's own run-fact citations (fixture-only, never the lane)."""
import re
import subprocess
import sys
from pathlib import Path

D = Path("/fast/scratch/hyaku/kama-r71/CRT01ClaimsAttack/fx/nocite")
SC = D / "SCORECARD.md"
IDENT = ["-c", "user.name=r71", "-c", "user.email=r71@example.invalid"]
RUN_RE = re.compile(r"run `(.+?)` no stdout line == '(.+?)'")


def sh(*cmd, cwd=None):
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True)


def commit(msg):
    sh("git", "-C", str(D), "add", "-A")
    r = sh("git", "-C", str(D), *IDENT, "commit", "-q", "--allow-empty", "-m", msg)
    assert r.returncode == 0, r.stderr
    return sh("git", "-C", str(D), "rev-parse", "--short", "HEAD").stdout.strip()


def main():
    for it in range(6):
        p = sh(sys.executable, "tools/round42-selfdesc-reconcile.py", "--repo", ".", "--tip", "master", cwd=D)
        details = [ln for ln in p.stdout.splitlines() if ln.startswith("detail:")]
        print(f"iter {it}: reconciler exit={p.returncode} mismatches={len(details)}")
        text = SC.read_text(encoding="utf-8")
        changed = False
        for ln in details:
            m = RUN_RE.search(ln)
            if not m:
                continue
            cmd, want = m.group(1), m.group(2)
            q = sh("bash", "-c", cmd, cwd=D)
            got = [l.strip() for l in q.stdout.splitlines() if l.strip()]
            got = got[-1] if got else ""
            if not got or got == want:
                print(f"  cannot re-derive for {cmd[:60]!r}: got={got!r}")
                continue
            if want in text:
                text = text.replace(want, got, 1)
                changed = True
                print(f"  {want!r} -> {got!r} for {cmd[:50]!r}")
            else:
                print(f"  literal {want!r} not found in SCORECARD")
        if changed:
            SC.write_text(text, encoding="utf-8")
            head = commit(f"fixture: reconcile run facts {it}")
            print(f"  committed {head}")
        if not changed:
            print("no run-fact literal left to reconcile")
            break
    p = sh(sys.executable, "tools/round42-selfdesc-reconcile.py", "--repo", ".", "--tip", "master", cwd=D)
    print("final reconciler:", [l for l in p.stdout.splitlines() if "mismatches=" in l])


if __name__ == "__main__":
    sys.exit(main())
