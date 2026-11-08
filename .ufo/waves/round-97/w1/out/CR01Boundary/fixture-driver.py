#!/usr/bin/env python3
"""CR01Boundary round-97 fixture driver (read-only against the lane).

Builds the C3 boundary fixtures and runs the probe's own ROUTER_PY over them exactly as
router_file_states does:  python3 -c "$ROUTER_PY" body.json files 0

Fixtures (GGUF v3, zero-length names, dim 1, type F32=0, offset 0, no data):
  preamble 24 B; header 24 + 8*nd B; u32 KV 17 B (4 steps); string KV 43 B (5 steps)
"""
import json, os, struct, subprocess, sys, tempfile, time

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
REV = "HEAD"


def extract_router():
    probe = subprocess.run(["git", "-C", LANE, "show", f"{REV}:tools/kama-probe.sh"],
                           capture_output=True, text=True, check=True).stdout
    m = "ROUTER_PY=$(cat <<'PY'\n"
    i = probe.index(m) + len(m)
    j = probe.index("\nPY\n)", i)
    return probe[i:j]


def hdr(name_len, nd, dims, tt, off):
    b = struct.pack("<Q", name_len) + b"\x00" * name_len + struct.pack("<I", nd)
    for d in dims:
        b += struct.pack("<Q", d)
    return b + struct.pack("<I", tt) + struct.pack("<Q", off)


def kv(key, t, value):
    return struct.pack("<Q", len(key)) + key + struct.pack("<I", t) + value


def build(path, T, nd, kvs=()):
    h = hdr(0, nd, [1] * nd, 0, 0)
    with open(path, "wb") as f:
        f.write(b"GGUF" + struct.pack("<I", 3) + struct.pack("<Q", T) + struct.pack("<Q", len(kvs)))
        for k in kvs:
            f.write(k)
        q, r = divmod(T, 4096)
        f.write(h * (4096 * q) + h * r)
    return os.path.getsize(path)


def run(router, path, work):
    body = os.path.join(work, "body.json")
    json.dump({"data": [{"id": "x", "status": {"value": "unloaded",
              "args": [path, "-m", path]}}]}, open(body, "w"))
    t0 = time.time()
    o = subprocess.run([sys.executable, "-c", router, body, "files", "0"],
                       capture_output=True, text=True, timeout=600)
    return o.stdout.strip(), round(time.time() - t0, 1)


KV32 = kv(b"a", 4, struct.pack("<I", 1))
KVARCH = kv(b"general.architecture", 8, struct.pack("<Q", 3) + b"llm")

if __name__ == "__main__":
    work = tempfile.mkdtemp(prefix="cr01-", dir="/fast/scratch/hyaku/kama-r97")
    try:
        router = extract_router()
        cases = [
            ("t833332-nd1-kv0.gguf",      833_332, 1, ()),
            ("t833332-nd1-kv2.gguf",      833_332, 1, (KV32, KV32)),
            ("t833332-nd1-kv1arch.gguf",  833_332, 1, (KVARCH,)),
            ("t555555-nd4-kv0.gguf",      555_555, 4, ()),
            ("t555555-nd4-kv1.gguf",      555_555, 4, (KV32,)),
            ("t700000-nd1-kv0.gguf",      700_000, 1, ()),
        ]
        for name, T, nd, kvs in cases:
            p = os.path.join(work, name)
            size = build(p, T, nd, kvs)
            print(f"{name:28s} T={T} nd={nd} kv={len(kvs)} size={size} -> {run(router, p, work)}")
        # rank-5: declare 600,000 tensors, first header nd=5, pad to pass the 24-byte count check
        p = os.path.join(work, "t600000-nd5.gguf")
        with open(p, "wb") as f:
            f.write(b"GGUF" + struct.pack("<I", 3) + struct.pack("<Q", 600_000) + struct.pack("<Q", 0))
            f.write(hdr(0, 5, [1] * 5, 0, 0))
            f.write(b"\x00" * (14_400_100 - f.tell()))
        print(f"{'t600000-nd5.gguf':28s} size={os.path.getsize(p)} -> {run(router, p, work)}")
    finally:
        import shutil
        shutil.rmtree(work, ignore_errors=True)
