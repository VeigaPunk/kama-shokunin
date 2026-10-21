VERDICT: confirm - C1 audit strictly complements fleet checks; no automated fleet tool checks commit hashes or Landed enumeration

## Evidence: Fleet Report Checks vs C1 Audit
- **Automated fleet checks do NOT parse commits or Landed enumeration:**
  - `scripts/shokunin-watchdog.sh:144-162` (`report_of`): checks `[ -f "$f" ]`, byte floor (`wc -c >= MIN_REPORT_BYTES`, 400B), SHONEN regex (`^[#*-]+.*SHONEN`), and content digest != baseline.
  - `scripts/hyaku/inline.sh:110-125` (`verify`): delegates to `report_of`, sweeps uncommitted report into fleet git (`git status --porcelain`), and verifies lane `ahead == 0`.
  - `scripts/hyaku/append-closure.py:54-55`: checks `os.path.isfile(report)` on "ok" closure entries.
- **Non-author closure review is manual/retrospective, not automated:**
  - `scripts/hyaku/closure-prompt.md:20-29` §1: prompts human/LLM reviewer that "every cited lane commit exists and git -C {{LANE_CWD}} merge-base --is-ancestor <hash> <branch> holds".
  - `templates/round-prompt.md:107-108` §4: contract requires "every change tied to a LOG.md entry and to the commit hash that carries it", but fleet tools enforce no commit-level checks.
  - `MANIFEST.json:10112-10116` (kama r20 closure): reviewer spotted line 7 invalid hash and 4 omitted commits retrospectively in notes, routed as status-neutral defects.
- **Kama C1 audit complements all fleet checks:**
  - `tools/report-landing-audit.py` mechanically scans all 40-hex tokens (`unresolved-full-hash`), `## Landed changes` tokens (`landed-unresolved`), and verifies lane branch commits against citations (`landed-omitted`).
  - `registry/report-landing-errata.tsv` provides an append-only ledger for historical defects without violating fleet immutable-report rules (`lane-addendum.md:234-239`).
  - Executed: `python3 tools/report-landing-audit.py --selftest` (exit 0, 15 cases); `--no-errata` (exit 1, 9 uncorrected defects); default (exit 0, 9 corrected, 0 uncorrected).

## Affected Axes
- **Calibration (7 -> 7/8)**: turns informal/post-hoc closure verifier notes into a deterministic, fail-closed pre-landing invariant.
- **Operability (8 -> 8)**: zero friction or regression on existing git/jj workflows; complements rather than duplicates.

## Proposed Move: Ancestry-Gated Pre-Landing Audit Invariant
1. **Ancestry check in C1 audit**: Extend `is_object(repos, token, "commit")` for `landed-unresolved` to also verify `git merge-base --is-ancestor <token> <branch>` in the lane repo. This closes the gap where a commit exists in local git objects (e.g. detached HEAD or abandoned branch) but is not an ancestor of `branch`, directly enforcing `closure-prompt.md:22`.
2. **Pre-landing draft harness**: In the round-21 final integration runner, execute `python3 tools/report-landing-audit.py --report 21=<draft_report>` before the fleet commit. By default (`--rounds 10-20`), passing `--report 21=...` automatically audits rounds 10-21, verifying the 9 historical errata match and round 21 is defect-free before landing.

## Risks
- Uncommitted draft timing: auditing with `--report 21` before making the round-21 lane commits triggers `landed-unresolved` on cited hashes; the round commits must be committed to the lane branch first [INFERENCE].
- Partial rounds trap: running `--rounds 21-21 --report 21=...` causes `errata-unmatched` failure because historical errata rows are unconsumed. Must rely on default `--rounds 10-20` union with `--report 21`.

## Verification (Executed)
- `python3 tools/report-landing-audit.py --selftest` -> exit 0 (`selftest cases=15 failed=0`).
- `python3 tools/report-landing-audit.py --no-errata` -> exit 1 (`uncorrected=9 status=failed`).
- `python3 tools/report-landing-audit.py` -> exit 0 (`uncorrected=0 status=clean`).
- Draft audit test: `python3 tools/report-landing-audit.py --report 21=<tmp>` with `a29bb84` -> exit 0; with omitted `a29bb84` -> exit 1 (`UNCORRECTED landed-omitted`); with bad hash -> exit 1 (`UNCORRECTED unresolved-full-hash`).
- Ancestry check: verified all cited tokens across rounds 10-20 reports are `merge-base --is-ancestor` of master -> exit 0.

Artifact: `.ufo/waves/round-21/build/out/ConnectorFleetReportChecks/fleet-report-checks-matrix.json`
Report: `.ufo/waves/round-21/build/advice/ConnectorFleetReportChecks.md`
Tool installs: none.
