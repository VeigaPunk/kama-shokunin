# CN01OverlapScan — round 87 wave 1 overlap scan (read-only)

Full evidence: `.ufo/waves/round-87/w1/out/CN01OverlapScan/overlap.md`.
Measured revision: kama `HEAD` = `94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659` (freeze), rc 0. Working-tree
`tools/pre-report-gate.py` and `tools/round86-rendered-cells.py` match the freeze blobs
(`0ad6a80a…6979`, `f9d36b5b…e633b`), rc 0.

## Scope
1. Identifier scan over `*-shokunin/{tools,corpus,plans}` and `scripts/hyaku`: `round87-rendered-cells`,
   `round87-gate-arm-faults`, `round86-instruments`, `ARM14_FAULTS`, `C1_PROBES`, `c1-probes`, `round86-*`,
   copies of `pre-report-gate.py`. Grep tool, case-sensitive. 36 files matched in total.
2. PROVINCE placement of the selector and the gate.
3. Sibling pre-report or rendered-cell instruments that would duplicate C1 or C2.

## Commands and outputs
- Grep, pattern `round87|round86-instruments|ARM14|C1_PROBES|c1-probes|round86-rendered-cells|round86-mutant-owners|round86-pin-origin`,
  explicit sibling paths. `Showing files 1-20 of 36`; `skip=20` returned the rest.
- Glob `*-shokunin/tools/pre-report-gate*.py` → only `kama-shokunin/tools/pre-report-gate.py`.
- Glob `*-shokunin/tools/round87*`, `*arm-faults*`, `scripts/hyaku/*` → no round-87 selector, fault harness, or gate copy in any sibling.
- `ls kama-shokunin/tools/round87-rendered-cells.py kama-shokunin/tools/round87-gate-arm-faults.py` → No such file, exit 2.
  (Expected at wave 1: those are sibling build candidates not yet integrated.)
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse --show-toplevel` → kama path, rc 0.
- `git -C kama grep -n -E 'round-87|round87|round86-instruments|ARM14' 94e8fe7b… -- PROVINCE.md` → no output, rc 1.

## Findings
F1. Zero sibling hits for `round87-rendered-cells`, `round87-gate-arm-faults`, `round86-instruments`, `ARM14_FAULTS`,
    `C1_PROBES`, `round86-rendered-cells`, or any copy of `pre-report-gate.py`. `scripts/hyaku/` has no hits.
    Evidence: `out/CN01OverlapScan/overlap.md` §1.
F2. Collisions: none. The bare token `ARM14` appears in tameshi (`tools/design-blob-audit.py:565`,
    `receipt-bytes-bind.py:675`, `selfstate-freshness.py:866`, `registry.json:2026`); those are tameshi arm labels,
    different tokens. `round-87-claims.md` has the same basename in kengaku and kaidoku (`plans/`), a separate repo,
    no content collision. kengaku's `plans/round87_*.py` use underscores, a different namespace.
    Caution: do not grep bare `ARM14` for kama's arm.
F3. PROVINCE.md places the selector and the gate, quoted:
    - `PROVINCE.md:301`: "`tools/pre-report-gate.py` runs the round's four reconciled instruments plus a round-worktree cleanliness arm and emits one `PRE_REPORT` verdict;"
    - `PROVINCE.md:344-345`: "`tools/pre-report-gate.py` now composes the three round-78 instrument selftests as its tenth arm (`round78-instruments`)…"
    - `PROVINCE.md:408-411`: "`tools/round86-rendered-cells.py` grades the lane's own self-assessment cells as a *renderer* shows them…"
    - Absent: no PROVINCE line names `round87-rendered-cells`, `round87-gate-arm-faults`, the `round86-instruments` arm, `ARM14`, or `c1-probes` (grep rc 1 at freeze).
    - `corpus/knowledge/cross-lane-scope.md:95-100`: a pre-report gate "aggregates the instruments of its own lane and is never cited as another lane's evidence."
F4. Sibling pre-report gates exist, each lane-scoped, none duplicates C1 or C2:
    - `souji-shokunin/tools/souji-pre-report-gate.sh` (+ `souji-report-contract.py`): souji's own report checks.
    - `kasegi-shokunin/corpus/instruments/r46-landing-gate.py --pre-report`: tree-clean, jj-state, remote-tip, placeholders;
      overlaps only the concept of kama's existing round-clean arm.
    - `tameshi-shokunin/tools/receipt-revision-gate.py`: receipt-to-revision binding; overlaps only the concept of kama's round-73 binding arm.
F5. No sibling grades a self-assessment cell, head authority cell, calibration row, or disposition token. Sibling fence walkers
    exist (`kasegi …/r46-c1-gate.py:114-115`, `tsukuroi …/check-owed-statements-r29.py:19-23`, `mori …/mori-claim-sweep.py:45-49`,
    `kotoba …/verify_corpus_integrity.py:138-141`, `kotoba …/verify_skill_checklist.py:344-348`). The CommonMark closer rule (C1 R1)
    is reimplemented in at least six lanes; that is shared fence logic, not a duplicate C1 instrument.
F6. Adjacency gaps inside kama (from frozen text, not collisions):
    - A. `round86-instruments` runs the selftests of the three round-86 instruments only (`plans/round-87-claims.md:90-92`).
      The C1 successor `round87-rendered-cells.py` is in no arm. A regression there would not turn the gate red.
    - B. `round87-gate-arm-faults.py` seeds faults only in round-86 instruments, so it cannot catch the successor's fault (same gap as A).
    - C. `ARM_ORDER` appends `round86-instruments` after `round83-instruments`; prefix unchanged. No overlap.

## Deliverables
- `.ufo/waves/round-87/w1/out/CN01OverlapScan/overlap.md` (commands, hit table, PROVINCE quotes, sibling equivalence, verdict table).
- This report: `.ufo/waves/round-87/w1/CN01OverlapScan.md`.
- No lane-tree file was edited. Scratch dir `/fast/scratch/hyaku/kama-r87/CN01OverlapScan/` removed after the receipts were copied.
- No tool was installed or upgraded.

VERDICT: no collisions and no sibling duplicates of C1 or C2; the gate does not compose the round-87 successor selector, leaving a regression gap for C1 under C2.
