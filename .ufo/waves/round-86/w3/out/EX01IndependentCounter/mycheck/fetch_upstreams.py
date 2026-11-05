#!/usr/bin/env python3
"""EX01: fetch the five declared upstream URLs live, store bytes+sha, for later
database comparison against the committed anchor bodies."""
import hashlib, json, os, urllib.request

URLS = {
 "b11755": "https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/README.md",
 "b12111": "https://raw.githubusercontent.com/ggml-org/llama.cpp/b12111/tools/server/README.md",
 "39feb": "https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md",
 "b7200": "https://raw.githubusercontent.com/ggml-org/llama.cpp/b7200/tools/server/README.md",
 "sglang22": "https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx",
 "sglang23": "https://raw.githubusercontent.com/sgl-project/sglang/v0.5.23/docs/docs/basic_usage/native_api.mdx",
 "vllm32": "https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/docs/design/prefix_caching.md",
 "vllm33": "https://raw.githubusercontent.com/vllm-project/vllm/v0.33.0/docs/design/prefix_caching.md",
}
out = {}
for k, u in URLS.items():
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "kama-shokunin-pin-origin/1 (read-only documentary check)"})
        data = urllib.request.urlopen(req, timeout=60).read()
        out[k] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
        open(f"/fast/scratch/hyaku/kama-r86/EX01IndependentCounter/mycheck/up_{k}.bin", "wb").write(data)
    except Exception as e:
        out[k] = {"error": repr(e)}
print(json.dumps(out, indent=1))
