"""Hostile-interpreter-environment probe for the frozen round-27 C1 counter.

This file is only reachable when the counter is started with
PYTHONPATH=/tmp/kama-r27-noreader/pyhack. It shows what the frozen counter
does when the *environment* it is started in lies to it:

  KAMA_CTL_MODE=server   -> subprocess.Popen starts the fake llama-server
                            instead of the sha256-pinned binary (the pin check
                            still hashes the real file on disk, so it passes).
  KAMA_CTL_MODE=full     -> the same, plus hashlib.sha256 is made to hash the
                            pristine pinned snapshot file whenever it is asked
                            to hash the fabricated one, so the source pin on the
                            fabricated snapshot also passes.

Nothing here is part of the lane. It is a control probe, named and documented
as such.
"""
import builtins
import hashlib
import os
import subprocess

MODE = os.environ.get("KAMA_CTL_MODE", "server")
FAKE_SERVER = os.environ.get("KAMA_CTL_FAKE_SERVER", "/tmp/kama-r27-noreader/fake-llama-server.py")
FAKE_FILE = os.environ.get("KAMA_CTL_FAKE_FILE", "")
PINNED_FILE = os.environ.get("KAMA_CTL_PINNED_FILE", "")

# --- 1. substitute the server binary the counter launches -------------------
_real_popen = subprocess.Popen


class _Popen(_real_popen):
    def __init__(self, args, *a, **kw):
        try:
            if (isinstance(args, (list, tuple)) and args
                    and str(args[0]).endswith("llama-server")):
                args = [FAKE_SERVER] + list(args[1:])
        except Exception:
            pass
        super().__init__(args, *a, **kw)


subprocess.Popen = _Popen

# --- 2. optionally lie about the sha256 of the fabricated snapshot file ------
if MODE == "full" and FAKE_FILE and PINNED_FILE:
    _real_open = builtins.open
    _state = {"path": None}

    def _open_hook(file, mode="r", *a, **kw):
        try:
            _state["path"] = os.fspath(file)
        except Exception:
            _state["path"] = None
        return _real_open(file, mode, *a, **kw)

    builtins.open = _open_hook
    _real_sha256 = hashlib.sha256
    _fa = os.path.abspath(FAKE_FILE)
    _pa = os.path.abspath(PINNED_FILE)

    class _Sha:
        def __init__(self, data=b""):
            self._h = _real_sha256(data)

        def update(self, chunk):
            path = _state["path"]
            if path:
                try:
                    if os.path.abspath(str(path)) == _fa:
                        with _real_open(_pa, "rb") as f:
                            chunk = f.read()
                except Exception:
                    pass
            self._h.update(chunk)

        def hexdigest(self):
            return self._h.hexdigest()

        def digest(self):
            return self._h.digest()

        def copy(self):
            return self

    hashlib.sha256 = _Sha
