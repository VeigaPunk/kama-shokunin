"""V5: positive control on the PG32 fixture - the report CITES the missing
unselected-branch blob.  The two-root diagnosis must then fire: exit 2, a
content-derived reason naming the unavailable object, no verdict document,
and not the r23 metadata refusal.  This shows the machinery is alive and
discriminates between an unrelated hole (V0) and a required one (V5)."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/fast/scratch/hyaku/kama-r24/postfix/FinalCase32")
from variant_probe import (AUDIT, BASE, git, load, pg)  # noqa: E402


def run_v5():
    name = "V5-cited-hole-positive-control"
    root = BASE / name
    if root.exists():
        shutil.rmtree(root)
    tmp = root / "case"
    tmp.mkdir(parents=True)
    built = pg.build(root, tmp, unselected_hole=True,
                     drop=("unselected_blob",))
    lane, fleet = built["lane"], built["fleet"]
    hole = "2299c37978265a95cbe835a4b0f0bbf15aad5549"
    # rewind the fleet report commit and republish the same commit time with
    # a report that CITES the missing blob
    rc, _, err = git(fleet, "reset", "--hard", "HEAD~1")
    assert rc == 0, err
    text = "# kama round 1\n\n## Landed changes\n\n- %s\n" % hole
    pg.publish(fleet, text, 2000)
    before = {"lane": pg.object_inventory(lane),
              "fleet": pg.object_inventory(fleet)}
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata"]
    proc = subprocess.run(argv, capture_output=True, cwd=str(tmp), env=pg.env())
    after = {"lane": pg.object_inventory(lane),
             "fleet": pg.object_inventory(fleet)}
    out = proc.stdout.decode(errors="replace")
    err = proc.stderr.decode(errors="replace")
    is_json = False
    try:
        json.loads(out)
        is_json = True
    except ValueError:
        pass
    res = {"variant": name, "argv": argv, "exit": proc.returncode,
           "stderr": err.strip(), "stdout_len": len(out),
           "stdout_is_json_document": is_json,
           "stdout_head": out[:200],
           "internal_error": "could-not-evaluate: internal:" in err,
           "traceback": "Traceback (most recent call last)" in err,
           "objects_acquired": {k: sorted(after[k] - before[k]) for k in after},
           "names_unavailable_object": hole in err,
           "forbidden_metadata_reason": ("partial clone (" in err
                                         or "promisor pack" in err),
           "stderr_starts_cne": err.startswith("could-not-evaluate:"),
           "report": git(fleet, "show", "HEAD:.ufo/reports/round-1/kama.md")[1]}
    (BASE / "v5.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    run_v5()
