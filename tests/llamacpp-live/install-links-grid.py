#!/usr/bin/env python3
"""Symlink-retarget detection grid for the llama.cpp install-tree pin.

Usage: install-links-grid.py [--tree DIR] [--arm frozen|current|both] [--json]
       install-links-grid.py --selftest

Mirrors one real install directory (symlinks preserved as links, regular
files copied) into a temporary directory, applies one named mutation per
cell, and asks each arm whether the recorded install identity changed:

  frozen   install_tree() from tools/kama-llamacpp-live.py at FROZEN_REV
           (regular files only; identity = install_tree_sha256)
  current  install_tree() + install_links() from the working tree
           (identity = install_tree_sha256, install_links_sha256)

Cell classes: `link` (only symlinks change), `regular` (a regular member
changes; control), `type` (a symlink becomes a regular file; control), and
`null` (no change; false-positive control). The current arm additionally
reports the receipt gate's chain verdict (tests/llamacpp-live/check-receipt.py
link_chain_problem) for every link cell.

Exit: 0 when the selected arm(s) detect every link/regular/type cell and no
null cell; 1 when an arm misses a cell or flags the null cell; 2 when the
grid could not be evaluated (missing tree, unusable git, copy failure).
`--arm frozen` is expected to exit 1: it is the before-state instrument.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types

LANE = Path(__file__).resolve().parents[2]
PRODUCER = "tools/kama-llamacpp-live.py"
GATE = LANE / "tests/llamacpp-live/check-receipt.py"
FROZEN_REV = "7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d"
DEFAULT_TREE = Path.home() / ".local/opt/llama-b11755"
SERVER = "llama-server"


class EvalError(Exception):
    """Could not evaluate: never a verdict."""


def load_source(name, source, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


def frozen_producer():
    proc = subprocess.run(["git", "-C", str(LANE), "show",
                           f"{FROZEN_REV}:{PRODUCER}"],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise EvalError(f"git show {FROZEN_REV}:{PRODUCER}: "
                        f"{proc.stderr.strip()}")
    return load_source("frozen_producer", proc.stdout,
                       LANE / f"{PRODUCER}@{FROZEN_REV[:12]}")


def current_producer():
    path = LANE / PRODUCER
    return load_source("current_producer", path.read_text(encoding="utf-8"),
                       path)


def gate_module():
    spec = importlib.util.spec_from_file_location("kama_gate", GATE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def mirror(src, dst):
    dst.mkdir()
    for entry in sorted(os.listdir(src)):
        full = src / entry
        if full.is_symlink():
            os.symlink(os.readlink(full), dst / entry)
        elif full.is_file():
            shutil.copyfile(full, dst / entry)
            shutil.copymode(full, dst / entry)


def links_of(directory):
    return sorted(e for e in os.listdir(directory)
                  if (directory / e).is_symlink())


def _relink(d, name, target):
    os.unlink(d / name)
    os.symlink(target, d / name)


def build_cells(tree):
    """Named cells over the real tree's own soname links. Each mutation is
    a function of the mirror directory; cells needing absent names are
    skipped with a reason rather than silently passing."""
    links = links_of(tree)
    regular = sorted(e for e in os.listdir(tree)
                     if (tree / e).is_file() and not (tree / e).is_symlink())
    if not links:
        raise EvalError(f"{tree}: no symlinks; the grid needs a soname tree")
    first, second = links[0], links[-1]
    real_of = {n: os.path.realpath(tree / n) for n in links}
    other_member = next(r for r in regular
                        if str(tree / r) != real_of[first])
    target_reg = os.path.basename(real_of[first])
    return [
        ("null-unchanged", "null", lambda d: None),
        ("link-retarget-member", "link",
         lambda d: _relink(d, first, other_member)),
        ("link-retarget-second", "link",
         lambda d: _relink(d, second, other_member)),
        ("link-dangling", "link",
         lambda d: _relink(d, first, first + ".missing")),
        ("link-absolute-outside", "link",
         lambda d: _relink(d, first, "/usr/lib/libc.so.6")),
        ("link-dotdot", "link",
         lambda d: _relink(d, first, "../" + target_reg)),
        ("link-delete", "link", lambda d: os.unlink(d / first)),
        ("link-add", "link",
         lambda d: os.symlink(target_reg, d / (first + ".kama-extra"))),
        ("link-same-resolution-shortcut", "link",
         lambda d: _relink(d, first, target_reg)
         if os.readlink(tree / first) != target_reg
         else _relink(d, first, "./" + target_reg)),
        ("link-loop", "link",
         lambda d: (_relink(d, first, first + ".loop"),
                    os.symlink(first, d / (first + ".loop")))),
        ("regular-append-byte", "regular",
         lambda d: open(d / target_reg, "ab").write(b"\0")),
        ("regular-add-file", "regular",
         lambda d: (d / "kama-extra.so").write_bytes(b"x")),
        ("type-link-to-regular-copy", "type",
         lambda d: (os.unlink(d / first),
                    shutil.copyfile(d / target_reg, d / first))),
    ]


def identities(module, server_path, with_links):
    tree, tree_sha = module.install_tree(str(server_path))
    if not with_links:
        return {"install_tree_sha256": tree_sha}, tree, {}
    links, links_sha = module.install_links(str(server_path))
    return ({"install_tree_sha256": tree_sha,
             "install_links_sha256": links_sha}, tree, links)


def run(tree, arms):
    tree = Path(tree)
    if not (tree / SERVER).is_file():
        raise EvalError(f"{tree}/{SERVER} missing")
    modules = {}
    if "frozen" in arms:
        modules["frozen"] = frozen_producer()
    if "current" in arms:
        modules["current"] = current_producer()
        if not hasattr(modules["current"], "install_links"):
            raise EvalError("current producer has no install_links()")
    gate = gate_module() if "current" in arms else None
    cells = build_cells(tree)
    rows = []
    real_ids = {arm: identities(m, tree / SERVER, arm == "current")[0]
                for arm, m in modules.items()}
    with tempfile.TemporaryDirectory(prefix="kama-links-grid-") as tmp:
        for name, klass, mutate in cells:
            mdir = Path(tmp) / name
            try:
                mirror(tree, mdir)
            except OSError as exc:
                raise EvalError(f"mirror {tree}: {exc}") from exc
            base = {arm: identities(m, mdir / SERVER, arm == "current")[0]
                    for arm, m in modules.items()}
            for arm in modules:
                if base[arm] != real_ids[arm]:
                    raise EvalError(f"mirror identity differs from {tree} "
                                    f"({arm})")
            mutate(mdir)
            row = {"cell": name, "class": klass, "expect_change":
                   klass != "null"}
            for arm, m in modules.items():
                ident, mtree, mlinks = identities(m, mdir / SERVER,
                                                  arm == "current")
                row[arm] = {"changed": ident != base[arm]}
                if arm == "current":
                    problems = {}
                    for link in sorted(mlinks):
                        if link in mtree:
                            problems[link] = "shadows member"
                            continue
                        why = gate.link_chain_problem(link, mlinks, mtree)
                        if why:
                            problems[link] = why
                    row[arm]["gate_chain_problems"] = problems
            rows.append(row)
            shutil.rmtree(mdir)
    summary = {}
    for arm in modules:
        missed = [r["cell"] for r in rows
                  if r[arm]["changed"] != r["expect_change"]]
        by = {}
        for klass in ("link", "regular", "type", "null"):
            sel = [r for r in rows if r["class"] == klass]
            by[klass] = {"cells": len(sel),
                         "changed": sum(r[arm]["changed"] for r in sel)}
        summary[arm] = {"by_class": by, "wrong": missed,
                        "status": "pass" if not missed else "fail"}
    if "frozen" in modules and "current" in modules:
        summary["back_compat_install_tree_sha256_equal"] = (
            real_ids["frozen"]["install_tree_sha256"]
            == real_ids["current"]["install_tree_sha256"])
    doc = {"tree": str(tree), "frozen_rev": FROZEN_REV, "arms": list(modules),
           "real_identity": real_ids, "summary": summary, "cells": rows}
    ok = all(summary[a]["status"] == "pass" for a in modules)
    if "back_compat_install_tree_sha256_equal" in summary:
        ok = ok and summary["back_compat_install_tree_sha256_equal"]
    return (0 if ok else 1), doc


def render(doc):
    out = []
    for r in doc["cells"]:
        parts = [f"{r['cell']:<32} class={r['class']:<7}"]
        for arm in doc["arms"]:
            parts.append(f"{arm}={'changed' if r[arm]['changed'] else 'same'}")
        if "current" in r and r["current"].get("gate_chain_problems"):
            parts.append("gate=" + ";".join(
                f"{k}:{v}" for k, v in r["current"]["gate_chain_problems"].items()))
        out.append(" ".join(parts))
    for arm in doc["arms"]:
        s = doc["summary"][arm]
        by = " ".join(f"{k}={v['changed']}/{v['cells']}"
                      for k, v in s["by_class"].items())
        out.append(f"summary arm={arm} {by} wrong={len(s['wrong'])} "
                   f"status={s['status']}")
    if "back_compat_install_tree_sha256_equal" in doc["summary"]:
        out.append("back_compat install_tree_sha256 equal="
                   f"{doc['summary']['back_compat_install_tree_sha256_equal']}")
    return "\n".join(out)


def selftest():
    """Synthetic soname tree: frozen-equivalent arm must miss link cells,
    current must catch all; missing tree and soname-less tree are errors."""
    checks = []
    with tempfile.TemporaryDirectory(prefix="kama-links-selftest-") as tmp:
        t = Path(tmp) / "tree"
        t.mkdir()
        (t / SERVER).write_bytes(b"server")
        os.chmod(t / SERVER, 0o755)
        (t / "libllama.so.0.7.0").write_bytes(b"lib")
        (t / "libggml.so.0.27.0").write_bytes(b"ggml")
        os.symlink("libllama.so.0.7.0", t / "libllama.so.0")
        os.symlink("libllama.so.0", t / "libllama.so")
        rc, doc = run(t, ("frozen", "current"))
        fz, cu = doc["summary"]["frozen"], doc["summary"]["current"]
        checks.append(("frozen-misses-all-link-cells",
                       fz["by_class"]["link"]["changed"] == 0))
        checks.append(("current-catches-all", cu["status"] == "pass"))
        checks.append(("controls-both-arms",
                       fz["by_class"]["regular"]["changed"] == 2
                       and fz["by_class"]["type"]["changed"] == 1))
        checks.append(("null-quiet", fz["by_class"]["null"]["changed"] == 0
                       and cu["by_class"]["null"]["changed"] == 0))
        checks.append(("combined-exit-1-because-frozen", rc == 1))
        rc_cur, _ = run(t, ("current",))
        checks.append(("current-only-exit-0", rc_cur == 0))
        gate_rows = {r["cell"]: r["current"]["gate_chain_problems"]
                     for r in doc["cells"]}
        checks.append(("gate-flags-dangling", bool(gate_rows["link-dangling"])))
        checks.append(("gate-flags-outside",
                       bool(gate_rows["link-absolute-outside"])))
        checks.append(("gate-flags-loop", bool(gate_rows["link-loop"])))
        checks.append(("gate-quiet-on-null", not gate_rows["null-unchanged"]))
        for label, path in (("missing-tree-error", Path(tmp) / "nope"),):
            try:
                run(path, ("current",))
                checks.append((label, False))
            except EvalError:
                checks.append((label, True))
        flat = Path(tmp) / "flat"
        flat.mkdir()
        (flat / SERVER).write_bytes(b"s")
        try:
            run(flat, ("current",))
            checks.append(("no-symlink-tree-error", False))
        except EvalError:
            checks.append(("no-symlink-tree-error", True))
    for name, ok in checks:
        print(f"{'ok' if ok else 'FAIL'} {name}")
    failed = sum(not ok for _, ok in checks)
    print(f"selftest cases={len(checks)} failed={failed}")
    return 0 if not failed else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tree", default=str(DEFAULT_TREE))
    ap.add_argument("--arm", choices=("frozen", "current", "both"),
                    default="both")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        try:
            return selftest()
        except EvalError as exc:
            print(f"could-not-evaluate: {exc}", file=sys.stderr)
            return 2
    arms = ("frozen", "current") if args.arm == "both" else (args.arm,)
    try:
        rc, doc = run(args.tree, arms)
    except (EvalError, OSError) as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(doc, indent=1, sort_keys=True) if args.json
          else render(doc))
    return rc


if __name__ == "__main__":
    sys.exit(main())
