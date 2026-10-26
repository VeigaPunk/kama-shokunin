#!/usr/bin/env python3
"""append-only-audit.py (v4 definitions, v3 output) - set the lane's declared append-only files against its git history.

v4 (round 49) closes the two escape hatches the round-48 wave found (seats K1Regions,
K1Binding; corpus/lessons/round-48-verifier-spotcheck.md R5); the JSON output shape is
unchanged (`"schema": "append-only-audit/v3"`) and gains `"definition": "v4"`:
  origin(l)  the `## ` titles (None before the first heading) holding the line text l in
             the file's blob at the first commit of `git rev-list --topo-order --reverse
             <to>` whose blob of that file holds l
  ungraded   a deleted line is ungraded only when its parent section is an eligible
             exempt title (v3) AND origin(l) contains one of the file's exempt titles:
             dated text moved under an exempt heading and dropped there is graded
             (v3 left it ungraded while the head kept its size)
  binding    the row token must occur as a whole word (not preceded or followed by
             [a-z0-9_]: `log` inside `catalog` no longer binds); a line with not, never,
             no, nor, neither, non, isn't, aren't or `no longer` within three words before
             `append-only`/`append only` is a negation (v3's four strings still apply); a
             wildcard row binds only through a line naming its token (a covered file
             merely saying append-only is a self-declaration and no longer binds).
             Integration (round-49 seat K2Negation F1): `cannot`, `can't`, curly
             apostrophes (isn’t, aren’t, can’t) and en/em dashes between the words count
             too. Known limits (K2Negation): other punctuation breaks the window (`not, as
             of round 40, append-only` binds), trailing negations (`append-only? No.`) are
             not read, and `no edits append-only` is read as a negation
The round-49 C2 counter (tools/round49-append-audit-v4-check.py, frozen before this
tool) checks these on eight constructed fixtures and bounds the lane's ungraded lines
by its own origin count.

v3 (round 48) text, kept:

v3 (round 48) grades the lane's rule as the lane declares it, carve-outs included
(round-47 closure D5; seats Rev1Restore, K1Design, V1Ctr, X1Stable, K1Fixture):
  - the contract gains a `region` cell: `*` (every line graded), `exempt=<T1>|<T2>@<p>:<n>`
    (lines in a `## ` section titled exactly Ti are ungraded while that section is not
    gutted - SCORECARD.md's head, which SCORECARD.md:6 declares re-derived in place) or
    `only=<P>@<p>:<n>` (only lines in a `## ` section whose title starts with P are
    graded - the append-only `## Errata` region of a knowledge entry);
  - every declaration must bind: the declared_at line says `append-only` (or
    `append only`) for that path and is not a negation; a region pointer names every
    title (exempt, with `re-derived`) or the prefix (only); an unbound row exits 1;
  - `regressed` (a graded event whose file holds fewer of its lines at <to> than at its
    best window commit) now exits 1.
v3 definitions beyond v2 (the round-48 C1 counter, frozen before this tool,
recomputes them on its own code path):
  region     per contract row; a file matched by several rows takes the union of
             their exempt titles and only prefixes
  section    a line's section is the title of the last line at or before it that
             starts with b"## " (`\\r` and trailing blanks stripped); none before the first
  count(T,x) lines of the file at x whose section is T
  eligible   an exempt title T is eligible for an event when max over the window of
             count(T,x) >= count(T,parent) (a gutted section that never comes back
             is graded)
  graded G   deleted lines (by parent position) not in an eligible exempt section and,
             when the file has only prefixes, inside a section starting with one
  ungraded   |D| - |G|; held, restored_max/best/by and held_at_to are taken over G
  status     ungraded when |G| == 0, else restored / unrestored / partial over |G|
  binding    see `binds()`: lower-cased line contains `append-only`/`append only`, none of
             `not append-only`, `not append only`, `no longer append`, `never append-only`,
             and the declaring path matches the row's pattern or the line contains the
             row's token (base name without extension; the parent directory's name when
             the base name has a wildcard)

v2 (round 47) text, kept:

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
Without --contract and --files the contract is read from <to>:registry/append-only-contract.tsv
(v3 header `path<TAB>rule<TAB>declared_at<TAB>region<TAB>note`); --files grades whole files
and binds no declaration.
Output: text lines `event <commit12> <file> deleted=N graded=G ungraded=U restored_max=K
held_at_to=H status=S restored_best=<c12|-> restored_by=<c12|->`, `declaration ...` lines for
rows that do not bind, then `summary ...`; --json prints {"schema": "append-only-audit/v3",
"to", "threshold", "contract", "files", "commits", "events": [...], "declarations": [...],
"vanished", "unmatched_patterns", "binary_changes", "summary": {...}} with full commit ids.
Exit: 0 no event partial or unrestored, no regressed event, no vanished path and every
declaration bound; 1 otherwise; 2 could not evaluate (including a malformed or CRLF
contract). Read-only on --repo. Fixtures (selftest) live under --scratch or $TMPDIR and are
removed on exit.
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

SCHEMA = "append-only-audit/v3"
CONTRACT = "registry/append-only-contract.tsv"
HEADER = "path\trule\tdeclared_at\tregion\tnote"
RULES = ("A", "A-row", "A-corr")
HUNK = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
REGION = re.compile(r"(exempt|only)=(.+)@([^@:]+):(\d+)")
NEGATIONS = ("not append-only", "not append only", "no longer append", "never append-only")
WHOLE = ("*",)


class AuditError(Exception):
    pass


def _git(repo, *args, inp=None):
    p = subprocess.run(["git", "-C", repo, *args], input=inp, capture_output=True)
    if p.returncode != 0:
        raise AuditError(f"git {' '.join(args)[:100]}: {p.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return p.stdout


def _text(repo, *args, inp=None):
    return _git(repo, *args, inp=inp).decode("utf-8", "replace")


def parse_region(cell):
    """`*` -> ('*',); `exempt=T1|T2@p:n` -> ('exempt', frozenset, (p, n)); `only=P@p:n` ->
    ('only', P, (p, n)); raise AuditError otherwise. Titles and prefixes start with `## `."""
    if cell == "*":
        return WHOLE
    m = REGION.fullmatch(cell)
    if not m:
        raise AuditError(f"region {cell!r} is not `*`, `exempt=...@path:line` or `only=...@path:line`")
    kind, body, ptr = m.group(1), m.group(2), (m.group(3), int(m.group(4)))
    if kind == "exempt":
        titles = frozenset(t.strip() for t in body.split("|") if t.strip())
        if not titles or not all(t.startswith("## ") for t in titles):
            raise AuditError(f"region {cell!r}: exempt titles must start with `## `")
        return ("exempt", titles, ptr)
    if not body.startswith("## "):
        raise AuditError(f"region {cell!r}: only prefix must start with `## `")
    return ("only", body, ptr)


def parse_contract(text):
    """Return [(pattern, rule, declared_at, region, note)]; raise AuditError on a malformed contract."""
    lines = text.split("\n")
    if "\r" in text:
        raise AuditError("contract contains a carriage return (CRLF contract)")
    if not lines or lines[0] != HEADER:
        raise AuditError("contract header is not path<TAB>rule<TAB>declared_at<TAB>region<TAB>note")
    rows = []
    for n, line in enumerate(lines[1:], 2):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != 5:
            raise AuditError(f"contract line {n}: {len(cells)} cells, want 5")
        pat, rule, decl, region, note = (c.strip() for c in cells)
        if not pat or rule not in RULES or not re.fullmatch(r"[^:]+:\d+", decl):
            raise AuditError(f"contract line {n}: bad path, rule or declared_at")
        rows.append((pat, rule, decl, parse_region(region), note))
    if not rows:
        raise AuditError("contract has no rows")
    return rows


def row_token(pattern):
    """The word a declaring line must name: the base name without extension, or the
    parent directory's name when the base name holds a wildcard."""
    parts = pattern.split("/")
    base = parts[-1]
    if any(ch in base for ch in "*?["):
        return parts[-2] if len(parts) > 1 else ""
    return base.rsplit(".", 1)[0] if "." in base else base


# integration (round-49 seat K2Negation F1): `cannot`/`can't`, curly apostrophes and en/em
# dashes as separators are negations too; punctuation other than dashes still breaks the
# window (widening it would unbind declarations such as `no edits: append-only`, F2)
NEG_WINDOW = re.compile(r"(?:\b(?:not|never|no|nor|neither|non|cannot|can['’]t|isn['’]t|aren['’]t)\b"
                        r"|\bno longer\b)(?:[\s\-–—]+[\w'’]+){0,3}?[\s\-–—]+append[- ]only")


def binds(text, pattern, decl_path):
    """A declaring line binds a row when it says append-only, is not a negation, and either
    the declaring file is the row's (non-wildcard) path or the line names the row's token
    as a whole word. v4 (round 49, round-48 seat K1Binding): the token match is
    word-bounded (`log` inside `catalog` no longer binds), a negation within three words
    before `append-only` unbinds (`not strictly append-only`), and a wildcard row is never
    bound by a line of a file it covers merely saying append-only (self-declaration)."""
    if text is None:
        return False
    low = text.lower()
    if not ("append-only" in low or "append only" in low) or any(n in low for n in NEGATIONS) \
            or NEG_WINDOW.search(low):
        return False
    tok = row_token(pattern).lower()
    wild = any(ch in pattern for ch in "*?[")
    if not wild and fnmatch.fnmatchcase(decl_path, pattern):
        return True
    return bool(tok) and re.search(r"(?<![a-z0-9_])" + re.escape(tok) + r"(?![a-z0-9_])", low) is not None


def line_at(repo, rev, path, n):
    p = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True)
    if p.returncode != 0:
        return None
    ls = p.stdout.decode("utf-8", "replace").split("\n")
    return ls[n - 1] if 1 <= n <= len(ls) else None


def declaration(repo, rev, row):
    """{path, declared_at, region, ok, reason} for one contract row at rev."""
    pat, _rule, decl, region, _note = row
    dp, dn = decl.rsplit(":", 1)
    out = {"path": pat, "declared_at": decl, "region": region[0], "ok": True, "reason": ""}
    if not binds(line_at(repo, rev, dp, int(dn)), pat, dp):
        out.update(ok=False, reason=f"declared_at {decl} does not say append-only for {pat}")
        return out
    if region[0] == "*":
        return out
    pp, pn = region[2]
    text = line_at(repo, rev, pp, pn)
    low = (text or "").lower()
    if region[0] == "exempt":
        if text is None or "re-derived" not in low or not all(t[3:].strip().lower() in low for t in region[1]):
            out.update(ok=False, reason=f"exempt pointer {pp}:{pn} does not name every title as re-derived")
    elif not binds(text, pat, pp) or region[1][3:].strip().lower() not in low:
        out.update(ok=False, reason=f"only pointer {pp}:{pn} does not declare {region[1]!r} append-only")
    return out


def sections(body):
    """The `## ` section title owning each line of a list of byte lines (None before the first)."""
    out, title = [], None
    for line in body:
        if line.startswith(b"## "):
            title = line.rstrip(b"\r").decode("utf-8", "replace").rstrip()
        out.append(title)
    return out


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
    """(parent line number, bytes) of every deleted line, read by hunk-header counts."""
    raw = _git(repo, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", "--text",
               parent, commit, "--", path)
    out, lines, i = [], raw.split(b"\n"), 0
    while i < len(lines):
        m = HUNK.match(lines[i])
        i += 1
        if not m:
            continue
        start = int(m.group(1))
        nd = int(m.group(2)) if m.group(2) is not None else 1
        na = int(m.group(4)) if m.group(4) is not None else 1
        gd = ga = 0
        while i < len(lines) and (gd < nd or ga < na):
            ln = lines[i]
            if ln.startswith(b"-") and gd < nd:
                out.append((start + gd, ln[1:]))
                gd += 1
            elif ln.startswith(b"+") and ga < na:
                ga += 1
            i += 1
    return out


class Repo:
    def __init__(self, path):
        self.path = path
        self._raw = {}
        self._lines = {}
        self._sections = {}

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

    def list_lines(self, blob):
        """The blob's lines in order; empty for an absent blob."""
        if blob is None:
            return []
        if blob not in self._raw:
            self._raw[blob] = split_lines(_git(self.path, "cat-file", "blob", blob))
        return self._raw[blob]

    def lines(self, blob):
        if blob is None:
            return collections.Counter()
        if blob not in self._lines:
            self._lines[blob] = collections.Counter(self.list_lines(blob))
        return self._lines[blob]

    def section_counts(self, blob):
        """{section title: number of lines in it} for the blob."""
        if blob not in self._sections:
            self._sections[blob] = collections.Counter(sections(self.list_lines(blob)))
        return self._sections[blob]


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


def file_regions(rows, f):
    """(exempt titles, only prefixes) for a file from every contract row whose pattern matches it."""
    titles, prefixes = set(), []
    for row in rows:
        if fnmatch.fnmatchcase(f, row[0]):
            region = row[3]
            if region[0] == "exempt":
                titles |= set(region[1])
            elif region[0] == "only":
                prefixes.append(region[1])
    return titles, prefixes


def audit(repo_path, to="HEAD", threshold=20, files=None, contract=None):
    """files: explicit list (whole files graded); else contract: (label, text); else the
    contract at <to>."""
    r = Repo(repo_path)
    to_full = _text(repo_path, "rev-parse", "--verify", to + "^{commit}").strip()
    label, gone, nomatch, rows, decls = None, [], [], [], []
    if files is None:
        if contract is None:
            contract = (f"{to_full}:{CONTRACT}", _text(repo_path, "show", f"{to_full}:{CONTRACT}"))
        label, text = contract
        rows = parse_contract(text)
        patterns = [row[0] for row in rows]
        files = expand(repo_path, to_full, patterns)
        nomatch = unmatched(repo_path, to_full, patterns)
        gone = vanished(repo_path, to_full, patterns, set(files))
        decls = [declaration(repo_path, to_full, row) for row in rows]
    files = sorted(set(files))
    commits, parents = [], {}
    for line in _text(repo_path, "rev-list", "--topo-order", "--reverse", "--parents", to_full).split("\n"):
        parts = line.split()
        if parts:
            commits.append(parts[0])
            parents[parts[0]] = parts[1] if len(parts) > 1 else None
    events, binary = [], []
    origin_cache = {}

    def origins(f):
        """v4 origin: line text -> the `## ` titles holding it in the first commit's blob of f
        (rev-list order) that holds it."""
        if f not in origin_cache:
            orig, seen = {}, set()
            bl = r.blobs([f"{x}:{f}" for x in commits])
            for x in commits:
                b = bl[f"{x}:{f}"]
                if b is None or b in seen:
                    continue
                seen.add(b)
                body = r.list_lines(b)
                fresh = collections.defaultdict(set)
                for ln, t in zip(body, sections(body)):
                    if ln not in orig:
                        fresh[ln].add(t)
                orig.update(fresh)
            origin_cache[f] = orig
        return origin_cache[f]

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
            D = collections.Counter(text for _pos, text in dl)
            pb = r.blobs([f"{p}:{f}"])[f"{p}:{f}"]
            K = r.lines(pb) - D
            window = commits[i:]
            wb = r.blobs([f"{x}:{f}" for x in window])
            titles, prefixes = file_regions(rows, f)
            psec = sections(r.list_lines(pb))
            pcount = r.section_counts(pb)
            eligible = {t for t in titles
                        if max(r.section_counts(wb[f"{x}:{f}"])[t] if wb[f"{x}:{f}"] else 0 for x in window)
                        >= pcount[t]}
            G = collections.Counter()
            org = origins(f) if titles else {}
            for pos, text in dl:
                s = psec[pos - 1]
                if prefixes and not any(s is not None and s.startswith(q) for q in prefixes):
                    continue
                # v4: the carve-out covers only text born in an exempt section (origin)
                if s in eligible and org.get(text, frozenset()) & titles:
                    continue
                G[text] += 1
            ng = sum(G.values())
            best, best_c, by, h = 0, None, None, 0
            for x in window:
                M = r.lines(wb[f"{x}:{f}"])
                h = sum(min(n, max(0, M[l] - K[l])) for l, n in G.items())
                if h > best:
                    best, best_c = h, x
                if by is None and ng and h == ng:
                    by = x
            if ng == 0:
                status = "ungraded"
            else:
                status = "restored" if best == ng else ("unrestored" if best == 0 else "partial")
            events.append({"commit": c, "file": f, "deleted": len(dl), "graded": ng, "ungraded": len(dl) - ng,
                           "restored_max": best, "restored_best": best_c, "restored_by": by,
                           "held_at_to": h, "status": status})
    summary = {"commits": len(commits), "files": len(files), "events": len(events),
               "restored": sum(e["status"] == "restored" for e in events),
               "partial": sum(e["status"] == "partial" for e in events),
               "unrestored": sum(e["status"] == "unrestored" for e in events),
               "ungraded": sum(e["status"] == "ungraded" for e in events),
               "ungraded_lines": sum(e["ungraded"] for e in events),
               "regressed": sum(e["status"] in ("restored", "partial") and e["held_at_to"] < e["restored_max"]
                                for e in events),
               "vanished": len(gone), "unmatched": len(nomatch), "binary": len(binary),
               "bad_declarations": sum(not d["ok"] for d in decls)}
    return {"schema": SCHEMA, "definition": "v4", "to": to_full, "threshold": threshold, "contract": label,
            "files": files,
            "commits": len(commits), "events": events, "declarations": decls, "vanished": gone,
            "unmatched_patterns": nomatch, "binary_changes": binary, "summary": summary}


def render(res):
    out = [f"event {e['commit'][:12]} {e['file']} deleted={e['deleted']} graded={e['graded']} "
           f"ungraded={e['ungraded']} restored_max={e['restored_max']} held_at_to={e['held_at_to']} "
           f"status={e['status']} restored_best={(e['restored_best'] or '-')[:12]} "
           f"restored_by={(e['restored_by'] or '-')[:12]}" for e in res["events"]]
    s = res["summary"]
    out += [f"declaration {d['path']} {d['declared_at']} unbound: {d['reason']}"
            for d in res.get("declarations", []) if not d["ok"]]
    out += [f"vanished {v}" for v in res.get("vanished", [])]
    out += [f"unmatched-pattern {v}" for v in res.get("unmatched_patterns", [])]
    out += [f"binary-change {b['commit'][:12]} {b['file']}" for b in res.get("binary_changes", [])]
    out.append(f"summary commits={s['commits']} files={s['files']} events={s['events']} restored={s['restored']} "
               f"partial={s['partial']} unrestored={s['unrestored']} ungraded={s['ungraded']} "
               f"ungraded_lines={s['ungraded_lines']} regressed={s['regressed']} vanished={s['vanished']} "
               f"unmatched={s['unmatched']} binary={s['binary']} bad_declarations={s['bad_declarations']}")
    return "\n".join(out)


def exit_code(res):
    """1 on a partial or unrestored event, a regressed event, a vanished declared path or an
    unbound declaration."""
    s = res["summary"]
    return 1 if (s["partial"] or s["unrestored"] or s["regressed"] or s["vanished"]
                 or s["bad_declarations"]) else 0


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
        # restored fully, then re-trimmed below threshold: the window maximum keeps it restored,
        # held_at_to shows the loss and v3 exits 1 on the regression (round-47 seat X1Stable)
        f = Fixture(root)
        a = lines("a", 40)
        f.commit({"SCORECARD.md": a})
        f.commit({"SCORECARD.md": a[:15]})           # 25 deleted
        r = f.commit({"SCORECARD.md": a})
        t = f.commit({"SCORECARD.md": a[:35]})       # 5 of them deleted again (no event)
        res = audit(f.d, t, files=F)
        e = res["events"]
        return (len(e) == 1 and e[0]["restored_max"] == 25 and e[0]["restored_by"] == r
                and e[0]["status"] == "restored" and e[0]["held_at_to"] == 20
                and res["summary"]["regressed"] == 1 and exit_code(res) == 1), str(e)

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
                  CONTRACT: [HEADER, "corpus/lessons/*.md\tA-corr\tAGENTS.md:1\t*\tx"]})
        t = f.commit({"corpus/lessons/r1.md": a[:5], "notes.md": a[:5]})
        res = audit(f.d, t)
        e = res["events"]
        ok = (res["files"] == ["corpus/lessons/r1.md"] and len(e) == 1 and e[0]["file"] == "corpus/lessons/r1.md"
              and res["declarations"][0]["ok"] is True)
        for bad in ("path\trule\n", HEADER + "\nLOG.md\tA\tAGENTS.md:1\tx\n",
                    HEADER + "\nLOG.md\tA\tAGENTS.md:1\texempt=Axes@AGENTS.md:1\tx\n",
                    HEADER + "\nLOG.md\tA\tAGENTS.md:1\tonly=## E\tx\n"):
            try:
                parse_contract(bad)
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
        contract = [HEADER, "corpus/lessons/*.md\tA-corr\tAGENTS.md:1\t*\tx", "nope/*.md\tA\tAGENTS.md:1\t*\tx"]
        f.commit({"AGENTS.md": ["lessons and nope are append-only"], "corpus/lessons/gone.md": a,
                  "corpus/lessons/caf\u00e9.md": a, CONTRACT: contract})
        f.commit({"corpus/lessons/caf\u00e9.md": a + ["more"]}, delete=["corpus/lessons/gone.md"])
        t = f.commit({"corpus/lessons/bin.md": b"\x00\x01" * 40}, raw=True)
        t = f.commit({"corpus/lessons/bin.md": b"\x00\x02" * 41}, raw=True)
        res = audit(f.d, t)
        ok = (res["files"] == ["corpus/lessons/bin.md", "corpus/lessons/caf\u00e9.md"]
              and res["vanished"] == ["corpus/lessons/gone.md"] and res["unmatched_patterns"] == ["nope/*.md"]
              and len(res["binary_changes"]) == 2 and res["summary"]["bad_declarations"] == 0
              and exit_code(res) == 1)
        try:
            parse_contract(HEADER + "\r\nLOG.md\tA\tAGENTS.md:1\t*\tx\r\n")
            ok = False
        except AuditError:
            pass
        return ok, json.dumps({k: res[k] for k in ("files", "vanished", "unmatched_patterns", "binary_changes")})

    # ---- v3 (round 48): regions, binding, regressed
    NOTES = ["# notes", "score.md is append-only below its head.",
             "The ## Axes and ## Plan heads of score.md are re-derived in place.",
             "know.md keeps its ## Errata region append-only.",
             "score.md gets appended to.", "score.md is not append-only.", "LOG.md is append-only."]
    SCORE = "score.md\tA-corr\tNOTES.md:2\texempt=## Axes|## Plan@NOTES.md:3\tx"
    KNOW = "know.md\tA-corr\tNOTES.md:4\tonly=## Errata@NOTES.md:4\tx"
    head, tail = ["# score", "## Axes"] + lines("h", 24), ["## Round 1"] + lines("d", 25)

    def scored(rows, body):
        f = Fixture(root)
        f.commit({"NOTES.md": NOTES, CONTRACT: [HEADER] + rows, "score.md": body})
        return f

    def t_exempt_rewritten():
        f = scored([SCORE], head + tail)
        c = f.commit({"score.md": ["# score", "## Axes"] + lines("h2", 24) + tail})
        res = audit(f.d, c)
        e = res["events"]
        return (len(e) == 1 and e[0]["deleted"] == 24 and e[0]["graded"] == 0 and e[0]["ungraded"] == 24
                and e[0]["status"] == "ungraded" and e[0]["restored_best"] is None
                and res["summary"]["ungraded_lines"] == 24 and exit_code(res) == 0), str(e)

    def t_exempt_gutted():
        f = scored([SCORE], head + tail)
        c = f.commit({"score.md": ["# score", "## Axes", "collapsed"] + tail})
        res = audit(f.d, c)
        e = res["events"]
        return (len(e) == 1 and e[0]["graded"] == 24 and e[0]["status"] == "unrestored"
                and exit_code(res) == 1), str(e)

    def t_exempt_gutted_then_regrown():
        # the section shrinks at the event and grows back later in the window: eligible
        f = scored([SCORE], head + tail)
        c = f.commit({"score.md": ["# score", "## Axes", "collapsed"] + tail})
        t = f.commit({"score.md": ["# score", "## Axes"] + lines("h3", 30) + tail})
        res = audit(f.d, t)
        e = res["events"]
        return (len(e) == 1 and e[0]["commit"] == c and e[0]["ungraded"] == 24 and e[0]["status"] == "ungraded"
                and exit_code(res) == 0), str(e)

    def t_dated_rewritten():
        f = scored([SCORE], head + tail)
        c = f.commit({"score.md": head + ["## Round 1"] + lines("d2", 25)})
        res = audit(f.d, c)
        e = res["events"]
        return (len(e) == 1 and e[0]["graded"] == 25 and e[0]["ungraded"] == 0 and e[0]["status"] == "unrestored"
                and exit_code(res) == 1), str(e)

    def t_only_errata():
        f = Fixture(root)
        body, errata = ["# know", "## Body"] + lines("k", 25), ["## Errata — x"] + lines("e", 20)
        f.commit({"NOTES.md": NOTES, CONTRACT: [HEADER, KNOW], "know.md": body + errata})
        c1 = f.commit({"know.md": ["# know", "## Body"] + errata})
        c2 = f.commit({"know.md": ["# know", "## Body", "## Errata — x"]})
        res = audit(f.d, c2)
        ev = {e["commit"]: e for e in res["events"]}
        return (len(ev) == 2 and ev[c1]["status"] == "ungraded" and ev[c1]["ungraded"] == 25
                and ev[c2]["graded"] == 20 and ev[c2]["status"] == "unrestored" and exit_code(res) == 1), str(ev)

    def t_clamp():
        # K > M for a duplicated line must contribute 0, not a negative (round-47 seat K1Fixture)
        f = Fixture(root)
        u = lines("u", 20)
        f.commit({"LOG.md": ["dup"] * 30 + u})
        f.commit({"LOG.md": ["dup"] * 10})          # 20 dup + 20 unique deleted
        t = f.commit({"LOG.md": u})                  # uniques back, every dup gone
        res = audit(f.d, t, files=F)
        e = res["events"]
        return (len(e) == 1 and e[0]["deleted"] == 40 and e[0]["restored_max"] == 20
                and e[0]["status"] == "partial"), str(e)

    def t_bad_declarations():
        f = Fixture(root)
        f.commit({"NOTES.md": NOTES, "score.md": head + tail, "LOG.md": ["x"],
                  CONTRACT: [HEADER, "score.md\tA\tNOTES.md:5\t*\tno append-only",
                             "score.md\tA\tNOTES.md:6\t*\tnegation",
                             "score.md\tA-corr\tNOTES.md:2\texempt=## Axes|## Round 1@NOTES.md:3\tunnamed",
                             "LOG.md\tA\tNOTES.md:2\t*\ttoken missing",
                             "LOG.md\tA\tNOTES.md:7\t*\tbound"]})
        res = audit(f.d, "HEAD")
        oks = [d["ok"] for d in res["declarations"]]
        return oks == [False, False, False, False, True] and exit_code(res) == 1, str(res["declarations"])

    def t_clean():
        f = scored([SCORE, "LOG.md\tA\tNOTES.md:7\t*\tx"], head + tail)
        a = lines("c", 30)
        f.commit({"LOG.md": a})
        f.commit({"LOG.md": a[20:], "score.md": ["# score", "## Axes"] + lines("h4", 24) + tail})
        t = f.commit({"LOG.md": a})
        res = audit(f.d, t)
        s = res["summary"]
        return (s["events"] == 2 and s["restored"] == 1 and s["ungraded"] == 1 and s["regressed"] == 0
                and s["bad_declarations"] == 0 and exit_code(res) == 0), str(res["events"])

    def t_preamble_graded():
        # lines before the first `## ` heading (the SCORECARD authority banner) have no
        # section, so no exempt title covers them: a rewrite is graded (round-48 build finding;
        # seat X1SelftestPower: no case covered the pre-heading region)
        f = scored([SCORE], ["# score"] + lines("p", 24) + head[1:] + tail)
        c = f.commit({"score.md": ["# score"] + lines("p2", 24) + head[1:] + tail})
        res = audit(f.d, c)
        e = res["events"]
        return (len(e) == 1 and e[0]["graded"] == 24 and e[0]["ungraded"] == 0
                and e[0]["status"] == "unrestored" and exit_code(res) == 1), str(e)

    # ---- v4 (round 49): origin-aware carve-out, word-bounded token, negation window,
    # no wildcard self-declaration (round-48 seats K1Regions, K1Binding)
    def t_launder_through_head():
        # dated text moved under the exempt head (a 1-line diff), then dropped there while
        # the head regrows past its parent size: v3 left it ungraded, v4 grades it
        f = scored([SCORE], head + tail)
        f.commit({"score.md": head + tail[1:] + ["## Round 1", "kept"]})
        c = f.commit({"score.md": head + lines("regrow", 30) + ["## Round 1", "kept"]})
        res = audit(f.d, c)
        e = [x for x in res["events"] if x["commit"] == c]
        return (len(e) == 1 and e[0]["deleted"] == 25 and e[0]["graded"] == 25 and e[0]["ungraded"] == 0
                and e[0]["status"] == "unrestored" and exit_code(res) == 1), str(res["events"])

    def t_binding_v4():
        f = Fixture(root)
        f.commit({"NOTES.md": ["# n", "the catalog is append-only", "score.md is not strictly append-only",
                               "LOG.md is append-only", "score.md cannot be called append-only",
                               "score.md isn’t append-only", "score.md is not—append-only"],
                  "notes/a.md": ["this file is append-only"], "notes/b.md": ["x"], "score.md": ["s"],
                  "LOG.md": ["x"],
                  CONTRACT: [HEADER, "LOG.md\tA\tNOTES.md:2\t*\tsubstring token",
                             "score.md\tA\tNOTES.md:3\t*\tnegation window",
                             "notes/*.md\tA\tnotes/a.md:1\t*\twildcard self-declaration",
                             "LOG.md\tA\tNOTES.md:4\t*\tbound",
                             "score.md\tA\tNOTES.md:5\t*\tcannot (seat K2Negation)",
                             "score.md\tA\tNOTES.md:6\t*\tcurly apostrophe",
                             "score.md\tA\tNOTES.md:7\t*\tem dash"]})
        res = audit(f.d, "HEAD")
        oks = [d["ok"] for d in res["declarations"]]
        return oks == [False, False, False, True, False, False, False] and exit_code(res) == 1, \
            str(res["declarations"])

    def t_wildcard_token_bound():
        # v4: a wildcard row binds through a line naming its directory token as a whole word,
        # and not through the token inside a longer word. `contract` covers the positive only
        # in passing (its declaring line is the token itself, which v3's substring test also
        # accepts); this pins both sides of the rule.
        f = Fixture(root)
        f.commit({"NOTES.md": ["# n", "the logs directory is append-only",
                               "our catalogs are append-only"],
                  "corpus/logs/a.md": ["this file is append-only"],
                  CONTRACT: [HEADER, "corpus/logs/*.md\tA\tNOTES.md:2\t*\tbound by token",
                             "corpus/logs/*.md\tA\tNOTES.md:3\t*\ttoken inside longer word"]})
        res = audit(f.d, "HEAD")
        oks = [d["ok"] for d in res["declarations"]]
        return oks == [True, False] and exit_code(res) == 1, str(res["declarations"])

    def t_origin_preamble_moved_under_head():
        # preamble-born text (origin None) moved under the exempt head and dropped there while
        # the head regrows past its parent size: the carve-out needs an origin inside an exempt
        # title, so None never qualifies and the deletion is graded (v4 origin clause, None side)
        p = lines("p", 25)
        f = scored([SCORE], ["# score"] + p + head[1:] + tail)
        f.commit({"score.md": ["# score", "## Axes"] + head[2:] + p + tail})
        c = f.commit({"score.md": ["# score", "## Axes"] + head[2:] + lines("regrow", 30) + tail})
        res = audit(f.d, c)
        e = [x for x in res["events"] if x["commit"] == c]
        return (len(e) == 1 and e[0]["deleted"] == 25 and e[0]["graded"] == 25 and e[0]["ungraded"] == 0
                and e[0]["status"] == "unrestored" and exit_code(res) == 1), str(res["events"])

    def t_negation_window_three_vs_four():
        # the negation window reaches three words before append-only, not four: both sides of
        # the {0,3} bound are pinned (v3 had no window and bound both lines)
        f = Fixture(root)
        f.commit({"NOTES.md": ["# n", "score.md is not yet considered strictly append-only",
                               "LOG.md is not yet really considered strictly append-only"],
                  "score.md": ["s"], "LOG.md": ["x"],
                  CONTRACT: [HEADER, "score.md\tA\tNOTES.md:2\t*\tthree words",
                             "LOG.md\tA\tNOTES.md:3\t*\tfour words"]})
        res = audit(f.d, "HEAD")
        oks = [d["ok"] for d in res["declarations"]]
        return oks == [False, True] and exit_code(res) == 1, str(res["declarations"])

    def t_negation_curly_apostrophe():
        # a word carrying a typographic apostrophe still counts as one word inside the negation
        # window (v4 `[\\w'\u2019]`); dropping U+2019 from the class binds the line
        f = Fixture(root)
        f.commit({"NOTES.md": ["# n", "score.md is not the round\u2019s append-only log",
                               "LOG.md is not the round's append-only log"],
                  "score.md": ["s"], "LOG.md": ["x"],
                  CONTRACT: [HEADER, "score.md\tA\tNOTES.md:2\t*\tcurly",
                             "LOG.md\tA\tNOTES.md:3\t*\tascii"]})
        res = audit(f.d, "HEAD")
        oks = [d["ok"] for d in res["declarations"]]
        return oks == [False, False] and exit_code(res) == 1, str(res["declarations"])

    def t_origin_multi_title():
        # origin(l) may hold several titles; one of them being exempt keeps the line ungraded
        # (`origin ... contains one of`). A line born both under the head and under a dated
        # heading is exempt (v4); a single-origin reading grades it.
        h = lines("h", 24) + ["shared line"]
        d = ["shared line"] + lines("d", 24)
        f = scored([SCORE], ["# score", "## Axes"] + h + ["## Round 1"] + d)
        c = f.commit({"score.md": ["# score", "## Axes"] + h[:-1] + lines("regrow", 30)
                      + ["## Round 1"] + d})
        res = audit(f.d, c, threshold=1)
        e = [x for x in res["events"] if x["commit"] == c]
        return (len(e) == 1 and e[0]["deleted"] == 1 and e[0]["graded"] == 0 and e[0]["ungraded"] == 1
                and e[0]["status"] == "ungraded" and exit_code(res) == 0), str(res["events"])

    for name, fn in [("no-deletion", t_none), ("below-threshold", t_below),
                     ("exact-threshold-unrestored", t_exact_unrestored), ("restored-later", t_restored),
                     ("partial", t_partial), ("undeclared-file", t_undeclared),
                     ("declared-file-removed", t_file_removed), ("merge-first-parent", t_merge_first_parent),
                     ("dashdash-lines", t_dashdash), ("crlf-and-eof", t_crlf_and_eof), ("multiset", t_multiset),
                     ("window-max", t_window_max), ("relocation", t_relocation), ("contract", t_contract),
                     ("threshold-flag", t_threshold_flag), ("crlf-restore-exact", t_crlf_restore_exact),
                     ("dup-kept-not-restored", t_dup_kept_not_restored), ("final-segment", t_final_segment),
                     ("vanished-and-paths", t_vanished_and_paths), ("exempt-rewritten", t_exempt_rewritten),
                     ("exempt-gutted", t_exempt_gutted), ("exempt-gutted-then-regrown", t_exempt_gutted_then_regrown),
                     ("dated-rewritten", t_dated_rewritten), ("only-errata", t_only_errata), ("clamp", t_clamp),
                     ("bad-declarations", t_bad_declarations), ("clean", t_clean),
                     ("preamble-graded", t_preamble_graded), ("launder-through-head", t_launder_through_head),
                     ("binding-v4", t_binding_v4),
                     ("wildcard-token-bound", t_wildcard_token_bound),
                     ("origin-preamble-moved-under-head", t_origin_preamble_moved_under_head),
                     ("negation-window-three-vs-four", t_negation_window_three_vs_four),
                     ("negation-curly-apostrophe", t_negation_curly_apostrophe),
                     ("origin-multi-title", t_origin_multi_title)]:
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
