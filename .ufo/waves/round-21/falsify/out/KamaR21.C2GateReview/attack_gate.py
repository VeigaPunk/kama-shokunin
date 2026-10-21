#!/usr/bin/env python3
"""KamaR21.C2GateReview falsification harness (FALSIFY seat, read-only).

Loads the attacked gate and producer from a scratch clone pinned at
a6617149, mutates copies of the committed live v3 receipt, runs the gate CLI
on each mutant, builds synthetic install trees under WORK and compares the
real producer output with the gate verdict, then recomputes the real install
tree read-only. Writes only under WORK and OUT_TXT.

Usage: attack_gate.py GATE PRODUCER LIVE_RECEIPT WORK OUT_TXT
"""
import copy
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time

GATE, PRODUCER, LIVE, WORK, OUT_TXT = sys.argv[1:6]
REAL_SERVER = "/home/vgpnk/.local/opt/llama-b11755/llama-server"
EMITTED = []
RECOMPUTE = object()
LINK_WORDS = ("install_links", "install_tree", "link", "chain", "target",
              "symlink", "leaves", "pinned")


def emit(text=""):
    EMITTED.append(text)
    print(text, flush=True)


def sha_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


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
L0 = dict(SRV["install_links"])
L0_SHA = SRV["install_links_sha256"]
END = "libggml.so.0.27.0"
assert END in SRV["install_tree"], "chain end must be a pinned member"
assert gate.install_links_sha(L0) == L0_SHA, "gate digest != receipt digest"

shutil.rmtree(WORK, ignore_errors=True)
os.makedirs(WORK)

emit(f"gate     {GATE} sha256={sha_file(GATE)}")
emit(f"producer {PRODUCER} sha256={sha_file(PRODUCER)}")
emit(f"live receipt {LIVE} sha256={sha_file(LIVE)}")
emit()


def mk(fn=None):
    r = copy.deepcopy(BASE)
    if fn is not None:
        fn(r)
    return r


def set_links(r, links, digest=RECOMPUTE):
    r["server"]["install_links"] = links
    r["server"]["install_links_sha256"] = (
        gate.install_links_sha(links) if digest is RECOMPUTE else digest)


def links_with(extra):
    out = dict(L0)
    out.update(extra)
    return out


def strip_both(r):
    r["server"].pop("install_links", None)
    r["server"].pop("install_links_sha256", None)


def orphan_garbage(r):
    r["server"].pop("install_links", None)
    r["server"]["install_links_sha256"] = "zz"


def orphan_valid(r):
    r["server"].pop("install_links", None)
    r["server"]["install_links_sha256"] = gate.install_links_sha(L0)


def empty_null(r):
    set_links(r, {}, digest=None)


def drop_end(r):
    tree = dict(r["server"]["install_tree"])
    tree.pop(END)
    r["server"]["install_tree"] = tree
    r["server"]["install_tree_sha256"] = gate.install_tree_sha(tree)


def chain(n):
    links = {f"c{i:05d}": f"c{i + 1:05d}" for i in range(n - 1)}
    links[f"c{n - 1:05d}"] = END
    return links


def run_gate(receipt, flags, tag):
    path = os.path.join(WORK, tag + ".json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh)
    t0 = time.perf_counter()
    p = subprocess.run([sys.executable, GATE, path, *flags],
                       capture_output=True, text=True, timeout=900)
    return p.returncode, p.stdout.splitlines(), time.perf_counter() - t0


CASES = []


def case(name, want, note, build, flags=()):
    CASES.append((name, want, note, build, list(flags)))


# ---- receipt-level mutants on the committed live v3 receipt ----------------
case("base", 0, "committed live v3 receipt, default flags",
     lambda: mk())
case("strip-both-default", 0,
     "links block and digest deleted; default mode accepts (downgrade)",
     lambda: mk(strip_both))
case("strip-both-require", 1, "same with --require-install-links",
     lambda: mk(strip_both), ["--require-install-links"])
case("strip-both-pin", 1, "same with --expect-install-links-sha256",
     lambda: mk(strip_both), ["--expect-install-links-sha256", L0_SHA])
case("orphan-digest-garbage", 0,
     "no links block, digest field 'zz' present (never checked)",
     lambda: mk(orphan_garbage))
case("orphan-digest-garbage-require", 1,
     "same with --require-install-links",
     lambda: mk(orphan_garbage), ["--require-install-links"])
case("orphan-digest-valid", 0,
     "no links block, correct digest of L0 present (never checked)",
     lambda: mk(orphan_valid))
case("empty-block-null-digest", 0,
     "install_links {} with install_links_sha256 null",
     lambda: mk(empty_null))
case("empty-block-null-digest-require", 0,
     "same with --require-install-links",
     lambda: mk(empty_null), ["--require-install-links"])
case("empty-block-null-digest-pin", 1, "same with the links pin",
     lambda: mk(empty_null), ["--expect-install-links-sha256", L0_SHA])
case("empty-block-hex-digest", 0,
     "install_links {} with sha256('{}') (producer success shape)",
     lambda: mk(lambda r: set_links(r, {})))
case("nonempty-null-digest", 1, "non-empty links, null digest",
     lambda: mk(lambda r: r["server"].update(install_links_sha256=None)))
case("name-SOH-chain-ok", 0,
     "control-char (0x01) link name; producer fails closed, gate accepts",
     lambda: mk(lambda r: set_links(r, links_with({"lib\x01x.so": END}))))
case("name-LF-chain-ok", 0, "newline in link name",
     lambda: mk(lambda r: set_links(r, links_with({"lib\nx.so": END}))))
case("name-NUL-chain-ok", 0, "NUL in link name",
     lambda: mk(lambda r: set_links(r, links_with({"lib\x00x.so": END}))))
case("name-DEL-chain-ok", 0, "DEL (0x7f) in link name",
     lambda: mk(lambda r: set_links(r, links_with({"lib\x7fx.so": END}))))
case("name-surrogate-chain-ok", 0, "surrogate-escaped (non-UTF-8) name",
     lambda: mk(lambda r: set_links(r, links_with({"lib\udcffx.so": END}))))
case("target-dot", 1, "link target '.'",
     lambda: mk(lambda r: set_links(r, links_with({"libdot.so": "."}))))
case("target-dotdot", 1, "link target '..'",
     lambda: mk(lambda r: set_links(r, links_with({"libdot.so": ".."}))))
case("target-dotslash", 1,
     "same-directory './name' rejected (producer records it without problem)",
     lambda: mk(lambda r: set_links(r, links_with({"libdot.so": "./" + END}))))
case("target-empty", 1, "empty link target",
     lambda: mk(lambda r: set_links(r, links_with({"libdot.so": ""}))))
case("target-trailing-slash", 1, "target with trailing '/'",
     lambda: mk(lambda r: set_links(r, links_with({"libdot.so": END + "/"}))))
case("target-nul", 1, "target with trailing NUL",
     lambda: mk(lambda r: set_links(r, links_with({"libdot.so": END + "\x00"}))))
case("target-case", 1, "target with different case",
     lambda: mk(lambda r: set_links(r, links_with({"libdot.so": END.upper()}))))
case("target-server-exe", 0,
     "chain ends at executable llama-server (pinned member): accepted",
     lambda: mk(lambda r: set_links(r, links_with({"libalias.so": "llama-server"}))))
case("target-text-LICENSE", 0,
     "chain ends at text file LICENSE (pinned member): accepted",
     lambda: mk(lambda r: set_links(r, links_with({"libtxt.so": "LICENSE"}))))
case("dangling", 1, "chain ends outside pinned tree",
     lambda: mk(lambda r: set_links(
         r, links_with({"libggml.so.0": "libggml.so.0.99"}))))
case("loop", 1, "two-link cycle",
     lambda: mk(lambda r: set_links(r, links_with({"libggml.so.0": "libggml.so"}))))
case("shadow-tree-member", 1, "link named like a pinned member",
     lambda: mk(lambda r: set_links(r, links_with({"llama-cli": END}))))
case("links-is-list", 1, "install_links as array",
     lambda: mk(lambda r: set_links(r, list(L0.items()))))
case("links-is-null", 1, "install_links null",
     lambda: mk(lambda r: r["server"].update(install_links=None)))
case("links-int-value", 1, "non-string link text",
     lambda: mk(lambda r: set_links(r, links_with({"libint.so": 5}))))
case("pin-uppercase", 1, "pin given in uppercase hex",
     lambda: mk(), ["--expect-install-links-sha256", L0_SHA.upper()])
case("pin-leading-space", 1, "pin with leading space",
     lambda: mk(), ["--expect-install-links-sha256", " " + L0_SHA])
case("retarget-unpinned", 0,
     "consistent retarget onto another pinned member, no pin (documented)",
     lambda: mk(lambda r: set_links(
         r, links_with({"libggml.so.0": "libggml-base.so.0.27.0"}))))
case("retarget-pinned", 1, "same retarget with the links pin",
     lambda: mk(lambda r: set_links(
         r, links_with({"libggml.so.0": "libggml-base.so.0.27.0"}))),
     ["--expect-install-links-sha256", L0_SHA])
case("tree-end-removed", 1,
     "chain end removed from install_tree; tree digest recomputed",
     lambda: mk(drop_end))
case("sha-uppercase-recomputed", 1,
     "install_links_sha256 is the correct digest in uppercase",
     lambda: mk(lambda r: r["server"].update(
         install_links_sha256=gate.install_links_sha(L0).upper())))
case("chain-2000", 0, "timing: 2000-link chain, all valid",
     lambda: mk(lambda r: set_links(r, chain(2000))))
case("chain-8000", 0, "timing: 8000-link chain, all valid",
     lambda: mk(lambda r: set_links(r, chain(8000))))
case("orphan-digest-null", 0,
     "no links block, digest null (never checked)",
     lambda: mk(lambda r: (r["server"].pop("install_links", None),
                           r["server"].update(install_links_sha256=None))))
case("name-slash-chain-ok", 0,
     "link key with '/': subdirectory link the producer refuses",
     lambda: mk(lambda r: set_links(
         r, links_with({"glibc-hwcaps/x86-64-v3/libggml.so.0": END}))))
case("name-empty-chain-ok", 0, "empty link key",
     lambda: mk(lambda r: set_links(r, links_with({"": END}))))
case("name-dot-chain-ok", 0, "link key '.'",
     lambda: mk(lambda r: set_links(r, links_with({".": END}))))
case("name-dotdot-chain-ok", 0, "link key '..'",
     lambda: mk(lambda r: set_links(r, links_with({"..": END}))))

emit("## gate CLI on mutants of the committed live v3 receipt")
emit(f"{'case':30} {'want':>4} {'rc':>3} {'ok':4} {'sec':>6}  verdict")
DIFF = 0
for name, want, note, build, flags in CASES:
    rc, lines, dt = run_gate(build(), flags, name)
    ok = "OK" if rc == want else "DIFF"
    if ok == "DIFF":
        DIFF += 1
    verdict = lines[0].split(" ", 1)[0] if lines else "(no stdout)"
    emit(f"{name:30} {want:>4} {rc:>3} {ok:4} {dt:6.2f}  {verdict}")
    if note:
        emit(f"{'':30}      note: {note}")
    for m in [l.strip() for l in lines[1:4]]:
        emit(f"{'':30}      gate: {m[:160]}")
emit(f"mutant cases: {len(CASES)} run, {DIFF} differ from the verdict predicted by source reading")
emit()


# ---- producer output vs gate verdict on synthetic real install trees -------
def write_file(path, body):
    with open(path, "wb") as fh:
        fh.write(body)


def base_tree(name, extra):
    d = os.path.join(WORK, "tree-" + name)
    os.makedirs(d)
    server = os.path.join(d, "llama-server")
    write_file(server, b"server-stub\n")
    write_file(os.path.join(d, "libA.so.0.1"), b"lib-A\n")
    os.symlink("libA.so.0.1", os.path.join(d, "libA.so.0"))
    os.symlink("libA.so.0", os.path.join(d, "libA.so"))
    if extra is not None:
        extra(d)
    return server


def abs_outside(d):
    outside = os.path.join(WORK, "outside")
    os.makedirs(outside, exist_ok=True)
    write_file(os.path.join(outside, "libA.so.0.1"), b"outside\n")
    os.symlink(os.path.join(outside, "libA.so.0.1"),
               os.path.join(d, "libD.so"))


def loop(d):
    os.symlink("libG.so", os.path.join(d, "libF.so"))
    os.symlink("libF.so", os.path.join(d, "libG.so"))


def link(name, target):
    return lambda d: os.symlink(target, os.path.join(d, name))


def member(name, mode=None):
    def f(d):
        p = os.path.join(d, name)
        write_file(p, b"u\n")
        if mode is not None:
            os.chmod(p, mode)
    return f


MATRIX = [
    ("baseline", None, None),
    ("dot-slash-target", link("libB.so", "./libA.so.0.1"), None),
    ("dot-target", link("libC.so", "."), None),
    ("absolute-outside", abs_outside, None),
    ("dangling", link("libE.so", "libNOPE.so.9"), None),
    ("loop", loop, None),
    ("dir-symlink-dot", link("hwdir", "."), None),
    ("unreadable-unlinked", member("libU.so.0.1", mode=0), None),
    ("subdir-glibc-hwcaps",
     lambda d: os.makedirs(os.path.join(d, "glibc-hwcaps", "x86-64-v3")),
     None),
    ("fifo-member", lambda d: os.mkfifo(os.path.join(d, "pipe.so")), None),
    ("newline-name-member", member("lib\nI.so"), None),
    ("surrogate-name-link", link("lib\udcffS.so", "libA.so.0.1"), None),
    ("read-error-linked", None, "libA.so.0.1"),
    ("read-error-unlinked", member("libU.so.0.1"), "libU.so.0.1"),
]


def producer_outputs(server, fail_on):
    orig = prod.sha256_file
    if fail_on is not None:
        def failing(path):
            if os.path.basename(path) == fail_on:
                raise PermissionError(13, "simulated read failure")
            return orig(path)
        prod.sha256_file = failing
    try:
        tree, tsha = prod.install_tree(server)
        links, lsha, problems = prod.install_links(server)
    finally:
        prod.sha256_file = orig
    return tree, tsha, links, lsha, problems


def receipt_for(server, tree, tsha, links, lsha):
    r = mk()
    r["server"].update(
        arg=server, realpath=server,
        sha256=tree.get("llama-server"),
        install_tree=tree, install_tree_sha256=tsha,
        install_links=links, install_links_sha256=lsha,
        server_impl_sha256=tree.get("libllama-server-impl.so"))
    return r


emit("## producer (real install_tree/install_links) vs gate on synthetic trees")
emit("## gate rc counts unrelated argv/probe mismatches; only link lines are signal")
for name, extra, fail_on in MATRIX:
    server = base_tree(name, extra)
    tree, tsha, links, lsha, problems = producer_outputs(server, fail_on)
    if problems:
        emit(f"{name:26} producer REFUSES: {problems}")
        continue
    rc, lines, dt = run_gate(receipt_for(server, tree, tsha, links, lsha),
                             [], "tree-" + name)
    link_lines = [l.strip() for l in lines[1:] if any(w in l for w in LINK_WORDS)]
    emit(f"{name:26} producer OK tree={sorted(tree)} links={sorted(links.items())} "
         f"read-error={fail_on}")
    emit(f"{'':26} gate rc={rc} link-related lines={len(link_lines)}")
    for m in link_lines[:3]:
        emit(f"{'':26}   gate: {m[:160]}")
emit()

# ---- real tree: does the live receipt still describe it? (read-only) -------
rt_tree, rt_tsha = prod.install_tree(REAL_SERVER)
rt_links, rt_lsha, rt_problems = prod.install_links(REAL_SERVER)
emit("## real tree (read-only)")
emit(f"install_tree_sha256 match={rt_tsha == SRV['install_tree_sha256']} "
     f"install_links_sha256 match={rt_lsha == L0_SHA} "
     f"members={len(rt_tree)} links={len(rt_links)} problems={rt_problems}")
emit()

# ---- direct function probes ------------------------------------------------
emit("## gate.link_chain_problem direct probes")
for args in [("a", {"a": "."}, {"b": "h"}),
             ("a", {"a": "b", "b": "a"}, {}),
             ("a", {"a": "b"}, {"b": "h"}),
             ("a", {"a": "b"}, {"c": "h"}),
             ("a", {"a": ""}, {"b": "h"})]:
    emit(f"link_chain_problem{args} -> {gate.link_chain_problem(*args)!r}")

with open(OUT_TXT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(EMITTED) + "\n")
