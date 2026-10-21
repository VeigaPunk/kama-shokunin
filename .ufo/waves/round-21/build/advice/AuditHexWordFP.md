VERDICT: confirm - five non-commit lookalikes produce landed-unresolved findings

Axes: detection precision (avoid false positives), citation recall (retain real abbreviated and full OIDs), scope (no edits to the canonical lane).

Fixture and observed result
- Scratch clone command (exit 0): `mkdir -p /tmp/kama-r21-AuditHexWordFP && git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r21-AuditHexWordFP/lane && git -C /tmp/kama-r21-AuditHexWordFP/lane checkout -q a29bb84abbb8b4d328f5970a89e448330a3a42ac && git -C /tmp/kama-r21-AuditHexWordFP/lane rev-parse HEAD`; stdout was `a29bb84abbb8b4d328f5970a89e448330a3a42ac`.
- Fixture setup commands, each exit 0 with empty stdout/stderr:
  - `git init -q -b master /tmp/kama-r21-AuditHexWordFP/fixture-lane`
  - `git init -q -b master /tmp/kama-r21-AuditHexWordFP/fixture-fleet`
  - `git -C /tmp/kama-r21-AuditHexWordFP/fixture-lane add seed.txt`
  - `git -C /tmp/kama-r21-AuditHexWordFP/fixture-fleet add seed.txt`
  - `git -C /tmp/kama-r21-AuditHexWordFP/fixture-lane commit -q -m 'fixture seed'`
  - `git -C /tmp/kama-r21-AuditHexWordFP/fixture-fleet commit -q -m 'fixture seed'`
- Audit command (exit 1): `python3 /tmp/kama-r21-AuditHexWordFP/lane/tools/report-landing-audit.py --lane-repo /tmp/kama-r21-AuditHexWordFP/fixture-lane --fleet-repo /tmp/kama-r21-AuditHexWordFP/fixture-fleet --branch master --lane kama --rounds 1 --report 1=/tmp/kama-r21-AuditHexWordFP/fixture-report.md --no-errata --json`.
- Exact audit stdout summary: `landed-unresolved=5`, `unresolved-full-hash=0`, `landed-omitted=0`, `landed-section-missing=0`, `uncorrected=5`, `status=failed`; stderr empty. Tokens: `1234567`, `ab51c80f`, `acceded`, `defaced`, `facade1`. No other defect kinds were returned.
- The same input contained `PR #12345` and ISO date `2026-10-21`; neither was flagged. `PR #1234567` was flagged as token `1234567`.

Proposal
- `out/AuditHexWordFP/report-landing-audit.patch` is a unified diff generated from the scratch clone at the specified base commit. Generation command (exit 0): `git -C /tmp/kama-r21-AuditHexWordFP/lane -c diff.mnemonicPrefix=false diff --src-prefix=a/ --dst-prefix=b/ -- tools/report-landing-audit.py`. It keeps bare 40-hex OIDs, recognizes shorter OIDs only as exact inline-code tokens, updates the existing short-citation selftest fixtures, and adds a false-positive regression fixture for these words, the ellipsized prefix, PR number, and date. The patch was not applied to the canonical lane; no lane files were edited.
- This matches observed Kama report style: r10 short citation is inline code (`.ufo/reports/round-10/kama.md:30`); r16/r17 short citations are inline code (`round-16/kama.md:78`, `round-17/kama.md:50`); r20 full OIDs are bare (`round-20/kama.md:15-19`).
- Risk: plain, unformatted abbreviated commit IDs would cease to count as citations (full 40-character OIDs remain supported). Backticked all-hex prose remains inherently ambiguous. The proposal's selftest case was not run; no build, lint, or test suite was run.

Files written: `.ufo/waves/round-21/build/advice/AuditHexWordFP.md`; `.ufo/waves/round-21/build/out/AuditHexWordFP/report-landing-audit.patch`. No tool was installed.