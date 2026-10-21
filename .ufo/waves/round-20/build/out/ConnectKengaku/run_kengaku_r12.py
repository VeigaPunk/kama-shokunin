#!/usr/bin/env python3
"""ConnectKengaku (kama round 20): run kengaku's committed r12 GGUF header-parse
script (corpus/evidence/round12-fleet/r12-endpoint-freshness.md, ```python block
after line 355) against another GGUF, changing only the PATH constant. Read-only.
Usage: python3 run_kengaku_r12.py KENGAKU_REPO REV MODEL"""
import hashlib, subprocess, sys

repo, rev, model = sys.argv[1:4]
md = subprocess.run(["git", "-C", repo, "show", f"{rev}:corpus/evidence/round12-fleet/r12-endpoint-freshness.md"],
                    check=True, capture_output=True, text=True).stdout.splitlines()
start = md.index("```python", 350) + 1          # first fenced python block at/after line 351
end = md.index("```", start)
block = "\n".join(md[start:end]) + "\n"
print(f"block lines {start + 1}-{end} (1-based), sha256 {hashlib.sha256(block.encode()).hexdigest()}")
path_line = [l for l in block.splitlines() if l.startswith("PATH = ")]
assert len(path_line) == 1, path_line
block = block.replace(path_line[0], f"PATH = {model!r}")
exec(compile(block, "kengaku-r12-block", "exec"), {"__name__": "kengaku_r12"})
