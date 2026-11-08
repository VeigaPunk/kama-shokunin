#!/usr/bin/env python3
"""SN01StepFlips - cross-check my independent fixtures against the counter's own bytes.

Imports the frozen counter's gguf() (read-only) and compares the bytes it would write for
t800k / m520k4 against mine, so the measurement I ran is on the same bytes the frozen cells
use. Also reports which guard fires first for each.
"""
import hashlib
import importlib.util
import struct
import sys
from pathlib import Path

counter_path = Path(sys.argv[1])
fdir = Path(sys.argv[2]).resolve()

spec = importlib.util.spec_from_file_location("r98budget", counter_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

pairs = [("t800k_nd1", mod.gguf(mod.OVER_TENSORS, 1, False)),
         ("t520k_nd4", mod.gguf(mod.OVER4_TENSORS, 1, False, nd=4)),
         ("ok", mod.gguf(1, 32, True))]
for name, cb in pairs:
    mine = (fdir / f"{name}.gguf").read_bytes()
    same = mine == cb
    print(f"XCHECK {name} mine_sha={hashlib.sha256(mine).hexdigest()[:16]} "
          f"counter_sha={hashlib.sha256(cb).hexdigest()[:16]} identical={int(same)} "
          f"bytes={len(mine)}")
    n_t = struct.unpack_from("<Q", mine, 8)[0]
    n_kv = struct.unpack_from("<Q", mine, 16)[0]
    size = len(mine)
    print(f"XCHECK {name} n_tensors={n_t} n_kv={n_kv} size={size} "
          f"size_guard_needs={n_kv * 13 + n_t * 24} size_guard_fires="
          f"{int(n_kv * 13 + n_t * 24 > size)} MAX_TENSORS_fires={int(n_t > 1_000_000)}")
    # what the counter's own oracle says
    print(f"XCHECK {name} counter_fixture_class={mod.fixture_class(fdir / (name + '.gguf'))}")
