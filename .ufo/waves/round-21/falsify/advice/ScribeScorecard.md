VERDICT: partial - round-21 scorecard numbers reproduce (C1 9 defects/selftest 32, C2 grid 0/13 vs 13/13, live receipt VALID); C1 input is a fleet working-tree read and the 9/9 hand-confirmation is relayed, not re-run.

# ScribeScorecard — round 21 scorecard draft (kama)

Attacked target: the round-21 SCORECARD section claims (C1 calibration 7→7, C2 operability 8→8), their counting commands, the measured commit `b76727f31e522763ce24e43d6ec86d21b507a11f`, evidence pointers, and the capability-table decision.

Deliverables: draft section `.ufo/waves/round-21/falsify/out/ScribeScorecard/SCORECARD-round-21.md` (new file, not yet in SCORECARD.md; the L1 integrates).

## Executed checks (my commands, observed exit)
- Stream integrity: re-hashed 56 `runs/b76727f3/*.stdout|*.stderr` against `commands.json`: mismatches 0; all 28 `as_expected` true. Recipe SHA `9d68997d…` matches `git show b76727f:.ufo/waves/round-21/recipe.json`.
- `git cat-file -e 7a6bc91…:tools/report-landing-audit.py` exit 128 (tool absent at round start, as claimed).
- `git diff --stat b76727f a661714 -- tools tests registry corpus SCORECARD.md AXES.md LOG.md SKILL.md`: empty output: no product change after the measured commit.
- `c1-audit-raw.stdout` (exit 1): defects 9 (landed-omitted 8, unresolved-full-hash 1), uncorrected 9, required_commits 42, post_report 4. `c1-audit-ledger.stdout` (exit 0): corrected 9, uncorrected 0, errata_invalid 0, errata_unmatched 0.
- `c1-audit-selftest.stdout` (exit 0): cases=32 failed=0.
- `c2-grid-frozen` (exit 1): link 0/13, subdir 0/1, regular 3/3, type 1/1, null 1/1. `c2-grid-current` (exit 0): link 13/13, subdir 1/1, regular 3/3, type 1/1, real_tree_gate_clean true. `c2-grid-both`: back_compat_install_tree_sha256_equal true.
- `c2-gate-selftest` exit 0 (11 VALID + 1 NOT-EVALUATED, 91 mutations); `c2-grid-selftest` exit 0 (13 cases); `c2-producer-selftest` exit 0.
- `live-receipt.json`: schema v3, outcome pass, 10 links, install_links_sha256 `5cb9f486…6470060`. `c2-live-gate-pinned` exit 0 VALID; wrong links pin exit 1 INVALID.
- Legacy R18 receipts 1–3 exit 0 VALID; receipt-1 with `--require-install-links` exit 1 INVALID.
- `sources-census` / `validate` exit 0; rows 65→74 (A 62→70, B 0→1, C 3; mined 52→60, queued 6→7, rejected 7).
- `pgrep`-equivalent `ps aux | grep -c "[l]lama-server"` → 0 at 11:18 UTC (no live server left).
- `AXES.md` lines 27-41, 59-64, 68-70 read in the fleet root (contract quoted in the draft); `shokunin.conf:52` = operability + calibration.

## Findings
1. **Attack on C1 input snapshot (partial).** `tools/report-landing-audit.py:161,168` reads reports from `Path(fleet_repo)/rel`, the working tree, not a commit. Fleet `.ufo/reports` was clean when I checked (`git status -- .ufo/reports` empty, exit 0), but that does not prove the same at measurement time. The draft states this as a limit. Fix: pin the fleet input by commit, or record the fleet HEAD in the run output.
2. **Relayed claim (partial).** "9/9 hand-confirmed, 0 FP/FN" rests on build-seat recounts I did not re-run. The draft marks it as relayed.
3. **Capability decision: no row for C2.** Agrees with the CapabilityRuleReader ruling (`build/advice/CapabilityRuleReader.md`, VERDICT partial): hardening of `live-llamacpp-lifecycle` (SCORECARD canonical list line 628) with R17–R19 precedent, scored 8→8. Strongest counter (gate could not reject a retargeted soname link) is recorded with its rebuttal. [INFERENCE] the grid runs on a mirror copy (`install-links-grid.py:44`, `mirror()` 83-91), so it is not a real-surface probe; the operator may still rule "capability", which would need a read-only probe on the real tree.
4. **Stale advice count.** CapabilityRuleReader reports `--selftest cases=15` and "SKILL.md has no match for report-landing" at draft a29bb84. At measured commit b76727f the selftest prints cases=32 and `SKILL.md:683` (report landing audit) and `SKILL.md:684-685` (links pin, grid) exist. The draft uses the measured values; the advice's SKILL objection is resolved at the measured commit.
5. **Trend verdicts not drafted** (owned by ScribeTrends). The draft says so.

## Not verified by me
- Hand recounts of the 9 defects; C2 grid run on a fresh tree; any live server launch (none launched); outside non-author sampling.
- Axis scores other than C1/C2 (freshness 8, coverage 9, depth 7, adjacency 7) carried from round 20 without re-measurement.

## Installs / changes
- None. No tool installed or upgraded. No lane file, index, git state or fleet file modified. No scratch under /tmp created. Writes limited to `.ufo/waves/round-21/falsify/out/ScribeScorecard/` and this report (the report path was set by the assignment).

## Checks for the L1 to run once
- `python3 tools/report-landing-audit.py --rounds 10-20 --no-errata --json` (expect exit 1, defects 9) and without `--no-errata` (expect exit 0, corrected 9).
- `python3 tests/llamacpp-live/install-links-grid.py --arm both --json` (expect exit 1, combined) and `--arm current --json` (expect exit 0).
- `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-21/runs/b76727f3/live-receipt.json --require-install-links --expect-install-links-sha256 5cb9f4865c8e1315dbd1baa99310c9bc65ddcf469929488359c66587b6470060` (expect exit 0).
