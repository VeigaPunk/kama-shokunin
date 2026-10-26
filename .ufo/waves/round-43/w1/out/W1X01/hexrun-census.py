#!/usr/bin/env python3
"""hexrun-census.py - census of every non-64 hex run the lane's documents cite.

Round-43 C2 capability, implementation A (stdlib only, read-only). Contract
(the round-43 counter tools/round43-hexrun-audit.py docstring is the authority):

    hexrun-census.py scan (--repo R --rev REV | --dir DIR) [--ledger FILE] [--details]
    hexrun-census.py selftest

Documents: git mode - blobs at REV whose path ends .md or .tsv, outside
  `.ufo/`, except registry/hexrun-ledger.tsv and registry/digest-ledger.tsv;
  dir mode - regular files under DIR (symlinks not followed) with the same name
  rules.
Token: a maximal run of lower-case hex characters [0-9a-f] of length L with
  32 <= L <= 127 and L != 64, with no [0-9A-Za-z] immediately before or after.
Classes (first match wins; every distinct token lands in exactly one):
  lane_oid     L == 40 and the object exists in the repository (git mode only)
  md5_blob     L == 32 and equals the MD5 of a regular-file blob (git mode:
               every regular-file blob at REV, i.e. modes 100644/100755; dir
               mode: every regular file under DIR)
  ledger       a row of registry/hexrun-ledger.tsv (at REV, or DIR; --ledger
               overrides), TAB-separated, header
               `token class repo evidence correct verified-at note`:
                 upstream      `evidence` is a regular-file blob at REV (a
                               regular file under DIR) whose bytes contain the
                               token and the non-empty `repo` cell text ->
                               upstream_ok; otherwise ledger_bad
                 unverifiable  `note` (trailing whitespace stripped) has >= 10
                               characters -> unverifiable; else ledger_bad
                 wrong         `correct` is a different token-shaped run that
                               classifies lane_oid, md5_blob or upstream and
                               shares its first 8 characters with `token` ->
                               wrong_flagged; otherwise ledger_bad
               a duplicated ledger token, a row with fewer than 7 cells, or an
               unknown class -> ledger_bad
  unknown      anything else
Output (one line on stdout):
  tokens=T distinct=D lane_oid=A md5_blob=B upstream_ok=C unverifiable=U
  wrong_flagged=W ledger_bad=L unknown=K
  `--details` appends one `detail<TAB>token<TAB>class` line per distinct token
  on stderr, so stdout stays the single summary line.
Exit: 0 when ledger_bad + unknown == 0, 1 otherwise, 2 usage or git error.

Read-only: nothing is written to the repository or to the temporary directory
(no temporary files are created at all; the git population is streamed through
one `git cat-file --batch` process).
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import threading

TOKEN_RE = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{32,127}(?![0-9A-Za-z])")
LEDGERS = ("registry/hexrun-ledger.tsv", "registry/digest-ledger.tsv")
LEDGER_DEFAULT = "registry/hexrun-ledger.tsv"
REGULAR_MODES = ("100644", "100755")
LEDGER_COLS = 7
NOTE_MIN = 10
PREFIX = 8
FIELDS = ("tokens", "distinct", "lane_oid", "md5_blob", "upstream_ok", "unverifiable",
          "wrong_flagged", "ledger_bad", "unknown")


class GitError(Exception):
    """A git command the census needs failed."""


def git(repo: str, *args: str, inp: bytes | None = None) -> bytes:
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, input=inp)
    if p.returncode != 0:
        raise GitError(f"git {' '.join(args)}: {p.stderr.decode('utf-8', 'replace').strip()}")
    return p.stdout


def tokens_of(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text) if len(t) != 64]


def is_doc(rel: str) -> bool:
    return rel.endswith((".md", ".tsv")) and not rel.startswith(".ufo/") and rel not in LEDGERS


def read_exact(stream, n: int) -> bytes:
    data = stream.read(n)
    if len(data) != n:
        raise GitError("short read from git cat-file --batch")
    return data


class Population:
    """The document set, the regular-file MD5 set and the ledger text."""

    def __init__(self, kind: str, docs, md5s, ledger_text, repo=None, rev=None, root=None,
                 blob_paths=frozenset(), oids=frozenset()):
        self.kind = kind
        self.docs = docs                    # list[(rel path, text)]
        self.md5s = md5s                    # set[str]
        self.ledger_text = ledger_text
        self.repo = repo
        self.rev = rev
        self.root = root
        self.blob_paths = set(blob_paths)   # git mode: regular-file blob paths
        self.oids = set(oids)               # git mode: 40-runs that exist


def git_scan(repo: str, rev: str) -> Population:
    entries = []
    for rec in git(repo, "ls-tree", "-r", "-z", rev).split(b"\0"):
        if not rec:
            continue
        meta, _, path = rec.partition(b"\t")
        parts = meta.split()
        if len(parts) != 3:
            raise GitError(f"unparsable ls-tree record: {rec[:80]!r}")
        mode, typ, sha = (p.decode("utf-8", "replace") for p in parts)
        entries.append((mode, typ, sha, os.fsdecode(path)))
    blobs = [(sha, path) for mode, typ, sha, path in entries
             if typ == "blob" and mode in REGULAR_MODES]
    docs: dict[str, bytes] = {}
    md5s: set[str] = set()
    proc = subprocess.Popen(["git", "-C", repo, "cat-file", "--batch"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    assert proc.stdin is not None and proc.stdout is not None
    errors: list[str] = []

    def feed() -> None:
        try:
            for sha, _ in blobs:
                proc.stdin.write(sha.encode() + b"\n")
            proc.stdin.close()
        except OSError as exc:  # git exited early; the read loop reports it
            errors.append(str(exc))

    th = threading.Thread(target=feed)
    th.start()
    for _sha, path in blobs:
        hdr = proc.stdout.readline().split()
        if len(hdr) != 3 or hdr[1] != b"blob":
            raise GitError(f"cat-file --batch header for {path}: {hdr!r}")
        size = int(hdr[2])
        data = read_exact(proc.stdout, size)
        read_exact(proc.stdout, 1)
        md5s.add(hashlib.md5(data).hexdigest())
        if is_doc(path):
            docs[path] = data
    th.join()
    if proc.wait() != 0 or errors:
        raise GitError(f"git cat-file --batch failed: {'; '.join(errors) or proc.returncode}")
    ledger_text = read_git_file(repo, rev, LEDGER_DEFAULT)
    return Population("git", [(p, docs[p].decode("utf-8", "replace")) for p in sorted(docs)],
                      md5s, ledger_text, repo=repo, rev=rev,
                      blob_paths={p for sha, p in blobs})


def read_git_file(repo: str, rev: str, path: str) -> str | None:
    p = subprocess.run(["git", "-C", repo, "cat-file", "-p", f"{rev}:{path}"], capture_output=True)
    if p.returncode != 0:
        return None
    return p.stdout.decode("utf-8", "replace")


def dir_scan(root: str) -> Population:
    docs = []
    md5s: set[str] = set()
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not os.path.islink(os.path.join(base, d)))
        for name in sorted(files):
            full = os.path.join(base, name)
            if os.path.islink(full) or not os.path.isfile(full):
                continue
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            with open(full, "rb") as fh:
                data = fh.read()
            md5s.add(hashlib.md5(data).hexdigest())
            if is_doc(rel):
                docs.append((rel, data.decode("utf-8", "replace")))
    ledger_text = None
    ledger_file = os.path.join(root, LEDGER_DEFAULT)
    if os.path.isfile(ledger_file) and not os.path.islink(ledger_file):
        with open(ledger_file, "rb") as fh:
            ledger_text = fh.read().decode("utf-8", "replace")
    return Population("dir", docs, md5s, ledger_text, repo=None, rev=None, root=root)


def read_ledger_override(path: str, repo: str | None, rev: str | None) -> str | None:
    if os.path.isfile(path):
        with open(path, "rb") as fh:
            return fh.read().decode("utf-8", "replace")
    if repo is not None and rev is not None:
        return read_git_file(repo, rev, path)
    print(f"hexrun-census: ledger {path!r} not found; no rows applied", file=sys.stderr)
    return None


class Ledger:
    def __init__(self, text: str | None):
        self.rows: dict[str, list[list[str]]] = {}
        if not text:
            return
        first = True
        for ln in text.splitlines():
            if not ln.strip():
                continue
            cells = ln.split("\t")
            if first:
                first = False
                if cells[0].strip().lower() == "token":
                    continue
            tok = cells[0].strip()
            if tok:
                self.rows.setdefault(tok, []).append(cells)


class Census:
    def __init__(self, pop: Population, ledger: Ledger):
        self.pop = pop
        self.ledger = ledger
        self._evidence: dict[str, bytes | None] = {}
        self._oid: dict[str, bool] = {}

    def _evidence_bytes(self, path: str) -> bytes | None:
        if path in self._evidence:
            return self._evidence[path]
        data = None
        if self.pop.kind == "git":
            if path in self.pop.blob_paths:
                p = subprocess.run(["git", "-C", self.pop.repo, "cat-file", "-p",
                                    f"{self.pop.rev}:{path}"], capture_output=True)
                data = p.stdout if p.returncode == 0 else None
        else:
            root = os.path.realpath(self.pop.root)
            full = os.path.realpath(os.path.join(root, path))
            if full.startswith(root + os.sep) and os.path.isfile(full) and not os.path.islink(full):
                with open(full, "rb") as fh:
                    data = fh.read()
        self._evidence[path] = data
        return data

    def _oid_exists(self, tok: str) -> bool:
        if self.pop.kind != "git":
            return False
        if tok in self.pop.oids:
            return True
        if tok in self._oid:
            return self._oid[tok]
        p = subprocess.run(["git", "-C", self.pop.repo, "cat-file", "--batch-check"],
                           input=tok + "\n", capture_output=True, text=True)
        parts = p.stdout.split()
        ok = p.returncode == 0 and len(parts) == 3 and parts[1] != "missing"
        self._oid[tok] = ok
        return ok

    def _upstream_ok(self, tok: str, cells: list[str]) -> bool:
        if len(cells) < LEDGER_COLS:
            return False
        repo_cell, evidence = cells[2].strip(), cells[3].strip()
        if not repo_cell or not evidence:
            return False
        data = self._evidence_bytes(evidence)
        if data is None:
            return False
        return tok.encode() in data and repo_cell.encode() in data

    def _resolvable(self, tok: str) -> bool:
        if len(tok) == 40 and self._oid_exists(tok):
            return True
        if len(tok) == 32 and tok in self.pop.md5s:
            return True
        rows = self.ledger.rows.get(tok)
        return bool(rows and len(rows) == 1 and rows[0][1:2] == ["upstream"]
                    and self._upstream_ok(tok, rows[0]))

    def classify(self, tok: str) -> str:
        if len(tok) == 40 and self._oid_exists(tok):
            return "lane_oid"
        if len(tok) == 32 and tok in self.pop.md5s:
            return "md5_blob"
        rows = self.ledger.rows.get(tok)
        if rows is None:
            return "unknown"
        if len(rows) > 1:
            return "ledger_bad"
        cells = rows[0]
        if len(cells) < LEDGER_COLS:
            return "ledger_bad"
        cls = cells[1].strip()
        if cls == "upstream":
            return "upstream_ok" if self._upstream_ok(tok, cells) else "ledger_bad"
        if cls == "unverifiable":
            note = "\t".join(cells[LEDGER_COLS - 1:]).strip()
            return "unverifiable" if len(note) >= NOTE_MIN else "ledger_bad"
        if cls == "wrong":
            correct = cells[4].strip()
            if not (TOKEN_RE.fullmatch(correct) and len(correct) != 64 and correct != tok):
                return "ledger_bad"
            if correct[:PREFIX] != tok[:PREFIX]:
                return "ledger_bad"
            return "wrong_flagged" if self._resolvable(correct) else "ledger_bad"
        return "ledger_bad"


def run_scan(repo: str | None = None, rev: str | None = None, directory: str | None = None,
             ledger_path: str | None = None):
    pop = git_scan(repo, rev) if repo is not None else dir_scan(directory)
    if ledger_path:
        pop.ledger_text = read_ledger_override(ledger_path, repo, rev)
    cen = Census(pop, Ledger(pop.ledger_text))
    tokens: list[str] = []
    for _rel, text in pop.docs:
        tokens += tokens_of(text)
    counts = dict.fromkeys(FIELDS, 0)
    counts["tokens"] = len(tokens)
    distinct = sorted(set(tokens))
    counts["distinct"] = len(distinct)
    details = []
    for tok in distinct:
        cls = cen.classify(tok)
        counts[cls] += 1
        details.append((tok, cls))
    return counts, details


def summary(counts: dict) -> str:
    return " ".join(f"{k}={counts[k]}" for k in FIELDS)


def exit_code(counts: dict) -> int:
    return 0 if counts["ledger_bad"] == 0 and counts["unknown"] == 0 else 1


LEDGER_HDR = "token\tclass\trepo\tevidence\tcorrect\tverified-at\tnote\n"


def selftest() -> int:
    import random

    rng = random.Random(43)
    data = bytes(rng.randrange(256) for _ in range(64))
    md5 = hashlib.md5(data).hexdigest()

    def rhex(n: int) -> str:
        return "".join(rng.choice("0123456789abcdef") for _ in range(n))

    def w(root: str, rel: str, text) -> None:
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p) or root, exist_ok=True)
        with open(p, "wb" if isinstance(text, bytes) else "w") as fh:
            fh.write(text)

    def want(**k) -> dict:
        d = {f: 0 for f in FIELDS}
        d.update(k)
        return d

    cases: list[tuple[str, callable]] = []

    def case(name, build, expect, code, ledger=None, git=False):
        cases.append((name, build, expect, code, ledger, git))

    t40 = [rhex(40) for _ in range(12)]

    def c_md5(root, _k=0):
        w(root, "data.bin", data)
        w(root, "doc.md", f"cited sum {md5} end\n")

    case("md5-blob", c_md5, want(tokens=1, distinct=1, md5_blob=1), 0)

    def c_md5_unknown(root):
        w(root, "data.bin", data)
        w(root, "doc.md", f"cited sum {rhex(32)} end\n")

    case("md5-unknown", c_md5_unknown, want(tokens=1, distinct=1, unknown=1), 1)

    def c_overlong(root):
        w(root, "doc.md", f"over-long {rhex(65)} and a digest {rhex(64)} and short {rhex(31)}\n")

    case("overlong-ignores-64-and-31", c_overlong, want(tokens=1, distinct=1, unknown=1), 1)

    def c_up_ok(root):
        t = t40[0]
        w(root, "doc.md", f"commit {t}\n")
        w(root, "ev/up.json", f'{{"sha": "{t}", "repo": "acme/widget"}}\n')
        w(root, "registry/hexrun-ledger.tsv",
          LEDGER_HDR + f"{t}\tupstream\tacme/widget\tev/up.json\t\t2026-10-25\tapi 200\n")

    case("upstream-ok", c_up_ok, want(tokens=1, distinct=1, upstream_ok=1), 0)

    def c_up_bad(root):
        t = t40[1]
        w(root, "doc.md", f"commit {t}\n")
        w(root, "ev/up.json", '{"sha": "not-the-token", "repo": "acme/widget"}\n')
        w(root, "registry/hexrun-ledger.tsv",
          LEDGER_HDR + f"{t}\tupstream\tacme/widget\tev/up.json\t\t2026-10-25\tapi 200\n")

    case("upstream-evidence-lacks-token", c_up_bad, want(tokens=1, distinct=1, ledger_bad=1), 1)

    def c_up_missing_file(root):
        t = t40[2]
        w(root, "doc.md", f"commit {t}\n")
        w(root, "registry/hexrun-ledger.tsv",
          LEDGER_HDR + f"{t}\tupstream\tacme/widget\tev/absent.json\t\t2026-10-25\tapi 200\n")

    case("upstream-evidence-absent", c_up_missing_file, want(tokens=1, distinct=1, ledger_bad=1), 1)

    def c_dup_row(root):
        t = t40[3]
        w(root, "doc.md", f"commit {t}\n")
        w(root, "ev/up.json", f'{{"sha": "{t}", "repo": "acme/widget"}}\n')
        row = f"{t}\tupstream\tacme/widget\tev/up.json\t\t2026-10-25\tapi 200\n"
        w(root, "registry/hexrun-ledger.tsv", LEDGER_HDR + row + row)

    case("duplicate-ledger-row", c_dup_row, want(tokens=1, distinct=1, ledger_bad=1), 1)

    def c_unver(root):
        t = t40[4]
        w(root, "doc.md", f"commit {t}\n")
        w(root, "registry/hexrun-ledger.tsv",
          LEDGER_HDR + f"{t}\tunverifiable\t\t\t\t2026-10-25\tupstream repository deleted\n")

    case("unverifiable-with-note", c_unver, want(tokens=1, distinct=1, unverifiable=1), 0)

    def c_unver_short(root):
        t = t40[5]
        w(root, "doc.md", f"commit {t}\n")
        w(root, "registry/hexrun-ledger.tsv",
          LEDGER_HDR + f"{t}\tunverifiable\t\t\t\t2026-10-25\tshort\n")

    case("unverifiable-without-reason", c_unver_short, want(tokens=1, distinct=1, ledger_bad=1), 1)

    def c_wrong(root):
        t = md5[:8] + rhex(24)
        w(root, "data.bin", data)
        w(root, "doc.md", f"sum {t}\n")
        w(root, "registry/hexrun-ledger.tsv",
          LEDGER_HDR + f"{t}\twrong\t\t\t{md5}\t2026-10-25\tprefix-equal typo\n")

    case("wrong-flagged", c_wrong, want(tokens=1, distinct=1, wrong_flagged=1), 0)

    def c_wrong_bad(root):
        t = md5[:8] + rhex(24)
        w(root, "data.bin", data)
        w(root, "doc.md", f"sum {t}\n")
        w(root, "registry/hexrun-ledger.tsv",
          LEDGER_HDR + f"{t}\twrong\t\t\t{rhex(32)}\t2026-10-25\tbad correction\n")

    case("wrong-correct-unresolved", c_wrong_bad, want(tokens=1, distinct=1, ledger_bad=1), 1)

    def c_bounds(root):
        t = t40[6]
        w(root, "doc.md", f"UP {t.upper()} g{t} {t}g {rhex(128)} {t}\n{t}\n")
        w(root, ".ufo/hidden.md", f"{rhex(40)}\n")
        w(root, "note.txt", f"{rhex(40)}\n")

    case("boundaries-and-exclusions", c_bounds, want(tokens=2, distinct=1, unknown=1), 1)

    def c_dup_token(root):
        t = t40[7]
        w(root, "registry/hexrun-ledger.tsv", LEDGER_HDR)
        w(root, "doc.md", f"a {t} b {t}\n")

    case("duplicate-token-counts-once", c_dup_token, want(tokens=2, distinct=1, unknown=1), 1)

    def c_unknown_class(root):
        t = t40[8]
        w(root, "doc.md", f"commit {t}\n")
        w(root, "registry/hexrun-ledger.tsv",
          LEDGER_HDR + f"{t}\tprobably\tacme/widget\t\t\t2026-10-25\tsounds right to me\n")

    case("unknown-ledger-class", c_unknown_class, want(tokens=1, distinct=1, ledger_bad=1), 1)

    def c_symlink(root):
        t = t40[9]
        w(root, "outside.txt", f"{t}\n")
        os.symlink(os.path.join(root, "outside.txt"), os.path.join(root, "linked.md"))
        w(root, "real.md", "no runs here\n")

    case("symlink-not-followed", c_symlink, want(tokens=0, distinct=0), 0)

    def c_override(root):
        t = t40[10]
        w(root, "doc.md", f"commit {t}\n")
        w(root, "alt/rows.ledger", LEDGER_HDR +
          f"{t}\tunverifiable\t\t\t\t2026-10-25\tupstream repository deleted\n")

    case("ledger-override", c_override, want(tokens=1, distinct=1, unverifiable=1), 0,
         ledger="alt/rows.ledger")

    def c_git(root):
        subprocess.run(["git", "-C", root, "init", "-q"], check=True)
        top = subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True).stdout.strip()
        if os.path.realpath(top) != os.path.realpath(root):
            raise RuntimeError("selftest git fixture toplevel mismatch")
        ident = ["-c", "user.name=selftest", "-c", "user.email=selftest@invalid"]
        with open(os.path.join(root, "a.txt"), "w") as fh:
            fh.write("one\n")
        subprocess.run(["git", "-C", root, "add", "-A"], check=True)
        subprocess.run(["git", "-C", root, *ident, "commit", "-qm", "first"],
                       check=True, capture_output=True)
        first = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"],
                               capture_output=True, text=True).stdout.strip()
        w(root, "doc.md", f"resolves {first} and fabricated {t40[11]}\n")
        subprocess.run(["git", "-C", root, "add", "-A"], check=True)
        subprocess.run(["git", "-C", root, *ident, "commit", "-qm", "second"],
                       check=True, capture_output=True)

    case("git-lane-oid-and-unknown", c_git,
         want(tokens=2, distinct=2, lane_oid=1, unknown=1), 1, git=True)

    fails = 0
    for name, build, expect, code, ledger, git_mode in cases:
        with tempfile.TemporaryDirectory(prefix="hexrun-selftest-") as root:
            try:
                build(root)
                if git_mode:
                    counts, _ = run_scan(repo=root, rev="HEAD")
                elif ledger:
                    counts, _ = run_scan(directory=root, ledger_path=os.path.join(root, ledger))
                else:
                    counts, _ = run_scan(directory=root)
                got_line, got_code = summary(counts), exit_code(counts)
            except Exception as exc:  # every failure is a failed case, not a crash
                counts, got_line, got_code = None, f"error: {exc}", None
            if got_line != summary(expect) or got_code != code:
                fails += 1
                print(f"selftest FAIL {name}: want exit {code} {summary(expect)!r}; "
                      f"got exit {got_code} {got_line!r}", file=sys.stderr)
    print(f"selftest pass={len(cases) - fails} fail={fails} cases={len(cases)}")
    return 0 if fails == 0 else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="hexrun-census.py",
                                 description="census of non-64 hex runs cited by documents")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("scan", help="census a revision or a directory")
    sp.add_argument("--repo", help="git repository (with --rev)")
    sp.add_argument("--rev", help="revision to read in the repository")
    sp.add_argument("--dir", help="directory to read instead of a repository")
    sp.add_argument("--ledger", help="ledger file (default registry/hexrun-ledger.tsv)")
    sp.add_argument("--details", action="store_true", help="per-token classes on stderr")
    sub.add_parser("selftest", help="run the built-in contract cases")
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    if bool(a.repo) != bool(a.rev):
        ap.error("--repo and --rev must be given together")
    if bool(a.dir) == bool(a.repo):
        ap.error("give exactly one of --dir or (--repo with --rev)")
    try:
        counts, details = run_scan(repo=a.repo, rev=a.rev, directory=a.dir, ledger_path=a.ledger)
    except GitError as exc:
        print(f"hexrun-census: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"hexrun-census: {exc}", file=sys.stderr)
        return 2
    print(summary(counts))
    if a.details:
        for tok, cls in details:
            print(f"detail\t{tok}\t{cls}", file=sys.stderr)
    return exit_code(counts)


if __name__ == "__main__":
    sys.exit(main())
