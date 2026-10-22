import importlib.util, json, os, sys
from pathlib import Path
CLONE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase37/clone")
sys.path.insert(0, str(CLONE / "tests/report-audit"))

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

grid = load("promisor_grid", CLONE / "tests/report-audit/promisor-grid.py")
aud = load("report_landing_audit", CLONE / "tools/report-landing-audit.py")

root = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase37/tmp-inspect/root")
root.mkdir(parents=True, exist_ok=True)
tmp = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase37/tmp-inspect/root/000")
tmp.mkdir(parents=True, exist_ok=True)
built = grid.BUILDERS["c_unused_missing_blob_fabricated_plain"](root, tmp)
print("PREMIISE:", json.dumps(built["premise"], indent=1))
print("SHAS:", json.dumps(built["shas"], indent=1))
print("lane:", built["lane"], "fleet:", built["fleet"])
for label, repo, ref in (("lane", built["lane"], "refs/heads/master"),
                         ("fleet", built["fleet"], "HEAD")):
    missing, opaque = aud.missing_reachable(repo, ref)
    types = {}
    for oid in sorted(missing):
        t = aud.git(repo, "--no-lazy-fetch", "--no-replace-objects", "cat-file", "-t", oid) if False else None
        types[oid] = None
    # classify object type of the missing ids without fetching: use the grid's own type probe
    for oid in sorted(missing):
        p = aud.git_type = None
    print(f"{label} missing={[ (o, ) for o in sorted(missing)]}")
    print(f"{label} opaque={sorted(opaque)}")
    print(f"{label} FAKE_in_missing={built['shas']['fake'] in missing}")
    print(f"{label} FAKE_in_opaque={built['shas']['fake'] in opaque}")
# type of the missing objects: ask git for the type of the object id recorded in the tree
for label, repo in (("lane", built["lane"]), ("fleet", built["fleet"])):
    for key in ("unused_blob",):
        sha = built["shas"].get(key)
        if not sha:
            continue
        out = grid.git(repo, "rev-list", "--objects", "--missing=print", "--no-object-names", "refs/heads/master")
        print(f"{label} rev-list missing lines:", [l for l in out.split("\n") if l.startswith("?")])
        # the tree entry name that references it
        print(f"{label} tree entries referencing {sha}:",
              grid.git(repo, "ls-tree", "-r", "refs/heads/master").splitlines()[:10])
