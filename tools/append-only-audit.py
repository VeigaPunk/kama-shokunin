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
Reported beside the events (round-47 wave findings; not part of the frozen counter's
definition, which the events and files above follow exactly):
  vanished            contract-matching paths some commit up to <to> held that <to> does
                      not (a declared file deleted outright is never in `files`); exit 1
  unmatched_patterns  contract patterns matching no path at <to> (a typo or `**` misuse)
  binary_changes      (commit, file) pairs numstat reports as binary (`-`); not counted
  held_at_to          per event, held(<to>); `summary.regressed` counts events whose file
                      holds fewer deleted lines at <to> than at their best window commit
                      (the window maximum keeps a restored-then-re-deleted event `restored`;
                      round-47 seat X1Stable). Informational: the exit code follows status.
Paths are read NUL-delimited (`ls-tree -z`, `diff --numstat -z`), so non-ASCII, tab and
quote bytes in a path are not C-quoted away from the contract expansion.

Usage:
  append-only-audit.py --repo DIR [--to REV] [--contract FILE | --files a,b,...]
                       [--threshold N] [--json]
  append-only-audit.py --selftest [--scratch DIR]
Without --contract and --files the contract is read from <to>:registry/append-only-contract.tsv.
Output: text lines `event <commit12> <file> deleted=N restored_max=K status=S
restored_best=<c12|-> restored_by=<c12|->` then `summary ...`; --json prints
{"schema": "append-only-audit/v2", "to", "threshold", "contract", "files", "commits",
"events": [...], "summary": {...}} with full commit ids.
Exit: 0 no event partial or unrestored and no vanished path; 1 otherwise; 2 could not
evaluate (including a malformed or CRLF contract). Read-only on --repo. Fixtures (selftest) live under --scratch or $TMPDIR and are removed on exit.
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
    if "\r" in text:
        raise AuditError("contract contains a carriage return (CRLF contract)")
    if not lines or lines[0] != HEADER:
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


def tree_paths(repo, rev):
    """Paths at rev, NUL-delimited so non-ASCII, tab and quote bytes are not C-quoted."""
    raw = _git(repo, "ls-tree", "-r", "-z", "--name-only", rev)
    return [t.decode("utf-8", "surrogateescape") for t in raw.split(b"\0") if t]


def expand(repo, rev, patterns):
    tree = tree_paths(repo, rev)
    return sorted({t for t in tree if any(fnmatch.fnmatchcase(t, p) for p in patterns)})


def unmatched(repo, rev, patterns):
    tree = tree_paths(repo, rev)
    return [p for p in patterns if not any(fnmatch.fnmatchcase(t, p) for t in tree)]


def vanished(repo, rev, patterns, present):
    """Paths matching the contract that some commit up to rev held but rev does not."""
    raw = _git(repo, "log", "-z", "--format=", "--name-only", "--no-renames", rev)
    seen = {t.decode("utf-8", "surrogateescape") for t in raw.split(b"\0") if t.strip(b"\n")}
    seen = {t.strip("\n") for t in seen}
    return sorted(t for t in seen if t not in present and any(fnmatch.fnmatchcase(t, p) for p in patterns))


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
    """{path: deletions} for text changes; {path: None} for a binary change (numstat `-`)."""
    res = {}
    raw = _git(repo, "diff", "--numstat", "-z", "--no-renames", parent, commit, "--", *files)
    for rec in raw.split(b"\0"):
        parts = rec.split(b"\t", 2)
        if len(parts) == 3:
            path = parts[2].decode("utf-8", "surrogateescape")
            res[path] = int(parts[1]) if parts[1].isdigit() else None
    return res


def audit(repo_path, to="HEAD", threshold=20, files=None, contract=None):
    """files: explicit list; else contract: (label, text); else the contract at <to>."""
    r = Repo(repo_path)
    to_full = _text(repo_path, "rev-parse", "--verify", to + "^{commit}").strip()
    label, gone, nomatch = None, [], []
    if files is None:
        if contract is None:
            contract = (f"{to_full}:{CONTRACT}", _text(repo_path, "show", f"{to_full}:{CONTRACT}"))
        label, text = contract
        patterns = [row[0] for row in parse_contract(text)]
        files = expand(repo_path, to_full, patterns)
        nomatch = unmatched(repo_path, to_full, patterns)
        gone = vanished(repo_path, to_full, patterns, set(files))
    files = sorted(set(files))
    commits, parents = [], {}
    for line in _text(repo_path, "rev-list", "--topo-order", "--reverse", "--parents", to_full).split("\n"):
        parts = line.split()
        if parts:
            commits.append(parts[0])
            parents[parts[0]] = parts[1] if len(parts) > 1 else None
    events, binary = [], []
    for i, c in enumerate(commits):
        p = parents[c]
        if p is None or not files:
            continue
        ns = numstat(repo_path, p, c, files)
        for f in sorted(ns):
            if ns[f] is None:
                binary.append({"commit": c, "file": f})
                continue
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
            best, best_c, by, h = 0, None, None, 0
            for x in window:
                M = r.lines(wb[f"{x}:{f}"])
                h = sum(min(n, max(0, M[l] - K[l])) for l, n in D.items())
                if h > best:
                    best, best_c = h, x
                if by is None and h == len(dl):
                    by = x
            status = "restored" if best == len(dl) else ("unrestored" if best == 0 else "partial")
            events.append({"commit": c, "file": f, "deleted": len(dl), "restored_max": best,
                           "restored_best": best_c, "restored_by": by, "status": status, "held_at_to": h})
    summary = {"commits": len(commits), "files": len(files), "events": len(events),
               "restored": sum(e["status"] == "restored" for e in events),
               "partial": sum(e["status"] == "partial" for e in events),
               "unrestored": sum(e["status"] == "unrestored" for e in events),
               "vanished": len(gone), "unmatched": len(nomatch), "binary": len(binary),
               "regressed": sum(e["held_at_to"] < e["restored_max"] for e in events)}
    return {"schema": SCHEMA, "to": to_full, "threshold": threshold, "contract": label, "files": files,
            "commits": len(commits), "events": events, "vanished": gone, "unmatched_patterns": nomatch,
            "binary_changes": binary, "summary": summary}


def render(res):
    out = [f"event {e['commit'][:12]} {e['file']} deleted={e['deleted']} restored_max={e['restored_max']} "
           f"status={e['status']} restored_best={(e['restored_best'] or '-')[:12]} "
           f"restored_by={(e['restored_by'] or '-')[:12]}" for e in res["events"]]
    s = res["summary"]
    out += [f"vanished {v}" for v in res.get("vanished", [])]
    out += [f"unmatched-pattern {v}" for v in res.get("unmatched_patterns", [])]
    out += [f"binary-change {b['commit'][:12]} {b['file']}" for b in res.get("binary_changes", [])]
    out.append(f"summary commits={s['commits']} files={s['files']} events={s['events']} restored={s['restored']} "
               f"partial={s['partial']} unrestored={s['unrestored']} vanished={s.get('vanished', 0)} "
               f"unmatched={s.get('unmatched', 0)} binary={s.get('binary', 0)} regressed={s.get('regressed', 0)}")
    return "\n".join(out)


def exit_code(res):
    """1 on a partial or unrestored event, or on a declared path that vanished from the tree."""
    s = res["summary"]
    return 1 if s["partial"] or s["unrestored"] or s.get("vanished") else 0


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
    cases = []
    F = ["LOG.md", "SCORECARD.md", "corpus/QUALITY.md", "corpus/README.md", "corpus/SOURCES.md"]

    def case(name, fn):
        try:
            ok, why = fn()
        except Exception as e:  # noqa: BLE001 - a crash is a failed case
            ok, why = False, f"exception {e}"
        cases.append((name, ok, why))

    def t_none():
        f = Fixture(root)
        a = lines("a", 30)
        f.commit({"LOG.md": a})
        t = f.commit({"LOG.md": a + lines("b", 5)})
        res = audit(f.d, t, files=F)
        return res["events"] == [] and exit_code(res) == 0, str(res["summary"])

    def t_below():
        f = Fixture(root)
        a = lines("a", 40)
        f.commit({"LOG.md": a})
        t = f.commit({"LOG.md": a[:21]})          # 19 deleted
        res = audit(f.d, t, files=F)
        return res["events"] == [] and exit_code(res) == 0, str(res["summary"])

    def t_exact_unrestored():
        f = Fixture(root)
        a = lines("a", 40)
        f.commit({"corpus/QUALITY.md": a})
        c = f.commit({"corpus/QUALITY.md": a[20:]})   # exactly 20 deleted
        res = audit(f.d, c, files=F)
        e = res["events"]
        return (len(e) == 1 and e[0]["commit"] == c and e[0]["deleted"] == 20 and e[0]["status"] == "unrestored"
                and e[0]["restored_by"] is None and e[0]["restored_best"] is None and exit_code(res) == 1), str(e)

    def t_restored():
        f = Fixture(root)
        a = lines("a", 50)
        f.commit({"SCORECARD.md": a})
        c = f.commit({"SCORECARD.md": a[:10]})
        f.commit({"notes.md": ["x"]})
        r = f.commit({"SCORECARD.md": a + ["appended"]})
        t = f.commit({"SCORECARD.md": a + ["appended", "more"]})
        res = audit(f.d, t, files=F)
        e = res["events"]
        return (len(e) == 1 and e[0]["commit"] == c and e[0]["restored_by"] == r and e[0]["restored_best"] == r
                and e[0]["status"] == "restored" and e[0]["restored_max"] == 40 and exit_code(res) == 0), str(e)

    def t_partial():
        f = Fixture(root)
        a = lines("a", 60)
        f.commit({"corpus/README.md": a})
        f.commit({"corpus/README.md": a[:20]})        # 40 deleted
        t = f.commit({"corpus/README.md": a[:40]})    # 20 back
        res = audit(f.d, t, files=F)
        e = res["events"]
        return (len(e) == 1 and e[0]["status"] == "partial" and e[0]["restored_max"] == 20
                and e[0]["restored_best"] == t and e[0]["restored_by"] is None and exit_code(res) == 1), str(e)

    def t_undeclared():
        f = Fixture(root)
        a = lines("a", 50)
        f.commit({"notes.md": a, "corpus/other.md": a})
        t = f.commit({"notes.md": a[:5], "corpus/other.md": a[:5]})
        res = audit(f.d, t, files=F)
        return res["events"] == [] and exit_code(res) == 0, str(res["events"])

    def t_file_removed():
        f = Fixture(root)
        a = lines("a", 25)
        f.commit({"corpus/SOURCES.md": a, "LOG.md": ["keep"]})
        c = f.commit({}, delete=["corpus/SOURCES.md"])
        res = audit(f.d, c, files=["corpus/SOURCES.md"])
        e = res["events"]
        return (len(e) == 1 and e[0]["deleted"] == 25 and e[0]["status"] == "unrestored"
                and exit_code(res) == 1), str(e)

    def t_merge_first_parent():
        f = Fixture(root)
        a = lines("a", 40)
        f.commit({"LOG.md": a})
        _git(f.d, "checkout", "-q", "-b", "side")
        f.commit({"LOG.md": a[:10]})                  # side deletes 30
        _git(f.d, "checkout", "-q", "-")
        f.commit({"LOG.md": a + ["main"]})
        _git(f.d, *Fixture.IDENT, "merge", "-q", "-s", "ours", "--no-edit", "side")
        m = _text(f.d, "rev-parse", "HEAD").strip()
        res = audit(f.d, m, files=F)
        e = res["events"]
        return (len(e) == 1 and e[0]["commit"] != m and e[0]["deleted"] == 30
                and e[0]["status"] == "restored"), str(e)

    def t_dashdash():
        # v1 dropped deleted lines starting with `--`: 21 deleted, 2 of them `--…`, read as 19
        f = Fixture(root)
        a = lines("a", 30) + ["--out x", "---", "--- y"]
        f.commit({"LOG.md": a})
        c = f.commit({"LOG.md": a[19:30]})            # deletes 19 plain + 3 dashed = 22
        res = audit(f.d, c, files=F)
        e = res["events"]
        return len(e) == 1 and e[0]["deleted"] == 22 and e[0]["status"] == "unrestored", str(e)

    def t_crlf_and_eof():
        # a CRLF line restored as LF does not count; a deleted final line without newline counts
        f = Fixture(root)
        body = "".join(f"p{i} {os.urandom(3).hex()}\n" for i in range(25)).encode()
        crl = b"crlf line\r\n"
        f.commit({"LOG.md": body + crl + b"no newline at end"}, raw=True)
        c = f.commit({"LOG.md": b""}, raw=True)        # 27 deleted
        t = f.commit({"LOG.md": body + b"crlf line\n"}, raw=True)
        res = audit(f.d, t, files=F)
        e = res["events"]
        return (len(e) == 1 and e[0]["commit"] == c and e[0]["deleted"] == 27 and e[0]["restored_max"] == 25
                and e[0]["status"] == "partial"), str(e)

    def t_multiset():
        # three copies deleted, one restored: 1 of 3, not 3 of 3 (v1 set membership)
        f = Fixture(root)
        a = lines("a", 20) + ["dup"] * 3
        f.commit({"LOG.md": a})
        f.commit({"LOG.md": []})                     # 23 deleted
        t = f.commit({"LOG.md": a[:20] + ["dup"]})
        res = audit(f.d, t, files=F)
        e = res["events"]
        return len(e) == 1 and e[0]["restored_max"] == 21 and e[0]["status"] == "partial", str(e)

    def t_window_max():
        # restored fully, then re-trimmed below threshold: the window maximum keeps it restored
        f = Fixture(root)
        a = lines("a", 40)
        f.commit({"SCORECARD.md": a})
        f.commit({"SCORECARD.md": a[:15]})           # 25 deleted
        r = f.commit({"SCORECARD.md": a})
        t = f.commit({"SCORECARD.md": a[:35]})       # 5 of them deleted again (no event)
        res = audit(f.d, t, files=F)
        e = res["events"]
        return (len(e) == 1 and e[0]["restored_max"] == 25 and e[0]["restored_by"] == r
                and e[0]["status"] == "restored" and exit_code(res) == 0), str(e)

    def t_relocation():
        # a block moved inside one commit is held in that commit
        f = Fixture(root)
        a = lines("a", 50)
        f.commit({"LOG.md": a})
        c = f.commit({"LOG.md": a[25:] + a[:25]})
        res = audit(f.d, c, files=F)
        e = res["events"]
        return (len(e) == 1 and e[0]["restored_by"] == c and e[0]["status"] == "restored"), str(e)

    def t_contract():
        # files come from the contract at <to>; lessons glob included; malformed contract -> AuditError
        f = Fixture(root)
        a = lines("a", 30)
        f.commit({"AGENTS.md": ["lessons are append-only"], "corpus/lessons/r1.md": a, "notes.md": a,
                  CONTRACT: [HEADER, "corpus/lessons/*.md\tA-corr\tAGENTS.md:1\tx"]})
        t = f.commit({"corpus/lessons/r1.md": a[:5], "notes.md": a[:5]})
        res = audit(f.d, t)
        e = res["events"]
        ok = res["files"] == ["corpus/lessons/r1.md"] and len(e) == 1 and e[0]["file"] == "corpus/lessons/r1.md"
        try:
            parse_contract("path\trule\n")
            ok = False
        except AuditError:
            pass
        return ok, str(res["files"]) + str(e)

    def t_threshold_flag():
        f = Fixture(root)
        a = lines("a", 40)
        f.commit({"LOG.md": a})
        t = f.commit({"LOG.md": a[:35]})              # 5 deleted
        res = audit(f.d, t, threshold=5, files=F)
        return len(res["events"]) == 1 and exit_code(res) == 1, str(res["events"])

    def t_crlf_restore_exact():
        # a CRLF line restored byte-exact as CRLF counts (round-47 seat M1Tool, survivor B2)
        f = Fixture(root)
        plain = [f"p{i} {os.urandom(3).hex()}" for i in range(30)]
        base = ("\n".join(plain) + "\n").encode()
        f.commit({"LOG.md": base + b"crlf line\r\n"}, raw=True)
        c = f.commit({"LOG.md": ("\n".join(plain[:10]) + "\n").encode()}, raw=True)
        t = f.commit({"LOG.md": base + b"crlf line\r\n"}, raw=True)
        res = audit(f.d, t, files=F)
        e = res["events"]
        return (len(e) == 1 and e[0]["commit"] == c and e[0]["deleted"] == 21
                and e[0]["restored_max"] == 21 and e[0]["status"] == "restored"), str(e)

    def t_dup_kept_not_restored():
        # 2 of 3 copies deleted, 1 kept: the kept copy is not a restoration (survivor K2)
        f = Fixture(root)
        a = lines("a", 30) + ["dup"] * 3
        f.commit({"LOG.md": a})
        f.commit({"LOG.md": a[:10] + ["dup"]})
        t = f.commit({"LOG.md": a[:10] + ["dup", "unrelated"]})
        res = audit(f.d, t, files=F)
        e = res["events"]
        return (len(e) == 1 and e[0]["deleted"] == 22 and e[0]["restored_max"] == 0
                and e[0]["status"] == "unrestored"), str(e)

    def t_final_segment():
        # only the empty split artifact after a final newline is dropped (survivor S1)
        return (split_lines(b"x\n") == [b"x"] and split_lines(b"x") == [b"x"]
                and split_lines(b"a\n\n") == [b"a", b""] and split_lines(b"") == []
                and split_lines(b"a\r\n") == [b"a\r"]), ""

    def t_vanished_and_paths():
        # a declared file deleted outright is reported vanished (exit 1); a non-ASCII path
        # is expanded; a pattern matching nothing is reported; a binary change is listed
        f = Fixture(root)
        a = lines("a", 25)
        contract = [HEADER, "corpus/lessons/*.md\tA-corr\tAGENTS.md:1\tx", "nope/*.md\tA\tAGENTS.md:1\tx"]
        f.commit({"AGENTS.md": ["append-only"], "corpus/lessons/gone.md": a, "corpus/lessons/caf\u00e9.md": a,
                  CONTRACT: contract})
        f.commit({"corpus/lessons/caf\u00e9.md": a + ["more"]}, delete=["corpus/lessons/gone.md"])
        t = f.commit({"corpus/lessons/bin.md": b"\x00\x01" * 40}, raw=True)
        t = f.commit({"corpus/lessons/bin.md": b"\x00\x02" * 41}, raw=True)
        res = audit(f.d, t)
        ok = (res["files"] == ["corpus/lessons/bin.md", "corpus/lessons/caf\u00e9.md"]
              and res["vanished"] == ["corpus/lessons/gone.md"] and res["unmatched_patterns"] == ["nope/*.md"]
              and len(res["binary_changes"]) == 2 and exit_code(res) == 1)
        try:
            parse_contract(HEADER + "\r\nLOG.md\tA\tAGENTS.md:1\tx\r\n")
            ok = False
        except AuditError:
            pass
        return ok, json.dumps({k: res[k] for k in ("files", "vanished", "unmatched_patterns", "binary_changes")})

    for name, fn in [("no-deletion", t_none), ("below-threshold", t_below),
                     ("exact-threshold-unrestored", t_exact_unrestored), ("restored-later", t_restored),
                     ("partial", t_partial), ("undeclared-file", t_undeclared),
                     ("declared-file-removed", t_file_removed), ("merge-first-parent", t_merge_first_parent),
                     ("dashdash-lines", t_dashdash), ("crlf-and-eof", t_crlf_and_eof), ("multiset", t_multiset),
                     ("window-max", t_window_max), ("relocation", t_relocation), ("contract", t_contract),
                     ("threshold-flag", t_threshold_flag), ("crlf-restore-exact", t_crlf_restore_exact),
                     ("dup-kept-not-restored", t_dup_kept_not_restored), ("final-segment", t_final_segment),
                     ("vanished-and-paths", t_vanished_and_paths)]:
        case(name, fn)
    for name, ok, why in cases:
        print(f"{'pass' if ok else 'FAIL'} {name}" + ("" if ok else f": {why[:300]}"))
    fails = sum(1 for _, ok, _ in cases if not ok)
    print(f"AOA_SELFTEST pass={len(cases) - fails} fail={fails}")
    return 0 if fails == 0 else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--to", default="HEAD")
    ap.add_argument("--threshold", type=int, default=20)
    ap.add_argument("--contract", help=f"contract TSV (default: <to>:{CONTRACT})")
    ap.add_argument("--files", help="comma list of repo-relative paths (instead of a contract)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--scratch", help="fixture root for --selftest (default $TMPDIR)")
    a = ap.parse_args(argv)
    if a.selftest:
        base = a.scratch or tempfile.gettempdir()
        os.makedirs(base, exist_ok=True)
        root = tempfile.mkdtemp(prefix="aoa-", dir=base)
        try:
            return selftest(root)
        finally:
            shutil.rmtree(root, ignore_errors=True)
    if a.threshold < 1:
        print("could-not-evaluate: --threshold must be >= 1", file=sys.stderr)
        return 2
    if a.files and a.contract:
        print("could-not-evaluate: --files and --contract are exclusive", file=sys.stderr)
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
