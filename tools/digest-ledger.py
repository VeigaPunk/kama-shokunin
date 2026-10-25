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

Scope and limits (found by the round-42 wave, kept honest here): only exact
64-character runs are tokens. A cited "digest" of another length (a 65-character
run, a digest hard-wrapped over two lines), an upper-case digest, abbreviated
digests (`3ad0df68...`) and UTF-16 documents are not seen. A mixed-case
neighbour (an upper-case hex character next to the run) is not a token boundary
either. `path` cells are confined: a relative path resolves against the scanned
tree, the resolved real path must lie inside the scanned tree or the home
directory, the file must be regular and at most 256 MiB, and anything else (or
any read error) counts as external_absent. Two ledger rows with the same digest
make the digest ledger_bad. A promisor (partial) clone is refused with exit 2,
because completing its blob set would write into the audited repository. Git mode
considers regular-file blobs only (symlinks and gitlinks are skipped).

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
import stat
import subprocess
import sys
import tempfile
import threading

TOKEN = re.compile(r"(?<![0-9a-fA-F])[0-9a-f]{64}(?![0-9a-fA-F])")
MAX_EXTERNAL = 256 * 1024 * 1024
LEDGER = "registry/digest-ledger.tsv"
HEADER = "digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote"
KEYS = ("tokens", "blob", "external_ok", "external_absent", "unverifiable", "wrong_flagged",
        "ledger_bad", "wrong_unflagged", "unknown")


def is_doc(rel: str) -> bool:
    return not rel.startswith(".ufo/") and rel != LEDGER and rel.endswith((".md", ".tsv"))


def parse_ledger(text: str) -> dict:
    rows = {}
    for i, line in enumerate(text.splitlines()):
        if not line or (i == 0 and line.startswith("digest\t")):
            continue
        c = line.split("\t") + [""] * 7
        cls = "duplicate" if c[0] in rows else c[1]
        rows[c[0]] = {"cls": cls, "path": c[3], "correct": c[4], "note": c[6]}
    return rows


def hash_external(path: str, roots: list):
    """sha256 of a confined regular file, or None (absent, outside the roots, unreadable, too big)."""
    if not path:
        return None
    base = roots[0] if roots else os.getcwd()
    real = os.path.realpath(path if os.path.isabs(path) else os.path.join(base, path))
    if not any(real == r or real.startswith(r.rstrip(os.sep) + os.sep) for r in roots):
        return None
    try:
        fd = os.open(real, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError:
        return None
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_size > MAX_EXTERNAL:
            return None
        h = hashlib.sha256()
        with os.fdopen(fd, "rb", closefd=False) as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None
    finally:
        os.close(fd)


def classify(tokens: set, blobs: set, ledger: dict, roots: list | None = None):
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
                got = hash_external(r["path"], roots or [])
                key = "external_absent" if got is None else ("external_ok" if got == t else "ledger_bad")
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


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def home_root() -> str:
    return os.path.realpath(os.path.expanduser("~"))


def scan_dir(root: str, ledger_file: str | None):
    tokens, blobs, ledger = set(), set(), {}
    for cur, _, files in os.walk(root):
        for name in files:
            full = os.path.join(cur, name)
            rel = os.path.relpath(full, root)
            if os.path.islink(full) or not os.path.isfile(full):
                continue
            blobs.add(file_sha256(full))
            if rel == LEDGER and ledger_file is None:
                with open(full, "rb") as f:
                    ledger = parse_ledger(f.read().decode(errors="replace"))
            elif is_doc(rel):
                with open(full, "rb") as f:
                    tokens |= set(TOKEN.findall(f.read().decode(errors="replace")))
    if ledger_file is not None:
        with open(ledger_file, encoding="utf-8", errors="replace") as f:
            ledger = parse_ledger(f.read())
    return tokens, blobs, ledger, [os.path.realpath(root), home_root()]


def git(repo: str, *args: str) -> bytes:
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout


def stream_blob_digests(repo: str, ids: list) -> set:
    """SHA-256 of every blob in ids, streaming `git cat-file --batch` (one blob in memory at a time)."""
    p = subprocess.Popen(["git", "-C", repo, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    def feed():
        try:
            for i in ids:
                p.stdin.write((i + "\n").encode())
            p.stdin.close()
        except OSError:
            pass

    t = threading.Thread(target=feed, daemon=True)
    t.start()
    blobs = set()
    out = p.stdout
    while True:
        head = out.readline()
        if not head:
            break
        _, typ, size = head.decode().split()
        size = int(size)
        h = hashlib.sha256() if typ == "blob" else None
        left = size
        while left > 0:
            chunk = out.read(min(left, 1 << 20))
            if not chunk:
                raise RuntimeError("git cat-file --batch: truncated stream")
            if h is not None:
                h.update(chunk)
            left -= len(chunk)
        out.read(1)
        if h is not None:
            blobs.add(h.hexdigest())
    t.join()
    if p.wait() != 0:
        raise RuntimeError("git cat-file --batch: " + p.stderr.read().decode(errors="replace").strip())
    return blobs


def scan_git(repo: str, rev: str, ledger_file: str | None):
    top = git(repo, "rev-parse", "--show-toplevel").decode(errors="replace").strip()
    if git(repo, "rev-parse", "--is-bare-repository").decode().strip() == "false" and \
            subprocess.run(["git", "-C", repo, "config", "--get-regexp", r"^(remote\..*\.promisor|extensions\.partialclone)$"],
                           capture_output=True).stdout.strip():
        raise RuntimeError("partial (promisor) clone refused: completing its blob set would write into the audited repository")
    rev = git(repo, "rev-parse", "--verify", f"{rev}^{{commit}}").decode().strip()
    ids = [l.split(" ", 1)[0] for l in git(repo, "rev-list", "--objects", rev).decode(errors="replace").split("\n") if l]
    blobs = stream_blob_digests(repo, ids)
    tokens, ledger = set(), {}
    for rec in git(repo, "ls-tree", "-r", "-z", rev).decode(errors="replace").split("\0"):
        if not rec:
            continue
        meta, _, path = rec.partition("\t")
        mode, typ, _oid = (meta.split(" ") + ["", "", ""])[:3]
        if typ != "blob" or mode not in ("100644", "100755"):
            continue
        if path == LEDGER and ledger_file is None:
            ledger = parse_ledger(git(repo, "cat-file", "-p", f"{rev}:{path}").decode(errors="replace"))
        elif is_doc(path):
            tokens |= set(TOKEN.findall(git(repo, "cat-file", "-p", f"{rev}:{path}").decode(errors="replace")))
    if ledger_file is not None:
        with open(ledger_file, encoding="utf-8", errors="replace") as f:
            ledger = parse_ledger(f.read())
    return tokens, blobs, ledger, [os.path.realpath(top), home_root()]


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
            tok, blobs, led, roots = scan_dir(d, None)
            n, _ = classify(tok, blobs, led, roots)
            exp = dict.fromkeys(KEYS, 0)
            exp.update(want)
            got = (n, 1 if n["ledger_bad"] + n["wrong_unflagged"] + n["unknown"] else 0)
            if got == (exp, code):
                ok += 1
            else:
                bad += 1
                print(f"selftest FAIL: {name}: got {render(n)} exit {got[1]}", file=sys.stderr)
        # round-42 wave hardening: duplicate rows, confinement, CRLF, upper-case adjacency
        lp = os.path.join(d, "registry", "digest-ledger.tsv")
        extra = [
            ("duplicate ledger rows make the digest ledger_bad",
             [f"{unk}\tunverifiable\ts\t\t\t\twhy", f"{unk}\tunverifiable\ts\t\t\t\twhy again"], {"unverifiable": 0, "ledger_bad": 1}),
            ("an external path outside the scanned tree and the home directory is not read",
             [f"{unk}\tunverifiable\ts\t\t\t\twhy", f"{ext}\texternal\ts\t/etc/hostname\t\t\t"],
             {"external_absent": 1, "unverifiable": 1}),
            ("CRLF ledger rows parse like LF rows",
             [f"{unk}\tunverifiable\ts\t\t\t\twhy\r", f"{ext}\texternal\ts\t\t\t\t\r"], {"unverifiable": 1, "external_absent": 1}),
        ]
        for name, rows, want in extra:
            with open(lp, "w", newline="") as f:
                f.write(HEADER + "\n" + "\n".join(rows) + "\n")
            tok, blobs, led, roots = scan_dir(d, None)
            n, _ = classify(tok, blobs, led, roots)
            if all(n[k] == v for k, v in want.items()):
                ok += 1
            else:
                bad += 1
                print(f"selftest FAIL: {name}: got {render(n)}", file=sys.stderr)
        with open(os.path.join(d, "up.md"), "w") as f:
            f.write("A" * 64 + good + " " + good.upper() + "\n")
        tok, _, _, _ = scan_dir(d, None)
        if tok != {good, wrong, unk, ext}:
            bad += 1
            print("selftest FAIL: upper-case neighbour carved a token out of a longer run", file=sys.stderr)
        else:
            ok += 1
        os.remove(os.path.join(d, "up.md"))
        with open(lp, "w") as f:
            f.write(HEADER + "\n" + f"{unk}\tunverifiable\ts\t\t\t\twhy\n")
        # a .ufo/ document and the ledger file are not documents
        with open(os.path.join(d, "registry", "digest-ledger.tsv"), "w") as f:
            f.write(HEADER + "\n" + f"{unk}\tunverifiable\ts\t\t\t\twhy\n")
        os.makedirs(os.path.join(d, ".ufo"))
        with open(os.path.join(d, ".ufo", "x.md"), "w") as f:
            f.write("ef" * 32 + "\n")
        tok, _, _, _ = scan_dir(d, None)
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
        tok, blobs, led, roots = scan_dir(a.dir, a.ledger) if a.dir else scan_git(a.repo, a.rev, a.ledger)
    except (RuntimeError, OSError, ValueError) as e:
        print(f"digest-ledger: {e}", file=sys.stderr)
        return 2
    n, detail = classify(tok, blobs, led, roots)
    print(render(n))
    if a.details:
        print("\n".join(detail))
    return 1 if n["ledger_bad"] + n["wrong_unflagged"] + n["unknown"] else 0


if __name__ == "__main__":
    sys.exit(main())
