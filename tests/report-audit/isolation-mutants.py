#!/usr/bin/env python3
"""Mutation check for the round-23 isolation elements of
tools/report-landing-audit.py against tests/report-audit/repo-state-grid.py.

Each mutant removes or weakens exactly one element (one literal source
replacement that must match exactly once). A mutant is killed only when the
grid's current arm reports a violation (exit 1); a grid that cannot
evaluate (exit 2, e.g. a fixture premise or disk failure) kills nothing.
Pristine must pass. Surviving mutants are reported without a necessity
claim; survival alone does not establish defensive-only status.

Round 24 migration (the promisor repair removed the metadata classifier):

* the four metadata-classifier mutants M14, M22, M27 and M29 are RETIRED.
  Their literals are gone from the auditor by design, so their mutants can
  never be applied again. The ids are retired, never reused and never
  replaced by a placeholder; the semantic checks they carried are now
  carried by the round-24 promisor mutants in
  tests/report-audit/promisor-mutants.py (see RETIRED below for the
  explicit attribution).
* the fail-fast rule is kept unchanged: a replacement that does not match
  exactly once, or a grid that cannot evaluate a mutant, is
  could-not-evaluate for the whole run (exit 2) and kills nothing. The
  registered exit contract (0 = pristine passed and every mutant ran;
  2 = could not evaluate) is unchanged.

Round 25 re-anchor (the round-24 auditor drifted from two literals):

* M11 keeps its element; its literal now spans the wrapped call.
* M17 keeps its round-23 element, the peel-guarded check in lookup(); the
  same refusal also exists in bare_objects() since round 24, and that second
  call site is the new mutant M33. No id is reused or retired.

Exit: 0 pristine passed and every mutant ran (killed or surviving, as
listed); 2 could not evaluate (pristine failed, a replacement did not match
exactly once, or the grid could not evaluate a mutant). The exit contract
of the registered round-23 CLI is unchanged.
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
    # round 25: the call now wraps before errors=; the element (surrogate-
    # escape decoding of the fleet report listing) is unchanged
    ("M11-listing-surrogates",
     '"--", ".ufo/reports",\n                             errors="surrogateescape"',
     '"--", ".ufo/reports"'),
    ("M12-shallow-check",
     'raise EvalError(f"{repo}: shallow repository")', 'pass'),
    ("M13-grafts-check",
     'raise EvalError(f"{repo}: {path} rewrites history")', 'pass'),
    ("M15-object-format",
     'raise EvalError(f"{repo}: object format {fmt!r}, not sha1")', 'pass'),
    ("M16-top-level",
     'raise EvalError(f"{repo}: not a repository top level")', 'pass'),
    # round 24: the auditor names the store, not the repository, in this
    # message; the element (a ref-named citation is refused) is unchanged.
    # round 25: the message now occurs at two call sites. M17 keeps the
    # round-23 site, the peel-guarded check in lookup(); the second site,
    # added in round 24 to bare_objects(), is the new mutant M33.
    ("M17-ref-shadow",
     'if not peel and not parts[0].startswith(token):\n'
     '                # git resolved a same-named ref before the object prefix\n'
     '                raise EvalError(f"{store.path}: citation {token} names a ref")',
     'if not peel and not parts[0].startswith(token):\n'
     '                # git resolved a same-named ref before the object prefix\n'
     '                pass'),
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
    ("M23-strict-decode-catch",
     'out = proc.stdout.decode("utf-8", errors)',
     'out = proc.stdout.decode("utf-8", "replace")'),
    ("M24-catch-all", "except Exception as exc:  # an unanticipated error "
     "is never a verdict", "except ZeroDivisionError as exc:"),
    ("M25-timestamp-shape", 're.fullmatch(r"[0-9]{1,18}", atime)',
     're.fullmatch(r"[0-9]+", atime)'),
    ("M26-record-separators", 'fields = out.split("\\0")',
     'fields = re.split("[\\0\\x1e\\x1f]", out)'),
    ("M28-correction-casefold", 'e["correction"].lower() for e in errata',
     'e["correction"] for e in errata'),
    ("M30-fleet-history-check", 'for repo in (lane_repo, fleet_repo):',
     'for repo in (lane_repo,):'),
    ("M31-git-timeout", ',\n                              timeout=GIT_TIMEOUT)', ')'),
    ("M32-grafts-content",
     'return any(line.strip() and not line.startswith(b"#")',
     'return True or any(line.strip() and not line.startswith(b"#")'),
    # round 25: second call site of the M17 element (see M17); new id, the
    # same weakening (the ref-named citation is no longer refused)
    ("M33-ref-shadow-bare-objects",
     'if not parts[0].startswith(token):\n'
     '                # git resolved a same-named ref before the object prefix\n'
     '                raise EvalError(f"{store.path}: citation {token} names a ref")',
     'if not parts[0].startswith(token):\n'
     '                # git resolved a same-named ref before the object prefix\n'
     '                pass'),
]


# Round 24: the metadata-classifier mutants are retired, not reused and not
# replaced by placeholders. The auditor no longer classifies promisor
# metadata, so the literals these mutants removed are gone from the
# source; the semantic checks they carried are now carried by the round-24
# promisor mutants (tests/report-audit/promisor-mutants.py), attributed
# one to one below.
RETIRED = [
    ("M14-promisor-config",
     'raise EvalError(f"{repo}: partial clone ({key})")',
     "the metadata refusal is gone from the auditor",
     "PM01-blanket-metadata-refusal: the mutant reintroduces the blanket "
     "refusal and is killed by the complete/marker/hydrated rows"),
    ("M22-promisor-pack",
     'raise EvalError(f"{repo}: partial clone (promisor pack)")',
     "the metadata refusal is gone from the auditor",
     "PM01-blanket-metadata-refusal: the same blanket refusal, reached "
     "through the paired .promisor marker"),
    ("M27-promisor-boolean",
     "and git_bool(value)",
     "no promisor boolean is classified any more",
     "PM01-blanket-metadata-refusal: a remote.*.promisor=true repository "
     "must keep the verdict of its full-clone twin"),
    ("M29-promisor-pack-pairing",
     'p.with_suffix(".pack").exists()',
     "the paired-marker classifier is gone from the auditor",
     "PM01-blanket-metadata-refusal: a paired .promisor+.pack marker alone "
     "must not refuse the repository"),
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
    # an empty selection is could-not-evaluate, and it is decided before
    # the source is read, before the pristine run and before any grid
    # call: a selector that names no mutant must not look like a pass
    selected = [name for name, _, _ in MUTANTS
                if not args.only or name in args.only]
    if args.only and not selected:
        print(f"could-not-evaluate: --only selected no mutant: "
              f"{args.only}; the ids are {', '.join(n for n, _, _ in MUTANTS)}",
              file=sys.stderr)
        return 2
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
                # fail fast: a pattern that does not apply exactly once is
                # could-not-evaluate for the whole run, and it kills
                # nothing. The exit contract of the round-23 CLI is kept.
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
           "retired": [r[0] for r in RETIRED],
           "retired_detail": [{"id": r[0], "literal": r[1], "why": r[2],
                               "replaced_by": r[3]} for r in RETIRED],
           "killed": sum(r["killed"] for r in rows),
           "surviving": [r["mutant"] for r in rows if not r["killed"]],
           "rows": rows}
    if args.json:
        print(json.dumps(doc, indent=1, sort_keys=True))
    else:
        for r in rows:
            state = "KILLED" if r["killed"] else "survived"
            print(f"{r['mutant']} {state} grid={r['grid_exit']} "
                  f"rows={r['failed_rows']}")
        print(f"mutants={doc['mutants']} killed={doc['killed']} "
              f"surviving={doc['surviving']} retired={doc['retired']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
