#!/usr/bin/env python3
"""KamaR21.C2GateReview extra probes (read-only against the scratch clone).

(1) A consistent soname retarget seen by a consumer that pins only the tree
    digest (the pre-round-21 pin set) versus one that also pins the links.
(2) Producer install_links() on lstat/readlink failures (monkeypatched:
    simulated I/O errors, not reproduced on a real device).

Usage: probe_extra.py GATE PRODUCER LIVE_RECEIPT WORK
"""
import copy
import importlib.util
import json
import os
import shutil
import subprocess
import sys

GATE, PRODUCER, LIVE, WORK = sys.argv[1:5]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gate = load("gate_under_test", GATE)
prod = load("producer_under_test", PRODUCER)
with open(LIVE, encoding="utf-8") as fh:
    BASE = json.load(fh)
SRV = BASE["server"]
TREE_PIN = SRV["install_tree_sha256"]
LINKS_PIN = SRV["install_links_sha256"]
shutil.rmtree(WORK, ignore_errors=True)
os.makedirs(WORK)


def run(receipt, flags, tag):
    path = os.path.join(WORK, tag + ".json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh)
    p = subprocess.run([sys.executable, GATE, path, *flags],
                       capture_output=True, text=True, timeout=300)
    return p.returncode, (p.stdout.splitlines() or [""])[0]


print("## (1) consistent retarget libggml.so.0 -> libggml-base.so.0.27.0")
r = copy.deepcopy(BASE)
links = dict(SRV["install_links"])
links["libggml.so.0"] = "libggml-base.so.0.27.0"
r["server"]["install_links"] = links
r["server"]["install_links_sha256"] = gate.install_links_sha(links)
print("retarget, tree pin only          rc=%d %s"
      % run(r, ["--expect-install-tree-sha256", TREE_PIN], "retarget-treepin"))
print("retarget, tree pin + require     rc=%d %s"
      % run(r, ["--expect-install-tree-sha256", TREE_PIN,
                "--require-install-links"], "retarget-treereq"))
print("retarget, tree pin + links pin   rc=%d %s"
      % run(r, ["--expect-install-tree-sha256", TREE_PIN,
                "--expect-install-links-sha256", LINKS_PIN],
            "retarget-treelinks"))
print("live, tree pin only              rc=%d %s"
      % run(copy.deepcopy(BASE), ["--expect-install-tree-sha256", TREE_PIN],
            "live-treepin"))

print("## (2) producer install_links() failure paths (simulated errors)")
d = os.path.join(WORK, "ptree")
os.makedirs(d)
server = os.path.join(d, "llama-server")
with open(server, "wb") as fh:
    fh.write(b"s\n")
with open(os.path.join(d, "libA.so.0.1"), "wb") as fh:
    fh.write(b"a\n")
os.symlink("libA.so.0.1", os.path.join(d, "libA.so.0"))
os.symlink("libA.so.0", os.path.join(d, "libA.so"))
real_readlink, real_lstat = os.readlink, os.lstat


def bad_readlink(p, *a, **k):
    if os.path.basename(p) == "libA.so":
        raise OSError(5, "simulated EIO")
    return real_readlink(p, *a, **k)


def bad_lstat(p, *a, **k):
    if os.path.basename(p) == "libA.so.0":
        raise FileNotFoundError(2, "simulated ENOENT")
    return real_lstat(p, *a, **k)


os.readlink = bad_readlink
try:
    print("readlink EIO on libA.so   problems=%r"
          % (prod.install_links(server)[2],))
finally:
    os.readlink = real_readlink
os.lstat = bad_lstat
try:
    print("lstat ENOENT on libA.so.0 problems=%r"
          % (prod.install_links(server)[2],))
finally:
    os.lstat = real_lstat
print("unpatched                 problems=%r"
      % (prod.install_links(server)[2],))
