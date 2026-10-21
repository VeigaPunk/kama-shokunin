#!/usr/bin/env python3
"""Recheck12 (KamaR21 FALSIFY seat): attack C1 on kama round 12.

Read-only against --lane-repo and --fleet-repo. Synthetic fixtures live in a
TemporaryDirectory removed on exit. Every line is a check with an expectation;
exit 0 only when all hold.

  python3 recheck12.py --lane-repo LANE --fleet-repo FLEET \
      --tool LANE/tools/report-landing-audit.py --raw OFFICIAL_RAW_JSON
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict

ATTACK = "a6617149722c73d90e142fbdc8154d6967055f7e"
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
FULL = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{40}(?![0-9A-Za-z])")
ABBREV = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])")
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
N_CHECKS = 0
FAILS = []


def check(name, cond, detail=""):
    global N_CHECKS
    N_CHECKS += 1
    print(("ok   " if cond else "FAIL ") + name + (f" :: {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)


def git(repo, *args, stdin=None):
    r = subprocess.run(["git", "--no-optional-locks", "-C", str(repo), *args],
                       input=stdin, capture_output=True, text=True, env=ENV)
    return r.returncode, r.stdout, r.stderr


def iso(t):
    return datetime.datetime.fromtimestamp(int(t), datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def checkable(t):
    return len(t) == 40 or (re.search(r"[0-9]", t) is not None and re.search(r"[a-f]", t) is not None)


def landed(text):
    m = re.search(r"^## Landed changes[^\n]*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return None if m is None else m.group(1)


def commits_named(repo, tok):
    """Per-object: commit objects that `tok` names in one repo (type-filtered)."""
    rc, out, _ = git(repo, "rev-parse", "--disambiguate=" + tok)
    names = out.split() if rc == 0 else []
    return {x for x in names if git(repo, "cat-file", "-t", x)[1].strip() == "commit"}


def candidates(lane, fleet, tok):
    return commits_named(lane, tok) | commits_named(fleet, tok)


def object_exists(lane, fleet, tok):
    return any(git(repo, "cat-file", "-t", tok)[0] == 0 for repo in (lane, fleet))


def lane_rows(lane, rev):
    rc, out, err = git(lane, "log", "--format=%H|%an|%at|%ct|%s", rev)
    if rc:
        raise SystemExit(f"git log {rev} failed: {err.strip()}")
    rows = []
    for line in out.splitlines():
        s, an, at, ct, subj = line.split("|", 4)
        rows.append((s, an, int(at), int(ct), subj))
    return rows


def first_add(fleet, n):
    rc, out, _ = git(fleet, "log", "--diff-filter=A", "--format=%H|%at|%ct", "--",
                     f".ufo/reports/round-{n}/kama.md")
    lines = out.strip().splitlines()
    if not lines:
        return None
    h, at, ct = lines[-1].split("|")
    return h, int(at), int(ct)


def round_pattern(n):
    return re.compile(rf"^(?:round-{n}:|checkpoint\(r{n}\))")


def derive(lane, fleet, rows, n, rule, add):
    """Per-object derivation of the C1 defect set for round n under one time rule."""
    cutoff = add[1] if rule == "author" else add[2]
    tcol = 2 if rule == "author" else 3
    text = open(os.path.join(fleet, f".ufo/reports/round-{n}/kama.md"), encoding="utf-8").read()
    defects, disagree = [], []
    for t in sorted(set(FULL.findall(text))):
        if not object_exists(lane, fleet, t):
            defects.append(("unresolved-full-hash", t))
    sec = landed(text)
    if sec is None:
        defects.append(("landed-section-missing", "-"))
        sec = ""
    toks = sorted(set(ABBREV.findall(sec)))
    named = set()
    for t in toks:
        cands = candidates(lane, fleet, t)
        named |= cands
        if checkable(t):
            if not cands:
                defects.append(("landed-unresolved", t))
            elif len(cands) > 1:
                defects.append(("landed-ambiguous", t))
    commits = [r for r in rows if r[1] == "kama-shokunin" and round_pattern(n).match(r[4])]
    pre = [r for r in commits if r[tcol] <= cutoff]
    for r in pre:
        by_prefix = any(r[0].startswith(t) for t in toks)
        if by_prefix != (r[0] in named):
            disagree.append(r[0][:12])
        if not by_prefix:
            defects.append(("landed-omitted", r[0]))
    return {"cutoff": cutoff, "pre": sorted(r[0] for r in pre),
            "post": sorted(r[0] for r in commits if r[tcol] > cutoff),
            "defects": sorted(defects), "disagree": disagree}


def tool_run(tool, lane, fleet, rounds):
    r = subprocess.run([sys.executable, tool, "--lane-repo", lane, "--fleet-repo", fleet,
                        "--rounds", rounds, "--no-errata", "--json"],
                       capture_output=True, text=True, env=ENV, cwd=lane)
    return r.returncode, (json.loads(r.stdout) if r.stdout.strip() else None), r.stderr


def load_tool(path):
    spec = importlib.util.spec_from_file_location("rla", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane-repo", required=True)
    ap.add_argument("--fleet-repo", required=True)
    ap.add_argument("--tool", required=True)
    ap.add_argument("--raw", required=True)
    a = ap.parse_args()
    lane, fleet, tool = (os.path.abspath(a.lane_repo), os.path.abspath(a.fleet_repo),
                         os.path.abspath(a.tool))
    lib = load_tool(tool)
    rows = lane_rows(lane, ATTACK)
    check("0 lane history at attacked commit readable", len(rows) > 0, f"commits={len(rows)}")
    check("0b no lane commit has author time later than committer time",
          all(r[2] <= r[3] for r in rows))

    # A. Literal round-12 command, and the official 10-20 raw reproduction.
    rc, doc, _ = tool_run(tool, lane, fleet, "12")
    res12 = doc["results"][0] if doc else {}
    check("A1 literal `--rounds 12 --no-errata --json` exits 0", rc == 0, f"rc={rc}")
    check("A2 round 12: 0 defects, required 2, post 0, cutoff 1792471121",
          res12.get("defects") == [] and res12.get("required") == 2
          and res12.get("post_report") == [] and res12.get("cutoff") == 1792471121,
          f"cutoff={res12.get('cutoff')} required={res12.get('required')}")
    rc, doc, _ = tool_run(tool, lane, fleet, "10-20")
    raw = json.load(open(a.raw, encoding="utf-8"))
    check("A3 `--rounds 10-20` exits 1 with 9 uncorrected defects",
          rc == 1 and doc["summary"]["defects"] == 9, f"rc={rc}")
    check("A4 `--rounds 10-20` results and summary identical to committed raw",
          doc["results"] == raw["results"] and doc["summary"] == raw["summary"])
    tr = {r["round"]: r for r in doc["results"]}

    # B. Author-time vs committer-time, per-object vs tool, rounds 10-20.
    for n in range(10, 21):
        add = first_add(fleet, n)
        A = derive(lane, fleet, rows, n, "author", add)
        Cc = derive(lane, fleet, rows, n, "committer", add)
        tdef = sorted((d["kind"], d["token"]) for d in tr[n]["defects"])
        same_rule = A["pre"] == Cc["pre"] and A["post"] == Cc["post"] and A["defects"] == Cc["defects"]
        tool_eq = (tdef == A["defects"] and sorted(tr[n]["post_report"]) == A["post"]
                   and len(A["pre"]) == tr[n]["required"])
        check(f"B round {n}: per-object == tool; author rule == committer rule",
              same_rule and tool_eq and not A["disagree"] and not Cc["disagree"],
              f"defects={len(tdef)} required={len(A['pre'])} post={len(A['post'])}")
    for n in range(10, 21):
        add = first_add(fleet, n)
        for r in rows:
            if r[1] == "kama-shokunin" and r[2] != r[3] and round_pattern(n).match(r[4]):
                print(f"   note round {n} {r[0][:12]} A={iso(r[2])} C={iso(r[3])} "
                      f"cutoff={iso(add[1])} committer_margin_s={add[1] - r[3]}")

    # C. Batch-check (tool lookup) vs per-object statuses on every token, rounds 10-20.
    mism = total = 0
    for n in range(10, 21):
        text = open(os.path.join(fleet, f".ufo/reports/round-{n}/kama.md"), encoding="utf-8").read()
        chk = sorted(set(t for t in ABBREV.findall(landed(text) or "") if lib.checkable_abbrev(t)))
        bstat = lib.lookup((lane, fleet), chk, "^{commit}")
        for t in chk:
            c = candidates(lane, fleet, t)
            want = "missing" if not c else ("found" if len(c) == 1 else "ambiguous")
            total += 1
            mism += bstat[t] != want
        full = sorted(set(FULL.findall(text)))
        fstat = lib.lookup((lane, fleet), full, "")
        for t in full:
            total += 1
            mism += fstat[t] != ("found" if object_exists(lane, fleet, t) else "missing")
    check("C1 batch-check statuses == per-object statuses (rounds 10-20)", mism == 0,
          f"tokens={total} mismatches={mism}")

    # D. Round 12 specifics.
    add12, add11 = first_add(fleet, 12), first_add(fleet, 11)
    print(f"   round 12 fleet add {add12[0][:12]} author={iso(add12[1])} committer={iso(add12[2])}")
    d12 = derive(lane, fleet, rows, 12, "author", add12)
    d12c = derive(lane, fleet, rows, 12, "committer", add12)
    r12 = [r for r in rows if r[1] == "kama-shokunin" and round_pattern(12).match(r[4])]
    check("D1 round 12 fleet add: author time == committer time", add12[1] == add12[2])
    check("D2 round 12 lane commits: author time == committer time",
          all(r[2] == r[3] for r in r12),
          "; ".join(f"{r[0][:12]} A={iso(r[2])} C={iso(r[3])}" for r in r12))
    check("D3 round 12: author rule == committer rule == expected {33f46685, 1df80eab}, 0 defects",
          d12 == d12c and d12["defects"] == [] and d12["pre"] == sorted(r[0] for r in r12)
          and len(r12) == 2, f"pre={[p[:12] for p in d12['pre']]}")
    window = [r for r in rows if r[1] == "kama-shokunin" and add11[1] < r[2] <= add12[1]]
    check("E1 round-12 window (r11 cutoff, r12 cutoff]: every kama-shokunin commit has a round-12 subject",
          all(round_pattern(12).match(r[4]) for r in window),
          "; ".join(f"{r[0][:12]} {iso(r[2])} {r[4][:40]}" for r in window))
    allrows = lane_rows(lane, "--all")
    on_master = {r[0] for r in rows}
    extra = [r for r in allrows if r[0] not in on_master and re.search(r"^(?:round-\d+:|checkpoint\(r\d+\))", r[4])]
    check("E2 no round-subject commit reachable only from a non-master ref", not extra, f"extra={len(extra)}")

    # F. Synthetic fixtures: 7-char ambiguity, fleet masking, controls, cutoff selection.
    with tempfile.TemporaryDirectory(prefix="recheck12-") as tmp:
        def mkrepo(name):
            d = os.path.join(tmp, name)
            os.makedirs(d)
            subprocess.run(["git", "init", "-q", "-b", "master", d], env=ENV, check=True)
            return d

        def hobj(repo, content):
            r = subprocess.run(["git", "-C", repo, "hash-object", "--literally", "-t", "commit", "-w", "--stdin"],
                               input=content, capture_output=True, env=ENV)
            assert r.returncode == 0, r.stderr
            return r.stdout.decode().strip()

        def ccontent(i):
            return (f"tree {EMPTY_TREE}\nauthor kama-shokunin <kama@shokunin.local> {1000 + i} +0000\n"
                    f"committer kama-shokunin <kama@shokunin.local> {1000 + i} +0000\n\n"
                    f"round-1: candidate {i}\n").encode()

        def chash(c):
            return hashlib.sha1(b"commit %d\x00" % len(c) + c).hexdigest()

        groups = defaultdict(list)
        for i in range(60000):
            groups[chash(ccontent(i))[:7]].append(i)
        i, j = next(v[:2] for v in groups.values() if len(v) >= 2)
        X, Y = chash(ccontent(i)), chash(ccontent(j))
        P7 = X[:7]
        L2 = mkrepo("lane")
        assert hobj(L2, ccontent(i)) == X and hobj(L2, ccontent(j)) == Y
        merge = (f"tree {EMPTY_TREE}\nparent {X}\nparent {Y}\nauthor merge-bot <m@x> 1050 +0000\n"
                 f"committer merge-bot <m@x> 1050 +0000\n\nmerge\n").encode()
        subprocess.run(["git", "-C", L2, "update-ref", "refs/heads/master", hobj(L2, merge)], env=ENV, check=True)
        rc, out, _ = git(L2, "cat-file", "--batch-check", stdin=f"{P7}^{{commit}}\n{P7}\n")
        check("F1 git batch-check on two lane commits sharing P7: `P7^{commit}` -> missing, `P7` -> ambiguous",
              rc == 0 and out.splitlines() == [f"{P7}^{{commit}} missing", f"{P7} ambiguous"],
              " | ".join(out.splitlines()))

        def mkfleet(name, body, copies=()):
            d = mkrepo(name)
            for c in copies:
                hobj(d, c)
            os.makedirs(os.path.join(d, ".ufo/reports/round-1"))
            with open(os.path.join(d, ".ufo/reports/round-1/kama.md"), "w", encoding="utf-8") as fh:
                fh.write(body)
            subprocess.run(["git", "-C", d, "add", "--", ".ufo/reports/round-1/kama.md"], env=ENV, check=True)
            e = dict(ENV, GIT_AUTHOR_NAME="kama-shokunin", GIT_AUTHOR_EMAIL="kama@shokunin.local",
                     GIT_AUTHOR_DATE="@1000000 +0000", GIT_COMMITTER_NAME="kama-shokunin",
                     GIT_COMMITTER_EMAIL="kama@shokunin.local", GIT_COMMITTER_DATE="@1000000 +0000")
            subprocess.run(["git", "-C", d, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
                            "round-1: kama report"], env=e, check=True)
            return d

        def audit(fleet_dir):
            rc2, doc2, _ = tool_run(tool, L2, fleet_dir, "1")
            res = doc2["results"][0] if doc2 else {}
            return rc2, sorted((d["kind"], d["token"]) for d in res.get("defects", [])), res.get("required")

        bodyA = f"# r1\n## Landed changes\n- `{P7}` candidate work\n"
        rcA, dA, _ = audit(mkfleet("fleetA", bodyA))
        check("F2 ambiguous 7-char citation, fleet lacks X: exit 1 and kind is landed-unresolved (not landed-ambiguous)",
              rcA == 1 and dA == [("landed-unresolved", P7)], f"rc={rcA} defects={dA}")
        rcB, dB, reqB = audit(mkfleet("fleetB", bodyA, copies=[ccontent(i)]))
        check("F3 same citation, fleet holds a copy of X: exit 0 (lane ambiguity masked by fleet 'found')",
              rcB == 0 and dB == [], f"rc={rcB} defects={dB} required={reqB}")
        rcC, dC, reqC = audit(mkfleet("fleetC", f"# r1\n## Landed changes\n- `{X}` a\n- `{Y}` b\n"))
        check("F4 control: full X and Y cited -> exit 0, required 2", rcC == 0 and dC == [] and reqC == 2,
              f"rc={rcC} required={reqC}")
        rcD, dD, _ = audit(mkfleet("fleetD", f"# r1\n## Landed changes\n- `{Y}` b\n"))
        check("F5 control: only Y cited -> landed-omitted X detected",
              rcD == 1 and dD == [("landed-omitted", X)], f"rc={rcD} defects={dD}")

        FR = mkrepo("fleet_readd")

        def fcommit(msg, content, a_t, c_t):
            p = os.path.join(FR, ".ufo/reports/round-1/kama.md")
            if content is None:
                subprocess.run(["git", "-C", FR, "rm", "-q", "-f", "--", ".ufo/reports/round-1/kama.md"],
                               env=ENV, check=True)
            else:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(content)
                subprocess.run(["git", "-C", FR, "add", "--", ".ufo/reports/round-1/kama.md"], env=ENV, check=True)
            e = dict(ENV, GIT_AUTHOR_NAME="kama-shokunin", GIT_AUTHOR_EMAIL="kama@shokunin.local",
                     GIT_AUTHOR_DATE=f"@{a_t} +0000", GIT_COMMITTER_NAME="kama-shokunin",
                     GIT_COMMITTER_EMAIL="kama@shokunin.local", GIT_COMMITTER_DATE=f"@{c_t} +0000")
            subprocess.run(["git", "-C", FR, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg],
                           env=e, check=True)

        fcommit("add", "# v1\n## Landed changes\nnone\n", 2000, 5000)
        fcommit("remove", None, 3000, 3000)
        fcommit("re-add", "# v2\n## Landed changes\nnone\n", 2500, 4000)
        adds = git(FR, "log", "--diff-filter=A", "--format=%at", "--", ".ufo/reports/round-1/kama.md")[1].split()
        check("F6 report_cutoff is the topologically-first add (author 2000), not the re-add (2500)",
              int(adds[-1]) == 2000 and lib.report_cutoff(FR, ".ufo/reports/round-1/kama.md") == 2000,
              f"git lists {adds}")

    print(f"recheck12: checks={N_CHECKS} fails={len(FAILS)}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
