#!/usr/bin/env python3
"""KQ146 falsifier (round 91): compare SKILL T01-T07 values with the pinned llama-server --help defaults.

Usage: python3 kq146-help-check.py <llama-server binary>
Prints one KQ146_ROW line per row and `KQ146 rows=7 disagree=<n>`; exit 1 when any row disagrees
or a default cannot be read (so the check fails closed)."""
import hashlib, re, subprocess, sys

ROWS = [("T01", "--port", "9931"), ("T02", "--timeout", "3600"), ("T03", "--sse-ping-interval", "30"),
        ("T04", "--cache-ram", "8192"), ("T05", "--sleep-idle-seconds", "-1"), ("T06", "--models-max", "4"),
        ("T07", "--parallel", "1")]

binary = sys.argv[1]
text = subprocess.run([binary, "--help"], capture_output=True, text=True).stdout
blocks, cur = [], None
for line in text.splitlines():
    if re.match(r"^-", line):
        cur = [line]; blocks.append(cur)
    elif cur is not None:
        cur.append(line)
print(f"# binary_sha256={hashlib.sha256(open(binary, 'rb').read()).hexdigest()}")
bad = 0
for rid, flag, value in ROWS:
    blk = next((" ".join(b) for b in blocks if re.search(re.escape(flag) + r"(\s|,|$)", b[0])), "")
    m = re.search(r"default:\s*(-?\d+)", blk)
    d = m.group(1) if m else "none"
    ok = d == value
    bad += not ok
    print(f"KQ146_ROW {rid} flag={flag} row_value={value} help_default={d} {'agree' if ok else 'DISAGREE'}")
print(f"KQ146 rows={len(ROWS)} disagree={bad}")
sys.exit(1 if bad else 0)
