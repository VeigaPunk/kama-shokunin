#!/usr/bin/env python3
"""round50-append-audit-v5-check.py - kama round-50 C2 (calibration) counter.

Question: does the lane's append-only audit grade the lane's declared rule the same
way whatever order git lists sibling commits in, whatever a fenced code block says,
and whatever line ending a moved line carries - and does it account for every
deleted line it reports?
Routed (corpus/lessons/round-49-verifier-spotcheck.md R3; SCORECARD.md §Planned
(round 50) item 1):
  K2Origin   v4 origin is the first blob in `git rev-list --topo-order --reverse`
             that holds the text, so sibling order can flip a verdict (F3); a `## `
             line inside a fenced code block re-titles the dated lines after it (F4);
             origin keys are byte-exact, so a line moved with a changed line ending
             has no origin of its own (F5);
  K2Cheat    the round-49 lane leg only upper-bounded the tool's self-reported
             `ungraded`; a tool whose graded + ungraded != deleted met it;
  V2Ctr      the round-49 binder copies the tool's rule (still true here: limit).

v5 definitions (the build must implement them; this counter checks them on its own
fixtures, whose expectations are written by construction, and on the lane):
  key(l)     the line bytes with one trailing carriage return removed
  fence      CommonMark 0.31.2 §4.5: a line of up to three spaces of indentation and at
             least three backticks or tildes opens a fenced block (a backtick fence's
             info string holds no backtick); the block closes at a line of up to three
             spaces, the same character at least as many times, and only spaces or
             tabs after; an unclosed fence runs to the end of the file
  section    the title of the last `## ` line at or before the line that is not inside
             (or itself) a fence line; None before the first such heading; titles and
             fence tests read the line with the trailing CR and blanks stripped
  birth      a commit c whose blob of the file holds key k while no parent of c holds k
             (a root commit: every key it holds)
  origin(l)  the union, over every birth of key(l) among the commits reachable from
             <to>, of the section titles holding key(l) in that commit's blob - a
             property of the commit graph and its blobs, not of any listing order
  ungraded   a deleted line is ungraded only when its parent section is an eligible
             exempt title (v3, sections fence-aware) and origin(l) contains one of the
             file's exempt titles (v4, origin as above)
Unchanged from v4: binding, threshold, restoration measures, JSON shape (`"schema":
"append-only-audit/v3"`).

Fixture scenarios (each a fresh repo under --scratch; contract outside the repo).
v4 scenarios, kept as written in round 49 (the closed hatches must stay closed):
  launder, native-head, dated-loss, substring, word-token, negated, wildcard-self,
  wildcard-named (see tools/round49-append-audit-v4-check.py)
v5 scenarios:
  order-a / order-b  from one base, branch A adds `twin line` at the end of `## Axes`,
                 branch B adds it at the end of `## Round 1`; the merge holds it in both;
                 the event then rewrites `## Axes` (24 head lines and the twin deleted,
                 30 new ones added). order-a merges B into A, order-b merges A into B
                 (same trees, parents swapped). The twin was born under `## Axes` on
                 branch A, so in BOTH: expect the event deleted=25 graded=0 ungraded=25
                 status=ungraded and exit 0
  fence          `## Round 1` holds a fenced block whose content is a `## Axes` line,
                 then 25 dated lines; the event deletes those 25 while `## Axes` regrows:
                 expect the event deleted=25 graded=25 ungraded=0 status=unrestored,
                 exit 1 (v4: ungraded under the fake title, exit 0)
  crlf-launder   25 dated LF lines are moved under `## Axes` as CRLF lines (that move is
                 itself an unrestored event), then deleted there while `## Axes` regrows:
                 expect the last event deleted=25 graded=25 ungraded=0 status=unrestored
                 and exit 1 (v4: ungraded, the CRLF bytes having been born in `## Axes`)
Every scenario also requires graded + ungraded == deleted for every event.
Legs:
  fixture  every scenario's expectation holds for the tool at --tip
           (tools/append-only-audit.py from `git archive`)
  lane     the tool at --tip on --repo (contract from --tip) exits 0 with
           bad_declarations 0 and >= 5 events; this counter's own binder (the v4
           rule) binds every --tip contract row; for every event the tool reports,
           graded + ungraded == deleted and deleted equals `git diff --numstat`'s
           deletion count for that file at that commit; and its `ungraded` count is at
           most this counter's own count, under the v5 definitions above, of the
           event's deleted lines whose parent section is an exempt title of the file
           and whose origin contains an exempt title
met = fixture and lane.
PREDICATE (same sentence in the preregistration): append-only-audit at the measured
commit gives the same verdict under either merge-parent order, grades dated lines
behind a fenced fake heading and dated lines laundered through the head with a changed
line ending, keeps every round-49 scenario, accounts for every deleted line of every
event, and on the lane binds every contract row, exits 0 and ungrades no deleted line
the v5 definitions grade; fixture=1 lane=1.

Output: `fixture=0|1 lane=0|1 scenarios=N/12 met=True|False`, then `detail:` lines.
Exit 0 met, 1 not met, 2 could not evaluate. Read-only on --repo; fixtures and the
tip tree live under --scratch and are removed on exit.
"""
from __future__ import annotations

import argparse
import collections
import fnmatch
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

TOOL = "tools/append-only-audit.py"
IDENT = ["-c", "user.name=r50c2-fixture", "-c", "user.email=r50c2-fixture@invalid", "-c", "commit.gpgsign=false"]
NSCEN = 12
FENCE_OPEN = re.compile(rb"^ {0,3}(`{3,}|~{3,})(.*)$")
HEADER = "path\trule\tdeclared_at\tregion\tnote"
NEG3 = ("not append-only", "not append only", "no longer append", "never append-only")
NEGW = re.compile(r"(?:\b(?:not|never|no|nor|neither|non|isn't|aren't)\b|\bno longer\b)"
                  r"(?:[\s\-]+[\w'’]+){0,3}?[\s\-]+append[- ]only")


class EvalError(Exception):
    pass


def git(repo, *args, inp=None, ok=(0,)):
    p = subprocess.run(["git", "-C", repo, *args], input=inp, capture_output=True)
    if p.returncode not in ok:
        raise EvalError(f"git {' '.join(args)[:120]}: {p.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return p.stdout


# ------------------------------------------------------------- own v4 binder
def token(pattern):
    parts = pattern.split("/")
    base = parts[-1]
    if any(ch in base for ch in "*?["):
        return parts[-2] if len(parts) > 1 else ""
    return base.rsplit(".", 1)[0] if "." in base else base


def says(low):
    return ("append-only" in low or "append only" in low) and not any(n in low for n in NEG3) \
        and not NEGW.search(low)


def binds(text, pattern, decl_path):
    if text is None:
        return False
    low = text.lower()
    if not says(low):
        return False
    tok = token(pattern).lower()
    wild = any(ch in pattern for ch in "*?[")
    if not wild and fnmatch.fnmatchcase(decl_path, pattern):
        return True
    return bool(tok) and re.search(r"(?<![a-z0-9_])" + re.escape(tok) + r"(?![a-z0-9_])", low) is not None


# ------------------------------------------------------------- fixtures
class Fx:
    def __init__(self, root, name):
        self.d = os.path.join(root, name)
        os.makedirs(self.d)
        git(self.d, "init", "-q")
        top = git(self.d, "rev-parse", "--show-toplevel").decode().strip()
        if os.path.realpath(top) != os.path.realpath(self.d):
            raise EvalError(f"fixture {name}: toplevel {top} is not {self.d}")
        self.n = 0
        self.files = {}

    def commit(self, files, parents=None):
        """Commit the tracked set (earlier files plus `files`; bytes kept raw, lists joined
        with LF) on `parents` (default: HEAD, none for the first) and move HEAD there."""
        self.files.update(files)
        for name in os.listdir(self.d):
            if name != ".git":
                p = os.path.join(self.d, name)
                shutil.rmtree(p) if os.path.isdir(p) else os.unlink(p)
        for name, body in self.files.items():
            p = os.path.join(self.d, name)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as fh:
                fh.write(body if isinstance(body, bytes) else "".join(x + "\n" for x in body).encode())
        git(self.d, "add", "-A")
        tree = git(self.d, "write-tree").decode().strip()
        if parents is None:
            head = git(self.d, "rev-parse", "-q", "--verify", "HEAD^{commit}", ok=(0, 1)).decode().strip()
            parents = [head] if head else []
        self.n += 1
        argv = ["commit-tree", tree, "-m", f"c{self.n}"]
        for q in parents:
            argv += ["-p", q]
        c = git(self.d, *IDENT, *argv).decode().strip()
        git(self.d, "update-ref", "HEAD", c)
        return c


def L(tag, n):
    return [f"{tag} line {i} r50" for i in range(n)]


def run_tool(tree, repo, contract_text, S, name):
    cpath = os.path.join(S, f"{name}.contract.tsv")
    with open(cpath, "w") as fh:
        fh.write(contract_text)
    p = subprocess.run([sys.executable, os.path.join(tree, TOOL), "--repo", repo, "--to", "HEAD",
                        "--contract", cpath, "--json"], capture_output=True, text=True, timeout=300)
    try:
        j = json.loads(p.stdout)
    except ValueError:
        j = None
    return p.returncode, j


def scenarios(tree, S, detail):
    NOTES_EX = ["SCORE.md is append-only", "the ## Axes head of SCORE.md is re-derived in place"]
    ex_row = HEADER + "\nSCORE.md\tA-corr\tNOTES.md:1\texempt=## Axes@NOTES.md:2\tfixture\n"
    results = []

    def check(name, code, j, want_exit, ev=None, bad=None):
        ok = code == want_exit and isinstance(j, dict)
        why = f"exit {code} (want {want_exit})"
        if isinstance(j, dict):
            off = [str(e.get("commit"))[:8] for e in j.get("events") or []
                   if e.get("graded", 0) + e.get("ungraded", 0) != e.get("deleted")]
            if off:
                ok = False
                why += f" graded+ungraded!=deleted at {off}"
        if ok and ev is not None:
            commit, want = ev
            got = [e for e in j.get("events", []) if e.get("commit") == commit]
            ok = len(got) == 1 and all(got[0].get(k) == v for k, v in want.items())
            why += f" event {({k: got[0].get(k) for k in want} if got else None)} want {want}"
        if ok and bad is not None:
            got = (j.get("summary") or {}).get("bad_declarations")
            ok = got == bad
            why += f" bad_declarations {got} want {bad}"
        results.append(ok)
        detail.append(f"scenario {name}: {'ok' if ok else 'FAIL'} {why}")

    # launder
    f = Fx(S, "launder")
    head, dated = L("head", 5), L("dated", 25)
    f.commit({"NOTES.md": NOTES_EX, "SCORE.md": ["# s", "## Axes"] + head + ["## Round 1"] + dated})
    f.commit({"SCORE.md": ["# s", "## Axes"] + head + dated + ["## Round 1", "round one kept"]})
    c3 = f.commit({"SCORE.md": ["# s", "## Axes"] + head + L("regrow", 30) + ["## Round 1", "round one kept"]})
    code, j = run_tool(tree, f.d, ex_row, S, "launder")
    check("launder", code, j, 1, (c3, {"deleted": 25, "graded": 25, "ungraded": 0, "status": "unrestored"}))
    # native-head
    f = Fx(S, "native-head")
    f.commit({"NOTES.md": NOTES_EX, "SCORE.md": ["# s", "## Axes"] + L("old", 25) + ["## Round 1"] + L("r", 3)})
    c2 = f.commit({"SCORE.md": ["# s", "## Axes"] + L("new", 25) + ["## Round 1"] + L("r", 3)})
    code, j = run_tool(tree, f.d, ex_row, S, "native-head")
    check("native-head", code, j, 0, (c2, {"deleted": 25, "graded": 0, "ungraded": 25, "status": "ungraded"}))
    # dated-loss
    f = Fx(S, "dated-loss")
    f.commit({"NOTES.md": NOTES_EX, "SCORE.md": ["# s", "## Axes"] + L("h", 3) + ["## Round 1"] + L("d", 30)})
    c2 = f.commit({"SCORE.md": ["# s", "## Axes"] + L("h", 3) + ["## Round 1"] + L("d", 30)[25:]})
    code, j = run_tool(tree, f.d, ex_row, S, "dated-loss")
    check("dated-loss", code, j, 1, (c2, {"deleted": 25, "graded": 25, "status": "unrestored"}))
    # binding scenarios: no deletions, only declarations
    for name, files, row, want_exit, bad in (
            ("substring", {"NOTES.md": ["the catalog is append-only"], "LOG.md": L("l", 3)},
             "LOG.md\tA\tNOTES.md:1\t*\tfixture", 1, 1),
            ("word-token", {"NOTES.md": ["LOG.md is append-only"], "LOG.md": L("l", 3)},
             "LOG.md\tA\tNOTES.md:1\t*\tfixture", 0, 0),
            ("negated", {"NOTES.md": ["SCORE.md is not strictly append-only"], "SCORE.md": L("s", 3)},
             "SCORE.md\tA\tNOTES.md:1\t*\tfixture", 1, 1),
            ("wildcard-self", {"notes/a.md": ["this file is append-only"], "notes/b.md": L("b", 3)},
             "notes/*.md\tA-corr\tnotes/a.md:1\t*\tfixture", 1, 1),
            ("wildcard-named", {"README.md": ["files under notes/ are append-only"], "notes/b.md": L("b", 3)},
             "notes/*.md\tA-corr\tREADME.md:1\t*\tfixture", 0, 0)):
        f = Fx(S, name)
        f.commit(files)
        code, j = run_tool(tree, f.d, HEADER + "\n" + row + "\n", S, name)
        check(name, code, j, want_exit, None, bad)
    # ---- v5 scenarios
    head24 = L("hd", 24)
    base_score = ["# s", "## Axes"] + head24 + ["## Round 1"] + L("r", 3)
    for name, swap in (("order-a", False), ("order-b", True)):
        f = Fx(S, name)
        c1 = f.commit({"NOTES.md": NOTES_EX, "SCORE.md": base_score})
        ca = f.commit({"SCORE.md": ["# s", "## Axes"] + head24 + ["twin line", "## Round 1"] + L("r", 3)}, [c1])
        cb = f.commit({"SCORE.md": ["# s", "## Axes"] + head24 + ["## Round 1"] + L("r", 3) + ["twin line"]}, [c1])
        both = ["# s", "## Axes"] + head24 + ["twin line", "## Round 1"] + L("r", 3) + ["twin line"]
        cm = f.commit({"SCORE.md": both}, [cb, ca] if swap else [ca, cb])
        ce = f.commit({"SCORE.md": ["# s", "## Axes"] + L("nh", 30) + ["## Round 1"] + L("r", 3) + ["twin line"]},
                      [cm])
        code, j = run_tool(tree, f.d, ex_row, S, name)
        check(name, code, j, 0, (ce, {"deleted": 25, "graded": 0, "ungraded": 25, "status": "ungraded"}))
    # fence
    f = Fx(S, "fence")
    dated = L("fd", 25)
    f.commit({"NOTES.md": NOTES_EX, "SCORE.md": ["# s", "## Axes"] + L("h", 3) + ["## Round 1", "kept one",
                                                 "```text", "## Axes", "```"] + dated})
    c2 = f.commit({"SCORE.md": ["# s", "## Axes"] + L("h", 3) + L("grow", 30) + ["## Round 1", "kept one",
                                                 "```text", "## Axes", "```"]})
    code, j = run_tool(tree, f.d, ex_row, S, "fence")
    check("fence", code, j, 1, (c2, {"deleted": 25, "graded": 25, "ungraded": 0, "status": "unrestored"}))
    # crlf-launder
    f = Fx(S, "crlf-launder")
    head5, dated = L("head", 5), L("cd", 25)

    def raw(lines_):
        return b"".join(x if isinstance(x, bytes) else (x + "\n").encode() for x in lines_)
    f.commit({"NOTES.md": NOTES_EX, "SCORE.md": raw(["# s", "## Axes"] + head5 + ["## Round 1"] + dated)})
    f.commit({"SCORE.md": raw(["# s", "## Axes"] + head5 + [(x + "\r\n").encode() for x in dated]
                              + ["## Round 1", "round one kept"])})
    c3 = f.commit({"SCORE.md": raw(["# s", "## Axes"] + head5 + L("regrow", 30) + ["## Round 1", "round one kept"])})
    code, j = run_tool(tree, f.d, ex_row, S, "crlf-launder")
    check("crlf-launder", code, j, 1, (c3, {"deleted": 25, "graded": 25, "ungraded": 0, "status": "unrestored"}))
    return results


# ------------------------------------------------------------- lane leg
def fence_open(ln):
    """(char, length) when ln opens a CommonMark fenced block, else None."""
    m = FENCE_OPEN.match(ln)
    if not m:
        return None
    run = m.group(1)
    if run[:1] == b"`" and b"`" in m.group(2):
        return None
    return run[:1], len(run)


def fence_close(ln, fence):
    ch, n = fence
    s = ln.lstrip(b" ")
    if len(ln) - len(s) > 3:
        return False
    k = len(s) - len(s.lstrip(ch))
    return k >= n and s[k:].strip(b" \t") == b""


def sections(lines):
    """v5: the `## ` title owning each line, headings inside fenced blocks ignored."""
    out, t, fence = [], None, None
    for ln in lines:
        b = ln.rstrip(b"\r")
        if fence is not None:
            if fence_close(b, fence):
                fence = None
        else:
            fo = fence_open(b)
            if fo is not None:
                fence = fo
            elif b.startswith(b"## "):
                t = b.decode("utf-8", "replace").rstrip()
        out.append(t)
    return out


def key(ln):
    return ln


def split_lines(data):
    s = data.split(b"\n")
    if s and s[-1] == b"":
        s.pop()
    return s


def parse_contract(text):
    rows = []
    for ln in text.split("\n")[1:]:
        if ln.strip():
            c = ln.split("\t")
            if len(c) != 5:
                raise EvalError(f"contract row with {len(c)} cells")
            rows.append([x.strip() for x in c])
    return rows


def deleted_with_pos(repo, parent, commit, path):
    raw = git(repo, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", "--text", parent, commit,
              "--", path)
    out, ls, i = [], raw.split(b"\n"), 0
    hunk = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
    while i < len(ls):
        m = hunk.match(ls[i])
        i += 1
        if not m:
            continue
        st, nd = int(m.group(1)), int(m.group(2)) if m.group(2) is not None else 1
        na = int(m.group(4)) if m.group(4) is not None else 1
        gd = ga = 0
        while i < len(ls) and (gd < nd or ga < na):
            if ls[i].startswith(b"-") and gd < nd:
                out.append((st + gd, ls[i][1:]))
                gd += 1
            elif ls[i].startswith(b"+") and ga < na:
                ga += 1
            i += 1
    return out


def lane_leg(tree, repo, tip, detail):
    p = subprocess.run([sys.executable, os.path.join(tree, TOOL), "--repo", repo, "--to", tip, "--json"],
                       capture_output=True, text=True, timeout=1800)
    try:
        j = json.loads(p.stdout)
    except ValueError:
        detail.append(f"lane: tool JSON unreadable (exit {p.returncode}): {p.stderr[-200:]}")
        return False
    s = j.get("summary") or {}
    ok = p.returncode == 0 and s.get("bad_declarations") == 0 and len(j.get("events") or []) >= 5
    detail.append(f"lane: tool exit {p.returncode} events {len(j.get('events') or [])} "
                  f"bad_declarations {s.get('bad_declarations')} regressed {s.get('regressed')} "
                  f"ungraded_lines {s.get('ungraded_lines')}")
    rows = parse_contract(git(repo, "show", f"{tip}:registry/append-only-contract.tsv").decode())
    for pat, _rule, decl, region, _note in rows:
        dp, dn = decl.rsplit(":", 1)
        try:
            body = git(repo, "show", f"{tip}:{dp}").decode("utf-8", "replace").split("\n")
            text = body[int(dn) - 1] if 1 <= int(dn) <= len(body) else None
        except EvalError:
            text = None
        if not binds(text, pat, dp):
            ok = False
            detail.append(f"lane: contract row {pat} declared_at {decl} does not bind under v4")
    titles = {}
    for pat, _r, _d, region, _n in rows:
        m = re.fullmatch(r"exempt=(.+)@[^@:]+:\d+", region)
        if m:
            titles[pat] = {t.strip() for t in m.group(1).split("|") if t.strip()}
    order = git(repo, "rev-list", "--parents", tip).decode().split("\n")
    allpar = {ln.split()[0]: ln.split()[1:] for ln in order if ln.strip()}
    commits = list(allpar)
    origin_cache, keyset_cache = {}, {}

    def blob_ids(f):
        specs = "\n".join(f"{c}:{f}" for c in commits) + "\n"
        out = git(repo, "cat-file", "--batch-check=%(objectname) %(objecttype)", inp=specs.encode()).decode()
        res = {}
        for c, line in zip(commits, out.split("\n")):
            parts = line.split()
            res[c] = parts[0] if len(parts) == 2 and parts[1] == "blob" else None
        return res

    def body_of(b):
        if b not in keyset_cache:
            body = split_lines(git(repo, "cat-file", "blob", b)) if b else []
            keyset_cache[b] = (body, {key(x) for x in body})
        return keyset_cache[b]

    def origins(f):
        """v5 origin: key -> union of titles holding it at each of its births."""
        if f in origin_cache:
            return origin_cache[f]
        bl = blob_ids(f)
        orig = collections.defaultdict(set)
        for c in commits:
            b = bl[c]
            if b is None:
                continue
            body, keys = body_of(b)
            pkeys = set()
            for q in allpar[c]:
                if bl.get(q) == b:
                    pkeys = keys
                    break
                if bl.get(q) is not None:
                    pkeys |= body_of(bl[q])[1]
            if pkeys is keys:
                continue
            for ln, t in zip(body, sections(body)):
                k = key(ln)
                if k not in pkeys:
                    orig[k].add(t)
        origin_cache[f] = orig
        return orig

    for e in j.get("events") or []:
        f, c = e.get("file"), e.get("commit")
        par = (allpar.get(c) or [None])[0]
        if e.get("graded", 0) + e.get("ungraded", 0) != e.get("deleted"):
            ok = False
            detail.append(f"lane: event {str(c)[:12]} {f} graded {e.get('graded')} + ungraded {e.get('ungraded')} "
                          f"!= deleted {e.get('deleted')}")
        if par is not None:
            ns = git(repo, "diff", "--numstat", "--no-renames", par, c, "--", f).decode().split("\t")
            if not ns[1:] or not ns[1].isdigit() or int(ns[1]) != e.get("deleted"):
                ok = False
                detail.append(f"lane: event {str(c)[:12]} {f} deleted {e.get('deleted')} != numstat {ns[1:2]}")
        ex = set()
        for pat, ts in titles.items():
            if fnmatch.fnmatchcase(f or "", pat):
                ex |= ts
        if not e.get("ungraded"):
            continue
        if not ex or par is None:
            ok = False
            detail.append(f"lane: event {str(c)[:12]} {f} ungrades lines in a file with no exempt row")
            continue
        pb = split_lines(git(repo, "show", f"{par}:{f}"))
        psec = sections(pb)
        org = origins(f)
        native = sum(1 for pos, text in deleted_with_pos(repo, par, c, f)
                     if psec[pos - 1] in ex and org.get(key(text), set()) & ex)
        if e["ungraded"] > native:
            ok = False
            detail.append(f"lane: event {c[:12]} {f} ungraded {e['ungraded']} > v5 natively exempt {native}")
        else:
            detail.append(f"lane: event {c[:12]} {f} ungraded {e['ungraded']} <= v5 natively exempt {native}")
    return ok


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", required=True, help="lane clone (read-only)")
    ap.add_argument("--tip", required=True, help="full commit to measure")
    ap.add_argument("--scratch", default=None, help="scratch dir (default: TMPDIR)")
    ap.add_argument("--out", default=None, help="also write the receipt here")
    a = ap.parse_args(argv)
    root = a.scratch or tempfile.gettempdir()
    os.makedirs(root, exist_ok=True)
    S = tempfile.mkdtemp(prefix="r50c2-", dir=root)
    detail = []
    try:
        try:
            tip = git(a.repo, "rev-parse", "--verify", a.tip + "^{commit}").decode().strip()
            arc = git(a.repo, "archive", "--format=tar", tip)
            tree = os.path.join(S, "tree")
            os.makedirs(tree)
            with tarfile.open(fileobj=io.BytesIO(arc)) as tf:
                tf.extractall(tree, filter=lambda m, dest: None if (m.issym() or m.islnk())
                              else tarfile.data_filter(m, dest))
            fx = os.path.join(S, "fx")
            os.makedirs(fx)
            if not os.path.isfile(os.path.join(tree, TOOL)):
                detail.append(f"{TOOL} absent at tip")
                res, ll = [False] * NSCEN, False
            else:
                res = scenarios(tree, fx, detail)
                ll = lane_leg(tree, a.repo, tip, detail)
        except EvalError as exc:
            print(f"could-not-evaluate: {exc}")
            return 2
        fl = len(res) == NSCEN and all(res)
        met = fl and ll
        lines = [f"tip={tip}", f"fixture={int(fl)} lane={int(ll)} scenarios={sum(res)}/{NSCEN} met={met}"]
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
