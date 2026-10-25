#!/usr/bin/env python3
"""Probe the lane's actual scanned doc set (tip 3d9bd8d7) for live instances of
the defect classes under test: uppercase-adjacent hex, pure uppercase digests,
split/wrapped hex across lines, non-UTF-8 content or paths, BOMs, extension
case variants. Mirrors tools/digest-ledger.py's doc enumeration exactly.
"""
import re
import subprocess

REPO = "/fast/scratch/kama-r42/clone"
REV = "3d9bd8d72366e281fab291874524130428ee423d"
LEDGER = "registry/digest-ledger.tsv"

ADJ = re.compile(r"[0-9A-F][0-9a-f]{64}|[0-9a-f]{64}[0-9A-F]")
UP = re.compile(r"[0-9A-F]{64}")
SPLIT = re.compile(r"[0-9a-f]{32}\n[0-9a-f]{32}")


def gitb(*args):
    p = subprocess.run(["git", "-C", REPO, *args], capture_output=True, check=True)
    return p.stdout


def lineno(text, pos):
    return text.count("\n", 0, pos) + 1


paths_raw = gitb("ls-tree", "-r", "--name-only", "-z", REV)
nonutf8_paths = []
docs = []
for pb in paths_raw.split(b"\0"):
    if not pb:
        continue
    try:
        p = pb.decode("utf-8")
    except UnicodeDecodeError:
        nonutf8_paths.append(repr(pb))
        continue
    if p.startswith(".ufo/") or p == LEDGER:
        continue
    if p.endswith((".md", ".tsv")):
        docs.append(p)

print(f"docs scanned: {len(docs)}; non-UTF-8 tracked paths: {nonutf8_paths or 'none'}")
total_tokens = 0
tok = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
for p in docs:
    data = gitb("cat-file", "-p", f"{REV}:{p}")
    try:
        data.decode("utf-8")
        utf8_ok = True
    except UnicodeDecodeError:
        utf8_ok = False
    bom = data[:2] in (b"\xff\xfe", b"\xfe\xff") or data[:3] == b"\xef\xbb\xbf"
    text = data.decode("utf-8", "replace")
    total_tokens += len(set(tok.findall(text)))
    for m in ADJ.finditer(text):
        ctx = text[max(0, m.start() - 15):m.end() + 15].replace("\n", "\\n")
        print(f"ADJACENT-UPPER  {p}:{lineno(text, m.start())}: ...{ctx}...")
    for m in UP.finditer(text):
        ctx = text[max(0, m.start() - 15):m.end() + 15].replace("\n", "\\n")
        print(f"UPPER64         {p}:{lineno(text, m.start())}: ...{ctx}...")
    for m in SPLIT.finditer(text):
        ctx = text[max(0, m.start() - 15):m.end() + 15].replace("\n", "\\n")
        print(f"SPLIT-32/32     {p}:{lineno(text, m.start())}: ...{ctx}...")
    if not utf8_ok:
        print(f"NON-UTF8-CONTENT {p}")
    if bom:
        print(f"BOM             {p}")
print(f"distinct tokens over doc set (tool regex): {total_tokens}")
