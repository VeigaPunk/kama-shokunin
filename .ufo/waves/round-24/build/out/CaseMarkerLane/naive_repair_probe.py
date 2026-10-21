#!/usr/bin/env python3
"""Discriminator probe for the CaseMarkerLane oracle case.

Question: does "stop refusing on a .promisor marker alone" (the naive
repair) keep the *incomplete* promisor-backed lane honest?

Fixture F23-style: a blobless clone (git's own partial clone) whose promisor
config keys were removed, so the repository still carries the paired
.pack/.promisor marker but genuinely LACKS a blob the report cites.
Truth (round-24 contract): the required object is unavailable -> exit 2
could-not-evaluate, never a clean or failed verdict.

Observation 1: the r23 base refuses it (exit 2, "promisor pack").
Observation 2: with ONLY the marker file removed (ablation of the refusal),
the same repository audits to a FAILED verdict (exit 1) — a wrong verdict
that treats unavailable evidence as proved absence.

Therefore the CaseMarkerLane case (marker + complete + clean) MUST be graded
in the same arm as this case; alone it would let the naive repair pass.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time

LANE_DIR = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
AUDIT = LANE_DIR / "tools/report-landing-audit.py"
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/CaseMarkerLane")
REL = ".ufo/reports/round-1/kama.md"
TIMEOUT = 30


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       env=env(**extra))
    if check and p.returncode:
        raise RuntimeError(f"git {' '.join(map(str, args))}: "
                           f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def commit(repo, author, when, msg, path="f", content=None):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        with open(target, "ab") as fh:
            fh.write((msg + "\n").encode())
    else:
        target.write_bytes(content)
    g(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return g(repo, "rev-parse", "HEAD")


def run_audit(lane, fleet, tmp):
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--no-errata",
            "--json"]
    p = subprocess.run(argv, capture_output=True, env=env(), cwd=str(tmp),
                       timeout=TIMEOUT)
    kinds, defects = None, []
    if p.returncode in (0, 1):
        try:
            doc = json.loads(p.stdout)
            kinds = sorted({d["kind"] for r in doc["results"]
                            for d in r["defects"]})
            defects = sorted({(d["kind"], d["token"])
                              for r in doc["results"] for d in r["defects"]})
        except (ValueError, KeyError, TypeError):
            kinds = "unparseable"
    return {"exit": p.returncode, "kinds": kinds, "defects": defects,
            "stderr": p.stderr.decode(errors="replace").strip()}


def main():
    run_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    root = SCRATCH / run_id / "naive-repair-probe"
    root.mkdir(parents=True, exist_ok=True)
    out = {"probe": "naive-repair discriminator", "run_id": run_id,
           "scratch": str(root), "observations": {}, "expectations": {}}

    src = Path(root, "src")
    src.mkdir()
    g(root, "init", "-q", "-b", "master", str(src))
    lc = commit(src, "kama-shokunin", 1000, "round-1: work")
    blob = g(src, "rev-parse", f"{lc}:f")
    g(src, "config", "uploadpack.allowFilter", "true")
    clone = Path(root, "blobless")
    g(root, "-c", "protocol.file.allow=always", "clone", "-q", "--no-checkout",
      "--filter=blob:none", "--no-local", f"file://{src}", str(clone))
    for key in ("remote.origin.promisor", "remote.origin.partialclonefilter",
                "extensions.partialclone"):
        g(clone, "config", "--unset", key, check=False)
    fleet = Path(root, "fleet")
    fleet.mkdir()
    g(root, "init", "-q", "-b", "master", str(fleet))
    body = ("# kama round 1\n\n## Landed changes\n\n"
            f"- `{lc}` work\n\n## Notes\n\nblob {blob}\n").encode()
    commit(fleet, "fleet", 2000, "round-1: report", REL, body)

    packdir = Path(clone, ".git/objects/pack")
    marks = sorted(p.name for p in packdir.glob("*.promisor"))
    missing = subprocess.run(["git", "-C", str(clone), "cat-file", "-e", blob],
                             capture_output=True, env=env()).returncode
    out["observations"]["fixture"] = {
        "promisor_markers": marks,
        "paired_pack": bool(marks) and all(
            packdir.joinpath(m.replace(".promisor", ".pack")).is_file()
            for m in marks),
        "cited_blob_absent_locally": missing != 0,
        "cited_commit_present": subprocess.run(
            ["git", "-C", str(clone), "cat-file", "-e", lc + "^{commit}"],
            capture_output=True, env=env()).returncode == 0,
        "blob": blob, "commit": lc,
        "no_promisor_config": not any(
            "promisor" in line.split("\n")[0]
            for line in g(clone, "config", "--null", "--list").split("\0")
            if line),
    }

    out["observations"]["base_r23"] = run_audit(clone, fleet, root)
    # ablation of the refusal: remove ONLY the marker file(s)
    removed = []
    for m in packdir.glob("*.promisor"):
        m.unlink()
        removed.append(m.name)
    out["observations"]["refusal_ablated"] = run_audit(clone, fleet, root)
    out["observations"]["refusal_ablated"]["removed_markers"] = removed
    out["expectations"] = {
        "base_r23": {"exit": 2, "kinds": None,
                     "note": "r23 blanket refusal: partial clone (promisor pack)"},
        "refusal_ablated": {"exit": 1,
                            "note": "NAIVE repair outcome: unavailable evidence "
                                    "turned into a failed verdict"},
        "contract_truth": {"exit": 2,
                           "note": "required object unavailable -> "
                                   "could-not-evaluate, never clean/failed"},
    }
    ev = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/"
              "round-24/build/out/CaseMarkerLane/evidence-naive-repair.json")
    ev.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n",
                  encoding="utf-8")
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
