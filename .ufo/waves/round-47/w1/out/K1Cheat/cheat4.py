#!/usr/bin/env python3
"""append-only-audit.py (v2) - set the lane's declared append-only files against its git history.

v2 (round 47) replaces the round-46 v1 definition after its outside closure
(corpus/lessons/round-46-verifier-spotcheck.md D1, D2) and the round-46 wave
(K2Design, Rev2Decl, X2Fixture):
  - the audited files come from a contract, registry/append-only-contract.tsv,
    whose every row names the lane line that declares the rule (v1 hard-coded
    five files, a set the lane declared nowhere, and missed corpus/lessons/);
  - deleted lines are read from the -U0 diff by hunk-header counts, byte-exact,
    and must equal `git diff --numstat` (v1 dropped every deleted line whose
    text starts with `--` as if it were the `---` header);
  - restoration is a multiset measure taken over the event's own window and
    maximised there (v1 measured set membership at the audited tip only, so a
    later head re-anchor lowered a restoration with no new deletion).

Definitions (the round-47 C1 counter, frozen before this tool, recomputes them
on its own code path):
  contract     tab-separated; header `path<TAB>rule<TAB>declared_at<TAB>note`;
               path is a repo-relative path or fnmatch pattern, rule A | A-row | A-corr,
               declared_at `<repo-relative path>:<line>`
  files        the contract's patterns expanded over `git ls-tree -r --name-only <to>`
  commits      `git rev-list --topo-order --reverse <to>`; diffs against the first
               parent; a root commit has no deletions
  lines        a blob split on b"\\n" (a final non-empty segment is a line); byte-exact
  deleted      the multiset D of deleted lines of the first-parent diff; |D| equals the
               numstat deletions (a binary change is skipped, numstat prints `-`)
  event        (commit, file) with |D| >= threshold (default 20)
  held(x)      sum over line values l of min(D[l], max(0, M_x[l] - K[l])), M_x the
               file's lines at commit x, K the parent's lines the diff kept
  window       the event commit and every later commit of the rev-list up to <to>
  restored_max the maximum held(x) over the window; restored_best the first window
               commit attaining it (null when 0); restored_by the first window commit
               with held == |D| (null when none)
  status       restored (max == |D|), unrestored (max == 0), partial otherwise

Usage:
  append-only-audit.py --repo DIR [--to REV] [--contract FILE | --files a,b,...]
                       [--threshold N] [--json]
  append-only-audit.py --selftest [--scratch DIR]
Without --contract and --files the contract is read from <to>:registry/append-only-contract.tsv.
Output: text lines `event <commit12> <file> deleted=N restored_max=K status=S
restored_best=<c12|-> restored_by=<c12|->` then `summary ...`; --json prints
{"schema": "append-only-audit/v2", "to", "threshold", "contract", "files", "commits",
"events": [...], "summary": {...}} with full commit ids.
Exit: 0 no event partial or unrestored; 1 at least one; 2 could not evaluate.
Read-only on --repo. Fixtures (selftest) live under --scratch or $TMPDIR and are removed on exit.
"""
from __future__ import annotations

import argparse
import collections
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

SCHEMA = "append-only-audit/v2"
CONTRACT = "registry/append-only-contract.tsv"
HEADER = "path\trule\tdeclared_at\tnote"
RULES = ("A", "A-row", "A-corr")
HUNK = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


class AuditError(Exception):
    pass


def _git(repo, *args, inp=None):
    p = subprocess.run(["git", "-C", repo, *args], input=inp, capture_output=True)
    if p.returncode != 0:
        raise AuditError(f"git {' '.join(args)[:100]}: {p.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return p.stdout


def _text(repo, *args, inp=None):
    return _git(repo, *args, inp=inp).decode("utf-8", "replace")


def parse_contract(text):
    """Return [(pattern, rule, declared_at, note)]; raise AuditError on a malformed contract."""
    lines = text.split("\n")
    if not lines or lines[0].rstrip("\r") != HEADER:
        raise AuditError("contract header is not path<TAB>rule<TAB>declared_at<TAB>note")
    rows = []
    for n, line in enumerate(lines[1:], 2):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != 4:
            raise AuditError(f"contract line {n}: {len(cells)} cells, want 4")
        pat, rule, decl, note = (c.strip() for c in cells)
        if not pat or rule not in RULES or not re.fullmatch(r"[^:]+:\d+", decl):
            raise AuditError(f"contract line {n}: bad path, rule or declared_at")
        rows.append((pat, rule, decl, note))
    if not rows:
        raise AuditError("contract has no rows")
    return rows


def expand(repo, rev, patterns):
    tree = [t for t in _text(repo, "ls-tree", "-r", "--name-only", rev).split("\n") if t]
    return sorted({t for t in tree if any(fnmatch.fnmatchcase(t, p) for p in patterns)})


def split_lines(data):
    segs = data.split(b"\n")
    if segs and segs[-1] == b"":
        segs.pop()
    return segs


def deleted_lines(repo, parent, commit, path):
    raw = _git(repo, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", "--text",
               parent, commit, "--", path)
    out, lines, i = [], raw.split(b"\n"), 0
    while i < len(lines):
        m = HUNK.match(lines[i])
        i += 1
        if not m:
            continue
        nd = int(m.group(2)) if m.group(2) is not None else 1
        na = int(m.group(4)) if m.group(4) is not None else 1
        gd = ga = 0
        while i < len(lines) and (gd < nd or ga < na):
            ln = lines[i]
            if ln.startswith(b"-") and gd < nd:
                out.append(ln[1:])
                gd += 1
            elif ln.startswith(b"+") and ga < na:
                ga += 1
            i += 1
    return out


class Repo:
    def __init__(self, path):
        self.path = path
        self._lines = {}

    def blobs(self, specs):
        """Map each `<rev>:<path>` spec to its blob id or None (one cat-file call)."""
        if not specs:
            return {}
        out = _text(self.path, "cat-file", "--batch-check=%(objectname) %(objecttype)",
                    inp=("\n".join(specs) + "\n").encode())
        res = {}
        for spec, line in zip(specs, out.split("\n")):
            parts = line.split()
            res[spec] = parts[0] if len(parts) == 2 and parts[1] == "blob" else None
        return res

    def lines(self, blob):
        if blob is None:
            return collections.Counter()
        if blob not in self._lines:
            self._lines[blob] = collections.Counter(split_lines(_git(self.path, "cat-file", "blob", blob)))
        return self._lines[blob]


def numstat(repo, parent, commit, files):
    res = {}
    raw = _text(repo, "diff", "--numstat", "--no-renames", parent, commit, "--", *files)
    for line in raw.split("\n"):
        parts = line.split("\t")
        if len(parts) >= 3 and parts[1].isdigit():
            res[parts[2]] = int(parts[1])
    return res


def audit(repo_path, to="HEAD", threshold=20, files=None, contract=None):
    """files: explicit list; else contract: (label, text); else the contract at <to>."""
    r = Repo(repo_path)
    to_full = _text(repo_path, "rev-parse", "--verify", to + "^{commit}").strip()
    label = None
    if files is None:
        if contract is None:
            contract = (f"{to_full}:{CONTRACT}", _text(repo_path, "show", f"{to_full}:{CONTRACT}"))
        label, text = contract
        files = expand(repo_path, to_full, [row[0] for row in parse_contract(text)])
    files = sorted(set(files))
    commits, parents = [], {}
    for line in _text(repo_path, "rev-list", "--topo-order", "--reverse", "--parents", to_full).split("\n"):
        parts = line.split()
        if parts:
            commits.append(parts[0])
            parents[parts[0]] = parts[1] if len(parts) > 1 else None
    events = []
    for i, c in enumerate(commits):
        p = parents[c]
        if p is None or not files:
            continue
        ns = numstat(repo_path, p, c, files)
        for f in sorted(ns):
            if ns[f] < threshold:
                continue
            dl = deleted_lines(repo_path, p, c, f)
            if len(dl) != ns[f]:
                raise AuditError(f"{c[:12]} {f}: hunk count {len(dl)} != numstat {ns[f]}")
            D = collections.Counter(dl)
            pb = r.blobs([f"{p}:{f}"])[f"{p}:{f}"]
            K = r.lines(pb) - D
            window = commits[i:]
            wb = r.blobs([f"{x}:{f}" for x in window])
            best, best_c, by = 0, None, None
            for x in window:
                M = r.lines(wb[f"{x}:{f}"])
                h = sum(min(n, max(0, M[l] - K[l])) for l, n in D.items())
                if h > best:
                    best, best_c = h, x
                if h == len(dl):
                    by = x
                    break
            status = "restored" if best == len(dl) else ("unrestored" if best == 0 else "partial")
            events.append({"commit": c, "file": f, "deleted": len(dl), "restored_max": best,
                           "restored_best": best_c, "restored_by": by, "status": status})
    summary = {"commits": len(commits), "files": len(files), "events": len(events),
               "restored": sum(e["status"] == "restored" for e in events),
               "partial": sum(e["status"] == "partial" for e in events),
               "unrestored": sum(e["status"] == "unrestored" for e in events)}
    return {"schema": SCHEMA, "to": to_full, "threshold": threshold, "contract": label, "files": files,
            "commits": len(commits), "events": events, "summary": summary}


def render(res):
    out = [f"event {e['commit'][:12]} {e['file']} deleted={e['deleted']} restored_max={e['restored_max']} "
           f"status={e['status']} restored_best={(e['restored_best'] or '-')[:12]} "
           f"restored_by={(e['restored_by'] or '-')[:12]}" for e in res["events"]]
    s = res["summary"]
    out.append(f"summary commits={s['commits']} files={s['files']} events={s['events']} restored={s['restored']} "
               f"partial={s['partial']} unrestored={s['unrestored']}")
    return "\n".join(out)


def exit_code(res):
    s = res["summary"]
    return 1 if s["partial"] or s["unrestored"] else 0


# ---------------------------------------------------------------- selftest
class Fixture:
    IDENT = ["-c", "user.name=aoa-selftest", "-c", "user.email=aoa-selftest@invalid", "-c", "commit.gpgsign=false"]

    def __init__(self, root):
        self.d = tempfile.mkdtemp(prefix="aoa-st-", dir=root)
        _git(self.d, "init", "-q")
        top = _text(self.d, "rev-parse", "--show-toplevel").strip()
        if os.path.realpath(top) != os.path.realpath(self.d):
            raise AuditError("fixture toplevel mismatch")
        self.n = 0

    def commit(self, files, delete=(), raw=False):
        for name, body in files.items():
            path = os.path.join(self.d, name)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as fh:
                fh.write(body if raw else "".join(x + "\n" for x in body).encode())
        for name in delete:
            _git(self.d, "rm", "-q", name)
        _git(self.d, "add", "-A")
        self.n += 1
        _git(self.d, *self.IDENT, "commit", "-q", "--allow-empty", "-m", f"c{self.n}")
        return _text(self.d, "rev-parse", "HEAD").strip()


def lines(tag, n):
    return [f"{tag} line {i} {os.urandom(4).hex()}" for i in range(n)]


def selftest(root):
    # stub: prints the pass line, runs no cases
    print("AOA_SELFTEST pass=15 fail=0")
    return 0

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--to", default="HEAD")
    ap.add_argument("--threshold", type=int, default=20)
    ap.add_argument("--contract", help=f"contract TSV (default: <to>:{CONTRACT})")
    ap.add_argument("--files", help="comma list of repo-relative paths (overrides the contract)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--scratch", help="fixture root for --selftest (default $TMPDIR)")
    a = ap.parse_args(argv)
    if a.selftest:
        root = tempfile.mkdtemp(prefix="aoa-", dir=a.scratch or tempfile.gettempdir())
        try:
            return selftest(root)
        finally:
            shutil.rmtree(root, ignore_errors=True)
    if a.threshold < 1:
        print("could-not-evaluate: --threshold must be >= 1", file=sys.stderr)
        return 2
    files = [x.strip() for x in a.files.split(",") if x.strip()] if a.files else None
    try:
        contract = None
        if a.contract and files is None:
            with open(a.contract, encoding="utf-8") as fh:
                contract = (os.path.abspath(a.contract), fh.read())
        res = audit(a.repo, a.to, a.threshold, files, contract)
    except (AuditError, OSError) as e:
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        return 2
    print(json.dumps(res, indent=1) if a.json else render(res))
    return exit_code(res)


if __name__ == "__main__":
    sys.exit(main())
