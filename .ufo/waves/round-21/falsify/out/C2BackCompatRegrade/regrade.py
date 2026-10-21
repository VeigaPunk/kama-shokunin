#!/usr/bin/env python3
"""C2 back-compat regrade (round 21, FALSIFY seat C2BackCompatRegrade).

Every committed JSON under .ufo/waves/ at a6617149 that carries the
kama-llamacpp-live marker is run through tests/llamacpp-live/check-receipt.py
of 7a6bc911 and of a6617149, with no extra flags. The lane is read-only: blobs
come from `git cat-file` on a scratch clone, receipts are mirrored into scratch
under their committed relative paths, and each gate runs with cwd set to the
mirror so both arms print the same repo-relative path.
"""
import collections
import concurrent.futures as cf
import hashlib
import json
import os
import shutil
import subprocess
import sys

SCRATCH = "/tmp/kama-r21-C2BackCompatRegrade"
LANE = os.path.join(SCRATCH, "lane")  # scratch clone, detached at a6617149
G7 = os.path.join(SCRATCH, "g7")  # scratch clone, detached at 7a6bc911
MIRROR = os.path.join(SCRATCH, "rx")  # committed receipt bytes, committed relative paths
A6 = "a6617149722c73d90e142fbdc8154d6967055f7e"
B7 = "7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d"
WORK = "/home/vgpnk/Projects/shokunin/kama-shokunin"
OUT = os.path.join(WORK, ".ufo/waves/round-21/falsify/out/C2BackCompatRegrade")
LIVE = ".ufo/waves/round-21/runs/b76727f3/live-receipt.json"
GATE = "tests/llamacpp-live/check-receipt.py"
MARKER = b"kama-llamacpp-live/"
MAX_CHARS = 1500


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"git {args} exit={p.returncode}: {p.stderr.decode(errors='replace')}")
    return p.stdout


def json_blobs(repo, commit):
    raw = git(repo, "ls-tree", "-r", "-z", "--full-tree", commit, "--", ".ufo/waves")
    blobs = {}
    for rec in raw.split(b"\0"):
        if not rec:
            continue
        meta, _, name = rec.partition(b"\t")
        _mode, otype, sha = meta.decode().split()
        path = name.decode("utf-8")
        if otype == "blob" and path.endswith(".json"):
            blobs[path] = sha
    return blobs


def classify(data):
    try:
        obj = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return ("unparseable-marker" if MARKER in data else "unparseable"), None
    if isinstance(obj, dict) and str(obj.get("schema", "")).startswith("kama-llamacpp-live/"):
        return "receipt", obj
    if MARKER in data:
        return "marker-nonreceipt", obj
    return "other", obj


def fields(obj):
    if not isinstance(obj, dict):
        return "", "", ""
    server = obj.get("server")
    links = ""
    if isinstance(server, dict):
        links = ";".join(sorted(k for k in server if k.startswith("install_links")))
    return str(obj.get("schema", "")), str(obj.get("outcome", "")), links


def run_gate(repo, rel):
    p = subprocess.run(
        [sys.executable, "-B", os.path.join(repo, GATE), rel],
        cwd=MIRROR, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=300)
    return p.returncode, p.stdout, p.stderr


def first(s):
    ls = s.splitlines()
    return ls[0] if ls else "(no stdout)"


def problems(s):
    return [ln[4:] for ln in s.splitlines() if ln.startswith("  - ")]


def cell(v):
    return str(v).replace("\t", " ").replace("\n", " ").replace("\r", " ")


def token(line):
    return line.split(" ", 1)[0] if line else "(none)"


def main():
    os.makedirs(OUT, exist_ok=True)
    a6 = json_blobs(LANE, A6)
    b7 = json_blobs(LANE, B7)
    dropped = sorted(p for p in b7 if p not in a6)
    modified = sorted(p for p in b7 if p in a6 and a6[p] != b7[p])
    added = sorted(p for p in a6 if p not in b7)

    shutil.rmtree(MIRROR, ignore_errors=True)
    rows, unmarked = [], 0
    for path in sorted(a6):
        data = git(LANE, "cat-file", "blob", a6[path])
        dst = os.path.join(MIRROR, path)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as fh:
            fh.write(data)
        kind, obj = classify(data)
        if kind == "other":
            unmarked += 1
            continue
        schema, outcome, links = fields(obj)
        rows.append({
            "path": path, "kind": kind, "blob": a6[path],
            "sha256": hashlib.sha256(data).hexdigest(),
            "schema": schema, "outcome": outcome, "install_links_keys": links,
            "in_7a": path in b7, "added_in_a6": path not in b7,
        })

    gate_meta = {}
    for name, repo, commit in (("g7", G7, B7), ("a6", LANE, A6)):
        head = git(repo, "rev-parse", "HEAD").decode().strip()
        blob = git(repo, "rev-parse", f"{commit}:{GATE}").decode().strip()
        with open(os.path.join(repo, GATE), "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        gate_meta[name] = (head, blob, digest)
    assert gate_meta["g7"][0] == B7, gate_meta["g7"]
    assert gate_meta["a6"][0] == A6, gate_meta["a6"]

    results = {}
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {}
        for r in rows:
            futs[ex.submit(run_gate, G7, r["path"])] = (r["path"], "g7")
            futs[ex.submit(run_gate, LANE, r["path"])] = (r["path"], "a6")
        for fut in cf.as_completed(futs):
            results[futs[fut]] = fut.result()

    for r in rows:
        rc7, out7, err7 = results[(r["path"], "g7")]
        rca, outa, erra = results[(r["path"], "a6")]
        if rc7 != rca:
            change = "EXIT"
        elif out7 != outa:
            change = "STDOUT"
        elif err7 != erra:
            change = "STDERR"
        else:
            change = "none"
        r.update(
            g7_exit=rc7, g7_line=first(out7), a6_exit=rca, a6_line=first(outa),
            verdict_changed=first(out7) != first(outa), change=change,
            g7_problems=" | ".join(problems(out7))[:400],
            a6_problems=" | ".join(problems(outa))[:400],
            g7_err=first(err7)[:200], a6_err=first(erra)[:200])

    cols = ["path", "kind", "schema", "outcome", "install_links_keys", "in_7a",
            "added_in_a6", "sha256", "g7_exit", "g7_line", "a6_exit", "a6_line",
            "change", "verdict_changed", "g7_problems", "a6_problems",
            "g7_err", "a6_err"]
    with open(os.path.join(OUT, "regrade-matrix.tsv"), "w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(cell(r[c]) for c in cols) + "\n")

    detail = []
    for r in rows:
        if r["change"] == "none":
            continue
        rc7, out7, err7 = results[(r["path"], "g7")]
        rca, outa, erra = results[(r["path"], "a6")]
        detail.append(
            f"== {r['path']} change={r['change']} sha256={r['sha256']}\n"
            f"-- gate 7a6bc911 exit={rc7} stdout:\n{out7[:MAX_CHARS]}"
            f"stderr:\n{err7[:MAX_CHARS]}"
            f"-- gate a6617149 exit={rca} stdout:\n{outa[:MAX_CHARS]}"
            f"stderr:\n{erra[:MAX_CHARS]}\n")
    with open(os.path.join(OUT, "regrade-changes.txt"), "w", encoding="utf-8") as fh:
        fh.write("".join(detail) if detail else "no changes\n")

    print(f"gate g7 HEAD={gate_meta['g7'][0]} gate_blob={gate_meta['g7'][1]} "
          f"gate_sha256={gate_meta['g7'][2]}")
    print(f"gate a6 HEAD={gate_meta['a6'][0]} gate_blob={gate_meta['a6'][1]} "
          f"gate_sha256={gate_meta['a6'][2]}")
    print(f"committed .ufo/waves json: 7a={len(b7)} a6={len(a6)} added={len(added)} "
          f"modified={len(modified)} dropped={len(dropped)} unmarked_json_skipped={unmarked}")
    print("regraded kinds:", dict(collections.Counter(r["kind"] for r in rows)),
          "total:", len(rows))
    print("receipts added in a6 (not in 7a):",
          sum(1 for r in rows if r["added_in_a6"] and r["kind"] == "receipt"))
    print("g7 exits:", dict(collections.Counter(r["g7_exit"] for r in rows)))
    print("a6 exits:", dict(collections.Counter(r["a6_exit"] for r in rows)))
    print("g7 verdict tokens:", dict(collections.Counter(token(r["g7_line"]) for r in rows)))
    print("a6 verdict tokens:", dict(collections.Counter(token(r["a6_line"]) for r in rows)))
    print("change:", dict(collections.Counter(r["change"] for r in rows)),
          "verdict_changed:", sum(1 for r in rows if r["verdict_changed"]))
    legacy = [r for r in rows if r["kind"] == "receipt" and not r["install_links_keys"]]
    linked = [r for r in rows if r["kind"] == "receipt" and r["install_links_keys"]]
    print(f"receipts without server.install_links* keys: {len(legacy)} "
          f"changed={sum(1 for r in legacy if r['change'] != 'none')}")
    print(f"receipts with server.install_links* keys: {len(linked)} "
          f"changed={sum(1 for r in linked if r['change'] != 'none')}")
    for r in rows:
        if r["change"] != "none":
            print(f"CHANGE {r['change']} {r['path']} | g7 exit {r['g7_exit']}: {r['g7_line']}"
                  f" | a6 exit {r['a6_exit']}: {r['a6_line']}")
    for r in rows:
        if r["kind"] != "receipt":
            print(f"NON-RECEIPT {r['kind']} {r['path']} g7={r['g7_exit']} a6={r['a6_exit']}"
                  f" | {r['a6_line']}")
    live = [r for r in rows if r["path"] == LIVE]
    for r in live:
        print(f"LIVE {r['path']} blob_sha256={r['sha256']} schema={r['schema']} "
              f"outcome={r['outcome']} links={r['install_links_keys']}")
        print(f"LIVE g7 exit={r['g7_exit']} line={r['g7_line']} problems={r['g7_problems']!r}")
        print(f"LIVE a6 exit={r['a6_exit']} line={r['a6_line']} problems={r['a6_problems']!r}")
    with open(os.path.join(WORK, LIVE), "rb") as fh:
        wsha = hashlib.sha256(fh.read()).hexdigest()
    print(f"LIVE lane working-copy sha256={wsha} == committed blob: "
          f"{bool(live) and wsha == live[0]['sha256']}")


if __name__ == "__main__":
    main()
