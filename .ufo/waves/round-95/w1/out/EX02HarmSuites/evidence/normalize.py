#!/usr/bin/env python3
"""Normalize harm-suite receipts so two revisions can be diffed on behaviour only.

Strips: 64-hex digests, sha256=/probe_sha256=/base_sha256= values, seconds=/time=/WALL=/
elapsed=/load1=/dur= values, absolute scratch or repo paths, and ISO timestamps.
Keeps: every verdict, reason, ok=, cell id, exit code, counts.
"""
import re
import sys

STRICT = "--strict" in sys.argv

PATTERNS = [
    (re.compile(r"\b[0-9a-f]{64}\b"), "<DIGEST>"),
    (re.compile(r"(sha256|probe_sha256|base_sha256|server_sha256)=[0-9a-f]+"), r"\1=<DIGEST>"),
    (re.compile(r"\b(seconds|time|WALL|elapsed|dur|wall|t)=[0-9]+(\.[0-9]+)?"), r"\1=<T>"),
    (re.compile(r"\b(load1|load1_nat|load5|load15|load)=[0-9]+(\.[0-9]+)?"), r"\1=<LOAD>"),
    (re.compile(r"\b[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z?\b"), "<TS>"),
    (re.compile(r"/fast/scratch/hyaku/kama-r95/[A-Za-z0-9_.-]+"), "<SCRATCH>"),
    (re.compile(r"/home/vgpnk/Projects/shokunin/kama-shokunin"), "<LANE>"),
    (re.compile(r"/[0-9]+(?:\.[0-9]+)?s\b"), "/<T>s"),
]+ ([
    (re.compile(r'"port": [0-9]+'), '"port": <PORT>'),
    (re.compile(r"\brev=[0-9a-f]+"), "rev=<REV>"),
    (re.compile(r"127\.0\.0\.1:[0-9]+"), "127.0.0.1:<PORT>"),
    (re.compile(r"after [0-9]+ ms"), "after <T> ms"),
    (re.compile(r"\bsent=[0-9]+"), "sent=<BYTES>"),
] if STRICT else []) + [
    (re.compile(r'"probe": "[^"]*"'), '"probe": "<PATH>"'),
    (re.compile(r'"probe_sha256": "[^"]*"'), '"probe_sha256": "<DIGEST>"'),
]


for path in [a for a in sys.argv[1:] if a != "--strict"]:
    with open(path, "r", errors="replace") as f:
        text = f.read()
    for rx, repl in PATTERNS:
        text = rx.sub(repl, text)
    sys.stdout.write(text)
