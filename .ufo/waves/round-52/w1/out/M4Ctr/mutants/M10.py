#!/usr/bin/env python3
"""round52-append-restore-check.py - kama round-52 C2 (calibration) counter.

Question: at a lane revision, does the lane's append-only self-description hold in its
correction-appending (A-corr) files - every line any commit deleted from a graded region of
LOG.md, SCORECARD.md, corpus/QUALITY.md, corpus/README.md or a filed lesson is still held
in that file - so that the disclosure ledger names only losses a verbatim re-append cannot
repair (A / A-row files, where a duplicated registry or errata row would be a new defect)?
And does the counter decide graded regions with its own section logic, not the tool's?
Routed: SCORECARD §Planned (round 52) item 2 (recompute the exempt= and only= files
independently, test the ledger's introduction cutoff in the counter, decide whether the
in-place edits disclosed in round 51 warrant appended corrections - the round-51 slice
audits judged them contrary to the files' own A-corr practice); round-51 closure D5 (C2
carried limits: region-restricted files only bound-checked; cutoff untested).

Frozen names (before data):
  tool        tools/append-only-audit.py at --tip (run as a CLI from the tip's own bytes)
  contract    registry/append-only-contract.tsv; every row of it at --base must be present
              at --tip with the same path, rule and region (a dropped or narrowed row fails
              the lane leg); the files audited are the --tip rows expanded over the tip tree
  ledger      registry/append-only-disclosures.tsv at --tip
  key(l)      the line bytes with one trailing CR removed; hashed with sha256 (hex)
  fence       the counter's own CommonMark 0.31.2 §4.5 reading: a line of 0-3 spaces then
              3+ backticks (info string without a backtick) or 3+ tildes opens; a line of
              0-3 spaces, the same character at least as many times, then only spaces or
              tabs closes; an unclosed fence runs to the end of the file
  section(l)  in the PARENT blob, the text of the last line at or before l that starts with
              `## ` and is not inside or itself a fence line (`\\r` and trailing blanks
              stripped); None before the first
  graded      region `*`: every deleted line; `exempt=T1|..@p:n`: a deleted line whose
              section is not one of the Ti; `only=P@p:n`: a deleted line whose section
              starts with P; minus, for an A-row file, a deleted registry row (`^ {0,3}|
              *S[0-9]{3,} *|`, eleven cells split on `|` outside backtick spans) whose id
              the commit's blob still holds with cells other than 8, 10, 11 byte-equal
  unheld      per event (commit c, file f, first-parent diff): for each key l graded G[l]
              times, G[l] - min(G[l], max(0, M_tip[l] - K[l])), M_tip the tip blob's line
              multiset and K the parent's lines the diff kept
  base        9ff76b1f763512be2f554cbbfd0b2213b63b0847 (round-51 tip after the
              orchestrator's salvage; round-52 start)

Legs:
  fixture   eight constructed scenarios (the counter's own fixtures, expectations by
            construction), each audited by the tip's tool CLI with an explicit contract and
            the counter's own recomputation on the same repo: (1) an A-corr line edited in
            place: tool exit 1, counter unheld 1; (2) the same, with the original line
            re-appended verbatim inside a five-backtick fence at the end of the file: tool
            exit 0, counter unheld 0; (3) an in-tree ledger that discloses a deletion made
            after the ledger's own introduction: tool exit 1; (4) an in-tree ledger that
            discloses a deletion made before its introduction: tool exit 0; (5) an only=
            file edited above its region: tool exit 0, counter graded 0; (6) the same file
            edited inside its region: tool exit 1, counter unheld 1; (7) an exempt= file
            edited inside an exempt section (line count kept): tool exit 0, counter graded
            0; (8) the same file edited in a dated section: tool exit 1, counter unheld 1.
  lane      the tip's tool, run with no --threshold over a clone at --tip: exit 0, summary
            unrestored 0, partial 0, regressed 0, bad_disclosures 0, bad_declarations 0;
            every --base contract row present at --tip unchanged; and the counter's own
            recomputation over `git rev-list --topo-order --parents --tip` (first-parent
            diffs, -U0 hunk counts equal to numstat) finds corr_lost = 0 unheld lines in
            files whose rules are all A-corr, and, for files with an A or A-row rule, the
            unheld keys of each event equal the ledger's rows for that event key by key
            and count by count; no ledger row names an A-corr-only file or a commit/file
            pair that is not a deletion event.
met = fixture (8/8) and lane.
PREDICATE (same sentence in the preregistration): every line any commit deleted from a
graded region of the lane's A-corr append-only files is held at --tip by the counter's own
section and fence logic (corr_lost=0), the disclosure ledger names exactly the unheld lines
of the A and A-row files, the tip's append-only-audit exits 0 on the lane, and eight
constructed scenarios - the ledger cutoff, only= and exempt= regions, and a fenced verbatim
re-append among them - each get the verdict their construction fixes; fixture=1 lane=1
corr_lost=0.

Output: `fixture=0|1 lane=0|1 scenarios=N/8 corr_lost=C row_lost=R disclosed=X
met=True|False`, then `detail:` lines. Exit 0 met, 1 not met, 2 could not evaluate.
Read-only on --repo; fixtures live under --scratch (default TMPDIR) and are removed on
exit; --out's parent directories are created before anything is written.
"""
from __future__ import annotations

import argparse
import collections
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOOL = "tools/append-only-audit.py"
CONTRACT = "registry/append-only-contract.tsv"
LEDGER = "registry/append-only-disclosures.tsv"
BASE = "9ff76b1f763512be2f554cbbfd0b2213b63b0847"
HUNK = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
ROW = re.compile(rb"^ {0,3}\| *S[0-9]{3,} *\|")
OPEN = re.compile(rb"^ {0,3}(`{3,}|~{3,})(.*)$")
MUT = (7, 9, 10)
IDENT = ["-c", "user.name=r52c2-fixture", "-c", "user.email=r52c2@invalid", "-c", "commit.gpgsign=false"]
DHEADER = "commit\tfile\tline_sha256\tcount\tclass\tnote"
CHEADER = "path\trule\tdeclared_at\tregion\tnote"
NSCEN = 8


class EvalError(Exception):
    pass


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode != 0:
        raise EvalError(f"git {' '.join(args)[:100]}: {p.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return p.stdout


def blob(repo, rev, path):
    p = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True)
    return p.stdout if p.returncode == 0 else None


def lines_of(data):
    if data is None:
        return []
    segs = data.split(b"\n")
    if segs and segs[-1] == b"":
        segs.pop()
    return segs


def k(ln):
    return ln[:-1] if ln.endswith(b"\r") else ln


def h(ln):
    return hashlib.sha256(k(ln)).hexdigest()


def cells(ln):
    if not ROW.match(ln):
        return None
    try:
        s = ln.decode("utf-8").rstrip("\r").strip()
    except UnicodeDecodeError:
        return None
    out, cur, code = [], "", False
    for ch in s[1:]:
        if ch == "`":
            code = not code
        if ch == "|" and not code:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    return out if not cur.strip() else None


def sections(lines):
    """Per line (0-based), the counter's own fence-aware `## ` section title."""
    out, cur, fence = [], None, None
    for ln in lines:
        x = k(ln)
        if fence is not None:
            ch, n = fence
            m = re.match(rb"^ {0,3}(" + re.escape(ch) + rb"{%d,})[ \t]*$" % n, x)
            if m:
                fence = None
            out.append(cur)
            continue
        m = OPEN.match(x)
        if m and not (m.group(1)[:1] == b"`" and b"`" in m.group(2)):
            fence = (m.group(1)[:1], len(m.group(1)))
            out.append(cur)
            continue
        if x.startswith(b"## "):
            cur = x.rstrip().decode("utf-8", "replace")
        out.append(cur)
    return out


def region_of(cell):
    if cell == "*":
        return ("*", None)
    kind, _, rest = cell.partition("=")
    titles = rest.rsplit("@", 1)[0]
    if kind == "exempt":
        return ("exempt", set(titles.split("|")))
    if kind == "only":
        return ("only", titles)
    raise EvalError(f"region {cell!r} unreadable")


def deleted(repo, p, c, f):
    """[(parent line no (1-based), bytes, hunk adds)] by hunk-header counts."""
    raw = git(repo, "diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0", "--text", p, c, "--", f)
    out, ls, i = [], raw.split(b"\n"), 0
    while i < len(ls):
        m = HUNK.match(ls[i])
        i += 1
        if not m:
            continue
        start, nd = int(m.group(1)), int(m.group(2)) if m.group(2) is not None else 1
        na = int(m.group(4)) if m.group(4) is not None else 1
        gd = ga = 0
        while i < len(ls) and (gd < nd or ga < na):
            if ls[i].startswith(b"-") and gd < nd:
                out.append((start + gd, ls[i][1:], na))
                gd += 1
            elif ls[i].startswith(b"+") and ga < na:
                ga += 1
            i += 1
    return out


def graded_of(repo, p, c, f, regions, arow, dl):
    """The graded deleted lines [(pos, text)] by the counter's own section logic."""
    psec = None
    if any(r[0] != "*" for r in regions):
        psec = sections(lines_of(blob(repo, p, f)))
    perm = set()
    if arow:
        new = collections.defaultdict(list)
        for ln in lines_of(blob(repo, c, f)):
            cc = cells(ln)
            if cc is not None and len(cc) == 11:
                new[cc[0]].append([x for j, x in enumerate(cc) if j not in MUT])
        for pos, text, _na in dl:
            cc = cells(text)
            if cc is not None and len(cc) == 11 and [x for j, x in enumerate(cc) if j not in MUT] in new.get(cc[1], []):
                perm.add(pos)
    out = []
    for pos, text, _na in dl:
        if pos in perm:
            continue
        g = False
        for kind, arg in regions:
            if kind == "*":
                g = True
            else:
                s = psec[pos - 1] if psec is not None and 0 < pos <= len(psec) else None
                if kind == "exempt" and s not in arg:
                    g = True
                elif kind == "only" and s is not None and s.startswith(arg):
                    g = True
        if g:
            out.append((pos, text))
    return out, len(perm)


def recompute(repo, tip, files, detail, tev=None):
    """{(commit, file): Counter(unheld key hash -> n)}, graded count, numstat agreement."""
    commits, parents = [], {}
    for ln in git(repo, "rev-list", "--topo-order", "--reverse", "--parents", tip).decode().split("\n"):
        q = ln.split()
        if q:
            commits.append(q[0])
            parents[q[0]] = q[1] if len(q) > 1 else None
    names = sorted(files)
    unheld, graded_n, ok, tipcache = {}, 0, True, {}
    for c in commits:
        p = parents[c]
        if p is None or not names:
            continue
        ns = git(repo, "diff", "--no-renames", "--numstat", "-z", p, c, "--", *names).decode().split("\0")
        for rec in ns:
            parts = rec.split("\t")
            if len(parts) != 3 or parts[1] in ("-", "0"):
                continue
            f = parts[2]
            if f not in files:
                continue
            dl = deleted(repo, p, c, f)
            if len(dl) != int(parts[1]):
                detail.append(f"lane: {c[:12]} {f}: own deleted {len(dl)} numstat {parts[1]}")
                ok = False
            rules = files[f]
            regions = [region_of(reg) for _r, reg in rules]
            G, _perm = graded_of(repo, p, c, f, regions, any(r == "A-row" for r, _ in rules), dl)
            graded_n += len(G)
            if tev is not None:
                e = tev.get((c, f))
                if e is None or e.get("deleted") != len(dl):
                    detail.append(f"lane: {c[:12]} {f}: own deleted {len(dl)} tool "
                                  f"{e.get('deleted') if e else 'no event'}")
                    ok = False
            if not G:
                unheld[(c, f)] = collections.Counter()
                continue
            kept = collections.Counter(k(x) for x in lines_of(blob(repo, p, f))) - \
                collections.Counter(k(t) for _p, t, _n in dl)
            if f not in tipcache:
                tipcache[f] = collections.Counter(k(x) for x in lines_of(blob(repo, tip, f)))
            M = tipcache[f]
            D = collections.Counter(k(t) for _p, t in G)
            un = collections.Counter()
            for l, n in D.items():
                u = n - min(n, max(0, M[l] - kept[l]))
                if u:
                    un[hashlib.sha256(l).hexdigest()] += u
            unheld[(c, f)] = un
    return unheld, graded_n, ok


def run_tool(tool, repo, to, contract=None, ledger=None):
    argv = [sys.executable, tool, "--repo", repo, "--to", to, "--json"]
    if contract:
        argv += ["--contract", contract]
    if ledger:
        argv += ["--disclosures", ledger]
    p = subprocess.run(argv, capture_output=True, text=True)
    try:
        res = json.loads(p.stdout)
    except ValueError:
        res = None
    return p.returncode, res, p.stderr[-300:]


def files_of(repo, tip, crow):
    tree = git(repo, "ls-tree", "-r", "--name-only", "-z", tip).decode().split("\0")
    files = {}
    for f in tree:
        for c in crow:
            if f and fnmatch.fnmatchcase(f, c[0]):
                files.setdefault(f, set()).add((c[1], c[3]))
    return files


def parse_contract(text):
    return [ln.split("\t") for ln in text.decode().split("\n")[1:] if ln.strip()]


# ------------------------------------------------------------------ fixture leg
def fixtures(tool, S, detail):
    notes = ["# notes", "score.md is append-only below its head.",
             "The ## Axes and ## Plan heads of score.md are re-derived in place.",
             "know.md keeps its ## Errata region append-only.",
             "LOG.md is append-only; corrections are appended.",
             "SRC.md is append-only by row."]
    crows = ["LOG.md\tA-corr\tNOTES.md:5\t*\tx",
             "score.md\tA-corr\tNOTES.md:2\texempt=## Axes|## Plan@NOTES.md:3\tx",
             "know.md\tA-corr\tNOTES.md:4\tonly=## Errata@NOTES.md:4\tx",
             "SRC.md\tA-row\tNOTES.md:6\t*\tx"]
    contract = os.path.join(S, "contract.tsv")
    with open(contract, "w") as fh:
        fh.write(CHEADER + "\n" + "".join(r + "\n" for r in crows))
    head = "| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |"
    src = [head, "|---|---|---|---|---|---|---|---|---|---|---|"] + [
        f"| S10{i} | doc {i} https://f.invalid/{i} | docs | A | scope {i} | sec | lesson {i} | mined "
        f"| 2026-09-0{i} | 60d | a.md |" for i in range(1, 4)]
    log = [f"entry {i} {os.urandom(3).hex()}" for i in range(6)]
    score = ["# score", "## Axes"] + [f"axis {i}" for i in range(4)] + ["## Round 1"] + [f"dated {i}" for i in range(4)]
    know = ["# know", "body 1", "body 2", "## Errata"] + [f"erratum {i}" for i in range(3)]
    base = {"NOTES.md": notes, "SRC.md": src, "LOG.md": log, "score.md": score, "know.md": know}
    sha = lambda x: hashlib.sha256(x.encode()).hexdigest()  # noqa: E731
    parsed = parse_contract((CHEADER + "\n" + "\n".join(crows)).encode())

    def repo(name, steps):
        d = os.path.join(S, "fx-" + name)
        os.makedirs(d)
        git(d, "init", "-q")
        if os.path.realpath(git(d, "rev-parse", "--show-toplevel").decode().strip()) != os.path.realpath(d):
            raise EvalError("fixture toplevel mismatch")
        for files in steps:
            for fn, body in files.items():
                os.makedirs(os.path.dirname(os.path.join(d, fn)) or d, exist_ok=True)
                with open(os.path.join(d, fn), "w") as fh:
                    fh.write("".join(x + "\n" for x in body))
            git(d, "add", "-A")
            git(d, *IDENT, "commit", "-q", "--allow-empty", "-m", "fx")
        return d, git(d, "rev-parse", "HEAD").decode().strip()

    def case(name, steps, want_exit, want_unheld, want_graded=None):
        d, t = repo(name, [base] + steps)
        code, res, err = run_tool(tool, d, t, contract)
        fd = []
        un, gn, _ok = recompute(d, t, files_of(d, t, parsed), fd)
        own = sum(sum(v.values()) for v in un.values())
        ok = code == want_exit and res is not None and own == want_unheld and \
            (want_graded is None or gn == want_graded)
        detail.append(f"fixture {name}: tool exit {code} (want {want_exit}) own unheld {own} "
                      f"(want {want_unheld}) own graded {gn}{'' if want_graded is None else f' (want {want_graded})'} "
                      f"{'ok' if ok else 'FAIL'}" + ("" if res is not None else f" stderr={err!r}"))
        return ok

    fence = ["", "`````text"]
    n = 0
    edited = [log[0], log[1] + " (edited)"] + log[2:]
    n += case("corr-in-place", [{"LOG.md": [log[0]] + edited[1:]}], 1, 1)
    n += case("corr-fenced-reappend", [{"LOG.md": [log[0]] + edited[1:]},
                                       {"LOG.md": [log[0]] + edited[1:] + fence + [log[1], "`````"]}], 0, 0)
    led_old = f"{{c}}\tSRC.md\t{sha(src[4])}\t1\tremoval\tx"
    drop = src[:4]

    def ledger_case(name, before):
        # before: the deletion is committed before the ledger's introduction
        led_dir = "registry/append-only-disclosures.tsv"
        d = os.path.join(S, "fx-" + name)
        os.makedirs(d)
        git(d, "init", "-q")
        if os.path.realpath(git(d, "rev-parse", "--show-toplevel").decode().strip()) != os.path.realpath(d):
            raise EvalError("fixture toplevel mismatch")

        def commit(files):
            for fn, body in files.items():
                os.makedirs(os.path.dirname(os.path.join(d, fn)) or d, exist_ok=True)
                with open(os.path.join(d, fn), "w") as fh:
                    fh.write("".join(x + "\n" for x in body))
            git(d, "add", "-A")
            git(d, *IDENT, "commit", "-q", "--allow-empty", "-m", "fx")
            return git(d, "rev-parse", "HEAD").decode().strip()
        commit({**base, CONTRACT: [CHEADER] + crows})
        if before:
            c = commit({"SRC.md": drop})
            t = commit({led_dir: [DHEADER, led_old.replace("{c}", c)]})
        else:
            commit({led_dir: [DHEADER]})
            c = commit({"SRC.md": drop})
            t = commit({led_dir: [DHEADER, led_old.replace("{c}", c)]})
        code, res, err = run_tool(tool, d, t)
        want = 0 if before else 1
        bad = (res or {}).get("summary", {}).get("bad_disclosures")
        ok = code == want and res is not None and bad == (0 if before else 1)
        detail.append(f"fixture {name}: tool exit {code} (want {want}) bad_disclosures {bad} "
                      f"(want {0 if before else 1}) "
                      f"{'ok' if ok else 'FAIL'}" + ("" if res is not None else f" stderr={err!r}"))
        return ok
    n += ledger_case("cutoff-after-intro", False)
    n += ledger_case("cutoff-before-intro", True)
    n += case("only-outside", [{"know.md": ["# know", "body 1 (edited)"] + know[2:]}], 0, 0, 0)
    n += case("only-inside", [{"know.md": know[:4] + ["erratum 0 (edited)"] + know[5:]}], 1, 1, 1)
    n += case("exempt-inside", [{"score.md": score[:2] + ["axis 0 (re-derived)"] + score[3:]}], 0, 0, 0)
    n += case("exempt-dated", [{"score.md": score[:7] + ["dated 0 (edited)"] + score[8:]}], 1, 1, 1)
    return n


# ------------------------------------------------------------------ lane leg
def lane(tool, repo, tip, detail):
    code, res, err = run_tool(tool, repo, tip)
    if res is None:
        detail.append(f"lane: tool produced no JSON (exit {code}) {err!r}")
        return False, -1, -1, -1
    s = res.get("summary", {})
    ok = True
    want = {"unrestored": 0, "partial": 0, "regressed": 0, "bad_disclosures": 0, "bad_declarations": 0}
    got = {x: s.get(x) for x in want}
    if code != 0 or got != want:
        detail.append(f"lane: tool definition {res.get('definition')} threshold {res.get('threshold')} exit {code} {got}")
        ok = False
    ctext, btext = blob(repo, tip, CONTRACT), blob(repo, BASE, CONTRACT)
    if ctext is None or btext is None:
        detail.append("lane: no contract at tip or base")
        return False, -1, -1, -1
    crow = parse_contract(ctext)
    have = {(c[0], c[1], c[3]) for c in crow if len(c) >= 4}
    for c in parse_contract(btext):
        if (c[0], c[1], c[3]) not in have:
            detail.append(f"lane: base contract row {c[0]} {c[1]} {c[3][:40]} absent or changed at tip")
            ok = False
    files = files_of(repo, tip, crow)
    led = collections.defaultdict(collections.Counter)
    ltext = blob(repo, tip, LEDGER)
    for ln in (ltext.decode().split("\n")[1:] if ltext else []):
        if ln.strip():
            c = ln.split("\t")
            led[(c[0], c[1])][c[2]] += int(c[3])
    tev = {(e["commit"], e["file"]): e for e in res.get("events", [])}
    unheld, gn, rok = recompute(repo, tip, files, detail, tev)
    ok = ok and rok
    corr = row = 0
    corr_files = collections.Counter()
    for (c, f), un in unheld.items():
        n = sum(un.values())
        rowfile = any(r in ("A", "A-row") for r, _ in files[f])
        if rowfile:
            row += n
            if un != led.get((c, f), collections.Counter()):
                detail.append(f"lane: {c[:12]} {f}: own unheld {n} ledger {sum(led.get((c, f), {}).values())} "
                              f"({len(set(un) ^ set(led.get((c, f), {})))} keys differ)")
                ok = False
        else:
            corr += n
            if n:
                corr_files[f] += n
            if led.get((c, f)):
                detail.append(f"lane: ledger discloses {c[:12]} {f}, an A-corr file (restore by append)")
                ok = False
    for key_ in led:
        if key_ not in unheld:
            detail.append(f"lane: ledger names {key_[0][:12]} {key_[1]}, not a deletion event of a declared file")
            ok = False
    if corr:
        detail.append(f"lane: unheld lines in A-corr files: {dict(corr_files.most_common())}")
    disclosed = sum(sum(v.values()) for v in led.values())
    detail.append(f"lane: tool {res.get('definition')} threshold {res.get('threshold')} exit {code} "
                  f"events {s.get('events')} disclosed_lines {s.get('disclosed_lines')}; own graded {gn}; "
                  f"own unheld A-corr {corr}, A/A-row {row}; ledger lines {disclosed}")
    return ok and corr == 0, corr, row, disclosed


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", required=True, help="lane clone (read-only)")
    ap.add_argument("--tip", required=True, help="full commit to measure")
    ap.add_argument("--scratch", default=None, help="scratch dir (default: TMPDIR)")
    ap.add_argument("--out", default=None, help="also write the receipt here")
    a = ap.parse_args(argv)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    root = a.scratch or tempfile.gettempdir()
    os.makedirs(root, exist_ok=True)
    S = tempfile.mkdtemp(prefix="r52c2-", dir=root)
    detail = []
    try:
        try:
            tip = git(a.repo, "rev-parse", "--verify", a.tip + "^{commit}").decode().strip()
            src = git(a.repo, "show", f"{tip}:{TOOL}")
        except EvalError as exc:
            print(f"could-not-evaluate: {exc}")
            return 2
        tool = os.path.join(S, "append-only-audit.py")
        with open(tool, "wb") as fh:
            fh.write(src)
        try:
            n = fixtures(tool, S, detail)
            ll, corr, row, disc = lane(tool, a.repo, tip, detail)
        except EvalError as exc:
            print(f"could-not-evaluate: {exc}")
            return 2
        fl = n == NSCEN
        met = bool(fl and ll)
        lines = [f"tip={tip}", f"fixture={int(fl)} lane={int(ll)} scenarios={n}/{NSCEN} corr_lost={corr} "
                 f"row_lost={row} disclosed={disc} met={met}"]
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
