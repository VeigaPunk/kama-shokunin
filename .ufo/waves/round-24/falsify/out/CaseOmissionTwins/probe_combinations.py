#!/usr/bin/env python3
"""Extra cross-combination probe for the OmissionTwins family (NOT a manifest
row): lane and fleet promisor metadata combined in every way, plus the
marker x config combination.  The amended policy says promisor metadata alone
never changes a verdict, so every combination must yield the identical
substantive verdict as the plain twin.

Offline, local plumbing only.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_omission import build_family, g, inventory  # noqa: E402

AUDITOR = Path(sys.argv[1]).resolve()
ROOT = Path(sys.argv[2]).resolve()


def env():
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    return e


def mark_config(repo, url):
    g(repo, "config", "remote.origin.promisor", "true")
    g(repo, "config", "extensions.partialclone", "origin")
    g(repo, "config", "remote.origin.url", str(url))


def mark_marker(repo):
    g(repo, "repack", "-a", "-d", "-q")
    gd = Path(g(repo, "rev-parse", "--absolute-git-dir").strip())
    for pack in sorted((gd / "objects" / "pack").glob("*.pack")):
        pack.with_suffix(".promisor").write_bytes(b"")


def audit(lane, fleet):
    p = subprocess.run([sys.executable, str(AUDITOR), "--lane-repo", str(lane),
                        "--fleet-repo", str(fleet), "--rounds", "1", "--json",
                        "--no-errata"], capture_output=True, env=env(),
                       cwd=str(ROOT))
    return p.returncode, p.stdout.decode(errors="replace"), \
        p.stderr.decode(errors="replace")


def norm(out, lane, fleet):
    return out.replace(str(fleet), "<fleet>").replace(str(lane), "<lane>")


def combo(name, lane_mark, fleet_mark):
    root = ROOT / name
    fx = build_family(root, "base")
    lane, fleet = fx["lane"], fx["fleet"]
    absent = root / "absent-remote.git"
    if lane_mark == "config":
        mark_config(lane, absent)
    elif lane_mark == "marker":
        mark_marker(lane)
    if fleet_mark == "config":
        mark_config(fleet, absent)
    elif fleet_mark == "marker":
        mark_marker(fleet)
    before = {"lane": inventory(lane), "fleet": inventory(fleet)}
    code, out, err = audit(lane, fleet)
    after = {"lane": inventory(lane), "fleet": inventory(fleet)}
    doc = None
    try:
        doc = json.loads(out)
    except ValueError:
        pass
    defects = []
    if doc:
        for res in doc.get("results", []):
            for d in res.get("defects", []):
                defects.append((d.get("kind"), d.get("token")))
    return {"combo": name, "lane_mark": lane_mark, "fleet_mark": fleet_mark,
            "exit": code, "stderr": err.strip(),
            "defects": sorted(defects),
            "status": (doc or {}).get("summary", {}).get("status"),
            "objects_acquired": {k: sorted(after[k] - before[k]) for k in after},
            "norm_out": norm(out, lane, fleet)}


def main():
    out = []
    for name, lm, fm in (("plain", None, None),
                         ("lane_config", "config", None),
                         ("fleet_config", None, "config"),
                         ("lane_marker", "marker", None),
                         ("fleet_marker", None, "marker"),
                         ("both_config", "config", "config"),
                         ("both_marker", "marker", "marker"),
                         ("lane_config_fleet_marker", "config", "marker"),
                         ("lane_marker_fleet_config", "marker", "config")):
        out.append(combo(name, lm, fm))
    base = out[0]["norm_out"]
    for r in out:
        r["document_equal_to_plain"] = (r["norm_out"] == base)
        r.pop("norm_out")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
