#!/usr/bin/env python3
"""White-box probe of the pinned auditor's per-store bare lookup and
canonical merge (lookup()/bare_objects() in tools/report-landing-audit.py).

Read-only: it builds no fixture, mutates nothing and runs the pinned
auditor's own functions against the PG04 fixture that the pinned grid
builder produced.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase04/clone")
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24"
           "/postfix/out/FinalCase04")
FIX = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase04/controls-root"
           "/C0-pg04-asis/case")

spec = importlib.util.spec_from_file_location(
    "rla", CLONE / "tools/report-landing-audit.py")
RLA = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RLA)
assert hashlib.sha256(Path(RLA.__file__).read_bytes()).hexdigest() == \
    "b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f"


def git(repo, *args):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       env=e)
    return p.stdout.decode().strip()


lane, fleet = FIX / "lane", FIX / "fleet"
tip = git(lane, "rev-parse", "--verify", "refs/heads/master^{commit}")
ftip = git(fleet, "rev-parse", "--verify", "HEAD^{commit}")
stores = (RLA.build_store(lane, tip), RLA.build_store(fleet, ftip))
l1 = git(lane, "rev-parse", "HEAD")
f0 = git(fleet, "rev-parse", f"{ftip}~1")
FAKE = "0123456789abcdef0123456789abcdef01234567"
short = l1[:8]

tokens = [l1, f0, FAKE, short]
bare = {}
for name, store in (("lane", stores[0]), ("fleet", stores[1])):
    bare[name] = RLA.bare_objects(store, tokens)
res = {
    "lane_tip": tip, "fleet_tip": ftip,
    "tokens": {"lane_commit_l1": l1, "fleet_commit_f0": f0,
               "fabricated": FAKE, "abbrev": short},
    "bare_objects": {k: {t: list(v) for t, v in val.items()}
                     for k, val in bare.items()},
    "lookup_no_peel": RLA.lookup(stores, tokens),
    "lookup_peel_commit": RLA.lookup(stores, tokens, "^{commit}"),
    "lookup_peel_commit_per_token": {
        t: RLA.lookup(stores, [t], "^{commit}")[t] for t in tokens},
    "rank": RLA.RANK,
}
(OUT / "merge-probe.json").write_text(json.dumps(res, indent=1,
                                                  sort_keys=True) + "\n")
print(json.dumps(res, indent=1, sort_keys=True))
