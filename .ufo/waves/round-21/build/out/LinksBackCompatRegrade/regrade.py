#!/usr/bin/env python3
"""Round-21 LinksBackCompatRegrade (kama lane, executor seat).

Regrades committed kama-llamacpp-live receipts with tests/llamacpp-live/check-receipt.py
at two pinned commits, each arm run from its own scratch clone of the lane:

  base = 7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d
  work = a29bb84abbb8b4d328f5970a89e448330a3a42ac

Every committed .ufo/waves/**/*.json that contains the schema string
kama-llamacpp-live/v is run as `python3 tests/llamacpp-live/check-receipt.py RECEIPT`
(cwd = clone root, no optional flags). Committed JSON that mentions llamacpp-live
without that schema string is run the same way as a supplementary scope. Two
stray-digest probes run on a scratch copy of the first VALID schema receipt.
The lane is only cloned (read); every output is written under OUT.

Run: python3 regrade.py   (exit 0 = completed; comparison results in summary.txt)
"""
import hashlib
import json
import os
import subprocess
from collections import Counter

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
SCRATCH = "/tmp/kama-r21-LinksBackCompatRegrade"
OUT = os.path.join(LANE, ".ufo/waves/round-21/build/out/LinksBackCompatRegrade")
GATE = "tests/llamacpp-live/check-receipt.py"
GLOB = ".ufo/waves/**/*.json"
ARMS = {"base": "7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d",
        "work": "a29bb84abbb8b4d328f5970a89e448330a3a42ac"}
SCHEMA_NEEDLE = "kama-llamacpp-live/v"
MENTION_NEEDLE = "llamacpp-live"
TRACEBACK = "Traceback (most recent call last)"
PROBE_DIGEST = "1" * 64


def run(args, cwd=None, ok=(0,)):
    p = subprocess.run(args, cwd=cwd, capture_output=True, timeout=300)
    if ok is not None and p.returncode not in ok:
        raise SystemExit(f"FATAL: {' '.join(args)} exited {p.returncode}: "
                         f"{p.stderr.decode('utf-8', 'replace').strip()}")
    return p


def git(clone, *args, ok=(0,)):
    return run(["git", "-C", clone, *args], ok=ok).stdout


def text(data):
    return data.decode("utf-8", "replace")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def yn(flag):
    return "yes" if flag else "no"


def ensure_clone(name, commit):
    clone = os.path.join(SCRATCH, name)
    if not os.path.isdir(clone):
        os.makedirs(SCRATCH, exist_ok=True)
        run(["git", "clone", "-q", LANE, clone])
    if text(git(clone, "rev-parse", "HEAD")).strip() != commit:
        git(clone, "checkout", "-q", commit)
    head = text(git(clone, "rev-parse", "HEAD")).strip()
    if head != commit:
        raise SystemExit(f"FATAL: {name} HEAD {head} != {commit}")
    dirty = text(git(clone, "status", "--porcelain"))
    if dirty:
        raise SystemExit(f"FATAL: {name} clone is not clean:\n{dirty}")
    return clone


def listing(clone, commit, needle):
    out = text(git(clone, "grep", "-l", "-F", needle, commit, "--", GLOB, ok=(0, 1)))
    paths = set()
    for line in out.splitlines():
        ref, _, path = line.partition(":")
        if ref != commit:
            raise SystemExit(f"FATAL: unexpected git grep output {line!r}")
        paths.add(path)
    return sorted(paths)


def gate(clone, receipt, extra=()):
    p = run(["python3", GATE, receipt, *extra], cwd=clone, ok=None)
    return p.returncode, text(p.stdout), text(p.stderr)


def first_line(out, err):
    body = out if out.strip() else err
    lines = body.splitlines()
    return (lines[0] if lines else "<no output>").replace("\t", " ").strip()


def describe(data):
    try:
        doc = json.loads(text(data))
    except ValueError:
        return "<not-json>", "n/a"
    if not isinstance(doc, dict):
        return "<non-object>", "n/a"
    server = doc.get("server")
    has_links = isinstance(server, dict) and "install_links" in server
    return str(doc.get("schema", "<no-schema-key>")), yn(has_links)


def block(label, cmd, code, out, err):
    return (f"### {label}\n$ {cmd}   (cwd: arm clone root)\n"
            f"exit={code}\n--- stdout ---\n{out}--- stderr ---\n{err}\n")


def write_tsv(name, header, rows):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
        fh.write("\t".join(header) + "\n")
        for row in rows:
            fh.write("\t".join(str(c) for c in row) + "\n")


def differs(recs, field):
    return [r["path"] for r in recs if r["base"][field] != r["work"][field]]


def outcomes(recs, arm):
    return dict(Counter(f"exit{r[arm]['exit']}:{r[arm]['verdict'].split(' ', 1)[0]}"
                        for r in recs))


def main():
    os.makedirs(OUT, exist_ok=True)
    clones = {n: ensure_clone(n, c) for n, c in ARMS.items()}
    gate_blob = {n: text(git(clones[n], "rev-parse", f"{ARMS[n]}:{GATE}")).strip()
                 for n in ARMS}
    lists = {n: {"schema": listing(clones[n], ARMS[n], SCHEMA_NEEDLE),
                 "mention": listing(clones[n], ARMS[n], MENTION_NEEDLE)}
             for n in ARMS}
    if lists["base"] != lists["work"]:
        raise SystemExit("FATAL: committed receipt listings differ between arms")
    schema_paths = lists["base"]["schema"]
    supp_paths = sorted(set(lists["base"]["mention"]) - set(schema_paths))

    logs = {n: [] for n in ARMS}
    records = []
    for scope, paths in (("schema", schema_paths), ("mention-only", supp_paths)):
        for rel in paths:
            blobs = {n: git(clones[n], "cat-file", "blob", f"{ARMS[n]}:{rel}")
                     for n in ARMS}
            rec = {"set": scope, "path": rel,
                   "blob_sha256": sha256(blobs["base"]),
                   "blob_same": blobs["base"] == blobs["work"],
                   "worktree_ok": all(
                       sha256(read_bytes(os.path.join(clones[n], rel)))
                       == sha256(blobs[n]) for n in ARMS)}
            rec["declared"], rec["links"] = describe(blobs["base"])
            for n in ARMS:
                code, out, err = gate(clones[n], rel)
                out = out.replace(clones[n], "<CLONE>")
                err = err.replace(clones[n], "<CLONE>")
                logs[n].append(block(f"[{n}] [{scope}] {rel}",
                                     f"python3 {GATE} {rel}", code, out, err))
                rec[n] = {"exit": code, "verdict": first_line(out, err),
                          "text": f"exit={code}\n{out}{err}",
                          "crash": TRACEBACK in err}
            records.append(rec)

    schema_recs = [r for r in records if r["set"] == "schema"]
    supp_recs = [r for r in records if r["set"] == "mention-only"]

    seed = next((r for r in schema_recs if r["base"]["verdict"].startswith("VALID ")), None)
    if seed is None:
        raise SystemExit("FATAL: no VALID base receipt to seed the probes")
    doc = json.loads(text(git(clones["base"], "cat-file", "blob",
                              f"{ARMS['base']}:{seed['path']}")))
    doc["server"]["install_links_sha256"] = PROBE_DIGEST
    probe_dir = os.path.join(SCRATCH, "probes")
    os.makedirs(probe_dir, exist_ok=True)
    probe = os.path.join(probe_dir, "stray-digest.json")
    with open(probe, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1)
    probe_rows = []
    cases = (("P1 stray install_links_sha256, no pin", ()),
             ("P2 P1 + --expect-install-links-sha256",
              ("--expect-install-links-sha256", PROBE_DIGEST)))
    for label, extra in cases:
        for n in ARMS:
            code, out, err = gate(clones[n], probe, extra)
            out = out.replace(clones[n], "<CLONE>")
            err = err.replace(clones[n], "<CLONE>")
            cmd = " ".join(["python3", GATE, probe, *extra])
            logs[n].append(block(f"[{n}] [{label}]", cmd, code, out, err))
            probe_rows.append((label, n, code, first_line(out, err)))

    for n in ARMS:
        with open(os.path.join(OUT, f"run-{n}.log"), "w", encoding="utf-8") as fh:
            fh.write("".join(logs[n]))
    verdict_header = ["path", "base_verdict_line", "work_verdict_line"]
    write_tsv("regrade.tsv", verdict_header,
              [(r["path"], r["base"]["verdict"], r["work"]["verdict"])
               for r in schema_recs])
    write_tsv("regrade-mention-only.tsv", verdict_header,
              [(r["path"], r["base"]["verdict"], r["work"]["verdict"])
               for r in supp_recs])
    write_tsv("regrade-detail.tsv",
              ["set", "path", "blob_sha256", "blob_same_in_arms",
               "worktree_matches_blob", "declared_schema", "server_install_links",
               "base_exit", "work_exit", "base_traceback", "work_traceback",
               "verdict_line_identical", "output_identical"],
              [(r["set"], r["path"], r["blob_sha256"], yn(r["blob_same"]),
                yn(r["worktree_ok"]), r["declared"], r["links"],
                r["base"]["exit"], r["work"]["exit"],
                yn(r["base"]["crash"]), yn(r["work"]["crash"]),
                yn(r["base"]["verdict"] == r["work"]["verdict"]),
                yn(r["base"]["text"] == r["work"]["text"]))
               for r in records])
    write_tsv("probes.tsv", ["probe", "arm", "exit", "verdict_line"], probe_rows)

    pv = run(["python3", "--version"], ok=None)
    lines = [
        f"lane: {LANE}",
        f"arms: base={ARMS['base']} work={ARMS['work']}",
        f"gate blob: base={gate_blob['base']} work={gate_blob['work']}",
        f"interpreter: {text(pv.stdout + pv.stderr).strip()}",
        f"listing: schema-string JSON={len(schema_paths)} "
        f"mention-only JSON={len(supp_paths)} identical across arms=yes",
        f"schema scope n={len(schema_recs)}: blob identical across arms="
        f"{sum(r['blob_same'] for r in schema_recs)}; worktree matches blob="
        f"{sum(r['worktree_ok'] for r in schema_recs)}",
        f"schema scope declared schema: "
        f"{dict(Counter(r['declared'] for r in schema_recs))}",
        f"schema scope server.install_links present: "
        f"{dict(Counter(r['links'] for r in schema_recs))}",
        f"schema scope base outcomes: {outcomes(schema_recs, 'base')}",
        f"schema scope work outcomes: {outcomes(schema_recs, 'work')}",
        f"schema scope verdict-line changes: {len(differs(schema_recs, 'verdict'))} "
        f"{differs(schema_recs, 'verdict')}",
        f"schema scope output changes (stdout+stderr+exit): "
        f"{len(differs(schema_recs, 'text'))} {differs(schema_recs, 'text')}",
        f"schema scope tracebacks: base={sum(r['base']['crash'] for r in schema_recs)} "
        f"work={sum(r['work']['crash'] for r in schema_recs)}",
        f"mention-only scope n={len(supp_recs)}: verdict-line changes="
        f"{len(differs(supp_recs, 'verdict'))}; output changes="
        f"{len(differs(supp_recs, 'text'))}",
        f"mention-only base outcomes: {outcomes(supp_recs, 'base')}",
        f"mention-only work outcomes: {outcomes(supp_recs, 'work')}",
        f"mention-only tracebacks: base={sum(r['base']['crash'] for r in supp_recs)} "
        f"work={sum(r['work']['crash'] for r in supp_recs)}",
        f"probe seed: {seed['path']}",
    ] + [f"probe {label} [{n}] exit={code}: {v}" for label, n, code, v in probe_rows]
    summary = "\n".join(lines) + "\n"
    with open(os.path.join(OUT, "summary.txt"), "w", encoding="utf-8") as fh:
        fh.write(summary)
    print(summary, end="")


if __name__ == "__main__":
    main()
