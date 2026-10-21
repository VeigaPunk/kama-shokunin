#!/usr/bin/env python3
"""F23 premise check: what does an otherwise identical full repository say,
and does all-ref object closure separate F23 from a complete marker-only
repository citing a fabricated hash? Usage: SCRATCH_ROOT"""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
spec = importlib.util.spec_from_file_location(
    "grid", LANE / "tests/report-audit/repo-state-grid.py")
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)
ISO = ["--no-replace-objects", "--no-lazy-fetch"]
root = Path(sys.argv[1])
shutil.rmtree(root, ignore_errors=True)
root.mkdir(parents=True)
frozen = root / "frozen-audit.py"
frozen.write_bytes(subprocess.run(
    ["git", "-C", str(LANE), "show", f"{grid.FROZEN}:{grid.AUDIT}"],
    capture_output=True, check=True).stdout)
r23 = root / "r23-audit.py"
r23.write_bytes(subprocess.run(
    ["git", "-C", str(LANE), "show", f"0df800e:{grid.AUDIT}"],
    capture_output=True, check=True).stdout)


def audit(tool, lane, fleet):
    p = subprocess.run([sys.executable, str(tool), "--lane-repo", str(lane),
                        "--fleet-repo", str(fleet), "--rounds", "1",
                        "--no-errata", "--json"], capture_output=True,
                       env=grid.env())
    kinds = None
    if p.returncode in (0, 1):
        kinds = sorted({d["kind"] for r in json.loads(p.stdout)["results"]
                        for d in r["defects"]})
    return p.returncode, kinds, p.stderr.decode().strip()[:120]


def closure(repo):
    p = subprocess.run(["git", *ISO, "-C", str(repo), "rev-list", "--objects",
                        "--all", "--missing=print"], capture_output=True,
                       env=grid.env())
    miss = [l for l in p.stdout.decode().split("\n") if l.startswith("?")]
    return p.returncode, miss


def show(label, lane, fleet):
    print(f"## {label}")
    print("  frozen(r22):", audit(frozen, lane, fleet))
    print("  r23        :", audit(r23, lane, fleet))
    print("  closure lane --all:", closure(lane), " fleet:", closure(fleet))


t = root / "f23"
t.mkdir()
clone, fleet, _, _ = grid.f_promisor_pack(t)
origin = t / "lane"
show("F23 blobless clone, promisor config removed (grid row as built)",
     clone, fleet)
show("F23 full twin: the origin lane the clone was made from", origin, fleet)

t = root / "marker"
t.mkdir()
lane, fleet = grid.pair(t)
lc = grid.commit(lane, "kama-shokunin", 1000, "round-1: work")
grid.publish(fleet, grid.report([lc]) + b"\n## Notes\n\nsee " +
             grid.FAKE.encode() + b"\n")
twin = t / "twin"
shutil.copytree(lane, twin, symlinks=True)
grid.g(lane, "repack", "-adq")
pack = next(Path(lane, ".git/objects/pack").glob("*.pack"))
pack.with_suffix(".promisor").write_bytes(b"")
show("complete lane, paired .promisor marker only, fabricated 40-hex cited",
     lane, fleet)
show("its full twin (same objects, no marker)", twin, fleet)
