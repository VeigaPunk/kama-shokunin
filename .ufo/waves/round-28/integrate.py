#!/usr/bin/env python3
"""Round-28 L1 integrator: wave-1 data-seat row drafts -> registry, SKILL.md section, SOURCES rows.

Reads .ufo/waves/round-28/w1/out/DataG*/rows.json (seat drafts), keeps each draft that has
the frozen row shape, orders rows by declaring line, assigns ids F28-01.. and SOURCES ids from
--first-s, and prints (does not write) the three artefacts to --outdir for the L1 to append.
It never edits the counter and never judges a row: the frozen counter does that.
"""
import argparse
import json
import re
from pathlib import Path

LANE = Path(__file__).resolve().parents[3]
URL = ("https://raw.githubusercontent.com/ggml-org/llama.cpp/"
       "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp")
BLOB = ("https://github.com/ggml-org/llama.cpp/blob/"
        "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp")
SNAP_SHA = "1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050"
EXCLUDED = {"n_cache_reuse", "xtc_threshold"}


def canon(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False)


def outcome_text(o):
    if o["kind"] == "reject":
        return f"reject 400, bounds {canon(o['bounds'][0])} to {canon(o['bounds'][1])}"
    return f"200, {o['key']} = {canon(o['value'])}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--first-s", type=int, required=True)
    ap.add_argument("--outdir", required=True)
    a = ap.parse_args()
    drafts, problems = [], []
    for p in sorted((LANE / ".ufo/waves/round-28/w1/out").glob("DataG*/rows.json")):
        doc = json.loads(p.read_text("utf-8"))
        for r in doc.get("rows", []):
            f = r.get("field")
            o = r.get("outcome") or {}
            ok = (isinstance(f, str) and f not in EXCLUDED and r.get("set") and list(r["set"]) == [f]
                  and o.get("kind") in ("reject", "effective") and isinstance(r.get("line"), int)
                  and isinstance(r.get("meaning"), str) and "|" not in r["meaning"]
                  and len(r["meaning"].split()) >= 6)
            if not ok:
                problems.append(f"{p.parent.name}: {f}: malformed draft")
                continue
            drafts.append((r["line"], p.parent.name, r))
    drafts.sort(key=lambda x: x[0])
    reg, skill, src = [], [], []
    for i, (line, seat, r) in enumerate(drafts, 1):
        rid, sid = f"F28-{i:02d}", f"S{a.first_s + i - 1}"
        o = r["outcome"]
        lim = r.get("limits_line")
        reg.append({"id": rid, "field": r["field"], "set": r["set"], "outcome": o,
                    "source": {"row": sid, "file": "server-schema.cpp", "line": line},
                    "seat": seat, "live_by_seat": r.get("live")})
        meaning = " ".join(r["meaning"].split()).replace("|", "/")
        skill.append(f"| {rid} | {r['field']} | {canon(r['set'][r['field']])} | {outcome_text(o)} | {meaning} | {sid} |")
        snap = (LANE / ".ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp").read_text("utf-8").splitlines()
        quote = " ".join(" ".join(snap[line - 1:line + 1]).split()[:25]).replace("|", "/")
        anchor = (f"server-schema.cpp line {line} (declaration `{r['field']}`)"
                  + (f", limits/handler line {lim}" if lim else "")
                  + f" @ 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad; raw sha256 {SNAP_SHA}")
        kind = "rejects an out-of-range value with HTTP 400 and the field's hard bounds" if o["kind"] == "reject" \
            else "accepts the value and stores a different one in generation_settings"
        teaches = (f"request field `{r['field']}` is declared here; on b11755 the server {kind} "
                   f"(live: {outcome_text(o)} for value {canon(r['set'][r['field']])}); quote: {quote}")
        src.append(f"| {sid} | llama.cpp tools/server/server-schema.cpp @ 704366d (b11755) — {BLOB}#L{line} | code | A | "
                   f"how this build declares and bounds request field `{r['field']}` for /completion, at commit 704366d76 only; "
                   f"not other builds, other endpoints' field handling or model quality | {anchor} | {teaches} | mined | 2026-10-23 | on-release | "
                   f"SKILL.md, registry/request-field-outcomes-r28.json, corpus/lessons/round-28.md |")
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "registry.json").write_text(json.dumps({"schema": "kama-r28-request-field-outcomes/v1",
                                                   "build": "llama.cpp b11755 (704366d76)",
                                                   "rows": reg}, indent=1, ensure_ascii=False) + "\n", "utf-8")
    (out / "skill-rows.md").write_text("\n".join(skill) + "\n", "utf-8")
    (out / "sources-rows.md").write_text("\n".join(src) + "\n", "utf-8")
    (out / "problems.txt").write_text("\n".join(problems) + "\n", "utf-8")
    print(f"drafts {len(drafts)} problems {len(problems)}")


if __name__ == "__main__":
    main()
