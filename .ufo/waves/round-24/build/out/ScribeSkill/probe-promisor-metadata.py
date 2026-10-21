#!/usr/bin/env python3
"""Round-24 (ScribeSkill) bounded probe: promisor metadata vs available evidence.

Reads the base (0df800e) auditor and the round-23 grid's fixture helpers.
Builds synthetic offline lane/fleet fixtures only; never touches the real
lane or fleet repository. Question: does promisor *metadata* alone change a
substantive verdict for repositories whose required objects are all local?

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

spec = importlib.util.spec_from_file_location("grid", GRID)
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)


def audit(lane, fleet, rounds="1"):
    p = subprocess.run(
        [sys.executable, str(AUDIT), "--lane-repo", str(lane),
         "--fleet-repo", str(fleet), "--rounds", rounds, "--no-errata",
         "--json"],
        capture_output=True, text=True)
    kinds = []
    try:
        doc = json.loads(p.stdout)
        for res in doc.get("results", []):
            kinds.extend(d["kind"] for d in res.get("defects", []))
    except Exception:
        pass
    return {"exit": p.returncode, "kinds": kinds,
            "stderr": p.stderr.strip()[:400]}


def missing_objects(repo):
    """Objects git cannot resolve locally (promisor-marked missing set)."""
    out = grid.g(repo, "rev-list", "--objects", "--all", "--missing=print")
    return [line for line in out.split("\n") if line.startswith("?")]


def clone_complete(src, dst, tmp, promisor_cfg=False, marker=False):
    """A complete local clone; optionally carry promisor metadata only."""
    grid.g(tmp, "-c", "protocol.file.allow=always", "clone", "-q", "--no-local",
           str(src), str(dst))
    if promisor_cfg:
        grid.g(dst, "config", "remote.origin.promisor", "true")
        grid.g(dst, "config", "remote.origin.partialclonefilter", "blob:none")
        grid.g(dst, "config", "extensions.partialclone", "blob:none")
    if marker:
        packs = sorted(Path(dst, ".git/objects/pack").glob("*.pack"))
        grid.require(bool(packs), "clone wrote no pack file")
        packs[0].with_suffix(".promisor").write_text("")
    return dst


def clone_blobless(src, dst, tmp):
    """A genuinely incomplete (blobless) clone, promisor metadata intact."""
    grid.g(src, "config", "uploadpack.allowFilter", "true")
    grid.g(tmp, "-c", "protocol.file.allow=always", "clone", "-q", "--no-checkout",
           "--filter=blob:none", "--no-local", f"file://{src}", str(dst))
    return dst


def main():
    out = {"git": subprocess.run(["git", "--version"], capture_output=True,
                                 text=True).stdout.strip(),
           "python": sys.version.split()[0], "cases": {}}

    def case(name, lane, fleet, note=None):
        rec = audit(lane, fleet)
        rec["missing_objects"] = missing_objects(lane)
        if note:
            rec["note"] = note
        out["cases"][name] = rec

    with tempfile.TemporaryDirectory(prefix="kama-r24-scribeskill-") as tmp:
        tmp = Path(tmp)

        # A. content-complete, no promisor metadata
        c = tmp / "A1"; c.mkdir()
        lane, fleet, lc = grid.base(c)
        case("A1-clean-full-clone", lane, fleet)

        # B. genuine omission, no promisor metadata
        c = tmp / "A2"; c.mkdir()
        lane2, fleet2, lc2 = grid.base(c)
        grid.commit(lane2, "kama-shokunin", 1500, "round-1: more")
        case("A2-omission-full-clone", lane2, fleet2)

        # C. same content as A1, complete clone + promisor config
        c = tmp / "B1"; c.mkdir()
        lane3, fleet3, _ = grid.base(c)
        c3l = clone_complete(lane3, c / "clone-lane", c, promisor_cfg=True)
        c3f = clone_complete(fleet3, c / "clone-fleet", c, promisor_cfg=True)
        case("B1-clean-promisor-config", c3l, c3f,
             note="complete clone; remote.origin.promisor=true only")

        # D. same content as A2, complete clone + promisor config
        c = tmp / "B2"; c.mkdir()
        lane4, fleet4, _ = grid.base(c)
        grid.commit(lane4, "kama-shokunin", 1500, "round-1: more")
        d4l = clone_complete(lane4, c / "clone-lane", c, promisor_cfg=True)
        d4f = clone_complete(fleet4, c / "clone-fleet", c, promisor_cfg=True)
        case("B2-omission-promisor-config", d4l, d4f,
             note="complete clone; promisor metadata only")

        # E. same content as A1, complete clone + .promisor marker + .pack
        c = tmp / "C1"; c.mkdir()
        lane5, fleet5, _ = grid.base(c)
        e5l = clone_complete(lane5, c / "clone-lane", c, marker=True)
        e5f = clone_complete(fleet5, c / "clone-fleet", c)
        case("C1-clean-promisor-marker", e5l, e5f,
             note="complete clone; paired .promisor marker, no promisor config")

        # F. genuinely missing blob (blobless clone, metadata intact)
        c = tmp / "D1"; c.mkdir()
        lane6, fleet6, lc6 = grid.base(c)
        blob = grid.g(lane6, "rev-parse", f"{lc6}:f")
        f6l = clone_blobless(lane6, c / "clone-lane", c)
        grid.publish(fleet6, grid.report([lc6])
                     + b"\n## Notes\n\nblob " + blob.encode() + b"\n")
        case("D1-missing-blob-promisor", f6l, fleet6,
             note="blobless clone; cited blob absent locally")

        # G. same as F but with promisor config removed (marker only)
        c = tmp / "D2"; c.mkdir()
        lane7, fleet7, lc7 = grid.base(c)
        blob7 = grid.g(lane7, "rev-parse", f"{lc7}:f")
        g7l = clone_blobless(lane7, c / "clone-lane", c)
        for key in ("remote.origin.promisor", "remote.origin.partialclonefilter",
                    "extensions.partialclone"):
            grid.g(g7l, "config", "--unset", key, check=False)
        grid.publish(fleet7, grid.report([lc7])
                     + b"\n## Notes\n\nblob " + blob7.encode() + b"\n")
        case("D2-missing-blob-marker-only", g7l, fleet7,
             note="blobless clone, config stripped; marker only")

    out["frozen_auditor"] = "4fe9339f8fc3a4a4a479d9c938a850da12f1124d"
    out["base_commit"] = "0df800e896f6bce285a81e794ad4ae1d1e6c3a71"
    json.dump(out, sys.stdout, indent=1, sort_keys=True)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
