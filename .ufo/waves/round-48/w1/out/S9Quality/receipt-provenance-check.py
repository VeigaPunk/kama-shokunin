#!/usr/bin/env python3
"""receipt-provenance-check.py - re-derive a v5 live receipt's record-time provenance binding.

Drafted by round-48 wave seat S9Quality (`.ufo/waves/round-48/w1/out/S9Quality/`) as the
check a KQ74 row can name. It reads receipts only; no network, no lane writes.

Binding checked per receipt (all must hold):
  schema      schema == "kama-llamacpp-live/v5"
  commit      provenance.model.commit is 40 lower-case hex
  url         provenance.model.url contains "/resolve/<commit>/"
  verified    provenance.verified.at == "record"
  archive     verify.archive_sha256 == server.asset_sha256 (non-empty)
  member      verify.member_sha256  == the receipt's top-level server.sha256
  model       verify.model_sha256   == provenance.model.sha256 == the receipt's top-level
              model.sha256

Output: one line per receipt `path schema-v5=1 commit-40hex=1 url-pinned=1
verified-at-record=1 archive-digest=1 member-digest=1 model-digest=1`, then
`receipts=N bound=1|0`. Exit 0 bound, 1 not bound, 2 a receipt cannot be read.

Usage: python3 receipt-provenance-check.py RECEIPT [RECEIPT ...]
"""
from __future__ import annotations

import json
import re
import sys

SCHEMA = "kama-llamacpp-live/v5"


def checks(path):
    with open(path, "rb") as fh:
        d = json.load(fh)
    prov = d.get("provenance") if isinstance(d.get("provenance"), dict) else {}
    model = prov.get("model") if isinstance(prov.get("model"), dict) else {}
    server = prov.get("server") if isinstance(prov.get("server"), dict) else {}
    ver = prov.get("verified") if isinstance(prov.get("verified"), dict) else {}
    server_top = d.get("server") if isinstance(d.get("server"), dict) else {}
    bin_sha = server_top.get("sha256")
    commit = model.get("commit") or ""
    return {
        "schema-v5": d.get("schema") == SCHEMA,
        "commit-40hex": bool(re.fullmatch(r"[0-9a-f]{40}", commit)),
        "url-pinned": bool(commit) and f"/resolve/{commit}/" in (model.get("url") or ""),
        "verified-at-record": ver.get("at") == "record",
        "archive-digest": bool(server.get("asset_sha256")) and ver.get("archive_sha256") == server.get("asset_sha256"),
        "member-digest": bool(bin_sha) and ver.get("member_sha256") == bin_sha,
        "model-digest": bool(model.get("sha256")) and ver.get("model_sha256") == model.get("sha256") == d.get("model", {}).get("sha256"),
    }


def main(argv):
    if not argv:
        print("usage: receipt-provenance-check.py RECEIPT [RECEIPT ...]", file=sys.stderr)
        return 2
    all_ok = True
    for path in argv:
        try:
            got = checks(path)
        except (OSError, ValueError) as exc:
            print(f"{path}: cannot-read {exc}")
            return 2
        print(path, " ".join(f"{k}={int(v)}" for k, v in got.items()))
        all_ok = all_ok and all(got.values())
    print(f"receipts={len(argv)} bound={int(all_ok)}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
