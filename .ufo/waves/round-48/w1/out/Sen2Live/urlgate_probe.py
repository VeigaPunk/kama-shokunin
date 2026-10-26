#!/usr/bin/env python3
"""URL-gate probe: what the v5 provenance gate does and does not anchor, plus
the v4 counter-example to the C2 docstring's general claim."""
import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
COMMIT = "499bc8821c6b12b4e53c5bffcb21ec206f212d81"
D = os.path.join(HERE, "urlgate")
os.makedirs(D, exist_ok=True)
m = os.path.join(D, "m.gguf")
open(m, "wb").write(b"GGUF")
msha = hashlib.sha256(open(m, "rb").read()).hexdigest()
arc = os.path.join(D, "a.tgz")
BIN = b"#!/bin/sh\ntrue\n"
with tarfile.open(arc, "w:gz") as tf:
    ti = tarfile.TarInfo("rel/llama-server")
    ti.size = len(BIN)
    tf.addfile(ti, io.BytesIO(BIN))
asha = hashlib.sha256(open(arc, "rb").read()).hexdigest()


def run(label, model_url, with_archive=True, server=None):
    out = os.path.join(D, label + ".json")
    argv = [sys.executable, "kama-llamacpp-live.py",
            "--server", server or os.path.join(D, "missing-server"),
            "--model", m, "--model-sha256", msha,
            "--server-asset-url", "https://evil.invalid/a.tgz",
            "--server-asset-sha256", asha, "--server-member", "rel/llama-server",
            "--model-url", model_url, "--out", out]
    if with_archive:
        argv[-2:-2] = ["--server-archive", arc]
    p = subprocess.run(argv, capture_output=True, text=True)
    r = json.load(open(out)) if os.path.exists(out) else {}
    tail = p.stderr.strip().splitlines()[-1][:110] if p.stderr.strip() else ""
    print(f"{label:30s} rc={p.returncode} schema={r.get('schema')} "
          f"setup_error={r.get('setup_error')} stderr={tail}")


run("v5-any-host-pinned-shape", f"https://evil.invalid/x/resolve/{COMMIT}/m.gguf")
run("v5-any-host-unpinned", "https://evil.invalid/m.gguf")
run("v4-any-host-unpinned-no-archive", "https://evil.invalid/m.gguf", with_archive=False)
