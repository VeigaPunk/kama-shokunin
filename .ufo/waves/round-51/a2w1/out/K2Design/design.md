# C2 design critique — calibration

**Verdict: disclosure is useful calibration evidence, but the current ledger is not a legitimacy ledger and must not be allowed to bless its own or future losses.** Axes: calibration (primary), auditability/robustness (secondary).

## Case for calibration

The frozen claim explicitly narrows the meaning: compare the lane's self-assessment with independently recomputed repository state; disclose rather than restore; nine constructed cases exercise expectations by construction. v6 lowers the event threshold from 20 to 1, directly addressing the prior blind spot (the docstring identifies 97 hidden sub-20 events, including the real LOG.md loss at `ed135b3c`). The lane ledger holds 166 line entries across 51 events (ledger rows 11–167 include the historical losses); its rows name a specific commit, file, CR-stripped-line hash, multiplicity, and a mechanical class. The checker recomputes deletion events and unheld graded keys, so a ledger entry is not accepted merely because someone wrote a note: nonexistent event/key, excess count, and wrong mechanical class are rejected. This makes the disclosure inventory falsifiable and materially better than a threshold that simply omits small losses.

The preregistration is candid that the tool and counters were authored alongside the build, and that C2 had one pre-freeze dry run. That is an independence limitation, not evidence that the observed inventory is false; the counter's own recomputation and external fixture expectations are the relevant checks.

## Strong laundering counterexample

The ledger is read from the **same target revision** being audited (`audit()` lines 551–564 reads `registry/append-only-disclosures.tsv` at `to_full`). A commit can delete a graded line and add a matching disclosure row in that same commit; its commit subject and added hunk determine a mechanical class, and the ledger can make every remaining loss `disclosed`, hence exit zero. The check validates that the row points to an actual loss; it does not establish that the disclosure was made before the loss, was authorized, or is truthful as a justification. The frozen limit admits precisely this: class is mechanical and note is the deleting commit subject (preregistration lines 43, 29–31). Thus 166 disclosed lines are calibration of *accounting completeness*, not validation of the deletions' legitimacy. Without a temporal/authority constraint, the ledger can turn “unrestored” into a cheap successful verdict, rather than being a retrospective audit trail.

**Required temporal guard:** for every ledger row, resolve the named commit and the ledger blob's introducing/update commit from git history, and require the ledger record to predate the deletion event (at minimum, ledger-record commit must be an ancestor of the loss commit; compare commit graph/date, not mutable author timestamps). Also require the ledger's target commit identifier to match the event exactly and reject rows added at or after the deletion. Better still, bind a disclosure to a prior approval/reference and keep the ledger append-only. The existing note is just subject text and cannot substitute for this.

## A-row mismatch: `opened` is not permitted

The contract row says A-row cells `status`, `recheck`, `used-by` are mutable (`registry/append-only-contract.tsv:6`). `sources-append-only.py` independently defines exactly those three as `MUTABLE_CELLS` (lines 68–77); its `opened` cell is explicitly immutable (line 76; line 437's per-cell oracle says opened edit exits 1). But v6 `append-only-audit.py` sets `MUTABLE_COLS = (7, 9, 10)` (line 175), then `permitted_edits()` (lines 508–521) treats equality outside those indices as permission. That does appear to exclude index 8 (`opened`) and therefore matches the source tool's mutable set, assuming the documented 11-cell layout and zero-based indexing. The prose in v6 docstring lines 10–14 says the same three cells; no `opened` exception is present. This is not the laundering defect: verify it against the fixture counter, but mechanically the current index set correctly leaves `opened` immutable.

A sharper robustness concern: allowed status/recheck/used-by changes are considered “permitted” by comparing old/new row cells, irrespective of whether those fields changed to a sensible value. That matches the stated byte-equality contract, but is a permission classification, not semantic validation; do not claim it assesses registry correctness.

## Smallest safe correction

Keep the disclosure mechanism and calibration interpretation, but make it impossible for contemporaneous documentation to erase a failure: require each disclosure row's introducing commit to be an ancestor of the corresponding deletion commit, and reject otherwise. Continue reporting mechanical class as evidence of diff shape only; do not label it an approval or legitimacy judgment. Retain the A-row exact immutable-cell comparison including `opened`.

## Evidence / commands and scope

Read frozen files directly: `tools/append-only-audit.py` docstring lines 4–27, 508–522, audit lines 551–564 and 669–710; `registry/append-only-disclosures.tsv` rows 1–167; `registry/append-only-contract.tsv` row 6; `.ufo/waves/round-51/preregistration.json` lines 8–10, 29–44; `tools/sources-append-only.py` lines 68–77 and 432–438. No counter was run; no result is claimed beyond source inspection. The reported build count (166 disclosed lines / 51 events) is from the assignment context, not independently rerun here.
