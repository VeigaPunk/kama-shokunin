#!/usr/bin/env python3
"""Differential mutation runner for the kama round-23 repo-state fault grid.

Derives named mutants of a candidate tools/report-landing-audit.py, runs the
real grid (out/GridHarness/repo-state-grid.py) on the pristine candidate and on
each mutant, and attributes kills differentially: a mutant kills the graded
rows it newly fails, i.e. rows failing on the mutant but not on the pristine.

Grid interface (read from GridHarness, not assumed):
  repo-state-grid.py --arm current --current PATH --json
  stdout  {"mode", "pass", "reasons", "population_sha256", "rows": [...]}
  row     {"case", "kind", "expect", "observed": {"current": obs},
           "ok": {"current": true | false | null}}
  obs     {"verdict", "exit", "traceback", "marker", "timed_out", "defects"}
  Graded kinds: control, fault, guard. open and tradeoff rows are never graded.
  Exit: 0 gate holds, 1 gate violated, 2 cannot evaluate.

Mutant groups:
  defense  removes one hardening defense through every channel that enforces
           it. Must newly fail at least one of its predicted rows.
  probe    removes exactly one channel, or one protective wrapper. Predicted to
           newly fail nothing: a survivor is a finding (channel redundancy or a
           grid blind spot), a new kill would be unexpected and is reported.

Every edit is an exact literal substring that must occur exactly once in the
candidate. A mutant that cannot be anchored or does not compile is reported as
NOT-APPLIED or INVALID and is never counted as a kill.

Exit: 0 pristine clean, every defense killed as predicted, every probe as
      predicted; 1 a defense survived or a probe deviated from prediction;
      2 pristine fails graded rows not listed in --accept-baseline, or a grid
      error; 3 a mutant is not applied or does not compile.
"""
import argparse
import concurrent.futures
import hashlib
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

GRID = Path(__file__).resolve().parents[1] / "GridHarness" / "repo-state-grid.py"
GRADED = ("control", "fault", "guard")
GRID_TIMEOUT_S = 1800


@dataclass(frozen=True)
class Mutant:
    name: str
    group: str       # "defense" or "probe"
    fault: str       # fault class or coverage question the mutant exercises
    edits: tuple     # ((exact_old, exact_new), ...); each old occurs exactly once
    kills: frozenset  # defense: predicted rows, one must be newly failed; probe: empty


# Argv channel and env channel of each protective setting, from the
# git-wrapper.patch candidate (_GIT_PREFIX tuple and git_env update).
NO_REPLACE_ARGV = ('"--no-replace-objects", "--no-lazy-fetch",', '"--no-lazy-fetch",')
NO_REPLACE_ENV = ('GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1", **extra)',
                  'GIT_NO_LAZY_FETCH="1", **extra)')
NO_LAZY_ARGV = ('"--no-replace-objects", "--no-lazy-fetch",', '"--no-replace-objects",')
NO_LAZY_ENV = ('GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1", **extra)',
               'GIT_NO_REPLACE_OBJECTS="1", **extra)')
REFUSAL = 'print(f"could-not-evaluate: {exc}", file=sys.stderr)\n        return 2'

MUTANTS = (
    Mutant("drop-no-replace-objects", "defense",
           "(c) replace ref hides an omitted round commit; (d) replace ref makes a fabricated citation resolve",
           (NO_REPLACE_ARGV, NO_REPLACE_ENV), frozenset({"F3", "F4", "F4b"})),
    Mutant("drop-no-lazy-fetch", "defense",
           "(e) promisor lazy fetch runs the repo-configured core.sshCommand",
           (NO_LAZY_ARGV, NO_LAZY_ENV), frozenset({"F5"})),
    Mutant("decode-errors-replace", "defense",
           "(b) invalid UTF-8 committed report decoded with errors=replace instead of refusal",
           (('return proc.stdout.decode("utf-8")',
             'return proc.stdout.decode("utf-8", "replace")'),),
           frozenset({"F2"})),
    Mutant("decode-swallow-empty", "defense",
           "(a)+(b) UnicodeDecodeError swallowed into empty git output",
           (('raise EvalError(f"git {\' \'.join(args)} in {repo}: output not UTF-8"\n'
             '                        ) from exc',
             'return ""'),),
           frozenset({"F2"})),
    Mutant("drop-logoutputencoding-override", "defense",
           "(a) lane i18n.logOutputEncoding=ISO-8859-1 with a non-ASCII subject reaches strict decode",
           (('"-c", "i18n.logOutputEncoding=UTF-8",\n    ', ""),),
           frozenset({"F1"})),
    Mutant("drop-log-follow-override", "defense",
           "fleet log.follow=true moves the report cutoff behind a rename",
           (('"-c", "log.follow=false",\n', ""),),
           frozenset({"F6"})),
    Mutant("refusal-exit-clean", "defense",
           "refusal exit 2 rewritten to exit 0: an error becomes a clean verdict",
           ((REFUSAL, REFUSAL.replace("return 2", "return 0")),),
           frozenset({"F2", "F13"})),
    Mutant("refusal-exit-failed", "defense",
           "refusal exit 2 rewritten to exit 1: an error becomes a failed verdict",
           ((REFUSAL, REFUSAL.replace("return 2", "return 1")),),
           frozenset({"F2", "F13"})),
    Mutant("probe-drop-config-isolation", "probe",
           "git_env drops GIT_CONFIG_GLOBAL and GIT_CONFIG_NOSYSTEM (grid already isolates its child env)",
           (('env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",',
             "env.update("),),
           frozenset()),
    Mutant("probe-lane-log-swallow", "probe",
           "round_commits swallows EvalError from the lane git log into zero commits",
           (('out = git(lane_repo, "log", f"--format=%H{SEP}%an{SEP}%at{SEP}%s{END}",\n'
             '              branch)',
             'try:\n'
             '        out = git(lane_repo, "log", f"--format=%H{SEP}%an{SEP}%at{SEP}%s{END}",\n'
             '                  branch)\n'
             '    except EvalError:\n'
             '        out = ""'),),
           frozenset()),
    Mutant("probe-replace-argv-only", "probe",
           "only the argv --no-replace-objects removed; the env channel remains",
           (NO_REPLACE_ARGV,), frozenset()),
    Mutant("probe-replace-env-only", "probe",
           "only GIT_NO_REPLACE_OBJECTS removed from the env; the argv channel remains",
           (NO_REPLACE_ENV,), frozenset()),
    Mutant("probe-lazy-argv-only", "probe",
           "only the argv --no-lazy-fetch removed; the env channel remains",
           (NO_LAZY_ARGV,), frozenset()),
    Mutant("probe-lazy-env-only", "probe",
           "only GIT_NO_LAZY_FETCH removed from the env; the argv channel remains",
           (NO_LAZY_ENV,), frozenset()),
)


class GridError(Exception):
    """The grid could not evaluate; never a verdict about the candidate."""


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_grid(grid, auditor, timeout):
    try:
        proc = subprocess.run(
            [sys.executable, str(grid), "--arm", "current", "--current",
             str(auditor), "--json"],
            capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise GridError(f"grid timed out after {timeout}s on {auditor}") from exc
    if proc.returncode not in (0, 1):
        tail = proc.stderr.decode("utf-8", "replace").strip()[-400:]
        raise GridError(f"grid rc={proc.returncode} on {auditor}: {tail}")
    try:
        doc = json.loads(proc.stdout.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise GridError(f"grid stdout is not JSON on {auditor}: {exc}") from exc
    if doc.get("mode") != "current" or not isinstance(doc.get("rows"), list):
        raise GridError(f"grid JSON schema unexpected on {auditor}")
    return doc


def short(case):
    return case.split("-", 1)[0]


def failing(doc):
    """{short id: observed obs} for graded rows whose current expectation is unmet."""
    return {short(row["case"]): row for row in doc["rows"]
            if row["kind"] in GRADED and row["ok"]["current"] is not True}


def fmt_obs(obs):
    flags = [name for name, on in (("TB", obs["traceback"]),
                                   ("MARKER", obs["marker"]),
                                   ("TIMEOUT", obs["timed_out"])) if on]
    kinds = "-" if obs["defects"] is None else (",".join(obs["defects"]) or "none")
    tag = f"[{','.join(flags)}]" if flags else ""
    return f"{obs['verdict']}/{obs['exit']}{tag}({kinds})"


def fmt_expect(expect):
    if expect is None:
        return "-"
    kinds = "any" if expect["kinds"] is None else (",".join(expect["kinds"]) or "none")
    return f"exit={expect['exit']} kinds={kinds}"


def apply(source, mutant):
    """-> (text, status, detail); status is 'ok', 'NOT-APPLIED' or 'INVALID'."""
    text = source
    for old, new in mutant.edits:
        hits = text.count(old)
        if hits != 1:
            return None, "NOT-APPLIED", f"anchor found {hits}x: {old[:70]!r}"
        text = text.replace(old, new, 1)
    if text == source:
        return None, "NOT-APPLIED", "no change"
    try:
        compile(text, mutant.name, "exec")
    except SyntaxError as exc:
        return None, "INVALID", f"syntax error line {exc.lineno}: {exc.msg}"
    return text, "ok", ""


def list_mutants():
    for m in MUTANTS:
        print(f"{m.name:<32} {m.group:<8} {m.fault}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Differential mutation runner for the round-23 repo-state grid.")
    ap.add_argument("--auditor", help="candidate tools/report-landing-audit.py")
    ap.add_argument("--grid", type=Path, default=GRID,
                    help="grid script (default: out/GridHarness/repo-state-grid.py)")
    ap.add_argument("--jobs", type=int, default=4, help="concurrent grid runs")
    ap.add_argument("--timeout", type=int, default=GRID_TIMEOUT_S,
                    help="per grid run, seconds")
    ap.add_argument("--keep", type=Path,
                    help="keep mutant sources and grid JSON in this directory")
    ap.add_argument("--accept-baseline", default="", metavar="IDS",
                    help="comma list of graded rows the pristine may fail; must match exactly")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--list", action="store_true", help="list mutants and exit")
    args = ap.parse_args(argv)
    if args.list:
        return list_mutants()
    if not args.auditor:
        ap.error("--auditor is required")
    auditor = Path(args.auditor).resolve()
    grid = args.grid.resolve()
    for label, path in (("auditor", auditor), ("grid", grid)):
        if not path.is_file():
            ap.error(f"{label} is not a file: {path}")

    source = auditor.read_text(encoding="utf-8")
    work = (args.keep or Path(tempfile.mkdtemp(prefix="kama-r23-mutants-"))).resolve()
    work.mkdir(parents=True, exist_ok=True)
    accept = frozenset(s.strip() for s in args.accept_baseline.split(",") if s.strip())

    plans = []
    for m in MUTANTS:
        text, status, detail = apply(source, m)
        path = None
        if text is not None:
            path = work / f"{m.name}.py"
            path.write_text(text, encoding="utf-8")
        plans.append((m, path, status, detail))

    print(f"grid    {grid} sha256:{sha256(grid)[:12]}", file=sys.stderr)
    print(f"auditor {auditor} sha256:{sha256(auditor)[:12]}", file=sys.stderr)
    print(f"work    {work}", file=sys.stderr)

    jobs = [("PRISTINE", auditor)] + [(m.name, p) for m, p, _, _ in plans if p]
    print(f"running {len(jobs)} grid invocations, jobs={args.jobs}", file=sys.stderr)
    docs = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        futs = {ex.submit(run_grid, grid, path, args.timeout): name
                for name, path in jobs}
        for fut in concurrent.futures.as_completed(futs):
            name = futs[fut]
            try:
                docs[name] = fut.result()
            except GridError as exc:
                docs[name] = exc
            if args.keep and not isinstance(docs[name], GridError):
                (work / f"{name}.grid.json").write_text(
                    json.dumps(docs[name], indent=1, sort_keys=True), encoding="utf-8")
            print(f"  done {name}", file=sys.stderr)

    pristine = docs["PRISTINE"]
    if isinstance(pristine, GridError):
        print(f"grid error on pristine candidate: {pristine}", file=sys.stderr)
        return 2
    base_rows = failing(pristine)
    baseline_ok = frozenset(base_rows) == accept
    names = {short(r["case"]): r["case"] for r in pristine["rows"]}

    results = []
    for m, path, status, detail in plans:
        rec = {"name": m.name, "group": m.group, "fault": m.fault,
               "predicted": sorted(m.kills)}
        if status != "ok":
            rec.update(verdict=status, detail=detail, new=[], retained=[],
                       as_predicted=False)
            results.append(rec)
            continue
        doc = docs[m.name]
        if isinstance(doc, GridError):
            rec.update(verdict="GRID-ERROR", detail=str(doc), new=[], retained=[],
                       as_predicted=False)
            results.append(rec)
            continue
        mut_rows = failing(doc)
        new = sorted(set(mut_rows) - set(base_rows))
        retained = sorted(set(mut_rows) & set(base_rows))
        if m.group == "defense":
            killed = bool(new)
            as_predicted = bool(set(new) & m.kills)
            verdict = "KILLED" if killed else "SURVIVED"
        else:
            killed = bool(new)
            as_predicted = not killed
            verdict = "KILLED" if killed else "SURVIVED"
        rec.update(verdict=verdict, detail="", new=new, retained=retained,
                   as_predicted=as_predicted,
                   new_detail={k: {"case": names.get(k, k),
                                   "observed": fmt_obs(mut_rows[k]["observed"]["current"]),
                                   "expect": fmt_expect(mut_rows[k]["expect"])}
                               for k in new})
        results.append(rec)

    if any(r["verdict"] in ("NOT-APPLIED", "INVALID") for r in results):
        rc = 3
    elif not baseline_ok:
        rc = 2
    elif any(r["verdict"] == "GRID-ERROR" for r in results):
        rc = 2
    elif any(not r["as_predicted"] for r in results):
        rc = 1
    else:
        rc = 0

    report = {
        "grid": str(grid), "grid_sha256_12": sha256(grid)[:12],
        "population_sha256": pristine.get("population_sha256"),
        "auditor": str(auditor), "auditor_sha256_12": sha256(auditor)[:12],
        "pristine": {"failing": {k: fmt_obs(v["observed"]["current"])
                                 for k, v in sorted(base_rows.items())},
                     "accepted_baseline": sorted(accept),
                     "baseline_ok": baseline_ok,
                     "case_names": {k: names[k] for k in sorted(base_rows)}},
        "mutants": results, "exit": rc,
    }
    if args.json:
        print(json.dumps(report, indent=1, sort_keys=True))
        return rc

    print(f"pristine: {'PASS' if not base_rows else 'FAIL'}"
          f"{'' if baseline_ok else ' (not an accepted baseline)'}")
    for k in sorted(base_rows):
        print(f"  {k:<4} {names[k]:<30} {fmt_obs(base_rows[k]['observed']['current'])}"
              f"  expect {fmt_expect(base_rows[k]['expect'])}")
    print()
    print(f"{'mutant':<30} {'group':<8} {'verdict':<9} {'as-pred':<8} "
          f"{'new':<22} retained")
    for r in results:
        if r["verdict"] in ("NOT-APPLIED", "INVALID", "GRID-ERROR"):
            print(f"{r['name']:<30} {r['group']:<8} {r['verdict']:<9} "
                  f"{'no':<8} {r['detail']}")
            continue
        print(f"{r['name']:<30} {r['group']:<8} {r['verdict']:<9} "
              f"{'yes' if r['as_predicted'] else 'NO':<8} "
              f"{','.join(r['new']) or '-':<22} {','.join(r['retained']) or '-'}")
        for k, d in r.get("new_detail", {}).items():
            print(f"      {k} {d['case']}: {d['observed']} (expect {d['expect']})")
    defense = [r for r in results if r["group"] == "defense"]
    probes = [r for r in results if r["group"] == "probe"]
    print(f"\nsummary: pristine={'PASS' if not base_rows else 'FAIL'} "
          f"defense killed {sum(r['verdict'] == 'KILLED' for r in defense)}/{len(defense)} "
          f"(as predicted {sum(r['as_predicted'] for r in defense)}) "
          f"probes survived {sum(r['verdict'] == 'SURVIVED' for r in probes)}/{len(probes)} "
          f"(as predicted {sum(r['as_predicted'] for r in probes)}) -> exit {rc}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
