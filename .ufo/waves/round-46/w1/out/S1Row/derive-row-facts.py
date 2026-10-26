#!/usr/bin/env python3
"""derive-row-facts.py - recompute the S486/S487 row cells from the round-46 evidence.

Read-only. Prints one `key=value` per line for the values the two drafts cite:
release identity (release JSON + install.txt) and the live-receipt facts.
Run from anywhere; paths are absolute.
"""
import hashlib
import json
import os

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
LIVE = os.path.join(LANE, ".ufo/waves/round-46/c1/live")
REL = os.path.join(LANE, ".ufo/waves/round-46/c1/release-b11906.json")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


d = json.load(open(REL))
print("release_json_sha256", sha(REL))
print("release_tag", d["tag_name"])
print("release_target_commitish", d["target_commitish"])
print("release_published_at", d["published_at"])
print("release_prerelease", d["prerelease"])
asset = [a for a in d["assets"] if a["name"] == "llama-b11906-bin-ubuntu-x64.tar.gz"][0]
print("asset_name", asset["name"])
print("asset_size", asset["size"])
print("asset_digest", asset["digest"])

txt = open(os.path.join(LIVE, "install.txt")).read().splitlines()
print("install_txt_sha256", sha(os.path.join(LIVE, "install.txt")))
for line in txt:
    if line.startswith(("c9499", "68271", "version:")):
        print("install_line", line)

for i in (1, 2, 3):
    p = os.path.join(LIVE, f"receipt-{i}.json")
    r = json.load(open(p))
    print(f"receipt-{i}_sha256", sha(p))
    print(f"receipt-{i}_schema", r["schema"])
    print(f"receipt-{i}_window", r["started_utc"], r["ended_utc"])
    print(f"receipt-{i}_port", r["port"])
    print(f"receipt-{i}_outcome", r["outcome"])
    print(f"receipt-{i}_checks_passed", sum(1 for c in r["checks"] if c["passed"]), "of", len(r["checks"]))
    print(f"receipt-{i}_server_sha256", r["server"]["sha256"])
    print(f"receipt-{i}_build_info", r["captures"]["props"]["fields"].get("build_info"))
    print(f"receipt-{i}_alias", r["alias"])
    print(f"receipt-{i}_health_body", r["captures"]["health"]["body"])
    print(f"receipt-{i}_metrics_status", r["captures"]["metrics"]["status"])
    print(f"receipt-{i}_loading_bodies", len(r["loading_503_bodies"]), "exact", r["loading_envelope_exact"])
    print(f"receipt-{i}_model_sha256", r["model"]["sha256"])
    print(f"receipt-{i}_tool_sha256", r["tool"]["sha256"])
    print(f"receipt-{i}_probe_sha256", r["probe"]["sha256"])
    print(f"receipt-{i}_teardown", r["teardown"]["returncode"], r["teardown"]["sigkill_sent"],
          r["teardown"]["sigterm_sent"], r["teardown"]["term_wait_ms"])
