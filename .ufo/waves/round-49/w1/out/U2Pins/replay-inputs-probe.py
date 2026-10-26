#!/usr/bin/env python3
"""PROPOSED (not in lane): probe whether a v5 live receipt's replay inputs are still obtainable.
Usage: replay-inputs-probe.py RECEIPT.json   (needs gh + network; 1 gh API call, 2 HEAD requests)
Exit 0 all inputs present and release asset digest == receipt asset_sha256; 1 otherwise (prints why)."""
import json, re, subprocess, sys, urllib.request
r = json.load(open(sys.argv[1])); p = r["provenance"]; s = p["server"]; m = p["model"]
tag = re.search(r"/releases/download/([^/]+)/([^/]+)$", s["asset_url"])
bad = []
out = subprocess.run(["gh", "api", f"repos/ggml-org/llama.cpp/releases/tags/{tag[1]}", "--jq",
    f'{{pre:.prerelease,a:[.assets[]|select(.name=="{tag[2]}")|.digest]}}'], capture_output=True, text=True)
if out.returncode: bad.append("release-tag-gone:" + out.stdout[:80])
else:
    d = json.loads(out.stdout); print("prerelease", d["pre"], "asset_digests", d["a"])
    if ["sha256:" + s["asset_sha256"]] != d["a"]: bad.append("asset-digest-differs-or-missing")
for u in (s["asset_url"], m["url"]):
    try:
        c = urllib.request.urlopen(urllib.request.Request(u, method="HEAD"), timeout=60).status
    except Exception as e: c = repr(e)
    print("HEAD", c, u[:100])
    if c != 200: bad.append("head-not-200:" + u)
print("replayable" if not bad else "NOT replayable: " + ",".join(bad)); sys.exit(1 if bad else 0)
