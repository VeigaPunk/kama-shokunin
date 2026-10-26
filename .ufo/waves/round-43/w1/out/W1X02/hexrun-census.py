#!/usr/bin/env python3
"""hexrun-census.py - census every non-digest hex run the lane's documents cite.

Round-43 C2 capability (kama lane, operability). Question: does the lane hold a
working census of every hex run its documents cite that is NOT a 64-character
digest (git object ids, MD5 sums, over-long or abbreviated runs), classifying
each as a lane object, a hash of a committed blob, an upstream object whose
existence a committed evidence file shows, an unverifiable citation with its
reason, or a flagged wrong citation - so that no cited run is unexplained?

Contract (frozen in tools/round43-hexrun-audit.py):

    hexrun-census.py scan (--repo R --rev REV | --dir DIR) [--ledger FILE] [--details]
    hexrun-census.py selftest

Documents: git mode - blobs at REV whose path ends .md or .tsv, outside `.ufo/`,
  except registry/hexrun-ledger.tsv and registry/digest-ledger.tsv; dir mode -
  regular files under DIR (symlinks not followed) with the same name rules.
Token: a maximal run of lower-case hex characters [0-9a-f] of length L with
  32 <= L <= 127 and L != 64, with no [0-9A-Za-z] immediately before or after.
Counts: `tokens` counts occurrences, `distinct` counts distinct token strings.
  Each distinct token falls in exactly one class, first match wins:
    lane_oid   L == 40 and the object exists in the repository (git mode only)
    md5_blob   L == 32 and equals the MD5 of a regular-file blob (git mode:
               every blob at REV; dir mode: every regular file under DIR)
    ledger     a row of registry/hexrun-ledger.tsv (at REV, or DIR; --ledger
               overrides), TAB-separated, header
               `token class repo evidence correct verified-at note`:
                 upstream      `evidence` is a path of a blob at REV (a file
                               under DIR) whose bytes contain the token and the
                               `repo` cell text -> upstream_ok; else ledger_bad
                 unverifiable  `note` has >= 10 characters -> unverifiable;
                               else ledger_bad
                 wrong         `correct` is a different token-shaped run that
                               classifies lane_oid, md5_blob or upstream, and
                               shares its first 8 characters with `token`
                               -> wrong_flagged; else ledger_bad
               a duplicated ledger token or an unknown class -> ledger_bad
    unknown    anything else
Output (one line, stdout):
  tokens=T distinct=D lane_oid=A md5_blob=B upstream_ok=C unverifiable=U wrong_flagged=W ledger_bad=L unknown=K
Exit: 0 when L + K == 0, 1 otherwise, 2 usage or git error. Read-only; it
  leaves nothing in the temporary directory.

Implementation notes (implementation B, independent of the counter):
  * Population is enumerated once with `git ls-tree -r -z` and streamed through
    ONE `git cat-file --batch` session; the MD5 set is built from that same
    stream (no per-document subprocess, no repeated reads).
  * The ledger is parsed with the stdlib csv module under an explicit TAB
    delimiter (QUOTE_NONE, strict=True), never with string splitting.
  * Nothing is written outside the requested output; no temporary files are
    created by `scan` at all.
  * `--details` writes per-token lines to stderr so stdout stays the one-line
    contract summary.

Resolved ambiguities are listed in the round-43 report for seat W1X02.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
import re
import stat
import subprocess
import sys

TOKEN_RE = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{32,127}(?![0-9A-Za-z])")
TOKEN_EXACT_RE = re.compile(r"(?:[0-9a-f]{32,63}|[0-9a-f]{65,127})\Z")
LEDGER_REL = "registry/hexrun-ledger.tsv"
NON_DOCUMENTS = frozenset({"registry/hexrun-ledger.tsv", "registry/digest-ledger.tsv"})
LEDGER_HEADER = ("token", "class", "repo", "evidence", "correct", "verified-at", "note")
LEDGER_CLASSES = frozenset({"upstream", "unverifiable", "wrong"})
NOTE_MIN = 10
REGULAR_MODES = frozenset({"100644", "100755"})
ORDER = ("tokens", "distinct", "lane_oid", "md5_blob", "upstream_ok", "unverifiable",
         "wrong_flagged", "ledger_bad", "unknown")


class CensusError(Exception):
    """Usage, git or input error: exit 2."""


# --------------------------------------------------------------------------- #
# token and path rules
# --------------------------------------------------------------------------- #

def tokens_of(data: bytes) -> list[str]:
    text = data.decode("utf-8", "replace")
    return [t for t in TOKEN_RE.findall(text) if len(t) != 64]


def is_document(path: str) -> bool:
    return (path.endswith((".md", ".tsv"))
            and not path.startswith(".ufo/")
            and path not in NON_DOCUMENTS)


def token_shaped(cell: str) -> bool:
    return TOKEN_EXACT_RE.fullmatch(cell) is not None


# --------------------------------------------------------------------------- #
# git helpers
# --------------------------------------------------------------------------- #

def git(repo: str, *args: str, inp: bytes | None = None) -> bytes:
    p = subprocess.run(["git", "-C", repo, *args], input=inp, capture_output=True)
    if p.returncode != 0:
        raise CensusError(f"git {' '.join(args)}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout


class Entry:
    __slots__ = ("path", "mode", "kind", "sha")

    def __init__(self, path: str, mode: str, kind: str, sha: str) -> None:
        self.path, self.mode, self.kind, self.sha = path, mode, kind, sha


def ls_tree(repo: str, rev: str) -> list[Entry]:
    out = git(repo, "ls-tree", "-r", "-z", "--full-tree", rev)
    entries: list[Entry] = []
    for rec in out.split(b"\0"):
        if not rec:
            continue
        meta, sep, path = rec.partition(b"\t")
        if not sep:
            raise CensusError(f"unparseable ls-tree record: {rec[:80]!r}")
        mode, kind, sha = meta.split(b" ")
        entries.append(Entry(path.decode("utf-8", "surrogateescape"),
                             mode.decode(), kind.decode(), sha.decode()))
    return entries


def batch_contents(repo: str, shas: list[str]):
    """Stream `git cat-file --batch` responses for `shas` in order.

    One process, one pass; a feeder thread keeps the request pipe full without
    materialising every blob in memory.
    """
    if not shas:
        return
    import threading

    proc = subprocess.Popen(["git", "-C", repo, "cat-file", "--batch"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    assert proc.stdin is not None and proc.stdout is not None

    def feed() -> None:
        try:
            for sha in shas:
                proc.stdin.write((sha + "\n").encode())
            proc.stdin.close()
        except BrokenPipeError:
            pass

    th = threading.Thread(target=feed, daemon=True)
    th.start()
    try:
        for want in shas:
            header = proc.stdout.readline()
            if not header:
                raise CensusError(f"cat-file --batch ended early at {want}")
            parts = header.split()
            if len(parts) < 2:
                raise CensusError(f"unparseable cat-file header: {header!r}")
            if parts[1] == b"missing":
                yield want, None
                continue
            size = int(parts[2])
            data = proc.stdout.read(size)
            proc.stdout.read(1)  # trailing LF
            yield want, data
    finally:
        try:
            proc.stdout.close()
        finally:
            proc.wait()
        th.join(timeout=5)


def object_exists(repo: str, oids: list[str]) -> set[str]:
    """Full 40-hex ids that name an object at REV's object store (any type)."""
    if not oids:
        return set()
    out = git(repo, "cat-file", "--batch-check",
              inp=("\n".join(oids) + "\n").encode()).decode("utf-8", "replace")
    present: set[str] = set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 3:  # `<id> <type> <size>`; missing/ambiguous are shorter
            present.add(parts[0])
    return present


# --------------------------------------------------------------------------- #
# ledger
# --------------------------------------------------------------------------- #

class LedgerRow:
    __slots__ = ("token", "cls", "repo", "evidence", "correct", "note", "well_formed")

    def __init__(self, token, cls, repo, evidence, correct, note, well_formed=True) -> None:
        self.token, self.cls, self.repo = token, cls, repo
        self.evidence, self.correct, self.note = evidence, correct, note
        self.well_formed = well_formed


def parse_ledger(data: bytes) -> dict[str, list[LedgerRow]]:
    text = data.decode("utf-8", "replace")
    rows: dict[str, list[LedgerRow]] = {}
    reader = csv.reader(io.StringIO(text, newline=""), delimiter="\t",
                        quoting=csv.QUOTE_NONE, strict=True)
    first = True
    for cells in reader:
        if not any(c for c in cells):
            continue
        if first and tuple(cells) == LEDGER_HEADER:
            first = False
            continue
        first = False
        token = cells[0] if cells else ""
        if not token_shaped(token):
            # A row whose token cell is not a non-digest hex run can never
            # classify a cited token; ignore it.
            continue
        if len(cells) == len(LEDGER_HEADER):
            rows.setdefault(token, []).append(
                LedgerRow(token, cells[1], cells[2], cells[3], cells[4], cells[6]))
        else:
            rows.setdefault(token, []).append(
                LedgerRow(token, "", "", "", "", "", well_formed=False))
    return rows


class Context:
    def __init__(self) -> None:
        self.md5s: set[str] = set()
        self.lane_oids: set[str] = set()
        self.ledger: dict[str, list[LedgerRow]] = {}
        self.evidence: dict[str, bytes | None] = {}

    # -- ledger classes ---------------------------------------------------- #
    def upstream_ok(self, row: LedgerRow) -> bool:
        data = self.evidence.get(row.evidence)
        if not data:
            return False
        if row.token.encode() not in data:
            return False
        want_repo = row.repo.encode()
        return not want_repo or want_repo in data

    def resolve(self, token: str, seen: frozenset[str] = frozenset()) -> str:
        if len(token) == 40 and token in self.lane_oids:
            return "lane_oid"
        if len(token) == 32 and token in self.md5s:
            return "md5_blob"
        rows = self.ledger.get(token)
        if not rows:
            return "unknown"
        if len(rows) > 1:
            return "ledger_bad"
        row = rows[0]
        if not row.well_formed:
            return "ledger_bad"
        cls = row.cls
        if cls == "upstream":
            return "upstream_ok" if self.upstream_ok(row) else "ledger_bad"
        if cls == "unverifiable":
            return "unverifiable" if len(row.note) >= NOTE_MIN else "ledger_bad"
        if cls == "wrong":
            correction = row.correct
            if (correction != token and token_shaped(correction)
                    and correction[:8] == token[:8]
                    and correction not in seen):
                got = self.resolve(correction, seen | {token})
                if got in ("lane_oid", "md5_blob", "upstream_ok"):
                    return "wrong_flagged"
            return "ledger_bad"
        return "ledger_bad"


# --------------------------------------------------------------------------- #
# population sources
# --------------------------------------------------------------------------- #

def git_population(repo: str, rev: str, ctx: Context,
                   ledger_override: bytes | None) -> list[str]:
    rev_full = git(repo, "rev-parse", "--verify", f"{rev}^{{commit}}").decode().strip()
    entries = ls_tree(repo, rev_full)

    by_sha: dict[str, list[Entry]] = {}
    for e in entries:
        by_sha.setdefault(e.sha, []).append(e)

    # Ledger first: it decides which evidence blobs must be retained.
    if ledger_override is not None:
        ledger_bytes = ledger_override
    else:
        ledger_entry = next((e for e in entries
                             if e.path == LEDGER_REL and e.kind == "blob"), None)
        if ledger_entry is None:
            ledger_bytes = b""
        else:
            ledger_bytes = next((data for _, data in batch_contents(repo, [ledger_entry.sha])), None) or b""
    ctx.ledger = parse_ledger(ledger_bytes)
    evidence_paths = {row.evidence for rows in ctx.ledger.values() for row in rows
                      if row.well_formed and row.cls == "upstream" and row.evidence}

    tokens: list[str] = []
    shas = [sha for sha, group in by_sha.items()]
    for sha, data in batch_contents(repo, shas):
        group = by_sha[sha]
        if data is None:
            continue
        if any(e.mode in REGULAR_MODES for e in group):
            ctx.md5s.add(hashlib.md5(data).hexdigest())
        docs = [e.path for e in group if e.kind == "blob" and is_document(e.path)]
        if docs:
            toks = tokens_of(data)
            for _ in docs:
                tokens.extend(toks)
        for e in group:
            if e.path in evidence_paths:
                ctx.evidence[e.path] = data

    oids = sorted({t for t in set(tokens) if len(t) == 40})
    ctx.lane_oids = object_exists(repo, oids)
    return tokens


def dir_population(root: str, ctx: Context, ledger_override: bytes | None) -> list[str]:
    root = os.path.realpath(root)
    if not os.path.isdir(root):
        raise CensusError(f"--dir not a directory: {root}")

    if ledger_override is not None:
        ledger_bytes = ledger_override
    else:
        candidate = os.path.join(root, LEDGER_REL)
        ledger_bytes = b""
        if os.path.isfile(candidate) and not os.path.islink(candidate):
            with open(candidate, "rb") as fh:
                ledger_bytes = fh.read()
    ctx.ledger = parse_ledger(ledger_bytes)

    evidence_rel: set[str] = set()
    for rows in ctx.ledger.values():
        for row in rows:
            if not row.well_formed or row.cls != "upstream" or not row.evidence:
                continue
            rel = os.path.normpath(row.evidence).replace(os.sep, "/")
            if rel.startswith("../") or os.path.isabs(rel):
                continue  # an evidence path "under DIR" cannot escape it
            evidence_rel.add(rel)

    tokens: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames
                             if not os.path.islink(os.path.join(dirpath, d)))
        for name in sorted(filenames):
            full = os.path.join(dirpath, name)
            try:
                st = os.stat(full, follow_symlinks=False)
            except OSError:
                continue
            if not stat.S_ISREG(st.st_mode):
                continue
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            try:
                with open(full, "rb") as fh:
                    data = fh.read()
            except OSError as e:
                raise CensusError(f"cannot read {full}: {e}") from e
            ctx.md5s.add(hashlib.md5(data).hexdigest())
            if is_document(rel):
                tokens.extend(tokens_of(data))
            if rel in evidence_rel:
                ctx.evidence[rel] = data
    return tokens


# --------------------------------------------------------------------------- #
# accounting
# --------------------------------------------------------------------------- #

def census(tokens: list[str], ctx: Context) -> dict[str, int]:
    counts = dict.fromkeys(ORDER, 0)
    distinct = sorted(set(tokens))
    counts["tokens"] = len(tokens)
    counts["distinct"] = len(distinct)
    for token in distinct:
        cls = ctx.resolve(token)
        if cls == "upstream_ok":
            counts["upstream_ok"] += 1
        elif cls in counts:
            counts[cls] += 1
        else:  # pragma: no cover - resolve only returns the names above
            raise CensusError(f"unexpected class {cls!r} for {token}")
    return counts


def summary(counts: dict[str, int]) -> str:
    return " ".join(f"{k}={counts[k]}" for k in ORDER)


# --------------------------------------------------------------------------- #
# subcommands
# --------------------------------------------------------------------------- #

def run_scan(args: argparse.Namespace) -> int:
    ctx = Context()
    if args.dir is not None:
        if args.repo is not None or args.rev is not None:
            raise CensusError("--dir excludes --repo/--rev")
        ledger_override = read_ledger_override(args.ledger, None, None)
        tokens = dir_population(args.dir, ctx, ledger_override)
    else:
        if args.repo is None or args.rev is None:
            raise CensusError("scan needs --repo and --rev, or --dir")
        ledger_override = read_ledger_override(args.ledger, args.repo, args.rev)
        tokens = git_population(args.repo, args.rev, ctx, ledger_override)

    counts = census(tokens, ctx)
    sys.stdout.write(summary(counts) + "\n")
    if args.details:
        for token in sorted(set(tokens)):
            sys.stderr.write(f"detail: {token} len={len(token)} "
                             f"occurrences={tokens.count(token)} class={ctx.resolve(token)}\n")
    return 0 if counts["ledger_bad"] + counts["unknown"] == 0 else 1


def read_ledger_override(path: str | None, repo: str | None, rev: str | None) -> bytes | None:
    if not path:
        return None
    if os.path.isfile(path):
        with open(path, "rb") as fh:
            return fh.read()
    if repo is not None and rev is not None:
        return git(repo, "cat-file", "-p", f"{rev}:{path}")
    raise CensusError(f"--ledger file not found: {path}")


def run_selftest() -> int:
    import shutil
    import tempfile

    base = tempfile.mkdtemp(prefix="hexrun-census-selftest-")
    passed = failed = 0
    try:
        def check(name: str, want: str, want_rc: int, argv: list[str]) -> None:
            nonlocal passed, failed
            try:
                p = subprocess.run([sys.executable, __file__, *argv],
                                   capture_output=True, text=True, timeout=300,
                                   env=dict(os.environ, TMPDIR=os.path.join(base, "tmp")))
            except subprocess.TimeoutExpired:
                failed += 1
                print(f"selftest fail {name}: timeout", file=sys.stderr)
                return
            got = p.stdout.strip()
            if got == want and p.returncode == want_rc:
                passed += 1
            else:
                failed += 1
                print(f"selftest fail {name}: want rc={want_rc} {want!r}; "
                      f"got rc={p.returncode} {got!r} {p.stderr.strip()[:200]!r}", file=sys.stderr)

        os.makedirs(os.path.join(base, "tmp"))
        blob = bytes(range(64))
        md5 = hashlib.md5(blob).hexdigest()

        def case(name: str, files: dict[str, bytes | str]) -> str:
            d = os.path.join(base, name)
            for rel, body in files.items():
                full = os.path.join(d, rel)
                os.makedirs(os.path.dirname(full) or d, exist_ok=True)
                with open(full, "wb") as fh:
                    fh.write(body.encode() if isinstance(body, str) else body)
            return d

        def line(**k) -> str:
            d = dict.fromkeys(ORDER, 0)
            d.update(k)
            return " ".join(f"{a}={d[a]}" for a in ORDER)

        def h(n: int, seed: int) -> str:
            out = hashlib.sha256(f"{seed}".encode()).hexdigest()
            while len(out) < n:
                out += hashlib.sha256(out.encode()).hexdigest()
            return out[:n]

        d = case("md5", {"b.bin": blob, "doc.md": f"sum {md5}\n"})
        check("md5-blob", line(tokens=1, distinct=1, md5_blob=1), 0, ["scan", "--dir", d])

        d = case("md5miss", {"doc.md": f"sum {h(32, 1)}\n"})
        check("md5-unknown", line(tokens=1, distinct=1, unknown=1), 1, ["scan", "--dir", d])

        d = case("bounds", {"doc.md": f"{h(31, 2)} {h(64, 3)} {h(65, 4)} {h(128, 5)} "
                                      f"x{h(40, 6)} {h(40, 7)}y {h(40, 6).upper()}\n"})
        check("bounds", line(tokens=1, distinct=1, unknown=1), 1, ["scan", "--dir", d])

        t = h(40, 8)
        d = case("up", {"doc.md": f"cite {t}\n", "ev/x.json": f'{{"sha":"{t}","repo":"a/b"}}\n',
                        "registry/hexrun-ledger.tsv":
                            f"{LEDGER_TXT}\n{t}\tupstream\ta/b\tev/x.json\t\t2026-10-25\tapi 200\n"})
        check("upstream-ok", line(tokens=1, distinct=1, upstream_ok=1), 0, ["scan", "--dir", d])

        d = case("upmiss", {"doc.md": f"cite {t}\n", "ev/x.json": '{"sha":"nope"}\n',
                            "registry/hexrun-ledger.tsv":
                                f"{LEDGER_TXT}\n{t}\tupstream\ta/b\tev/x.json\t\t2026-10-25\tapi 200\n"})
        check("upstream-missing", line(tokens=1, distinct=1, ledger_bad=1), 1, ["scan", "--dir", d])

        d = case("unver", {"doc.md": f"cite {t}\n",
                           "registry/hexrun-ledger.tsv":
                               f"{LEDGER_TXT}\n{t}\tunverifiable\t\t\t\t2026-10-25\tdeleted upstream\n"})
        check("unverifiable-ok", line(tokens=1, distinct=1, unverifiable=1), 0, ["scan", "--dir", d])

        d = case("unvershort", {"doc.md": f"cite {t}\n",
                                "registry/hexrun-ledger.tsv":
                                    f"{LEDGER_TXT}\n{t}\tunverifiable\t\t\t\t2026-10-25\tshort\n"})
        check("unverifiable-short", line(tokens=1, distinct=1, ledger_bad=1), 1, ["scan", "--dir", d])

        typo = md5[:8] + h(24, 9)
        d = case("wrong", {"b.bin": blob, "doc.md": f"sum {typo}\n",
                           "registry/hexrun-ledger.tsv":
                               f"{LEDGER_TXT}\n{typo}\twrong\t\t\t{md5}\t2026-10-25\tprefix typo\n"})
        check("wrong-flagged", line(tokens=1, distinct=1, wrong_flagged=1), 0, ["scan", "--dir", d])

        d = case("wrongbad", {"b.bin": blob, "doc.md": f"sum {typo}\n",
                              "registry/hexrun-ledger.tsv":
                                  f"{LEDGER_TXT}\n{typo}\twrong\t\t\t{h(32, 10)}\t2026-10-25\tbad\n"})
        check("wrong-unresolved", line(tokens=1, distinct=1, ledger_bad=1), 1, ["scan", "--dir", d])

        # A wrong row whose correction resolves only as an upstream ledger row;
        # the correction token itself is cited nowhere, so it is not counted.
        up_tok = h(40, 12)
        bad_tok = up_tok[:8] + h(32, 13)[8:]
        d = case("wrongup", {"doc.md": f"sum {bad_tok}\n",
                             "ev/u.json": f'{{"sha":"{up_tok}","repo":"a/b"}}\n',
                             "registry/hexrun-ledger.tsv":
                                 f"{LEDGER_TXT}\n"
                                 f"{bad_tok}\twrong\t\t\t{up_tok}\t2026-10-25\tprefix typo\n"
                                 f"{up_tok}\tupstream\ta/b\tev/u.json\t\t2026-10-25\tapi 200\n"})
        check("wrong-to-upstream", line(tokens=1, distinct=1, wrong_flagged=1), 0,
              ["scan", "--dir", d])

        d = case("note10", {"doc.md": f"cite {t}\n",
                            "registry/hexrun-ledger.tsv":
                                f"{LEDGER_TXT}\n{t}\tunverifiable\t\t\t\t2026-10-25\t0123456789\n"})
        check("note-10-chars", line(tokens=1, distinct=1, unverifiable=1), 0, ["scan", "--dir", d])

        d = case("note9", {"doc.md": f"cite {t}\n",
                           "registry/hexrun-ledger.tsv":
                               f"{LEDGER_TXT}\n{t}\tunverifiable\t\t\t\t2026-10-25\t012345678\n"})
        check("note-9-chars", line(tokens=1, distinct=1, ledger_bad=1), 1, ["scan", "--dir", d])

        d = case("punct", {"doc.md": f"a_{t}_b -{t}- .{t}. [{t}] {t}x\n"})
        check("punctuation-boundaries", line(tokens=4, distinct=1, unknown=1), 1,
              ["scan", "--dir", d])

        d = case("dup", {"doc.md": f"cite {t}\n",
                         "registry/hexrun-ledger.tsv":
                             f"{LEDGER_TXT}\n{t}\tunverifiable\t\t\t\t2026-10-25\treason here\n"
                             f"{t}\tunverifiable\t\t\t\t2026-10-25\treason here\n"})
        check("duplicate-row", line(tokens=1, distinct=1, ledger_bad=1), 1, ["scan", "--dir", d])

        d = case("cls", {"doc.md": f"cite {t}\n",
                         "registry/hexrun-ledger.tsv":
                             f"{LEDGER_TXT}\n{t}\tmystery\t\t\t\t2026-10-25\treason here\n"})
        check("unknown-class", line(tokens=1, distinct=1, ledger_bad=1), 1, ["scan", "--dir", d])

        d = case("dupcite", {"doc.md": f"a {t} b {t}\n"})
        check("occurrences", line(tokens=2, distinct=1, unknown=1), 1, ["scan", "--dir", d])

        # git mode: a cited object resolves, a fabricated oid does not.
        repo = os.path.join(base, "git")
        os.makedirs(repo)
        ident = ["-c", "user.name=hexrun-census-selftest", "-c", "user.email=selftest@invalid"]
        subprocess.run(["git", "-C", repo, "init", "-q"], check=True)
        top = subprocess.run(["git", "-C", repo, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True).stdout.strip()
        if os.path.realpath(top) != os.path.realpath(repo):
            raise CensusError("selftest fixture toplevel mismatch")
        with open(os.path.join(repo, "a.txt"), "w") as fh:
            fh.write("one\n")
        subprocess.run(["git", "-C", repo, "add", "-A"], check=True)
        subprocess.run(["git", "-C", repo, *ident, "commit", "-qm", "one"],
                       check=True, capture_output=True)
        first = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"],
                               capture_output=True, text=True).stdout.strip()
        fake = h(40, 11)
        with open(os.path.join(repo, "doc.md"), "w") as fh:
            fh.write(f"resolves {first} fabricated {fake}\n")
        subprocess.run(["git", "-C", repo, "add", "-A"], check=True)
        subprocess.run(["git", "-C", repo, *ident, "commit", "-qm", "two"],
                       check=True, capture_output=True)
        check("git-lane-oid", line(tokens=2, distinct=2, lane_oid=1, unknown=1), 1,
              ["scan", "--repo", repo, "--rev", "HEAD"])

        # --ledger override: a filesystem ledger outside the scanned tree.
        d = case("override", {"doc.md": f"cite {t}\n"})
        led = os.path.join(base, "ledger.tsv")
        with open(led, "w") as fh:
            fh.write(f"{LEDGER_TXT}\n{t}\tunverifiable\t\t\t\t2026-10-25\tdeleted upstream\n")
        check("ledger-override", line(tokens=1, distinct=1, unverifiable=1), 0,
              ["scan", "--dir", d, "--ledger", led])
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print(f"selftest pass={passed} fail={failed}")
    return 0 if failed == 0 else 1


LEDGER_TXT = "\t".join(LEDGER_HEADER)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="hexrun-census.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sc = sub.add_parser("scan")
    sc.add_argument("--repo")
    sc.add_argument("--rev")
    sc.add_argument("--dir")
    sc.add_argument("--ledger")
    sc.add_argument("--details", action="store_true")
    sub.add_parser("selftest")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "selftest":
            return run_selftest()
        return run_scan(args)
    except CensusError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
