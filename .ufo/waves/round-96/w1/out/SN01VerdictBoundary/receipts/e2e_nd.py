#!/usr/bin/env python3
"""E2E: does the 700 000-tensor file still decide at nd>1? (the C1 headline)"""
import json
import sys
from pathlib import Path

sys.path.insert(0, "/fast/scratch/hyaku/kama-r96/SN01VerdictBoundary")
import boundary as B

FIX = B.FIX

specs = []
for nd in (1, 2, 3, 4):
    p = B.write(f"nd_{nd}_700k.gguf", B.gguf(700_000, nd=nd))
    specs.append((f"700000 tensors nd={nd}", p, "MODEL_UNLOADED"))
    p2 = B.write(f"nd_{nd}_600k.gguf", B.gguf(600_000, nd=nd))
    specs.append((f"600000 tensors nd={nd}", p2, "MODEL_UNLOADED"))
B.e2e(specs)
