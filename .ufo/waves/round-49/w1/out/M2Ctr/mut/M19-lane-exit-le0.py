#!/usr/bin/env python3
"""round49-append-audit-v4-check.py - kama round-49 C2 (calibration) counter.

Question: does the lane's append-only audit still grade the lane's declared rule
when the two escape hatches the round-48 wave found are used?
Routed (SCORECARD.md §Round 48 "What met=True does not show"; corpus/lessons/
round-48-verifier-spotcheck.md R5):
  K1Regions  the v3 exemption is title-based and content-blind: dated-section text
             moved under an exempt `## ` heading and deleted there later is
             `ungraded`, so a loss the lane's rule forbids exits 0;
  K1Binding  a declaration binds by substring (`log` inside `catalog`), by any line
             of a file a wildcard row covers (self-declaration), and its negation
             list is four fixed strings (`not strictly append-only` binds).

v4 definitions (the build must implement them; this counter checks them on its own
fixtures, whose expectations are written by construction, and on the lane):
  origin(l)  the set of `## ` section titles (None before the first heading) that
             hold the line text l in the file's blob at the first commit of
             `git rev-list --topo-order --reverse <to>` whose blob of that file
             holds l
  ungraded   a deleted line is ungraded only when (v3) its parent section is an
             eligible exempt title AND (v4) origin(l) contains one of the file's
             exempt titles; otherwise it is graded
  token      the row token (v3: base name without extension; the parent
             directory's name when the base name has a wildcard) must occur in the
             lower-cased line as a whole word: not preceded or followed by
             [a-z0-9_]
  self       a declaring file covered by the row's pattern binds without naming the
             token only when the pattern has no wildcard
  negation   the line is unbound when any `append-only`/`append only` in it is
             preceded within three words by not, never, no, nor, neither, non,
             isn't, aren't or `no longer` (v3's four fixed strings still apply)
Output JSON shape is unchanged (`"schema": "append-only-audit/v3"`).

Fixture scenarios (each a fresh repo under --scratch; contract outside the repo):
  launder        dated `## Round 1` text moved under the exempt `## Axes` (the
                 move is a held event), then deleted there while `## Axes` regrows
                 past its parent size: expect the c3 event graded=25 ungraded=0
                 status=unrestored and exit 1 (v3: ungraded, exit 0)
  native-head    25 lines born in `## Axes` rewritten in place: expect ungraded=25
                 graded=0 status=ungraded, exit 0 (v4 keeps the carve-out)
  dated-loss     25 lines of `## Round 1` deleted: expect graded=25 unrestored, exit 1
  substring      LOG.md declared by `the catalog is append-only`: expect the row
                 unbound, exit 1 (v3: bound)
  word-token     LOG.md declared by `LOG.md is append-only`: expect bound, exit 0
  negated        SCORE.md declared by `SCORE.md is not strictly append-only`:
                 expect unbound, exit 1 (v3: bound)
  wildcard-self  notes/*.md declared at notes/a.md:1 `this file is append-only`:
                 expect unbound, exit 1 (v3: bound)
  wildcard-named notes/*.md declared at README.md:1 `files under notes/ are
                 append-only`: expect bound, exit 0
Legs:
  fixture  every scenario's expectation holds for the tool at --tip
           (tools/append-only-audit.py from `git archive`)
  lane     the tool at --tip on --repo (contract from --tip) exits 0 with
           bad_declarations 0 and >= 5 events; this counter's own binder (the v4
           rule) binds every --tip contract row; and for every event the tool
           reports, its `ungraded` count is at most this counter's own count of
           the event's deleted lines whose parent section is an exempt title of
           the file and whose origin contains an exempt title
met = fixture and lane.
PREDICATE (same sentence in the preregistration): append-only-audit at the
measured commit grades dated text laundered through an exempt heading,
refuses substring, negated and wildcard self-declaration bindings, keeps the
native head carve-out, and on the lane binds every contract row, exits 0 and
ungrades no deleted line whose origin is not an exempt section; fixture=1 lane=1.

Output: `fixture=0|1 lane=0|1 scenarios=N/8 met=True|False`, then `detail:` lines.
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
IDENT = ["-c", "user.name=r49c2-fixture", "-c", "user.email=r49c2-fixture@invalid", "-c", "commit.gpgsign=false"]
HEADER = "path\trule\tdeclared_at\tregion\tnote"
NEG3 = ("not append-only", "not append only", "no longer append", "never append-only")
NEGW = re.compile(r"(?:\b(?:not|never|no|nor|neither|non|isn't|aren't)\b|\bno longer\b)"
                  r"(?:[\s\-]+[\w'’]+){0,3}?[\s\-]+append[- ]only")


class EvalError(Exception):
    pass


def git(repo, *args, inp=None):
    p = subprocess.run(["git", "-C", repo, *args], input=inp, capture_output=True)
    if p.returncode != 0:
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

    def commit(self, files):
        for name, body in files.items():
            p = os.path.join(self.d, name)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as fh:
                fh.write("".join(x + "\n" for x in body))
        git(self.d, "add", "-A")
        self.n += 1
        git(self.d, *IDENT, "commit", "-q", "--allow-empty", "-m", f"c{self.n}")
        return git(self.d, "rev-parse", "HEAD").decode().strip()


def L(tag, n):
    return [f"{tag} line {i} r49" for i in range(n)]


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
    return results


# ------------------------------------------------------------- lane leg
def sections(lines):
    out, t = [], None
    for ln in lines:
        if ln.startswith(b"## "):
            t = ln.rstrip(b"\r").decode("utf-8", "replace").rstrip()
        out.append(t)
    return out


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
    ok = p.returncode <= 0 and s.get("bad_declarations") == 0 and len(j.get("events") or []) >= 5
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
    order = git(repo, "rev-list", "--topo-order", "--reverse", "--parents", tip).decode().split("\n")
    commits = [ln.split()[0] for ln in order if ln.strip()]
    parents = {ln.split()[0]: (ln.split()[1] if len(ln.split()) > 1 else None) for ln in order if ln.strip()}
    origin_cache = {}

    def origins(f):
        if f in origin_cache:
            return origin_cache[f]
        orig, seen_blob = {}, set()
        specs = "\n".join(f"{c}:{f}" for c in commits) + "\n"
        out = git(repo, "cat-file", "--batch-check=%(objectname) %(objecttype)", inp=specs.encode()).decode()
        for line in out.split("\n"):
            parts = line.split()
            if len(parts) != 2 or parts[1] != "blob" or parts[0] in seen_blob:
                continue
            seen_blob.add(parts[0])
            body = split_lines(git(repo, "cat-file", "blob", parts[0]))
            fresh = collections.defaultdict(set)
            for ln, t in zip(body, sections(body)):
                if ln not in orig:
                    fresh[ln].add(t)
            orig.update(fresh)
        origin_cache[f] = orig
        return orig

    for e in j.get("events") or []:
        f = e.get("file")
        ex = set()
        for pat, ts in titles.items():
            if fnmatch.fnmatchcase(f or "", pat):
                ex |= ts
        if not e.get("ungraded"):
            continue
        par = parents.get(e.get("commit"))
        if not ex or par is None:
            ok = False
            detail.append(f"lane: event {str(e.get('commit'))[:12]} {f} ungrades lines in a file with no exempt row")
            continue
        pb = split_lines(git(repo, "show", f"{par}:{f}"))
        psec = sections(pb)
        org = origins(f)
        native = sum(1 for pos, text in deleted_with_pos(repo, par, e["commit"], f)
                     if psec[pos - 1] in ex and org.get(text, set()) & ex)
        if e["ungraded"] > native:
            ok = False
            detail.append(f"lane: event {e['commit'][:12]} {f} ungraded {e['ungraded']} > natively exempt {native}")
        else:
            detail.append(f"lane: event {e['commit'][:12]} {f} ungraded {e['ungraded']} <= natively exempt {native}")
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
    S = tempfile.mkdtemp(prefix="r49c2-", dir=root)
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
                res, ll = [False] * 8, False
            else:
                res = scenarios(tree, fx, detail)
                ll = lane_leg(tree, a.repo, tip, detail)
        except EvalError as exc:
            print(f"could-not-evaluate: {exc}")
            return 2
        fl = len(res) == 8 and all(res)
        met = fl and ll
        lines = [f"tip={tip}", f"fixture={int(fl)} lane={int(ll)} scenarios={sum(res)}/8 met={met}"]
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
