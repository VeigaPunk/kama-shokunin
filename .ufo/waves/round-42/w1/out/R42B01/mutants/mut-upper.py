#!/usr/bin/env python3
"""digest-ledger.py - find every full SHA-256 the lane's documents cite and
classify it, so that no cited digest is unexplained.

Why: round 38 cited a SHA-256 for S472 that shared its first eight characters
with the real digest and hashed nothing; the outside closure found it a round
later. This tool checks identifiers mechanically (considerthese/2026-10-25.md,
proposal 1): it hashes what a document points at and says what each cited
digest is.

    digest-ledger.py scan (--repo R --rev REV | --dir DIR) [--ledger FILE] [--details]
    digest-ledger.py selftest

Documents scanned: tracked files at REV (or regular files under DIR) whose name
ends .md or .tsv, except paths under .ufo/ and registry/digest-ledger.tsv itself.
A token is a 64-character lower-case hex run not adjacent to another hex
character. The blob set is the SHA-256 of every blob reachable from REV (git
mode) or of every regular file under DIR.

Ledger: registry/digest-ledger.tsv (read from the revision or DIR; --ledger
overrides), TAB-separated, header
    digest  class  subject  path  correct  verified-at  note
classes:
    external      digest of an artifact outside the revision; when `path` names
                  an existing file its SHA-256 must equal digest (else
                  ledger_bad); a missing file counts external_absent
    unverifiable  nothing here can re-hash it; `note` must say why (else
                  ledger_bad)
    wrong         a known-wrong cited digest; `correct` must be a 64-hex digest
                  in the blob set sharing the first 8 characters (else
                  ledger_bad)

Classification, first match wins: blob | ledger (by class) | wrong_unflagged
(first 8 characters equal those of some blob-set digest) | unknown.

Output (one line):
    tokens=T blob=B external_ok=E external_absent=A unverifiable=U wrong_flagged=W ledger_bad=L wrong_unflagged=X unknown=K
`--details` also prints one `detail:` line per unexplained or flagged token.
Exit: 0 L+X+K == 0; 1 otherwise; 2 usage or git error.
Read-only: it reads git objects and files and writes nothing.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
import tempfile

TOKEN = re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]{64}(?![0-9a-fA-F])")
LEDGER = "registry/digest-ledger.tsv"
HEADER = "digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote"
KEYS = ("tokens", "blob", "external_ok", "external_absent", "unverifiable", "wrong_flagged",
        "ledger_bad", "wrong_unflagged", "unknown")


def is_doc(rel: str) -> bool:
    return not rel.startswith(".ufo/") and rel != LEDGER and rel.endswith((".md", ".tsv"))


def parse_ledger(text: str) -> dict:
    rows = {}
    for i, line in enumerate(text.split("\n")):
        if not line or (i == 0 and line.startswith("digest\t")):
            continue
        c = line.split("\t") + [""] * 7
        rows[c[0]] = {"cls": c[1], "path": c[3], "correct": c[4], "note": c[6]}
    return rows


def classify(tokens: set, blobs: set, ledger: dict):
    n = dict.fromkeys(KEYS, 0)
    n["tokens"] = len(tokens)
    detail = []
    prefixes = {b[:8] for b in blobs}
    for t in sorted(tokens):
        if t in blobs:
            n["blob"] += 1
        elif t in ledger:
            r = ledger[t]
            cls = r["cls"]
            if cls == "external":
                p = r["path"]
                if p and os.path.isfile(p):
                    with open(p, "rb") as f:
                        h = hashlib.sha256(f.read()).hexdigest()
                    key = "external_ok" if h == t else "ledger_bad"
                else:
                    key = "external_absent"
            elif cls == "unverifiable":
                key = "unverifiable" if r["note"].strip() else "ledger_bad"
            elif cls == "wrong":
                c = r["correct"]
                ok = re.fullmatch(r"[0-9a-f]{64}", c) is not None and c in blobs and c[:8] == t[:8]
                key = "wrong_flagged" if ok else "ledger_bad"
            else:
                key = "ledger_bad"
            n[key] += 1
            if key in ("ledger_bad", "wrong_flagged", "external_absent"):
                detail.append(f"detail: {key} {t} class={cls}")
        elif t[:8] in prefixes:
            n["wrong_unflagged"] += 1
            detail.append(f"detail: wrong_unflagged {t} (first 8 characters match a real digest)")
        else:
            n["unknown"] += 1
            detail.append(f"detail: unknown {t}")
    return n, detail


def scan_dir(root: str, ledger_file: str | None):
    tokens, blobs, ledger = set(), set(), {}
    for cur, _, files in os.walk(root):
        for name in files:
            full = os.path.join(cur, name)
            rel = os.path.relpath(full, root)
            if os.path.islink(full) or not os.path.isfile(full):
                continue
            with open(full, "rb") as f:
                data = f.read()
            blobs.add(hashlib.sha256(data).hexdigest())
            if rel == LEDGER and ledger_file is None:
                ledger = parse_ledger(data.decode(errors="replace"))
            elif is_doc(rel):
                tokens |= set(TOKEN.findall(data.decode(errors="replace")))
    if ledger_file is not None:
        with open(ledger_file, encoding="utf-8", errors="replace") as f:
            ledger = parse_ledger(f.read())
    return tokens, blobs, ledger


def git(repo: str, *args: str) -> bytes:
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout


def scan_git(repo: str, rev: str, ledger_file: str | None):
    rev = git(repo, "rev-parse", "--verify", f"{rev}^{{commit}}").decode().strip()
    ids = [l.split(" ", 1)[0] for l in git(repo, "rev-list", "--objects", rev).decode().split("\n") if l]
    p = subprocess.run(["git", "-C", repo, "cat-file", "--batch"], input="".join(i + "\n" for i in ids).encode(),
                       capture_output=True)
    if p.returncode != 0:
        raise RuntimeError("git cat-file --batch: " + p.stderr.decode(errors="replace").strip())
    blobs, buf, i = set(), p.stdout, 0
    while i < len(buf):
        j = buf.index(b"\n", i)
        _, typ, size = buf[i:j].decode().split()
        size = int(size)
        if typ == "blob":
            blobs.add(hashlib.sha256(buf[j + 1:j + 1 + size]).hexdigest())
        i = j + 1 + size + 1
    tokens, ledger = set(), {}
    for path in git(repo, "ls-tree", "-r", "--name-only", "-z", rev).decode().split("\0"):
        if not path:
            continue
        if path == LEDGER and ledger_file is None:
            ledger = parse_ledger(git(repo, "cat-file", "-p", f"{rev}:{path}").decode(errors="replace"))
        elif is_doc(path):
            tokens |= set(TOKEN.findall(git(repo, "cat-file", "-p", f"{rev}:{path}").decode(errors="replace")))
    if ledger_file is not None:
        with open(ledger_file, encoding="utf-8", errors="replace") as f:
            ledger = parse_ledger(f.read())
    return tokens, blobs, ledger


def render(n: dict) -> str:
    return " ".join(f"{k}={n[k]}" for k in KEYS)


def selftest() -> int:
    ok = bad = 0
    with tempfile.TemporaryDirectory(prefix="digest-ledger-selftest-") as d:
        os.makedirs(os.path.join(d, "registry"))
        data = b"alpha\n"
        with open(os.path.join(d, "alpha.bin"), "wb") as f:
            f.write(data)
        good = hashlib.sha256(data).hexdigest()
        wrong = good[:8] + "0" * 56
        unk = "ab" * 32
        ext = "cd" * 32
        with open(os.path.join(d, "doc.md"), "w") as f:
            f.write(f"{good} {wrong} {unk} {ext}\n")
        cases = [
            ("no ledger: blob, wrong_unflagged, 2 unknown", None, dict(tokens=4, blob=1, wrong_unflagged=1, unknown=2), 1),
            ("ledger flags wrong + unverifiable + external-absent", [
                f"{wrong}\twrong\ts\t\t{good}\t\t", f"{unk}\tunverifiable\ts\t\t\t\tno host copy",
                f"{ext}\texternal\ts\t/nonexistent/x\t\t\t"], dict(tokens=4, blob=1, wrong_flagged=1, unverifiable=1,
                                                               external_absent=1), 0),
            ("wrong row with a non-matching correct digest is ledger_bad", [
                f"{wrong}\twrong\ts\t\t{unk}\t\t", f"{unk}\tunverifiable\ts\t\t\t\twhy",
                f"{ext}\texternal\ts\t\t\t\t"], dict(tokens=4, blob=1, ledger_bad=1, unverifiable=1,
                                                      external_absent=1), 1),
            ("unverifiable row with an empty note is ledger_bad", [
                f"{wrong}\twrong\ts\t\t{good}\t\t", f"{unk}\tunverifiable\ts\t\t\t\t",
                f"{ext}\texternal\ts\t\t\t\t"], dict(tokens=4, blob=1, wrong_flagged=1, ledger_bad=1,
                                                      external_absent=1), 1),
            ("external row whose file hashes differently is ledger_bad", [
                f"{wrong}\twrong\ts\t\t{good}\t\t", f"{unk}\tunverifiable\ts\t\t\t\twhy",
                f"{ext}\texternal\ts\t{os.path.join(d, 'alpha.bin')}\t\t\t"], dict(tokens=4, blob=1, wrong_flagged=1,
                                                                             unverifiable=1, ledger_bad=1), 1),
        ]
        for name, rows, want, code in cases:
            lp = os.path.join(d, "registry", "digest-ledger.tsv")
            if rows is None:
                if os.path.exists(lp):
                    os.remove(lp)
            else:
                with open(lp, "w") as f:
                    f.write(HEADER + "\n" + "\n".join(rows) + "\n")
            tok, blobs, led = scan_dir(d, None)
            n, _ = classify(tok, blobs, led)
            exp = dict.fromkeys(KEYS, 0)
            exp.update(want)
            got = (n, 1 if n["ledger_bad"] + n["wrong_unflagged"] + n["unknown"] else 0)
            if got == (exp, code):
                ok += 1
            else:
                bad += 1
                print(f"selftest FAIL: {name}: got {render(n)} exit {got[1]}", file=sys.stderr)
        # a .ufo/ document and the ledger file are not documents
        with open(os.path.join(d, "registry", "digest-ledger.tsv"), "w") as f:
            f.write(HEADER + "\n" + f"{unk}\tunverifiable\ts\t\t\t\twhy\n")
        os.makedirs(os.path.join(d, ".ufo"))
        with open(os.path.join(d, ".ufo", "x.md"), "w") as f:
            f.write("ef" * 32 + "\n")
        tok, _, _ = scan_dir(d, None)
        if "ef" * 32 in tok or tok != {good, wrong, unk, ext}:
            bad += 1
            print("selftest FAIL: scope (.ufo/ or ledger file leaked into tokens)", file=sys.stderr)
        else:
            ok += 1
    print(f"selftest pass={ok} fail={bad}")
    return 0 if bad == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sc = sub.add_parser("scan")
    g = sc.add_mutually_exclusive_group(required=True)
    g.add_argument("--dir")
    g.add_argument("--repo")
    sc.add_argument("--rev", default="HEAD")
    sc.add_argument("--ledger")
    sc.add_argument("--details", action="store_true")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    try:
        tok, blobs, led = scan_dir(a.dir, a.ledger) if a.dir else scan_git(a.repo, a.rev, a.ledger)
    except (RuntimeError, OSError, ValueError) as e:
        print(f"digest-ledger: {e}", file=sys.stderr)
        return 2
    n, detail = classify(tok, blobs, led)
    print(render(n))
    if a.details:
        print("\n".join(detail))
    return 1 if n["ledger_bad"] + n["wrong_unflagged"] + n["unknown"] else 0


if __name__ == "__main__":
    sys.exit(main())
