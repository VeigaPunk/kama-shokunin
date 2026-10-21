#!/usr/bin/env python3
"""Frozen-fairness probes: rebuild grid fixtures, neutralize or respell the
fault, and run frozen/current auditors on both forms."""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

CLONE = Path("/tmp/kama-r23w2/CritFrozenFairness")
spec = importlib.util.spec_from_file_location(
    "grid", CLONE / "tests/report-audit/repo-state-grid.py")
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)
FROZEN = Path("/tmp/kama-r23w2/CritFrozenFairness-frozen.py")
CURRENT = CLONE / "tools/report-landing-audit.py"


def audit(tool, lane, fleet, errata=False, rounds="1"):
    argv = [sys.executable, str(tool), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--json", "--rounds", rounds]
    if not errata:
        argv.append("--no-errata")
    p = subprocess.run(argv, capture_output=True, env=G.env(), timeout=30)
    kinds = None
    if p.returncode in (0, 1):
        doc = json.loads(p.stdout)
        kinds = sorted({d["kind"] for r in doc["results"] for d in r["defects"]})
        s = doc["summary"]
        kinds = (kinds, "invalid=%s unmatched=%s uncorrected=%s" % (
            s["errata_invalid"], s["errata_unmatched"], s["uncorrected"]))
    return p.returncode, kinds, p.stderr.decode(errors="replace").strip()[-160:]


def show(label, lane, fleet, **kw):
    for name, tool in (("frozen", FROZEN), ("current", CURRENT)):
        print(f"{label} {name}: {audit(tool, lane, fleet, **kw)}")


def tmpdir():
    return Path(tempfile.mkdtemp(prefix="crit-ff-", dir="/tmp/kama-r23w2"))


# F17: HEAD versus the full hash HEAD names
t = tmpdir()
lane, fleet, _, _ = G.f_errata_revision(t)
show("F17-HEAD", lane, fleet, errata=True)
head = G.g(lane, "rev-parse", "HEAD")
G.commit(lane, "fixture", 1700, "errata full", "registry/report-landing-errata.tsv",
         f"1\tunresolved-full-hash\t{G.FAKE}\t{head}\tev\n".encode())
show("F17-fullhash-of-same-commit", lane, fleet, errata=True)

# F21: subdirectory versus the real lane
t = tmpdir()
sub, fleet, _, _ = G.f_nested_subdir(t)
show("F21-subdir", sub, fleet)
show("F21-real-lane", Path(t, "lane"), fleet)

# F23: blobless clone without config versus its origin lane
t = tmpdir()
clone, fleet, _, _ = G.f_promisor_pack(t)
show("F23-clone", clone, fleet)
show("F23-origin-lane", Path(t, "lane"), fleet)
print("F23 clone config:", G.g(clone, "config", "--list", "--name-only").split())

# F11: does git's own --no-replace-objects already ignore grafts?
t = tmpdir()
lane, fleet, _, _ = G.f_grafts(t)
for flag in ([], ["--no-replace-objects"]):
    p = subprocess.run(["git", *flag, "-C", str(lane), "rev-list", "--count",
                        "HEAD"], capture_output=True, env=G.env())
    print("F11 rev-list", flag, p.stdout.decode().strip(),
          p.stderr.decode().strip()[-120:])

# F10: shallow, objects kept
t = tmpdir()
lane, fleet, _, _ = G.f_shallow(t)
Path(lane, ".git/shallow").unlink()
show("F10-unshallowed", lane, fleet)

# F07 / F08 / F12: frozen on the same fixture with the fault knob removed
t = tmpdir()
lane, fleet, _, _ = G.f_log_follow(t)
show("F07-with-log.follow", lane, fleet)
G.g(fleet, "config", "--unset", "log.follow")
show("F07-knob-removed", lane, fleet)
t = tmpdir()
lane, fleet, _, _ = G.f_show_root(t)
show("F08-with-showRoot=false", lane, fleet)
G.g(fleet, "config", "--unset", "log.showRoot")
show("F08-knob-removed", lane, fleet)
t = tmpdir()
lane, fleet, _, _ = G.f_tag_shadow(t)
show("F12-tag", lane, fleet)
G.g(lane, "tag", "-d", "master")
show("F12-tag-removed", lane, fleet)

# F26: what git emits for the huge author time
t = tmpdir()
lane, fleet, _, _ = G.f_huge_timestamp(t)
out = G.g(lane, "log", "-1", "--format=%at")
print("F26 %at digits:", len(out), "cutoff-report author time 2000")

# F15: sha256 lane, the cited token
t = tmpdir()
lane, fleet, _, _ = G.f_sha256_lane(t)
print("F15 report:", G.g(fleet, "show", f"HEAD:{G.REL}").split("\n")[-1])
