#!/usr/bin/env python3
"""Receipt-pointer resolution audit (round 68).

Audits the section-relative ``measured/...`` receipt-pointer citations in the
lane's self-record. Within a ``... Round <N> ...`` heading's section, a
backtick-quoted `` `measured/<rest>` `` token denotes the repo path
``.ufo/waves/round-<N>/<rest>``; the audit verifies that blob exists at
``--rev`` (``git cat-file -e``, read-only, index-free). This is the citation
class whose meaning silently depends on where a line was copy-pasted: the
round-67 closure routed one dangling instance (``measured/before/banner-before.out``
cited where only ``banner-pending-phrase-before.out`` was committed) and the
round-68 census found a second the closure did not name
(``measured/province-marker-lines-after.out``, never committed).

Scope limit (declared, not hidden): only the section-relative ``measured/``
class is audited. Citations that carry their own round in the path
(``.ufo/waves/round-N/...``) are a different, historically much larger class
(418 backtick occurrences in SCORECARD.md at the round-68 start head, many of
them brace/glob/dir shorthands) and are out of scope here.

Two notations inside the class are resolved mechanically, not by ledger:
  - brace alternatives in the basename, ``{a,b}``: every expansion must exist;
  - a ``*`` in the basename: at least one blob under the same directory whose
    name starts with the prefix before ``*`` and ends with the suffix after
    ``*`` must exist (``git ls-tree``, read-only).

Any other unresolved citation may be mapped by the resolution ledger
(--ledger, default registry/receipt-pointer-resolutions.tsv, read from the
worktree: corrections are knowledge about past citations, applied at the
auditing tip). A ledger row matches on (file, cited token, section round) and
resolves the citation only when its ``resolved-by`` path itself exists at
--rev; a row whose target is missing is reported as a defective row, never as
a pass. Rows are append-only: a superseded row is never deleted, it is
superseded by a later row naming it.

Exit map (pinned):
  0  every citation resolved (directly, expanded, or by a resolving ledger row)
  1  at least one citation unresolved
  2  could-not-evaluate (git failure, audited file missing at --rev,
     undecodable blob, unreadable ledger) -- never silently 0

Selftest: builds throwaway git repositories in tempfile.TemporaryDirectory
fixtures (own ``git init`` there, ``core.autocrlf=false`` pinned) and drives
the same audit entry point the CLI uses; no lane path is read or written.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile

HEADING_RE = re.compile(r"^#{1,6}\s", re.M)
# Only round-record headings advance the section tracker: a capitalized
# `Round <N>` / `Round-<N>`. Lowercase parentheticals — `### Planned (round
# 66)` inside the Round-65 record — describe the NEXT round's plan; their
# citations still belong to the record they sit in.
ROUND_IN_HEADING_RE = re.compile(r"\bRound[-\s]+#?(\d+)")
CITATION_RE = re.compile(r"`([^`\n]+)`")
LEDGER_HEADER = ("file", "cited", "round", "resolved-by", "reason", "correction-round")


class CouldNotEvaluate(Exception):
    """Raised for fail-closed conditions; maps to exit 2."""


def _git(repo, *args):
    proc = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if proc.returncode != 0:
        raise CouldNotEvaluate(
            "git {} failed (rc={}): {}".format(
                " ".join(args[:2]), proc.returncode, proc.stderr.decode("utf-8", "replace").strip()
            )
        )
    return proc.stdout


def _read_blob(repo, rev, path):
    out = _git(repo, "show", "{}:{}".format(rev, path))
    try:
        return out.decode("utf-8")
    except UnicodeDecodeError as e:
        raise CouldNotEvaluate("blob {}:{} is not UTF-8: {}".format(rev, path, e))


def _blob_exists(repo, rev, path):
    return subprocess.run(
        ["git", "-C", repo, "cat-file", "-e", "{}:{}".format(rev, path)],
        capture_output=True,
    ).returncode == 0


def _dir_names(repo, rev, dirpath):
    out = _git(repo, "ls-tree", "--name-only", "{}:{}".format(rev, dirpath.rstrip("/")))
    return [n.decode("utf-8", "replace") for n in out.splitlines() if n.strip()]


def _brace_alternatives(basename):
    m = re.search(r"\{([^{}]+)\}", basename)
    if not m:
        return None
    alts = m.group(1).split(",")
    return [basename.replace(m.group(0), a, 1) for a in alts]


def _resolve_target(repo, rev, target):
    """Return (status, note); status in {'resolved','expanded','unresolved'}."""
    if _blob_exists(repo, rev, target):
        return "resolved", ""
    directory, basename = target.rsplit("/", 1)
    alts = _brace_alternatives(basename)
    if alts is not None:
        missing = [a for a in alts if not _blob_exists(repo, rev, "{}/{}".format(directory, a))]
        if not missing:
            return "expanded", "brace-all-of-{}".format(len(alts))
        return "unresolved", "brace missing: {}".format(",".join(missing))
    if "*" in basename:
        prefix, suffix = basename.split("*", 1)
        try:
            names = _dir_names(repo, rev, directory)
        except CouldNotEvaluate:
            names = []
        hits = [n for n in names if n.startswith(prefix) and n.endswith(suffix)]
        if hits:
            return "expanded", "glob {} hit(s)".format(len(hits))
        return "unresolved", "glob no match under {}/".format(directory)
    return "unresolved", ""


def _read_ledger(path):
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, "rb") as fh:
        data = fh.read()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as e:
        raise CouldNotEvaluate("ledger {} is not UTF-8: {}".format(path, e))
    for lineno, line in enumerate(text.split("\n"), 1):
        if not line.strip() or line.startswith("#") or line.startswith("file\t"):
            continue
        parts = line.split("\t")
        if len(parts) != len(LEDGER_HEADER):
            raise CouldNotEvaluate(
                "ledger {} line {}: expected {} fields, got {}".format(
                    path, lineno, len(LEDGER_HEADER), len(parts)
                )
            )
        rows.append(dict(zip(LEDGER_HEADER, [p.strip() for p in parts])))
    return rows


def audit(repo, rev, files, ledger_path):
    ledger = _read_ledger(ledger_path)
    results = []
    for path in files:
        text = _read_blob(repo, rev, path)
        current_round = None
        for lineno, line in enumerate(text.split("\n"), 1):
            if HEADING_RE.match(line):
                m = ROUND_IN_HEADING_RE.search(line)
                if m:
                    current_round = m.group(1)
            for tok in CITATION_RE.findall(line):
                # `measured/` alone, and tokens whose remainder is dots only
                # (`measured/...`, `measured/…`), are prose about the class,
                # not citations; a citation names a receipt path.
                rest = tok[len("measured/"):] if tok.startswith("measured/") else ""
                if not rest or not any(ch not in ".\u2026" for ch in rest):
                    continue
                if current_round is None:
                    results.append(
                        {
                            "file": path,
                            "line": lineno,
                            "round": "",
                            "cited": tok,
                            "target": "",
                            "status": "unresolved",
                            "note": "no round section precedes the citation",
                        }
                    )
                    continue
                target = ".ufo/waves/round-{}/{}".format(current_round, tok)
                status, note = _resolve_target(repo, rev, target)
                if status == "unresolved":
                    rows = [
                        r
                        for r in ledger
                        if r["file"] == path and r["cited"] == tok and r["round"] == current_round
                    ]
                    resolved_by = None
                    for row in rows:
                        if _blob_exists(repo, rev, row["resolved-by"]):
                            resolved_by = row
                            break
                    if resolved_by is not None:
                        status, note = "corrected", "ledger -> {}".format(resolved_by["resolved-by"])
                    elif rows:
                        note = "ledger row(s) defective: resolved-by missing at rev"
                    elif not note:
                        note = "target missing at rev"
                results.append(
                    {
                        "file": path,
                        "line": lineno,
                        "round": current_round,
                        "cited": tok,
                        "target": target,
                        "status": status,
                        "note": note,
                    }
                )
    return results


def render(results):
    counts = {"resolved": 0, "expanded": 0, "corrected": 0, "unresolved": 0}
    files = set()
    for r in results:
        counts[r["status"]] += 1
        files.add(r["file"])
    lines = []
    for r in results:
        if r["status"] == "unresolved":
            lines.append(
                "UNRESOLVED file={} line={} round={} cited=`{}` target={} note={}".format(
                    r["file"], r["line"], r["round"] or "-", r["cited"], r["target"] or "-", r["note"]
                )
            )
    summary = "RECEIPT_POINTER_AUDIT files={} cited={} resolved={} expanded={} corrected={} unresolved={}".format(
        len(files), len(results), counts["resolved"], counts["expanded"], counts["corrected"], counts["unresolved"]
    )
    return lines, summary


def run_audit(repo, rev, files, ledger_path):
    results = audit(repo, rev, files, ledger_path)
    lines, summary = render(results)
    for ln in lines:
        print(ln)
    print(summary)
    unresolved = sum(1 for r in results if r["status"] == "unresolved")
    return 1 if unresolved else 0


# ---------------------------------------------------------------- selftest


def _init_repo(root):
    def run(*args, **kw):
        proc = subprocess.run(["git", *args], cwd=root, capture_output=True, **kw)
        assert proc.returncode == 0, proc.stderr.decode("utf-8", "replace")
        return proc.stdout

    run("init", "-q", "-b", "master", ".")
    run("config", "core.autocrlf", "false")
    run("config", "user.email", "selftest@example.invalid")
    run("config", "user.name", "selftest")
    return run


def _write(root, relpath, content):
    full = os.path.join(root, relpath.replace("/", os.sep))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb") as fh:
        fh.write(content.encode("utf-8"))


def _commit_all(run):
    run("add", "-A")
    run("commit", "-q", "-m", "fixture")


def run_selftest():
    arms = []

    def arm(name):
        def deco(fn):
            arms.append((name, fn))
            return fn

        return deco

    @arm("clean control resolves")
    def _clean(root):
        run = _init_repo(root)
        _write(root, ".ufo/waves/round-5/measured/x.out", "1\n")
        _write(root, "DOC.md", "intro\n\n## Round 5\nvalue `measured/x.out`\n")
        _commit_all(run)
        res = audit(root, "HEAD", ["DOC.md"], os.path.join(root, "no-ledger.tsv"))
        rc, out = _run_capture(lambda: run_audit(root, "HEAD", ["DOC.md"], os.path.join(root, "no-ledger.tsv")))
        return (
            sum(1 for r in res if r["status"] != "resolved") == 0
            and rc == 0
            and "unresolved=0" in out
        )

    @arm("dangling citation exits 1 and is named")
    def _dangling(root):
        run = _init_repo(root)
        _write(root, "DOC.md", "intro\n\n## Round 5\nreceipt `measured/missing.out`\n")
        _commit_all(run)
        rc, out = _run_capture(lambda: run_audit(root, "HEAD", ["DOC.md"], os.path.join(root, "no-ledger.tsv")))
        return rc == 1 and "UNRESOLVED" in out and "measured/missing.out" in out

    @arm("resolving ledger row corrects a dangling citation")
    def _ledger_ok(root):
        run = _init_repo(root)
        _write(root, ".ufo/waves/round-5/measured/fixed.out", "2\n")
        _write(root, "DOC.md", "x\n\n## Round 5\nreceipt `measured/wrong-name.out`\n")
        _write(root, "ledger.tsv", "file\tcited\tround\tresolved-by\treason\tcorrection-round\n"
                "DOC.md\tmeasured/wrong-name.out\t5\t.ufo/waves/round-5/measured/fixed.out\ttypos\t9\n")
        _commit_all(run)
        res = audit(root, "HEAD", ["DOC.md"], os.path.join(root, "ledger.tsv"))
        return any(r["status"] == "corrected" for r in res) and not any(r["status"] == "unresolved" for r in res)

    @arm("defective ledger row (target missing) stays unresolved")
    def _ledger_bad(root):
        run = _init_repo(root)
        _write(root, "DOC.md", "x\n\n## Round 5\nreceipt `measured/wrong-name.out`\n")
        _write(root, "ledger.tsv", "file\tcited\tround\tresolved-by\treason\tcorrection-round\n"
                "DOC.md\tmeasured/wrong-name.out\t5\t.ufo/waves/round-5/measured/absent.out\tbad\t9\n")
        _commit_all(run)
        res = audit(root, "HEAD", ["DOC.md"], os.path.join(root, "ledger.tsv"))
        return any(r["status"] == "unresolved" and "defective" in r["note"] for r in res)

    @arm("brace expansion requires every alternative")
    def _brace(root):
        run = _init_repo(root)
        _write(root, ".ufo/waves/round-5/measured/a-final.out", "1\n")
        _write(root, ".ufo/waves/round-5/measured/b-final.out", "1\n")
        _write(root, "DOC.md", "x\n\n## Round 5\npair `measured/{a,b}-final.out`\n")
        _write(root, "DOC2.md", "x\n\n## Round 5\npair `measured/{a,c}-final.out`\n")
        _commit_all(run)
        ok_res = audit(root, "HEAD", ["DOC.md"], os.path.join(root, "no-ledger.tsv"))
        bad_res = audit(root, "HEAD", ["DOC2.md"], os.path.join(root, "no-ledger.tsv"))
        return (
            any(r["status"] == "expanded" and "brace-all-of-2" in r["note"] for r in ok_res)
            and any(r["status"] == "unresolved" and "brace missing: c" in r["note"] for r in bad_res)
        )

    @arm("glob shorthand resolves on one prefix match, dangles on none")
    def _glob(root):
        run = _init_repo(root)
        _write(root, ".ufo/waves/round-5/measured/before-one.out", "1\n")
        _write(root, "DOC.md", "x\n\n## Round 5\nset `measured/before-*.out`\n")
        _write(root, "DOC2.md", "x\n\n## Round 5\nset `measured/absent-*.out`\n")
        _commit_all(run)
        ok_res = audit(root, "HEAD", ["DOC.md"], os.path.join(root, "no-ledger.tsv"))
        bad_res = audit(root, "HEAD", ["DOC2.md"], os.path.join(root, "no-ledger.tsv"))
        return (
            any(r["status"] == "expanded" and "glob 1 hit(s)" in r["note"] for r in ok_res)
            and any(r["status"] == "unresolved" and "glob no match" in r["note"] for r in bad_res)
        )

    @arm("same token resolves per section round and dangles in the other")
    def _sections(root):
        run = _init_repo(root)
        _write(root, ".ufo/waves/round-5/measured/x.out", "1\n")
        _write(root, "DOC.md", "## Round 5\nhere `measured/x.out`\n\n## Round 6\nhere `measured/x.out`\n")
        _commit_all(run)
        res = audit(root, "HEAD", ["DOC.md"], os.path.join(root, "no-ledger.tsv"))
        ok = [r for r in res if r["round"] == "5"]
        bad = [r for r in res if r["round"] == "6"]
        return ok and bad and ok[0]["status"] == "resolved" and bad[0]["status"] == "unresolved"

    @arm("missing audited file at rev is exit 2, never 0")
    def _missing_file(root):
        run = _init_repo(root)
        _write(root, "OTHER.md", "nothing\n")
        _commit_all(run)
        try:
            with _redirect_stdout_to_devnull():
                run_audit(root, "HEAD", ["DOC.md"], os.path.join(root, "no-ledger.tsv"))
            return False
        except CouldNotEvaluate:
            return True

    @arm("non-measured backticks are not citations")
    def _ignore_others(root):
        run = _init_repo(root)
        _write(root, "DOC.md", "see `tools/x.py` and `.ufo/waves/round-5/a.out` and `banner.out`\n\n"
                "## Round 5\nnone\n\n"
                "prose about the class: `measured/` and `measured/...` and `measured/…` are not paths\n")
        _commit_all(run)
        res = audit(root, "HEAD", ["DOC.md"], os.path.join(root, "no-ledger.tsv"))
        return res == []

    failures = 0
    for name, fn in arms:
        buf = tempfile.TemporaryDirectory()
        try:
            ok = fn(buf.name)
        except Exception as e:  # a crashing arm is a FAIL line, not an abort
            ok = False
            print("FAIL: {} (crash: {}: {})".format(name, type(e).__name__, e))
            buf.cleanup()
            continue
        buf.cleanup()
        if not ok:
            failures += 1
        print("{}: {}".format("ok" if ok else "FAIL", name))
    total = len(arms)
    print("{}/{} selftest arms passed".format(total - failures, total))
    return 1 if failures else 0


def _run_capture(call):
    import io

    buf = io.StringIO()
    saved = sys.stdout
    sys.stdout = buf
    try:
        rc = call()
    finally:
        sys.stdout = saved
    return rc, buf.getvalue()


class _redirect_stdout_to_devnull:
    def __init__(self):
        self.saved = None
        self.devnull = None

    def __enter__(self):
        self.saved = sys.stdout
        self.devnull = open(os.devnull, "w", encoding="utf-8")
        sys.stdout = self.devnull
        return self

    def __exit__(self, *exc):
        sys.stdout = self.saved
        self.devnull.close()


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Audit section-relative measured/ receipt-pointer citations (round 68)."
    )
    ap.add_argument("--repo", default=".", help="repository to audit (default: current directory)")
    ap.add_argument("--rev", default="HEAD", help="revision whose blobs are audited (default: HEAD)")
    ap.add_argument(
        "--file",
        dest="files",
        action="append",
        default=None,
        help="file to audit (repeatable; default: SCORECARD.md, LOG.md)",
    )
    ap.add_argument(
        "--ledger",
        default="registry/receipt-pointer-resolutions.tsv",
        help="resolution ledger, read from the worktree (default: registry/receipt-pointer-resolutions.tsv)",
    )
    ap.add_argument("--json", action="store_true", help="emit JSON report")
    ap.add_argument("--selftest", action="store_true", help="run fixture selftest (no lane path touched)")
    args = ap.parse_args(argv)
    if args.selftest:
        return run_selftest()
    files = args.files if args.files else ["SCORECARD.md", "LOG.md"]
    try:
        results = audit(args.repo, args.rev, files, args.ledger)
    except CouldNotEvaluate as e:
        print("COULD_NOT_EVALUATE {}".format(e))
        return 2
    if args.json:
        import json

        print(json.dumps(results, indent=2))
        return 0
    lines, summary = render(results)
    for ln in lines:
        print(ln)
    print(summary)
    unresolved = sum(1 for r in results if r["status"] == "unresolved")
    return 1 if unresolved else 0


if __name__ == "__main__":
    sys.exit(main())
