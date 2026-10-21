#!/usr/bin/env python3
"""Synthetic and real-tree checks of the C2 link rules, run against the head
snapshot of check-receipt.py and tools/kama-llamacpp-live.py. Read-only on the
real install directory (~/.local/opt/llama-b11755); all synthetic trees are
built under the reviewer's scratch directory and nothing is executed beyond the
gate's own CLI. Writes module-checks-corrected.txt into the out directory.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import traceback

S = "/tmp/kama-r21-LinksGateReview"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
OUT = f"{LANE}/.ufo/waves/round-21/build/out/LinksGateReview"
REAL = "/home/vgpnk/.local/opt/llama-b11755/llama-server"
SYN = f"{S}/synth2"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def gate_path(rev):
    return f"{S}/{rev}/tests/llamacpp-live/check-receipt.py"


prod = load(f"{S}/head/tools/kama-llamacpp-live.py", "prod_head")
gate = load(gate_path("head"), "gate_head")
log = []


def P(*a):
    s = " ".join(str(x) for x in a)
    log.append(s)
    print(s)


def fresh(name):
    root = os.path.join(SYN, name)
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(root)
    files = {"llama-server": b"server-bytes",
             "libllama-server-impl.so": b"impl-bytes",
             "libllama.so.0.7.0": b"llama-bytes",
             "libllama-common.so.0.7.0": b"common-bytes"}
    for n, b in files.items():
        with open(os.path.join(root, n), "wb") as fh:
            fh.write(b)
    links = {"libllama.so.0": "libllama.so.0.7.0",
             "libllama.so": "libllama.so.0",
             "libllama-common.so.0": "libllama-common.so.0.7.0"}
    for n, t in links.items():
        os.symlink(t, os.path.join(root, n))
    return root


def set_link(root, n, t):
    p = os.path.join(root, n)
    if os.path.lexists(p):
        os.remove(p)
    os.symlink(t, p)


def receipt(root):
    srv = os.path.join(root, "llama-server")
    r = gate._selftest_receipt()
    tr, trs = prod.install_tree(srv)
    lk, lks = prod.install_links(srv)
    r["server"].update(arg=srv, realpath=srv, sha256=tr["llama-server"],
                       install_tree=tr, install_tree_sha256=trs,
                       install_links=lk, install_links_sha256=lks,
                       server_impl_sha256=tr["libllama-server-impl.so"])
    r["argv"][0] = srv
    return r, trs, lks


def verdict(r, **pins):
    try:
        return gate.validate(r, **pins)
    except Exception as exc:
        return [f"EXCEPTION {type(exc).__name__}: {exc}"]


def clone(r):
    return json.loads(json.dumps(r))


def main():
    os.makedirs(OUT, exist_ok=True)
    try:
        tree, tree_sha = prod.install_tree(REAL)
        links, links_sha = prod.install_links(REAL)
        P("REAL members", len(tree), "tree_sha", tree_sha)
        P("REAL links", len(links), "links_sha", links_sha)
        P("REAL gate_links_digest_equals_producer",
          gate.install_links_sha(links) == links_sha,
          "gate_tree_digest_equals_producer", gate.install_tree_sha(tree) == tree_sha)
        for n in sorted(links):
            P("REAL chain", n, "->", links[n], "=> verdict",
              gate.link_chain_problem(n, links, tree))
    except Exception:
        P("REAL ERROR", traceback.format_exc()[-900:])

    try:
        root = fresh("base")
        r0, tree0, links0 = receipt(root)
        P("A base unpinned ->", verdict(r0))
        P("A base pinned(links,tree) ->", verdict(r0, expect_links=links0, expect_tree=tree0))
        set_link(root, "libllama.so.0", "libllama-common.so.0.7.0")
        r1, tree1, links1 = receipt(root)
        P("B retarget-to-member tree_sha_unchanged=", tree1 == tree0,
          "links_sha_changed=", links1 != links0)
        P("B retarget-to-member unpinned ->", verdict(r1))
        P("B retarget-to-member pinned_to_base_links ->", verdict(r1, expect_links=links0))
        set_link(root, "libllama.so.0", "libllama.so.9")
        r2, _, _ = receipt(root)
        P("C dangling unpinned ->", verdict(r2))
        set_link(root, "libllama.so.0", "/usr/lib/libllama.so")
        r3, _, _ = receipt(root)
        P("C absolute unpinned ->", verdict(r3))
    except Exception:
        P("SYN-A-C ERROR", traceback.format_exc()[-900:])

    try:
        root = fresh("forms")
        r, tree_sha, links_sha = receipt(root)
        x = clone(r); del x["server"]["install_links"]
        P("D digest-only(real digest, no links) unpinned ->", verdict(x))
        P("D digest-only(real digest, no links) pinned ->", verdict(x, expect_links=links_sha))
        y = clone(r); del y["server"]["install_links"]; y["server"]["install_links_sha256"] = "0" * 64
        P("D digest-only(bogus digest, no links) unpinned ->", verdict(y))
        z = clone(r); del z["server"]["install_links_sha256"]
        P("D links-without-digest-key unpinned ->", verdict(z))
        w = clone(r); del w["server"]["install_links"]; del w["server"]["install_links_sha256"]
        P("D stripped-both unpinned ->", verdict(w))
        P("D stripped-both pinned ->", verdict(w, expect_links=links_sha))
        u = clone(r); u["server"]["install_links_sha256"] = links_sha.upper()
        P("D uppercase digest unpinned ->", verdict(u))
        s = clone(r)
        s["server"]["install_links"]["sub/../libllama.so"] = "libllama.so.0.7.0"
        s["server"]["install_links_sha256"] = gate.install_links_sha(s["server"]["install_links"])
        P("D slash-name key unpinned ->", verdict(s))
        e = clone(r); e["server"]["install_links"] = {}; e["server"]["install_links_sha256"] = None
        P("D empty+null unpinned ->", verdict(e))
        n = clone(r); n["server"]["install_links"] = None
        P("D links=null unpinned ->", verdict(n))
    except Exception:
        P("FORM ERROR", traceback.format_exc()[-900:])

    try:
        root = fresh("surrogate")
        r, _, _ = receipt(root)
        rs = clone(r)
        rs["server"]["install_links"]["\udcff"] = "libllama.so.0.7.0"
        rs["server"]["install_links_sha256"] = "0" * 64
        P("SURR links-key validate:", verdict(rs))
        path_links = f"{SYN}/surrogate-links.json"
        with open(path_links, "w", encoding="utf-8") as fh:
            json.dump(rs, fh)
        rt = clone(r)
        rt["server"]["install_tree"]["\udcff"] = "0" * 64
        path_tree = f"{SYN}/surrogate-tree.json"
        with open(path_tree, "w", encoding="utf-8") as fh:
            json.dump(rt, fh)
        for rev in ("base", "head"):
            for label, pth in (("links-key", path_links), ("tree-key", path_tree)):
                p = subprocess.run([sys.executable, gate_path(rev), pth],
                                   capture_output=True, text=True, timeout=60)
                last = p.stderr.strip().splitlines()[-1:] if p.stderr.strip() else []
                P(f"SURR CLI {rev} {label} exit={p.returncode} "
                  f"stdout={p.stdout.strip()[:160]!r} stderr_last={last}")
    except Exception:
        P("SURR ERROR", traceback.format_exc()[-900:])

    with open(f"{OUT}/module-checks-corrected.txt", "w", encoding="utf-8") as fh:
        fh.write("\n".join(log) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
