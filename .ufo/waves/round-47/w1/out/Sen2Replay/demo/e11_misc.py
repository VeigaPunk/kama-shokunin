#!/usr/bin/env python3
"""E11: extraction size cap, redirect scheme, file modes, and the fetch deadline."""
import importlib.util
import io
import os
import shutil
import stat
import sys
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
REPLAY = os.environ.get("KAMA_REPLAY", os.path.join(LANE, "tools/kama-live-replay.py"))
S = os.environ["S"]
ROOT = os.path.join(S, "e11")

spec = importlib.util.spec_from_file_location("klr", REPLAY)
klr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(klr)


class Zeros(io.RawIOBase):
    """A readable stream of n zero bytes, never materialised in memory."""

    def __init__(self, n):
        self.left = n

    def read(self, size=-1):
        if self.left <= 0:
            return b""
        size = 4096 if size is None or size < 0 else min(size, self.left)
        self.left -= size
        return b"\0" * size


def bomb():
    shutil.rmtree(ROOT, ignore_errors=True)
    os.makedirs(ROOT)
    arc = os.path.join(ROOT, "bomb.tar.gz")
    size = 512 << 20
    ti = tarfile.TarInfo("zeros.bin")
    ti.size = size
    ti.mode = 0o644
    with tarfile.open(arc, "w:gz") as tf:
        tf.addfile(ti, Zeros(size))
    tree = os.path.join(ROOT, "tree")
    os.makedirs(tree)
    t0 = time.monotonic()
    klr.extract(arc, tree)
    dt = time.monotonic() - t0
    out = os.path.join(tree, "zeros.bin")
    print(f"E11a archive={os.path.getsize(arc)} bytes -> extracted={os.path.getsize(out)} "
          f"bytes ratio={os.path.getsize(out)//max(1, os.path.getsize(arc))}x seconds={dt:.2f} "
          f"cap=none")
    os.unlink(out)
    os.unlink(arc)


def redirect_unit():
    seen = {}

    class Recorder:
        def open(self, req, timeout=None):
            seen["url"] = req.full_url
            raise RuntimeError("stop here: reached the redirect target")

    class FP:
        def read(self, *a):
            return b""

        def close(self):
            pass

    def attempt(location):
        h = urllib.request.HTTPRedirectHandler()
        h.parent = Recorder()
        req = urllib.request.Request("https://example.invalid/asset.bin")
        req.timeout = 30
        try:
            h.http_error_302(req, FP(), 302, "Found", {"location": location})
            return f"accepted -> {seen.get('url')}"
        except urllib.error.HTTPError as exc:
            return f"refused: HTTPError {exc}"
        except RuntimeError as exc:
            return f"accepted -> {seen.get('url')} ({exc})"

    for loc in ("http://example.invalid/asset.bin",
                "ftp://example.invalid/asset.bin",
                "file:///etc/passwd"):
        print(f"E11b 302 Location: {loc:34s} -> {attempt(loc)}")
    print("E11b note: fetch() checks only the URL it is given; "
          "urllib rebuilds the request from the Location header "
          "(/usr/lib/python3.14/urllib/request.py:676 allows http, https, ftp).")


def modes():
    d = os.path.join(ROOT, "perm")
    os.makedirs(d, exist_ok=True)
    src = os.path.join(d, "one.gguf")
    with open(src, "wb") as fh:
        fh.write(b"x" * 32)
    dest = os.path.join(d, "download", "one.gguf")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    klr.fetch("file://" + src, dest)
    st = os.stat(dest)
    dirst = os.stat(os.path.dirname(dest))
    print(f"E11c download file mode={oct(stat.S_IMODE(st.st_mode))} "
          f"dir mode={oct(stat.S_IMODE(dirst.st_mode))} "
          f"umask_sensitive={'yes' if stat.S_IMODE(st.st_mode) & 0o004 else 'no'}")


if __name__ == "__main__":
    bomb()
    redirect_unit()
    modes()
