#!/usr/bin/env python3
"""C2LiveReceiptVerify: independent recomputation of a kama-llamacpp-live v3 receipt.

Stdlib only. Imports nothing from the lane and calls no lane code. Subprocesses are
limited to find(1) (type, name, readlink text, NUL framed) and `git show <commit>:<path>`
(read-only blob reads from a scratch clone). Writes only under --out. Never executes
llama-server, the producer, or the probe.

Gating checks bind the receipt to COMMITTED bytes (producer/probe at PRODUCER_COMMIT)
and to the install tree on disk. Working-tree drift in the lane checkout is reported
as non-gating drift rows, never folded into the receipt verdict.
"""
import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys

SCHEMA = "kama-llamacpp-live/v3"
PRODUCER_COMMIT = "b76727f31e522763ce24e43d6ec86d21b507a11f"
LLAMA_COMMIT = "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"
LLAMA_RAW = "https://raw.githubusercontent.com/ggml-org/llama.cpp/" + LLAMA_COMMIT + "/"

# Literal values from recipe.json (model, tree, links) and from this session's
# sha256sum observations (tool, probe, server, impl). Compared only, never used
# to derive any recomputed value.
EXPECT = {
    "model_sha256": "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d",
    "install_tree_sha256": "6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c",
    "install_links_sha256": "5cb9f4865c8e1315dbd1baa99310c9bc65ddcf469929488359c66587b6470060",
    "tool_sha256": "e4cc6d8885c7755717157fd23bfce3be39288990a9cf5985cb1c56a4b11cf68f",
    "probe_sha256": "36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3",
    "server_sha256": "b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804",
    "server_impl_sha256": "e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed",
    "link_count": 10,
}

DUPLICATE_KEYS = []


def _pairs_hook(pairs):
    seen = set()
    for key, _ in pairs:
        if key in seen:
            DUPLICATE_KEYS.append(key)
        seen.add(key)
    return dict(pairs)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob(lane, commit, path):
    proc = subprocess.run(["git", "-C", lane, "show", f"{commit}:{path}"],
                          capture_output=True)
    if proc.returncode != 0:
        raise SystemExit(f"git show {commit}:{path} failed: "
                         f"{proc.stderr.decode(errors='replace').strip()}")
    return proc.stdout


def find_entries(directory):
    proc = subprocess.run(
        ["find", directory, "-mindepth", "1", "-maxdepth", "1",
         "-printf", "%y\\0%f\\0%l\\0"],
        capture_output=True, check=True)
    parts = proc.stdout.split(b"\0")
    if parts and parts[-1] == b"":
        parts.pop()
    if len(parts) % 3:
        raise SystemExit("find output is not (type, name, target) triples")
    entries = []
    for i in range(0, len(parts), 3):
        entries.append((parts[i].decode("ascii"),
                        parts[i + 1].decode("utf-8", "surrogateescape"),
                        parts[i + 2].decode("utf-8", "surrogateescape")))
    return entries


def snapshot_find(directory):
    """find(1) pass: symlinks -> readlink text, regular files -> sha256."""
    links, regular, other = {}, {}, []
    for kind, name, target in find_entries(directory):
        full = os.path.join(directory, name)
        if kind == "l":
            links[name] = target
        elif kind == "f":
            regular[name] = sha256_file(full)
        else:
            other.append(name)
    return links, regular, sorted(other)


def snapshot_os(directory):
    """Cross-check pass with os.lstat / os.readlink (no find)."""
    links, regular, other = {}, {}, []
    for name in sorted(os.listdir(directory)):
        full = os.path.join(directory, name)
        mode = os.lstat(full).st_mode
        if stat.S_ISLNK(mode):
            links[name] = os.readlink(full)
        elif stat.S_ISREG(mode):
            regular[name] = sha256_file(full)
        else:
            other.append(name)
    return links, regular, sorted(other)


def canonical_links(links):
    text = json.dumps(links, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True)
    manual = "{" + ",".join(json.dumps(k) + ":" + json.dumps(links[k])
                            for k in sorted(links)) + "}"
    return text, text == manual


def tree_digest(tree):
    text = "".join(f"{name} {tree[name]}\n" for name in sorted(tree))
    return sha256_bytes(text.encode("utf-8", "surrogateescape"))


def resolve_on_disk(directory, name, links, regular):
    """Follow the same-directory symlink chain, then compare realpath."""
    current, seen = name, []
    while current in links:
        if current in seen:
            return None, "symlink loop"
        seen.append(current)
        target = links[current]
        if "/" in target or target in ("", ".", ".."):
            return None, f"target {target!r} is not a same-directory basename"
        current = target
    if current not in regular:
        return None, f"chain ends at {current!r}, not a regular member"
    real = os.path.realpath(os.path.join(directory, name))
    want = os.path.join(os.path.realpath(directory), current)
    if real != want:
        return None, f"realpath {real} != {want}"
    return current, None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Recompute a kama-llamacpp-live v3 receipt.")
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--install-dir",
                    default=os.path.expanduser("~/.local/opt/llama-b11755"))
    ap.add_argument("--lane", required=True,
                    help="scratch clone at the producer commit (git show only)")
    ap.add_argument("--worktree",
                    default="/home/vgpnk/Projects/shokunin/kama-shokunin",
                    help="lane checkout, read-only, for non-gating drift rows")
    ap.add_argument("--upstream-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    os.makedirs(args.out, exist_ok=True)

    results = []

    def check(cid, expected, observed, note="", gating=True):
        ok = expected == observed
        results.append({"id": cid, "gating": gating, "pass": ok,
                        "expected": expected, "observed": observed, "note": note})
        return ok

    with open(args.receipt, "rb") as fh:
        rec = json.loads(fh.read(), object_pairs_hook=_pairs_hook)
    check("receipt.no_duplicate_keys", [], sorted(set(DUPLICATE_KEYS)))
    check("receipt.schema", SCHEMA, rec.get("schema"))
    check("receipt.outcome", "pass", rec.get("outcome"))
    check("receipt.setup_error", None, rec.get("setup_error"))
    check("receipt.internal_fault", None, rec.get("internal_fault"))

    srv = rec["server"]
    install = os.path.abspath(args.install_dir)

    # Producer, gate and probe: COMMITTED bytes at PRODUCER_COMMIT are the identity.
    prod_sha = sha256_bytes(git_blob(args.lane, PRODUCER_COMMIT,
                                     "tools/kama-llamacpp-live.py"))
    gate_sha = sha256_bytes(git_blob(args.lane, PRODUCER_COMMIT,
                                     "tests/llamacpp-live/check-receipt.py"))
    probe_sha = sha256_bytes(git_blob(args.lane, PRODUCER_COMMIT,
                                      "tools/kama-probe.sh"))
    check("tool.sha256 == git show b76727f3:tools/kama-llamacpp-live.py",
          rec["tool"]["sha256"], prod_sha)
    check("tool.sha256 == observed e4cc6d88", EXPECT["tool_sha256"], prod_sha)
    check("probe.sha256 == git show b76727f3:tools/kama-probe.sh",
          rec["probe"]["sha256"], probe_sha)
    check("probe.sha256 == observed 36b64978", EXPECT["probe_sha256"], probe_sha)

    # Working-tree drift (non-gating): the receipt verdict does not depend on it.
    for rel, committed in (("tools/kama-llamacpp-live.py", prod_sha),
                           ("tests/llamacpp-live/check-receipt.py", gate_sha),
                           ("tools/kama-probe.sh", probe_sha)):
        check(f"drift: worktree {rel} == committed b76727f3", committed,
              sha256_file(os.path.join(args.worktree, rel)), gating=False)
    check("drift: receipt.tool.path bytes == committed producer", prod_sha,
          sha256_file(rec["tool"]["path"]), gating=False)

    # Model bytes.
    check("model.sha256 recomputed from model.path", rec["model"]["sha256"],
          sha256_file(rec["model"]["path"]))
    check("model.sha256 == recipe pin", EXPECT["model_sha256"],
          rec["model"]["sha256"])
    check("model_sha256_post == model.sha256", rec["model"]["sha256"],
          rec["model_sha256_post"])

    # Server identity.
    real = os.path.realpath(os.path.join(install, "llama-server"))
    check("server.realpath == realpath(install/llama-server)", srv["realpath"], real)
    check("server.sha256 recomputed", srv["sha256"], sha256_file(real))
    check("server.sha256 == observed b6a31a8e", EXPECT["server_sha256"], srv["sha256"])
    impl = os.path.join(install, "libllama-server-impl.so")
    check("server_impl_sha256 recomputed", srv["server_impl_sha256"], sha256_file(impl))
    check("server_impl_sha256 == observed e404b91a", EXPECT["server_impl_sha256"],
          srv["server_impl_sha256"])

    # Install tree and install links: find(1) pass and os.lstat pass must agree.
    lf, rf, of = snapshot_find(install)
    lo, ro, oo = snapshot_os(install)
    check("find/readlink snapshot == os.lstat/os.readlink snapshot",
          [lf, rf, of], [lo, ro, oo])
    check("no entries other than regular files and symlinks", [], of)
    check("install_tree members == receipt server.install_tree", srv["install_tree"], rf)
    tree_sha = tree_digest(rf)
    check("install_tree_sha256 recomputed", srv["install_tree_sha256"], tree_sha)
    check("install_tree_sha256 == recipe pin", EXPECT["install_tree_sha256"], tree_sha)
    check("install_tree[llama-server] == server.sha256", srv["sha256"],
          rf.get("llama-server"))
    check("install_links == find/readlink link map", srv["install_links"], lf)
    check("install_links entry count", EXPECT["link_count"], len(lf))
    text, manual_ok = canonical_links(lf)
    check("canonical JSON: json.dumps == manual construction", True, manual_ok)
    links_sha = sha256_bytes(text.encode("ascii"))
    check("install_links_sha256 recomputed over canonical JSON",
          srv["install_links_sha256"], links_sha)
    check("install_links_sha256 == recipe pin", EXPECT["install_links_sha256"], links_sha)
    for name in sorted(lf):
        member, why = resolve_on_disk(install, name, lf, rf)
        results.append({"id": f"on-disk chain {name}", "gating": True,
                        "pass": why is None,
                        "expected": "pinned regular member",
                        "observed": member if why is None else why, "note": ""})

    # source_binding: fetched upstream bytes at LLAMA_COMMIT, not the gate's pins.
    sb = rec.get("source_binding")
    check("source_binding entry count", 5, len(sb) if isinstance(sb, list) else None)
    for i, entry in enumerate(sb):
        path = entry["path"]
        first, last = entry["lines"]
        with open(os.path.join(args.upstream_dir, os.path.basename(path)), "rb") as fh:
            up = fh.read()
        span = b"\n".join(up.split(b"\n")[first - 1:last]) + b"\n"
        tag = f"source_binding[{i}] {entry['check']} {path}:{first}-{last}"
        check(f"{tag} url", LLAMA_RAW + path, entry["url"])
        check(f"{tag} commit", LLAMA_COMMIT, entry["commit"])
        check(f"{tag} file_sha256 == sha256(upstream bytes)", entry["file_sha256"],
              sha256_bytes(up))
        check(f"{tag} span_text == upstream lines", span.decode("utf-8"),
              entry["span_text"])
        check(f"{tag} span_sha256 == sha256(upstream span)", entry["span_sha256"],
              sha256_bytes(span))

    gating_failed = [r["id"] for r in results if r["gating"] and not r["pass"]]
    drift = [r["id"] for r in results if not r["gating"] and not r["pass"]]
    summary = {"receipt": args.receipt, "install_dir": install, "lane": args.lane,
               "worktree": args.worktree, "upstream_dir": args.upstream_dir,
               "checks": len(results), "gating_checks": sum(r["gating"] for r in results),
               "gating_failed": gating_failed, "pass": not gating_failed,
               "nongating_drift": drift,
               "links_sha256": links_sha, "install_tree_sha256": tree_sha,
               "link_count": len(lf), "tree_members": len(rf)}
    with open(os.path.join(args.out, "result.json"), "w", encoding="utf-8") as fh:
        json.dump({"summary": summary, "results": results}, fh, indent=2,
                  ensure_ascii=True)
        fh.write("\n")
    with open(os.path.join(args.out, "install-links.canonical.json"), "w",
              encoding="ascii") as fh:
        fh.write(text + "\n")
    with open(os.path.join(args.out, "install-tree.sha256sum"), "w",
              encoding="utf-8") as fh:
        for name in sorted(rf):
            fh.write(f"{rf[name]}  {name}\n")
    for r in results:
        tag = "PASS" if r["pass"] else ("FAIL" if r["gating"] else "DRIFT")
        print(f"{tag} {r['id']}")
    print(f"summary checks={len(results)} gating_failed={len(gating_failed)} "
          f"nongating_drift={len(drift)} links_sha256={links_sha} "
          f"install_tree_sha256={tree_sha}")
    return 0 if not gating_failed else 1


if __name__ == "__main__":
    sys.exit(main())
