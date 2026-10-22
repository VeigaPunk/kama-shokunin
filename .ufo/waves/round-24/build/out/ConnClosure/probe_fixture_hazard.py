#!/usr/bin/env python3
"""ConnClosure: independent reproduction of the fixture hazard reported by
peer KamaR23-2.CaseFleetBlobless.

Claim under test: the r24 grid's blobless clone keeps `remote.origin.url`
pointing at a REACHABLE local file:// origin, so any git probe WITHOUT
--no-lazy-fetch lazy-fetches, materialises the missing blob, and the fixture
premise evaporates -- letting the auditor return a false clean instead of the
correct exit 2.

Reproduced here with the grid's OWN helpers (blobless_clone, object_exists,
missing_objects), offline and local.

Measured (git 2.56.0):
  * clone remote.origin.url -> file:///.../origin, origin still on disk
  * before a stray probe: object_exists -> False, missing_objects -> [oid]
  * one stray `git cat-file -e <oid>` (no --no-lazy-fetch): rc 0, blob now
    present, missing_objects -> []      <-- premise destroyed
  * the auditor alone, run twice: exit 2 both times, premise intact
    (the auditor carries --no-lazy-fetch in GIT_ISOLATION)
  * auditor after the stray probe: exit 1 with a failed finding -- the
    content-derived refusal became a verdict

Which probe FORM materialises:
  path    `cat-file -e HEAD:f`      -> materialises (rc 0)
  raw oid `cat-file -e <oid>`       -> materialises (rc 0)
  peel    `cat-file -e HEAD:f^{blob}`-> does NOT (rc 128, path does not exist)
  with --no-lazy-fetch: every form correctly reports absence (rc 1)

No network transport: the "remote" is a local directory reached over file://.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

GRID = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/tests/"
            "report-audit/promisor-grid.py")
CAND = Path("/fast/scratch/hyaku/kama-r24/ConnClosure/auditors/cand.py")
OUT = Path(__file__).resolve().parent


def load_grid():
    spec = importlib.util.spec_from_file_location("pg", GRID)
    pg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pg)
    return pg


def make_origin(pg, tmp):
    origin = tmp / "origin"
    origin.mkdir()
    subprocess.run(["git", "-C", str(origin), "init", "-q", "-b", "master"],
                   check=True)
    (origin / "f").write_text("payload\n")
    subprocess.run(["git", "-C", str(origin), "add", "f"], check=True)
    subprocess.run(["git", "-C", str(origin), "-c", "commit.gpgsign=false",
                    "commit", "-q", "-m", "round-1: work"], check=True,
                   env=pg.env())
    return origin


def main():
    pg = load_grid()
    res = {}

    # 1. which probe form materialises a missing blob
    tmp = Path(tempfile.mkdtemp(prefix="cc-form-", dir="/tmp"))
    origin = make_origin(pg, tmp)
    clone = pg.blobless_clone(tmp, origin, tmp / "lane")
    oid = pg.git(origin, "rev-parse", "HEAD:f").strip()
    forms = {
        "path": ["git", "-C", str(clone), "cat-file", "-e", "HEAD:f"],
        "raw_oid": ["git", "-C", str(clone), "cat-file", "-e", oid],
        "peel_path": ["git", "-C", str(clone), "cat-file", "-e",
                      "HEAD:f^{blob}"],
    }
    for name, cmd in forms.items():
        t = Path(tempfile.mkdtemp(prefix=f"cc-{name}-", dir="/tmp"))
        o2 = make_origin(pg, t)
        c2 = pg.blobless_clone(t, o2, t / "lane")
        oid2 = pg.git(o2, "rev-parse", "HEAD:f").strip()
        cmd2 = [x.replace(str(clone), str(c2)).replace(oid, oid2)
                for x in cmd]
        p = subprocess.run(cmd2, capture_output=True, env=pg.env())
        res[f"probe_form_{name}"] = {
            "rc": p.returncode,
            "blob_present_after": pg.object_exists(c2, oid2),
            "missing_after": pg.missing_objects(c2, "HEAD"),
        }
    # the same forms WITH --no-lazy-fetch
    for name, cmd in forms.items():
        t = Path(tempfile.mkdtemp(prefix=f"cc-nf-{name}-", dir="/tmp"))
        o2 = make_origin(pg, t)
        c2 = pg.blobless_clone(t, o2, t / "lane")
        oid2 = pg.git(o2, "rev-parse", "HEAD:f").strip()
        cmd2 = ["git", "--no-lazy-fetch"] + [
            x.replace(str(clone), str(c2)).replace(oid, oid2) for x in cmd[1:]]
        p = subprocess.run(cmd2, capture_output=True, env=pg.env())
        res[f"probe_form_{name}_with_no_lazy_fetch"] = {
            "rc": p.returncode,
            "blob_present_after": pg.object_exists(c2, oid2),
            "missing_after": pg.missing_objects(c2, "HEAD"),
        }

    # 2. the auditor's own isolation, and the false verdict after a stray probe
    tmp = Path(tempfile.mkdtemp(prefix="cc-aud-", dir="/tmp"))
    fleet = tmp / "fleet"
    fleet.mkdir()
    subprocess.run(["git", "-C", str(fleet), "init", "-q", "-b", "master"],
                   check=True)
    rel = ".ufo/reports/round-1/kama.md"
    pth = fleet / rel
    pth.parent.mkdir(parents=True, exist_ok=True)
    pth.write_text("# r1\n## Landed changes\n- `deadbee1` work\n")
    subprocess.run(["git", "-C", str(fleet), "add", rel], check=True)
    subprocess.run(["git", "-C", str(fleet), "-c", "commit.gpgsign=false",
                    "commit", "-q", "-m", "round-1: kama report"], check=True,
                   env=pg.env())
    lane = tmp / "lane"
    lane.mkdir()
    subprocess.run(["git", "-C", str(lane), "init", "-q", "-b", "master"],
                   check=True)
    (lane / "f").write_text("x\n")
    subprocess.run(["git", "-C", str(lane), "add", "f"], check=True)
    subprocess.run(["git", "-C", str(lane), "-c", "commit.gpgsign=false",
                    "commit", "-q", "-m", "round-1: work"], check=True,
                   env=pg.env())
    reg = lane / "registry/report-landing-errata.tsv"
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text("# round\tkind\ttoken\tcorrection\tevidence\n")
    subprocess.run(["git", "-C", str(lane), "add",
                    "registry/report-landing-errata.tsv"], check=True)
    subprocess.run(["git", "-C", str(lane), "-c", "commit.gpgsign=false",
                    "commit", "-q", "-m", "round-1: registry"], check=True,
                   env=pg.env())
    origin2 = tmp / "fleet-origin"
    subprocess.run(["git", "clone", "-q", "--bare", str(fleet), str(origin2)],
                   check=True, env=pg.env())
    subprocess.run(["git", "-C", str(origin2), "config",
                    "uploadpack.allowFilter", "true"], check=True)
    fclone = pg.blobless_clone(tmp, origin2, tmp / "fleet-clone")
    rblob = pg.git(fleet, "rev-parse", f"HEAD:{rel}").strip()

    def audit():
        q = subprocess.run([sys.executable, str(CAND), "--lane-repo", str(lane),
                            "--fleet-repo", str(fclone), "--rounds", "1",
                            "--json"], capture_output=True, env=pg.env(),
                           timeout=120)
        kinds = []
        if q.returncode in (0, 1):
            d = json.loads(q.stdout.decode())
            kinds = [(x["kind"], x["token"][:10]) for r in d["results"]
                     for x in r["defects"]]
        return {"rc": q.returncode, "kinds": kinds,
                "stderr": q.stderr.decode().strip()[:160]}

    res["auditor_alone_run1"] = audit()
    res["premise_after_run1"] = {
        "blob_present": pg.object_exists(fclone, rblob),
        "missing": pg.missing_objects(fclone, "HEAD")}
    res["auditor_alone_run2"] = audit()
    res["premise_after_run2"] = {
        "blob_present": pg.object_exists(fclone, rblob),
        "missing": pg.missing_objects(fclone, "HEAD")}
    sp = subprocess.run(["git", "-C", str(fclone), "cat-file", "-e", rblob],
                        capture_output=True, env=pg.env())
    res["stray_probe"] = {"rc": sp.returncode,
                          "blob_present_after": pg.object_exists(fclone, rblob),
                          "missing_after": pg.missing_objects(fclone, "HEAD")}
    res["auditor_after_stray_probe"] = audit()

    out = OUT / "probe_fixture_hazard-result.json"
    out.write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
