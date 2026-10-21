#!/usr/bin/env python3
"""KnowledgeAccuracy (round 21, FALSIFY) probes for the llamacpp-loading-lifecycle
round-21 supplement (corpus/knowledge/llamacpp-loading-lifecycle.md:324-362).

Read-only on the real install tree and on the live receipt; every write goes under
--work. Prints observed values. It computes no verdict; the report draws verdicts.
Needs gcc (glibc loader probes). Starts no server.

Usage: probe.py --lane DIR --work DIR --tree SERVER --receipt FILE --r18 DIR
  --lane     lane checkout at a6617149 (tools/, tests/, corpus/ read from here)
  --tree     real install server path, e.g. ~/.local/opt/llama-b11755/llama-server
  --receipt  live v3 receipt (round 21 measured run)
  --r18      directory holding round-18 receipt-*.json files
"""
import argparse
import copy
import errno
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
for flag in ("--lane", "--work", "--tree", "--receipt", "--r18"):
    ap.add_argument(flag, required=True)
args = ap.parse_args()
LANE, WORK = Path(args.lane), Path(args.work)
GATE = LANE / "tests/llamacpp-live/check-receipt.py"
PROD = LANE / "tools/kama-llamacpp-live.py"
shutil.rmtree(WORK, ignore_errors=True)
WORK.mkdir(parents=True)
ENV = ["env", "-i", "PATH=/usr/bin:/bin", "LANG=C"]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gate = load("kama_gate", GATE)
prod = load("kama_producer", PROD)
base = gate._selftest_receipt_v3()
BASE_SHA = base["server"]["install_links_sha256"]


def sha_of(links):
    return prod.links_digest(links)


def scen(label, mutate, **kw):
    r = copy.deepcopy(base)
    mutate(r["server"])
    probs = gate.validate(r, **kw)
    print(f"[{label}] {'VALID' if not probs else 'INVALID'} kw={kw} problems={probs}")


def drop_block(s):
    s.pop("install_links")
    s.pop("install_links_sha256")


def empty_null(s):
    s["install_links"] = {}
    s["install_links_sha256"] = None


def empty_consistent(s):
    s["install_links"] = {}
    s["install_links_sha256"] = sha_of({})


def map_null_digest(s):
    s["install_links_sha256"] = None


def set_links(links):
    def fn(s):
        s["install_links"] = links
        s["install_links_sha256"] = sha_of(links)
    return fn


def skeleton(s):
    s["install_tree"] = {}
    s["install_tree_sha256"] = None
    s["install_links"] = {}
    s["install_links_sha256"] = None


RETARGET = {"libllama.so.0": "llama-server", "libllama-alias.so": "libllama.so.0"}

print("== 1 gate boundary scenarios: gate.validate() on the round-21 v3 fixture")
scen("S0 base", lambda s: None)
scen("S1 block dropped, default", drop_block)
scen("S1 block dropped, require", drop_block, require_links=True)
scen("S1 block dropped, pin=base", drop_block, expect_links=BASE_SHA)
scen("S2 empty map + null digest, default", empty_null)
scen("S2 empty map + null digest, require", empty_null, require_links=True)
scen("S2 empty map + null digest, pin=base", empty_null, expect_links=BASE_SHA)
scen("S3 empty map + digest({}), pin=base", empty_consistent, expect_links=BASE_SHA)
scen("S4 non-empty map + null digest", map_null_digest)
scen("S5 './' same-directory target", set_links({"libllama.so.0": "./libllama.so"}))
scen("S6 consistent retarget, default", set_links(RETARGET))
scen("S6 consistent retarget, pin=base", set_links(RETARGET), expect_links=BASE_SHA)
scen("S7 link name == regular member", set_links({"llama-server": "libllama.so"}))
scen("S8 dangling chain", set_links({"libllama.so.0": "missing.so"}))
scen("S9 loop", set_links({"a.so": "b.so", "b.so": "a.so"}))
scen("S10 '../x/' target", set_links({"libllama.so.0": "../x/libllama.so"}))
scen("S11 producer setup-error skeleton", skeleton)


def write_receipt(name, mutate):
    r = copy.deepcopy(base)
    mutate(r["server"])
    p = WORK / name
    p.write_text(json.dumps(r), encoding="utf-8")
    return p


def cli(p, *extra):
    proc = subprocess.run([sys.executable, str(GATE), str(p), *extra],
                          capture_output=True, text=True)
    lines = (proc.stdout + proc.stderr).strip().splitlines()
    return proc.returncode, " | ".join(lines[:2])


print("== 2 CLI exit codes: check-receipt.py on the same mutations")
cases = [
    ("drop-block", write_receipt("drop-block.json", drop_block), []),
    ("drop-block", write_receipt("drop-block.json", drop_block), ["--require-install-links"]),
    ("empty-null", write_receipt("empty-null.json", empty_null), ["--require-install-links"]),
    ("empty-null", write_receipt("empty-null.json", empty_null),
     ["--expect-install-links-sha256", BASE_SHA]),
    ("dot-target", write_receipt("dot-target.json",
                                 set_links({"libllama.so.0": "./libllama.so"})), []),
]
for label, p, extra in cases:
    rc, out = cli(p, *extra)
    print(f"exit={rc} [{label}] {' '.join(extra)} :: {out[:200]}")

print("== 3 producer install_tree / install_links on a synthetic tree (fault injection)")
T = WORK / "synthetic"
T.mkdir()
(T / "llama-server").write_bytes(b"server-bytes\n")
(T / "libllama.so.0.7.0").write_bytes(b"lib-a\n")
(T / "libllama.so.0.7.1").write_bytes(b"lib-b\n")
os.symlink("libllama.so.0.7.0", T / "libllama.so.0")
SERVER = str(T / "llama-server")
t0, s0 = prod.install_tree(SERVER)
l0, _, p0 = prod.install_links(SERVER)
print("unmodified: regular", sorted(t0), "links", l0, "problems", p0)

real_sha = prod.sha256_file


def eio_on_b(path):
    if os.path.basename(path) == "libllama.so.0.7.1":
        raise OSError(errno.EIO, "injected read error")
    return real_sha(path)


prod.sha256_file = eio_on_b
try:
    t1, s1 = prod.install_tree(SERVER)
    _, _, p1 = prod.install_links(SERVER)
finally:
    prod.sha256_file = real_sha
print("injected EIO on libllama.so.0.7.1: regular", sorted(t1),
      "tree_sha changed", s1 != s0, "install_links problems", p1)

os.chmod(T / "libllama.so.0.7.1", 0)
t2, _ = prod.install_tree(SERVER)
_, _, p2 = prod.install_links(SERVER)
print(f"chmod 000 (euid {os.geteuid()}): regular", sorted(t2), "problems", p2)
os.chmod(T / "libllama.so.0.7.1", 0o644)

D = WORK / "ctl"
D.mkdir()
(D / "llama-server").write_bytes(b"s")
for nm in ["lib\x01x.so", "lib\x7fx.so", "lib\x85x.so"]:
    (D / nm).write_bytes(b"x")
    _, _, pc = prod.install_links(str(D / "llama-server"))
    print("name", repr(nm), "-> problems", pc)
    (D / nm).unlink()

print("== 4 glibc-hwcaps loader order (gcc stubs, RUNPATH=$ORIGIN, env -i)")
H = WORK / "hwcaps"
H.mkdir()
(H / "base.c").write_text("int which(void){return 2;}\n")
(H / "hwcaps.c").write_text("int which(void){return 1;}\n")
(H / "main.c").write_text("int which(void);\nint main(void){return which();}\n")


def cc(*argv):
    return subprocess.run(["gcc", *argv], capture_output=True, text=True)


assert cc("-shared", "-fPIC", "-Wl,-soname,libprobe.so.0", "-o",
          str(H / "libprobe-base.so.0"), str(H / "base.c")).returncode == 0
assert cc("-shared", "-fPIC", "-Wl,-soname,libprobe.so.0", "-o",
          str(H / "libprobe-hwcaps.so.0"), str(H / "hwcaps.c")).returncode == 0
TR = H / "tree"
TR.mkdir()
shutil.copyfile(H / "libprobe-base.so.0", TR / "libprobe.so.0")
assert cc("-o", str(TR / "prog"), str(H / "main.c"), str(H / "libprobe-base.so.0"),
          "-Wl,-rpath,$ORIGIN").returncode == 0


def prog_exit(tree):
    return subprocess.run(ENV + [str(tree / "prog")], capture_output=True).returncode


(TR / "glibc-hwcaps" / "x86-64-v3").mkdir(parents=True)
shutil.copyfile(H / "libprobe-hwcaps.so.0", TR / "glibc-hwcaps" / "x86-64-v3" / "libprobe.so.0")
print("A glibc-hwcaps/x86-64-v3 copy present: prog exit", prog_exit(TR), "(1 = hwcaps copy, 2 = base)")
shutil.rmtree(TR / "glibc-hwcaps")
print("A glibc-hwcaps removed:                prog exit", prog_exit(TR))

OUTSIDE = H / "outside" / "x86-64-v3"
OUTSIDE.mkdir(parents=True)
shutil.copyfile(H / "libprobe-hwcaps.so.0", OUTSIDE / "libprobe.so.0")
os.symlink("../outside", TR / "glibc-hwcaps")
print("B symlink glibc-hwcaps -> ../outside:  prog exit", prog_exit(TR), "(1 = loaded from outside the tree)")
trace = subprocess.run(ENV + ["LD_DEBUG=libs", str(TR / "prog")], capture_output=True, text=True).stderr
print("  trace:", [l.strip()[-80:] for l in trace.splitlines() if "trying file" in l and "glibc-hwcaps" in l][:2])
links_b, _, probs_b = prod.install_links(str(TR / "prog"))
tree_b, _ = prod.install_tree(str(TR / "prog"))
print("  producer install_links", links_b, "problems", probs_b, "regular", sorted(tree_b))
print("  gate chain rule for 'glibc-hwcaps':", gate.link_chain_problem("glibc-hwcaps", links_b, tree_b))

print("== 5 real install tree (read-only) vs live receipt")
REAL = args.tree
links_now, sha_now, probs_now = prod.install_links(REAL)
tree_now, tsha_now = prod.install_tree(REAL)
rs = json.loads(Path(args.receipt).read_text(encoding="utf-8"))["server"]
print("producer install_tree_sha256", tsha_now, "regular", len(tree_now))
print("receipt  install_tree_sha256", rs["install_tree_sha256"], "regular", len(rs["install_tree"]))
print("producer install_links_sha256", sha_now, "links", len(links_now), "problems", probs_now)
print("receipt  install_links_sha256", rs["install_links_sha256"], "links", len(rs["install_links"]))
print("maps equal: links", links_now == rs["install_links"], "| tree", tree_now == rs["install_tree"])
legacy = "".join(f"{k} -> {v}\n" for k, v in sorted(links_now.items()))
print("line-joined 'name -> target' digest (pre-canonical):", hashlib.sha256(legacy.encode()).hexdigest())

print("== 6 round-18 v3 receipts through the current gate (CLI)")
for p in sorted(Path(args.r18).glob("**/receipt-*.json")):
    a = subprocess.run([sys.executable, str(GATE), str(p)], capture_output=True, text=True).returncode
    b = subprocess.run([sys.executable, str(GATE), str(p), "--require-install-links"],
                       capture_output=True, text=True).returncode
    print(f"{p.parent.name}/{p.name}: default exit {a}; --require-install-links exit {b}")
print("probe-done")
