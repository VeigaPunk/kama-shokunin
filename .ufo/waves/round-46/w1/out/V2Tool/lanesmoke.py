#!/usr/bin/env python3
"""V2Tool round-46 lane smoke: run append-only-audit.py on the lane at the
calibration commit 0163fea2 and check the 5 claimed events. READ-ONLY on the
lane: every git invocation is a read (proof: GIT_TRACE receipt)."""
import json
import os
import re
import shutil
import subprocess
import sys
import time

TOOL = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
REV = "0163fea2dab3f282ebd70c71da9ab5de4cedf733"
OUT = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/V2Tool"
S = os.environ["V2SCRATCH"]
TMP = os.path.join(S, "tmp")


def git(*a):
    p = subprocess.run(["git", "-C", LANE, *a], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git -C LANE {' '.join(a)}: {p.stderr.decode(errors='replace')[:300]}")
    return p.stdout.decode().strip()


receipt = []


def say(line):
    print(line)
    receipt.append(line)


def main():
    say(f"lane HEAD: {git('rev-parse', 'HEAD')}")
    say(f"tool file dirty vs HEAD: {git('status', '--porcelain', '--', 'tools/append-only-audit.py')!r}")
    before = git("status", "--porcelain")
    trace = os.path.join(S, "trace-lane.txt")
    env = dict(os.environ, TMPDIR=TMP, GIT_TRACE=trace)
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, TOOL, "--repo", LANE, "--to", REV, "--json"],
                       capture_output=True, env=env, timeout=1800)
    dt = time.monotonic() - t0
    rc, out, err = p.returncode, p.stdout.decode(errors="replace"), p.stderr.decode(errors="replace")
    after = git("status", "--porcelain")
    say(f"elapsed: {dt:.2f}s rc={rc} stderr={err[:200]!r}")
    say(f"status --porcelain identical before/after: {before == after} (before lines={len(before.splitlines())}, after lines={len(after.splitlines())})")
    j = json.loads(out)
    with open(os.path.join(OUT, "lane-events.json"), "w") as fh:
        json.dump(j, fh, indent=1)
    evs = j["events"]
    say(f"event count: {len(evs)} (claim: 5), summary={j['summary']}")
    checks = []
    e0718 = [e for e in evs if e["commit"].startswith("0718b6ab")]
    trio = {e["file"] for e in e0718 if e["file"] in ("LOG.md", "corpus/QUALITY.md", "corpus/README.md")}
    checks.append(("3 trio files restored by 82b5e9d3",
                   len(trio) == 3 and all(e["status"] == "restored" and e["restored_by"].startswith("82b5e9d3")
                                          and e["deleted"] == e["restored_at_tip"] for e in e0718 if e["file"] in trio)))
    say("trio detail: " + repr([(e["file"], e["deleted"], e["restored_at_tip"], e["status"], (e["restored_by"] or "")[:8]) for e in e0718 if e["file"] in trio]))
    sc = [e for e in e0718 if e["file"] == "SCORECARD.md"]
    checks.append(("0718b6ab SCORECARD partial 2416/2417",
                   len(sc) == 1 and sc[0]["status"] == "partial" and sc[0]["deleted"] == 2417
                   and sc[0]["restored_at_tip"] == 2416 and sc[0]["restored_by"] is None))
    dd9 = [e for e in evs if e["commit"].startswith("dd9f5dc6")]
    checks.append(("dd9f5dc6 SCORECARD partial 24/31",
                   len(dd9) == 1 and dd9[0]["file"] == "SCORECARD.md" and dd9[0]["status"] == "partial"
                   and dd9[0]["deleted"] == 31 and dd9[0]["restored_at_tip"] == 24 and dd9[0]["restored_by"] is None))
    checks.append(("exit code agrees (rc==1 with 2 partials)", rc == 1))
    for name, ok in checks:
        say(f"check {'PASS' if ok else 'FAIL'}: {name}")
    lines = open(trace, errors="replace").read().splitlines()
    builtin = [l for l in lines if "built-in: git" in l]
    read_only = all(re.search(r"built-in: git (rev-parse|rev-list|diff|cat-file) ", l) for l in builtin)
    say(f"git calls: {len(builtin)}; all read-only (rev-parse/rev-list/diff/cat-file): {read_only}")
    say("unique command heads: " + repr(sorted({l.split('built-in: git ')[1].split(' -- ')[0].rsplit(' --', 1)[0].split()[0] + ' ' + (l.split('built-in: git ')[1].split()[1] if len(l.split('built-in: git ')[1].split()) > 1 else '') for l in builtin})))
    shutil.copy(trace, os.path.join(OUT, "trace-lane.txt"))
    with open(os.path.join(OUT, "receipt-lane.txt"), "w") as fh:
        fh.write("\n".join(receipt) + "\n")
    print("LANE_SMOKE " + ("PASS" if all(ok for _, ok in checks) else "FAIL"))


if __name__ == "__main__":
    main()
