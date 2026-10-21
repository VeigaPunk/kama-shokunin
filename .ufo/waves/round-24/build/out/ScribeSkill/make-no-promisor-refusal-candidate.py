#!/usr/bin/env python3
"""Round-24 (ScribeSkill) bounded probe 3: what the base auditor does when
the promisor *metadata* refusal is removed but no availability check is
added.

This builds a scratch candidate copy of the base auditor (never the
production file) with exactly two blocks removed:
  * the `objects/pack` `.promisor`-marker refusal
  * the `extensions.partialclone` / true `remote.*.promisor` config refusal
and runs three synthetic offline fixtures through it:
  T01-like  blobless clone, all cited objects present
  F23-like  blobless clone with the cited blob absent (config stripped)
  F06-like  promisor-marked lane with a fabricated citation

Output: one JSON object on stdout.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPO = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
GRID = REPO / "tests/report-audit/repo-state-grid.py"
AUDIT = REPO / "tools/report-landing-audit.py"
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/ScribeSkill")

spec = importlib.util.spec_from_file_location("grid", GRID)
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)

PACK_BLOCK = """        if rel == "objects/pack" and path.is_dir() and any(
                p.suffix == ".promisor" and p.with_suffix(".pack").exists()
                for p in path.iterdir()):
            raise EvalError(f"{repo}: partial clone (promisor pack)")
"""
CONFIG_BLOCK = """    listing = git(repo, "config", "--null", "--list",
                  errors="surrogateescape")
    for entry in filter(None, listing.split("\\0")):
        key, _, value = entry.partition("\\n")
        if key == "extensions.partialclone" or (
                re.fullmatch(r"remote\\..+\\.promisor", key)
                and git_bool(value)):
            raise EvalError(f"{repo}: partial clone ({key})")
"""


def make_candidate():
    text = AUDIT.read_text()
    for block in (PACK_BLOCK, CONFIG_BLOCK):
        if block not in text:
            raise SystemExit(f"block not found:\n{block}")
        text = text.replace(block, "")
    dest = SCRATCH / "candidate-no-promisor-refusal.py"
    dest.write_text(text)
    return dest


def audit(script, lane, fleet):
    p = subprocess.run(
        [sys.executable, str(script), "--lane-repo", str(lane),
         "--fleet-repo", str(fleet), "--rounds", "1", "--no-errata", "--json"],
        capture_output=True, text=True)
    kinds = []
    try:
        doc = json.loads(p.stdout)
        for res in doc.get("results", []):
            kinds.extend(d["kind"] for d in res.get("defects", []))
    except Exception:
        pass
    return {"exit": p.returncode, "kinds": sorted(set(kinds)),
            "stderr": p.stderr.strip()[:300]}


def main():
    cand = make_candidate()
    out = {"candidate": str(cand), "base": str(AUDIT), "cases": {}}
    with tempfile.TemporaryDirectory(prefix="kama-r24-scribeskill3-") as tmp:
        tmp = Path(tmp)

        # T01-like: blobless clone, the cited lane commit is present
        c = tmp / "T01"; c.mkdir()
        lane, fleet, lc = grid.base(c)
        grid.g(lane, "config", "uploadpack.allowFilter", "true")
        clone = c / "blobless"
        grid.g(c, "-c", "protocol.file.allow=always", "clone", "-q",
               "--no-checkout", "--filter=blob:none", "--no-local",
               f"file://{lane}", str(clone))
        out["cases"]["T01-like-blobless"] = {
            "base": audit(AUDIT, clone, fleet),
            "candidate": audit(cand, clone, fleet)}

        # F23-like: the cited blob is absent locally (config stripped)
        c = tmp / "F23"; c.mkdir()
        lane2, fleet2, lc2 = grid.base(c)
        blob = grid.g(lane2, "rev-parse", f"{lc2}:f")
        grid.g(lane2, "config", "uploadpack.allowFilter", "true")
        clone2 = c / "blobless2"
        grid.g(c, "-c", "protocol.file.allow=always", "clone", "-q",
               "--no-checkout", "--filter=blob:none", "--no-local",
               f"file://{lane2}", str(clone2))
        for key in ("remote.origin.promisor", "remote.origin.partialclonefilter",
                    "extensions.partialclone"):
            grid.g(clone2, "config", "--unset", key, check=False)
        grid.publish(fleet2, grid.report([lc2])
                     + b"\n## Notes\n\nblob " + blob.encode() + b"\n")
        out["cases"]["F23-like-missing-cited-blob"] = {
            "base": audit(AUDIT, clone2, fleet2),
            "candidate": audit(cand, clone2, fleet2)}

        # F06-like: promisor-marked lane, fabricated citation
        c = tmp / "F06"; c.mkdir()
        lane3, fleet3, lc3 = grid.base(c)
        fake = "abcdefabcdefabcdefabcdefabcdefabcdefabcd"
        grid.publish(fleet3, grid.report([lc3, fake]))
        marker = c / "lazy-fetch-ran"
        for k, v in (("extensions.partialClone", "origin"),
                     ("remote.origin.url", "ssh://example.invalid/x.git"),
                     ("remote.origin.promisor", "true"),
                     ("core.sshCommand", f"touch {marker}; false")):
            grid.g(lane3, "config", k, v)
        out["cases"]["F06-like-fabricated-citation"] = {
            "base": audit(AUDIT, lane3, fleet3),
            "candidate": audit(cand, lane3, fleet3),
            "transport_program_ran": marker.exists()}
    json.dump(out, sys.stdout, indent=1, sort_keys=True)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
