#!/usr/bin/env python3
"""Symlink/loader-layout detection grid for the llama.cpp install-tree pin.

Usage: install-links-grid.py [--tree DIR] [--arm current|frozen|both] [--json]
       install-links-grid.py --selftest

Mirrors one real install directory (symlinks preserved as links, regular
files copied) into a temporary directory, applies one named mutation per
cell, and asks each arm whether the recorded install identity changed:

  frozen   install_tree() from tools/kama-llamacpp-live.py at FROZEN_REV
           (regular files only; identity = install_tree_sha256)
  current  install_tree() + install_links() from the working tree
           (identity = install_tree_sha256, install_links_sha256 and the
           producer's fail-closed problem list; any problem = refusal)

Cells name the soname links that `libllama-server-impl.so`/`llama-server`
list in DT_NEEDED for release b11755 (NEEDED_SONAMES; absent names are a
could-not-evaluate, never skipped). Classes: `link` (only symlinks change),
`subdir` (a glibc-hwcaps/ copy the loader searches first), `regular`
(regular member changes; control), `type` (symlink becomes a regular file;
control) and `null` (no change; false-positive control). The current arm
also reports the receipt gate's chain verdict (check-receipt.py
link_chain_problem) per row; the real (null) tree must have none.

Exit: 0 when every selected arm detects every non-null cell and no null
cell (and, for current, the real tree is gate-clean); 1 when an arm misses
or flags wrongly; 2 could-not-evaluate (missing tree or soname, unusable
git, copy failure, any internal error). `--arm frozen` is the before-state
instrument and is expected to exit 1.
"""
from __future__ import annotations

import argparse
import hashlib
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
NEEDED_SONAMES = ("libggml-base.so.0", "libggml.so.0", "libllama-common.so.0",
                  "libllama.so.0", "libmtmd.so.0")
CLASSES = ("link", "subdir", "regular", "type", "null")


class EvalError(Exception):
    """Could not evaluate: never a verdict."""


def load_source(name, source, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


def frozen_producer(lane=LANE):
    proc = subprocess.run(["git", "-C", str(lane), "show",
                           f"{FROZEN_REV}:{PRODUCER}"],
                          capture_output=True, encoding="utf-8")
    if proc.returncode != 0:
        raise EvalError(f"git show {FROZEN_REV}:{PRODUCER}: "
                        f"{proc.stderr.strip()}")
    return load_source("frozen_producer", proc.stdout,
                       lane / f"{PRODUCER}@{FROZEN_REV[:12]}")


def current_producer(lane=LANE):
    path = lane / PRODUCER
    module = load_source("current_producer",
                         path.read_text(encoding="utf-8"), path)
    if not hasattr(module, "install_links"):
        raise EvalError("current producer has no install_links()")
    return module


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
        else:
            raise EvalError(f"{full}: neither regular file nor symlink")


def _relink(d, name, target):
    os.unlink(d / name)
    os.symlink(target, d / name)


def _append(path):
    with open(path, "ab") as fh:
        fh.write(b"\0")


def _hwcaps(d, name):
    sub = d / "glibc-hwcaps" / "x86-64-v3"
    sub.mkdir(parents=True)
    shutil.copyfile(os.path.realpath(d / name), sub / name)


def build_cells(tree, sonames=NEEDED_SONAMES):
    links = {e for e in os.listdir(tree) if (tree / e).is_symlink()}
    missing = [n for n in sonames if n not in links]
    if missing:
        raise EvalError(f"{tree}: missing soname link(s): {', '.join(missing)}")
    real = {n: os.path.basename(os.path.realpath(tree / n)) for n in sonames}
    regular = sorted(e for e in os.listdir(tree) if (tree / e).is_file()
                     and not (tree / e).is_symlink())
    key = sonames[0] if "libllama.so.0" not in sonames else "libllama.so.0"
    key_real = real[key]
    libs = [r for r in regular if r.startswith("lib")]
    other = {n: next((r for r in libs if r != real[n]), None)
             for n in sonames}
    if None in other.values():
        raise EvalError(f"{tree}: no alternative regular member to retarget to")
    cells = [("null-unchanged", "null", lambda d: None)]
    for n in sonames:
        cells.append((f"needed-retarget-{n}", "link",
                      lambda d, n=n: _relink(d, n, other[n])))
    dev = sorted(links - set(sonames))
    if dev:
        cells.append((f"dev-link-retarget-{dev[0]}", "link",
                      lambda d: _relink(d, dev[0], other[sonames[0]])))
    cells += [
        ("link-dangling", "link", lambda d: _relink(d, key, key + ".missing")),
        ("link-absolute-outside", "link",
         lambda d: _relink(d, key, "/usr/lib/libc.so.6")),
        ("link-dotdot", "link", lambda d: _relink(d, key, "../" + key_real)),
        ("link-delete", "link", lambda d: os.unlink(d / key)),
        ("link-add", "link",
         lambda d: os.symlink(key_real, d / (key + ".kama-extra"))),
        ("link-same-resolution-text", "link",
         lambda d: _relink(d, key, "./" + key_real)),
        ("link-loop", "link",
         lambda d: (_relink(d, key, key + ".loop"),
                    os.symlink(key, d / (key + ".loop")))),
        ("subdir-hwcaps-shadow", "subdir", lambda d: _hwcaps(d, key)),
        ("regular-append-byte", "regular", lambda d: _append(d / key_real)),
        ("regular-add-file", "regular",
         lambda d: (d / "kama-extra.so").write_bytes(b"x")),
        ("regular-unreadable", "regular",
         lambda d: os.chmod(d / regular[-1], 0)),
        ("type-link-to-regular-copy", "type",
         lambda d: (os.unlink(d / key), shutil.copyfile(d / key_real, d / key))),
    ]
    return cells


def identity(module, server, with_links):
    tree, tree_sha = module.install_tree(str(server))
    if not with_links:
        return {"install_tree_sha256": tree_sha}, tree, {}
    links, links_sha, problems = module.install_links(str(server))
    return ({"install_tree_sha256": tree_sha, "install_links_sha256": links_sha,
             "problems": problems}, tree, links)


def gate_problems(gate, tree, links):
    out = {}
    for link in sorted(links):
        if link in tree:
            out[link] = "shadows member"
            continue
        why = gate.link_chain_problem(link, links, tree)
        if why:
            out[link] = why
    return out


def sha256_path(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(tree, arms, lane=LANE, sonames=NEEDED_SONAMES):
    tree = Path(os.path.realpath(tree))
    if not (tree / SERVER).is_file():
        raise EvalError(f"{tree}/{SERVER} missing")
    modules = {}
    if "frozen" in arms:
        modules["frozen"] = frozen_producer(lane)
    if "current" in arms:
        modules["current"] = current_producer(lane)
    gate = gate_module() if "current" in arms else None
    cells = build_cells(tree, sonames)
    server = Path(os.path.realpath(tree / SERVER))
    real_ids = {a: identity(m, server, a == "current")[0]
                for a, m in modules.items()}
    if "current" in modules and real_ids["current"]["problems"]:
        raise EvalError(f"{tree}: real tree is not pinnable: "
                        f"{real_ids['current']['problems']}")
    rows = []
    with tempfile.TemporaryDirectory(prefix="kama-links-grid-") as tmp:
        for name, klass, mutate in cells:
            mdir = Path(tmp) / name
            mirror(tree, mdir)
            mserver = mdir / SERVER
            for arm, m in modules.items():
                if identity(m, mserver, arm == "current")[0] != real_ids[arm]:
                    raise EvalError(f"mirror identity differs from {tree} ({arm})")
            mutate(mdir)
            row = {"cell": name, "class": klass, "expect_change": klass != "null"}
            for arm, m in modules.items():
                ident, mtree, mlinks = identity(m, mserver, arm == "current")
                row[arm] = {"changed": ident != real_ids[arm]}
                if arm == "current":
                    row[arm]["refused"] = bool(ident["problems"])
                    row[arm]["gate_chain_problems"] = gate_problems(
                        gate, mtree, mlinks)
            rows.append(row)
            for root, dirs, files in os.walk(mdir):
                for entry in dirs + files:
                    p = os.path.join(root, entry)
                    if not os.path.islink(p):
                        os.chmod(p, 0o755)
            shutil.rmtree(mdir)
    summary = {}
    for arm in modules:
        wrong = [r["cell"] for r in rows
                 if r[arm]["changed"] != r["expect_change"]]
        by = {k: {"cells": sum(r["class"] == k for r in rows),
                  "changed": sum(r[arm]["changed"] for r in rows
                                 if r["class"] == k)} for k in CLASSES}
        summary[arm] = {"by_class": by, "wrong": wrong,
                        "status": "pass" if not wrong else "fail"}
    ok = all(summary[a]["status"] == "pass" for a in modules)
    if "current" in modules:
        null = [r for r in rows if r["class"] == "null"]
        clean = all(not r["current"]["gate_chain_problems"] for r in null)
        summary["current"]["real_tree_gate_clean"] = clean
        ok = ok and clean
    if len(modules) == 2:
        same = (real_ids["frozen"]["install_tree_sha256"]
                == real_ids["current"]["install_tree_sha256"])
        summary["back_compat_install_tree_sha256_equal"] = same
        ok = ok and same
    doc = {"tree": str(tree), "frozen_rev": FROZEN_REV, "arms": list(modules),
           "sonames": list(sonames),
           "current_sources_sha256": {
               PRODUCER: sha256_path(lane / PRODUCER),
               "tests/llamacpp-live/check-receipt.py": sha256_path(GATE)},
           "real_identity": real_ids, "summary": summary, "cells": rows}
    return (0 if ok else 1), doc


def render(doc):
    out = []
    for r in doc["cells"]:
        parts = [f"{r['cell']:<40} class={r['class']:<7}"]
        for arm in doc["arms"]:
            word = "changed" if r[arm]["changed"] else "same"
            if r[arm].get("refused"):
                word += "+refused"
            parts.append(f"{arm}={word}")
        if "current" in r and r["current"]["gate_chain_problems"]:
            parts.append("gate=" + ";".join(
                f"{k}:{v}" for k, v in r["current"]["gate_chain_problems"].items()))
        out.append(" ".join(parts))
    for arm in doc["arms"]:
        s = doc["summary"][arm]
        by = " ".join(f"{k}={v['changed']}/{v['cells']}"
                      for k, v in s["by_class"].items())
        extra = (f" real_tree_gate_clean={s['real_tree_gate_clean']}"
                 if "real_tree_gate_clean" in s else "")
        out.append(f"summary arm={arm} {by} wrong={len(s['wrong'])}{extra} "
                   f"status={s['status']}")
    if "back_compat_install_tree_sha256_equal" in doc["summary"]:
        out.append("back_compat install_tree_sha256 equal="
                   f"{doc['summary']['back_compat_install_tree_sha256_equal']}")
    return "\n".join(out)


def selftest():
    """Synthetic soname tree: frozen misses link/subdir cells, current
    catches all; missing tree/soname and unpinnable real trees are errors."""
    checks = []

    def is_error(fn):
        try:
            fn()
        except EvalError:
            return True
        return False

    sonames = ("libggml.so.0", "libllama.so.0")
    with tempfile.TemporaryDirectory(prefix="kama-links-selftest-") as tmp:
        t = Path(tmp) / "tree"
        t.mkdir()
        for name, body in ((SERVER, b"server"), ("libllama.so.0.7.0", b"lib"),
                           ("libggml.so.0.27.0", b"ggml"), ("LICENSE", b"l")):
            (t / name).write_bytes(body)
        os.chmod(t / SERVER, 0o755)
        os.symlink("libllama.so.0.7.0", t / "libllama.so.0")
        os.symlink("libllama.so.0", t / "libllama.so")
        os.symlink("libggml.so.0.27.0", t / "libggml.so.0")
        alias = Path(tmp) / "alias"
        os.symlink(t, alias)
        rc, doc = run(alias, ("frozen", "current"), sonames=sonames)
        fz, cu = doc["summary"]["frozen"], doc["summary"]["current"]
        checks.append(("frozen-misses-link-and-subdir",
                       fz["by_class"]["link"]["changed"] == 0
                       and fz["by_class"]["subdir"]["changed"] == 0))
        checks.append(("current-catches-all-via-symlinked-tree",
                       cu["status"] == "pass"))
        checks.append(("controls-both-arms",
                       fz["by_class"]["regular"]["changed"] == 3
                       and fz["by_class"]["type"]["changed"] == 1
                       and cu["by_class"]["regular"]["changed"] == 3))
        checks.append(("null-quiet", fz["by_class"]["null"]["changed"] == 0
                       and cu["by_class"]["null"]["changed"] == 0))
        checks.append(("combined-exit-1-because-frozen", rc == 1))
        rows = {r["cell"]: r["current"] for r in doc["cells"]}
        checks.append(("subdir-refused", rows["subdir-hwcaps-shadow"]["refused"]))
        checks.append(("gate-flags-dangling-outside-loop", all(
            rows[c]["gate_chain_problems"] for c in
            ("link-dangling", "link-absolute-outside", "link-loop"))))
        checks.append(("real-tree-gate-clean", cu["real_tree_gate_clean"]))
        rc_cur, _ = run(t, ("current",), sonames=sonames)
        checks.append(("current-only-exit-0", rc_cur == 0))
        checks.append(("missing-tree-error", is_error(
            lambda: run(Path(tmp) / "nope", ("current",), sonames=sonames))))
        checks.append(("missing-soname-error", is_error(
            lambda: run(t, ("current",), sonames=sonames + ("libx.so.0",)))))
        (t / "glibc-hwcaps").mkdir()
        checks.append(("unpinnable-real-tree-error", is_error(
            lambda: run(t, ("current",), sonames=sonames))))
        (t / "glibc-hwcaps").rmdir()
        os.unlink(t / "libggml.so.0")
        os.symlink("libggml.so.9", t / "libggml.so.0")
        rc_bad, _ = run(t, ("current",), sonames=("libllama.so.0",))
        checks.append(("dangling-real-tree-fails", rc_bad == 1))
    for name, ok in checks:
        print(f"{'ok' if ok else 'FAIL'} {name}")
    failed = sum(not ok for _, ok in checks)
    print(f"selftest cases={len(checks)} failed={failed}")
    return 0 if not failed else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tree", default=str(DEFAULT_TREE))
    ap.add_argument("--arm", choices=("current", "frozen", "both"),
                    default="current")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    arms = ("frozen", "current") if args.arm == "both" else (args.arm,)
    try:
        if args.selftest:
            return selftest()
        rc, doc = run(args.tree, arms)
        print(json.dumps(doc, indent=1, sort_keys=True) if args.json
              else render(doc), flush=True)
        return rc
    except Exception as exc:  # evaluation boundary: never a verdict
        try:
            print(f"could-not-evaluate: {type(exc).__name__}: {exc}",
                  file=sys.stderr)
        except OSError:
            pass
        return 2


if __name__ == "__main__":
    sys.exit(main())
