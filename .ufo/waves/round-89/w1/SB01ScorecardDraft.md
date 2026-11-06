# SB01ScorecardDraft — round-89 SCORECARD draft (kama r89 w1)

## Scope

Drafted, did not apply, the round-89 record text for the L1: (1) the `## Round 89` section, (2) two new
capability rows, (3) a corrected evidence pointer for the existing `router-mode-readiness` row, (4)
`### Planned (round 90)`. Every measured number was copied from the committed receipts under
`.ufo/waves/round-89/controls/` and `.ufo/waves/round-89/measured/`, never from lane prose. Lane read-only;
all work ran in one shared clone at `/fast/scratch/hyaku/kama-r89/SB01ScorecardDraft/wt` (detached from lane
master `c8db858691e883955f10cf9d7e1dec8f8d732bc8`), removed before yield. No tool installs (no pacman, no
uv, no npx); 127.0.0.1:1234 was never contacted and no server was started.

## Commands and outputs (true exit codes)

Recorded in `w1/out/SB01ScorecardDraft/counters-draft.out` (baseline block, then draft block).

| Command (in the clone) | Baseline `c8db8586` | Draft `e2e9399c` |
|---|---|---|
| `python3 tools/round42-selfdesc-reconcile.py --repo . --tip <rev>` | `mismatches=5 met=False`, exit 1 | `mismatches=0 met=True`, exit 0 |
| `python3 tools/round74-selfdesc-canon.py --repo .` | worktree read: baseline blob is `canon_round=88 canon_rows=55` (`.ufo/waves/round-88/measured/gate-final.out:8`) | `canon_round=89 canon_rows=57 invisible=0`, exit 0 |
| `python3 tools/round86-rendered-cells.py --repo . --rev <rev>` | `facts=3 mismatches=3 gate=0 closure=0 disposition=0`, exit 1 | `facts=3 mismatches=0 gate=1 closure=1 disposition=1`, exit 0 |
| `python3 tools/round68-receipt-pointer-audit.py --repo . --rev <rev>` | `cited=303 resolved=285 unresolved=0`, exit 0 | `cited=312 resolved=294 unresolved=0`, exit 0 |
| `python3 tools/round72-receipt-tip-binding.py --repo . --round 89 --tip <rev>` | exit 2 (`carries no '## Round 89' section`) | exit 2 (`.jsonl` citation in `corpus/lessons/round-89.md`) |
| `python3 tools/round69-newest-closure-counter.py --repo . --rev <rev> --since-round 63` | `row_current=false` + `STALE_CALIBRATION`, exit 1 | `row_current=true`, exit 0 |
| `git apply --check scorecard-draft.patch` (clone at `c8db8586`) | — | exit 0 (`2 files changed, 146 insertions(+), 9 deletions(-)`) |
| `git log --diff-filter=A --format=%H -- plans/round-89-claims.md` | — | `4eb75c62f6deb1a586a291d611b71775049b34a6` (same commit adds both counters) |

Intermediate reds I produced and repaired: a first draft cited receipts as `measured/c1.out:14`, which
`round68` read as a path (`unresolved=8`) and `round72` as a non-receipt file; line numbers are now prose.
A trailing blank line at EOF (caught by `git apply --check`) was removed. Both fixes are why the final
draft tip differs from earlier scratch commits.

## Findings

- **DEFECT (record state at lane master, before any draft): three self-description instruments are red.**
  `round42-selfdesc-reconcile` `mismatches=5` (SKILL sha256/lines/grep count, knowledge-file count, closure
  pointer at round 87 while the newest committed spotcheck is round 88); `round86-rendered-cells`
  `mismatches=3` (head gate names round 86 while the newest terminal receipt is round 88; calibration row
  names round 87 and names no disposition); `round69-newest-closure-counter` `STALE_CALIBRATION` exit 1.
  Evidence: `counters-draft.out`, baseline block.
- **DEFECT (the row I was asked to correct, reproduced): the live `router-mode-readiness` row's first
  pointer is a green of the superseded rule.** `corpus/lessons/round-88-verifier-spotcheck.md:28` (D1) and
  `:111` (R2) state it; the row describes the repaired rule while citing `ROUTER_CELLS cells=17
  mismatches=0` at `138a7543`. The draft cites the post-repair oracle green
  (`.ufo/waves/round-88/repair/oracle-cells-repair.out:5`, `ORACLE_CELLS rev=8b5bb69d… cells=3
  mismatches=0`) plus this round's re-run at M (`measured/harm-M.out:10`), and states that the round-88
  counter's own `mismatches=2` (C05, C12) is a residual, not a green.
- **BLOCKER-for-L1 (cross-seat, reproduced): the lane worktree PROVINCE.md paragraph now carried by another
  seat does not name `tools/round89-signature-rows.py`.** With my drafted SCORECARD plus that PROVINCE
  (sha256 `d41b7399…`, 435 lines) the reconciler prints `province: PROVINCE.md lacks
  tools/round89-signature-rows.py (capability router-error-signature-table)`, exit 1
  (`cross-seat-province.out`). The paragraph names `tools/round89-router-signatures.py` (the receipt
  generator), not the row counter the capability cites. Either name the counter or drop that token from the
  evidence cell.
- **BLOCKER-for-L1: the coverage-row anchor depends on which PROVINCE paragraph lands.** My patch's
  paragraph is 434 lines / sha256 `806c3db2…`; the worktree paragraph is 435 lines / `d41b7399…`, so
  landing both duplicates content and leaves the anchor red (`r41 coverage … observed d41b7399…`). Re-derive
  the anchor from the landed bytes with the reconciler itself; do not copy mine.
- **NOTE — base and M operator-router receipts are different commands, same verdict.** Base is a registry
  check (`controls/harm-base-operator-1234.out:14-16`: `model_ok=1 drift=0 exit=0`, one row whose
  `served_model` lists four ids at `:28`); M is four per-model lines (`measured/harm-M.out:19-22`,
  `MODEL_OK router-unloaded-autoload`). The draft discloses the form difference; neither loads a model.
- **NOTE — the freeze commit `4eb75c62…` is in no receipt.** Derived by three agreeing `--diff-filter=A`
  queries; the draft's provenance table says so instead of implying a receipt.
- **NOTE — `round72-receipt-tip-binding --round 89` exits 2 for a file outside this seat's write
  boundary**: `corpus/lessons/round-89.md:24` cites `.ufo/waves/round-89/measured/router-signatures.jsonl`
  and the instrument's receipt extensions are `.out .txt .log .json`. Round 88 has the same class (`.py`).
- **NOTE — landing-order hazard.** `round86-rendered-cells` takes the FIRST `PRE_REPORT` token on the
  single authority line and demands the newest `.ufo/waves/round-<N>/measured/*.out` gate receipt. The draft
  names the round-88 receipt (newest today); committing a round-89 gate receipt turns that sentence red
  until it is re-pointed at the new receipt's own `rev`, token and path. Copy, never invent, those values.
- **NOTE — what the draft deliberately does not contain**: wave-1 dispositions, any change to the claim
  verdicts, `LOG.md`, `plans/`, the round-89 lesson, the terminal gate receipt, or any edited predicate.

## Deliverables

Under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-89/w1/out/SB01ScorecardDraft/`:

- `round-89-draft.md` — the complete draft: placement map, section, canonical list, Planned (round 90),
  required head/Axes/Retired/Saturation/PROVINCE edits, number provenance, landing hazards.
- `round-89-section.md`, `capabilities-round89.md`, `planned-round90.md`, `province-round89-note.md` — the
  same text split per deliverable.
- `scorecard-draft.patch` — the landing form (SCORECARD.md + PROVINCE.md); applies clean to `c8db8586`.
- `counters-draft.out`, `baseline-reconcile.out`, `reconcile-draft.out`, `patch-apply-check.out`,
  `cross-seat-province.out` — receipts for the commands above.

Report: `.ufo/waves/round-89/w1/SB01ScorecardDraft.md`

VERDICT: holds — every measured number in the draft traces to a committed receipt line (the freeze hash is derived from three `--diff-filter=A` queries and labelled as such), the corrected pointer names a green of the landed rule as round-88 D1/R2 requires, and the drafted record is green on `round42-selfdesc-reconcile`, `round74-selfdesc-canon`, `round86-rendered-cells`, `round68-receipt-pointer-audit` and `round69-newest-closure-counter` at full hash `e2e9399c7d8353b0747a0f40de694d3ab558aad2`, with two cross-seat PROVINCE blockers named for the L1.
