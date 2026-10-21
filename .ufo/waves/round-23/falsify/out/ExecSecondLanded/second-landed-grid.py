#!/usr/bin/env python3
"""Round-23 fault grid: only the first `## Landed changes` section is read.

Open item under attack (kama round-23 falsify, seat ExecSecondLanded):
tools/report-landing-audit.py captures the report's first `## Landed
changes` section only (`landed_match` uses re.search at
tools/report-landing-audit.py:168-170; audit_round cites only that
section, :316/:323). A report with a second `## Landed changes` section

  * keeps `landed-omitted` for a commit cited only in the second section
    (false positive, annotated cited_elsewhere=true, :331-337), and
  * never checks second-section tokens, so an unresolvable checkable
    token there yields no `landed-unresolved`/`landed-ambiguous`
    (false negative).

Expected correct outcome (this grid's grading target): entries in every
`## Landed changes` section are honored with the tool's own defect
semantics (docstring kinds, tools/report-landing-audit.py:17-26): a
round commit cited in any such section is not omitted; an unresolvable
checkable token in any such section is `landed-unresolved` (plus
`unresolved-full-hash` when 40 hex, mirroring the repo-state grid's own
F04 expectation for first-section placement). Ambiguity overwrite is a
separate open item: every fixture token is verified absent from both
scratch repositories, so the two items cannot contaminate each other.

Arms: the frozen blob FROZEN and the committed file at CURRENT_REV, both
read from the lane repository's object store. Each case builds fresh
/tmp scratch repositories (GIT_CONFIG_GLOBAL=/dev/null,
GIT_CONFIG_NOSYSTEM=1, explicit identity), verifies its premise, and
runs an auditor subprocess with a timeout. A failed premise exits 2
(could not evaluate), never a verdict.

Exit: 0 every row of every selected arm matches the correct outcome;
1 at least one row does not (the item is live in that arm); 2 fixture
premise or tooling failure. Until the item is fixed, both arms are
expected to exit 1: the three SL rows are the fault evidence, the three
SLC rows must pass in both arms (harm none).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile

FROZEN = "4fe9339f8fc3a4a4a479d9c938a850da12f1124d"
CURRENT_REV = "245a37f69628c2c6bb29bbf17897d8fb5946c857"
AUDIT = "tools/report-landing-audit.py"
LANE_DEFAULT = "/home/vgpnk/Projects/shokunin/kama-shokunin"
REL = ".ufo/reports/round-1/kama.md"
FAKE = "1234567890abcdef1234567890abcdef12345678"
BOGUS = "abc123def012"  # 12 hex, digit+letter checkable, object never written
TIMEOUT = 30
HEADINGS = re.compile(rb"(?m)^## Landed changes")


class Premise(Exception):
    """The fixture did not establish its fault: cannot evaluate."""


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise Premise(f"git {' '.join(map(str, args))}: "
                      f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def init(path):
    g(path.parent, "init", "-q", "-b", "master", str(path))
    return path


def commit(repo, author, when, msg, path="f", content=None):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        with open(target, "ab") as fh:
            fh.write((msg + "\n").encode())
    else:
        target.write_bytes(content)
    g(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return g(repo, "rev-parse", "HEAD")


def publish(fleet, text, when=2000):
    commit(fleet, "fleet", when, "round-1: report", REL, text)
    return g(fleet, "show", f"HEAD:{REL}")


def pair(tmp):
    lane, fleet = Path(tmp, "lane"), Path(tmp, "fleet")
    init(lane)
    init(fleet)
    return lane, fleet


def require(cond, what):
    if not cond:
        raise Premise(what)


def report_bytes(first, second=None):
    """Committed report; `second` adds a Notes block and a second
    `## Landed changes` section (same heading, per the open item)."""
    out = (b"# kama round 1\n\n## Work performed\n\nmeasured\n\n"
           b"## Landed changes\n\n")
    out += b"".join(b"- " + c.encode() + b"\n" for c in first)
    if second is not None:
        out += (b"\n## Notes\n\ninterim\n\n## Landed changes\n\n"
                + b"".join(b"- " + c.encode() + b"\n" for c in second))
    return out


def token_absent(token, *repos):
    for repo in repos:
        p = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", token],
                           capture_output=True, env=env())
        require(p.returncode != 0,
                f"{token} unexpectedly resolvable in {repo}")


# ------------------------------------------------------------------ cases
# Each builder returns (lane, fleet, argv_extra, marker_or_None).

def f_sl1_second_section_omission(tmp):
    """Commit B cited only in the second section; correct outcome: not
    omitted (exit 0). Both arms flag landed-omitted (cited_elsewhere)."""
    lane, fleet = pair(tmp)
    a = commit(lane, "kama-shokunin", 1000, "round-1: work")
    b = commit(lane, "kama-shokunin", 1500, "round-1: more")
    text = publish(fleet, report_bytes([a], [b]))
    require(len(HEADINGS.findall(text.encode())) == 2,
            "fixture report lacks a second Landed section")
    require(b in text and a in text and a != b, "citations not committed")
    return lane, fleet, [], None


def f_sl2_second_section_unchecked_token(tmp):
    """Unresolvable checkable token only in the second section; correct
    outcome: landed-unresolved. Both arms stay silent on it."""
    lane, fleet = pair(tmp)
    a = commit(lane, "kama-shokunin", 1000, "round-1: work")
    text = publish(fleet, report_bytes([a], [BOGUS]))
    require(len(HEADINGS.findall(text.encode())) == 2,
            "fixture report lacks a second Landed section")
    token_absent(BOGUS, lane, fleet)
    require(any(ch.isdigit() for ch in BOGUS)
            and any(ch in "abcdef" for ch in BOGUS),
            "BOGUS is not a checkable abbreviation")
    return lane, fleet, [], None


def f_sl3_second_section_token_kind(tmp):
    """40-hex fake token only in the second section; correct outcome:
    landed-unresolved + unresolved-full-hash (the F04 kind pair for a
    fake inside a Landed section). Both arms drop the Landed kind."""
    lane, fleet = pair(tmp)
    a = commit(lane, "kama-shokunin", 1000, "round-1: work")
    text = publish(fleet, report_bytes([a], [FAKE]))
    require(len(HEADINGS.findall(text.encode())) == 2,
            "fixture report lacks a second Landed section")
    token_absent(FAKE, lane, fleet)
    return lane, fleet, [], None


def f_slc1_single_section_cites_all(tmp):
    """Control: same two commits, one section citing both; exit 0."""
    lane, fleet = pair(tmp)
    a = commit(lane, "kama-shokunin", 1000, "round-1: work")
    b = commit(lane, "kama-shokunin", 1500, "round-1: more")
    text = publish(fleet, report_bytes([a, b]))
    require(len(HEADINGS.findall(text.encode())) == 1
            and b in text, "control fixture malformed")
    return lane, fleet, [], None


def f_slc2_single_section_omission(tmp):
    """Control: B nowhere in the report; landed-omitted must fire."""
    lane, fleet = pair(tmp)
    a = commit(lane, "kama-shokunin", 1000, "round-1: work")
    b = commit(lane, "kama-shokunin", 1500, "round-1: more")
    text = publish(fleet, report_bytes([a]))
    require(len(HEADINGS.findall(text.encode())) == 1
            and b not in text, "control fixture malformed")
    return lane, fleet, [], None


def f_slc3_first_section_unchecked_token(tmp):
    """Control: same unresolvable token, first section; landed-unresolved
    must fire (proves SL2's silence is section-specific)."""
    lane, fleet = pair(tmp)
    a = commit(lane, "kama-shokunin", 1000, "round-1: work")
    text = publish(fleet, report_bytes([a, BOGUS]))
    require(len(HEADINGS.findall(text.encode())) == 1
            and BOGUS in text, "control fixture malformed")
    token_absent(BOGUS, lane, fleet)
    return lane, fleet, [], None


CASES = [
    # name, kind, builder, expected-correct {exit, kinds}
    ("SL1-second-section-omission", "fault",
     f_sl1_second_section_omission, 0, []),
    ("SL2-second-section-unchecked-token", "fault",
     f_sl2_second_section_unchecked_token, 1, ["landed-unresolved"]),
    ("SL3-second-section-token-kind", "fault",
     f_sl3_second_section_token_kind, 1,
     ["landed-unresolved", "unresolved-full-hash"]),
    ("SLC1-single-section-cites-all", "control",
     f_slc1_single_section_cites_all, 0, []),
    ("SLC2-single-section-omission", "control",
     f_slc2_single_section_omission, 1, ["landed-omitted"]),
    ("SLC3-first-section-unchecked-token", "control",
     f_slc3_first_section_unchecked_token, 1, ["landed-unresolved"]),
]


def population():
    rows = [[n, k, b.__name__, e, s] for n, k, b, e, s in CASES]
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()


def run_case(auditor, case, tmp):
    name, kind, build, want_exit, want_kinds = case
    lane, fleet, extra, marker = build(tmp)
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--no-errata",
            "--json"]
    try:
        p = subprocess.run(argv, capture_output=True, timeout=TIMEOUT,
                           env=env(), cwd=tmp)
        code, out, err, timed_out = p.returncode, p.stdout, p.stderr, False
    except subprocess.TimeoutExpired as exc:
        code, out, err, timed_out = None, exc.stdout or b"", exc.stderr or b"", True
    kinds, defects = None, None
    if code in (0, 1):
        try:
            doc = json.loads(out)
            defects = [d for r in doc["results"] for d in r["defects"]]
            kinds = sorted({d["kind"] for d in defects})
        except (ValueError, KeyError, TypeError):
            kinds, defects = "unparseable", None
    traceback = b"Traceback (most recent call last)" in err
    executed = bool(marker and marker.exists())
    met = (not timed_out and not traceback and not executed
           and code == want_exit and kinds == sorted(want_kinds))
    return {"case": name, "kind": kind, "exit": code, "kinds": kinds,
            "defects": defects, "traceback": traceback, "executed": executed,
            "timed_out": timed_out, "expected_exit": want_exit,
            "expected_kinds": want_kinds, "met": met,
            "stderr_tail": err.decode(errors="replace").strip()[-200:]}


def lane_object(tmp, lane_dir, spec, name):
    p = subprocess.run(["git", "-C", str(lane_dir), "cat-file", "blob", spec],
                       capture_output=True, env=env())
    if p.returncode:
        raise Premise(f"cannot read {name}: {p.stderr.decode().strip()}")
    path = Path(tmp, name)
    path.write_bytes(p.stdout)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arm", choices=("frozen", "current", "both"),
                    default="both")
    ap.add_argument("--case", action="append", help="run only these cases")
    ap.add_argument("--lane-dir", default=LANE_DEFAULT)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--save", help="write the full JSON document here")
    args = ap.parse_args(argv)
    arms = ("frozen", "current") if args.arm == "both" else (args.arm,)
    cases = [c for c in CASES if not args.case or c[0] in args.case]
    doc = {"frozen_revision": FROZEN, "current_revision": CURRENT_REV,
           "population_sha256": population(), "timeout_seconds": TIMEOUT,
           "arms": {}}
    try:
        with tempfile.TemporaryDirectory(prefix="second-landed-grid-") as root:
            auditors = {
                "frozen": lane_object(root, args.lane_dir,
                                      f"{FROZEN}:{AUDIT}", "frozen-audit.py"),
                "current": lane_object(root, args.lane_dir,
                                       f"{CURRENT_REV}:{AUDIT}",
                                       "current-audit.py")}
            doc["auditor_sha256"] = {
                a: hashlib.sha256(Path(auditors[a]).read_bytes()).hexdigest()
                for a in arms}
            doc["arms_identical"] = (
                auditors["frozen"].read_bytes()
                == auditors["current"].read_bytes())
            for arm in arms:
                rows = []
                for i, case in enumerate(cases):
                    tmp = Path(root, arm, f"{i:02d}")
                    tmp.mkdir(parents=True)
                    rows.append(run_case(auditors[arm], case, tmp))
                graded = [r for r in rows]
                doc["arms"][arm] = {
                    "faults": sum(r["kind"] == "fault" for r in rows),
                    "faults_met": sum(r["met"] for r in rows
                                      if r["kind"] == "fault"),
                    "controls": sum(r["kind"] == "control" for r in rows),
                    "controls_met": sum(r["met"] for r in rows
                                        if r["kind"] == "control"),
                    "tracebacks": sum(r["traceback"] for r in rows),
                    "timeouts": sum(r["timed_out"] for r in rows),
                    "violations": sum(not r["met"] for r in graded),
                    "rows": rows}
    except Premise as exc:
        print(f"could-not-evaluate: fixture premise: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # errors are never grid verdicts
        print(f"could-not-evaluate: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return 2
    if args.save:
        Path(args.save).write_text(
            json.dumps(doc, indent=1, sort_keys=True), encoding="utf-8")
    if args.json:
        print(json.dumps(doc, indent=1, sort_keys=True))
    else:
        for arm, res in doc["arms"].items():
            for r in res["rows"]:
                print(f"{arm} {r['case']} {r['kind']} exit={r['exit']} "
                      f"kinds={r['kinds']} tb={int(r['traceback'])} "
                      f"timeout={int(r['timed_out'])} "
                      f"{'met' if r['met'] else 'NOT-MET'}")
                if not r["met"] and r["defects"] is not None:
                    print(f"  defects={r['defects']}")
            print(f"{arm} faults={res['faults_met']}/{res['faults']} "
                  f"controls={res['controls_met']}/{res['controls']} "
                  f"tracebacks={res['tracebacks']} "
                  f"timeouts={res['timeouts']} "
                  f"violations={res['violations']}")
    bad = any(res["violations"] for res in doc["arms"].values())
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
