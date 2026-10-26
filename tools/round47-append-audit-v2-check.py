#!/usr/bin/env python3
"""round47-append-audit-v2-check.py - kama round-47 C1 (calibration) counter.

Question: at a lane revision, does the lane's append-only instrument agree with
ground truth it does not compute itself, and does it audit the append-only
self-description the lane actually declares? Round 46 acquired
tools/append-only-audit.py (v1). Its outside closure (corpus/lessons/
round-46-verifier-spotcheck.md, D1 and D2) and the round-46 wave found:
  D1  v1 drops every deleted line whose text starts with `--` (it filters
      `---` headers by prefix), so on the lane its deleted counts are low
      (0718b6ab SCORECARD.md 2417 vs `git diff --numstat` 2421; LOG.md 2290 vs
      2292), and the round-46 counter shared that rule;
  D2  v1's restored_at_tip is measured against the audited tip, so a later
      head re-anchor lowers it without any new deletion (2416 -> 2409);
  K2Design / Rev2Decl  the five-file default is declared nowhere as one set,
      and corpus/lessons/*.md, declared append-only, is not audited.
This counter scores v2 against the numstat count git itself prints, against a
constructed fixture whose answers are known by construction, and against a
machine-readable contract whose every row must point at a lane line that
declares the rule.

Frozen names (before data):
  tool       tools/append-only-audit.py
  contract   registry/append-only-contract.tsv
  threshold  20 deleted lines per (commit, file)

v2 definitions (the tool contract this counter scores):
  contract   tab-separated, first line exactly `path<TAB>rule<TAB>declared_at<TAB>note`;
             each later non-empty line has 4 cells: path is a repo-relative path
             or an fnmatch pattern (fnmatch.fnmatchcase on the full path), rule
             is one of A, A-row, A-corr, declared_at is `<repo-relative path>:<line>`.
  files      the contract's patterns expanded over `git ls-tree -r --name-only <to>`,
             sorted, de-duplicated.
  commits    `git rev-list --topo-order --reverse <to>`; a commit's diff is against
             its first parent; a root commit has no deletions.
  lines      a blob is split on b"\\n"; a final segment after the last b"\\n" is a
             line only when it is non-empty; lines compare byte-exact (a `\\r` is
             part of the line).
  deleted    the number of deleted lines of the first-parent diff of that file;
             it must equal the deletions `git diff --numstat --no-renames <p> <c> -- <file>`
             prints. D = the multiset of those deleted lines.
  event      (commit, file) with deleted >= threshold.
  held(x)    for a commit x: sum over line values l of min(D[l], max(0, M_x[l] - K[l]))
             where M_x is the multiset of the file's lines at x (empty when absent)
             and K = M_parent - D (the parent's lines the diff kept).
  window     the event commit and every later commit of the rev-list up to <to>.
  restored_max   the maximum of held(x) over the window.
  restored_best  the first window commit attaining restored_max; null when it is 0.
  restored_by    the first window commit with held(x) == deleted, else null.
  status     restored when restored_max == deleted, unrestored when 0, else partial.
Tool contract: `python3 tools/append-only-audit.py --repo R --to REV --contract C --json`
prints one JSON object with "schema": "append-only-audit/v2", "files" (sorted list)
and "events": list of objects with keys commit (40-hex), file, deleted,
restored_max, restored_best (40-hex or null), restored_by (40-hex or null), status;
exit 0 when no event is partial or unrestored, 1 when one is, 2 when it cannot
evaluate. `--selftest` prints a line `AOA_SELFTEST pass=<n> fail=<m>` and exits 0
only when m = 0.

Legs:
  selftest  the tool at --tip with `--selftest` exits 0 and prints
            `AOA_SELFTEST pass=n fail=0` with n >= 10.
  contract  registry/append-only-contract.tsv exists at --tip with the exact
            header; every row has 4 cells, a known rule, a declared_at path that
            exists at --tip and a line number whose text at --tip contains
            `append` (case-insensitive); the expansion holds SCORECARD.md, LOG.md,
            corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md and at least
            one corpus/lessons/*.md file; and the tool's lane run reports exactly
            that expansion as "files".
  lane      the tool on --repo at --tip (`--json --to <tip> --contract <the contract at tip>`)
            reports schema v2 and exactly the events this counter recomputes
            (the tool's source at --tip must not contain the string `round47`,
            so it cannot load this counter's recomputation):
            the (commit, file) set with numstat deletions >= 20, each with
            deleted equal to the numstat deletions, and restored_max,
            restored_best, restored_by and status equal to this counter's own
            recomputation; its exit code agrees with the statuses.
  fixture   this counter builds a fresh git repo under --scratch with random
            line content (os.urandom) and random sizes: `--`-prefixed lines, a
            `---` line, CRLF lines, a triplicated line and a final line without
            a newline; a pure-deletion event on LOG.md later partly restored (an
            LF copy of a deleted CRLF line must not count), a never-restored
            event on a corpus/lessons file, a deleted-then-fully-restored event
            whose restoration is partly deleted again below the threshold (the
            window maximum must keep it restored), a relocated 21-line block
            (held in its own commit), a 19-line deletion (no event) and an
            undeclared file losing 30 lines (no event). The tool must report
            exactly the constructed events with the constructed values, the
            contract's file expansion, and exit 1.
  stable    the tool on the lane `--to <base>` and `--to <tip>` (tip contract):
            at least one event at base, and every base event appears at tip
            with equal deleted and restored_max(tip) >= restored_max(base).
met = selftest and contract and lane and fixture and stable.
PREDICATE (same sentence in the preregistration): append-only-audit v2 at the
measured commit passes its selftest, audits exactly the files a resolvable
append-only contract declares, matches git numstat and this counter's
recomputation on the lane's own history and a constructed fixture, and does not
lower a restoration when the audited tip moves; selftest=1 contract=1 lane=1
fixture=1 stable=1.

Output: `selftest=0|1 contract=0|1 lane=0|1 fixture=0|1 stable=0|1 files=F
lane_events=E lane_mismatch=M fixture_mismatch=X met=True|False`, then `detail:` lines.
Exit 0 met, 1 not met, 2 could not evaluate (git failure on --repo).
Read-only on --repo; fixtures live under --scratch (or TMPDIR) and are removed on exit.
"""
from __future__ import annotations

import argparse
import collections
import fnmatch
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile

TOOL = "tools/append-only-audit.py"
CONTRACT = "registry/append-only-contract.tsv"
HEADER = "path\trule\tdeclared_at\tnote"
RULES = {"A", "A-row", "A-corr"}
REQUIRED = ["SCORECARD.md", "LOG.md", "corpus/QUALITY.md", "corpus/README.md", "corpus/SOURCES.md"]
THRESHOLD = 20
KEYS = ("commit", "file", "deleted", "restored_max", "restored_best", "restored_by", "status")
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
FIX_ENV = {"GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@kama.invalid",
           "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@kama.invalid",
           "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}


class EvalError(Exception):
    pass


def git(repo, *args, check=True, env=None, inp=None):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, env=env, input=inp)
    if check and p.returncode != 0:
        raise EvalError(f"git {' '.join(args)[:120]}: {p.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return p


def gtext(repo, *args, **kw):
    return git(repo, *args, **kw).stdout.decode("utf-8", "replace")


def blob_lines(repo, rev, path, cache):
    key = (rev, path)
    if key not in cache:
        p = git(repo, "cat-file", "-p", f"{rev}:{path}", check=False)
        if p.returncode != 0:
            cache[key] = collections.Counter()
        else:
            segs = p.stdout.split(b"\n")
            if segs and segs[-1] == b"":
                segs.pop()
            cache[key] = collections.Counter(segs)
    return cache[key]


def deleted_lines(repo, parent, commit, path):
    """Deleted lines of the first-parent -U0 diff, read by hunk-header counts."""
    raw = git(repo, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", "--text",
              parent, commit, "--", path).stdout
    out = []
    lines = raw.split(b"\n")
    i = 0
    hunk = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
    while i < len(lines):
        m = hunk.match(lines[i])
        if not m:
            i += 1
            continue
        nd = int(m.group(2)) if m.group(2) is not None else 1
        na = int(m.group(4)) if m.group(4) is not None else 1
        i += 1
        got_d = got_a = 0
        while i < len(lines) and (got_d < nd or got_a < na):
            ln = lines[i]
            if ln.startswith(b"-") and got_d < nd:
                out.append(ln[1:])
                got_d += 1
            elif ln.startswith(b"+") and got_a < na:
                got_a += 1
            i += 1
    return out


def numstat(repo, parent, commit, paths):
    res = {}
    if not paths:
        return res
    raw = gtext(repo, "diff", "--numstat", "--no-renames", parent, commit, "--", *paths)
    for line in raw.split("\n"):
        parts = line.split("\t")
        if len(parts) >= 3 and parts[1].isdigit():
            res[parts[2]] = int(parts[1])
    return res


def recompute(repo, to, files, threshold=THRESHOLD):
    to = gtext(repo, "rev-parse", "--verify", to + "^{commit}").strip()
    order = gtext(repo, "rev-list", "--topo-order", "--reverse", "--parents", to).split("\n")
    commits, parents = [], {}
    for line in order:
        parts = line.split()
        if parts:
            commits.append(parts[0])
            parents[parts[0]] = parts[1] if len(parts) > 1 else None
    cache = {}
    events = []
    for i, c in enumerate(commits):
        p = parents[c]
        if p is None:
            continue
        ns = numstat(repo, p, c, files)
        for f in sorted(ns):
            if ns[f] < threshold:
                continue
            dl = deleted_lines(repo, p, c, f)
            if len(dl) != ns[f]:
                raise EvalError(f"hunk parse {len(dl)} != numstat {ns[f]} at {c[:12]} {f}")
            D = collections.Counter(dl)
            K = blob_lines(repo, p, f, cache) - D
            best, best_c, by = 0, None, None
            for x in commits[i:]:
                M = blob_lines(repo, x, f, cache)
                h = sum(min(n, max(0, M[l] - K[l])) for l, n in D.items())
                if h > best:
                    best, best_c = h, x
                if by is None and h == len(dl):
                    by = x
                if h == len(dl):
                    break
            status = "restored" if best == len(dl) else ("unrestored" if best == 0 else "partial")
            events.append({"commit": c, "file": f, "deleted": len(dl), "restored_max": best,
                           "restored_best": best_c, "restored_by": by, "status": status})
    return events


def read_contract(repo, tip):
    p = git(repo, "show", f"{tip}:{CONTRACT}", check=False)
    if p.returncode != 0:
        return None, ["contract: absent at tip"]
    text = p.stdout.decode("utf-8", "replace")
    lines = text.split("\n")
    probs = []
    if not lines or lines[0] != HEADER:
        return None, ["contract: header line is not exactly path<TAB>rule<TAB>declared_at<TAB>note"]
    rows = []
    for n, line in enumerate(lines[1:], 2):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != 4:
            probs.append(f"contract line {n}: {len(cells)} cells")
            continue
        rows.append((n, cells))
    if not rows:
        probs.append("contract: no rows")
    return rows, probs


def contract_files(repo, rev, rows):
    tree = gtext(repo, "ls-tree", "-r", "--name-only", rev).split("\n")
    tree = [t for t in tree if t]
    out = set()
    for _, cells in rows:
        pat = cells[0].strip()
        out.update(t for t in tree if fnmatch.fnmatchcase(t, pat))
    return sorted(out)


def leg_contract(repo, tip, detail):
    rows, probs = read_contract(repo, tip)
    if rows is None:
        detail.extend(probs)
        return False, []
    for n, cells in rows:
        pat, rule, decl = cells[0].strip(), cells[1].strip(), cells[2].strip()
        if rule not in RULES:
            probs.append(f"contract line {n}: rule {rule!r} not in {sorted(RULES)}")
        m = re.fullmatch(r"([^:]+):(\d+)", decl)
        if not m:
            probs.append(f"contract line {n}: declared_at {decl!r} is not path:line")
            continue
        p = git(repo, "show", f"{tip}:{m.group(1)}", check=False)
        if p.returncode != 0:
            probs.append(f"contract line {n}: declared_at path {m.group(1)} absent at tip")
            continue
        flines = p.stdout.decode("utf-8", "replace").split("\n")
        k = int(m.group(2))
        if k < 1 or k > len(flines) or "append" not in flines[k - 1].lower():
            probs.append(f"contract line {n}: {decl} does not hold a line containing 'append'")
        if not pat:
            probs.append(f"contract line {n}: empty path")
    files = contract_files(repo, tip, rows)
    for f in REQUIRED:
        if f not in files:
            probs.append(f"contract expansion lacks {f}")
    if not any(f.startswith("corpus/lessons/") and f.endswith(".md") for f in files):
        probs.append("contract expansion holds no corpus/lessons/*.md file")
    detail.extend(probs)
    return not probs, files


def run_tool(tool_path, args, scratch, timeout=1800):
    env = dict(os.environ, TMPDIR=scratch)
    p = subprocess.run([sys.executable, tool_path, *args], capture_output=True, text=True,
                       env=env, timeout=timeout)
    return p


def parse_json(p):
    try:
        return json.loads(p.stdout)
    except (ValueError, TypeError):
        return None


def norm(events):
    out = set()
    for e in events or []:
        try:
            out.add(tuple(e[k] for k in KEYS))
        except (KeyError, TypeError):
            out.add(("malformed", json.dumps(e, sort_keys=True)[:200]))
    return out


def expected_exit(events):
    return 1 if any(e["status"] != "restored" for e in events) else 0


def leg_selftest(tool_path, scratch, detail):
    try:
        p = run_tool(tool_path, ["--selftest", "--scratch", scratch], scratch, timeout=900)
    except subprocess.TimeoutExpired:
        detail.append("selftest: timeout")
        return False
    m = re.search(r"AOA_SELFTEST pass=(\d+) fail=(\d+)", p.stdout)
    ok = p.returncode == 0 and m is not None and int(m.group(2)) == 0 and int(m.group(1)) >= 10
    if not ok:
        detail.append(f"selftest: exit={p.returncode} line={m.group(0) if m else None}")
    return ok


def compare(tag, got, want, detail, limit=12):
    g, w = norm(got), norm(want)
    miss, extra = sorted(w - g, key=str), sorted(g - w, key=str)
    for x in miss[:limit]:
        detail.append(f"{tag} missing {x}")
    for x in extra[:limit]:
        detail.append(f"{tag} unexpected {x}")
    return len(miss) + len(extra)


def tip_contract(repo, tip, scratch):
    path = os.path.join(scratch, "contract-at-tip.tsv")
    with open(path, "wb") as fh:
        fh.write(git(repo, "show", f"{tip}:{CONTRACT}").stdout)
    return path


def leg_lane(tool_path, repo, tip, files, scratch, detail):
    with open(tool_path, "rb") as fh:
        if b"round47" in fh.read():
            detail.append("lane: tool source names round47 (not independent of this counter)")
            return False, 0, -1, None
    try:
        p = run_tool(tool_path, ["--repo", repo, "--to", tip, "--contract", tip_contract(repo, tip, scratch),
                                 "--json"], scratch)
    except subprocess.TimeoutExpired:
        detail.append("lane: tool timeout")
        return False, 0, -1, None
    out = parse_json(p)
    if not isinstance(out, dict):
        detail.append(f"lane: tool exit={p.returncode}, stdout is not one JSON object")
        return False, 0, -1, None
    ok = True
    if out.get("schema") != "append-only-audit/v2":
        detail.append(f"lane: schema {out.get('schema')!r}")
        ok = False
    want = recompute(repo, tip, files)
    mism = compare("lane", out.get("events"), want, detail)
    if mism:
        ok = False
    if p.returncode != expected_exit(want):
        detail.append(f"lane: exit {p.returncode} vs expected {expected_exit(want)}")
        ok = False
    return ok, len(want), mism, out.get("files")


def build_fixture(root):
    """Construct the fixture repo and return (path, last_commit, expected_events, expected_files)."""
    rnd = random.Random(os.urandom(16))
    D = tempfile.mkdtemp(prefix="aoa-v2-fx-", dir=root)
    git(D, "init", "-q", env=dict(os.environ, **FIX_ENV))
    top = git(D, "rev-parse", "--show-toplevel").stdout.decode().strip()
    if os.path.realpath(top) != os.path.realpath(D):
        raise EvalError(f"fixture toplevel {top} != {D}")
    env = dict(os.environ, **FIX_ENV)

    def tok():
        return os.urandom(rnd.randint(6, 14)).hex()

    def write(path, lines, final_newline=True):
        full = os.path.join(D, path)
        os.makedirs(os.path.dirname(full) or D, exist_ok=True)
        data = b"\n".join(lines)
        if final_newline:
            data += b"\n"
        with open(full, "wb") as fh:
            fh.write(data)

    def commit(msg):
        git(D, "add", "-A", env=env)
        git(D, "commit", "-q", "--allow-empty", "-m", msg, env=env)
        return git(D, "rev-parse", "HEAD").stdout.decode().strip()

    # LOG.md body: plain lines plus special lines at random positions.
    plain = [("entry " + tok()).encode() for _ in range(rnd.randint(70, 90))]
    dashed = [("--out " + tok()).encode() for _ in range(3)]
    rule = [b"---", ("--- " + tok()).encode()]
    crlf = [(tok() + "\r").encode() for _ in range(2)]
    trip = ("triplicated " + tok()).encode()
    special = dashed + rule + crlf + [trip, trip, trip]
    log = plain[:]
    for s in special:
        log.insert(rnd.randint(0, len(log)), s)
    last = ("last line without newline " + tok()).encode()
    log.append(last)
    lesson1 = [("lesson " + tok()).encode() for _ in range(rnd.randint(40, 50))]
    lesson2 = [("lesson two " + tok()).encode() for _ in range(10)]
    notes = [("note " + tok()).encode() for _ in range(40)]
    agents = [b"# fixture lane", b"LOG.md and corpus/lessons/*.md are append-only here."]
    contract = [HEADER.encode(), b"LOG.md\tA-corr\tAGENTS.md:2\tfixture",
                b"corpus/lessons/*.md\tA-corr\tAGENTS.md:2\tfixture"]
    write("LOG.md", log, final_newline=False)
    write("corpus/lessons/r1.md", lesson1)
    write("corpus/lessons/r2.md", lesson2)
    write("notes.md", notes)
    write("AGENTS.md", agents)
    write(CONTRACT, contract)
    commit("c-root")
    exp = []

    # E1: pure deletion on LOG.md including every special kind.
    trip_idx = [i for i, l in enumerate(log) if l == trip]
    must = set(i for i, l in enumerate(log) if l in dashed or l in rule or l in crlf)
    must.add(trip_idx[rnd.randrange(3)])
    must.add(len(log) - 1)  # the final line without newline
    plain_idx = [i for i, l in enumerate(log) if l in set(plain)]
    k1 = rnd.randint(22, 30)
    extra = rnd.sample(plain_idx, k1 - len(must))
    gone = must | set(extra)
    d1 = [log[i] for i in sorted(gone)]
    log = [l for i, l in enumerate(log) if i not in gone]
    write("LOG.md", log)
    e1 = commit("c-e1")
    # undeclared notes.md loses 30 lines (no event)
    notes = notes[30:]
    write("notes.md", notes)
    commit("c-notes")
    # R1: append r1 deleted lines back (plain ones plus one triplicated copy) and
    # an LF copy of one deleted CRLF line (must not count).
    d1_plain = [l for l in d1 if l in set(plain)]
    r1_plain = rnd.sample(d1_plain, rnd.randint(4, len(d1_plain) - 4))
    back = r1_plain + [trip]
    log = log + back + [crlf[0][:-1]]
    write("LOG.md", log)
    r1c = commit("c-r1")
    r1 = len(back)
    # E2: never-restored deletion on corpus/lessons/r1.md.
    k2 = rnd.randint(20, 26)
    idx = set(rnd.sample(range(len(lesson1)), k2))
    lesson1 = [l for i, l in enumerate(lesson1) if i not in idx]
    write("corpus/lessons/r1.md", lesson1)
    e2 = commit("c-e2")
    exp.append({"commit": e2, "file": "corpus/lessons/r1.md", "deleted": k2, "restored_max": 0,
                "restored_best": None, "restored_by": None, "status": "unrestored"})
    # E3: delete k3 plain lines, restore them all, then delete a few again (below threshold).
    remaining_plain = [l for l in log if l in set(plain) and l not in set(back)]
    k3 = THRESHOLD + rnd.randint(0, 4)
    d3 = set(rnd.sample(remaining_plain, k3))
    log = [l for l in log if l not in d3]
    write("LOG.md", log)
    e3 = commit("c-e3")
    log = log + sorted(d3)
    write("LOG.md", log)
    r3 = commit("c-r3")
    again = set(rnd.sample(sorted(d3), rnd.randint(3, 8))) | set(rnd.sample(r1_plain, 2))
    log = [l for l in log if l not in again]
    write("LOG.md", log)
    commit("c-again")
    exp.append({"commit": e3, "file": "LOG.md", "deleted": k3, "restored_max": k3,
                "restored_best": r3, "restored_by": r3, "status": "restored"})
    exp.append({"commit": e1, "file": "LOG.md", "deleted": k1, "restored_max": r1,
                "restored_best": r1c, "restored_by": None, "status": "partial"})
    # Relocate a 21-line block from the top to the end (one commit).
    block = log[:21]
    log = log[21:] + block
    write("LOG.md", log)
    mv = commit("c-move")
    exp.append({"commit": mv, "file": "LOG.md", "deleted": 21, "restored_max": 21,
                "restored_best": mv, "restored_by": mv, "status": "restored"})
    # 19-line deletion: below threshold, no event.
    cut = set(rnd.sample(range(len(log)), 19))
    log = [l for i, l in enumerate(log) if i not in cut]
    write("LOG.md", log)
    lastc = commit("c-19")
    return D, lastc, exp, ["LOG.md", "corpus/lessons/r1.md", "corpus/lessons/r2.md"]


def leg_fixture(tool_path, scratch, detail):
    try:
        D, last, exp, files = build_fixture(scratch)
    except (EvalError, OSError) as exc:
        detail.append(f"fixture: build failed: {exc}")
        return False, -1
    try:
        # self-check: the counter's own recomputation must equal the construction
        own = recompute(D, last, files)
        selfm = compare("fixture-selfcheck", own, exp, detail)
        if selfm:
            raise EvalError("fixture construction disagrees with the counter's recomputation")
        try:
            p = run_tool(tool_path, ["--repo", D, "--to", last, "--contract", os.path.join(D, CONTRACT),
                                     "--json"], scratch, timeout=600)
        except subprocess.TimeoutExpired:
            detail.append("fixture: tool timeout")
            return False, -1
        out = parse_json(p)
        if not isinstance(out, dict):
            detail.append(f"fixture: tool exit={p.returncode}, stdout is not one JSON object")
            return False, -1
        ok = True
        if out.get("schema") != "append-only-audit/v2":
            detail.append(f"fixture: schema {out.get('schema')!r}")
            ok = False
        if out.get("files") != files:
            detail.append(f"fixture: files {out.get('files')!r} != {files!r}")
            ok = False
        mism = compare("fixture", out.get("events"), exp, detail)
        if mism:
            ok = False
        if p.returncode != 1:
            detail.append(f"fixture: exit {p.returncode} (want 1)")
            ok = False
        return ok, mism
    finally:
        shutil.rmtree(D, ignore_errors=True)


def leg_stable(tool_path, repo, base, tip, scratch, detail):
    res = {}
    for name, rev in (("base", base), ("tip", tip)):
        try:
            p = run_tool(tool_path, ["--repo", repo, "--to", rev, "--contract", tip_contract(repo, tip, scratch),
                                     "--json"], scratch)
        except subprocess.TimeoutExpired:
            detail.append(f"stable: tool timeout at {name}")
            return False
        out = parse_json(p)
        if not isinstance(out, dict) or not isinstance(out.get("events"), list):
            detail.append(f"stable: no JSON events at {name} (exit {p.returncode})")
            return False
        res[name] = out["events"]
    try:
        tipmap = {(e["commit"], e["file"]): e for e in res["tip"]}
        if not res["base"]:
            detail.append("stable: no event at base")
            return False
        ok = True
        for e in res["base"]:
            t = tipmap.get((e["commit"], e["file"]))
            if t is None or t["deleted"] != e["deleted"] or t["restored_max"] < e["restored_max"]:
                detail.append(f"stable: {e['commit'][:12]} {e['file']} base={e.get('restored_max')} "
                              f"tip={None if t is None else t.get('restored_max')}")
                ok = False
        return ok
    except (KeyError, TypeError) as exc:
        detail.append(f"stable: malformed event ({exc})")
        return False


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", required=True, help="lane clone (read-only)")
    ap.add_argument("--tip", required=True, help="full commit to measure")
    ap.add_argument("--base", default="172b8ad040d51ce8c011238c1408d4e0b6aa9595",
                    help="round-47 base (default: the frozen base)")
    ap.add_argument("--scratch", default=None, help="scratch dir (default: TMPDIR)")
    ap.add_argument("--out", default=None, help="also write the receipt here")
    a = ap.parse_args(argv)
    root = a.scratch or tempfile.gettempdir()
    os.makedirs(root, exist_ok=True)
    scratch = tempfile.mkdtemp(prefix="r47c1-", dir=root)
    detail = []
    try:
        try:
            tip = gtext(a.repo, "rev-parse", "--verify", a.tip + "^{commit}").strip()
            base = gtext(a.repo, "rev-parse", "--verify", a.base + "^{commit}").strip()
        except EvalError as exc:
            print(f"could-not-evaluate: {exc}")
            return 2
        tool_path = os.path.join(scratch, "append-only-audit.py")
        p = git(a.repo, "show", f"{tip}:{TOOL}", check=False)
        have_tool = p.returncode == 0
        if have_tool:
            with open(tool_path, "wb") as fh:
                fh.write(p.stdout)
        else:
            detail.append("tool absent at tip")
        try:
            con, files = leg_contract(a.repo, tip, detail)
            sel = have_tool and leg_selftest(tool_path, scratch, detail)
            lane, ev, lmis, tfiles = (leg_lane(tool_path, a.repo, tip, files, scratch, detail)
                                      if have_tool and files else (False, 0, -1, None))
            if con and tfiles != files:
                detail.append(f"contract: tool files ({0 if tfiles is None else len(tfiles)}) != expansion ({len(files)})")
                con = False
            fx, fmis = leg_fixture(tool_path, scratch, detail) if have_tool else (False, -1)
            st = (leg_stable(tool_path, a.repo, base, tip, scratch, detail)
                  if have_tool and files else False)
        except EvalError as exc:
            print(f"could-not-evaluate: {exc}")
            return 2
        met = bool(sel and con and lane and fx and st)
        lines = [f"selftest={int(bool(sel))} contract={int(bool(con))} lane={int(bool(lane))} "
                 f"fixture={int(bool(fx))} stable={int(bool(st))} files={len(files)} lane_events={ev} "
                 f"lane_mismatch={lmis} fixture_mismatch={fmis} met={met}",
                 f"tip={tip} base={base}"]
        lines += [f"detail: {d}" for d in detail]
        text = "\n".join(lines)
        print(text)
        if a.out:
            with open(a.out, "w") as fh:
                fh.write(text + "\n")
        return 0 if met else 1
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
