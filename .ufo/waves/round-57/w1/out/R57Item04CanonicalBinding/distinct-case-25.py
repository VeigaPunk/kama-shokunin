#!/usr/bin/env python3
"""distinct-case-25.py - independent test of case 25 (item R57Item04CanonicalBinding).

Case 25 asks whether the content-bound canonical capability-row audit tracks the
row CONTENT at a revision rather than a typed constant or an instrument's
self-description.  This driver tests it from a second surface: it derives the
table from four different SCORECARD states plus one mutation of the live table,
and checks that the audit's round, row count, row digests and verdicts move with
the bytes.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
AUDIT = os.path.join(HERE, "canon-row-audit.py")
WORK = os.path.join(HERE, "case25")


def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def kv(out: str) -> dict[str, str]:
    d: dict[str, str] = {}
    for tok in out.split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            d.setdefault(k, v)
    return d


def audit(args: list[str]) -> tuple[int, str, dict[str, str]]:
    rc, out = run([sys.executable, AUDIT] + args)
    return rc, out, kv(out)


def main() -> int:
    shutil.rmtree(WORK, ignore_errors=True)
    os.makedirs(WORK)
    checks: list[tuple[str, str, str]] = []

    live = open(os.path.join(LANE, "SCORECARD.md")).read()

    # 1. two revisions of the same file: freeze base and current tip
    rc, out, s = audit(["--repo", LANE, "--tip", "b89bdab2"])
    checks.append(("rev-base-b89bdab2", f"canon={s.get('canon')} rows={s.get('rows')} "
                                        f"bound={s.get('bind')} met={s.get('met')} exit={rc}",
                    "PASS" if rc == 0 and s.get("met") == "True" else "FAIL"))
    open(os.path.join(WORK, "rev-base.out"), "w").write(out)

    rc, out, s_tip = audit(["--repo", LANE, "--tip", "HEAD"])
    checks.append(("rev-tip", f"canon={s_tip.get('canon')} rows={s_tip.get('rows')} "
                              f"bound={s_tip.get('bind')} met={s_tip.get('met')} exit={rc}",
                    "PASS" if rc == 0 and s_tip.get("met") == "True" else "FAIL"))
    open(os.path.join(WORK, "rev-tip.out"), "w").write(out)

    # 2. the two frozen wave-57 control trees: audit derives whatever table the
    #    bytes hold, so `no-canonical` (round-49 block removed) must fall back
    for tree in ("canonical-noop", "no-canonical"):
        p = os.path.join(LANE, ".ufo/waves/round-57/controls", tree, "SCORECARD.md")
        rc, out, s = audit(["--repo", LANE, "--tip", "HEAD", "--scorecard", p])
        open(os.path.join(WORK, f"tree-{tree}.out"), "w").write(out)
        checks.append((f"tree-{tree}", f"canon={s.get('canon')} rows={s.get('rows')} "
                                       f"mismatches={s.get('mismatches')} met={s.get('met')} exit={rc}",
                        "PASS" if s.get("canon") else "FAIL"))

    # 3. mutation: change one row's capability text in BOTH the canonical table
    #    and the mirror; the row digest must move while the audit stays met
    base_dig = dict(re.findall(r"row (\S+) sha=(\S+)", open(os.path.join(WORK, "rev-tip.out")).read()))
    both = re.sub(r"(\| sources-registry \| )Curate where kama learns",
                  r"\1CURATE-MUTATED where kama learns", live)
    bp = os.path.join(WORK, "mutated-both.md")
    open(bp, "w").write(both)
    rc, out, s = audit(["--repo", LANE, "--tip", "HEAD", "--scorecard", bp])
    open(os.path.join(WORK, "mutated-both.out"), "w").write(out)
    mu = dict(re.findall(r"row (\S+) sha=(\S+)", out))
    moved = mu.get("sources-registry") != base_dig.get("sources-registry")
    checks.append(("mutate-what-both", f"digest_moved={moved} met={s.get('met')} exit={rc}",
                    "PASS" if moved and rc == 0 and s.get("met") == "True" else "FAIL"))

    # 4. mutation: change the mirror row only; the canonical/mirror content
    #    binding must report the divergence
    mir = re.sub(r"(\| sources-registry \| )Curate where kama learns",
                 r"\1CURATE-MUTATED where kama learns", live, count=1)
    mp = os.path.join(WORK, "mutated-mirror.md")
    open(mp, "w").write(mir)
    rc, out, s = audit(["--repo", LANE, "--tip", "HEAD", "--scorecard", mp])
    open(os.path.join(WORK, "mutated-mirror.out"), "w").write(out)
    checks.append(("mutate-mirror-only", f"met={s.get('met')} exit={rc} mismatches={s.get('mismatches')}",
                    "PASS" if rc == 1 and s.get("met") == "False" else "FAIL"))

    # 4. mutation: delete the highest canonical heading only; the audit must
    #    fall back to the next one, not silently keep its old constant
    stripped = re.sub(r"^\*\*Capabilities — canonical list as of round 49\*\*$", "", live, flags=re.M)
    sp = os.path.join(WORK, "drop-round49-heading.md")
    open(sp, "w").write(stripped)
    rc, out, s = audit(["--repo", LANE, "--tip", "HEAD", "--scorecard", sp])
    open(os.path.join(WORK, "drop-round49-heading.out"), "w").write(out)
    checks.append(("drop-canon-heading", f"canon={s.get('canon')} rows={s.get('rows')} exit={rc}",
                    "PASS" if str(s.get("canon","")).startswith("round48") else "FAIL"))

    # 5. mutation: remove the mirror table; audit must fail closed (exit 2)
    no_mirror = re.sub(r"^## Capabilities$", "## Capabilities-RENAMED", live, flags=re.M)
    np = os.path.join(WORK, "no-mirror.md")
    open(np, "w").write(no_mirror)
    rc, out, s = audit(["--repo", LANE, "--tip", "HEAD", "--scorecard", np])
    open(os.path.join(WORK, "no-mirror.out"), "w").write(out)
    checks.append(("no-mirror-fail-closed", f"exit={rc} streams={'present' if out.strip() else 'empty'}",
                    "PASS" if rc == 2 else "FAIL"))

    failed = 0
    for name, obs, verdict in checks:
        failed += verdict == "FAIL"
        print(f"case25 check={name:<26} {obs:<62} verdict={verdict}")
    print(f"summary checks={len(checks)} failed={failed} met={failed == 0}")
    print(f"live_sha256={hashlib.sha256(live.encode()).hexdigest()}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
