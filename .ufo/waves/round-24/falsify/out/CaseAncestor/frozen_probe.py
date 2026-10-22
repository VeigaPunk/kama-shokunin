#!/usr/bin/env python3
"""Frozen arm on the Ancestor family's plain twin, and the marked twin.

The frozen auditor (r23 base, 0df800e) is read with git cat-file from the
pinned clone, exactly as the grid does.  This measures what the r23 base
would have said for the SAME fixtures, so the r24 repair can be compared
on the Ancestor family alone.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/fast/scratch/hyaku/kama-r24/falsify/CaseAncestor/out")
import promisor_grid_py as G  # noqa: E402

REPO = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseAncestor/repo")
ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseAncestor/out/frozen-root")
AUDIT = REPO / "tools/report-landing-audit.py"
FROZEN = "0df800e896f6bce285a81e794ad4ae1d1e6c3a71"


def frozen_auditor(dest):
    p = subprocess.run(["git", "-C", str(REPO), "cat-file", "blob",
                        f"{FROZEN}:tools/report-landing-audit.py"],
                       capture_output=True, env=G.env())
    dest.write_bytes(p.stdout)
    return dest


def run(name, built, auditor):
    tmp = built["lane"].parent
    code, out, err, to = G.run_auditor(auditor, built["lane"], built["fleet"], tmp, False)
    return {"variant": name, "exit": code, "stderr": err.strip(),
            "stdout_bytes": len(out)}


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    frz = frozen_auditor(ROOT / "frozen-audit.py")
    res = []
    i = 0
    for name, opt in (("marked-missing", dict(lane_mark="config", ancestor=True,
                                               drop=("ancestor",))),
                      ("unmarked-missing", dict(ancestor=True,
                                                drop=("ancestor",))),
                      ("marked-present", dict(lane_mark="config", ancestor=True)),
                      ("unmarked-present", dict(ancestor=True))):
        tmp = ROOT / f"{i:02d}-{name}"
        tmp.mkdir(parents=True, exist_ok=True)
        built = G.build(ROOT, tmp, **opt)
        res.append(run(name, built, frz))
        res.append(run(name + "|current", built, AUDIT))
        i += 1
    print(json.dumps(res, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
