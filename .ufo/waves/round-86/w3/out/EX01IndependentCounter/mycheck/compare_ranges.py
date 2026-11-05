#!/usr/bin/env python3
"""EX01: compare each committed anchor's stored body to the live upstream bytes at the
declared line range (references the cached fetches from fetch_upstreams.py)."""
import json, re, subprocess

L = "/home/vgpnk/Projects/shokunin/kama-shokunin"
W = "/fast/scratch/hyaku/kama-r86/EX01IndependentCounter/mycheck"
REV = "bafae7afb41843564ac2468d28beb8e0bb98e8e6"
MAPPING = {
 "b11755": "b11755", "b12111": "b12111", "39febd2adb947b70da35e95f9351b3bf58ad170a": "39feb",
 "b7200": "b7200", "sglang-v0.5.22health": "sglang22", "sglang-v0.5.23health": "sglang23",
 "vllm-v0.32.0prefix": "vllm32", "vllm-v0.33.0prefix": "vllm33",
}
def upkey(rel):
    stem = rel.replace("corpus/anchors/", "")
    for k in MAPPING:
        if stem.startswith(k.replace("sglang-v0.5.22health", "sglang-v0.5.22-health")[:14]):
            pass
    if "llamacpp-b11755" in rel: return "b11755"
    if "llamacpp-b12111-health" in rel: return "b12111"
    if "llamacpp-b12111-router" in rel: return "b12111"
    if "39febd2a" in rel: return "39feb"
    if "llamacpp-b7200" in rel: return "b7200"
    if "sglang-v0.5.22" in rel: return "sglang22"
    if "sglang-v0.5.23" in rel: return "sglang23"
    if "vllm-v0.32.0" in rel: return "vllm32"
    if "vllm-v0.33.0" in rel: return "vllm33"
    raise KeyError(rel)

show = lambda p: subprocess.check_output(["git", "-C", L, "show", f"{REV}:{p}"], text=True,
                                         stderr=subprocess.DEVNULL)
rows = show("registry/pin-recheck-rows.tsv").splitlines()
for line in rows[1:]:
    if not line.strip() or line.startswith("#"): continue
    cells = line.split("\t")
    key = f"{cells[0]}/{cells[1]}"
    for rel in (cells[9], cells[10]):
        text = show(rel)
        first, *body = text.split("\n")
        m = re.match(r"^# url=\S+ sha256=([0-9a-f]{64}) ref=\S+ lines=(\d+)-(\d+)$", first)
        stored = "\n".join(body)
        u = open(f"{W}/up_{upkey(rel)}.bin", "rb").read().decode("utf-8", "surrogateescape")
        upto = u.splitlines()
        start, end = int(m.group(2)), int(m.group(3))
        window = "\n".join(upto[start - 1:end]) + "\n"
        same = window == stored
        print(f"{key} {rel} lines={start}-{end} byte_identical={same}")
