#!/usr/bin/env python3
"""round48-append-audit-v3-check.py - kama round-48 C1 (calibration) counter.

Question: does the lane's append-only instrument report the lane's declared
append-only rule as the lane declares it - carve-outs included - so that its
exit code is a verdict rather than a signal to go and read a contract note?
At the round-47 tip, tools/append-only-audit.py v2 exits 1 on two SCORECARD.md
`partial` events whose every unrestored line is head text that SCORECARD.md:6
declares re-derived in place (round-47 seats Rev1Restore, K1Design); the
contract row says so only in prose. The round-47 closure (D5) and wave also
found: the contract leg accepted any declaring line containing `append`, even
a negation (V1Ctr F1); the `## Errata` region of a knowledge entry, declared
append-only, was unaudited (K1Design D2); `held_at_to`/`regressed` did not
reach the exit code (X1Stable); the stable leg could be vacuous (V1Ctr); the
fixture never exercised the max(0, .) clamp, merge first-parent selection or
the exact threshold deterministically (K1Fixture).

Frozen names (before data):
  tool       tools/append-only-audit.py   (schema append-only-audit/v3)
  contract   registry/append-only-contract.tsv
  threshold  20 deleted lines per (commit, file)
  stable base  33e005827742b29772b153cda036ec9f27f653be (round-48 base)

v3 contract: tab-separated; first line exactly
  `path<TAB>rule<TAB>declared_at<TAB>region<TAB>note`
each later non-empty line has 5 cells: path is a repo-relative path or fnmatch
pattern; rule one of A, A-row, A-corr; declared_at `<path>:<line>`; region is
  `*`                              every line of the file is graded
  `exempt=<T1>|<T2>|...@<path>:<line>`  lines in a `## ` section titled exactly Ti
                                   are ungraded when that section is eligible
  `only=<P>@<path>:<line>`          only lines in a `## ` section whose title starts
                                   with P are graded
Declaration binding (this counter's own rule; the tool reports the same):
  a declared_at line binds when, lower-cased, it contains `append-only` or
  `append only`, contains none of `not append-only`, `not append only`,
  `no longer append`, `never append-only`, and either the declaring path matches
  the row's pattern (self-declaration) or it contains the row's token: the
  pattern's base name without extension when the base name has no wildcard,
  else the name of the pattern's parent directory.
  An exempt region pointer binds when its line contains `re-derived` and every
  title's text after `## ` (lower-cased); an only region pointer binds when its
  line binds as above for the row and contains P's text after `## `.
v3 definitions (the tool contract this counter scores):
  files, commits, lines, deleted, D, K, event, window, held(x) exactly as v2
  (first-parent diffs over `git rev-list --topo-order --reverse <to>`, byte lines
  split on b"\\n", deleted equal to `git diff --numstat --no-renames`, K = parent - D,
  held over a multiset G: sum_l min(G[l], max(0, M_x[l] - K[l]))).
  section    a line's section is the title of the last line at or before it that
             starts with b"## " (the line itself, `\\r` and trailing blanks
             stripped, utf-8 with replacement); none before the first.
  count(T,x) the number of lines of the file at x whose section is T.
  eligible   an exempt title T is eligible for an event when the maximum of
             count(T,x) over the window is >= count(T,parent).
  graded G   the deleted lines (by parent position) that are graded: region `*`
             all; exempt: all but those whose parent section is an eligible
             declared title; only: those whose parent section starts with P.
  ungraded   |D| - |G|.
  restored_max, restored_best, restored_by: over G, as v2 (by: held == |G| > 0).
  held_at_to held(<to>) over G.
  status     ungraded when |G| == 0; else restored (max == |G|), unrestored
             (max == 0), partial.
  regressed  events with status restored or partial and held_at_to < restored_max.
  exit       1 when any event is partial or unrestored, regressed > 0, a
             contract-matching path vanished, or a declaration does not bind;
             0 otherwise; 2 cannot evaluate.
Tool contract: `python3 tools/append-only-audit.py --repo R --to REV [--contract C] --json`
prints one object: "schema": "append-only-audit/v3", "files", "events" (keys commit,
file, deleted, graded, ungraded, restored_max, restored_best, restored_by,
held_at_to, status), "declarations" (one per row: path, ok), "summary" (keys
events, restored, partial, unrestored, ungraded, ungraded_lines, regressed,
vanished, bad_declarations). `--selftest` prints `AOA_SELFTEST pass=n fail=0`.

Legs:
  selftest  the tool at --tip with `--selftest --scratch` exits 0, prints
            `AOA_SELFTEST pass=n fail=0` with n >= 20.
  contract  the contract at --tip parses as v3; it holds the required rows
            (LOG.md, SCORECARD.md, corpus/QUALITY.md, corpus/README.md,
            corpus/SOURCES.md, corpus/lessons/*.md, registry/history/DELTA.md,
            registry/report-landing-errata.tsv with region `*`; SCORECARD.md
            with region exempt of exactly ## Axes, ## Planned, ## Retired,
            ## Saturation, ## Capabilities; corpus/knowledge/consumer-registry.md
            with region only=## Errata); every row's declaration and region
            pointer binds at --tip; the tool's lane run reports exactly the
            expansion as "files" and every declaration ok.
  lane      the tool on --repo at --tip (tip contract) reports schema v3 and
            exactly the files, events (all keys above) and summary this counter
            recomputes on its own code path; its exit code is the derived exit;
            and the derived lane verdict holds: no partial or unrestored event,
            regressed 0, vanished 0, bad declarations 0, ungraded lines > 0.
  fixture   eleven fresh fixture repos under --scratch, deterministic, each with
            expectations written by construction (not recomputed): the exact
            threshold (20 -> event, 19 -> none), an exempt head rewritten in place
            (ungraded, exit 0), the same head gutted (graded, unrestored), a dated
            section rewritten in the exempt file (graded), an only=## Errata file
            (body deletion ungraded, errata deletion graded), the max(0, .) clamp
            (restored_max 20 of 40, not 10), a merge whose first parent keeps the
            lines (event at the merge), a restoration re-deleted below the
            threshold (restored, held_at_to 15, regressed 1, exit 1), `--` and
            CRLF lines, three declarations that must not bind (no `append-only`,
            a negation, a region title its pointer does not name), and a clean
            repo (restored and ungraded only, exit 0).
  stable    the tool on the lane --to the stable base and --to --tip, both with
            the tip contract: the base differs from the tip, it has >= 1 event,
            and every base event (carrying an integer `graded`) appears at tip with
            equal deleted, graded, ungraded, restored_max and restored_best.
met = selftest and contract and lane and fixture and stable.
PREDICATE (same sentence in the preregistration): append-only-audit v3 at the
measured commit grades the lane's append-only files under declared, bound
regions - SCORECARD's re-derived head exempt, the consumer-registry Errata
region graded - equals this counter's recomputation on the lane, reports no
graded loss, regression, vanished path or unbound declaration there, passes eleven
constructed fixtures and is stable from the round-48 base; selftest=1
contract=1 lane=1 fixture=1 stable=1.

Output: `selftest=0|1 contract=0|1 lane=0|1 fixture=0|1 stable=0|1 rows=R files=F
lane_events=E lane_failures=N ungraded_lines=U fixture_fail=X met=True|False`,
then `detail:` lines. Exit 0 met, 1 not met, 2 could not evaluate.
Read-only on --repo; fixtures live under --scratch (or TMPDIR), removed on exit.
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

TOOL = "tools/append-only-audit.py"
CONTRACT = "registry/append-only-contract.tsv"
HEADER = "path\trule\tdeclared_at\tregion\tnote"
RULES = {"A", "A-row", "A-corr"}
THRESHOLD = 20
STABLE_BASE = "33e005827742b29772b153cda036ec9f27f653be"
HEAD_TITLES = {"## Axes", "## Planned", "## Retired", "## Saturation", "## Capabilities"}
REQUIRED = {
    "LOG.md": ("*",), "corpus/QUALITY.md": ("*",), "corpus/README.md": ("*",),
    "corpus/SOURCES.md": ("*",), "corpus/lessons/*.md": ("*",),
    "registry/history/DELTA.md": ("*",), "registry/report-landing-errata.tsv": ("*",),
    "SCORECARD.md": ("exempt", frozenset(HEAD_TITLES)),
    "corpus/knowledge/consumer-registry.md": ("only", "## Errata"),
}
NEG = ("not append-only", "not append only", "no longer append", "never append-only")
EVKEYS = ("deleted", "graded", "ungraded", "restored_max", "restored_best", "restored_by", "held_at_to", "status")
SUMKEYS = ("events", "restored", "partial", "unrestored", "ungraded", "ungraded_lines", "regressed",
           "vanished", "bad_declarations")


class EvalError(Exception):
    pass


def git(repo, *args, inp=None, check=True):
    p = subprocess.run(["git", "-C", repo, *args], input=inp, capture_output=True)
    if check and p.returncode != 0:
        raise EvalError(f"git {' '.join(args)[:120]}: {p.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return p


def show(repo, rev, path):
    p = git(repo, "show", f"{rev}:{path}", check=False)
    return p.stdout if p.returncode == 0 else None


# ------------------------------------------------------------- contract (own parser)
def parse_region(cell):
    """('*',) | ('exempt', frozenset titles, ptr) | ('only', prefix, ptr) | None."""
    if cell == "*":
        return ("*",)
    m = re.fullmatch(r"(exempt|only)=(.+)@([^@:]+):(\d+)", cell)
    if not m:
        return None
    kind, body, ptr = m.group(1), m.group(2), (m.group(3), int(m.group(4)))
    if kind == "exempt":
        titles = frozenset(t.strip() for t in body.split("|") if t.strip())
        if not titles or not all(t.startswith("## ") for t in titles):
            return None
        return ("exempt", titles, ptr)
    if not body.startswith("## "):
        return None
    return ("only", body, ptr)


def parse_contract(text):
    lines = text.split("\n")
    if "\r" in text or not lines or lines[0] != HEADER:
        return None, "header is not the v3 header (or CR present)"
    rows = []
    for n, line in enumerate(lines[1:], 2):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != 5:
            return None, f"line {n}: {len(cells)} cells"
        pat, rule, decl, region, note = (c.strip() for c in cells)
        m = re.fullmatch(r"([^:]+):(\d+)", decl)
        reg = parse_region(region)
        if not pat or rule not in RULES or not m or reg is None:
            return None, f"line {n}: bad path/rule/declared_at/region"
        rows.append({"path": pat, "rule": rule, "decl": (m.group(1), int(m.group(2))), "region": reg})
    if not rows:
        return None, "no rows"
    return rows, None


def token(pattern):
    base = pattern.rsplit("/", 1)[-1]
    if any(ch in base for ch in "*?["):
        parts = pattern.split("/")
        return parts[-2] if len(parts) > 1 else ""
    return base.rsplit(".", 1)[0] if "." in base else base


def line_at(repo, rev, path, n):
    raw = show(repo, rev, path)
    if raw is None:
        return None
    ls = raw.decode("utf-8", "replace").split("\n")
    return ls[n - 1] if 1 <= n <= len(ls) else None


def binds(text, pattern, decl_path):
    if text is None:
        return False
    low = text.lower()
    if not ("append-only" in low or "append only" in low) or any(n in low for n in NEG):
        return False
    tok = token(pattern).lower()
    return fnmatch.fnmatchcase(decl_path, pattern) or (bool(tok) and tok in low)


def row_binds(repo, rev, row):
    """(ok, reason) for the row's declaration and region pointer."""
    dp, dn = row["decl"]
    if not binds(line_at(repo, rev, dp, dn), row["path"], dp):
        return False, f"declared_at {dp}:{dn} does not bind"
    reg = row["region"]
    if reg[0] == "*":
        return True, ""
    pp, pn = reg[2]
    text = line_at(repo, rev, pp, pn)
    if text is None:
        return False, f"region pointer {pp}:{pn} absent"
    low = text.lower()
    if reg[0] == "exempt":
        if "re-derived" not in low or not all(t[3:].strip().lower() in low for t in reg[1]):
            return False, f"exempt pointer {pp}:{pn} does not name every title and re-derived"
        return True, ""
    if not binds(text, row["path"], pp) or reg[1][3:].strip().lower() not in low:
        return False, f"only pointer {pp}:{pn} does not bind"
    return True, ""


# ------------------------------------------------------------- recomputation (own code)
def blines(data):
    if data is None:
        return []
    s = data.split(b"\n")
    if s and s[-1] == b"":
        s.pop()
    return s


def sections(lines):
    out, cur = [], None
    for ln in lines:
        if ln.startswith(b"## "):
            cur = ln.rstrip(b"\r").decode("utf-8", "replace").rstrip()
        out.append(cur)
    return out


def del_positions(repo, p, c, path):
    """Parent positions (1-based) of deleted lines, from the -U0 diff hunk headers."""
    raw = git(repo, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", "--text", p, c, "--", path).stdout
    pos = []
    for ln in raw.split(b"\n"):
        m = re.match(rb"^@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@", ln)
        if m:
            start, cnt = int(m.group(1)), int(m.group(2)) if m.group(2) is not None else 1
            pos.extend(range(start, start + cnt))
    return pos


class Blobs:
    def __init__(self, repo):
        self.repo, self.cache = repo, {}

    def get(self, rev, path):
        key = (rev, path)
        if key not in self.cache:
            p = git(self.repo, "cat-file", "-p", f"{rev}:{path}", check=False)
            self.cache[key] = blines(p.stdout) if p.returncode == 0 else []
        return self.cache[key]


def recompute(repo, to, rows):
    to = git(repo, "rev-parse", "--verify", to + "^{commit}").stdout.decode().strip()
    tree = [t.decode("utf-8", "surrogateescape") for t in
            git(repo, "ls-tree", "-r", "-z", "--name-only", to).stdout.split(b"\0") if t]
    files = sorted({t for t in tree if any(fnmatch.fnmatchcase(t, r["path"]) for r in rows)})
    hist = {t.decode("utf-8", "surrogateescape").strip("\n") for t in
            git(repo, "log", "-z", "--format=", "--name-only", "--no-renames", to).stdout.split(b"\0") if t.strip(b"\n")}
    vanished = sorted(t for t in hist if t not in set(files) and any(fnmatch.fnmatchcase(t, r["path"]) for r in rows))
    regions = {}
    for f in files:
        regions[f] = [r["region"] for r in rows if fnmatch.fnmatchcase(f, r["path"])]
    order, parent = [], {}
    for line in git(repo, "rev-list", "--topo-order", "--reverse", "--parents", to).stdout.decode().split("\n"):
        ps = line.split()
        if ps:
            order.append(ps[0])
            parent[ps[0]] = ps[1] if len(ps) > 1 else None
    B = Blobs(repo)
    events = []
    for i, c in enumerate(order):
        p = parent[c]
        if p is None or not files:
            continue
        raw = git(repo, "diff", "--numstat", "-z", "--no-renames", p, c, "--", *files).stdout
        for rec in raw.split(b"\0"):
            parts = rec.split(b"\t", 2)
            if len(parts) != 3 or not parts[1].isdigit():
                continue
            f, nd = parts[2].decode("utf-8", "surrogateescape"), int(parts[1])
            if nd < THRESHOLD:
                continue
            pl = B.get(p, f)
            pos = del_positions(repo, p, c, f)
            if len(pos) != nd:
                raise EvalError(f"{c[:12]} {f}: hunk positions {len(pos)} != numstat {nd}")
            D = collections.Counter(pl[k - 1] for k in pos)
            K = collections.Counter(pl) - D
            psec = sections(pl)
            window = order[i:]
            graded_pos = []
            regs = regions.get(f, [("*",)])
            exempt_titles = set()
            only_prefixes = []
            for reg in regs:
                if reg[0] == "exempt":
                    exempt_titles |= set(reg[1])
                elif reg[0] == "only":
                    only_prefixes.append(reg[1])
            eligible = set()
            for t in exempt_titles:
                need = sum(1 for s in psec if s == t)
                if max(sum(1 for s in sections(B.get(x, f)) if s == t) for x in window) >= need:
                    eligible.add(t)
            for k in pos:
                s = psec[k - 1]
                if only_prefixes and not any(s is not None and s.startswith(pp) for pp in only_prefixes):
                    continue
                if s in eligible:
                    continue
                graded_pos.append(k)
            G = collections.Counter(pl[k - 1] for k in graded_pos)
            ng = len(graded_pos)
            best, best_c, by, h = 0, None, None, 0
            for x in window:
                M = collections.Counter(B.get(x, f))
                h = sum(min(n, max(0, M[l] - K[l])) for l, n in G.items())
                if h > best:
                    best, best_c = h, x
                if by is None and ng and h == ng:
                    by = x
            if ng == 0:
                status = "ungraded"
            else:
                status = "restored" if best == ng else ("unrestored" if best == 0 else "partial")
            events.append({"commit": c, "file": f, "deleted": nd, "graded": ng, "ungraded": nd - ng,
                           "restored_max": best, "restored_best": best_c, "restored_by": by,
                           "held_at_to": h, "status": status})
    bad = sum(1 for r in rows if not row_binds(repo, to, r)[0])
    s = {"events": len(events),
         "restored": sum(e["status"] == "restored" for e in events),
         "partial": sum(e["status"] == "partial" for e in events),
         "unrestored": sum(e["status"] == "unrestored" for e in events),
         "ungraded": sum(e["status"] == "ungraded" for e in events),
         "ungraded_lines": sum(e["ungraded"] for e in events),
         "regressed": sum(e["status"] in ("restored", "partial") and e["held_at_to"] < e["restored_max"]
                          for e in events),
         "vanished": len(vanished), "bad_declarations": bad}
    code = 1 if (s["partial"] or s["unrestored"] or s["regressed"] or s["vanished"] or bad) else 0
    return {"to": to, "files": files, "events": events, "summary": s, "exit": code}


# ------------------------------------------------------------- tool runner
def run_tool(tool, repo, to, contract=None, extra=(), timeout=1800):
    argv = [sys.executable, tool, "--repo", repo, "--to", to, "--json", *extra]
    if contract:
        argv += ["--contract", contract]
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, None, "timeout"
    try:
        j = json.loads(p.stdout)
    except ValueError:
        j = None
    return p.returncode, j, p.stderr[-300:]


def diff_result(j, rc, code, detail, tag):
    """Mismatches between the tool's JSON/exit and a recomputation."""
    bad = 0
    if not isinstance(j, dict) or j.get("schema") != "append-only-audit/v3":
        detail.append(f"{tag}: tool JSON missing or schema is not append-only-audit/v3")
        return 1 + len(rc["events"])
    if j.get("files") != rc["files"]:
        detail.append(f"{tag}: files differ (tool {len(j.get('files') or [])}, counter {len(rc['files'])})")
        bad += 1
    te = {(e.get("commit"), e.get("file")): e for e in j.get("events") or [] if isinstance(e, dict)}
    ce = {(e["commit"], e["file"]): e for e in rc["events"]}
    for k in sorted(set(te) | set(ce), key=str):
        if k not in te or k not in ce:
            detail.append(f"{tag}: event {k[0][:12] if k[0] else k[0]} {k[1]} only in {'counter' if k in ce else 'tool'}")
            bad += 1
            continue
        for f in EVKEYS:
            if te[k].get(f) != ce[k][f]:
                detail.append(f"{tag}: {k[0][:12]} {k[1]} {f} tool={te[k].get(f)} counter={ce[k][f]}")
                bad += 1
    ts = j.get("summary") or {}
    for f in SUMKEYS:
        if ts.get(f) != rc["summary"][f]:
            detail.append(f"{tag}: summary {f} tool={ts.get(f)} counter={rc['summary'][f]}")
            bad += 1
    if code != rc["exit"]:
        detail.append(f"{tag}: tool exit {code} != derived {rc['exit']}")
        bad += 1
    return bad


# ------------------------------------------------------------- fixtures (expectations by construction)
class Fx:
    ENV = {"GIT_AUTHOR_NAME": "r48c1-fixture", "GIT_AUTHOR_EMAIL": "r48c1@fixture.invalid",
           "GIT_COMMITTER_NAME": "r48c1-fixture", "GIT_COMMITTER_EMAIL": "r48c1@fixture.invalid",
           "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}

    def __init__(self, root, name):
        self.d = os.path.join(root, name)
        os.makedirs(self.d)
        self.env = dict(os.environ, **self.ENV)
        self.g("init", "-q", "-b", "main")
        top = self.g("rev-parse", "--show-toplevel").strip()
        if os.path.realpath(top) != os.path.realpath(self.d):
            raise EvalError(f"fixture toplevel {top} != {self.d}")
        self.n = 0

    def g(self, *a):
        p = subprocess.run(["git", "-C", self.d, *a], capture_output=True, text=True, env=self.env)
        if p.returncode != 0:
            raise EvalError(f"fixture git {a}: {p.stderr.strip()[:200]}")
        return p.stdout

    def write(self, files):
        for path, content in files.items():
            full = os.path.join(self.d, path)
            os.makedirs(os.path.dirname(full) or self.d, exist_ok=True)
            data = content if isinstance(content, bytes) else ("\n".join(content) + "\n").encode()
            with open(full, "wb") as fh:
                fh.write(data)

    def commit(self, files):
        self.write(files)
        self.n += 1
        self.g("add", "-A")
        self.g("commit", "-q", "--allow-empty", "-m", f"c{self.n}")
        return self.g("rev-parse", "HEAD").strip()


NOTES = ["# notes",
         "ledger.md is append-only: entries are appended.",
         "score.md is append-only below its head.",
         "The head sections ## Axes and ## Plan of score.md are re-derived in place.",
         "know.md: its ## Errata region is append-only.",
         "ledger.md is appended here sometimes.",
         "ledger2.md is not append-only."]
ROW_LEDGER = "ledger.md\tA\tNOTES.md:2\t*\tfixture"
ROW_SCORE = "score.md\tA-corr\tNOTES.md:3\texempt=## Axes|## Plan@NOTES.md:4\tfixture"
ROW_KNOW = "know.md\tA-corr\tNOTES.md:5\tonly=## Errata@NOTES.md:5\tfixture"


def L(tag, n, start=0):
    return [f"{tag} line {i}" for i in range(start, start + n)]


def base(f, rows, files):
    files = dict(files)
    files["NOTES.md"] = NOTES
    files[CONTRACT] = [HEADER] + rows
    return f.commit(files)


def scenarios(root):
    """Yield (name, repo, expected events [(commit, file, {key: value})], expected summary subset,
    expected exit, expected event count)."""
    # S1 exact threshold: 20 -> event, 19 -> none
    f = Fx(root, "s1")
    base(f, [ROW_LEDGER], {"ledger.md": L("t", 40)})
    c1 = f.commit({"ledger.md": L("t", 20, 20)})
    f.commit({"ledger.md": L("t", 1, 39)})
    yield ("threshold", f.d, [(c1, "ledger.md", {"deleted": 20, "graded": 20, "ungraded": 0, "restored_max": 0,
                                                  "status": "unrestored", "held_at_to": 0})],
           {"unrestored": 1}, 1, 1)
    # S2 exempt head rewritten in place
    head, tail = ["# score", "## Axes"] + L("a", 24), ["## Round 1"] + L("r", 25)
    f = Fx(root, "s2")
    base(f, [ROW_SCORE], {"score.md": head + tail})
    c1 = f.commit({"score.md": ["# score", "## Axes"] + L("b", 24) + tail})
    yield ("exempt-rewritten", f.d, [(c1, "score.md", {"deleted": 24, "graded": 0, "ungraded": 24, "restored_max": 0,
                                                       "restored_best": None, "restored_by": None,
                                                       "status": "ungraded"})],
           {"ungraded": 1, "ungraded_lines": 24, "partial": 0, "unrestored": 0}, 0, 1)
    # S3 exempt head gutted, never restored
    f = Fx(root, "s3")
    base(f, [ROW_SCORE], {"score.md": head + tail})
    c1 = f.commit({"score.md": ["# score", "## Axes", "collapsed"] + tail})
    yield ("exempt-gutted", f.d, [(c1, "score.md", {"deleted": 24, "graded": 24, "ungraded": 0,
                                                    "status": "unrestored"})], {"unrestored": 1}, 1, 1)
    # S4 dated section rewritten in the exempt file
    f = Fx(root, "s4")
    base(f, [ROW_SCORE], {"score.md": head + tail})
    c1 = f.commit({"score.md": head + ["## Round 1"] + L("s", 25)})
    yield ("dated-rewritten", f.d, [(c1, "score.md", {"deleted": 25, "graded": 25, "ungraded": 0,
                                                      "status": "unrestored"})], {"unrestored": 1}, 1, 1)
    # S5 only=## Errata: body deletion ungraded, errata deletion graded
    f = Fx(root, "s5")
    kb, ke = ["# know", "## Body"] + L("k", 25), ["## Errata — x"] + L("e", 20)
    base(f, [ROW_KNOW], {"know.md": kb + ke})
    c1 = f.commit({"know.md": ["# know", "## Body"] + ke})
    c2 = f.commit({"know.md": ["# know", "## Body", "## Errata — x"]})
    yield ("only-errata", f.d, [(c1, "know.md", {"deleted": 25, "graded": 0, "ungraded": 25, "status": "ungraded"}),
                                (c2, "know.md", {"deleted": 20, "graded": 20, "ungraded": 0, "status": "unrestored"})],
           {"ungraded": 1, "unrestored": 1}, 1, 2)
    # S6 max(0, .) clamp: 20 duplicate lines of 30 and 20 unique lines deleted; the uniques come back
    f = Fx(root, "s6")
    base(f, [ROW_LEDGER], {"ledger.md": ["dup"] * 30 + L("u", 20)})
    c1 = f.commit({"ledger.md": ["dup"] * 10})
    c2 = f.commit({"ledger.md": L("u", 20)})
    yield ("clamp", f.d, [(c1, "ledger.md", {"deleted": 40, "graded": 40, "restored_max": 20, "restored_best": c2,
                                             "restored_by": None, "held_at_to": 20, "status": "partial"})],
           {"partial": 1}, 1, 1)
    # S7 merge: the first parent keeps the lines the side branch deleted
    f = Fx(root, "s7")
    base(f, [ROW_LEDGER], {"ledger.md": L("m", 30)})
    f.g("checkout", "-q", "-b", "side")
    f.commit({"ledger.md": L("m", 5, 25)})
    f.g("checkout", "-q", "main")
    f.commit({"ledger.md": L("m", 30) + ["n0"]})
    f.g("merge", "-q", "--no-edit", "side")
    m = f.g("rev-parse", "HEAD").strip()
    yield ("merge-first-parent", f.d, [(m, "ledger.md", {"deleted": 25, "graded": 25, "status": "unrestored",
                                                         "held_at_to": 0})], {}, 1, 2)
    # S8 restored then re-deleted below the threshold
    f = Fx(root, "s8")
    base(f, [ROW_LEDGER], {"ledger.md": L("g", 30)})
    c1 = f.commit({"ledger.md": L("g", 10, 20)})
    c2 = f.commit({"ledger.md": L("g", 30)})
    f.commit({"ledger.md": L("g", 25, 5)})
    yield ("regressed", f.d, [(c1, "ledger.md", {"deleted": 20, "graded": 20, "restored_max": 20, "restored_best": c2,
                                                 "restored_by": c2, "held_at_to": 15, "status": "restored"})],
           {"restored": 1, "regressed": 1}, 1, 1)
    # S9 `--` lines with CRLF endings
    f = Fx(root, "s9")
    dash = [f"-- dash {i}\r" for i in range(20)]
    base(f, [ROW_LEDGER], {"ledger.md": dash + L("keep", 5)})
    c1 = f.commit({"ledger.md": L("keep", 5)})
    yield ("dashdash-crlf", f.d, [(c1, "ledger.md", {"deleted": 20, "graded": 20, "status": "unrestored"})],
           {"unrestored": 1}, 1, 1)
    # S10 declarations that must not bind
    f = Fx(root, "s10")
    base(f, ["ledger.md\tA\tNOTES.md:6\t*\tno append-only",
             "ledger2.md\tA\tNOTES.md:7\t*\tnegation",
             "score.md\tA-corr\tNOTES.md:3\texempt=## Axes|## Round 1@NOTES.md:4\tunnamed title"],
         {"ledger.md": L("x", 3), "ledger2.md": L("y", 3), "score.md": head + tail})
    yield ("bad-declarations", f.d, [], {"bad_declarations": 3, "events": 0}, 1, 0)
    # S11 clean: restored and ungraded only
    f = Fx(root, "s11")
    base(f, [ROW_LEDGER, ROW_SCORE], {"ledger.md": L("c", 30), "score.md": head + tail})
    c1 = f.commit({"ledger.md": L("c", 10, 20), "score.md": ["# score", "## Axes"] + L("b", 24) + tail})
    c2 = f.commit({"ledger.md": L("c", 30)})
    yield ("clean", f.d, [(c1, "ledger.md", {"deleted": 20, "graded": 20, "restored_max": 20, "restored_by": c2,
                                             "held_at_to": 20, "status": "restored"}),
                          (c1, "score.md", {"deleted": 24, "ungraded": 24, "status": "ungraded"})],
           {"partial": 0, "unrestored": 0, "regressed": 0, "bad_declarations": 0}, 0, 2)


def fixture_leg(tool, root, detail):
    fails, n = 0, 0
    for name, repo, evs, summ, want_exit, nev in scenarios(root):
        n += 1
        code, j, err = run_tool(tool, repo, "HEAD")
        probs = []
        if not isinstance(j, dict) or j.get("schema") != "append-only-audit/v3":
            probs.append(f"no v3 JSON (exit {code}; {err.strip()[:120]})")
        else:
            te = {(e.get("commit"), e.get("file")): e for e in j.get("events") or [] if isinstance(e, dict)}
            if len(te) != nev:
                probs.append(f"events {len(te)} != {nev}")
            for c, fn, want in evs:
                e = te.get((c, fn))
                if e is None:
                    probs.append(f"missing event {c[:8]} {fn}")
                    continue
                for k, v in want.items():
                    if e.get(k) != v:
                        probs.append(f"{c[:8]} {fn} {k}={e.get(k)} want {v}")
            s = j.get("summary") or {}
            for k, v in summ.items():
                if s.get(k) != v:
                    probs.append(f"summary {k}={s.get(k)} want {v}")
        if code != want_exit:
            probs.append(f"exit {code} want {want_exit}")
        if probs:
            fails += 1
            detail.append(f"fixture {name}: " + "; ".join(probs)[:400])
    return fails, n


# ------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", required=True, help="lane clone (read-only)")
    ap.add_argument("--tip", required=True, help="full commit to measure")
    ap.add_argument("--scratch", default=None, help="scratch dir (default: TMPDIR)")
    ap.add_argument("--out", default=None, help="also write the receipt here")
    a = ap.parse_args(argv)
    root = a.scratch or tempfile.gettempdir()
    os.makedirs(root, exist_ok=True)
    S = tempfile.mkdtemp(prefix="r48c1-", dir=root)
    detail = []
    sel = con = lane = fix = stab = False
    nrows = nfiles = nev = ung = 0
    failures, fixfail = "NA", "NA"
    try:
        try:
            tip = git(a.repo, "rev-parse", "--verify", a.tip + "^{commit}").stdout.decode().strip()
        except EvalError as exc:
            print(f"could-not-evaluate: {exc}")
            return 2
        src = show(a.repo, tip, TOOL)
        tool = os.path.join(S, "append-only-audit.py")
        if src is None:
            detail.append(f"{TOOL} absent at tip")
        else:
            with open(tool, "wb") as fh:
                fh.write(src)
        # selftest
        if src is not None:
            st = os.path.join(S, "selftest")
            os.makedirs(st)
            p = subprocess.run([sys.executable, tool, "--selftest", "--scratch", st], capture_output=True, text=True,
                               timeout=1800)
            m = re.search(r"AOA_SELFTEST pass=(\d+) fail=(\d+)", p.stdout)
            sel = p.returncode == 0 and bool(m) and int(m.group(1)) >= 20 and m.group(2) == "0"
            if not sel:
                detail.append(f"selftest: exit {p.returncode} line {m.group(0) if m else None}")
        # contract
        craw = show(a.repo, tip, CONTRACT)
        rows = None
        cpath = os.path.join(S, "contract.tsv")
        if craw is None:
            detail.append(f"contract: {CONTRACT} absent at tip")
        else:
            with open(cpath, "wb") as fh:
                fh.write(craw)
            rows, why = parse_contract(craw.decode("utf-8", "replace"))
            if rows is None:
                detail.append(f"contract: {why}")
        rc = None
        if rows is not None:
            nrows = len(rows)
            con = True
            by_path = {r["path"]: r for r in rows}
            for path, want in REQUIRED.items():
                r = by_path.get(path)
                if r is None:
                    detail.append(f"contract: required row {path} missing")
                    con = False
                    continue
                reg = r["region"]
                if want[0] != reg[0] or (want[0] in ("exempt", "only") and reg[1] != want[1]):
                    detail.append(f"contract: {path} region {reg[:2]} want {want}")
                    con = False
            for r in rows:
                ok, why = row_binds(a.repo, tip, r)
                if not ok:
                    detail.append(f"contract: {r['path']}: {why}")
                    con = False
            try:
                rc = recompute(a.repo, tip, rows)
            except EvalError as exc:
                detail.append(f"lane: recomputation failed: {exc}")
            if rc is not None:
                nfiles, nev = len(rc["files"]), len(rc["events"])
                ung = rc["summary"]["ungraded_lines"]
                failures = rc["summary"]["partial"] + rc["summary"]["unrestored"]
        # lane
        if src is not None and rc is not None:
            code, j, err = run_tool(tool, a.repo, tip, cpath)
            if isinstance(j, dict):
                decl = j.get("declarations")
                if not isinstance(decl, list) or len(decl) != len(rows) or not all(
                        isinstance(d, dict) and d.get("ok") is True for d in decl):
                    detail.append("contract: tool declarations list is not one ok entry per row")
                    con = False
                if j.get("files") != rc["files"]:
                    con = False
            else:
                con = False
            mism = diff_result(j, rc, code, detail, "lane")
            s = rc["summary"]
            verdict = (failures == 0 and s["regressed"] == 0 and s["vanished"] == 0
                       and s["bad_declarations"] == 0 and ung > 0 and rc["exit"] == 0)
            if not verdict:
                detail.append(f"lane: derived verdict failures={failures} regressed={s['regressed']} "
                              f"vanished={s['vanished']} bad_declarations={s['bad_declarations']} "
                              f"ungraded_lines={ung} exit={rc['exit']}")
            lane = mism == 0 and verdict
        # fixture
        if src is not None:
            fr = os.path.join(S, "fx")
            os.makedirs(fr)
            try:
                nf, nt = fixture_leg(tool, fr, detail)
                fixfail = nf
                fix = nf == 0 and nt == 11
            except EvalError as exc:
                detail.append(f"fixture: {exc}")
        # stable
        if src is not None and rows is not None:
            if git(a.repo, "cat-file", "-e", STABLE_BASE + "^{commit}", check=False).returncode != 0:
                detail.append("stable: base commit absent from --repo")
            elif STABLE_BASE == tip:
                detail.append("stable: base equals tip")
            else:
                cb, jb, _ = run_tool(tool, a.repo, STABLE_BASE, cpath)
                ct, jt, _ = run_tool(tool, a.repo, tip, cpath)
                if not (isinstance(jb, dict) and isinstance(jt, dict)):
                    detail.append("stable: tool JSON missing")
                else:
                    eb = {(e.get("commit"), e.get("file")): e for e in jb.get("events") or []}
                    et = {(e.get("commit"), e.get("file")): e for e in jt.get("events") or []}
                    stab = len(eb) >= 1
                    if not eb:
                        detail.append("stable: no event at base")
                    for k, e in eb.items():
                        t = et.get(k)
                        if t is None or not isinstance(e.get("graded"), int) or any(
                                t.get(f) != e.get(f) for f in
                                ("deleted", "graded", "ungraded", "restored_max", "restored_best")):
                            detail.append(f"stable: {str(k[0])[:12]} {k[1]} changed or missing at tip")
                            stab = False
        met = bool(sel and con and lane and fix and stab)
        lines = [f"selftest={int(sel)} contract={int(con)} lane={int(lane)} fixture={int(fix)} stable={int(stab)} "
                 f"rows={nrows} files={nfiles} lane_events={nev} lane_failures={failures} ungraded_lines={ung} "
                 f"fixture_fail={fixfail} met={met}", f"tip={tip}"]
        lines += [f"detail: {d}" for d in detail]
        text = "\n".join(lines)
        print(text)
        if a.out:
            with open(a.out, "w") as fh:
                fh.write(text + "\n")
        return 0 if met else 1
    except EvalError as exc:
        print(f"could-not-evaluate: {exc}")
        return 2
    finally:
        shutil.rmtree(S, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
