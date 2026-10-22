#!/usr/bin/env python3
"""Variant controls for the same-tag-both-stores consumer family.

Variant A: tag target blob ALSO copied into the lane store (both targets
present) -> must not be a false positive.
Variant B: tag target blob removed from the fleet store (target missing
everywhere) -> must not be silently accepted as a verdict.

Built from the COMMITTED driver scenario(); the pristine case is untouched.
"""
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer05")
C = S / "clone"
DRV = C / ".ufo/waves/round-24/fixes/StoreLocalPresence/proof-driver-replay-v3.py"
BEFORE = S / "out/before-report-landing-audit.py"
AFTER = C / "tools/report-landing-audit.py"

spec = importlib.util.spec_from_file_location("replay3", DRV)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def git(repo, *args):
    p = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch", "-C",
                        str(repo), *args], capture_output=True, timeout=30,
                       env={"GIT_CONFIG_GLOBAL": "/dev/null",
                            "GIT_CONFIG_NOSYSTEM": "1", "PATH": "/usr/bin:/bin"})
    return p.returncode, p.stdout.decode("utf-8", "replace").strip(), \
        p.stderr.decode("utf-8", "replace").strip()


def loose(repo, oid):
    return Path(repo, git(repo, "rev-parse", "--git-path", "objects")[1],
                oid[:2], oid[2:])


def tag_and_target(repo, tag_oid):
    rc, out, err = git(repo, "cat-file", "tag", tag_oid)
    target = None
    for line in out.splitlines():
        if line.startswith("object "):
            target = line.split(" ", 1)[1].strip()
    return target


def run(label, version, lane, fleet, draft):
    cmd = [sys.executable, str(version), "--lane-repo", str(lane),
           "--fleet-repo", str(fleet), "--branch", "master", "--rounds", "1",
           "--report", f"1={draft}", "--json", "--no-errata"]
    p = subprocess.run(cmd, capture_output=True, timeout=60)
    rec = {"argv": cmd, "exit": p.returncode,
           "stderr": p.stderr.decode("utf-8", "replace").strip()[:300]}
    try:
        doc = json.loads(p.stdout.decode("utf-8", "replace"))
        rec["kinds"] = sorted({d["kind"] for res in doc["results"]
                               for d in res["defects"]})
        rec["errata_invalid"] = doc["summary"].get("errata_invalid")
        rec["by_kind"] = doc["summary"].get("by_kind")
        rec["defects"] = [d for res in doc["results"] for d in res["defects"]]
    except Exception as exc:
        rec["kinds"] = None
        rec["errata_invalid"] = None
        rec["parse_error"] = repr(exc)
    return rec


results = {}
for variant in ("A-both-targets-present", "B-target-missing-everywhere"):
    root = S / f"fixture/variant-{variant}"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    lane, fleet, draft, errata = mod.scenario(str(root), "same-tag-both-stores")
    draft_text = Path(draft).read_text(encoding="utf-8")
    import re
    tag_oid = re.findall(r"`([0-9a-f]{40})`", draft_text)[-1]
    target = tag_and_target(fleet, tag_oid)
    if variant.startswith("A"):
        dst = loose(lane, target)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(loose(fleet, target).read_bytes())
    else:
        loose(fleet, target).unlink()
    rec = {"tag_oid": tag_oid, "target_oid": target,
           "draft": draft_text,
           "lane_target_type": git(lane, "cat-file", "-t", target)[1]
           or git(lane, "cat-file", "-t", target)[2][:120],
           "fleet_target_type": git(fleet, "cat-file", "-t", target)[1]
           or git(fleet, "cat-file", "-t", target)[2][:120],
           "lane_tag_type": git(lane, "cat-file", "-t", tag_oid)[1],
           "fleet_tag_type": git(fleet, "cat-file", "-t", tag_oid)[1]}
    rec["before"] = run("before", BEFORE, lane, fleet, draft)
    rec["after"] = run("after", AFTER, lane, fleet, draft)
    results[variant] = rec

results["hashes"] = {
    "before_sha256": hashlib.sha256(BEFORE.read_bytes()).hexdigest(),
    "after_sha256": hashlib.sha256(AFTER.read_bytes()).hexdigest(),
    "driver_sha256": hashlib.sha256(DRV.read_bytes()).hexdigest()}
(S / "out/variant-controls.json").write_text(
    json.dumps(results, indent=1, sort_keys=True), encoding="utf-8")
print(json.dumps(results, indent=1, sort_keys=True))
