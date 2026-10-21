#!/usr/bin/env python3
"""LinksTreeDeterminism probe (round 21), scratch only.

Imports the producer and the gate from LANE (bytecode writing disabled; LANE is
never written) and injects faults only into TREE, a scratch copy of
~/.local/opt/llama-b11755. Fault classes:
  unreadable  chmod 000 on one member (open -> EACCES; lstat still succeeds)
  race        unlink of one member between os.listdir() and its lstat (ENOENT)
  listing     os.listdir() of the install directory raises EACCES
Every injected state is restored and re-verified against the healthy digests.
Only `readelf -d` (static) is executed besides the producer and gate code.
Usage: probe.py LANE TREE OUT
"""
import contextlib
import copy
import errno
import hashlib
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from functools import partial
from pathlib import Path

sys.dont_write_bytecode = True
LANE = Path(sys.argv[1]).resolve()
TREE = Path(sys.argv[2]).resolve()
OUT = Path(sys.argv[3]).resolve()
SRC = Path(os.path.expanduser("~/.local/opt/llama-b11755"))
SCRATCH = Path("/tmp/kama-r21-LinksTreeDeterminism").resolve()
assert TREE.is_relative_to(SCRATCH) and LANE.is_relative_to(SCRATCH), "scratch only"
assert TREE != SRC.resolve()
OUT.mkdir(parents=True, exist_ok=True)
RECEIPTS = OUT / "receipts"
RECEIPTS.mkdir(exist_ok=True)
SERVER = TREE / "llama-server"
IMPL = TREE / "libllama-server-impl.so"
PRODUCER = LANE / "tools/kama-llamacpp-live.py"
GATE_FILE = LANE / "tests/llamacpp-live/check-receipt.py"


def sha256_of(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


prod = load("kama_prod", PRODUCER)
gate = load("kama_gate", GATE_FILE)
BASE = gate._selftest_receipt_v3()


def needed(path):
    r = subprocess.run(["readelf", "-d", str(path)], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return re.findall(r"Shared library: \[([^\]]+)\]", r.stdout)


REG = sorted(n for n in os.listdir(TREE) if (TREE / n).is_file() and not (TREE / n).is_symlink())
LINKS_NAMES = sorted(n for n in os.listdir(TREE) if (TREE / n).is_symlink())
assert len(REG) == 51 and len(LINKS_NAMES) == 10, (len(REG), len(LINKS_NAMES))
SIZE = {n: (TREE / n).stat().st_size for n in REG}
TOTAL_BYTES = sum(SIZE.values())
ELF = {n: needed(TREE / n) is not None for n in REG}


def realname(name):
    return Path(os.path.realpath(TREE / name)).name


closure, todo, seen = set(), ["llama-server"], set()
while todo:
    f = todo.pop()
    if f in seen:
        continue
    seen.add(f)
    for dep in needed(TREE / f) or []:
        if (TREE / dep).exists():
            real = realname(dep)
            if real not in closure:
                closure.add(real)
                todo.append(real)
LINK_TARGETS = {realname(n) for n in LINKS_NAMES}
assert len(LINK_TARGETS) == 5, LINK_TARGETS


def healthy_now():
    t, ts = prod.install_tree(str(SERVER))
    l, ls = prod.install_links(str(SERVER))
    return t, ts, l, ls


H_TREE, H_TSHA, H_LINKS, H_LSHA = healthy_now()
assert len(H_TREE) == 51 and len(H_LINKS) == 10


def assert_healthy(tag):
    _, ts, _, ls = healthy_now()
    if (ts, ls) != (H_TSHA, H_LSHA):
        raise SystemExit(f"NOT RESTORED after {tag}: {ts} {ls}")


def evaluate(tree_hook=None, links_hook=None):
    """Mirror main()'s identity order (access check, server sha, install_tree,
    install_links, impl sha unguarded) and run the gate on the result. Only
    OSError is mapped to setup-error (main's fail-closed route for these calls)."""
    res = {"setup_error": None}
    if not (SERVER.is_file() and os.access(SERVER, os.X_OK)):
        res.update(setup_error="server-not-executable", gate_default="SETUP-ERROR",
                   gate_tree_pin="SETUP-ERROR", gate_links_pin="SETUP-ERROR")
        return res
    try:
        server_sha = prod.sha256_file(SERVER)
        with (tree_hook() if tree_hook else contextlib.nullcontext()):
            tree, tsha = prod.install_tree(str(SERVER))
        res.update(tree_members=len(tree), tree_sha=tsha)
        with (links_hook() if links_hook else contextlib.nullcontext()):
            links, lsha = prod.install_links(str(SERVER))
        res.update(links_count=len(links), links_sha=lsha)
        impl_sha = prod.sha256_file(IMPL) if os.path.isfile(IMPL) else None
    except OSError as exc:
        res.update(setup_error=f"{type(exc).__name__}(errno={exc.errno})",
                   gate_default="SETUP-ERROR", gate_tree_pin="SETUP-ERROR",
                   gate_links_pin="SETUP-ERROR")
        return res
    r = copy.deepcopy(BASE)
    r["server"].update(arg=str(SERVER), realpath=str(SERVER), sha256=server_sha,
                       install_tree=tree, install_tree_sha256=tsha,
                       install_links=links, install_links_sha256=lsha,
                       server_impl_sha256=impl_sha)
    r["argv"] = [str(SERVER), "-m", r["model"]["arg"], "--alias", r["alias"],
                 "--host", "127.0.0.1", "--port", str(r["port"]),
                 "-c", str(r["ctx"]), "-t", str(r["threads"]),
                 "--no-webui", "--offline"]
    problems = gate.validate(r)
    # Pin-specific verdicts: only messages the default run does not already carry.
    pin_tree = [p for p in gate.validate(r, expect_tree=H_TSHA) if p not in problems]
    pin_links = [p for p in gate.validate(r, expect_links=H_LSHA) if p not in problems]
    res.update(
        self_consistent=(gate.install_tree_sha(tree) == tsha),
        impl_in_tree=("libllama-server-impl.so" in tree),
        gate_default="VALID" if not problems else "INVALID",
        gate_default_problems=problems,
        gate_tree_pin="VALID" if not pin_tree else "INVALID",
        gate_links_pin="VALID" if not pin_links else "INVALID",
        receipt=r,
    )
    return res


@contextlib.contextmanager
def unreadable(name):
    p = TREE / name
    mode = stat.S_IMODE(os.lstat(p).st_mode)
    os.chmod(p, 0)
    try:
        try:
            with open(p, "rb"):
                opened = True
        except PermissionError:
            opened = False
        yield opened
    finally:
        os.chmod(p, mode)


@contextlib.contextmanager
def unlinked_before_stat(name, hit):
    real_lstat = os.lstat

    def racing(path, *a, **k):
        p = os.fsdecode(path)
        if not hit and os.path.basename(p) == name:
            hit.append(p)
            os.unlink(p)
        return real_lstat(path, *a, **k)

    os.lstat = racing
    try:
        yield hit
    finally:
        os.lstat = real_lstat


@contextlib.contextmanager
def listing_denied():
    real_listdir = os.listdir

    def denied(path="."):
        if Path(os.fsdecode(path)).resolve() == TREE:
            raise PermissionError(errno.EACCES, "injected: listing denied", os.fsdecode(path))
        return real_listdir(path)

    os.listdir = denied
    try:
        yield
    finally:
        os.listdir = real_listdir


def restore(name):
    dst, src = TREE / name, SRC / name
    if os.path.lexists(dst):
        os.unlink(dst)
    if src.is_symlink():
        os.symlink(os.readlink(src), dst)
    else:
        shutil.copy2(src, dst)


rows = []


def base_row(kind, member, res, injected=True):
    d = {"kind": kind, "member": member, "bytes": SIZE.get(member), "elf": ELF.get(member),
         "server_closure": member in closure, "link_target": member in LINK_TARGETS,
         "injected": injected}
    d.update({k: v for k, v in res.items() if k not in ("receipt", "gate_default_problems")})
    d["gate_default_first"] = (res.get("gate_default_problems") or [None])[0]
    rows.append(d)
    return d


def dump(name, res):
    if "receipt" in res:
        (RECEIPTS / f"{name}.json").write_text(json.dumps(res["receipt"], indent=1, sort_keys=True) + "\n")


# ---- baseline
base = evaluate()
assert base["gate_default"] == "VALID" and base["gate_tree_pin"] == "VALID" \
    and base["gate_links_pin"] == "VALID", base
assert base["self_consistent"] and base["tree_sha"] == H_TSHA and base["links_sha"] == H_LSHA
dump("healthy", base)
base_row("healthy", "-", base, injected=False)

# ---- sweep 1: unreadable member (chmod 000)
for n in REG:
    with unreadable(n) as opened:
        res = evaluate()
    assert_healthy(f"unreadable:{n}")
    if opened:
        base_row("unreadable", n, {"setup_error": "NOT-INJECTED (open succeeded)"}, injected=False)
        continue
    dump(f"unreadable-{n}", res)
    base_row("unreadable", n, res)

# ---- sweep 2: regular member unlinked between listdir and lstat (race)
for n in REG:
    hit = []
    try:
        res = evaluate(tree_hook=partial(unlinked_before_stat, n, hit))
    finally:
        restore(n)
    assert_healthy(f"race:{n}")
    if not hit:
        base_row("race-member", n, {"setup_error": "NOT-INJECTED"}, injected=False)
        continue
    dump(f"race-{n}", res)
    base_row("race-member", n, res)

# ---- sweep 3: soname link unlinked between listdir and lstat (install_links only)
for n in LINKS_NAMES:
    hit = []
    try:
        res = evaluate(links_hook=partial(unlinked_before_stat, n, hit))
    finally:
        restore(n)
    assert_healthy(f"link-race:{n}")
    if not hit:
        base_row("race-link", n, {"setup_error": "NOT-INJECTED"}, injected=False)
        continue
    dump(f"race-link-{n}", res)
    base_row("race-link", n, res)

# ---- sweep 4: directory listing denied
for label, th, lh in (("listing-both", listing_denied, listing_denied),
                      ("listing-links-only", None, listing_denied),
                      ("listing-tree-only", listing_denied, None)):
    res = evaluate(tree_hook=th, links_hook=lh)
    dump(label, res)
    base_row(label, "-", res)
    assert_healthy(label)

# ---- contrast: non-UTF-8 member name (same producer function, fail-loud)
bad = os.fsencode(TREE) + b"/\xff-probe.so"
with open(bad, "wb") as fh:
    fh.write(b"x")
try:
    try:
        prod.install_tree(str(SERVER))
        contrast = "no exception"
    except Exception as exc:  # noqa: BLE001 - recording the exact type
        contrast = type(exc).__name__
finally:
    os.unlink(bad)
assert_healthy("nonutf8")

# ---- outputs
cols = ["kind", "member", "bytes", "elf", "server_closure", "link_target", "injected",
        "tree_members", "tree_sha", "impl_in_tree", "self_consistent", "links_count",
        "links_sha", "setup_error", "gate_default", "gate_default_first",
        "gate_tree_pin", "gate_links_pin"]
with open(OUT / "sweep.tsv", "w") as fh:
    fh.write("\t".join(cols) + "\n")
    for d in rows:
        vals = []
        for c in cols:
            v = d.get(c)
            if c in ("tree_sha", "links_sha") and v:
                v = v[:12]
            if c == "gate_default_first" and v:
                v = str(v)[:120]
            vals.append("" if v is None else str(v))
        fh.write("\t".join(vals) + "\n")


def tally(kind):
    sel = [d for d in rows if d["kind"] == kind and d["injected"]]
    ran = [d for d in sel if d["gate_default"] != "SETUP-ERROR"]
    silent = [d for d in ran if d["gate_default"] == "VALID"]
    accepted = [d for d in silent if d.get("tree_sha") != H_TSHA or d.get("links_sha") != H_LSHA]
    caught = [d for d in ran if d["gate_default"] == "INVALID"]
    shares = sorted(d["bytes"] / TOTAL_BYTES for d in accepted if d["bytes"])
    counts = [d["tree_members"] for d in ran if d.get("tree_members") is not None]
    first = lambda d: str(d.get("gate_default_first"))  # noqa: E731
    return {
        "cells": len(sel), "ran_to_gate": len(ran),
        "setup_error": [d["member"] for d in sel if d["gate_default"] == "SETUP-ERROR"],
        "default_VALID_with_changed_identity": len(accepted),
        "default_INVALID": len(caught),
        "INVALID_via_link_chain": sum("chain" in first(d) for d in caught),
        "INVALID_via_server_basename": sum("server basename" in first(d) for d in caught),
        "tree_pin_INVALID": sum(d["gate_tree_pin"] == "INVALID" for d in ran),
        "links_pin_INVALID": sum(d["gate_links_pin"] == "INVALID" for d in ran),
        "tree_digest_changed": sum(d.get("tree_sha") != H_TSHA for d in ran),
        "links_digest_changed": sum(d.get("links_sha") != H_LSHA for d in ran),
        "tree_members_after_min_max": [min(counts, default=None), max(counts, default=None)],
        "accepted_members": [d["member"] for d in accepted],
        "caught_members": [d["member"] for d in caught],
        "accepted_share_of_total_bytes_min_median_max":
            [round(shares[0], 4), round(shares[len(shares) // 2], 4), round(shares[-1], 4)]
            if shares else None,
    }


summary = {
    "lane": str(LANE),
    "producer_sha256": sha256_of(PRODUCER), "gate_sha256": sha256_of(GATE_FILE),
    "tree": str(TREE), "healthy_install_tree_sha256": H_TSHA,
    "healthy_install_links_sha256": H_LSHA, "regular_members": len(REG),
    "symlinks": len(LINKS_NAMES), "regular_bytes_total": TOTAL_BYTES,
    "link_targets": sorted(LINK_TARGETS), "server_dt_needed_closure": sorted(closure),
    "unreadable": tally("unreadable"), "race_member": tally("race-member"),
    "race_link": tally("race-link"),
    "listing": {k: {f: v for f, v in next(d for d in rows if d["kind"] == k).items()
                    if f not in ("kind", "member", "injected", "bytes", "elf")}
                for k in ("listing-both", "listing-links-only", "listing-tree-only")},
    "contrast_nonutf8_install_tree": contrast,
}
(OUT / "summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n")
print(json.dumps(summary, indent=1, sort_keys=True))
print("PROBE-DONE")
