#!/usr/bin/env python3
"""Read-only trace of the first session-written occurrence of the round-20 report token.

Default: print the transcript lines of the origin session that contain the token and the
surrounding tool calls. --full: scan every omp session file for the exact token and report
how many files contain it and the earliest timestamp (slow: ~10 GB).
Exit 0 iff the origin line is the earliest token line in the full scan (when --full) and the
origin session's first token line is a write of the round-20 report.
"""
import json
import os
import sys

TOKEN = b"0957ce619789d13d894ef21bc863486bcb35b56c"
SESS = "/home/vgpnk/.omp/agent/sessions"
ORIGIN = SESS + "/-Projects-shokunin/2026-10-21T03-31-39-302Z_01a15c83-baa6-76c9-b209-ce1123c6cc22/KamaR18Recovery.jsonl"
REPORT = "/home/vgpnk/Projects/shokunin/.ufo/reports/round-20/kama.md"


def describe(n, obj):
    m = obj.get("message", {}) or {}
    print(f"L{n} ts={obj.get('timestamp')} role={m.get('role')} toolName={m.get('toolName')}")
    cc = m.get("content")
    if isinstance(cc, list):
        for b in cc:
            if isinstance(b, dict) and b.get("type") == "toolCall":
                a = b.get("arguments", {}) or {}
                print(f"   toolCall name={b.get('name')} path={a.get('path')} content_chars={len(a.get('content', '') or '')}")
    d = m.get("details")
    if isinstance(d, dict):
        print(f"   details op={d.get('op')} path={d.get('path')} firstChangedLine={d.get('firstChangedLine')}")


def origin():
    lines = open(ORIGIN, "rb").read().split(b"\n")
    hits = [n for n, raw in enumerate(lines, 1) if TOKEN in raw]
    print("origin session token lines:", hits)
    for n in hits:
        describe(n, json.loads(lines[n - 1]))
    first = json.loads(lines[hits[0] - 1])
    m = first.get("message", {}) or {}
    cc = m.get("content") or []
    is_report_write = any(
        isinstance(b, dict) and b.get("type") == "toolCall" and b.get("name") == "write"
        and (b.get("arguments") or {}).get("path") == REPORT for b in cc
    )
    print("first token line is a write of the round-20 report:", is_report_write)
    return hits[0], first.get("timestamp"), is_report_write


def full_scan():
    files, earliest = 0, None
    for dp, _, fns in os.walk(SESS):
        for f in fns:
            p = os.path.join(dp, f)
            with open(p, "rb") as fh:
                data = fh.read()
            if TOKEN not in data:
                continue
            files += 1
            for n, raw in enumerate(data.split(b"\n"), 1):
                if TOKEN in raw:
                    try:
                        o = json.loads(raw)
                        ts = o.get("timestamp") or (o.get("message") or {}).get("timestamp")
                    except Exception:
                        ts = None
                    if ts and (earliest is None or ts < earliest[0]):
                        earliest = (ts, p, n)
    print("full scan: session files containing exact token =", files)
    print("full scan: earliest token line =", earliest)
    return earliest


if __name__ == "__main__":
    first_line, ts, ok = origin()
    good = ok
    if "--full" in sys.argv:
        earliest = full_scan()
        good = good and earliest is not None and earliest[1] == ORIGIN and earliest[2] == first_line
    print("RESULT", "PASS" if good else "FAIL")
    sys.exit(0 if good else 1)
