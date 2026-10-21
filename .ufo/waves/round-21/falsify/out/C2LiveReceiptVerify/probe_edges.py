#!/usr/bin/env python3
"""Edge probe for the COMMITTED producer's install_tree/install_links (b76727f3).

Extracts only four pure functions (sha256_file, install_tree, links_digest, install_links)
from the committed producer via ast and runs them on tiny scratch directories built here.
No llama-server, no producer main(), no network. Output: probe_edges.json next to this file.
"""
import ast
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile

LANE = sys.argv[1] if len(sys.argv) > 1 else "/tmp/kama-r21-C2LiveReceiptVerify/lane"
COMMIT = "b76727f31e522763ce24e43d6ec86d21b507a11f"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe_edges.json")

src = subprocess.run(["git", "-C", LANE, "show", f"{COMMIT}:tools/kama-llamacpp-live.py"],
                     capture_output=True, check=True).stdout.decode("utf-8")
want = {"sha256_file", "install_tree", "links_digest", "install_links"}
nodes = [n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name in want]
assert {n.name for n in nodes} == want, "producer lacks expected functions"
mod = ast.Module(body=nodes, type_ignores=[])
ast.fix_missing_locations(mod)
ns = {"os": os, "stat": stat, "hashlib": hashlib, "json": json, "sys": sys}
exec(compile(mod, "<committed-producer-extract>", "exec"), ns)


def write(path_bytes, data=b"x"):
    with open(path_bytes, "wb") as fh:
        fh.write(data)


def base(d):
    write(os.path.join(d, b"llama-server"), b"server-stub\n")
    write(os.path.join(d, b"libllama.so.0.7.0"), b"lib\n")
    os.symlink(b"libllama.so.0.7.0", os.path.join(d, b"libllama.so.0"))


def case_nonutf8_regular(d):
    base(d)
    write(os.path.join(d, b"\xffx.so"))


def case_nonutf8_symlink(d):
    base(d)
    os.symlink(b"llama-server", os.path.join(d, b"\xffy.so"))


def case_nonutf8_dir(d):
    base(d)
    os.mkdir(os.path.join(d, b"\xffdir"))


def case_control_name(d):
    base(d)
    write(os.path.join(d, b"lib\nx.so"))


def case_subdir(d):
    base(d)
    os.makedirs(os.path.join(d, b"glibc-hwcaps", b"x86-64-v3"))


def run(name, build):
    with tempfile.TemporaryDirectory(prefix="edge-") as root:
        d = os.path.join(root, "install")
        os.mkdir(d)
        build(os.fsencode(d))
        server = os.path.join(d, "llama-server")
        try:
            tree, tsha = ns["install_tree"](server)
            tree_res = {"ok": True, "members": sorted(tree), "sha256": tsha}
        except Exception as exc:  # observed behaviour, recorded verbatim
            tree_res = {"ok": False, "exception": type(exc).__name__, "message": str(exc)[:200]}
        try:
            links, lsha, probs = ns["install_links"](server)
            links_res = {"ok": True, "links": links, "sha256": lsha, "problems": probs}
        except Exception as exc:
            links_res = {"ok": False, "exception": type(exc).__name__, "message": str(exc)[:200]}
        return {"case": name, "install_tree": tree_res, "install_links": links_res}


cases = [("baseline", base),
         ("nonutf8-regular-name", case_nonutf8_regular),
         ("nonutf8-symlink-name", case_nonutf8_symlink),
         ("nonutf8-dir-name", case_nonutf8_dir),
         ("control-char-name", case_control_name),
         ("subdir-glibc-hwcaps", case_subdir)]
rows = [run(n, b) for n, b in cases]
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump({"commit": COMMIT, "cases": rows}, fh, indent=2, ensure_ascii=True)
    fh.write("\n")
for r in rows:
    t, l = r["install_tree"], r["install_links"]
    tt = "ok" if t["ok"] else f"EXC {t['exception']}"
    ll = "ok" if l["ok"] else f"EXC {l['exception']}"
    extra = "" if not l.get("ok") else f" problems={l['problems']}"
    print(f"{r['case']:<24} install_tree={tt:<28} install_links={ll}{extra}")
