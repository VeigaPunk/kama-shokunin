#!/usr/bin/env python3
"""Scratch probe (outside the lane). (1) AST-compare install_tree/sha256_file between
the frozen rev and the pinned rev. (2) Show producer identity depends on whether
server_real is realpath()-resolved (producer main does realpath; grid passes unresolved)."""
import ast
import os
import subprocess
import types
from pathlib import Path

LANE = "/tmp/kama-r21-LinksGridReview/lane"
PROD = "tools/kama-llamacpp-live.py"
FROZEN = "7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d"
PINNED = "a29bb84abbb8b4d328f5970a89e448330a3a42ac"


def src(rev):
    return subprocess.run(["git", "-C", LANE, "show", f"{rev}:{PROD}"],
                          capture_output=True, check=True).stdout.decode("utf-8")


def fn_dump(rev, name):
    for node in ast.parse(src(rev)).body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.dump(node)
    return None


for name in ("sha256_file", "install_tree"):
    a, b = fn_dump(FROZEN, name), fn_dump(PINNED, name)
    print(f"{name}: frozen_present={a is not None} pinned_present={b is not None} ast_equal={a == b}")
print("install_links: frozen_present=%s pinned_present=%s" % (
    fn_dump(FROZEN, "install_links") is not None, fn_dump(PINNED, "install_links") is not None))

# (2) realpath divergence, using the pinned producer exactly as the grid loads it
mod = types.ModuleType("prod")
mod.__file__ = f"{LANE}/{PROD}"
exec(compile(src(PINNED), mod.__file__, "exec"), mod.__dict__)
S = Path("/tmp/kama-r21-LinksGridReview/synth")
sym_link = S / "sym" / "llama-server"
print("unresolved dirname:", os.path.dirname(str(sym_link)))
print("realpath dirname:", os.path.dirname(os.path.realpath(sym_link)))
print("producer install_tree(unresolved) members:", sorted(mod.install_tree(str(sym_link))[0]))
print("producer install_tree(realpath) members:", sorted(mod.install_tree(os.path.realpath(sym_link))[0]))
print("digests equal:", mod.install_tree(str(sym_link))[1] == mod.install_tree(os.path.realpath(sym_link))[1])
