# SB01QualityCriterion — kama r88 w1 (calibration)

## Scope

Drafted one QUALITY criterion from lesson M3 (listing endpoint read as readiness endpoint) and one
from M1 (calibration oracle authored by the lane over its own prose), plus the round-88 `Frontier`
block for `corpus/README.md`. Read first: `plans/round-88-claims.md`, `corpus/lessons/round-88.md`,
`corpus/QUALITY.md` (all 675 lines; highest id KQ140), `corpus/README.md` frontier blocks (tail),
`corpus/knowledge/router-mode-readiness.md`, `SCORECARD.md` head and §Round 88, `corpus/SOURCES.md`
S581/S582, and the round-88 `controls/`+`measured/` receipts. Wrote only the out dir and this file.
Did not edit lane files, re-run the C1/C2 counters, send any live request, use the network, or
install/upgrade any tool (none installed or upgraded).

## Commands and outputs (true exit codes)

1. `grep -o '^| KQ[0-9]\+' corpus/QUALITY.md | sed 's/^| KQ//' | sort -n | uniq -d` → `46`; row count
   141, distinct ids 140; highest id KQ140 → next free 141. exit 0 (the pipeline ends in `uniq -d`);
   `grep -c '^| KQ'` → 141, exit 0.
2. `git diff --stat 9b4c7af1… 138a7543… -- tools/round42-selfdesc-reconcile.py tools/round41-scorecard-reconcile.py tools/round69-newest-closure-counter.py`
   → empty, exit 0 (C2 instruments byte-identical base→M).
3. `git diff --exit-code fb76e7f2… 138a7543… -- tools/round88-router-cells.py` → exit 0 (counter bytes = freeze).
4. `git log -1 --format='%h %ad %s' -- <instrument>` → round42 `bf0db9e3` 2026-10-28 (round-64),
   round41 `7be07423` 2026-11-03 (round-70), round69 `2bba0492` 2026-11-01 (round-69); all predate r88.
5. `git diff --name-status 9b4c7af1… 138a7543… -- tools/ tests/ corpus/ SCORECARD.md` → adds
   `tools/round88-router-cells.py`, `tools/fetch-pinned-model.py`, two corpus files; modifies
   `tools/kama-probe.sh`, `tools/round79-unregistered-census.py`, `corpus/SOURCES.md`, `SCORECARD.md`.
6. `git clone --shared …/kama-shokunin /fast/scratch/hyaku/kama-r88/SB01QualityCriterion/wt` +
   `checkout --detach 138a7543…` → toplevel asserted equal to the scratch dir.
7. Appended both candidate blocks in the clone, committed `356f478b` (throwaway identity, scratch only);
   `git diff --numstat 138a7543… HEAD` → `19 0 corpus/QUALITY.md`, `56 0 corpus/README.md` (zero deletions).
8. `python3 tools/append-only-audit.py --repo . --to 138a7543… --json` → exit 1 (`unrestored=91`
   pre-existing), `regressed=0 bad_disclosures=0 vanished=0 events=316`.
9. Same audit after the append → exit 1, `regressed=0 bad_disclosures=0 vanished=0 events=316`;
   only delta `commits 790→791`. The appends add no event and shift no existing line.
10. `grep -c 138a7543 SCORECARD.md` → 0; `grep -rn '1234' .ufo/waves/round-88/` → only
    `controls/pilot-live-1234.out`; `grep -rn UNREGISTERED_CENSUS .ufo/waves/round-88/` → only
    `*_SELFTEST` lines.

## Findings

1. **DEFECT (calibration, self-record).** `SCORECARD.md:6` says “Round-88 claims, counting commands
   and measured commit: §Round 88 below”, and §Round 88 says the measured values and commit are
   “recorded in the subsection appended after measurement” (`SCORECARD.md:5453-5455`); at T
   `f77d2ae9` that subsection is absent — `grep -c 138a7543 SCORECARD.md` → 0, and §Round 88 ends at
   the capability list (`SCORECARD.md:5521` = EOF). The measured hash appears only in receipt headers
   (`measured/c1.out:1`, `measured/gate.out:1`). M→T adds only the four `measured/*.out` files.
2. **DEFECT (calibration, receipt binding).** `corpus/knowledge/router-mode-readiness.md:30` gives the
   operator-router row a post-fix verdict (`MODEL_UNLOADED router-unloaded`) inside a table declared
   “What the lane observed (2026-11-06…)”; the only 1234 receipt is the pre-fix pilot
   (`controls/pilot-live-1234.out:2-7`: four `unloaded` entries, verdict `MODEL_OK`). The cell is
   derivable from that same GET body, but it is not an observation and no receipt names a post-fix run.
3. **DEFECT (KQ36, calibration/operability).** `tools/round79-unregistered-census.py` — the registered
   `unregistered-census` capability instrument (`SCORECARD.md:190`, counting command `SCORECARD.md:4626`)
   — is modified base→M (one line: adds `MODEL_UNLOADED` to its model-endpoint verdict tuple), but its
   registered command was not re-run at M: `measured/harm.out:6` pastes only
   `UNREGISTERED_CENSUS_SELFTEST pass=4 fail=0`, a different invocation from
   `python3 tools/round79-unregistered-census.py --repo .`. No `UNREGISTERED_CENSUS` live/fixture summary
   exists in any round-88 receipt.
4. **NOTE (gate state).** `measured/gate.out:6-7` is red at M: `PRE_REPORT round=88 arms=14 failed=3
   uncommitted=4`, exit 1, including `round-scope` stray `measured/c1.out status=??` and the carried
   round-75 instrument arm (r87 R4). No terminal gate receipt exists at T (M→T adds only receipts).
   This is consistent with receipts being written before commit, but the round has no green-gate
   receipt at its tip; it is not a predicate of C1 or C2.
5. **NOTE (C2 wording scope).** The plan's “Instruments are not edited” is verified for the three
   instruments C2 names (command 2); the round did change `tools/round79-unregistered-census.py` as a
   C1 consequence. The sentence is accurate only when read as scoped to those three.
6. **NOTE (KQ141 grounding).** Both falsifier branches exist at base: `controls/c1-base.out:16,18`
   prints `MODEL_OK matched` for L01/L03 where the completion oracle says unloaded (`mismatches=11`
   at `:19`), and `controls/pilot-live-1234.out:2-7` shows a listing of four `unloaded` entries graded
   `MODEL_OK`. The status-less limit KQ141 cites is already documented at
   `tools/kama-probe.sh:49-50`, so the row adds no verdict-text demand beyond the frozen rule.
7. **NOTE (KQ142 grounding).** Falsifiers are demonstrated by the round's own controls:
   `controls/c2-base.out:2` `mismatches=4 met=False`, `controls/c2-pointer-only.out:3`
   `mismatches=4` (partial fix still red), `controls/c2-newest-base.out:27-29` `STALE_CALIBRATION`
   exit 1; the measured run is green with `# instruments base vs M: identical`
   (`measured/c2.out:3,7`). r83–r87 provide the five-round rejection history (`lessons/round-88.md` M1).
8. **NOTE (pre-existing index defect).** `corpus/QUALITY.md` has two `| KQ46` rows (lines 328, 453):
   141 rows, 140 distinct ids. Not repaired (append-only, no authority here); it does not affect the
   next free id (KQ141/KQ142).
9. **NOTE (draft integration check).** Commands 7–9 show both candidate blocks are pure appends
   (19/0, 56/0), add no audit event, and leave `regressed`, `bad_disclosures`, `vanished` at 0. The
   audit's exit 1 is the same pre-existing `unrestored=91` seen at M.

## Deliverables

- `.ufo/waves/round-88/w1/out/SB01QualityCriterion/candidate-QUALITY.md-rows.md` — KQ141 (M3) and
  KQ142 (M1), four-column format, append after KQ140 at EOF, no supersession (KQ141 extends KQ13/KQ19;
  KQ142 qualifies KQ20 and extends KQ36), falsifier in each reject cell.
- `.ufo/waves/round-88/w1/out/SB01QualityCriterion/candidate-README-frontier.md` — round-88
  `Frontier` block to append at the end of `corpus/README.md` (router mode held; other-engine
  multi-model readiness, per-request `?autoload`, sleeping/cold-start, operator 1234, load/unload
  action, non-listing residency routes, external verdict-set consumers, retained r85 items, index note).
- `.ufo/waves/round-88/w1/out/SB01QualityCriterion/append-only-audit-base-at-M.json` and
  `append-only-audit-after-candidates.json` — the two audit JSONs compared in commands 8–9
  (`to` = `138a7543…` and `356f478b…`; both `regressed=0`, `unrestored=91`).
- `.ufo/waves/round-88/w1/SB01QualityCriterion.md` — this report.

VERDICT: holds — both candidate criteria and the frontier block are delivered, grounded in the round-88 receipts, format-matched, and demonstrated append-only-clean in a scratch clone; Findings 1–3 are L1 integration items, not gaps in the drafts.
