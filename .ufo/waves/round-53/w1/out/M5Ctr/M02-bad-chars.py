#!/usr/bin/env python3
"""round53-cited-path-check.py - kama round-53 C2 (calibration) counter.

Question: at a lane revision, does every repository path the lane's self-assessment
cites as evidence resolve in the repository it names - or, where it does not, is the
miss disclosed in the lane's correction ledger with a reason the counter can re-derive
from git history?

Routed: corpus/lessons/round-52.md Mistakes #4 (an instrument-registry sentence cited a
receipt set that was not in the tree), seat W3Mistakes' proposed cited-path-exists check
(`.ufo/waves/round-52/w1/out/W3Mistakes/cited-path-exists.py`: misses=51 at the round-52
build, 50 of them "pre-existing" and never examined); SCORECARD §Planned (round 53) item
2 ("land seat W3Mistakes' ... cited-path-exists checks as lane instruments").

Frozen names (before data):
  surfaces  SCORECARD.md, SHONEN.md, SKILL.md (the self-assessment: scores and their
            evidence pointers, the promotion checklist, the instrument registries)
  ledger    registry/cited-path-corrections.tsv (tab-separated; `#` lines are comments;
            columns surface, token, class, evidence, note)
  base      4229ea1b9a789148dded1f159c20967d9a01373f (round-52 lane tip; round-53 start)
  fleet     the fleet repository given by --fleet, read at --fleet-rev (default its HEAD)

Citation (frozen parser): every backtick span on a line of a surface that is outside a
``` fence (a line whose stripped text starts with ``` toggles the fence; the restored
blocks of round 52 are fenced, so history kept verbatim is not a standing citation). The
span is a citation when, after a trailing `:N` / `:N-M` / `:N,M` line anchor and a `#fragment`
are cut off, it contains none of the characters ` <>$=()|'"` and either starts with one
of the lane roots `.ufo/ tools/ tests/ corpus/ registry/ plans/ considerthese/`, starts
with one of the fleet roots `scripts/ templates/`, or is one of the lane's top-level
files (AGENTS.md LOG.md MINT.md PROVINCE.md README.md SCORECARD.md SHONEN.md SKILL.md).
`{a,b}` groups expand (each expansion is checked). A span containing `*`, `?` or `[`
is a glob and resolves when it matches at least one path. A span ending in `/`, or one
that names a directory, resolves when some path lies beneath it.

Resolution: an expansion resolves when it is a path (or glob/directory match) in the lane
tree at --tip; failing that, when it is in the fleet tree at --fleet-rev. A resolved file
with a line anchor additionally needs at least as many lines as its largest number in the tree that resolved
it; otherwise the expansion is `beyond-eof`.

Ledger (frozen classes; a row covers every occurrence of its (surface, token) pair):
  deleted   evidence = full commit of the lane (or fleet) repo; every unresolved
            expansion exists at <commit>^ and not at <commit>.
  never     evidence `-`; no unresolved expansion was ever a path in any commit of the
            lane repo, nor of the fleet repo (`git log --all --name-only`, globs and
            directories matched against that set).
  moved     evidence = a path; it resolves at --tip in the lane tree and its blob there
            equals the token's blob at the last lane commit that held the token's path
            (single-path tokens only).
  eof       evidence = full commit; at that commit of the repo that resolves the file,
            it had at least max(N, M) lines (the anchor named an older version).
  untracked evidence `-`; a fleet-root token absent from the fleet tree that exists on
            disk under --fleet (a runtime file such as the driver's log).
  upstream  evidence = https://raw.githubusercontent.com/<owner>/<repo>/<ref>/<token>; a
            single token naming another project's file (llama.cpp's `tools/server/...`
            shares the lane's `tools/` root); the URL answers HTTP 200 when fetched here.
  fixed     evidence = a replacement token; the original token is no longer cited in
            that surface at --tip, it was cited there and unresolved at --base, and the
            replacement is cited in that surface at --tip and resolves.
A row is `bad` when its class check fails, and `stale` when its token is not an
unresolved citation of its surface at --tip (for `fixed`: when its check fails it is bad).

Legs:
  fixture  eight constructed scenarios in a scratch git repository (built here, never in
           the lane) each get the verdict their construction fixes: an unresolved path is
           counted; a fenced one is not; a brace group with one dead member is counted;
           a forged `deleted` row is bad; a true `deleted` row discloses; a forged `never`
           row is bad; a line anchor past EOF is counted; a ledger row for a resolving
           token is stale.
  lane     at --tip: every unresolved citation is disclosed by a good row (undisclosed=0),
           bad=0, stale=0, and every token SCORECARD.md cites at --base is still cited
           there (dropped=0; the file is append-only outside its head tables, and a
           dropped citation is a deleted claim, not a corrected one).
met = fixture and lane.
PREDICATE (same sentence in the preregistration): at the measured commit every
repository path that SCORECARD.md, SHONEN.md and SKILL.md cite outside fences resolves in
the lane tree or the fleet tree, or is disclosed by a correction-ledger row whose class
the counter re-derives from git history, with no bad or stale row and no SCORECARD.md
citation dropped since the base, and eight constructed scenarios each get their fixed
verdict; fixture=1 lane=1 undisclosed=0 bad=0 stale=0 dropped=0.

Output: `fixture=0|1 lane=0|1 scenarios=N/8 cited=N unresolved=N disclosed=N
undisclosed=N bad=N stale=N dropped=N met=True|False`, then `detail:` lines.
Exit 0 met, 1 not met, 2 could not evaluate. Read-only on --repo and --fleet; scratch
under --scratch (default TMPDIR), removed on exit.
"""
from __future__ import annotations

import argparse
import fnmatch
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

BASE = "4229ea1b9a789148dded1f159c20967d9a01373f"
SURFACES = ("SCORECARD.md", "SHONEN.md", "SKILL.md")
LEDGER = "registry/cited-path-corrections.tsv"
LANE_ROOTS = (".ufo/", "tools/", "tests/", "corpus/", "registry/", "plans/", "considerthese/")
FLEET_ROOTS = ("scripts/", "templates/")
TOP = ("AGENTS.md", "LOG.md", "MINT.md", "PROVINCE.md", "README.md", "SCORECARD.md",
       "SHONEN.md", "SKILL.md")
BAD_CHARS = set(" <>$=()|'\"*?")
ANCHOR = re.compile(r"^(.*?):(\d+(?:[-,]\d+)*)$")
CLASSES = ("deleted", "never", "moved", "eof", "untracked", "upstream", "fixed")
SCENARIOS = 8


class EvalError(Exception):
    pass


def git(repo, *args, check=True):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if check and p.returncode != 0:
        raise EvalError(f"git {' '.join(args)[:120]}: {p.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return p


def show(repo, rev, path):
    p = git(repo, "show", f"{rev}:{path}", check=False)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def tree_paths(repo, rev):
    out = git(repo, "ls-tree", "-r", "--name-only", "-z", rev).stdout.decode("utf-8", "replace")
    return set(p for p in out.split("\0") if p)


def history_paths(repo):
    out = git(repo, "log", "--all", "--name-only", "--format=", "-z").stdout.decode("utf-8", "replace")
    return set(p.strip("\n") for p in out.split("\0") if p.strip("\n"))


def expand_braces(tok):
    m = re.search(r"\{([^{}]*)\}", tok)
    if not m:
        return [tok]
    out = []
    for alt in m.group(1).split(","):
        out.extend(expand_braces(tok[:m.start()] + alt + tok[m.end():]))
    return out


def citations(text):
    """[(line_no, token, path_part, lo, hi)] of the frozen parser."""
    out, fenced = [], False
    for n, line in enumerate(text.split("\n"), 1):
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        for span in re.findall(r"`([^`\n]+)`", line):
            tok = span.strip()
            if tok.startswith("./"):
                tok = tok[2:]
            core = tok.split("#", 1)[0]
            lo = hi = None
            m = ANCHOR.match(core)
            if m:
                nums = [int(x) for x in re.split(r"[-,]", m.group(2))]
                core, lo, hi = m.group(1), min(nums), max(nums)
            if not core or any(c in BAD_CHARS for c in core):
                continue
            if not (core.startswith(LANE_ROOTS) or core.startswith(FLEET_ROOTS) or core in TOP):
                continue
            out.append((n, tok, core, lo, hi))
    return out


def matches(path, paths):
    """True when path (plain, glob or directory) names something in the set."""
    if any(c in path for c in "*?["):
        return any(fnmatch.fnmatchcase(p, path) for p in paths)
    if path.endswith("/"):
        return any(p.startswith(path) for p in paths)
    return path in paths or any(p.startswith(path + "/") for p in paths)


class Repo:
    def __init__(self, path, rev):
        self.path, self.rev = path, rev
        self.tree = tree_paths(path, rev)
        self._hist = None
        self._lines = {}

    def hist(self):
        if self._hist is None:
            self._hist = history_paths(self.path)
        return self._hist

    def nlines(self, rev, p):
        key = (rev, p)
        if key not in self._lines:
            t = show(self.path, rev, p)
            self._lines[key] = None if t is None else len(t.split("\n")) - (1 if t.endswith("\n") else 0)
        return self._lines[key]


def resolve(core, lo, hi, lane, fleet):
    """[(expansion, verdict)] with verdict in ok | missing | beyond-eof."""
    res = []
    for e in expand_braces(core):
        where = lane if matches(e, lane.tree) else (fleet if fleet is not None and matches(e, fleet.tree) else None)
        if where is None:
            res.append((e, "missing"))
        elif hi is not None and e in where.tree:
            n = where.nlines(where.rev, e)
            res.append((e, "ok" if n is not None and n >= max(lo, hi) else "beyond-eof"))
        else:
            res.append((e, "ok"))
    return res


def read_ledger(lane):
    text = show(lane.path, lane.rev, LEDGER)
    rows = []
    if text is None:
        return rows
    for n, line in enumerate(text.split("\n"), 1):
        if not line.strip() or line.startswith("#"):
            continue
        f = line.split("\t")
        if f[0] == "surface":
            continue
        f += [""] * (5 - len(f))
        rows.append({"line": n, "surface": f[0], "token": f[1], "class": f[2], "evidence": f[3]})
    return rows


def check_row(row, bad_exp, lane, fleet, cited_tip, base_unres):
    """None when the row's class re-derives; else the reason it is bad."""
    cls, ev, tok = row["class"], row["evidence"], row["token"]
    if cls not in CLASSES:
        return f"unknown class {cls!r}"
    if cls == "fixed":
        surf = row["surface"]
        if tok in cited_tip.get(surf, {}):
            return "fixed token is still cited at tip"
        if tok not in base_unres.get(surf, set()):
            return "fixed token was not an unresolved citation of this surface at base"
        rep = cited_tip.get(surf, {}).get(ev)
        if rep is None:
            return f"replacement {ev!r} is not cited in {surf} at tip"
        if any(v != "ok" for _e, v in rep):
            return f"replacement {ev!r} does not resolve at tip"
        return None
    if not bad_exp:
        return None  # stale; reported by the caller
    if cls == "deleted":
        for repo in (lane, fleet):
            if repo is None or not re.fullmatch(r"[0-9a-f]{40}", ev):
                continue
            if git(repo.path, "cat-file", "-e", f"{ev}^{{commit}}", check=False).returncode != 0:
                continue
            before = tree_paths(repo.path, f"{ev}^") if git(repo.path, "rev-parse", "--verify", "-q", f"{ev}^",
                                                             check=False).returncode == 0 else set()
            after = tree_paths(repo.path, ev)
            if all(matches(e, before) and not matches(e, after) for e, _v in bad_exp):
                return None
        return f"no repo has commit {ev[:12]} deleting {[e for e, _v in bad_exp]}"
    if cls == "never":
        for e, _v in bad_exp:
            if matches(e, lane.hist()) or (fleet is not None and matches(e, fleet.hist())):
                return f"{e} was a path in some commit"
        return None
    if cls == "moved":
        if len(bad_exp) != 1 or any(c in bad_exp[0][0] for c in "*?[") or not matches(ev, lane.tree) or ev not in lane.tree:
            return "moved needs one plain token and a replacement file in the tip tree"
        e = bad_exp[0][0]
        last = git(lane.path, "log", "--all", "-1", "--format=%H", "--", e).stdout.decode().strip()
        if not last:
            return f"{e} never existed in the lane"
        old = git(lane.path, "rev-parse", "-q", "--verify", f"{last}:{e}", check=False)
        if old.returncode != 0:
            old = git(lane.path, "rev-parse", "-q", "--verify", f"{last}^:{e}", check=False)
        new = git(lane.path, "rev-parse", "-q", "--verify", f"{lane.rev}:{ev}", check=False)
        if old.returncode or new.returncode or old.stdout != new.stdout:
            return f"blob of {e} at its last commit != blob of {ev} at tip"
        return None
    if cls == "eof":
        for e, v in bad_exp:
            if v != "beyond-eof":
                return f"{e} is missing, not beyond EOF"
        m = ANCHOR.match(tok.split("#", 1)[0])
        need = max(int(x) for x in re.split(r"[-,]", m.group(2))) if m else None
        for repo in (lane, fleet):
            if repo is None or need is None or not re.fullmatch(r"[0-9a-f]{40}", ev):
                continue
            if git(repo.path, "cat-file", "-e", f"{ev}^{{commit}}", check=False).returncode != 0:
                continue
            if all((repo.nlines(ev, e) or 0) >= need for e, _v in bad_exp):
                return None
        return f"no commit {ev[:12]} where the file held {need} lines"
    if cls == "upstream":
        # a path of another project's repository (llama.cpp `tools/server/...`): the
        # evidence is a pinned raw URL whose path ends in the token, fetched here (HTTP 200)
        if len(bad_exp) != 1 or not re.fullmatch(r"https://raw\.githubusercontent\.com/[\w.-]+/[\w.-]+/[\w.-]+/\S+", ev) \
                or not ev.endswith("/" + bad_exp[0][0]):
            return "upstream needs one token and a pinned raw.githubusercontent.com URL ending in it"
        try:
            opener = urllib.request.build_opener()
            with opener.open(urllib.request.Request(ev, method="GET"), timeout=60) as r:
                if r.status != 200:
                    return f"{ev} answered {r.status}"
        except (OSError, ValueError) as exc:
            return f"{ev} unfetchable: {exc}"
        return None
    if cls == "untracked":
        if fleet is None:
            return "no fleet repo"
        for e, v in bad_exp:
            if v != "missing" or not e.startswith((".ufo/",) + FLEET_ROOTS) or e in fleet.tree \
                    or not os.path.exists(os.path.join(fleet.path, e)):
                return f"{e} is not an untracked file on disk under the fleet root"
        return None
    return "unreachable"


def survey(lane, fleet, base_unres=None):
    """Counts and per-item detail for one lane revision."""
    cited, unres = {}, {}
    for surf in SURFACES:
        text = show(lane.path, lane.rev, surf)
        cited[surf] = {}
        unres[surf] = {}
        if text is None:
            continue
        for _n, tok, core, lo, hi in citations(text):
            r = resolve(core, lo, hi, lane, fleet)
            cited[surf].setdefault(tok, r)
            bad = [(e, v) for e, v in r if v != "ok"]
            if bad:
                unres[surf].setdefault(tok, bad)
    return cited, unres


def evaluate(lane, fleet, base_lane, detail, verbose=True):
    cited, unres = survey(lane, fleet)
    _bc, bunres = survey(base_lane, fleet) if base_lane is not None else ({}, {})
    base_unres = {s: set(v) for s, v in bunres.items()}
    rows = read_ledger(lane)
    disclosed, bad, stale = set(), [], []
    for row in rows:
        key = (row["surface"], row["token"])
        if row["surface"] not in SURFACES:
            bad.append((row, "unknown surface"))
            continue
        exp = unres.get(row["surface"], {}).get(row["token"])
        why = check_row(row, exp, lane, fleet, cited, base_unres)
        if row["class"] != "fixed" and not exp and why is None:
            stale.append(row)
        elif why is not None:
            bad.append((row, why))
        elif row["class"] != "fixed":
            disclosed.add(key)
    n_cited = sum(len(v) for v in cited.values())
    n_unres = sum(len(v) for v in unres.values())
    undisclosed = [(s, t, v) for s, d in unres.items() for t, v in d.items() if (s, t) not in disclosed]
    dropped = []
    if base_lane is not None:
        bt = show(base_lane.path, base_lane.rev, "SCORECARD.md") or ""
        tt = show(lane.path, lane.rev, "SCORECARD.md") or ""
        bset = {tok for _n, tok, *_r in citations(bt)}
        tset = {tok for _n, tok, *_r in citations(tt)}
        dropped = sorted(bset - tset)
    if verbose:
        for s, t, v in undisclosed:
            detail.append(f"undisclosed {s} `{t}`: {v}")
        for row, why in bad:
            detail.append(f"bad ledger line {row['line']} ({row['surface']} `{row['token']}` {row['class']}): {why}")
        for row in stale:
            detail.append(f"stale ledger line {row['line']} ({row['surface']} `{row['token']}`): token resolves or is not cited")
        for t in dropped:
            detail.append(f"dropped SCORECARD.md citation `{t}` (cited at base, not at tip)")
    counts = {"cited": n_cited, "unresolved": n_unres, "disclosed": len(disclosed),
              "undisclosed": len(undisclosed), "bad": len(bad), "stale": len(stale), "dropped": len(dropped)}
    ok = not undisclosed and not bad and not stale and not dropped
    return ok, counts


# ------------------------------------------------------------- fixture
def fixture(S, detail):
    """Eight scenarios on a scratch repository; returns the number that get their verdict."""
    D = tempfile.mkdtemp(prefix="r53c2-fx-", dir=S)
    env = dict(os.environ, GIT_AUTHOR_NAME="fixture", GIT_AUTHOR_EMAIL="fixture@invalid",
               GIT_COMMITTER_NAME="fixture", GIT_COMMITTER_EMAIL="fixture@invalid",
               GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")

    def g(*a):
        p = subprocess.run(["git", "-C", D, *a], capture_output=True, env=env)
        if p.returncode:
            raise EvalError(f"fixture git {a}: {p.stderr.decode()[:200]}")
        return p.stdout.decode().strip()

    def w(path, text):
        full = os.path.join(D, path)
        os.makedirs(os.path.dirname(full) or D, exist_ok=True)
        with open(full, "w") as fh:
            fh.write(text)

    def commit(msg):
        g("add", "-A")
        g("commit", "-q", "--allow-empty", "-m", msg)
        return g("rev-parse", "HEAD")

    g("init", "-q")
    if os.path.realpath(g("rev-parse", "--show-toplevel")) != os.path.realpath(D):
        raise EvalError("fixture repository is not the scratch directory")
    w("tools/a.py", "a\n")
    w("tools/gone.py", "g\n")
    w("corpus/x.md", "1\n2\n3\n")
    w("SHONEN.md", "x\n")
    w("SKILL.md", "x\n")
    w("SCORECARD.md", "start\n")
    c0 = commit("c0")
    g("rm", "-q", "tools/gone.py")
    cdel = commit("delete gone")

    def at(scard, ledger=None):
        w("SCORECARD.md", scard)
        if ledger is None:
            if os.path.exists(os.path.join(D, LEDGER)):
                os.unlink(os.path.join(D, LEDGER))
        else:
            w(LEDGER, "surface\ttoken\tclass\tevidence\tnote\n" + ledger)
        rev = commit("scenario")
        return Repo(D, rev)

    base = Repo(D, c0)
    got = 0
    cases = [
        ("unresolved path is counted", "see `tools/nope.py`\n", None, lambda ok, c: not ok and c["undisclosed"] == 1),
        ("fenced path is not cited", "```\n`tools/nope.py`\n```\n", None, lambda ok, c: ok and c["cited"] == 0),
        ("brace group with one dead member", "`tools/{a,nope}.py`\n", None, lambda ok, c: not ok and c["undisclosed"] == 1),
        ("forged deleted row is bad", "`tools/nope.py`\n", f"SCORECARD.md\ttools/nope.py\tdeleted\t{cdel}\t\n",
         lambda ok, c: not ok and c["bad"] == 1),
        ("true deleted row discloses", "`tools/gone.py`\n", f"SCORECARD.md\ttools/gone.py\tdeleted\t{cdel}\t\n",
         lambda ok, c: ok and c["disclosed"] == 1),
        ("forged never row is bad", "`tools/gone.py`\n", "SCORECARD.md\ttools/gone.py\tnever\t-\t\n",
         lambda ok, c: not ok and c["bad"] == 1),
        ("line anchor past EOF is counted", "`corpus/x.md:9`\n", None, lambda ok, c: not ok and c["undisclosed"] == 1),
        ("row for a resolving token is stale", "`tools/a.py`\n", "SCORECARD.md\ttools/a.py\tnever\t-\t\n",
         lambda ok, c: not ok and c["stale"] == 1),
    ]
    for name, scard, ledger, want in cases:
        lane = at(scard, ledger)
        sub = []
        ok, c = evaluate(lane, None, None, sub, verbose=False)
        hit = bool(want(ok, c))
        got += hit
        detail.append(f"fixture {'ok' if hit else 'FAIL'}: {name} (met={ok} {c})")
    shutil.rmtree(D, ignore_errors=True)
    return got


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", required=True, help="lane clone (read-only)")
    ap.add_argument("--tip", required=True, help="full commit to measure")
    ap.add_argument("--fleet", default="/home/vgpnk/Projects/shokunin", help="fleet repository (read-only)")
    ap.add_argument("--fleet-rev", default="HEAD")
    ap.add_argument("--scratch", default=None, help="scratch dir (default: TMPDIR)")
    ap.add_argument("--out", default=None, help="also write the receipt here")
    a = ap.parse_args(argv)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    root = a.scratch or tempfile.gettempdir()
    os.makedirs(root, exist_ok=True)
    S = tempfile.mkdtemp(prefix="r53c2-", dir=root)
    detail = []
    try:
        try:
            tip = git(a.repo, "rev-parse", "--verify", a.tip + "^{commit}").stdout.decode().strip()
            frev = git(a.fleet, "rev-parse", "--verify", a.fleet_rev + "^{commit}").stdout.decode().strip()
            lane, fleet = Repo(a.repo, tip), Repo(a.fleet, frev)
            base = Repo(a.repo, BASE)
            nfx = fixture(S, detail)
            lok, c = evaluate(lane, fleet, base, detail)
        except EvalError as exc:
            print(f"could-not-evaluate: {exc}")
            return 2
        fx = nfx == SCENARIOS
        met = bool(fx and lok)
        lines = [f"tip={tip} fleet={frev}",
                 f"fixture={int(fx)} lane={int(lok)} scenarios={nfx}/{SCENARIOS} cited={c['cited']} "
                 f"unresolved={c['unresolved']} disclosed={c['disclosed']} undisclosed={c['undisclosed']} "
                 f"bad={c['bad']} stale={c['stale']} dropped={c['dropped']} met={met}"]
        lines += [f"detail: {d}" for d in detail]
        text = "\n".join(lines)
        print(text)
        if a.out:
            with open(a.out, "w") as fh:
                fh.write(text + "\n")
        return 0 if met else 1
    finally:
        shutil.rmtree(S, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
