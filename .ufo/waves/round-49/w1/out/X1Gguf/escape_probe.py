#!/usr/bin/env python3
"""Seat X1Gguf: which gguf_tokens() failures escape the C1 counter's handler.

The counter wraps its own decode in

    except (OSError, EvalError, struct.error) as exc:      # line 447
        detail.append(f"counter model unavailable: {type(exc).__name__}: {exc}")

Anything outside that tuple propagates out of main() and kills the whole
counter with a traceback (exit 1, indistinguishable by exit code from met=False).

  python3 escape_probe.py <counter.py> <case-dir>

The case dir is the one produced by malformed_gguf_tokens.py.
"""
import importlib.util
import json
import struct
import os
import sys

COUNTER, CASES = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("c1counter", COUNTER)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

REQUIRED = ("empty-file", "gguf-v1", "tokens-array-uint32", "random-1MiB",
            "real-prefix-6469B", "real-prefix-6466B", "skip-coverage-types-0-12")
EXTRA = ("random-1MiB-magic-forced", "nkv-2pow62", "nested-array-depth-2000",
         "million-empty-string-tokens")

FILES = {
    "empty-file": "empty.gguf",
    "gguf-v1": "v1.gguf",
    "tokens-array-uint32": "tokens-u32.gguf",
    "random-1MiB": "random1mb.gguf",
    "real-prefix-6469B": "real-keep-6469.gguf",
    "real-prefix-6466B": "real-keep-6466.gguf",
    "skip-coverage-types-0-12": "skip-coverage.gguf",
    "random-1MiB-magic-forced": "random-magic.gguf",
    "nkv-2pow62": "nkv-huge.gguf",
    "nested-array-depth-2000": "nested.gguf",
    "million-empty-string-tokens": "many-empty.gguf",
}


def probe(path):
    try:
        vocab = mod.gguf_tokens(path)
        return {"handled": True, "result": f"decoded {len(vocab)} tokens"}
    except (OSError, mod.EvalError, struct.error) as exc:
        return {"handled": True, "result": f"{type(exc).__name__}: {str(exc)[:90]}"}
    except BaseException as exc:            # what main() would let escape
        return {"handled": False, "escapes": type(exc).__name__, "message": str(exc)[:90]}


rows = []
for name in REQUIRED + EXTRA:
    path = os.path.join(CASES, FILES[name])
    rec = {"case": name, "exists": os.path.isfile(path)}
    if rec["exists"]:
        rec.update(probe(path))
    rec["group"] = "required" if name in REQUIRED else "extra"
    rows.append(rec)
    print(json.dumps(rec))

esc = [r["case"] for r in rows if r.get("handled") is False]
print(json.dumps({"escapes_handler": esc,
                  "required_all_handled": all(r.get("handled") for r in rows if r["group"] == "required")}))
sys.exit(1 if esc else 0)
