#!/usr/bin/env python3
"""m12-race.py <probe-file> <slow-invalid> <big-valid> - mid-invocation rewrite probe.

One ROUTER_PY `files` invocation, three candidates:
  0: -m slow (invalid; first look-up caches the state under its identity)
  1: -m big  (valid, ~a few seconds of parse: the rewrite window)
  2: -m slow-link (hard link to the same inode; the base key includes ctime, a key without
     ctime serves the stale cached state)
A background writer rewrites `slow` in place to the same byte length with mtime restored while
candidate 1 is being parsed, so only ctime changes. Prints the three states.
"""
import json
import os
import struct
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path


def valid_padded(n: int) -> bytes:
    name = b"t0000000"
    head = (b"GGUF" + struct.pack("<I", 3) + struct.pack("<QQ", 1, 0)
            + struct.pack("<Q", len(name)) + name + struct.pack("<IQIQ", 1, 32, 0, 0))
    pad = (len(head) + 31) // 32 * 32 - len(head)
    body = head + b"\0" * pad + b"\0" * (32 * 4)
    return body + b"\0" * (n - len(body))


def main() -> int:
    probe_path, slow, big = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    link = slow.with_name(slow.stem + "-link.gguf")
    if link.exists():
        link.unlink()
    os.link(slow, link)
    orig = slow.read_bytes()
    st = os.stat(slow)
    text = Path(probe_path).read_text()
    s = text.find("ROUTER_PY=$(cat <<'PY'\n") + len("ROUTER_PY=$(cat <<'PY'\n")
    rp = text[s:text.find("\nPY\n)", s)]

    def rewrite():
        time.sleep(6.0)
        slow.write_bytes(valid_padded(len(orig)))
        os.utime(slow, ns=(st.st_atime_ns, st.st_mtime_ns))
        print(f"REWRITE at {time.monotonic() - t0:.2f}s size={slow.stat().st_size}", flush=True)

    with tempfile.TemporaryDirectory() as td:
        body = Path(td) / "body.json"
        data = [{"id": "good", "status": {"value": "unloaded", "args": [str(big), "-m", str(p)]}}
                for p in (slow, big, link)]
        body.write_text(json.dumps({"object": "list", "data": data}, separators=(",", ":")))
        t0 = time.monotonic()
        th = threading.Thread(target=rewrite, daemon=True)
        th.start()
        p = subprocess.run([sys.executable, "-c", rp, str(body), "files", "0", "1", "2"],
                           capture_output=True, timeout=600)
        dt = time.monotonic() - t0
    th.join(timeout=30)
    slow.write_bytes(orig)
    os.utime(slow, ns=(st.st_atime_ns, st.st_mtime_ns))
    print(p.stdout.decode().rstrip())
    print(f"WALL {dt:.2f}s rc={p.returncode} restored_size={slow.stat().st_size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
