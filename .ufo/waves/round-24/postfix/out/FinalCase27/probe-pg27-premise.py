#!/usr/bin/env python3
"""PG27 premise probe (observation only, no verdict).

Reads the KEPT fixture of PG27-cross-repo-found-plain (grid --keep) and
records, for both audited stores: promisor marks, the cited tokens, the
bare/peeled presence of the fleet-only token in each store, and the report
bytes. Every git call carries --no-lazy-fetch --no-replace-objects, so no
origin is contacted and no object is acquired.
"""
import json
import pathlib
import subprocess
import sys

GIT = ["git", "--no-lazy-fetch", "--no-replace-objects"]


def g(repo, *args, stdin=None):
    p = subprocess.run(GIT + ["-C", str(repo)] + list(args),
                       input=stdin, capture_output=True, text=True)
    return {"rc": p.returncode, "out": p.stdout.strip(), "err": p.stderr.strip()}


def main(root):
    root = pathlib.Path(root)
    out = {"fixture_root": str(root), "stores": {}}
    lane, fleet = root / "lane", root / "fleet"
    for name, repo in (("lane", lane), ("fleet", fleet)):
        st = {"exists": repo.is_dir()}
        st["promisor_config"] = g(repo, "config", "--get", "remote.origin.promisor")
        st["partialclone_config"] = g(repo, "config", "--get", "extensions.partialclone")
        st["origin_url"] = g(repo, "config", "--get", "remote.origin.url")
        st["refs"] = g(repo, "for-each-ref", "--format=%(refname)")
        st["log"] = g(repo, "log", "--all", "--format=%H %s")
        st["objects"] = sorted(g(repo, "cat-file", "--batch-all-objects",
                                 "--batch-check=%(objectname)")["out"].split())
        out["stores"][name] = st
    fleet_log = out["stores"]["fleet"]["log"]["out"].splitlines()
    init = [l.split()[0] for l in fleet_log if l.endswith("fleet: init")]
    tokens = {"fleet_only_commit": init[0] if init else None}
    lane_log = out["stores"]["lane"]["log"]["out"].splitlines()
    tokens["lane_commit"] = lane_log[0].split()[0] if lane_log else None
    out["tokens"] = tokens
    presence = {}
    for tok_name, tok in tokens.items():
        if not tok:
            continue
        for name, repo in (("lane", lane), ("fleet", fleet)):
            presence[f"{tok_name}@{name}"] = {
                "bare": g(repo, "cat-file", "--batch-check", stdin=tok + "\n"),
                "peeled": g(repo, "cat-file", "--batch-check", stdin=tok + "^{commit}\n"),
            }
    out["presence"] = presence
    out["report"] = g(fleet, "show", "HEAD:.ufo/reports/round-1/kama.md")
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1])
