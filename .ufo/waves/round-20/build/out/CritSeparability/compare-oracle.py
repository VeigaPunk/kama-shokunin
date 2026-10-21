#!/usr/bin/env python3
"""Compare one gguf-identity JSON result with a retained gguf-py oracle."""
import json
import sys

model = json.load(open(sys.argv[1], encoding="utf-8"))
oracle = json.load(open(sys.argv[2], encoding="utf-8"))
metadata = oracle["metadata"]
keys = model["keys"]
arch = keys["general.architecture"]
checks = [
    model["version"] == oracle["version"],
    model["tensor_count"] == oracle["tensor_count"],
    model["kv_count"] == oracle["kv_count"],
    model["sha256"] == oracle["file"]["sha256"],
]
checks.extend(keys[key] == metadata.get(key) for key in (
    "general.architecture", "general.name", "general.file_type",
    "general.alignment", "tokenizer.ggml.model"))
checks.extend(keys[arch + "." + key] == metadata.get(arch + "." + key)
              for key in ("context_length", "block_count", "embedding_length"))
print(f"checks={len(checks)} passed={sum(checks)}/{len(checks)}")
raise SystemExit(0 if all(checks) else 1)
