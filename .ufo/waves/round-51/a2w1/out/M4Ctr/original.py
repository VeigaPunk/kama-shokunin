#!/usr/bin/env python3
"""round51-append-audit-v6-check.py - kama round-51 C2 (calibration) counter.

Question: at a lane revision, does the lane's append-only self-description hold for every
deletion its history holds - not only for deletions of 20 lines or more - with every
graded line that is gone at the revision either restored or disclosed by name, and with
the A-row rule's permitted in-place cells (status, recheck, used-by) not miscounted as
losses?
Routed: corpus/lessons/round-50-verifier-spotcheck.md R6 (C2: "the sub-20 threshold hides
97 events, including the real LOG.md loss at ed135b3c"); considerthese/2026-10-26.md
proposal 1 (flag deletions in append-only files); SCORECARD §Planned (round 51) item 1.

Frozen names (before data):
  tool        tools/append-only-audit.py at --tip (run as a CLI from the tip's own bytes)
  contract    registry/append-only-contract.tsv at --tip
  ledger      registry/append-only-disclosures.tsv at --tip
  key(l)      the line bytes with one trailing CR removed; hashed with sha256 (hex)
  class       `revert` when the deleting commit's subject starts with `Revert "`, else
              `in-place-edit` when the deleted line's -U0 hunk adds lines, else `removal`
  row         a line matching `^ {0,3}| *S[0-9]{3,} *|`, cells split on `|` outside
              backtick spans; eleven cells; mutable cells 8, 10 and 11 (status, recheck,
              used-by)
  base        57a2e25bf702b03aa61f9265e968cf68058ecb82 (round-50 closure; round-51 start)

Legs:
  fixture   nine constructed scenarios (the counter's own fixtures, expectations by
            construction), each audited by the tip's tool CLI with an explicit contract and
            ledger: a 1-line LOG deletion is graded by default (exit 1); an A-row status +
            recheck edit is permitted (exit 0); an A-row `teaches` edit is graded (exit 1);
            a `|` inside a backtick span is not a cell boundary (graded); a dropped row is
            graded; a correct disclosure clears its event (exit 0); a junk-hash, an
            over-count, a wrong-class and a no-event disclosure are each bad (exit 1); a
            disclosure covering one of two lost lines leaves the event unrestored (exit 1);
            a disclosure on the first file of a commit leaves the second file's verdict
            unchanged (exit 1, second file unrestored).
  lane      the tip's tool, run with no --threshold over a clone at --tip: JSON
            `definition` v6 and `threshold` 1, exit 0, summary unrestored 0, partial 0,
            regressed 0, bad_disclosures 0, bad_declarations 0; and the counter's own
            recomputation over the same commits (`git rev-list --topo-order --parents`,
            first-parent diffs) agrees: per event, deleted equals the counter's -U0 count
            and numstat; for A-row files the tool's `permitted` equals the counter's own
            row comparison; for every file whose contract region is `*`, the multiset of
            graded keys the counter finds not held at --tip (held = min(D, max(0, tip -
            kept))) equals the ledger's rows for that event, key by key and count by count
            - nothing hidden, nothing junk; for region-restricted files every ledger row's
            key is among the event's deleted keys at most as often; and every ledger row's
            class equals the counter's own class.
met = fixture (9/9) and lane.
PREDICATE (same sentence in the preregistration): append-only-audit at --tip grades every
deletion by default (threshold 1), permits exactly the A-row status/recheck/used-by cell
edits, and on the lane exits 0 because every graded line gone at --tip is restored or
named in registry/append-only-disclosures.tsv with its mechanical class - the counter's
own recomputation finding the same lost lines, key for key, in every whole-file-graded
file - while nine constructed scenarios each get the verdict their construction fixes;
fixture=1 lane=1.

Output: `fixture=0|1 lane=0|1 scenarios=N/9 lost=L disclosed=X met=True|False`, then
`detail:` lines. Exit 0 met, 1 not met, 2 could not evaluate (git failure).
Read-only on --repo; fixtures live under --scratch and are removed on exit; --out's
parent directories are created before anything is written.
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
BASE = "57a2e25bf702b03aa61f9265e968cf68058ecb82"
HUNK = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
ROW = re.compile(rb"^ {0,3}\| *S[0-9]{3,} *\|")
MUT = (7, 9, 10)
IDENT = ["-c", "user.name=r51c2-fixture", "-c", "user.email=r51c2@invalid", "-c", "commit.gpgsign=false"]
DHEADER = "commit\tfile\tline_sha256\tcount\tclass\tnote"
CHEADER = "path\trule\tdeclared_at\tregion\tnote"


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


def deleted(repo, p, c, f):
    """[(parent line no, bytes, hunk adds)] by hunk-header counts."""
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


def run_tool(tool, repo, to, contract=None, ledger=None, extra=()):
    argv = [sys.executable, tool, "--repo", repo, "--to", to, "--json", *extra]
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


# ------------------------------------------------------------------ fixture leg
def fixtures(tool, S, detail):
    head = "| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |"
    rows = [head, "|---|---|---|---|---|---|---|---|---|---|---|"] + [
        f"| S10{i} | doc {i} https://f.invalid/{i} | docs | A | scope `x|y` {i} | sec | lesson {i} | mined "
        f"| 2026-09-0{i} | 60d | a.md |" for i in range(1, 4)]
    log = [f"entry {i} {os.urandom(3).hex()}" for i in range(6)]
    notes = ["# n", "SRC.md is append-only by row.", "LOG.md is append-only."]
    contract = os.path.join(S, "contract.tsv")
    with open(contract, "w") as fh:
        fh.write(CHEADER + "\nSRC.md\tA-row\tN.md:2\t*\tx\nLOG.md\tA\tN.md:3\t*\tx\n")
    sha = lambda x: hashlib.sha256(x.encode()).hexdigest()  # noqa: E731

    def repo(name, steps):
        d = os.path.join(S, "fx-" + name)
        os.makedirs(d)
        git(d, "init", "-q")
        if os.path.realpath(git(d, "rev-parse", "--show-toplevel").decode().strip()) != os.path.realpath(d):
            raise EvalError("fixture toplevel mismatch")
        for files in steps:
            for fn, body in files.items():
                with open(os.path.join(d, fn), "w") as fh:
                    fh.write("".join(x + "\n" for x in body))
            git(d, "add", "-A")
            git(d, *IDENT, "commit", "-q", "--allow-empty", "-m", "fx")
        return d, git(d, "rev-parse", "HEAD").decode().strip()

    base = {"N.md": notes, "SRC.md": rows, "LOG.md": log}

    def case(name, steps, ledger_rows, want_exit, check):
        d, t = repo(name, [base] + steps)
        led = None
        if ledger_rows is not None:
            led = os.path.join(S, f"ledger-{name}.tsv")
            with open(led, "w") as fh:
                fh.write(DHEADER + "\n" + "".join(r.replace("{t}", t) + "\n" for r in ledger_rows))
        code, res, err = run_tool(tool, d, t, contract, led)
        ok = code == want_exit and res is not None and check(res, t)
        ev = [e for e in (res or {}).get("events", []) if e.get("commit") == t]
        detail.append(f"fixture {name}: exit {code} (want {want_exit}) "
                      f"{'ok' if ok else 'FAIL'} events={[(e.get('file'), e.get('status'), e.get('permitted'), e.get('disclosed')) for e in ev]}"
                      + ("" if res is not None else f" stderr={err!r}"))
        return ok

    def ev(res, t, f):
        e = [x for x in res.get("events", []) if x.get("commit") == t and x.get("file") == f]
        return e[0] if len(e) == 1 else {}

    swap = lambda i, a, b: rows[:i] + [rows[i].replace(a, b)] + rows[i + 1:]  # noqa: E731
    n = 0
    n += case("default-threshold", [{"LOG.md": log[1:]}], None, 1,
              lambda r, t: r.get("threshold") == 1 and ev(r, t, "LOG.md").get("status") == "unrestored")
    n += case("arow-mutable", [{"SRC.md": swap(2, "| mined |", "| queued |")[:2] +
                                [swap(2, "| mined |", "| queued |")[2].replace("60d", "30d")] + rows[3:]}], None, 0,
              lambda r, t: ev(r, t, "SRC.md").get("permitted") == 1 and ev(r, t, "SRC.md").get("graded") == 0)
    n += case("arow-immutable", [{"SRC.md": swap(3, "lesson 2", "lesson two")}], None, 1,
              lambda r, t: ev(r, t, "SRC.md").get("permitted") == 0 and ev(r, t, "SRC.md").get("graded") == 1)
    n += case("code-span-pipe", [{"SRC.md": swap(2, "`x|y`", "`x|z`")}], None, 1,
              lambda r, t: ev(r, t, "SRC.md").get("permitted") == 0)
    n += case("row-dropped", [{"SRC.md": rows[:4]}], None, 1,
              lambda r, t: ev(r, t, "SRC.md").get("status") == "unrestored")
    n += case("disclosed", [{"LOG.md": log[1:]}], [f"{{t}}\tLOG.md\t{sha(log[0])}\t1\tremoval\tx"], 0,
              lambda r, t: ev(r, t, "LOG.md").get("status") == "disclosed")
    bad = [f"{{t}}\tLOG.md\t{sha('nothing')}\t1\tremoval\tx",
           f"{{t}}\tLOG.md\t{sha(log[0])}\t2\tremoval\tx",
           f"{{t}}\tLOG.md\t{sha(log[0])}\t1\tin-place-edit\tx",
           f"{'f' * 40}\tLOG.md\t{sha(log[0])}\t1\tremoval\tx"]
    for j, row in enumerate(bad):
        n += case(f"bad-disclosure-{j + 1}", [{"LOG.md": log[1:]}], [row], 1,
                  lambda r, t: (r.get("summary") or {}).get("bad_disclosures") == 1)
    n += case("partial-disclosure", [{"LOG.md": log[2:]}], [f"{{t}}\tLOG.md\t{sha(log[0])}\t1\tremoval\tx"], 1,
              lambda r, t: ev(r, t, "LOG.md").get("status") == "unrestored" and ev(r, t, "LOG.md").get("disclosed") == 1)
    n += case("two-files-one-commit", [{"N.md": notes + ["x"]}, {"LOG.md": log[1:], "SRC.md": rows[:4]}],
              [f"{{t}}\tLOG.md\t{sha(log[0])}\t1\tremoval\tx"], 1,
              lambda r, t: ev(r, t, "LOG.md").get("status") == "disclosed"
              and ev(r, t, "SRC.md").get("status") == "unrestored" and ev(r, t, "SRC.md").get("restored_max") == 0)
    # bad-disclosure counts as one scenario (four sub-cases must all hold)
    subs = [d for d in detail if d.startswith("fixture bad-disclosure-")]
    bad_ok = len(subs) == 4 and all(" ok " in d for d in subs)
    total = n - sum(1 for d in subs if " ok " in d) + int(bad_ok)
    return total


# ------------------------------------------------------------------ lane leg
def lane(tool, repo, tip, detail):
    code, res, err = run_tool(tool, repo, tip)
    if res is None:
        detail.append(f"lane: tool produced no JSON (exit {code}) {err!r}")
        return False, 0, 0
    s = res.get("summary", {})
    ok = True
    want = {"unrestored": 0, "partial": 0, "regressed": 0, "bad_disclosures": 0, "bad_declarations": 0}
    got = {x: s.get(x) for x in want}
    if res.get("definition") != "v6" or res.get("threshold") != 1 or code != 0 or got != want:
        detail.append(f"lane: tool definition {res.get('definition')} threshold {res.get('threshold')} exit {code} {got}")
        ok = False
    ctext = blob(repo, tip, CONTRACT)
    if ctext is None:
        detail.append("lane: no contract at tip")
        return False, 0, 0
    crow = [ln.split("\t") for ln in ctext.decode().split("\n")[1:] if ln.strip()]
    tree = git(repo, "ls-tree", "-r", "--name-only", "-z", tip).decode().split("\0")
    files = {}
    for f in tree:
        for c in crow:
            if f and fnmatch.fnmatchcase(f, c[0]):
                files.setdefault(f, set()).add((c[1], c[3]))
    led = collections.defaultdict(collections.Counter)
    lcls = {}
    ltext = blob(repo, tip, LEDGER)
    for ln in (ltext.decode().split("\n")[1:] if ltext else []):
        if ln.strip():
            c = ln.split("\t")
            led[(c[0], c[1])][c[2]] += int(c[3])
            lcls[(c[0], c[1], c[2])] = c[4]
    tev = {(e["commit"], e["file"]): e for e in res.get("events", [])}
    commits, parents = [], {}
    for ln in git(repo, "rev-list", "--topo-order", "--reverse", "--parents", tip).decode().split("\n"):
        p = ln.split()
        if p:
            commits.append(p[0])
            parents[p[0]] = p[1] if len(p) > 1 else None
    names = sorted(files)
    lost = 0
    seen = set()
    tipcache = {}
    for c in commits:
        p = parents[c]
        if p is None:
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
            seen.add((c, f))
            e = tev.get((c, f))
            if e is None or e.get("deleted") != len(dl) or len(dl) != int(parts[1]):
                detail.append(f"lane: {c[:12]} {f}: own deleted {len(dl)} numstat {parts[1]} tool "
                              f"{e.get('deleted') if e else 'no event'}")
                ok = False
                continue
            rules = files[f]
            arow = any(r == "A-row" for r, _ in rules)
            whole = all(reg == "*" for _r, reg in rules)
            perm = set()
            if arow:
                new = collections.defaultdict(list)
                for ln in lines_of(blob(repo, c, f)):
                    cc = cells(ln)
                    if cc is not None and len(cc) == 11:
                        new[cc[0]].append([x for j, x in enumerate(cc) if j not in MUT])
                for pos, text, _na in dl:
                    cc = cells(text)
                    if cc is not None and len(cc) == 11 and [x for j, x in enumerate(cc) if j not in MUT] in new.get(cc[0], []):
                        perm.add(pos)
                if e.get("permitted") != len(perm):
                    detail.append(f"lane: {c[:12]} {f}: tool permitted {e.get('permitted')} own {len(perm)}")
                    ok = False
            subj = git(repo, "log", "-1", "--format=%s", c).decode().strip()
            klass = {}
            for pos, text, na in dl:
                if pos not in perm:
                    klass.setdefault(h(text), set()).add(
                        "revert" if subj.startswith('Revert "') else ("in-place-edit" if na else "removal"))
            for (lc, lf, lh), cl in lcls.items():
                if lc == c and lf == f and cl not in klass.get(lh, set()):
                    detail.append(f"lane: ledger {c[:12]} {f} {lh[:12]} class {cl} != own {sorted(klass.get(lh, set()))}")
                    ok = False
            D = collections.Counter(text for pos, text, _na in dl if pos not in perm)
            if whole:
                kept = collections.Counter(lines_of(blob(repo, p, f))) - collections.Counter(t for _p, t, _n in dl)
                if f not in tipcache:
                    tipcache[f] = collections.Counter(lines_of(blob(repo, tip, f)))
                M = tipcache[f]
                un = collections.Counter()
                for l, n in D.items():
                    u = n - min(n, max(0, M[l] - kept[l]))
                    if u:
                        un[h(l)] += u
                lost += sum(un.values())
                if un != led.get((c, f), collections.Counter()):
                    diff_keys = set(un) ^ set(led.get((c, f), {}))
                    detail.append(f"lane: {c[:12]} {f}: own lost {sum(un.values())} ledger "
                                  f"{sum(led.get((c, f), {}).values())} ({len(diff_keys)} keys differ)")
                    ok = False
            else:
                dk = collections.Counter(h(t) for t in D.elements())
                for lh, n in led.get((c, f), {}).items():
                    if n > dk[lh]:
                        detail.append(f"lane: {c[:12]} {f}: ledger {lh[:12]} x{n} > deleted {dk[lh]}")
                        ok = False
    for key_ in led:
        if key_ not in seen:
            detail.append(f"lane: ledger names {key_[0][:12]} {key_[1]}, not a deletion event of a declared file")
            ok = False
    disclosed = sum(sum(v.values()) for v in led.values())
    detail.append(f"lane: tool {res.get('definition')} threshold {res.get('threshold')} exit {code} "
                  f"events {s.get('events')} disclosed_lines {s.get('disclosed_lines')} permitted_lines "
                  f"{s.get('permitted_lines')}; own lost lines in whole-file-graded files {lost}; ledger lines {disclosed}")
    return ok, lost, disclosed


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
    S = tempfile.mkdtemp(prefix="r51c2-", dir=root)
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
            ll, lost, disc = lane(tool, a.repo, tip, detail)
        except EvalError as exc:
            print(f"could-not-evaluate: {exc}")
            return 2
        fl = n == 9
        met = bool(fl and ll)
        lines = [f"tip={tip}", f"fixture={int(fl)} lane={int(ll)} scenarios={n}/9 lost={lost} disclosed={disc} met={met}"]
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
