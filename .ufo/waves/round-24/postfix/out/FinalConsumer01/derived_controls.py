#!/usr/bin/env python3
"""FinalConsumer01 derived controls on the SAME fleet-only-blob fixture.

C1 (citation removed): the same fixture, the draft cites only the valid
    lane work commit -> the after side must be a clean exit 0, proving the
    landed-unresolved finding is caused by the fleet-only blob citation
    and not by the presence of the valid commit.
C2 (blob in BOTH stores): the same fixture with the under-test blob copied
    into the lane object store as well (unreachable there) -> the after side
    must STILL report landed-unresolved (exit 1), proving that generic
    store-presence does not make a wrong-type (blob) citation acceptable.

Neither control rewrites the driver fixture; both work on copies.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer01")
FIXTURE = BASE / "fixture"
AFTER = BASE / "clone/tools/report-landing-audit.py"
BEFORE = BASE / "out/before-report-landing-audit.py"

GITENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
          "GIT_AUTHOR_NAME": "k", "GIT_COMMITTER_NAME": "k",
          "GIT_AUTHOR_EMAIL": "a@x", "GIT_COMMITTER_EMAIL": "a@x",
          "PATH": "/usr/bin:/bin"}


def g(repo, *args):
    p = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch", "-C",
                        str(repo), *args], capture_output=True, env=GITENV,
                       timeout=30)
    return p.returncode, p.stdout.decode("utf-8", "replace").strip(), \
        p.stderr.decode("utf-8", "replace").strip()


def run(tool, lane, fleet, draft):
    cmd = [sys.executable, str(tool), "--lane-repo", str(lane),
           "--fleet-repo", str(fleet), "--branch", "master", "--rounds", "1",
           "--report", f"1={draft}", "--json", "--no-errata"]
    p = subprocess.run(cmd, capture_output=True, timeout=120,
                       env={**os.environ, "TMPDIR": str(BASE / "tmp")})
    kinds, errata_invalid = [], None
    if p.returncode in (0, 1):
        try:
            doc = json.loads(p.stdout.decode("utf-8", "replace"))
            kinds = sorted({d["kind"] for res in doc["results"]
                            for d in res["defects"]})
            errata_invalid = doc["summary"].get("errata_invalid")
        except Exception:
            pass
    return {"cmd": cmd, "exit": p.returncode, "kinds": kinds,
            "errata_invalid": errata_invalid,
            "stderr": p.stderr.decode("utf-8", "replace")[:400],
            "tool_sha256": hashlib.sha256(Path(tool).read_bytes()).hexdigest()}


def main():
    out = {}
    draft_text = (FIXTURE / "draft.md").read_text(encoding="utf-8")
    lines = draft_text.splitlines()
    valid = lines[1].split("`")[1]
    blob = lines[2].split("`")[1]

    # --- C1: only the valid lane commit is cited
    c1 = BASE / "fixture-c1"
    if c1.exists():
        shutil.rmtree(c1)
    shutil.copytree(FIXTURE, c1)
    d1 = c1 / "draft.md"
    d1.write_text("## Landed changes\n- `" + valid + "` work\n", encoding="utf-8")
    out["C1_citation_removed"] = {
        "draft": d1.read_text(encoding="utf-8"),
        "after": run(AFTER, c1 / "lane", c1 / "fleet", d1),
        "before": run(BEFORE, c1 / "lane", c1 / "fleet", d1)}

    # --- C2: the under-test blob is ALSO in the lane object store
    c2 = BASE / "fixture-c2"
    if c2.exists():
        shutil.rmtree(c2)
    shutil.copytree(FIXTURE, c2)
    lane, fleet = c2 / "lane", c2 / "fleet"
    rc, gitdir, err = g(lane, "rev-parse", "--git-path", "objects")
    objs = (lane / gitdir.strip())
    src = (fleet / (g(fleet, "rev-parse", "--git-path", "objects")[1].strip())
           / blob[:2] / blob[2:])
    dst = objs / blob[:2] / blob[2:]
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    rc, outt, errt = g(lane, "cat-file", "-t", blob)
    out["C2_blob_in_both_stores"] = {
        "copied_from": str(src), "copied_to": str(dst),
        "lane_cat_file_t": {"rc": rc, "stdout": outt, "stderr": errt},
        "after": run(AFTER, lane, fleet, c2 / "draft.md"),
        "before": run(BEFORE, lane, fleet, c2 / "draft.md")}

    (BASE / "out/derived-controls.json").write_text(
        json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
