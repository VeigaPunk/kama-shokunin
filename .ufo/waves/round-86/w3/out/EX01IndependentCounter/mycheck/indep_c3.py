#!/usr/bin/env python3
"""EX01 independent C3 leg - sha256 the stored bodies from committed bytes only."""
import hashlib, json, re, subprocess, sys

L = "/home/vgpnk/Projects/shokunin/kama-shokunin"
REV = "bafae7afb41843564ac2468d28beb8e0bb98e8e6"
show = lambda p: subprocess.check_output(["git", "-C", L, "show", f"{REV}:{p}"], text=True,
                                         stderr=subprocess.DEVNULL)
rows = show("registry/pin-recheck-rows.tsv").splitlines()
HEADER = ("engine","ref","newest","verdict","date","quote_pin","line_pin","quote_newest",
          "line_newest","extract_pin","extract_newest","note")
out = []
for line in rows[1:]:
    if not line.strip() or line.startswith("#"): continue
    cells = line.split("\t")
    row = dict(zip(HEADER, cells))
    rec = {"key": f"{row['engine']}/{row['ref']}"}
    for rel in (row["extract_pin"], row["extract_newest"]):
        text = show(rel)
        first, *body = text.split("\n")
        m = re.match(r"^# url=(\S+) sha256=([0-9a-f]{64}) ref=(\S+) lines=([0-9]+)-([0-9]+)$", first)
        if not m:
            rec[rel] = "malformed-header"; continue
        stored = ("\n".join(body)).encode()
        got = hashlib.sha256(stored).hexdigest()
        rec[rel] = {"url": m.group(1), "lines": f"{m.group(4)}-{m.group(5)}",
                    "sha_ok": got == m.group(2)}
    out.append(rec)
print(json.dumps(out, indent=1))
