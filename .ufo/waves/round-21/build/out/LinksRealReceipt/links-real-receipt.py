#!/usr/bin/env python3
"""Round-21 LinksRealReceipt: install-links pin checked on the real install tree.

SPLICED, NOT A LIVE CAPTURE. Nothing is launched: no llama-server, no model,
no socket. install_tree() and install_links() are imported read-only from the
lane producer and run over the real install directory. Only the four install
fields are spliced into a copy of the round-18 receipt; no other receipt field
is recomputed. A scratch copy of the tree is then made, libllama.so.0 is
retargeted (to a pinned regular member, and in a second copy to an absent
name), each copy is re-identified and spliced the same way, and the lane gate
(check-receipt.py) decides every row. Each row's verdict is predeclared in
MATRIX before the gate runs.

Usage: links-real-receipt.py --lane DIR --work DIR [--out DIR] [--tree DIR] [--receipt FILE]
Exit: 0 every row matched its predeclared verdict; 1 a row did not match;
      2 could not evaluate (lane rev, missing tree, copy or write failure).
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

LANE_REV = "a29bb84abbb8b4d328f5970a89e448330a3a42ac"
PRODUCER = Path("tools/kama-llamacpp-live.py")
GATE = Path("tests/llamacpp-live/check-receipt.py")
TREE = Path.home() / ".local/opt/llama-b11755"
ROUND18 = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/"
               "round-18/live-recovery/receipt-1.json")
SERVER = "llama-server"
RETARGET = ("libllama.so.0", "libllama-common.so.0.7.0")  # pinned regular member
DANGLING = ("libllama.so.0", "libllama.so.9")            # name absent from tree
MISSING = object()

# (row, description, receipt key, pin key or None, predeclared gate exit)
MATRIX = [
    ("B0", "round-18 receipt as recorded, no pin", "base", None, 0),
    ("B1", "round-18 receipt as recorded, links pin", "base", "links", 1),
    ("R1", "real-tree splice, no pin", "real", None, 0),
    ("R2", "real-tree splice, links pin = real digest", "real", "links", 0),
    ("R3", "retarget splice, no pin", "retarget", None, 0),
    ("R4", "retarget splice, links pin = real digest", "retarget", "links", 1),
    ("R5", "retarget splice, tree pin = real digest", "retarget", "tree", 0),
    ("R6", "dangling splice, no pin", "dangling", None, 1),
]


class Unevaluated(Exception):
    """Could not evaluate: never a verdict."""


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head(lane: Path) -> str:
    proc = subprocess.run(["git", "-C", str(lane), "rev-parse", "HEAD"],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise Unevaluated(f"git rev-parse HEAD in {lane}: "
                          f"{proc.stderr.strip()}")
    return proc.stdout.strip()


def load_producer(lane: Path):
    spec = importlib.util.spec_from_file_location(
        "kama_llamacpp_live_lane", lane / PRODUCER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # defines the functions; main() not run
    return module


def identify(producer, server: Path) -> dict:
    tree, tree_sha = producer.install_tree(str(server))
    links, links_sha = producer.install_links(str(server))
    if tree_sha is None or links_sha is None:
        raise Unevaluated(f"producer could not list {server.parent}")
    return {"server_sha256": producer.sha256_file(str(server)),
            "tree": tree, "tree_sha256": tree_sha,
            "links": links, "links_sha256": links_sha}


def splice(receipt: dict, ident: dict) -> dict:
    out = copy.deepcopy(receipt)
    server = out["server"]
    server.update(install_tree=ident["tree"],
                  install_tree_sha256=ident["tree_sha256"],
                  install_links=ident["links"],
                  install_links_sha256=ident["links_sha256"])
    out["server"] = dict(sorted(server.items()))
    return out


def changed_fields(before: dict, after: dict) -> list[str]:
    changed = []
    for key in sorted(set(before) | set(after)):
        b, a = before.get(key, MISSING), after.get(key, MISSING)
        if key == "server" and isinstance(b, dict) and isinstance(a, dict):
            changed += [f"server.{k}" for k in sorted(set(b) | set(a))
                        if b.get(k, MISSING) != a.get(k, MISSING)]
        elif b != a:
            changed.append(key)
    return changed


def differing(a: dict, b: dict) -> list[str]:
    return sorted(k for k in set(a) | set(b)
                  if a.get(k, MISSING) != b.get(k, MISSING))


def mutated(producer, src: Path, work: Path, name: str, link: str,
            target: str, real: dict) -> dict:
    """Copy the real tree (symlinks kept), prove the copy identifies as the
    real tree, retarget one soname link, then identify the mutated copy."""
    dst = work / f"tree-{name}"
    shutil.copytree(src, dst, symlinks=True)
    try:
        mirror = identify(producer, dst / SERVER)
        if mirror["tree"] != real["tree"] or mirror["links"] != real["links"]:
            raise Unevaluated(f"{name}: unmodified copy differs from the tree")
        os.unlink(dst / link)
        os.symlink(target, dst / link)
        return identify(producer, dst / SERVER)
    finally:
        shutil.rmtree(dst)


def run(args) -> int:
    lane = args.lane.resolve()
    head = git_head(lane)
    if head != LANE_REV:
        raise Unevaluated(f"lane HEAD {head} != {LANE_REV}")
    producer = load_producer(lane)
    gate = lane / GATE
    server = args.tree / SERVER
    if not server.is_file():
        raise Unevaluated(f"{server} is not a file")
    real_server = Path(os.path.realpath(server))
    base = json.loads(args.receipt.read_text(encoding="utf-8"))
    real = identify(producer, real_server)
    log: list[str] = []

    def say(line: str = "") -> None:
        print(line)
        log.append(line)

    say("SPLICED receipt check (not a live capture; nothing launched)")
    say(f"lane HEAD {head}")
    say(f"producer {lane / PRODUCER} sha256={sha256_file(lane / PRODUCER)}")
    say(f"gate     {gate} sha256={sha256_file(gate)}")
    say(f"tree     {real_server.parent} server.sha256={real['server_sha256']}")
    say(f"round-18 receipt {args.receipt} "
        f"sha256={sha256_file(args.receipt)}")
    say()
    say(f"real install_tree: members={len(real['tree'])} "
        f"install_tree_sha256={real['tree_sha256']}")
    say(f"real install_links: links={len(real['links'])} "
        f"install_links_sha256={real['links_sha256']}")
    for name in sorted(real["links"]):
        say(f"    {name} -> {real['links'][name]}")
    rec = base["server"]
    say(f"round-18 recorded: members={len(rec['install_tree'])} "
        f"install_tree_sha256={rec['install_tree_sha256']}")
    say(f"round-18 vs real: tree_equal={rec['install_tree'] == real['tree']} "
        f"tree_sha_equal={rec['install_tree_sha256'] == real['tree_sha256']} "
        f"server_sha_equal={rec['sha256'] == real['server_sha256']} "
        f"differing_members={differing(rec['install_tree'], real['tree'])}")
    say()

    with tempfile.TemporaryDirectory(prefix="links-real-", dir=args.work) as tmp:
        work = Path(tmp)
        idents = {"real": real}
        idents["retarget"] = mutated(producer, args.tree, work, "retarget",
                                     *RETARGET, real)
        idents["dangling"] = mutated(producer, args.tree, work, "dangling",
                                     *DANGLING, real)
        for name in ("retarget", "dangling"):
            ident = idents[name]
            say(f"{name}: libllama.so.0 -> {ident['links'].get('libllama.so.0')} "
                f"tree_sha_equal_real={ident['tree_sha256'] == real['tree_sha256']} "
                f"links_sha_equal_real={ident['links_sha256'] == real['links_sha256']} "
                f"links_differing={differing(ident['links'], real['links'])}")
        say()

        paths = {"base": args.receipt}
        for name in ("real", "retarget", "dangling"):
            spliced = splice(base, idents[name])
            path = args.out / f"spliced-{name}.json"
            path.write_text(json.dumps(spliced, indent=2)
                            + "\n", encoding="utf-8")
            paths[name] = path
            say(f"wrote {path} changed_fields="
                f"{changed_fields(base, spliced)}")
        (args.out / "identities.json").write_text(json.dumps(
            {"lane_head": head, "real": real,
             "retarget": idents["retarget"], "dangling": idents["dangling"]},
            indent=1, sort_keys=True) + "\n", encoding="utf-8")
        say(f"wrote {args.out / 'identities.json'}")
        say()

        def pin_args(kind):
            if kind == "links":
                return ["--expect-install-links-sha256", real["links_sha256"]]
            if kind == "tree":
                return ["--expect-install-tree-sha256", real["tree_sha256"]]
            return []

        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        mismatches = 0
        for row, what, key, pin, want in MATRIX:
            extra = pin_args(pin)
            proc = subprocess.run(
                [sys.executable, str(gate), str(paths[key]), *extra],
                capture_output=True, text=True, env=env)
            ok = proc.returncode == want
            mismatches += not ok
            say(f"[{row}] {what}")
            say(f"    exit={proc.returncode} predeclared={want} "
                f"{'OK' if ok else 'MISMATCH'}")
            for line in (proc.stdout.splitlines()
                         or [f"<no stdout> stderr={proc.stderr.strip()}"]):
                say(f"    | {line}")
            say(f"    argv: check-receipt.py {paths[key].name} "
                f"{' '.join(extra)}".rstrip())
        say()
        say(f"matrix rows={len(MATRIX)} mismatches={mismatches}")

    (args.out / "verdicts.txt").write_text("\n".join(log) + "\n",
                                           encoding="utf-8")
    return 0 if mismatches == 0 else 1


def main(argv=None) -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--lane", required=True, type=Path,
                    help="scratch clone checked out at " + LANE_REV)
    ap.add_argument("--work", required=True, type=Path,
                    help="scratch directory for the tree copies")
    ap.add_argument("--out", type=Path, default=here,
                    help="deliverable directory (default: this script's)")
    ap.add_argument("--tree", type=Path, default=TREE)
    ap.add_argument("--receipt", type=Path, default=ROUND18)
    args = ap.parse_args(argv)
    try:
        return run(args)
    except (Unevaluated, OSError, ValueError, KeyError) as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
