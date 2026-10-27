#!/usr/bin/env python3
"""Run the frozen counter's own observe() against a held server (argv: pid port label)."""
import importlib.util, json, os, sys
LANE = "/fast/scratch/hyaku/kama-r50/X11ModelSwap/lane"
spec = importlib.util.spec_from_file_location("r50c1", os.path.join(LANE, "tools/round50-replay-bind-audit.py"))
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
pid, port, label = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
vocab = c.gguf_tokens("/fast/scratch/hyaku/kama-r50/X11ModelSwap/origbytes.gguf")
probs = []
nonce, mapped = c.observe(pid, port, vocab, "KAMA_R50_CANARY", probs)
print(json.dumps({"label": label, "vocab_tokens": len(vocab), "mapped": mapped,
                  "nonce": nonce, "probs": probs}, indent=1))
