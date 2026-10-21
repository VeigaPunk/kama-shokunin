#!/usr/bin/env python3
"""RevengeInstallTreeIntent scan (read-only). (1) Compares lane working-tree bytes with
HEAD bytes for the files the report cites. (2) Lists every receipt under the lane .ufo
tree that carries server.install_tree / install_tree_sha256, with its member count,
pin, and any member whose name is a symlink in the real install directory.
Writes receipt-scan.json beside this file."""
import hashlib
import json
import os
import subprocess

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
INSTALL = "/home/vgpnk/.local/opt/llama-b11755"
HERE = os.path.dirname(os.path.abspath(__file__))
CITED = ["tools/kama-llamacpp-live.py", "tests/llamacpp-live/check-receipt.py",
         "tests/llamacpp-live/install-tree-grid.py", "tests/llamacpp-live/install-links-grid.py",
         "tests/llamacpp-live/controls.py"]


def head_bytes(path):
    r = subprocess.run(["git", "-C", LANE, "show", f"HEAD:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"git show HEAD:{path} rc={r.returncode}")
    return r.stdout


worktree = {}
for p in CITED:
    with open(os.path.join(LANE, p), "rb") as fh:
        data = fh.read()
    worktree[p] = {"worktree_equals_HEAD": data == head_bytes(p),
                   "sha256": hashlib.sha256(data).hexdigest()}
    print(f"{p}: worktree==HEAD {worktree[p]['worktree_equals_HEAD']}")

REAL_LINKS = {n for n in os.listdir(INSTALL) if os.path.islink(os.path.join(INSTALL, n))}
records = []
for root, _dirs, files in os.walk(os.path.join(LANE, ".ufo")):
    for f in files:
        if not f.endswith(".json"):
            continue
        path = os.path.join(root, f)
        try:
            with open(path, encoding="utf-8") as fh:
                doc = json.load(fh)
        except (OSError, ValueError):
            continue
        srv = doc.get("server") if isinstance(doc, dict) else None
        if not isinstance(srv, dict):
            continue
        if "install_tree" not in srv and "install_tree_sha256" not in srv:
            continue
        tree = srv.get("install_tree")
        records.append({
            "path": os.path.relpath(path, LANE),
            "install_tree_sha256": srv.get("install_tree_sha256"),
            "members": len(tree) if isinstance(tree, dict) else None,
            "real_symlink_names_in_tree": (sorted(set(tree) & REAL_LINKS)
                                           if isinstance(tree, dict) else None),
            "has_install_links": "install_links" in srv,
        })

records.sort(key=lambda r: r["path"])
for r in records:
    print(r)
live = [r for r in records if "/live" in r["path"]]
print("live receipts:", len(live),
      "| with 51 members and pin 6c216313:",
      sum(1 for r in live if r["members"] == 51 and str(r["install_tree_sha256"]).startswith("6c216313")),
      "| any symlink name as member:", any(r["real_symlink_names_in_tree"] for r in records))
with open(os.path.join(HERE, "receipt-scan.json"), "w", encoding="utf-8") as fh:
    json.dump({"worktree": worktree, "real_symlink_names": sorted(REAL_LINKS),
               "receipts": records}, fh, indent=2)
print("SCAN_DONE")
