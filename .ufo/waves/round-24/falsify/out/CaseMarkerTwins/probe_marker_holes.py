#!/usr/bin/env python3
"""MarkerTwins x hole probe (benign offline fixture).

Question: the fixed47 has no row that combines the PROMISOR MARKER with a
missing object.  Two combinations are therefore untested by the grid:
  (a) marker + a REQUIRED object missing  -> must be exit 2 with a
      content-derived reason naming the object;
  (b) marker + an UNRELATED object missing -> must stay the plain verdict.
The grid builder cannot express either (drop_object needs a loose object;
mark_markers repacks and then fails on the hole), so this probe builds the
promisor pack the way git itself expects -- pack the objects that ARE
present, then write the paired pack-<sha>.promisor marker (git convention,
see the vendored git source .ufo/waves/round-24/build/out/SrcPromisorCode/
packfile.c.v2.56.0:726-748) -- and compares against the plain twin.

No new git flag is used (git 2.56 `git repack -h` has no --missing option),
so no Git floor is raised.  Nothing in production is touched.
"""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseMarkerTwins")
spec = importlib.util.spec_from_file_location(
    "pg", CLONE / "tests/report-audit/promisor-grid.py")
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)
AUDIT = str(CLONE / "tools/report-landing-audit.py")
ROOT = CLONE / "probe-marker-holes"


def marker_only(lane):
    """Give the store a real promisor pack without repacking the closure."""
    gd = pg.git_dir(lane)
    oids = pg.git(lane, "cat-file", "--batch-all-objects",
                  "--batch-check=%(objectname)").split()
    stdin = "".join(o + "\n" for o in oids)
    p = subprocess.run(
        ["git", "-C", str(lane), "pack-objects",
         str(gd / "objects" / "pack" / "pack")],
        input=stdin.encode(), capture_output=True, env=pg.env())
    assert p.returncode == 0, p.stderr
    h = p.stdout.decode().strip()
    packdir = gd / "objects" / "pack"
    (packdir / f"pack-{h}.promisor").write_bytes(b"")
    for d in sorted((gd / "objects").iterdir()):
        if len(d.name) == 2 and d.is_dir():
            for f in d.iterdir():
                f.unlink()
            d.rmdir()
    return f"pack-{h}"


def run(case, mark, **opt):
    tmp = ROOT / case
    tmp.mkdir(parents=True, exist_ok=True)
    b = pg.build(ROOT, tmp, **opt)
    if mark:
        marker_only(b["lane"])
    facts = pg.promisor_facts(b["lane"])
    before = {"lane": pg.object_inventory(b["lane"]),
              "fleet": pg.object_inventory(b["fleet"])}
    r = subprocess.run(
        [sys.executable, AUDIT, "--lane-repo", str(b["lane"]),
         "--fleet-repo", str(b["fleet"]), "--rounds", "1", "--json",
         "--no-errata"], capture_output=True, env=pg.env(), cwd=str(tmp))
    after = {"lane": pg.object_inventory(b["lane"]),
             "fleet": pg.object_inventory(b["fleet"])}
    doc = json.loads(r.stdout.decode()) if r.stdout.strip() else None
    err = (r.stderr.decode().strip().replace(str(b["lane"]), "<lane>")
           .replace(str(b["fleet"]), "<fleet>"))
    return {"exit": r.returncode, "stderr": err,
            "defects": pg.observed_defects(r.stdout.decode())[0],
            "acquired": {k: sorted(after[k] - before[k]) for k in after},
            "doc": doc, "promisor": facts["promisor_backed"],
            "markers": facts["markers"],
            "missing": pg.missing_objects(b["lane"], "refs/heads/master")}


def main():
    shutil.rmtree(ROOT, ignore_errors=True)
    ROOT.mkdir(parents=True)
    a_m = run("a-marker-required-hole", True, drop=("sources_blob",))
    a_p = run("a-plain-required-hole", False, drop=("sources_blob",))
    b_m = run("b-marker-unused-hole", True, unused_file=True,
              drop=("unused_blob",))
    b_p = run("b-plain-unused-hole", False, unused_file=True,
              drop=("unused_blob",))
    for n, r in (("marker+required-hole", a_m), ("plain+required-hole", a_p),
                 ("marker+unrelated-hole", b_m),
                 ("plain+unrelated-hole", b_p)):
        print(f"{n:23s} exit={r['exit']} promisor={r['promisor']} "
              f"markers={r['markers']} missing={r['missing']}")
        print(f"    acquired={r['acquired']} defects={r['defects']}")
        print(f"    stderr={r['stderr'][:240]}")
    print("(a) marker reason == plain reason (path-normalised):",
          a_m["stderr"] == a_p["stderr"])
    print("(b) marker verdict == plain verdict:",
          b_m["exit"] == b_p["exit"] and b_m["defects"] == b_p["defects"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
