#!/usr/bin/env python3
"""Round-23 falsify grid for RevLookup F1: peel/cross-repo ambiguity overwrite.

Fault under attack (corpus/lessons/round-23.md, open, not claimed by C1):
a `## Landed changes` citation whose 7-hex prefix matches a commit and a blob
in one repository, or two commits across the lane and fleet repositories, is
"an ambiguous abbreviation" by the auditor's own defect definition
(tools/report-landing-audit.py:20 at 245a37f), yet a successful peel
(`<prefix>^{commit}` resolves by type, lookup():130-165) or a resolution in
the *other* repository (per-repo `found` overwrites `ambiguous`,
lookup():153-154) erases the ambiguity, so `landed-ambiguous` is never
reported. The same peel lookup validates errata corrections
(apply_errata():389-392).

Arms (both extracted with git cat-file, never a working-tree copy):
  frozen   4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py
  current  245a37f69628c2c6bb29bbf17897d8fb5946c857:tools/report-landing-audit.py

Rows are graded on the current arm (the falsify target); frozen cells are
recorded as context. Every fixture premise is verified with plain git before
grading; a failed premise exits 2, never a pass. Fixture repositories are
fresh scratch repos; collision objects come from a fast-import stream that is
byte-identical to the build wave's (.ufo/waves/round-23/build/out/RevLookup/
fixtures.py build_chunks), so the collision short-oids are reproducible.

Exit: 0 every graded row met its normative expectation (F1 falsified);
      1 at least one graded fault row unmet on current, or a control
        regression (F1 holds);
      2 could not evaluate (fixture premise failed, git or arm unusable).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

FROZEN_REV = "4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py"
CURRENT_REV = "245a37f69628c2c6bb29bbf17897d8fb5946c857:tools/report-landing-audit.py"
CURRENT_TIP = "245a37f69628c2c6bb29bbf17897d8fb5946c857"
REL = "tools/report-landing-audit.py"
N_OBJ = 90000
TIMEOUT = 30
BUILD_TIMEOUT = 300


class Premise(Exception):
    """The fixture did not establish its fault: cannot evaluate."""


class Tee:
    def __init__(self, path):
        self.fh = open(path, "w", encoding="utf-8")
        self.stdout = sys.stdout

    def write(self, text):
        self.fh.write(text)
        self.stdout.write(text)

    def flush(self):
        self.fh.flush()
        self.stdout.flush()


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_NAME="fixture", GIT_AUTHOR_EMAIL="f@example.invalid",
             GIT_COMMITTER_NAME="fixture", GIT_COMMITTER_EMAIL="f@example.invalid")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, timeout=BUILD_TIMEOUT, **extra):
    proc = subprocess.run(["git", "-C", str(repo), *args], input=data,
                          capture_output=True, env=env(**extra), timeout=timeout)
    if check and proc.returncode:
        raise Premise(f"git {' '.join(map(str, args))}: "
                      f"{proc.stderr.decode(errors='replace').strip()[:300]}")
    return proc.stdout.decode(errors="surrogateescape").strip()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def default_repo(start):
    for cand in [start, *start.parents]:
        if (cand / ".git").exists():
            return cand
    raise SystemExit("no git repository above this file; pass --repo")


def extract_arm(repo, rev, dest):
    proc = subprocess.run(["git", "-C", str(repo), "cat-file", "blob", rev],
                          capture_output=True, env=env())
    if proc.returncode != 0 or not proc.stdout:
        raise Premise(f"cannot extract {rev} from {repo}: "
                      f"{proc.stderr.decode(errors='replace').strip()[:200]}")
    Path(dest).write_bytes(proc.stdout)
    return dest


def build_chunks(n):
    # Byte-identical stream to the build wave's fixtures.py build_chunks, so
    # collision oids match across waves.
    chunks = []
    mark = 0
    for i in range(n):
        mark += 1
        body = f"blob probe {i}\n".encode()
        chunks.append((mark, "blob",
                       f"blob\nmark :{mark}\ndata {len(body)}\n".encode()
                       + body + b"\n"))
    for j in range(n):
        mark += 1
        msg = f"collision probe {j}\n".encode()
        ts = 1600000000 + j
        head = (f"reset refs/heads/x\ncommit refs/heads/x\nmark :{mark}\n"
                f"author T <t@example.invalid> {ts} +0000\n"
                f"committer T <t@example.invalid> {ts} +0000\n"
                f"data {len(msg)}\n").encode()
        chunks.append((mark, "commit", head + msg + b"\n"))
    return chunks


def fast_import(repo, stream, marks_path):
    proc = subprocess.run(["git", "-C", str(repo), "fast-import", "--quiet",
                           f"--export-marks={marks_path}"], input=stream,
                          capture_output=True, env=env(), timeout=BUILD_TIMEOUT)
    if proc.returncode != 0:
        raise Premise("fast-import: "
                      + proc.stderr.decode(errors="replace")[:300])
    oids = {}
    for line in Path(marks_path).read_text().splitlines():
        mark_text, oid = line.split(" ")
        oids[int(mark_text[1:])] = oid
    return oids


def hexish(text):
    # parity with the auditor's checkable_abbrev
    return (re.search("[0-9]", text) is not None
            and re.search("[a-f]", text) is not None)


def init(path):
    path.mkdir(parents=True)
    g(path.parent, "init", "-q", "-b", "main", str(path))
    return path


def base_commit(repo, when):
    (Path(repo) / "f.txt").write_text("init\n", encoding="utf-8")
    g(repo, "add", "f.txt")
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "init",
      GIT_AUTHOR_DATE=f"@{when} +0000", GIT_COMMITTER_DATE=f"@{when} +0000")


def commit_report(fleet, rnd, body, when):
    relpath = f".ufo/reports/round-{rnd}/kama.md"
    path = Path(fleet, relpath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    g(fleet, "add", relpath)
    g(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
      f"report r{rnd}", GIT_AUTHOR_DATE=f"@{when} +0000",
      GIT_COMMITTER_DATE=f"@{when} +0000")
    return relpath


def landed_body(token):
    return ("# round report\n\n## Work performed\nroutine fixture work\n\n"
            f"## Landed changes\n- `{token}` fixture citation\n\n"
            "## Notes\nend\n")


def batch_line(repo, query):
    out = g(repo, "cat-file", "--batch-check", data=f"{query}\n".encode(),
            check=False)
    return out.split("\n")[0].strip()


def lk(mod, repos, tokens, peel=""):
    try:
        return mod.lookup([Path(r) for r in repos], list(tokens), peel)
    except Exception as exc:  # arms promise EvalError, never a traceback
        return f"{type(exc).__name__}: {exc}"[:200]


def run_arm(py, lane, fleet, rnd, errata=None):
    argv = [sys.executable, str(py), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--branch", "main",
            "--rounds", str(rnd), "--json"]
    argv += ["--errata", str(errata)] if errata else ["--no-errata"]
    started = time.monotonic()
    try:
        proc = subprocess.run(argv, capture_output=True, env=env(),
                              timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return {"rc": "timeout", "defects": None, "stderr": "",
                "seconds": round(time.monotonic() - started, 2)}
    cell = {"rc": proc.returncode,
            "seconds": round(time.monotonic() - started, 2),
            "stderr": proc.stderr.decode(errors="replace").strip()[-200:]}
    defects = None
    if proc.returncode in (0, 1):
        try:
            doc = json.loads(proc.stdout.decode())
        except ValueError:
            doc = None
        if isinstance(doc, dict):
            defects = []
            for res in doc.get("results", []):
                for d in res.get("defects", []):
                    defects.append(f"{d['kind']}:{d['token']}")
            for e in doc.get("errata_invalid", []):
                defects.append(f"errata-invalid:{e['correction']}")
            defects = sorted(defects)
    cell["defects"] = defects
    return cell


def show(cell):
    bits = [f"rc={cell['rc']}"]
    if cell["defects"] is not None:
        bits.append(f"defects={cell['defects']}")
    if cell["stderr"]:
        bits.append(f"stderr={cell['stderr']!r}")
    bits.append(f"t={cell['seconds']}s")
    return " ".join(bits)


def main():
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=None,
                    help="git repo holding both arm revs (default: walk up)")
    ap.add_argument("--scratch", type=Path,
                    default=Path("/tmp/kama-r23w2/ExecAmbiguityFixture-grid"))
    args = ap.parse_args()
    repo = (args.repo or default_repo(here)).resolve()

    scratch = args.scratch
    shutil.rmtree(scratch, ignore_errors=True)
    scratch.mkdir(parents=True)
    out = Tee(here / "grid-run.txt")
    sys.stdout = out

    print(f"# RevLookup F1 falsify grid — peel/cross-repo ambiguity overwrite")
    print(f"repo         : {repo}")
    print(f"repo HEAD    : {g(repo, 'rev-parse', 'HEAD')}"
          f"{' (== expected tip)' if g(repo, 'rev-parse', 'HEAD') == CURRENT_TIP else ' (WARNING: not the expected tip)'}")
    print(f"git          : {subprocess.run(['git', '--version'], capture_output=True, env=env()).stdout.decode().strip()}")
    frozen = extract_arm(repo, FROZEN_REV, scratch / "frozen_audit.py")
    current = extract_arm(repo, CURRENT_REV, scratch / "current_audit.py")
    print(f"frozen arm   : {FROZEN_REV} sha256={sha256(frozen)}")
    print(f"current arm  : {CURRENT_REV} sha256={sha256(current)}")
    print(f"scratch      : {scratch}")

    # ---- fixtures --------------------------------------------------------
    lane = init(scratch / "lane")
    base_commit(lane, 1600000000)
    chunks = build_chunks(N_OBJ)
    kind = {m: k for m, k, _ in chunks}
    chunk_of = {m: c for m, _, c in chunks}
    oids = fast_import(lane, b"".join(c for _, _, c in chunks),
                       scratch / "marks-lane.txt")
    groups = {}
    for mark, oid in oids.items():
        groups.setdefault(oid[:7], {"commit": [], "blob": []})[kind[mark]].append(mark)

    cb = cc = None
    for prefix, gg in groups.items():
        if not hexish(prefix):
            continue
        if cb is None and len(gg["commit"]) == 1 and len(gg["blob"]) == 1:
            cb = prefix
        if cc is None and len(gg["commit"]) == 2 and not gg["blob"]:
            cc = prefix
    if cb is None or cc is None:
        raise Premise(f"no 7-hex collisions among {N_OBJ}+{N_OBJ} objects")
    unique = next(p for p, gg in groups.items()
                  if hexish(p) and len(gg["commit"]) == 1 and not gg["blob"])
    first_mark, second_mark = sorted(groups[cc]["commit"])
    first_oid = oids[first_mark]

    absent = "d3adb33"
    while not batch_line(lane, absent).endswith(" missing"):
        absent = format(int(absent, 16) + 1, "07x")
    absent2 = format(int(absent, 16) + 1, "07x")
    while not batch_line(lane, absent2).endswith(" missing"):
        absent2 = format(int(absent2, 16) + 1, "07x")

    fleet_pos = init(scratch / "fleet-pos")   # holds the FIRST cross-repo commit
    foids = fast_import(fleet_pos, chunk_of[first_mark],
                        scratch / "marks-fleet-pos.txt")
    if foids.get(first_mark) != first_oid:
        raise Premise("fleet-pos import diverged from lane oid")
    base_commit(fleet_pos, 1600000001)
    fleet_ctl = init(scratch / "fleet-ctl")   # holds no collision objects
    base_commit(fleet_ctl, 1600000002)

    # ---- premise verification with plain git (never the arms) ------------
    def need(cond, msg):
        if not cond:
            raise Premise(msg)

    # batch-check prints the resolved 40-hex oid (not the query) on found lines
    def found_parts(repo_, query):
        parts = batch_line(repo_, query).split(" ")
        return parts if (len(parts) == 3
                         and re.fullmatch(r"[0-9a-f]{40}", parts[0])) else None

    cb_commit_oid = oids[groups[cb]["commit"][0]]
    need(batch_line(lane, cb).endswith(" ambiguous"),
         f"lane bare {cb} not ambiguous")
    peel = found_parts(lane, f"{cb}^{{commit}}")
    need(peel is not None and peel[0] == cb_commit_oid and peel[1] == "commit",
         f"lane peel {cb}^{{commit}} did not resolve by type: {peel!r}")
    need(batch_line(lane, cc).endswith(" ambiguous"),
         f"lane bare {cc} not ambiguous")
    fp = found_parts(fleet_pos, cc)
    need(fp is not None and fp[0] == first_oid and fp[1] == "commit",
         f"fleet-pos bare {cc} not the first commit: {fp!r}")
    need(batch_line(fleet_ctl, cc).endswith(" missing"),
         f"fleet-ctl bare {cc} not missing")
    for repo_ in (lane, fleet_pos):
        need(batch_line(repo_, absent).endswith(" missing"),
             f"{repo_.name} bare {absent} not missing")
        need(batch_line(repo_, absent2).endswith(" missing"),
             f"{repo_.name} bare {absent2} not missing")
    print(f"cb={cb} cc={cc} unique={unique} first={first_oid[:12]} "
          f"absent={absent},{absent2} (premises verified with plain git)")

    reports = {}
    reports[1] = commit_report(fleet_pos, 1, landed_body(cb), 1700000001)
    reports[2] = commit_report(fleet_pos, 2, landed_body(cc), 1700000002)
    reports[3] = commit_report(fleet_pos, 3, landed_body(unique), 1700000003)
    reports[4] = commit_report(fleet_pos, 4, landed_body(absent), 1700000004)
    reports[5] = commit_report(fleet_pos, 5, landed_body(absent), 1700000005)
    reports[6] = commit_report(fleet_pos, 6, landed_body(absent), 1700000006)
    errata5 = scratch / "errata5.tsv"
    errata5.write_text(f"5\tlanded-unresolved\t{absent}\t{cb}\tfixture errata\n",
                       encoding="utf-8")
    errata6 = scratch / "errata6.tsv"
    errata6.write_text(
        f"6\tlanded-unresolved\t{absent}\t{absent2}\tfixture errata\n",
        encoding="utf-8")
    commit_report(fleet_ctl, 1, landed_body(cc), 1700000007)

    BASE = load("frozen_audit", frozen)
    CUR = load("current_audit", current)

    # ---- grid ------------------------------------------------------------
    rows = []

    def row(rid, kind, expect, frozen_cell, current_cell, met, note=""):
        rows.append({"id": rid, "kind": kind, "expect": expect,
                     "frozen": frozen_cell, "current": current_cell,
                     "met": met, "note": note})

    print("\n== Section A: lookup() matrix (module level)")
    a_specs = [
        ("A1a", "control", "bare commit+blob prefix in lane -> ambiguous",
         [lane], [cb], ""),
        ("A1b", "fault", "peel commit+blob prefix keeps ambiguity visible",
         [lane], [cb], "^{commit}"),
        ("A2a", "fault", "bare cross-repo prefix (lane both, fleet first) -> ambiguous",
         [lane, fleet_pos], [cc], ""),
        ("A2b", "fault", "peel cross-repo prefix -> ambiguous",
         [lane, fleet_pos], [cc], "^{commit}"),
        ("A2c", "control", "bare cross-repo prefix, fleet lacks both -> ambiguous",
         [lane, fleet_ctl], [cc], ""),
        ("A3", "control", "unique real prefix -> found (bare and peel)",
         [lane], [unique], ""),
        ("A4", "control", "absent token -> missing",
         [lane, fleet_pos], [absent], ""),
    ]
    for rid, kind, desc, repos, tokens, peel in a_specs:
        cells = {}
        for label, mod in (("frozen", BASE), ("current", CUR)):
            cells[label] = lk(mod, repos, tokens, peel)
        expect = ({t: "ambiguous" for t in tokens} if "ambig" in desc
                  else ({t: ("found" if "unique" in desc else "missing")
                         for t in tokens}))
        expect = str(expect)
        if rid == "A3":
            expect = "found (bare and peel)"
            met = (cells["current"] == {tokens[0]: "found"}
                   and lk(CUR, repos, tokens, "^{commit}") == {tokens[0]: "found"})
        elif rid == "A4":
            expect = str({t: "missing" for t in tokens})
            met = cells["current"] == {t: "missing" for t in tokens}
        else:
            met = cells["current"] == {t: "ambiguous" for t in tokens}
        row(rid, kind, expect, cells["frozen"], cells["current"], met)
        print(f"== {rid} {kind}: {desc}\n"
              f"   expect(current): {expect}\n"
              f"   frozen : {cells['frozen']}\n"
              f"   current: {cells['current']}\n"
              f"   met(current): {'yes' if met else 'no'}")

    print("\n== Section B: audit replay (subprocess, main() exit codes)")
    b_specs = [
        ("B1", "fault", "Landed cites commit+blob 7-hex prefix",
         fleet_pos, 1, None,
         lambda cell: cell["rc"] == 1 and cell["defects"] == [f"landed-ambiguous:{cb}"],
         f"rc=1 defects=['landed-ambiguous:{cb}']"),
        ("B2", "fault", "Landed cites cross-repo commit+commit prefix",
         fleet_pos, 2, None,
         lambda cell: cell["rc"] == 1 and cell["defects"] == [f"landed-ambiguous:{cc}"],
         f"rc=1 defects=['landed-ambiguous:{cc}']"),
        ("B2c", "control", "same citation, fleet lacks both commits",
         fleet_ctl, 1, None,
         lambda cell: cell["rc"] == 1 and cell["defects"] == [f"landed-ambiguous:{cc}"],
         f"rc=1 defects=['landed-ambiguous:{cc}']"),
        ("B3", "control", "Landed cites a unique real prefix",
         fleet_pos, 3, None,
         lambda cell: cell["rc"] == 0 and cell["defects"] == [],
         "rc=0 defects=[]"),
        ("B4", "control", "Landed cites an absent token",
         fleet_pos, 4, None,
         lambda cell: cell["rc"] == 1 and cell["defects"] == [f"landed-unresolved:{absent}"],
         f"rc=1 defects=['landed-unresolved:{absent}']"),
        ("B5", "fault", "errata correction is the ambiguous commit+blob prefix",
         fleet_pos, 5, errata5,
         lambda cell: cell["rc"] == 1 and f"errata-invalid:{cb}" in (cell["defects"] or []),
         f"rc=1 defects contain 'errata-invalid:{cb}'"),
        ("B5c", "control", "errata correction absent everywhere",
         fleet_pos, 6, errata6,
         lambda cell: cell["rc"] == 1 and f"errata-invalid:{absent2}" in (cell["defects"] or []),
         f"rc=1 defects contain 'errata-invalid:{absent2}'"),
    ]
    slowest = 0.0
    for rid, kind, desc, fleet, rnd, errata, check, expect in b_specs:
        cells = {}
        for label, mod_file in (("frozen", frozen), ("current", current)):
            cells[label] = run_arm(mod_file, lane, fleet, rnd, errata)
            if isinstance(cells[label]["seconds"], float):
                slowest = max(slowest, cells[label]["seconds"])
        met = check(cells["current"])
        row(rid, kind, expect, show(cells["frozen"]), show(cells["current"]), met)
        print(f"== {rid} {kind}: {desc}\n"
              f"   expect(current): {expect}\n"
              f"   frozen : {show(cells['frozen'])}\n"
              f"   current: {show(cells['current'])}\n"
              f"   met(current): {'yes' if met else 'no'}")

    # ---- verdict ---------------------------------------------------------
    faults_unmet = [r["id"] for r in rows if r["kind"] == "fault" and not r["met"]]
    controls_unmet = [r["id"] for r in rows if r["kind"] == "control" and not r["met"]]
    print("\n== Verdict")
    print(f"fault rows unmet on current : {faults_unmet or 'none'}")
    print(f"control rows unmet on current: {controls_unmet or 'none'}")
    print(f"slowest current-arm audit run: {slowest}")
    if faults_unmet or controls_unmet:
        print("F1 HOLDS: the current arm erases a real abbreviation ambiguity "
              "(peel/cross-repo overwrite); normative expectation not met.")
        code = 1
    else:
        print("F1 FALSIFIED: the current arm met every graded row.")
        code = 0
    print(f"(frozen cells are context only; scratch kept at {scratch})")
    sys.stdout = out.stdout
    out.fh.close()
    return code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Premise as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        sys.exit(2)
