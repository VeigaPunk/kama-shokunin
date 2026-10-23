#!/usr/bin/env python3
"""Survey pinned-source string literals against the base corpus.

Reports literals that `git grep -F` at base calls absent but that occur at base
after whitespace normalisation (line-wrapped prose), plus pipe/escape statistics.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
BASE = "1560e4d83f42b04f40336357de6f9637eafa0f4b"
SRC = Path(LANE) / ".ufo/waves/round-26/sources/llama.cpp-704366d"
BASE_TREE = Path(sys.argv[1])

lit_re = re.compile(rb'"((?:[^"\\\n]|\\.){20,}?)"')
base_text = []
for p in sorted([BASE_TREE / "SKILL.md"] + list((BASE_TREE / "corpus").rglob("*"))):
    if p.is_file():
        base_text.append(p.read_bytes().decode("utf-8", "replace"))
joined = "\n".join(base_text)
norm = re.sub(r"\s+", " ", joined)
# markdown soft-wrap and blockquote/list continuation removal
norm2 = re.sub(r"\s*\n\s*(?:>\s*)*", " ", joined)
norm2 = re.sub(r"\s+", " ", norm2)

out = {"wrapped": [], "pipes": [], "escaped_quote": [], "fmt": 0, "total": 0}
for f in sorted(SRC.iterdir()):
    data = f.read_bytes()
    for i, line in enumerate(data.split(b"\n"), 1):
        for m in lit_re.finditer(line):
            lit = m.group(1).decode("utf-8", "replace")
            out["total"] += 1
            # take the longest run without format specifiers or escapes
            for frag in re.split(r"%[-+ #0-9.]*[a-zA-Z]+|\\[nt]", lit):
                frag = frag.strip()
                if len(frag.encode()) < 20:
                    continue
                if "|" in frag:
                    out["pipes"].append([f.name, i, frag])
                if '\\"' in frag:
                    out["escaped_quote"].append([f.name, i, frag])
                if frag in joined:
                    continue
                if " " in frag and (frag in norm or frag in norm2):
                    r = subprocess.run(["git", "-C", LANE, "grep", "-F", "-q", "-e", frag, BASE,
                                        "--", "SKILL.md", "corpus"], capture_output=True)
                    out["wrapped"].append([f.name, i, frag, r.returncode])
json.dump(out, sys.stdout, indent=1)
