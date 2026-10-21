#!/usr/bin/env python3
"""Hidden-name hole: a promisor lane misses tree `d` AND the blob `d/f` it
names. The cited blob is then absent from `rev-list --missing=print` (only
the tree is listed), so token membership cannot see that history names it.
Compared with a blob-only hole. Usage: SCRATCH_ROOT"""
import importlib.util
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


def gi(repo, *a, data=None):
    p = subprocess.run(["git", *ISO, "-C", str(repo), *a], input=data,
                       capture_output=True, env=grid.env())
    return p.returncode, p.stdout.decode().strip()


def hole(repo, drop):
    assert gi(repo, "rev-parse", "--show-toplevel")[1] == str(repo)
    gi(repo, "repack", "-adq")
    keep = [o for o in gi(repo, "cat-file", "--batch-all-objects",
                          "--batch-check=%(objectname)")[1].split()
            if o not in drop]
    new = repo.parent / (repo.name + ".new")
    new.mkdir()
    rc, h = gi(repo, "pack-objects", "-q", str(new / "pack"),
               data=("\n".join(keep) + "\n").encode())
    assert rc == 0 and h
    pd = repo / ".git/objects/pack"
    for p in pd.glob("pack-*"):
        p.unlink()
    for p in new.glob("pack-*"):
        p.rename(pd / p.name)
    new.rmdir()
    (pd / f"pack-{h}.promisor").write_bytes(b"")
    for o in drop:
        assert gi(repo, "cat-file", "-e", o)[0] != 0


def build(name, hide_tree):
    t = root / name
    t.mkdir()
    lane, fleet = grid.pair(t)
    lc = grid.commit(lane, "kama-shokunin", 1000, "round-1: work", "d/f")
    grid.commit(lane, "kama-shokunin", 900, "unrelated", "u")
    blob = gi(lane, "rev-parse", "HEAD:d/f")[1]
    tree = gi(lane, "rev-parse", "HEAD:d")[1]
    grid.publish(fleet, grid.report([lc]) + b"\n## Notes\n\nblob " +
                 blob.encode() + b"\n")
    twin = t / "twin"
    shutil.copytree(lane, twin, symlinks=True)
    hole(lane, [blob, tree] if hide_tree else [blob])
    return lane, twin, fleet, blob, tree


def audit(tool, lane, fleet):
    p = subprocess.run([sys.executable, str(tool), "--lane-repo", str(lane),
                        "--fleet-repo", str(fleet), "--rounds", "1",
                        "--no-errata"], capture_output=True, env=grid.env())
    return p.returncode, (p.stdout + p.stderr).decode().strip().splitlines()[-1:]


for name, hide_tree in (("blob-hole", False), ("tree-hole", True)):
    lane, twin, fleet, blob, tree = build(name, hide_tree)
    _, listing = gi(lane, "rev-list", "--objects", "--all",
                    "--missing=print-info")
    missing = [l for l in listing.split("\n") if l.startswith("?")]
    print(f"## {name}: cited blob {blob[:12]} under tree {tree[:12]}")
    print("  missing listed:", missing)
    print("  cited token listed as missing:", any(blob in l for l in missing))
    print("  frozen on full twin :", audit(frozen, twin, fleet))
    print("  frozen on holed lane:", audit(frozen, lane, fleet))
