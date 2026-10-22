"""V6: the declared twin of PG32 - PG31's fixture (same hole, lane marked
promisor) - run through the PINNED producer + PINNED auditor, and compared
with PG32's own verdict document.  This is NOT a grid cell: it is a direct
auditor invocation on a twin fixture built by the same pinned builder, used
only to check the equality PG32's manifest note declares ("identical to
PG31's document")."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/fast/scratch/hyaku/kama-r24/postfix/FinalCase32")
from variant_probe import (AUDIT, BASE, git, load, pg)  # noqa: E402


def normalise(doc, fleet):
    text = json.dumps(doc, sort_keys=True)
    return text.replace(str(fleet), "<fleet>")


def run(name, opts):
    root = BASE / name
    if root.exists():
        shutil.rmtree(root)
    tmp = root / "case"
    tmp.mkdir(parents=True)
    built = pg.build(root, tmp, **opts)
    lane, fleet = built["lane"], built["fleet"]
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata"]
    proc = subprocess.run(argv, capture_output=True, cwd=str(tmp), env=pg.env())
    out = proc.stdout.decode(errors="replace")
    try:
        doc = json.loads(out)
    except ValueError:
        doc = None
    prom = pg.promisor_facts(lane)
    return {"variant": name, "exit": proc.returncode,
            "stderr": proc.stderr.decode(errors="replace").strip(),
            "document": doc, "normalised": normalise(doc, fleet) if doc else None,
            "lane_promisor_facts": prom,
            "lane_remotes": git(lane, "remote", "-v")[1],
            "refs": git(lane, "show-ref")[1],
            "argv": argv}


if __name__ == "__main__":
    plain = run("V6a-pg32-plain", dict(unselected_hole=True,
                                       drop=("unselected_blob",)))
    marked = run("V6b-pg31-promisor", dict(lane_mark="config",
                                           unselected_hole=True,
                                           drop=("unselected_blob",)))
    out = {"plain": plain, "promisor_twin": marked,
           "documents_equal_after_path_normalisation":
               plain["normalised"] is not None
               and plain["normalised"] == marked["normalised"]}
    (BASE / "v6.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("plain exit", plain["exit"], "stderr", plain["stderr"][:120])
    print("twin  exit", marked["exit"], "stderr", marked["stderr"][:120])
    print("equal:", out["documents_equal_after_path_normalisation"])
    print("promisor facts (twin lane):", json.dumps(marked["lane_promisor_facts"]))
    print("twin lane remotes:", marked["lane_remotes"])
    print("plain normalised == twin normalised:",
          plain["normalised"] == marked["normalised"])
    print("plain doc defects:", plain["document"]["summary"]["defects"],
          "status", plain["document"]["summary"]["status"])
    print("twin  doc defects:", marked["document"]["summary"]["defects"],
          "status", marked["document"]["summary"]["status"])
