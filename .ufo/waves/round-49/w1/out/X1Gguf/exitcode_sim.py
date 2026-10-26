#!/usr/bin/env python3
"""Seat X1Gguf: exit-code consequence of an exception escaping the C1 handler.

For each adversarial file, run the counter's exact guard

    try:    vocab = gguf_tokens(path)
    except (OSError, EvalError, struct.error) as exc:   # line 447
            detail.append(f"counter model unavailable: {type(exc).__name__}: {exc}")

in a child process and report rc + the last traceback line.  A non-zero rc with
a traceback means main() died instead of recording "counter model unavailable";
the counter's own met=False also exits 1, so the crash is only visible on stderr.

  python3 exitcode_sim.py <counter.py> <case-dir>
"""
import subprocess
import sys

COUNTER, CASES = sys.argv[1], sys.argv[2]
CHILD = """
import importlib.util, struct, sys
spec = importlib.util.spec_from_file_location("c1", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
detail = []
try:
    vocab = m.gguf_tokens(sys.argv[2])
    detail.append(f"counter vocabulary: {len(vocab)} tokens")
except (OSError, m.EvalError, struct.error) as exc:
    detail.append(f"counter model unavailable: {type(exc).__name__}: {exc}")
print("detail:", detail)
"""

for name in ("random-magic.gguf", "nested.gguf"):
    p = subprocess.run([sys.executable, "-c", CHILD, COUNTER, f"{CASES}/{name}"],
                       capture_output=True, text=True)
    tail = [ln for ln in p.stderr.strip().splitlines() if ln.strip()][-1:] or [""]
    print(f"{name}: rc={p.returncode} stdout={p.stdout.strip()!r} stderr_last={tail[0]!r}")
