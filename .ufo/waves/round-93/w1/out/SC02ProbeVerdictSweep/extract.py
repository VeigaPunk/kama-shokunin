#!/usr/bin/env python3
"""Extract ROUTER_PY from a probe file; build GGUF fixtures; time a parse."""
import struct, subprocess, sys, time
from pathlib import Path

def probe_router_py(text: str) -> str:
    start = text.find("ROUTER_PY=$(cat <<'PY'\n")
    if start < 0:
        raise SystemExit("ROUTER_PY not found")
    start += len("ROUTER_PY=$(cat <<'PY'\n")
    end = text.find("\nPY\n)", start)
    if end < 0:
        raise SystemExit("ROUTER_PY end not found")
    return text[start:end]

def gguf(n_tensors: int, elems: int, with_data: bool) -> bytes:
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", n_tensors, 0)]
    off = 0
    for i in range(n_tensors):
        name = b"t%07d" % i
        out.append(struct.pack("<Q", len(name)) + name + struct.pack("<IQIQ", 1, elems, 0, off))
        off += (elems * 4 + 31) // 32 * 32
    head = b"".join(out)
    pad = (len(head) + 31) // 32 * 32 - len(head)
    return head + b"\0" * pad + (b"\0" * off if with_data else b"\0" * 16)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "extract":
        text = Path(sys.argv[2]).read_text()
        Path(sys.argv[3]).write_text(probe_router_py(text))
        print("wrote", sys.argv[3])
    elif cmd == "fixture":
        # fixture.py <out.gguf> <n_tensors> <elems> <with_data 0|1>
        out = Path(sys.argv[2]); n = int(sys.argv[3]); e = int(sys.argv[4]); d = sys.argv[5] == "1"
        out.write_bytes(gguf(n, e, d))
        print("wrote", out, out.stat().st_size)
    elif cmd == "time":
        # time.py <router_py> <body.json> <idx...>
        rp = Path(sys.argv[2]).read_text()
        body = sys.argv[3]
        idx = sys.argv[4:]
        t0 = time.monotonic()
        p = subprocess.run([sys.executable, "-c", rp, body, "files", *idx], capture_output=True)
        dt = time.monotonic() - t0
        print(f"rc={p.returncode} dt={dt:.2f}s out={p.stdout.decode()[:200]!r} err={p.stderr.decode()[:200]!r}")
