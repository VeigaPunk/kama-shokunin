#!/usr/bin/env python3
"""KamaR21.SrcReproducibleBuildsArchive-6 - probe: install_links() on a non-UTF-8 link target.

Usage: python3 symlink_encoding_probe.py <path to tools/kama-llamacpp-live.py>
Imports the given module (its __main__ guard keeps import side-effect free) and calls
install_links() on two throwaway temp trees (nothing under ~/.local/opt is touched):
  control - soname symlink with an ASCII target;
  probe   - the same symlink whose target bytes include 0xff (not valid UTF-8).
Exit 0 when the probe ran to completion (the observed outcome is printed either way).
"""
import importlib.util
import os
import pathlib
import sys
import tempfile

mod_path = pathlib.Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("kama_live_probe", mod_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with tempfile.TemporaryDirectory() as d:
    server = os.path.join(d, "llama-server")
    open(server, "w").close()
    os.symlink("libllama.so.0.7.0", os.path.join(d, "libllama.so.0"))
    links, sha = mod.install_links(server)
    print("control: links =", links, "| install_links_sha256 =", sha)

with tempfile.TemporaryDirectory() as d:
    server = os.path.join(d, "llama-server")
    open(server, "w").close()
    os.symlink(b"lib\xffllama.so.0.7.0", os.path.join(d, "libllama.so.0"))
    try:
        links, sha = mod.install_links(server)
        print("probe: returned links =", ascii(links), "| sha =", sha)
    except Exception as exc:  # observed outcome, reported verbatim
        print("probe: raised", type(exc).__name__, "-", exc)
sys.exit(0)
