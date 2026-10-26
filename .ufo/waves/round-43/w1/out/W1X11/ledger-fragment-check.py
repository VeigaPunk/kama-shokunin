#!/usr/bin/env python3
"""ledger-fragment-check.py - pre-flight check of W1X11's hexrun ledger fragment.

NOT the frozen counter. It re-implements only the ledger rules printed in
tools/round43-hexrun-audit.py's docstring (classes lane_oid / md5_blob /
upstream / unverifiable / wrong, first match wins) and scores the nine tokens
assigned to seat W1X11, so the fragment can be shown to classify as intended
before the lane's tools/hexrun-census.py (round-43 C2) exists to read it.

--preflight-root mirrors the future repo root for evidence blobs that are
delivered but not yet committed (reported as preflight, never as committed).
"""
from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys

LEDGER_HDR = "token\tclass\trepo\tevidence\tcorrect\tverified-at\tnote"
TOKENS = [
    "61e82ee22dc89292175c5431f1ed6dc1",
    "860f26ac05938cdfc1a8816eff1570b4",
    "932ea3dc365e066e740731cf6a939506",
    "87eb156b7cc36e98f3cbfb37c00f5351",
    "00000000000000000000000001000000",
    "00000000000000000000000000000000",
    "f7a779ba0a3544dc9e3673c7eb0b3d77",
    "35ce313293052f8362e0829e7512bc9bc3d336c",
    "3ad0df68e8423a3b1b99d4e3b8d8c6271f7a4f4c96d3a5ad4e0a85a991ce234ff",
]


def git(repo: str, *args: str, binary: bool = False, inp: bytes | None = None):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, input=inp)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout if binary else p.stdout.decode(errors="replace")


def token_shape(t: str) -> bool:
    return 32 <= len(t) <= 127 and len(t) != 64 and all(c in "0123456789abcdef" for c in t)


def tip_blobs(repo: str, rev: str):
    out = git(repo, "ls-tree", "-r", "-z", rev)
    sha_paths = []
    for rec in out.split("\0"):
        if not rec:
            continue
        meta, path = rec.split("\t", 1)
        mode, typ, sha = meta.split()
        if typ == "blob":
            sha_paths.append((sha, path, mode))
    return sha_paths


def md5_set(repo: str, rev: str) -> set[str]:
    shas = [s for s, _, m in tip_blobs(repo, rev) if m in ("100644", "100755")]
    p = subprocess.Popen(["git", "-C", repo, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    assert p.stdin and p.stdout

    def feed():
        for s in shas:
            p.stdin.write((s + "\n").encode())
        p.stdin.close()

    import threading

    threading.Thread(target=feed).start()
    out = set()
    for _ in shas:
        hdr = p.stdout.readline().split()
        size = int(hdr[2])
        out.add(hashlib.md5(p.stdout.read(size)).hexdigest())
        p.stdout.read(1)
    p.wait()
    return out


def load_ledger(path: str):
    rows, bad = {}, []
    with open(path, encoding="utf-8") as fh:
        head = fh.readline().rstrip("\n")
        if head != LEDGER_HDR:
            bad.append(f"header mismatch: {head!r}")
        for n, line in enumerate(fh, 2):
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 7:
                bad.append(f"line {n}: {len(parts)} cells, want 7")
                continue
            tok = parts[0]
            if tok in rows:
                bad.append(f"line {n}: duplicated token {tok}")
            rows[tok] = dict(zip(["token", "class", "repo", "evidence", "correct", "verified", "note"], parts))
    return rows, bad


def classify(tok, repo, rev, rows, md5s, oids, preflight_root, trail):
    if len(tok) == 40:
        if oids.get(tok) == "present":
            return "lane_oid"
    if len(tok) == 32 and tok in md5s:
        return "md5_blob"
    row = rows.get(tok)
    if row is None:
        return "unknown"
    cls = row["class"]
    if cls == "upstream":
        ev = row["evidence"]
        data = None
        try:
            data = git(repo, "cat-file", "-p", f"{rev}:{ev}", binary=True)
            trail.append(f"{tok}: evidence {ev} read at {rev} (committed)")
        except RuntimeError:
            if preflight_root:
                p = os.path.join(preflight_root, ev)
                if os.path.isfile(p):
                    data = open(p, "rb").read()
                    trail.append(f"{tok}: evidence {ev} read from preflight root (UNCOMMITTED)")
        if data is None:
            trail.append(f"{tok}: evidence {ev or '<empty>'} not found")
            return "ledger_bad"
        ok = tok.encode() in data and row["repo"].encode() in data
        trail.append(f"{tok}: evidence contains token={tok.encode() in data} repo_text={row['repo'].encode() in data}")
        return "upstream_ok" if ok and row["repo"] else "ledger_bad"
    if cls == "unverifiable":
        ok = len(row["note"]) >= 10
        trail.append(f"{tok}: note length {len(row['note'])}")
        return "unverifiable" if ok else "ledger_bad"
    if cls == "wrong":
        cor = row["correct"]
        good_shape = cor != tok and token_shape(cor)
        same8 = cor[:8] == tok[:8]
        inner = classify(cor, repo, rev, rows, md5s, oids, preflight_root, trail) if good_shape else "none"
        ok = good_shape and same8 and inner in ("lane_oid", "md5_blob", "upstream_ok")
        trail.append(f"{tok}: correct {cor[:12]}.. shape={good_shape} first8={same8} class={inner}")
        return "wrong_flagged" if ok else "ledger_bad"
    trail.append(f"{tok}: unknown class {cls!r}")
    return "ledger_bad"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--rev", default="HEAD")
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--preflight-root", default=None)
    ap.add_argument("--tokens", default=None, help="file with one token per line; default the seat's nine")
    a = ap.parse_args()
    rows, bad = load_ledger(a.ledger)
    trail: list[str] = []
    toks = TOKENS
    if a.tokens:
        toks = [l.strip() for l in open(a.tokens) if l.strip()]
    md5s = md5_set(a.repo, a.rev)
    oids = {}
    forty = [t for t in toks if len(t) == 40]
    if forty:
        r = subprocess.run(["git", "-C", a.repo, "cat-file", "--batch-check"], input="\n".join(forty) + "\n",
                           capture_output=True, text=True)
        for line in r.stdout.splitlines():
            oids[line.split()[0]] = "missing" if "missing" in line else "present"
    cnt = {}
    for t in toks:
        c = classify(t, a.repo, a.rev, rows, md5s, oids, a.preflight_root, trail)
        cnt[c] = cnt.get(c, 0) + 1
        print(f"{t}\t{c}")
    order = ["lane_oid", "md5_blob", "upstream_ok", "unverifiable", "wrong_flagged", "ledger_bad", "unknown"]
    print("tokens={} distinct={} ".format(len(toks), len(set(toks)))
          + " ".join(f"{k}={cnt.get(k, 0)}" for k in order))
    for b in bad:
        print(f"ledger-defect: {b}")
    for t in trail:
        print(f"detail: {t}")
    ok = not bad and "ledger_bad=0" in " ".join(f"{k}={cnt.get(k, 0)}" for k in order) \
        and "unknown=0" in " ".join(f"{k}={cnt.get(k, 0)}" for k in order)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
