#!/usr/bin/env python3
"""Build the round-28 count-c2 repair fixtures from the committed receipt.

Usage: make-fixtures.py <committed-receipt.json> <out-dir>

Writes:
  forged-cells.receipt.json   -- receipt cell fields edited, raw hashes and
                                 raw files untouched (K2 per-slot/value/pool,
                                 K4 slot count, L1 request outcomes)
  forged-K3.props.body        -- raw /props body edited (n_ctx 2048 -> 512)
  forged-raw-receipt.json     -- the committed receipt with K3's raw_props
                                 hash rebound to the forged raw bytes
"""
import hashlib
import json
import re
import sys
from pathlib import Path


def main(argv):
    src = Path(argv[1])
    out = Path(argv[2])
    out.mkdir(parents=True, exist_ok=True)
    d = json.loads(src.read_text())
    cells = d["cells"]

    forged = json.loads(json.dumps(d))
    by_id = {c["id"]: c for c in forged["cells"]}

    # K2: per-slot value and KV pool edited, receipt log_lines edited to keep
    # the pre-fix structural checks green.
    k2 = by_id["K2"]
    k2["props_n_ctx"] = 512
    k2["slots_n_ctx"] = [512, 512]
    k2["kv_pool_candidates"] = [1024, 1024]
    k2["kv_pool_n_ctx"] = 1024
    k2["log_lines"] = [
        re.sub(r"(llama_context: n_ctx\s*=\s*)\d+", r"\g<1>1024", ln)
        if "llama_context: n_ctx" in ln else ln
        for ln in k2["log_lines"]]

    # K4: slot count edited (1 -> 2) with a matching per-slot list.
    k4 = by_id["K4"]
    k4["total_slots"] = 2
    k4["slots_n_ctx"] = [1024, 1024]

    # L1: request outcomes edited (both 500 -> 200 with 600 predicted).
    for q in by_id["L1"]["requests"]:
        q["status"] = 200
        q["error"] = None
        q["error_type"] = None
        q["tokens_predicted"] = 600
        q["truncated"] = False

    (out / "forged-cells.receipt.json").write_text(
        json.dumps(forged, indent=1, sort_keys=True) + "\n")

    props_path = Path("raw") / "K3.props.body"
    props_text = (src.parent / props_path).read_text()
    forged_text, hits = re.subn(r'"n_ctx"\s*:\s*2048', '"n_ctx":512',
                                props_text)
    assert hits == 1, f"expected one n_ctx in K3 props, got {hits}"
    (out / "forged-K3.props.body").write_text(forged_text)

    forged_raw = json.loads(json.dumps(d))
    for c in forged_raw["cells"]:
        if c["id"] == "K3":
            c["raw"]["raw_props"] = hashlib.sha256(
                (out / "forged-K3.props.body").read_bytes()).hexdigest()
            print("K3 rebound raw_props",
                  c["raw"]["raw_props"], "receipt cell n_ctx",
                  c["props_n_ctx"])
    (out / "forged-raw-receipt.json").write_text(
        json.dumps(forged_raw, indent=1, sort_keys=True) + "\n")
    print("wrote", out / "forged-cells.receipt.json",
          out / "forged-K3.props.body", out / "forged-raw-receipt.json")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
