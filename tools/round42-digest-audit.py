#!/usr/bin/env python3
"""round42-digest-audit.py - kama round-42 C2 (operability, capability) counter.

Question: at a revision, does the lane hold a working digest ledger - a tool
that finds every full SHA-256 cited in the lane's documents and classifies it,
so that no cited digest is unexplained?

Frozen tool contract (tools/digest-ledger.py):
  documents  tracked files at the revision whose names end .md or .tsv, except
             paths under .ufo/ and registry/digest-ledger.tsv itself. In --dir
             mode: the same suffix rule over every regular file under DIR,
             paths relative to DIR, except .ufo/ and registry/digest-ledger.tsv.
  token      a 64-char lower-case hex run not adjacent to another hex char
             (regex (?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])).  Distinct tokens
             are counted once.
  blob set   SHA-256 of every blob reachable from the revision (git mode:
             `git rev-list --objects REV` blobs), or of every regular file
             under DIR (--dir mode).
  ledger     registry/digest-ledger.tsv (TSV, header
             `digest class subject path correct verified-at note` separated by
             TABs; absent file = empty ledger).  classes:
               external      digest of an artifact outside the revision.  If
                             `path` is non-empty and the file exists, its
                             SHA-256 must equal digest (else ledger_bad); if
                             the file is missing the row counts external_absent.
               unverifiable  no way to re-hash here; `note` must be non-empty
                             (else ledger_bad).
               wrong         a known-wrong cited digest; `correct` must be a
                             64-hex digest that is in the blob set and shares
                             its first 8 chars with `digest` (else ledger_bad).
  classify each token (first match wins):
    blob            token in blob set
    wrong_unflagged token not in blob set, not in ledger, but its first 8 chars
                    equal the first 8 chars of some blob-set digest
    unknown         token not in blob set and not in ledger
    in ledger       by class: external -> external_ok (path exists and equals)
                    | external_absent | ledger_bad; unverifiable ->
                    unverifiable | ledger_bad; wrong -> wrong_flagged |
                    ledger_bad
  summary line:
    tokens=T blob=B external_ok=E external_absent=A unverifiable=U wrong_flagged=W ledger_bad=L wrong_unflagged=X unknown=K
  exit: 2 on a usage or git error; 1 if L+X+K > 0; else 0.
  command: python3 tools/digest-ledger.py scan (--repo R --rev REV | --dir DIR)

Legs (each 0/1):
  tool       tools/digest-ledger.py exists at --tip.
  contract   every one of CASES randomized offline --dir fixture cases (seeded;
             the seed is printed) gives a byte-equal summary line and equal exit
             code to this file's reference implementation.
  live       `scan --repo <repo> --rev <tip>` equals the reference computed
             here for the same revision, with ledger_bad=0 wrong_unflagged=0
             unknown=0 and external_ok >= 4 (the four tokens the base tree cites
             whose bytes sit on this host: the b11755 release archive, its
             libllama-server-impl.so, the shokuknow staged package and the
             round-35 Dockerfile fetch).
  hygiene    running the two round-41 counters at --tip with TMPDIR set to an
             empty private directory leaves that directory empty afterwards.
  capability the highest-numbered "Capabilities - canonical list as of round N"
             table in SCORECARD.md has a row whose first cell is `digest-ledger`
             and whose evidence cell contains `tools/digest-ledger.py`.
met = all five legs 1.

Output: `tool=T contract=C live=L hygiene=H capability=K met=True|False seed=N`,
a `live-reference:` line, then `detail:` lines.  Exit 0 met, 1 not met, 2 could
not evaluate.  Read-only on --repo; every temporary directory is removed.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile

CASES = 8
TOKEN = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
LEDGER = "registry/digest-ledger.tsv"
HDR = "digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote"


def git(repo, *args, binary=False):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout if binary else p.stdout.decode()


def doc_ok(path):
    if path.startswith(".ufo/") or path == LEDGER:
        return False
    return path.endswith((".md", ".tsv"))


def parse_ledger(text):
    rows = {}
    for i, l in enumerate(text.split("\n")):
        if not l or i == 0 and l.startswith("digest\t"):
            continue
        c = l.split("\t")
        c += [""] * (7 - len(c))
        rows[c[0]] = dict(cls=c[1], path=c[3], correct=c[4], note=c[6])
    return rows


def classify(tokens, blobs, ledger):
    n = dict(tokens=len(tokens), blob=0, external_ok=0, external_absent=0, unverifiable=0,
             wrong_flagged=0, ledger_bad=0, wrong_unflagged=0, unknown=0)
    pref = {b[:8] for b in blobs}
    for t in sorted(tokens):
        if t in blobs:
            n["blob"] += 1
        elif t in ledger:
            r = ledger[t]
            if r["cls"] == "external":
                if r["path"] and os.path.isfile(r["path"]):
                    h = hashlib.sha256(open(r["path"], "rb").read()).hexdigest()
                    n["external_ok" if h == t else "ledger_bad"] += 1
                else:
                    n["external_absent"] += 1
            elif r["cls"] == "unverifiable":
                n["unverifiable" if r["note"].strip() else "ledger_bad"] += 1
            elif r["cls"] == "wrong":
                c = r["correct"]
                good = bool(re.fullmatch(r"[0-9a-f]{64}", c)) and c in blobs and c[:8] == t[:8]
                n["wrong_flagged" if good else "ledger_bad"] += 1
            else:
                n["ledger_bad"] += 1
        elif t[:8] in pref:
            n["wrong_unflagged"] += 1
        else:
            n["unknown"] += 1
    return n


def summary(n):
    return ("tokens={tokens} blob={blob} external_ok={external_ok} external_absent={external_absent} "
            "unverifiable={unverifiable} wrong_flagged={wrong_flagged} ledger_bad={ledger_bad} "
            "wrong_unflagged={wrong_unflagged} unknown={unknown}").format(**n)


def exit_of(n):
    return 1 if n["ledger_bad"] + n["wrong_unflagged"] + n["unknown"] > 0 else 0


def ref_dir(d):
    tokens, blobs = set(), set()
    ledger = {}
    for root, _, files in os.walk(d):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, d)
            if not os.path.isfile(full) or os.path.islink(full):
                continue
            data = open(full, "rb").read()
            blobs.add(hashlib.sha256(data).hexdigest())
            if rel == LEDGER:
                ledger = parse_ledger(data.decode(errors="replace"))
            elif doc_ok(rel):
                tokens |= set(TOKEN.findall(data.decode(errors="replace")))
    return classify(tokens, blobs, ledger)


def ref_git(repo, rev):
    rev = git(repo, "rev-parse", "--verify", f"{rev}^{{commit}}").strip()
    objs = git(repo, "rev-list", "--objects", rev).split("\n")
    tokens, blobs, ledger = set(), set(), {}
    names = {}
    for l in objs:
        if not l:
            continue
        oid, _, name = l.partition(" ")
        names[oid] = name
    p = subprocess.run(["git", "-C", repo, "cat-file", "--batch"], input="".join(o + "\n" for o in names).encode(),
                       capture_output=True)
    buf, i = p.stdout, 0
    while i < len(buf):
        j = buf.index(b"\n", i)
        oid, typ, size = buf[i:j].decode().split()
        size = int(size)
        data = buf[j + 1:j + 1 + size]
        i = j + 1 + size + 1
        if typ != "blob":
            continue
        blobs.add(hashlib.sha256(data).hexdigest())
    tree = git(repo, "ls-tree", "-r", "--name-only", "-z", rev).split("\0")
    for path in tree:
        if not path:
            continue
        if path == LEDGER:
            ledger = parse_ledger(git(repo, "cat-file", "-p", f"{rev}:{path}"))
        elif doc_ok(path):
            tokens |= set(TOKEN.findall(git(repo, "cat-file", "-p", f"{rev}:{path}")))
    return classify(tokens, blobs, ledger)


def rand_hex(rng):
    return "".join(rng.choice("0123456789abcdef") for _ in range(64))


def make_case(rng, d, i):
    """Write a fixture directory; returns nothing (the reference reads it back)."""
    os.makedirs(os.path.join(d, "corpus"), exist_ok=True)
    os.makedirs(os.path.join(d, "registry"), exist_ok=True)
    os.makedirs(os.path.join(d, ".ufo"), exist_ok=True)
    files = {}
    payloads = {}
    for k in range(rng.randint(1, 4)):
        body = f"payload {i}-{k} {rng.random()}\n".encode()
        name = f"data{k}.bin"
        payloads[name] = body
        with open(os.path.join(d, name), "wb") as f:
            f.write(body)
    ext_file = os.path.join(d, "outside.bin")
    with open(ext_file, "wb") as f:
        f.write(b"external " + str(rng.random()).encode())
    ext_digest = hashlib.sha256(open(ext_file, "rb").read()).hexdigest()
    os.remove(ext_file) if rng.random() < 0.3 else None
    tokens = []
    for body in payloads.values():
        if rng.random() < 0.8:
            tokens.append(hashlib.sha256(body).hexdigest())
    wrong_rows = []
    for _ in range(rng.randint(0, 2)):
        good = hashlib.sha256(rng.choice(list(payloads.values()))).hexdigest()
        bad = good[:8] + rand_hex(rng)[8:]
        tokens.append(bad)
        if rng.random() < 0.6:
            wrong_rows.append((bad, "wrong", "w", "", good if rng.random() < 0.8 else rand_hex(rng), "", ""))
    for _ in range(rng.randint(0, 2)):
        tokens.append(rand_hex(rng))
    ext_row = None
    if rng.random() < 0.7:
        tokens.append(ext_digest)
        pth = ext_file if rng.random() < 0.7 else ""
        ext_row = (ext_digest, "external", "x", pth, "", "", "")
        if rng.random() < 0.2:
            ext_row = (rand_hex(rng), "external", "x", ext_file, "", "", "")
            tokens.append(ext_row[0])
    unv = None
    if rng.random() < 0.5:
        u = rand_hex(rng)
        tokens.append(u)
        unv = (u, "unverifiable", "u", "", "", "", "no host copy" if rng.random() < 0.8 else "")
    rng.shuffle(tokens)
    chunks = [" ".join(tokens[x::2]) for x in (0, 1)]
    with open(os.path.join(d, "corpus", "a.md"), "w") as f:
        f.write("# a\n" + chunks[0] + "\n`" + (tokens[0] if tokens else "") + "x`\n")
    with open(os.path.join(d, "b.tsv"), "w") as f:
        f.write(chunks[1] + "\n")
    with open(os.path.join(d, ".ufo", "hidden.md"), "w") as f:
        f.write(rand_hex(rng) + "\n")
    rows = list(wrong_rows) + [r for r in (ext_row, unv) if r]
    if rows or rng.random() < 0.3:
        with open(os.path.join(d, LEDGER), "w") as f:
            f.write(HDR + "\n")
            for r in rows:
                f.write("\t".join(r) + "\n")


def run_tool(export, args, timeout=120):
    p = subprocess.run([sys.executable, "tools/digest-ledger.py", *args], cwd=export, capture_output=True,
                       text=True, timeout=timeout)
    return p.stdout, p.returncode, p.stderr


def highest_canonical(text):
    best, rows = -1, []
    lines = text.split("\n")
    for i, l in enumerate(lines):
        m = re.search(r"canonical list as of round\s+(\d+)\*\*", l, re.I)
        if m and int(m.group(1)) > best:
            tbl = []
            for ln in lines[i + 1:]:
                if ln.startswith("|"):
                    tbl.append([c.strip() for c in ln.strip().strip("|").split("|")])
                elif tbl:
                    break
            best, rows = int(m.group(1)), tbl[2:]
    return best, rows


def evaluate(repo, tip, seed):
    tip = git(repo, "rev-parse", "--verify", f"{tip}^{{commit}}").strip()
    details = []
    legs = dict(tool=0, contract=0, live=0, hygiene=0, capability=0)
    live_ref = ""
    with tempfile.TemporaryDirectory(prefix="r42c2-") as export:
        subprocess.run(["tar", "-x", "-C", export], input=git(repo, "archive", "--format=tar", tip, binary=True),
                       check=True)
        if os.path.isfile(os.path.join(export, "tools/digest-ledger.py")):
            legs["tool"] = 1
        else:
            details.append("detail: tools/digest-ledger.py absent")
        if legs["tool"]:
            rng = random.Random(seed)
            ok = True
            for i in range(CASES):
                with tempfile.TemporaryDirectory(prefix=f"case{i}-", dir=export) as d:
                    make_case(rng, d, i)
                    want = ref_dir(d)
                    try:
                        out, code, err = run_tool(export, ["scan", "--dir", d])
                    except subprocess.TimeoutExpired:
                        out, code, err = "", None, "timeout"
                    if out.strip() != summary(want) or code != exit_of(want):
                        ok = False
                        details.append(f"detail: contract case {i}: want exit {exit_of(want)} {summary(want)!r} "
                                       f"got exit {code} {out.strip()[:200]!r} {err.strip()[:120]}")
            legs["contract"] = int(ok)
            ref = ref_git(repo, tip)
            live_ref = summary(ref) + f" exit={exit_of(ref)}"
            try:
                out, code, err = run_tool(export, ["scan", "--repo", repo, "--rev", tip], timeout=300)
            except subprocess.TimeoutExpired:
                out, code, err = "", None, "timeout"
            good = (out.strip() == summary(ref) and code == exit_of(ref) and ref["ledger_bad"] == 0
                    and ref["wrong_unflagged"] == 0 and ref["unknown"] == 0 and ref["external_ok"] >= 4)
            legs["live"] = int(good)
            if not good:
                details.append(f"detail: live: reference {live_ref}; tool exit {code} {out.strip()[:240]!r} {err.strip()[:120]}")
    # hygiene: round-41 counters leave their private TMPDIR empty
    with tempfile.TemporaryDirectory(prefix="r42c2-hyg-") as priv, tempfile.TemporaryDirectory(prefix="r42c2-src-") as src:
        subprocess.run(["tar", "-x", "-C", src], input=git(repo, "archive", "--format=tar", tip, binary=True), check=True)
        env = dict(os.environ, TMPDIR=priv)
        for tool in ("tools/round41-scorecard-reconcile.py", "tools/round41-pinwatch-audit.py"):
            if not os.path.isfile(os.path.join(src, tool)):
                details.append(f"detail: hygiene: {tool} absent at tip")
                continue
            try:
                subprocess.run([sys.executable, tool, "--repo", repo, "--tip", tip], cwd=src, env=env,
                               capture_output=True, timeout=900)
            except subprocess.TimeoutExpired:
                details.append(f"detail: hygiene: {tool} timeout")
        left = sorted(os.listdir(priv))
        legs["hygiene"] = int(not left and all(os.path.isfile(os.path.join(src, t)) for t in (
            "tools/round41-scorecard-reconcile.py", "tools/round41-pinwatch-audit.py")))
        if left:
            details.append(f"detail: hygiene: {len(left)} leaked temp entries after the round-41 counters: {left[:4]}")
    # capability
    sc = subprocess.run(["git", "-C", repo, "cat-file", "-p", f"{tip}:SCORECARD.md"], capture_output=True, text=True).stdout
    n, rows = highest_canonical(sc)
    for r in rows:
        if len(r) >= 3 and r[0].strip("` *") == "digest-ledger" and "tools/digest-ledger.py" in r[2]:
            legs["capability"] = 1
    if not legs["capability"]:
        details.append(f"detail: no digest-ledger row in canonical list as of round {n}")
    return tip, legs, live_ref, details


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--tip", default="HEAD")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out")
    a = ap.parse_args()
    seed = a.seed if a.seed is not None else random.SystemRandom().randrange(1, 2**31)
    try:
        tip, legs, live_ref, details = evaluate(os.path.abspath(a.repo), a.tip, seed)
    except (RuntimeError, subprocess.CalledProcessError) as e:
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        return 2
    met = all(legs.values())
    out = "\n".join([f"tip={tip}",
                     "tool={tool} contract={contract} live={live} hygiene={hygiene} capability={capability} "
                     "met={m} seed={s}".format(m=met, s=seed, **legs),
                     f"live-reference: {live_ref}", *details]) + "\n"
    sys.stdout.write(out)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w") as f:
            f.write(out)
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
