#!/usr/bin/env python3
"""AuditReport17 blind-spot harness for tools/report-landing-audit.py.

Control: the committed round-17 report through the tool's default paths.
Mutants: copies of that report with one edit each, audited with
`--report 17=COPY` (an uncommitted draft; cutoff is the current time, which
still makes the two lane commits required). Writes only to a temporary
directory. Expectations encode the results observed in AuditReport17: the
`clean` rows are blind spots of the tool, the others are caught.

Usage: python3 mutants-r17.py      Exit: 0 all cases as expected, 1 otherwise.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile

FLEET = pathlib.Path("/home/vgpnk/Projects/shokunin")
LANE = FLEET / "kama-shokunin"
TOOL = LANE / "tools" / "report-landing-audit.py"
REPORT = FLEET / ".ufo" / "reports" / "round-17" / "kama.md"

S5E = "5e9ae6e93dce529a48229647e482f18a291463cd"
ROW50 = ("| check.py grading, fault-controls.py, mutants.py, runs/ | "
         "§round 17 — graded fields and fail-capable live checks | `54a29268` |")
ROW54 = ("| falsify wave evidence (spec, dispatch, validation, provenance, 73 reports, summary) | "
         "§round 17 — falsify wave and corrections | `5e9ae6e9` |")
ROW55 = ("| S047 supersedes S043; SKILL/knowledge/AGENTS corrections; lesson §Falsify wave; "
         "SCORECARD falsify verdicts | same | `5e9ae6e9` |")


def once(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, old[:60]
    return text.replace(old, new, 1)


def cite_54_55(text: str, token: str) -> str:
    text = once(text, ROW54, ROW54.replace("`5e9ae6e9`", token))
    return once(text, ROW55, ROW55.replace("`5e9ae6e9`", token))


def audit(path: pathlib.Path) -> tuple[int, dict | None, str]:
    proc = subprocess.run(
        [sys.executable, str(TOOL), "--rounds", "17", "--no-errata", "--json",
         "--report", f"17={path}"],
        capture_output=True, text=True)
    doc = json.loads(proc.stdout) if proc.stdout.strip() else None
    return proc.returncode, doc, proc.stderr.strip()


def main() -> int:
    failures = 0
    base = REPORT.read_text(encoding="utf-8")

    control = subprocess.run(
        [sys.executable, str(TOOL), "--rounds", "17", "--no-errata", "--json"],
        capture_output=True, text=True)
    doc = json.loads(control.stdout)
    res = doc["results"][0]
    ok = (control.returncode == 0 and res["defects"] == [] and res["required"] == 2
          and not res["post_report"])
    failures += not ok
    print(f"{'ok  ' if ok else 'FAIL'} committed-report rc={control.returncode} "
          f"required={res['required']} post_report={len(res['post_report'])} "
          f"defects={len(res['defects'])}")

    # (name, mutated text, expected (kind, token) pairs, exact-match flag)
    cases = [
        ("M1-landed-cites-round16-kama-commit",
         once(base, ROW50, ROW50.replace("`54a29268`", "`ccc4bb31`")), [], True),
        ("M1b-landed-cites-protocol-commit",
         once(base, ROW50, ROW50.replace("`54a29268`", "`cff9e62`")), [], True),
        ("M2-fullhash-replaced-by-blob-id",
         once(base, S5E, "ce45ea8e53ee75d558615eeb4327faa2ed286a03"), [], True),
        ("M3-fullhash-nonexistent",
         once(base, S5E, S5E[:-1] + "e"),
         [("unresolved-full-hash", S5E[:-1] + "e")], True),
        ("M4-landed-cites-offmaster-jj-object",
         once(base, ROW50, ROW50.replace("`54a29268`", "`896956536a`")), [], True),
        ("M5-nonexistent-short-outside-landed",
         once(base, "`--from 54a2926 --to 5e9ae6e`", "`--from deadbee1 --to 5e9ae6e`"), [], True),
        ("M6-landed-drops-5e9ae6e9-citations",
         cite_54_55(base, "`none`"), [("landed-omitted", S5E)], True),
        ("M7-landed-uppercase-citations",
         cite_54_55(base, "`5E9AE6E9`"), [("landed-omitted", S5E)], True),
        ("M8-landed-nonexistent-prefix",
         once(base, ROW54, ROW54.replace("`5e9ae6e9`", "`5e9ae6e0`")),
         [("landed-unresolved", "5e9ae6e0")], True),
        ("M9-landed-heading-renamed",
         once(base, "## Landed changes", "## Landed change"),
         [("landed-section-missing", "-")], False),
    ]

    with tempfile.TemporaryDirectory(prefix="kama-r21-AuditReport17-") as tmp:
        for name, text, want, exact in cases:
            path = pathlib.Path(tmp, name + ".md")
            path.write_text(text, encoding="utf-8")
            rc, doc, err = audit(path)
            if doc is None:
                failures += 1
                print(f"FAIL {name} rc={rc} stderr={err[:160]}")
                continue
            res = doc["results"][0]
            got = [(d["kind"], d["token"]) for d in res["defects"]]
            ok = all(w in got for w in want) and (not exact or sorted(got) == sorted(want))
            failures += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {name} rc={rc} required={res['required']} "
                  f"defects={got}")

    print(f"cases={len(cases) + 1} failures={failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
