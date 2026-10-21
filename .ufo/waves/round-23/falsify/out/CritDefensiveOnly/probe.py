#!/usr/bin/env python3
"""CritDefensiveOnly probe: candidate faults for surviving mutants M02
(--no-lazy-fetch) and M20 (40-hex %H shape), graded with the grid's own
run_case criteria against pristine and mutant auditors.

Usage: probe.py CLONE   (CLONE = /tmp/kama-r23w2/CritDefensiveOnly at 245a37f6)
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

CLONE = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location(
    "grid", CLONE / "tests/report-audit/repo-state-grid.py")
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)
mspec = importlib.util.spec_from_file_location(
    "mut", CLONE / "tests/report-audit/isolation-mutants.py")
mut = importlib.util.module_from_spec(mspec)
mspec.loader.exec_module(mut)
g, env, pair, commit, publish, report, require = (
    grid.g, grid.env, grid.pair, grid.commit, grid.publish, grid.report,
    grid.require)
FAKE2 = "abcdefabcdefabcdefabcdefabcdefabcdefabcd"


def _filter_only(tmp, side):
    """Promisor remote created by remote.<name>.partialclonefilter alone:
    no remote.*.promisor, no extensions.partialclone, no .promisor pack."""
    lane, fleet = pair(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    publish(fleet, report([lc, FAKE2]))
    repo = lane if side == "lane" else fleet
    marker = Path(tmp, "lazy-fetch-ran")
    for k, v in (("remote.evil.url", "ssh://example.invalid/x.git"),
                 ("remote.evil.partialCloneFilter", "blob:none"),
                 ("core.sshCommand", f"touch {marker}; false")):
        g(repo, "config", k, v)
    names = g(repo, "config", "--list", "--name-only").split("\n")
    require(not any(n == "extensions.partialclone" or
                    (n.startswith("remote.") and n.endswith(".promisor"))
                    for n in names), "a refused promisor key is present")
    require(not list(Path(repo, ".git/objects/pack").glob("*.promisor")),
            "promisor pack present")
    subprocess.run(["git", "-C", str(repo), "cat-file", "-e", FAKE2],
                   capture_output=True, env=env())
    require(marker.exists(), "lazy fetch did not run the configured command")
    marker.unlink()
    return lane, fleet, [], marker


def p_filter_only_lane(tmp):
    return _filter_only(tmp, "lane")


def p_filter_only_fleet(tmp):
    return _filter_only(tmp, "fleet")


CASES = [
    # graded as the grid grades F06: no execution, no traceback, no timeout;
    # exit 1 + kinds is what the pristine tool is expected to return (it
    # does not refuse, but it must not run the program)
    ("P01-partialclonefilter-only-lane", "fault", p_filter_only_lane, 1,
     ["landed-unresolved", "unresolved-full-hash"]),
    ("P02-partialclonefilter-only-fleet", "fault", p_filter_only_fleet, 1,
     ["landed-unresolved", "unresolved-full-hash"]),
]


F09 = [c for c in grid.CASES if c[0] == "F09-signature-program"]


def mutant(tmp, *names):
    source = (CLONE / "tools/report-landing-audit.py").read_text()
    for name in names:
        (_, old, new), = [m for m in mut.MUTANTS if m[0] == name]
        assert source.count(old) == 1, name
        source = source.replace(old, new)
    path = Path(tmp, "+".join(names) + ".py")
    path.write_text(source)
    return path


def main():
    out = []
    with tempfile.TemporaryDirectory(prefix="critdef-") as root:
        arms = {"pristine": (CLONE / "tools/report-landing-audit.py", CASES),
                "M02": (mutant(root, "M02-lazy-fetch"), CASES),
                "M20": (mutant(root, "M20-log-sha-shape"), CASES),
                "M06": (mutant(root, "M06-log-signature"), F09),
                "M06+M20": (mutant(root, "M06-log-signature",
                                   "M20-log-sha-shape"), F09)}
        for arm, (auditor, cases) in arms.items():
            for i, case in enumerate(cases):
                tmp = Path(root, arm, f"{i:02d}")
                tmp.mkdir(parents=True)
                row = grid.run_case(auditor, case, tmp)
                row["arm"] = arm
                out.append(row)
    for r in out:
        print(f"{r['arm']} {r['case']} exit={r['exit']} kinds={r['kinds']} "
              f"tb={int(r['traceback'])} exec={int(r['executed'])} "
              f"timeout={int(r['timed_out'])} "
              f"{'met' if r['met'] else 'NOT-MET'} :: {r['stderr_tail'][-120:]!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
