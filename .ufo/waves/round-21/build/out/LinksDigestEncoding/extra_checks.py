#!/usr/bin/env python3
"""Extra probes: draft install_links() and gate install_links_sha() on a non-UTF-8 name.
Also records that the draft digest encodings are the only copies of the format
(producer + gate + install-tree-grid duplicate the tree encoding)."""
import importlib.util
import os
import sys
import tempfile
from pathlib import Path

SCRATCH = Path("/tmp/kama-r21-LinksDigestEncoding")
WORK = SCRATCH / "work"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


prod = load("kama_prod", SCRATCH / "lane/tools/kama-llamacpp-live.py")
gate = load("kama_gate", SCRATCH / "lane/tests/llamacpp-live/check-receipt.py")

WORK.mkdir(parents=True, exist_ok=True)
d = Path(tempfile.mkdtemp(prefix="xcase-", dir=WORK))
os.symlink(b"libllama.so.0", os.path.join(os.fsencode(str(d)), b"\xfflib.so"))
results = {}
try:
    prod.install_links(str(d / "llama-server"))
    results["producer_install_links_non_utf8"] = "no exception"
except Exception as exc:  # noqa: BLE001
    results["producer_install_links_non_utf8"] = type(exc).__name__
try:
    gate.install_links_sha({os.fsdecode(b"\xfflib.so"): "libllama.so.0"})
    results["gate_install_links_sha_non_utf8"] = "no exception"
except Exception as exc:  # noqa: BLE001
    results["gate_install_links_sha_non_utf8"] = type(exc).__name__
print(results)
ok = all(v == "UnicodeEncodeError" for v in results.values())
print("PASS: both links encoders crash on a non-UTF-8 name" if ok else "FAIL")
sys.exit(0 if ok else 1)
