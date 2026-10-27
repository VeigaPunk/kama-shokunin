#!/usr/bin/env python3
"""round54-cited-path-check.py - kama round-54 C2 (calibration) counter, frozen for
kama round 55 (preregistration .ufo/waves/round-55/preregistration.json; round-55
delta: the `superseded` class added with its fixture scenario - the round-54
vocabulary could not row a live citation re-pointed to a different file, which the
base control's dropped=1 demonstrates. BASE stays at the round-53 tip: the drop
horizon must include the round-54 re-anchor; a same-tip base would let the
do-nothing control pass, which the round-55 pre-freeze check caught and reverted).

Question: at a lane revision, does every repository path the lane's self-assessment
cites as evidence resolve in the repository it names - or, where it does not, is the
miss disclosed in the lane's correction ledger with a reason the counter re-derives
from git history - with citation drops guarded on every self-assessment surface,
upstream evidence pinned to a fixed revision and digest, replacements bound to what the
ellipsis stood for, and every git call run in an environment stripped of inherited
GIT_* redirection?

Routed: the round-53 outside closure (MANIFEST rounds[810]): C2 falsified by
committed hide/wrong-bytes controls - J12Hide HIGH (hiding a dead SKILL.md citation
with its ledger row removed met the frozen counter: its dropped leg read SCORECARD.md
only), J11BadFixed/V5Review HIGH (the upstream class accepted any HTTP-200 URL at any
ref; the fixed class accepted any resolving replacement), Sen4Fixture HIGH (the
fixture's git calls honored inherited GIT_DIR/GIT_CONFIG_COUNT: commits landed in an
arbitrary repository and an arbitrary hook executed), K4Cheat (history legs read
`git log --all`, so a clone's unrelated fixture branches flipped `never` rows; prose
citations were invisible), M6Ledger survivors M10-M13 and M15 (upstream ref/owner
mutations, an upstream->never class swap, a fixed replacement cited away from the
correction line); round-53 SCORECARD §Planned (round 54) item 2.

Frozen names (before data):
  surfaces  SCORECARD.md, SHONEN.md, SKILL.md (the self-assessment: scores and their
            evidence pointers, the promotion checklist, the instrument registries)
  ledger    registry/cited-path-corrections.tsv (tab-separated; `#` lines are comments;
            columns surface, token, class, evidence, note)
  base      0b75a84c56e024cac1662e8ff81802f249acb410 (round-53 lane tip; round-54 start)
  fleet     the fleet repository given by --fleet, read at --fleet-rev (default its HEAD)
  upstream  the four llama.cpp tools/server files the lane pins: owner/repo frozen to
            ggml-org/llama.cpp, revision frozen to
            704366d76f8748cf9ad3df62a464bfcc8d1ae6ad, digest frozen to what the citing
            surface states (full 64-hex, or the truncated first/last form)

Citation (frozen parser): every backtick span on a line of a surface that is outside a
``` fence (a line whose stripped text starts with ``` toggles the fence; the restored
blocks of round 52 are fenced, so history kept verbatim is not a standing citation). The
span is a citation when, after a trailing `:N` / `:N-M` / `:N,M` line anchor and a
`#fragment` are cut off, it contains none of the characters ` <>$=()|'"` and either
starts with one of the lane roots `.ufo/ tools/ tests/ corpus/ registry/ plans/
considerthese/`, starts with one of the fleet roots `scripts/ templates/`, or is one of
the lane's top-level files. `{a,b}` groups expand. A span containing `*`, `?` or `[` is
a glob. A span ending in `/`, or one that names a directory, resolves when some path
lies beneath it. Prose-shaped lane/fleet-root tokens are surfaced as advisory detail
lines (K4Cheat a2); they are not citations and do not gate.

Resolution: an expansion resolves when it is a path (or glob/directory match) in the
lane tree at --tip; failing that, when it is in the fleet tree at --fleet-rev. A
resolved file with a line anchor additionally needs at least as many lines as its
largest anchor number; otherwise the expansion is `beyond-eof`.

Ledger (frozen classes; a row covers every occurrence of its (surface, token) pair):
  deleted      evidence = full commit of the lane (or fleet) repo; every unresolved
               expansion exists at <commit>^ and not at <commit>.
  never        evidence `-`; no unresolved expansion was ever a path in any commit
               reachable from BASE or --tip of the lane repo, nor of the fleet repo
               (history legs are scoped to BASE..tip - K4Cheat X - with an `--all`
               fallback for repos that do not contain BASE). A token of the lane's
               frozen upstream inventory (llama.cpp's tools/server files) cannot be
               classed `never`: its provenance is upstream (M6Ledger M13).
  moved        evidence = a path; it resolves at --tip in the lane tree and its blob
               there equals the token's blob at the last lane commit, reachable from
               BASE or tip, that held the token's path (single-path tokens only).
  eof          evidence = full commit; at that commit of the repo that resolves the
               file, it had at least max(N, M) lines (the anchor named an older
               version).
  untracked    evidence `-`; a fleet-root token absent from the fleet tree that exists
               on disk under --fleet (a runtime file such as the driver's log).
  upstream     evidence = https://raw.githubusercontent.com/<owner>/<repo>/<ref>/<token>;
               a single token naming another project's file. The URL must name a FULL
               40-hex commit (a tag, branch, fork or prefix-resolved sha fails), and
               for the lane's pinned tokens the owner/repo and the commit must equal
               the frozen pins. The counter fetches the URL, sha256s the body and
               compares it with the digest the citing surface states for that token
               (full 64-hex, or the truncated first/last form); when the surface states
               nothing, the frozen pin's digest is used. An unfetchable URL is
               could-not-evaluate (exit 2), never a bad row (V5Review).
  fixed        evidence = a replacement token; the original token is no longer cited in
               that surface at --tip, it was cited there and unresolved at --base, the
               replacement is cited in that surface at --tip, resolves, EXTENDS the
               original token's stem up to its ellipsis or brace (J11BadFixed F2), and
               is cited at the SAME line where the base cited the original (M6Ledger
               M15: a resolving replacement cited elsewhere is not the correction).
  externalized (round 54) evidence = replacement text that now appears in that surface
               at --tip verbatim and is not itself a citation (J12Hide's unrowed
               in-place correction); the token is no longer cited at --tip and was
               unresolved at --base. Exempts the token from `dropped` and `stale`,
               like `fixed`.
  superseded (round 55) evidence = a replacement token; the original token was cited
               in that surface at --base and resolved there (unlike `fixed`, which
               corrects an UNRESOLVED citation, `superseded` discloses a live citation
               re-pointed to a different file - e.g. the calibration row's
               "latest outside closure" pointer moved from round-52's spotcheck to
               round-53's); the token is no longer cited at --tip, and the replacement
               is cited in that surface at --tip and resolves. Exempts the token from
               `dropped` and `stale`, like `fixed`.
A row is `bad` when its class check fails, and `stale` when its token is not an
unresolved citation of its surface at --tip (for `fixed`/`externalized`/`superseded`:
when its check fails it is bad).

Legs:
  fixture  fifteen constructed scenarios in a scratch git repository (built here,
           never in the lane) each get the verdict their construction fixes: the
           round-53 eight (unresolved counted; fenced not; brace group; forged
           deleted; true deleted; forged never; anchor past EOF; stale row) plus six:
           an upstream row at a mutable ref is bad (M10); an upstream row serving
           bytes the surface does not pin is bad (M11 bytes); an upstream row at the
           pinned revision with the pinned bytes discloses (M11/M12 contrast); a
           `never` row on an upstream-inventory token is bad (M13); a `fixed`
           replacement cited away from the base line is bad (M15); an honest `fixed`
           row - replacement at the base line, extending the original stem -
           discloses; and a `superseded` row whose live base citation was re-pointed
           to a cited, resolving replacement discloses while a `superseded` row whose
           token is still cited, or whose replacement is not cited at tip, is bad.
  lane     at --tip: every unresolved citation is disclosed by a good row
           (undisclosed=0), bad=0, stale=0, and no citation any of the three surfaces
           held at --base is absent at --tip unless a `fixed`/`externalized`/
           `superseded` row names it (dropped=0 across SCORECARD.md, SHONEN.md and
           SKILL.md - J12Hide/K4Cheat a5a).
met = fixture and lane.
PREDICATE (same sentence in the preregistration): at the measured commit every
repository path that SCORECARD.md, SHONEN.md and SKILL.md cite outside fences resolves
in the lane tree or the fleet tree, or is disclosed by a correction-ledger row whose
class the counter re-derives from git history with upstream rows pinned to a full
commit, the frozen owner and the surface-stated digest, and `fixed` rows bound to the
original stem and line, and `superseded` rows disclosing a live base citation
re-pointed to a cited, resolving replacement, with no bad or stale row and no citation
dropped on any of the three surfaces since the base, and fifteen constructed scenarios
each get their fixed verdict; fixture=1 lane=1 undisclosed=0 bad=0 stale=0 dropped=0.

Output: `fixture=0|1 lane=0|1 scenarios=N/15 cited=N unresolved=N disclosed=N
undisclosed=N bad=N stale=N dropped=N met=True|False`, then `detail:` lines.
Exit 0 met, 1 not met, 2 could not evaluate (git failure or an unfetchable upstream
row). Read-only on --repo and --fleet; every git call runs with inherited GIT_*
variables stripped (Sen4Fixture); scratch under --scratch (default TMPDIR), removed on
exit.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

BASE = "0b75a84c56e024cac1662e8ff81802f249acb410"  # the round-53 tip: the drop horizon must include the round-54 re-anchor (the unrowed drop the base control catches); a same-tip base would make the do-nothing control pass (round-55 pre-freeze check)
SURFACES = ("SCORECARD.md", "SHONEN.md", "SKILL.md")
LEDGER = "registry/cited-path-corrections.tsv"
LANE_ROOTS = (".ufo/", "tools/", "tests/", "corpus/", "registry/", "plans/", "considerthese/")
FLEET_ROOTS = ("scripts/", "templates/")
TOP = ("AGENTS.md", "LOG.md", "MINT.md", "PROVINCE.md", "README.md", "SCORECARD.md",
       "SHONEN.md", "SKILL.md")
BAD_CHARS = set(" <>$=()|'\"")
ANCHOR = re.compile(r"^(.*?):(\d+(?:[-,]\d+)*)$")
CLASSES = ("deleted", "never", "moved", "eof", "untracked", "upstream", "fixed", "externalized", "superseded")
SCENARIOS = 15
# the lane's frozen upstream inventory: llama.cpp's tools/server files the lane pins.
# owner/repo and revision are frozen here; the digest is the one the citing surface
# states (full, or the truncated first/last form) - J11BadFixed/M6Ledger M10-M12.
UPSTREAM_OWNER_REPO = "ggml-org/llama.cpp"
UPSTREAM_COMMIT = "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"
UPSTREAM_INVENTORY = frozenset((
    "tools/server/server-schema.cpp", "tools/server/server-common.cpp",
    "tools/server/server-task.cpp", "tools/server/server-chat.cpp",
))
# full digests of the four pinned files at UPSTREAM_COMMIT (as SKILL.md states them);
# a fallback when a citing surface states no digest of its own
UPSTREAM_DIGESTS = {
    "tools/server/server-common.cpp": "b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442",
    "tools/server/server-schema.cpp": "1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050",
    "tools/server/server-task.cpp": "4c3f413b9b54d4cc0e7b5998e6979a2389f5ff716e20cb1510ca7745fa233495",
    "tools/server/server-chat.cpp": "91f48e09afc5a345033866380e82db1c3ad4d18baf1cec38ffa6cddaf6a6263e",
}
FULL_SHA = re.compile(r"([0-9a-f]{64})")
TRUNC_SHA = re.compile(r"([0-9a-f]{8,12})\.\.\.([0-9a-f]{4,12})|([0-9a-f]{8,12})\u2026([0-9a-f]{4,12})")


class EvalError(Exception):
    pass


class Unevaluable(EvalError):
    """A could-not-evaluate condition (network, environment), never a verdict."""


def clean_env(extra=None):
    """Environment for every git call: inherited GIT_* redirection is dropped
    (Sen4Fixture: GIT_DIR redirected the fixture into a foreign repository,
    GIT_CONFIG_COUNT reached core.hooksPath and executed an attacker hook)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(extra or {})
    return env


def git(repo, *args, check=True):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, env=clean_env())
    if check and p.returncode != 0:
        raise EvalError(f"git {' '.join(args)[:120]}: {p.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return p


def show(repo, rev, path):
    p = git(repo, "show", f"{rev}:{path}", check=False)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def tree_paths(repo, rev):
    out = git(repo, "ls-tree", "-r", "--name-only", "-z", rev).stdout.decode("utf-8", "replace")
    return set(p for p in out.split("\0") if p)


def history_paths(repo, *tips):
    """Paths touched by commits reachable from the given tips (K4Cheat X: scoped to
    BASE..tip, so a clone's unrelated fixture branches cannot flip `never` rows or
    retarget `moved`'s last commit); `--all` only when a tip is absent (the counter's
    own scratch fixtures do not contain BASE)."""
    have = tips and all(git(repo, "cat-file", "-e", f"{t}^{{commit}}", check=False).returncode == 0
                        for t in tips)
    revs = tips if have else ("--all",)
    out = git(repo, "log", *revs, "--name-only", "--format=", "-z").stdout.decode("utf-8", "replace")
    return set(p.strip("\n") for p in out.split("\0") if p.strip("\n"))


def prose_paths(text):
    """[(line_no, token)] of lane/fleet-root path tokens NOT inside backticks (K4Cheat
    a2: advisory only - prose evidence claims surface in the receipt without gating)."""
    out = []
    plain = re.sub(r"`[^`\n]+`", "", text)
    plain = "\n".join(l for l in plain.split("\n") if not l.strip().startswith("```"))
    for n, line in enumerate(plain.split("\n"), 1):
        for tok in re.findall(r"(?:[\w.-]+/)+[\w.…-]+", line):
            if any(c in tok for c in BAD_CHARS):
                continue
            if tok.startswith(LANE_ROOTS) or tok.startswith(FLEET_ROOTS) or tok in TOP:
                out.append((n, tok))
    return out


def stated_digests(text):
    """{token: ('full', hex) | ('trunc', first, last)} of the digests a surface states
    for its upstream tokens: the token on a line, a full 64-hex or a truncated
    first…last form on the same line (J11BadFixed: pin digests at fixed revisions)."""
    out = {}
    for n, line in enumerate(text.split("\n"), 1):
        for _m, tok, _c, _l, _h in citations_line(line):
            full = FULL_SHA.search(line)
            if full:
                out[tok] = ("full", full.group(1))
                continue
            trunc = TRUNC_SHA.search(line)
            if trunc:
                first = trunc.group(1) or trunc.group(3)
                last = trunc.group(2) or trunc.group(4)
                out.setdefault(tok, ("trunc", first, last))
    return out


def citations_line(line):
    """citations() for one line (no fence state)."""
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
        yield 0, tok, core, lo, hi


def citation_lines(text):
    """{token: set(line_no)} of a surface's citations."""
    out = {}
    for n, tok, _c, _l, _h in citations(text):
        out.setdefault(tok, set()).add(n)
    return out


def fetch(url):
    opener = urllib.request.build_opener()
    with opener.open(urllib.request.Request(url, method="GET"), timeout=60) as r:
        if r.status != 200:
            raise OSError(f"HTTP {r.status}")
        return r.read()


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
            self._hist = history_paths(self.path, BASE, self.rev)
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


def check_row(row, bad_exp, lane, fleet, cited_tip, base_unres, base_citelines=None, digest_of=None,
              base_rows=None):
    """None when the row's class re-derives; else the reason it is bad. Raises
    Unevaluable when an upstream row cannot be fetched (V5Review: could-not-evaluate,
    never a verdict). base_rows: (surface, token) pairs the BASE ledger already held -
    an append-only ledger's inherited rows were verified when introduced."""
    cls, ev, tok = row["class"], row["evidence"], row["token"]
    if cls not in CLASSES:
        return f"unknown class {cls!r}"
    if cls == "fixed":
        surf = row["surface"]
        inherited = base_rows is not None and (surf, tok) in base_rows
        if tok in cited_tip.get(surf, {}):
            return "fixed token is still cited at tip"
        rep = cited_tip.get(surf, {}).get(ev)
        if rep is None:
            return f"replacement {ev!r} is not cited in {surf} at tip"
        if any(v != "ok" for _e, v in rep):
            return f"replacement {ev!r} does not resolve at tip"
        stem = re.split(r"[{…]", tok)[0]
        if stem and not ev.startswith(stem):
            return f"replacement {ev!r} does not extend the original token's stem {stem!r}"
        if not inherited:
            # a fixed row introduced at this tip must name a citation that was live at
            # base; an inherited row (the ledger is append-only) was verified when it
            # was introduced and its token may predate the frozen base
            if tok not in base_unres.get(surf, set()):
                return "fixed token was not an unresolved citation of this surface at base"
            lines = (base_citelines or {}).get(surf, {}).get(tok, set())
            if len(lines) != 1:
                return "fixed token needs exactly one base citation line"
            ln = next(iter(lines))
            tip_text = show(lane.path, lane.rev, surf) or ""
            tip_lines = tip_text.split("\n")
            cited = False
            if ln <= len(tip_lines):
                for _n2, t2, _c2, _l2, _h2 in citations_line(tip_lines[ln - 1]):
                    if t2 == ev or ev in t2 or t2 in ev:
                        cited = True
            if not cited:
                return f"replacement {ev!r} is not cited at the base citation line {ln}"
        return None
    if cls == "externalized":
        # the token is no longer cited and no longer resolves; the evidence text - the
        # in-place replacement - appears verbatim in the surface at tip and is not
        # itself a citation. The class exists for corrections made before the frozen
        # base (J12Hide's unrowed in-place correction); fabricating a replacement text
        # is visible, not invisible hiding.
        surf = row["surface"]
        if tok in cited_tip.get(surf, {}):
            return "externalized token is still cited at tip"
        if any(v == "ok" for _e, v in cited_tip.get(surf, {}).get(tok, [])):
            return "externalized token resolves at tip"
        tip_text = show(lane.path, lane.rev, surf) or ""
        if ev not in tip_text:
            return f"externalization {ev!r} does not appear in {surf} at tip"
        if any(t2 == ev or ev in t2 for _n, t2, _c, _l, _h in citations(tip_text)):
            return f"externalization {ev!r} is itself cited at tip"
        return None
    if cls == "superseded":
        # a live citation at base re-pointed to a different file (round 55: the
        # calibration row's "latest outside closure" pointer moved from round-52's
        # spotcheck to round-53's in round 54, and the round-54 class vocabulary had
        # no row for it - the base control's dropped=1 demonstrated the gap). The
        # token is no longer cited at tip, it WAS cited at base (unlike `fixed`,
        # whose token was unresolved at base), and the replacement token is cited
        # in that surface at tip and resolves.
        surf = row["surface"]
        rep = cited_tip.get(surf, {}).get(ev)
        if rep is None:
            return f"replacement {ev!r} is not cited in {surf} at tip"
        if any(v != "ok" for _e, v in rep):
            return f"replacement {ev!r} does not resolve at tip"
        if base_citelines is not None and tok not in (base_citelines.get(surf) or {}):
            return "superseded token was not cited in this surface at the base"
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
        if tok in UPSTREAM_INVENTORY or any(e in UPSTREAM_INVENTORY for e, _v in bad_exp):
            return "token is in the lane's frozen upstream inventory; its provenance is upstream, not never"
        for e, _v in bad_exp:
            if matches(e, lane.hist()) or (fleet is not None and matches(e, fleet.hist())):
                return f"{e} was a path in some commit"
        return None
    if cls == "moved":
        if len(bad_exp) != 1 or any(c in bad_exp[0][0] for c in "*?[") or not matches(ev, lane.tree) or ev not in lane.tree:
            return "moved needs one plain token and a replacement file in the tip tree"
        e = bad_exp[0][0]
        last = git(lane.path, "log", BASE, lane.rev, "-1", "--format=%H", "--", e).stdout.decode().strip()
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
        # evidence is a pinned raw URL; round 54 pins it at a fixed revision and digest
        # (J11BadFixed F1, M6Ledger M10-M12, V5Review)
        if len(bad_exp) != 1 or any(c in bad_exp[0][0] for c in "*?["):
            return "upstream needs one plain token"
        e = bad_exp[0][0]
        m = re.fullmatch(r"https://raw\.githubusercontent\.com/([\w.-]+)/([\w.-]+)/([\w.-]+)/(\S+)", ev)
        if not m:
            return "upstream needs a pinned raw.githubusercontent.com URL"
        owner_repo, ref, rest = f"{m.group(1)}/{m.group(2)}", m.group(3), m.group(4)
        if rest != e and not rest.endswith("/" + e):
            return f"upstream URL does not end in the token {e}"
        if not re.fullmatch(r"[0-9a-f]{40}", ref):
            return f"upstream URL is at {ref!r}, not a full 40-hex commit (tags, branches and forks fail)"
        if e in UPSTREAM_INVENTORY:
            if owner_repo != UPSTREAM_OWNER_REPO:
                return f"upstream owner/repo {owner_repo} is not the pinned {UPSTREAM_OWNER_REPO}"
            if ref != UPSTREAM_COMMIT:
                return f"upstream URL is at {ref[:12]}, not the pinned revision {UPSTREAM_COMMIT[:12]}"
        try:
            body = fetch(ev)
        except (OSError, ValueError) as exc:
            raise Unevaluable(f"upstream evidence {ev} unfetchable: {exc}")
        digest = hashlib.sha256(body).hexdigest()
        stated = (digest_of or {}).get(row["surface"], {}).get(e)
        pin = UPSTREAM_DIGESTS.get(e)
        if stated and stated[0] == "full":
            if pin and stated[1] != pin:
                return f"surface states digest {stated[1][:12]}..., contradicting the frozen pin {pin[:12]}..."
            expected = ("full", stated[1])
        elif stated and stated[0] == "trunc":
            expected = stated
        elif pin:
            expected = ("full", pin)
        else:
            expected = None
        if expected is not None:
            if expected[0] == "full":
                if digest != expected[1]:
                    return f"upstream serves sha256 {digest[:12]}..., not the pinned {expected[1][:12]}..."
            else:
                if not (digest.startswith(expected[1]) and digest.endswith(expected[2])):
                    return f"upstream serves sha256 {digest[:12]}..., not the pinned {expected[1]}...{expected[2]}"
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


def survey(lane, fleet, base_unres=None, detail=None):
    """Counts and per-item detail for one lane revision. With detail (a list), also
    appends advisory lines for prose-shaped root tokens that resolve nowhere (K4Cheat
    a2)."""
    cited, unres = {}, {}
    for surf in SURFACES:
        text = show(lane.path, lane.rev, surf)
        cited[surf] = {}
        unres[surf] = {}
        if text is None:
            continue
        if detail is not None:
            for n, tok in prose_paths(text):
                core = tok.split("#", 1)[0]
                if not matches(core, lane.tree) and not (fleet is not None and matches(core, fleet.tree)):
                    detail.append(f"advisory: {surf}:{n} prose-cites missing path {tok}")
        for _n, tok, core, lo, hi in citations(text):
            r = resolve(core, lo, hi, lane, fleet)
            cited[surf].setdefault(tok, r)
            bad = [(e, v) for e, v in r if v != "ok"]
            if bad:
                unres[surf].setdefault(tok, bad)
    return cited, unres


def evaluate(lane, fleet, base_lane, detail, verbose=True):
    cited, unres = survey(lane, fleet, detail=detail)
    _bc, bunres = survey(base_lane, fleet) if base_lane is not None else ({}, {})
    base_unres = {s: set(v) for s, v in bunres.items()}
    base_citelines = {}
    if base_lane is not None:
        for surf in SURFACES:
            bt = show(base_lane.path, base_lane.rev, surf)
            if bt is not None:
                base_citelines[surf] = citation_lines(bt)
    digest_of = {}
    for surf in SURFACES:
        text = show(lane.path, lane.rev, surf)
        if text is not None:
            digest_of[surf] = stated_digests(text)
    base_rows = set()
    if base_lane is not None:
        base_rows = {(r["surface"], r["token"]) for r in read_ledger(base_lane)}
    rows = read_ledger(lane)
    disclosed, bad, stale = set(), [], []
    for row in rows:
        key = (row["surface"], row["token"])
        if row["surface"] not in SURFACES:
            bad.append((row, "unknown surface"))
            continue
        exp = unres.get(row["surface"], {}).get(row["token"])
        why = check_row(row, exp, lane, fleet, cited, base_unres, base_citelines, digest_of, base_rows)
        if row["class"] not in ("fixed", "externalized", "superseded") and not exp and why is None:
            stale.append(row)
        elif why is not None:
            bad.append((row, why))
        elif row["class"] not in ("fixed", "externalized", "superseded"):
            disclosed.add(key)
    n_cited = sum(len(v) for v in cited.values())
    n_unres = sum(len(v) for v in unres.values())
    undisclosed = [(s, t, v) for s, d in unres.items() for t, v in d.items() if (s, t) not in disclosed]
    exempt = {(row["surface"], row["token"]) for row in rows
              if row["class"] in ("fixed", "externalized", "superseded")}
    dropped = []
    if base_lane is not None:
        for surf in SURFACES:
            bt = show(base_lane.path, base_lane.rev, surf) or ""
            tt = show(lane.path, lane.rev, surf) or ""
            bset = {tok for _n, tok, *_r in citations(bt)} - {t for s, t in exempt if s == surf}
            tset = {tok for _n, tok, *_r in citations(tt)}
            for t in sorted(bset - tset):
                dropped.append(f"{surf}: {t}")
    if verbose:
        for s, t, v in undisclosed:
            detail.append(f"undisclosed {s} `{t}`: {v}")
        for row, why in bad:
            detail.append(f"bad ledger line {row['line']} ({row['surface']} `{row['token']}` {row['class']}): {why}")
        for row in stale:
            detail.append(f"stale ledger line {row['line']} ({row['surface']} `{row['token']}`): token resolves or is not cited")
        for t in dropped:
            detail.append(f"dropped citation `{t}` (cited at base, not at tip)")
    counts = {"cited": n_cited, "unresolved": n_unres, "disclosed": len(disclosed),
              "undisclosed": len(undisclosed), "bad": len(bad), "stale": len(stale), "dropped": len(dropped)}
    ok = not undisclosed and not bad and not stale and not dropped
    return ok, counts


# ------------------------------------------------------------- fixture
def fixture(S, detail):
    """Fifteen scenarios on a scratch repository; returns the number that get their
    verdict. The scratch git calls run with inherited GIT_* variables stripped
    (Sen4Fixture) and the fixture git dir is verified, not just its worktree."""
    D = tempfile.mkdtemp(prefix="r54c2-fx-", dir=S)
    env = clean_env({"GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@invalid",
                     "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@invalid",
                     "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"})
    got = 0
    try:
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
        if os.path.realpath(g("rev-parse", "--show-toplevel")) != os.path.realpath(D) \
                or os.path.realpath(g("rev-parse", "--absolute-git-dir")) != os.path.realpath(os.path.join(D, ".git")):
            raise EvalError("fixture repository is not the scratch directory")
        w("tools/a.py", "a\n")
        w("tools/gone.py", "g\n")
        w("tools/deep/ok.py", "ok\n")
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

        PIN = UPSTREAM_COMMIT
        URL = f"https://raw.githubusercontent.com/ggml-org/llama.cpp/{PIN}/tools/server/server-chat.cpp"
        CHAT = UPSTREAM_DIGESTS["tools/server/server-chat.cpp"]
        SCHEMA = UPSTREAM_DIGESTS["tools/server/server-schema.cpp"]
        up_line = (f"fields are declared in `tools/server/server-chat.cpp` (pinned SHA-256 `{CHAT}`).\n")
        up_line_bad = (f"fields are declared in `tools/server/server-chat.cpp` (pinned SHA-256 `{SCHEMA}`).\n")
        got = 0
        cases = [
            ("unresolved path is counted", "see `tools/nope.py`\n", None, None,
             lambda ok, c: not ok and c["undisclosed"] == 1),
            ("fenced path is not cited", "```\n`tools/nope.py`\n```\n", None, None,
             lambda ok, c: ok and c["cited"] == 0),
            ("brace group with one dead member", "`tools/{a,nope}.py`\n", None, None,
             lambda ok, c: not ok and c["undisclosed"] == 1),
            ("forged deleted row is bad", "`tools/nope.py`\n", f"SCORECARD.md\ttools/nope.py\tdeleted\t{cdel}\t\n",
             None, lambda ok, c: not ok and c["bad"] == 1),
            ("true deleted row discloses", "`tools/gone.py`\n", f"SCORECARD.md\ttools/gone.py\tdeleted\t{cdel}\t\n",
             None, lambda ok, c: ok and c["disclosed"] == 1),
            ("forged never row is bad", "`tools/gone.py`\n", "SCORECARD.md\ttools/gone.py\tnever\t-\t\n",
             None, lambda ok, c: not ok and c["bad"] == 1),
            ("line anchor past EOF is counted", "`corpus/x.md:9`\n", None, None,
             lambda ok, c: not ok and c["undisclosed"] == 1),
            ("row for a resolving token is stale", "`tools/a.py`\n", "SCORECARD.md\ttools/a.py\tnever\t-\t\n",
             None, lambda ok, c: not ok and c["stale"] == 1),
            # the five that kill the round-53 survivors (M6Ledger M10-M13, M15)
            ("upstream at a mutable ref is bad (M10)", up_line,
             "SCORECARD.md\ttools/server/server-chat.cpp\tupstream\t"
             "https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/server/server-chat.cpp\t\n",
             None, lambda ok, c: not ok and c["bad"] == 1),
            ("upstream serving unpinned bytes is bad (M11)", up_line_bad,
             f"SCORECARD.md\ttools/server/server-chat.cpp\tupstream\t{URL}\t\n",
             None, lambda ok, c: not ok and c["bad"] == 1),
            ("upstream at the pinned revision with pinned bytes discloses (M12 contrast)",
             up_line, f"SCORECARD.md\ttools/server/server-chat.cpp\tupstream\t{URL}\t\n",
             None, lambda ok, c: ok and c["disclosed"] == 1),
            ("never row on an upstream-inventory token is bad (M13)",
             "fields are declared in `tools/server/server-task.cpp` upstream.\n",
             "SCORECARD.md\ttools/server/server-task.cpp\tnever\t-\t\n",
             None, lambda ok, c: not ok and c["bad"] == 1),
            ("fixed replacement cited away from the base line is bad (M15)",
             "one\ntwo\nthree\nfour\nfive\nsix `tools/deep/ok.py`\n",
             "SCORECARD.md\ttools/deep/…\tfixed\ttools/deep/ok.py\t\n",
             "m15", lambda ok, c: not ok and c["bad"] == 1),
            ("fixed replacement at the base line with the original stem discloses",
             "one\ntwo `tools/deep/ok.py`\n",
             "SCORECARD.md\ttools/deep/…\tfixed\ttools/deep/ok.py\t\n",
             "fixed-honest", lambda ok, c: ok and c["bad"] == 0 and c["undisclosed"] == 0 and c["stale"] == 0),
            # round 55: a live base citation re-pointed to a different file
            ("superseded re-pointed citation discloses, forged superseded is bad",
             None, None, "superseded", lambda ok, c: ok),
        ]
        for name, scard, ledger, shape, want in cases:
            sub = []
            if shape == "superseded":
                # base cites a live token (it resolves); the honest tip re-points the
                # citation to a different resolving file and rows it superseded (met,
                # no drop); the forged tip re-points in prose with the same row (the
                # replacement is never cited at tip -> bad, no met)
                w("tools/live.py", "live\n")
                w("tools/new.py", "new\n")
                w("SCORECARD.md", "closure `tools/live.py`\n")
                if os.path.exists(os.path.join(D, LEDGER)):
                    os.unlink(os.path.join(D, LEDGER))
                scen_base = Repo(D, commit("superseded base"))
                lane = at("closure now `tools/new.py`\n",
                          "SCORECARD.md\ttools/live.py\tsuperseded\ttools/new.py\t\n")
                ok, c = evaluate(lane, None, scen_base, sub, verbose=False)
                lane2 = at("closure re-pointed away in prose\n",
                           "SCORECARD.md\ttools/live.py\tsuperseded\ttools/new.py\t\n")
                ok2, c2 = evaluate(lane2, None, scen_base, sub, verbose=False)
                hit = bool(want(ok, c)) and ok and c["dropped"] == 0 and c["bad"] == 0 \
                    and (not ok2) and c2["bad"] == 1
            elif shape in ("m15", "fixed-honest"):
                # base cites the ellipsis token at line 2; the m15 tip cites the
                # replacement at line 6 (away from the base line -> bad), the honest tip
                # at line 2 (the in-place correction -> discloses)
                w("SCORECARD.md", "one\ntwo `tools/deep/…`\n")
                if os.path.exists(os.path.join(D, LEDGER)):
                    os.unlink(os.path.join(D, LEDGER))
                scen_base = Repo(D, commit(f"{shape} base"))
                lane = at(scard, ledger)
                ok, c = evaluate(lane, None, scen_base, sub, verbose=False)
            else:
                lane = at(scard, ledger)
                ok, c = evaluate(lane, None, None, sub, verbose=False)
            hit = bool(want(ok, c))
            got += hit
            detail.append(f"fixture {'ok' if hit else 'FAIL'}: {name} (met={ok} {c})")
    finally:
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
