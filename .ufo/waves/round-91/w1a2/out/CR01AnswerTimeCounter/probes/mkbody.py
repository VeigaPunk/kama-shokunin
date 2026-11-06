#!/usr/bin/env python3
"""Build held-out bodies (all under the probe's 4 MiB cap) into forg/bodies/."""
import json
import pathlib

OUT = pathlib.Path(__file__).resolve().parent / "bodies"
OUT.mkdir(exist_ok=True)

AL = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def b62(n: int) -> str:
    s = ""
    for _ in range(4):
        s = AL[n % 62] + s
        n //= 62
    return s


def dump(name, doc):
    b = json.dumps(doc, separators=(",", ":")).encode()
    (OUT / name).write_bytes(b)
    print(name, len(b), "under_cap=", len(b) < 4194304)


# good strictly in the middle, then 100 000 more ids (legal answer, under the cap)
ids = [f"x{i:06d}" for i in range(100000)] + ["good"] + [f"x{i:06d}" for i in range(100000, 200000)]
dump("mid-good.json", {"object": "list", "data": [{"id": i} for i in ids]})

# 260 001 ids: one past a 250 000 cap, still under 4 MiB (4-char ids)
ids = [b62(i) for i in range(260000)] + ["good"]
dump("cap260k.json", {"object": "list", "data": [{"id": i} for i in ids]})

# models[] instead of data[] (held-out key), 200 000 ids + good
ids = [f"x{i:06d}" for i in range(200000)] + ["good"]
dump("models200k.json", {"object": "list", "models": [{"id": i} for i in ids]})

# models[].name only
dump("models-name.json", {"object": "list", "models": [{"name": "good"}]})

# literal-grep false positive: rule says /a/goodness -> goodness != good
dump("grep-fp1.json", {"object": "list", "data": [{"id": "/a/goodness"}]})

# literal-grep false positive 2: x/good.gguf.gguf -> good.gguf != good
dump("grep-fp2.json", {"object": "list", "data": [{"id": "x/good.gguf.gguf"}]})
