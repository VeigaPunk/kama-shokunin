#!/usr/bin/env python3
"""Mutants for the CaseMissingFleetReport oracle case.

Each mutant is the BASE auditor (tools/report-landing-audit.py at
0df800e896f6bce285a81e794ad4ae1d1e6c3a71) with one small, named change.
They exist only to prove the oracle case is discriminating, i.e. that the
expected exit/findings of CaseMissingFleetReport are not produced by every
possible implementation of the round-24 promisor repair.

  M1  no-metadata-refusal
      The round-24 repair shape: the blanket promisor-metadata refusal is
      dropped and the audit proceeds.  Expected on the case: exit 2
      could-not-evaluate, because the required fleet report blob is
      genuinely unavailable.  The case must PASS this mutant.

  M2  empty-report-on-read-failure
      M1 plus: an unreadable fleet report is treated as an EMPTY report.
      Expected on the case: exit 1 with `landed-section-missing` (the
      missing blob read as a report without a Landed section).  The case
      must FAIL this mutant.

  M3  skip-unreadable-round
      M1 plus: a round whose report cannot be read is skipped.
      Expected on the case: exit 0 "clean" (guessed completeness).
      The case must FAIL this mutant.

  M4  no-lazy-fetch-isolation  (negative control for the fixture's teeth)
      M1 plus: the global `--no-lazy-fetch` isolation flag is dropped.
      Expected on the case: the auditor lazy-fetches the missing blob from
      the LOCAL file:// origin (no network), the blob materializes in the
      partial clone and the audit returns a real verdict.  The case must
      FAIL this mutant, because `blob_still_absent` then fails: that proves
      the "no lazy fetch" property of the fixture is observable rather than
      vacuous.

Usage: mutants.py --base PATH --outdir DIR
"""
from __future__ import annotations

import argparse
from pathlib import Path

DROP_PACK_REFUSAL = (
    '        if rel == "objects/pack" and path.is_dir() and any(\n'
    '                p.suffix == ".promisor" and p.with_suffix(".pack").exists()\n'
    '                for p in path.iterdir()):\n'
    '            raise EvalError(f"{repo}: partial clone (promisor pack)")\n'
)

DROP_CONFIG_REFUSAL = (
    '        if key == "extensions.partialclone" or (\n'
    '                re.fullmatch(r"remote\\..+\\.promisor", key)\n'
    '                and git_bool(value)):\n'
    '            raise EvalError(f"{repo}: partial clone ({key})")\n'
)

EMPTY_REPORT = (
    '    else:\n'
    '        # committed fleet bytes, not a possibly edited working-tree copy\n'
    '        try:\n'
    '            text = git(fleet_repo, "show", f"HEAD:{rel}")\n'
    '        except EvalError as exc:\n'
    '            raise EvalError(f"round {rnd}: cannot read {rel} at fleet "\n'
    '                            f"HEAD: {exc}") from exc\n'
)

SKIP_ROUND = (
    '    results = [audit_round(lane_repo, fleet_repo, tip, args.lane, r,\n'
    '                           overrides.get(r), source_urls) for r in rounds]\n'
)


def apply_once(text, old, new, what):
    if text.count(old) != 1:
        raise SystemExit(f"mutant {what}: anchor not unique/found "
                         f"({text.count(old)} matches)")
    return text.replace(old, new)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()
    base = Path(args.base).read_text(encoding="utf-8")
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)

    m1 = apply_once(base, DROP_PACK_REFUSAL, "", "M1 pack refusal")
    m1 = apply_once(m1, DROP_CONFIG_REFUSAL, "        pass\n",
                    "M1 config refusal")
    (out / "mutant-M1-no-metadata-refusal.py").write_text(m1, encoding="utf-8")

    m2 = apply_once(m1, EMPTY_REPORT,
                    '    else:\n'
                    '        # MUTANT M2: an unreadable fleet report is read as\n'
                    '        # an EMPTY report (a guessed absence).\n'
                    '        try:\n'
                    '            text = git(fleet_repo, "show", f"HEAD:{rel}")\n'
                    '        except EvalError:\n'
                    '            text = ""\n',
                    "M2 empty report")
    (out / "mutant-M2-empty-report.py").write_text(m2, encoding="utf-8")

    m3 = apply_once(m1, SKIP_ROUND,
                    '    results = []\n'
                    '    for r in rounds:\n'
                    '        try:\n'
                    '            results.append(audit_round(\n'
                    '                lane_repo, fleet_repo, tip, args.lane, r,\n'
                    '                overrides.get(r), source_urls))\n'
                    '        except EvalError:\n'
                    '            continue  # MUTANT M3: skip unreadable rounds\n',
                    "M3 skip round")
    (out / "mutant-M3-skip-round.py").write_text(m3, encoding="utf-8")

    m4 = apply_once(m1,
                    'GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch",\n',
                    'GIT_ISOLATION = ("--no-replace-objects",\n',
                    "M4 lazy fetch isolation")
    (out / "mutant-M4-no-lazy-fetch.py").write_text(m4, encoding="utf-8")

    for name in ("mutant-M1-no-metadata-refusal.py", "mutant-M2-empty-report.py",
                 "mutant-M3-skip-round.py", "mutant-M4-no-lazy-fetch.py"):
        print(f"wrote {out / name}")


if __name__ == "__main__":
    main()
