#!/usr/bin/env python3
"""census.py - independent census of port / slot-count setter lines in the pinned b12177
archive's common/ + tools/server/, compared with the counter's POP_RE; plus a map of which
archive files each S-row in SOURCES.md mentions (false-provenance check).

Usage: census.py <archive.tar.gz> <SOURCES.md>
"""
import re
import sys
import tarfile
import io
from pathlib import Path

archive, sources_md = Path(sys.argv[1]), Path(sys.argv[2])
ROOTS = ("common/", "tools/server/")
EXTS = (".cpp", ".h", ".hpp")
POP_RE = re.compile(r'\b(port|n_parallel)\s*=[^=]|LLAMA_ARG_PORT|LLAMA_ARG_N_PARALLEL|"--port"|"--parallel"|AIP_HTTP_PORT')

files = {}
with tarfile.open(fileobj=io.BytesIO(archive.read_bytes()), mode="r:gz") as tf:
    for m in tf.getmembers():
        if not m.isfile():
            continue
        rel = m.name.split("/", 1)[1] if "/" in m.name else m.name
        if rel.startswith(ROOTS) and rel.endswith(EXTS):
            files[rel] = tf.extractfile(m).read().decode("utf-8", "replace").split("\n")

pop = {(f, i): l for f, ls in files.items() for i, l in enumerate(ls, 1) if POP_RE.search(l)}
print(f"population={len(pop)}")

# Broad census: anything that could assign a port-ish or slot-ish identifier, or mentions an
# option/env spelling that POP_RE does not carry.
BROAD = [
    ("port-assign-wordchar-prefix", re.compile(r"\w+port\w*\s*=[^=]")),
    ("port-assign-spaced", re.compile(r"\bport\b\s*\+?=[^=]")),
    ("nparallel-assign", re.compile(r"\w*n_parallel\w*\s*[+]?=[^=]")),
    ("parallel-assign", re.compile(r"\bparallel\w*\s*=[^=]")),
    ("dash-port-eq", re.compile(r'"--port[="]|"--parallel[=]?"')),
    ("dash-port-prefix", re.compile(r'"--port[a-z-]+"|"--parallel[a-z-]+"')),
    ("short-p", re.compile(r'"-p"|"-np"')),
    ("AIP", re.compile(r"AIP_HTTP_PORT")),
    ("LLAMA_ARG_OTHER_PORT", re.compile(r"LLAMA_ARG_\w*PORT\w*")),
    ("slot", re.compile(r"\bslots?\s*=[^=]|\bn_slots\b")),
]
print("\n## broad-census hits NOT in POP_RE")
nmiss = 0
for (name, rx) in BROAD:
    hits = [(f, i, l) for f, ls in files.items() for i, l in enumerate(ls, 1)
            if rx.search(l) and (f, i) not in pop]
    for (f, i, l) in hits:
        nmiss += 1
        print(f"MISS[{name}] {f}:{i}: {l.strip()[:160]}")
print(f"miss_total={nmiss}")

print("\n## SOURCES.md rows: archive files each S-row mentions")
SRC_RE = re.compile(r"^ {0,3}\| *(S\d{3,}) *\|")
def cells(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]
for line in sources_md.read_text().split("\n"):
    m = SRC_RE.match(line)
    if not m:
        continue
    cs = cells(line)
    fl = sorted({mm.group(1) for c in cs for mm in re.finditer(r"/b12177/([^ `|]+)", c)})
    if m.group(1) in {"S593", "S596", "S597", "S598", "S599", "S600", "S601", "S602", "S603"}:
        print(f"{m.group(1)} files={fl} cells={len(cs)}")
