#!/usr/bin/env python3
"""Mutation check for the round-23 isolation elements of
tools/report-landing-audit.py against tests/report-audit/repo-state-grid.py.

Each mutant removes or weakens exactly one element (one literal source
replacement that must match exactly once). A mutant is killed only when the
grid's current arm reports a violation (exit 1); a grid that cannot
evaluate (exit 2, e.g. a fixture premise or disk failure) kills nothing and
stops the run. Pristine must pass. Elements whose mutant survives are
reported as defensive-only: the grid has no fault they are necessary for.

Exit: 0 pristine passed and every mutant ran (killed or surviving, as
listed); 2 could not evaluate (pristine failed, a replacement did not match
exactly once, or the grid could not evaluate a mutant).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

LANE = Path(__file__).resolve().parents[2]
AUDIT = LANE / "tools/report-landing-audit.py"
GRID = LANE / "tests/report-audit/repo-state-grid.py"

MUTANTS = [
    ("M01-replace-objects", '"--no-replace-objects", ', ""),
    ("M02-lazy-fetch", '"--no-lazy-fetch",\n', "\n"),
    ("M03-log-encoding", '"-c", "i18n.logOutputEncoding=UTF-8",\n', "\n"),
    ("M04-log-follow", '"-c", "log.follow=false", ', ""),
    ("M05-log-showroot", ', "-c", "log.showRoot=true"', ""),
    ("M06-log-signature", '"-c", "log.showSignature=false", ', ""),
    ("M07-log-mailmap", ', "-c", "log.mailmap=false"', ""),
    ("M09-strict-default", 'env=None, errors="strict"', 'env=None, errors="replace"'),
    ("M10-log-surrogates",
     'branch, errors="surrogateescape"', 'branch'),
    ("M11-listing-surrogates",
     '"--", ".ufo/reports", errors="surrogateescape"', '"--", ".ufo/reports"'),
    ("M12-shallow-check",
     'raise EvalError(f"{repo}: shallow repository")', 'pass'),
    ("M13-grafts-check",
     'raise EvalError(f"{repo}: {path} rewrites history")', 'pass'),
    ("M14-promisor-config",
     'raise EvalError(f"{repo}: partial clone ({key})")', 'pass'),
    ("M15-object-format",
     'raise EvalError(f"{repo}: object format {fmt!r}, not sha1")', 'pass'),
    ("M16-top-level",
     'raise EvalError(f"{repo}: not a repository top level")', 'pass'),
    ("M17-ref-shadow",
     'raise EvalError(f"{repo}: citation {token} names a ref")', 'pass'),
    ("M18-branch-heads",
     'if git(lane_repo, "for-each-ref", "--format=%(refname)", head).strip():',
     'if False:'),
    ("M19-errata-hex",
     '\n             and re.fullmatch(r"[0-9a-fA-F]{7,40}", e["correction"])}',
     '}'),
    ("M20-log-sha-shape",
     'if not re.fullmatch(r"[0-9a-f]{40}", sha):', 'if False:'),
    ("M21-newlines", 'return out.replace("\\r\\n", "\\n").replace("\\r", "\\n")',
     'return out'),
    ("M22-promisor-pack",
     'raise EvalError(f"{repo}: partial clone (promisor pack)")', 'pass'),
    ("M23-strict-decode-catch",
     'out = proc.stdout.decode("utf-8", errors)',
     'out = proc.stdout.decode("utf-8", "replace")'),
    ("M24-catch-all", "except Exception as exc:  # an unanticipated error "
     "is never a verdict", "except ZeroDivisionError as exc:"),
    ("M25-timestamp-shape", 're.fullmatch(r"[0-9]{1,18}", atime)',
     're.fullmatch(r"[0-9]+", atime)'),
    ("M26-record-separators", 'fields = out.split("\\0")',
     'fields = re.split("[\\0\\x1e\\x1f]", out)'),
    ("M27-promisor-boolean", '\n                and git_bool(value)):', '):'),
    ("M28-correction-casefold", 'e["correction"].lower() for e in errata',
     'e["correction"] for e in errata'),
    ("M29-promisor-pack-pairing",
     ' and p.with_suffix(".pack").exists()', ''),
    ("M30-fleet-history-check", 'for repo in (lane_repo, fleet_repo):',
     'for repo in (lane_repo,):'),
    ("M31-git-timeout", ',\n                              timeout=GIT_TIMEOUT)', ')'),
    ("M32-grafts-content",
     'return any(line.strip() and not line.startswith(b"#")',
     'return True or any(line.strip() and not line.startswith(b"#")'),
]


def grid(auditor):
    p = subprocess.run([sys.executable, str(GRID), "--arm", "current",
                        "--current", str(auditor), "--json"],
                       capture_output=True)
    if p.returncode == 2:
        return 2, None, p.stderr.decode(errors="replace").strip()[-300:]
    doc = json.loads(p.stdout)
    arm = doc["arms"]["current"]
    failed = [r["case"] for r in arm["rows"]
              if r["kind"] in ("fault", "contract", "control")
              and not r["met"]]
    return p.returncode, failed, None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--only", action="append")
    args = ap.parse_args(argv)
    source = AUDIT.read_text(encoding="utf-8")
    rc, failed, err = grid(AUDIT)
    if rc != 0:
        print(f"could-not-evaluate: pristine grid rc={rc} {failed} {err}",
              file=sys.stderr)
        return 2
    rows = []
    with tempfile.TemporaryDirectory(prefix="isolation-mutants-") as tmp:
        for name, old, new in MUTANTS:
            if args.only and name not in args.only:
                continue
            if source.count(old) != 1:
                print(f"could-not-evaluate: {name}: pattern matches "
                      f"{source.count(old)} times", file=sys.stderr)
                return 2
            path = Path(tmp, f"{name}.py")
            path.write_text(source.replace(old, new), encoding="utf-8")
            rc, failed, err = grid(path)
            if rc == 2:  # a grid that cannot evaluate kills nothing
                print(f"could-not-evaluate: {name}: grid exit 2: {err}",
                      file=sys.stderr)
                return 2
            rows.append({"mutant": name, "grid_exit": rc,
                         "killed": rc == 1, "failed_rows": failed,
                         "error": err})
    doc = {"pristine": "passed", "mutants": len(rows),
           "killed": sum(r["killed"] for r in rows),
           "surviving": [r["mutant"] for r in rows if not r["killed"]],
           "rows": rows}
    if args.json:
        print(json.dumps(doc, indent=1, sort_keys=True))
    else:
        for r in rows:
            print(f"{r['mutant']} {'KILLED' if r['killed'] else 'survived'} "
                  f"grid={r['grid_exit']} rows={r['failed_rows']}")
        print(f"mutants={doc['mutants']} killed={doc['killed']} "
              f"surviving={doc['surviving']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
