"""Bounded falsification probe for FinalCase32 (PG32 unselected-branch hole).

Every fixture is built by the PINNED grid producer
(tests/report-audit/promisor-grid.py at commit 92063cf...) and audited by the
PINNED auditor (tools/report-landing-audit.py at the same commit).  No other
producer is used.  Nothing is written outside this seat's scratch.
"""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase32/clone")
BASE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase32/variants")
AUDIT = CLONE / "tools/report-landing-audit.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pg = load("pg", CLONE / "tests/report-audit/promisor-grid.py")
aud = load("aud", AUDIT)


def git(repo, *args):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       env=pg.env())
    return p.returncode, p.stdout.decode(errors="replace").rstrip("\n"), \
        p.stderr.decode(errors="replace").strip()


def drop_side_tree(lane):
    """Remove the unselected side branch's TREE object: the hole becomes
    opaque-shaped (a missing tree) instead of a missing blob."""
    rc, tree, err = git(lane, "rev-parse", "side^{tree}")
    assert rc == 0, err
    obj = Path(lane, ".git/objects", tree[:2], tree[2:])
    assert obj.exists(), obj
    obj.unlink()
    return tree


def inventory(repo):
    return pg.object_inventory(repo)


def run_variant(name, opts, mutate=None):
    root = BASE / name
    if root.exists():
        shutil.rmtree(root)
    tmp = root / "case"
    tmp.mkdir(parents=True)
    built = pg.build(root, tmp, **opts)
    lane, fleet = built["lane"], built["fleet"]
    extra = {}
    if mutate:
        extra = mutate(lane, fleet, built)
    tip = git(lane, "rev-parse", "HEAD")[1]
    missing, opaque = aud.missing_reachable(lane, tip)
    before = {"lane": inventory(lane), "fleet": inventory(fleet)}
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata"]
    proc = subprocess.run(argv, capture_output=True, cwd=str(tmp),
                          env=pg.env())
    after = {"lane": inventory(lane), "fleet": inventory(fleet)}
    out = proc.stdout.decode(errors="replace")
    err = proc.stderr.decode(errors="replace")
    doc = None
    try:
        doc = json.loads(out)
    except ValueError:
        pass
    res = {
        "variant": name,
        "opts": {k: v for k, v in opts.items()},
        "mutate": extra,
        "argv": argv,
        "exit": proc.returncode,
        "stderr": err.strip(),
        "stdout_is_json": doc is not None,
        "internal_error": "could-not-evaluate: internal:" in err,
        "traceback": "Traceback (most recent call last)" in err,
        "objects_acquired": {k: sorted(after[k] - before[k]) for k in after},
        "store_wide_missing": sorted(missing),
        "root_scoped_opaque": sorted(opaque),
        "lane_tip": tip,
        "lane_refs": git(lane, "show-ref")[1].split("\n"),
        "fleet_report": git(fleet, "show", "HEAD:.ufo/reports/round-1/kama.md")[1],
    }
    if doc is not None:
        res["summary"] = doc.get("summary")
        res["results"] = doc.get("results")
        res["defects"] = [d for r in doc.get("results", [])
                           for d in r.get("defects", [])]
        res["kinds"] = sorted({d.get("kind") for d in res["defects"]})
    return res


VARIANTS = [
    ("V0-pg32-control", dict(unselected_hole=True,
                              drop=("unselected_blob",)), None),
    ("V1-wrongtype-with-hole", dict(unselected_hole=True, wrong_type=True,
                                    drop=("unselected_blob",)), None),
    ("V2-absent-with-hole", dict(unselected_hole=True, fake_landed=True,
                                 drop=("unselected_blob",)), None),
    ("V3-opaque-side-tree-hole", dict(unselected_hole=True,
                                      drop=("unselected_blob",)),
     lambda lane, fleet, built: {"dropped_side_tree": drop_side_tree(lane)}),
    ("V4-absent-with-opaque-hole", dict(unselected_hole=True, fake_landed=True,
                                        drop=("unselected_blob",)),
     lambda lane, fleet, built: {"dropped_side_tree": drop_side_tree(lane)}),
]

if __name__ == "__main__":
    BASE.mkdir(parents=True, exist_ok=True)
    results = []
    for name, opts, mutate in VARIANTS:
        try:
            results.append(run_variant(name, opts, mutate))
        except Exception as exc:  # a setup failure is evidence, not a kill
            results.append({"variant": name, "harness_error":
                            f"{type(exc).__name__}: {exc}"})
    out = BASE / "results.json"
    out.write_text(json.dumps(results, indent=1), encoding="utf-8")
    for r in results:
        print(r.get("variant"), "exit=", r.get("exit"),
              "kinds=", r.get("kinds"), "defects=", r.get("defects"),
              "acquired=", r.get("objects_acquired"),
              "missing=", r.get("store_wide_missing"),
              "opaque=", r.get("root_scoped_opaque"),
              "stderr=", (r.get("stderr") or "")[:160],
              "harness_error=", r.get("harness_error"))
