# CN01OverlapScan — overlap scan for kama round 87 (read-only, edits nothing)

Measured revision: kama-shokunin `HEAD` = `94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659` (the freeze commit).
`git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse --show-toplevel` → `/home/vgpnk/Projects/shokunin/kama-shokunin`, rc 0.
`git -C … rev-parse HEAD` → `94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659`, rc 0.
Freeze-blob hashes (`git -C … show 94e8fe7b…:<path> | sha256sum`, rc 0), equal to the working-tree files:
- `tools/pre-report-gate.py` → `0ad6a80aa20af72eea5741fd3a44e62840c260692c7e65b45e0ea8dd04316979`
- `tools/round86-rendered-cells.py` → `f9d36b5be0683fdc486da343f6c3aa2e140f250efc94c377ddda1a36ba6e633b`

Search scope: `tools/`, `corpus/`, `plans/` of the 20 sibling `*-shokunin` lanes (where present), plus kama's `plans/` and `PROVINCE.md`, and `scripts/hyaku/`. Matching is case-sensitive. `audio-shokunin/tools`, `kengaku-shokunin/tools`, `kake-shokunin/tools`, `kotodama-shokunin/plans`, `tabi-shokunin/tools`, `game-dev-2d-shokunin/tools` do not exist and were skipped by the grep tool.

## Commands and outputs

C1 (identifier scan). Grep tool, pattern
`round87|round86-instruments|ARM14|C1_PROBES|c1-probes|round86-rendered-cells|round86-mutant-owners|round86-pin-origin`,
over the explicit `*-shokunin/{tools,corpus,plans}` paths and `scripts/hyaku`. Output: `Showing files 1-20 of 36`; page 2 (`skip=20`) returned the rest. Total 36 files.

C1b (name globs, `gitignore=false`). Patterns `*-shokunin/tools/pre-report-gate*.py`, `*-shokunin/tools/round8*-rendered*.py`, `*-shokunin/tools/round87*`, `*-shokunin/tools/*arm-faults*`, `*-shokunin/plans/round-87-claims.md`, `*-shokunin/plans/round87*`, `scripts/hyaku/*`. Output: only kama files for the gate and selector names; `round-87-claims.md` in kama, kengaku and kaidoku; `round87_*.py` in kengaku.

C1c. `ls` of the three kama round-87 successor/probe paths (bash, rc shown):
```
ls kama-shokunin/tools/round87-rendered-cells.py kama-shokunin/tools/round87-gate-arm-faults.py kama-shokunin/.ufo/waves/round-87/controls/c1-probes.py
→ No such file (round87-rendered-cells.py), No such file (round87-gate-arm-faults.py); c1-probes.py present; exit=2
```
(The successor and fault harness are sibling build seats' out-dir candidates, not yet in the lane tree; expected at wave 1.)

C1d. `git -C kama-shokunin ls-tree --name-only 94e8fe7b… tools/ | grep -E 'round8[67]|pre-report'` → `tools/pre-report-gate.py`, `tools/round86-mutant-owners.py`, `tools/round86-pin-origin.py`, `tools/round86-rendered-cells.py`; rc 0.
`git -C kama-shokunin ls-tree --name-only 94e8fe7b… plans/ | grep round-87` → `plans/round-87-claims.md`; rc 0.
`git -C kama-shokunin grep -n -E 'round-87|round87|round86-instruments|ARM14' 94e8fe7b… -- PROVINCE.md` → no output; rc 1.

C1e. Pre-report / rendered-cell instrument glob and grep across sibling `tools/` and `corpus/` (`PRE_REPORT|pre-report-gate|rendered.cells|RENDERED_CELLS`, and `pre-report|rendered cell|self-assessment cell|calibration cell|CommonMark|fence closer`): hits listed in §3.

## Findings

### 1. Identifier hits, owner lane, collision with kama round-87 names

Exact kama round-87 names searched: `round87-rendered-cells`, `round87-gate-arm-faults`, `round86-instruments`, `ARM14_FAULTS`, `C1_PROBES`, `c1-probes`, copies of `pre-report-gate.py`.

| path:line | token | owner | collision |
|---|---|---|---|
| kama-shokunin/plans/round-87-claims.md:19-91 | `round87-rendered-cells`, `round86-instruments`, `round87-gate-arm-faults`, `c1-probes.py`, `ARM ` arm numbers | kama (the frozen claim) | self |
| kama-shokunin/plans/round-86-claims.md:20-23,63-65,94-96 | `round86-rendered-cells` / `-mutant-owners` / `-pin-origin` predicates | kama (predecessor) | self |
| tameshi-shokunin/tools/design-blob-audit.py:565 | `ARM14_MULTI_RECEIPT_POPULATION` | tameshi | no (different token; tameshi arm label) |
| tameshi-shokunin/tools/receipt-bytes-bind.py:675 | `ARM14_symlink_not_a_receipt` | tameshi | no |
| tameshi-shokunin/tools/selfstate-freshness.py:866 | `ARM14_python_isolation_tuple` | tameshi | no |
| tameshi-shokunin/tools/selfstate-freshness-mutants.spec:29 | `arm14-ARM14_python_isolation_tuple` | tameshi | no |
| tameshi-shokunin/tools/registry.json:2026 | `SELFTEST_ARM14_symlink_not_a_receipt: PASS` | tameshi | no |
| tameshi-shokunin/corpus/lessons/round-79.md:84, round-79-verifier-spotcheck.md:121-125, round-83.md:28 | `ARM14_python_isolation_tuple`, `SELFTEST_ARM14…` | tameshi | no |
| kengaku-shokunin/plans/round-87-claims.md:3-16,73-75 | basename `round-87-claims.md`; `round87_c1_replay.py`, `round87_c2_wording.py`, `round87_mteb_probe.py`, `round87_report_paths.py`, `round87-cases.json` | kengaku | no: same basename in a separate repo; underscore names are a different namespace from kama's hyphen names |
| kengaku-shokunin/plans/round88_claim_figures.py:94-96; round89_claim_figures.py:82-84 | `R87-C1` / `R87-C2` keys naming kengaku's own files | kengaku | no |
| kengaku-shokunin/corpus/evidence/round87/*; corpus/lessons/round-87*.md; plans/grader-population-ledger.json:537-541 | round-87 receipts | kengaku | no |
| kaidoku-shokunin/plans/round-87-claims.md | basename only | kaidoku | no |
| kake-shokunin/corpus/QUALITY.md:1758; corpus/lessons/round-87.md:5-6,52-63; round-88.md:55 | `round87 w1/ReviewCounter`, `.ufo/waves/round-87/` in kake's repo | kake | no |
| kotodama-shokunin/corpus/README.md:912-916 | "round87 counter" | kotodama | no |
| kotoba-shokunin/corpus/README.md:176-177; corpus/lessons/round-87-verifier-spotcheck.md:180-199 (`omp-root-semantics-round87.md`) | `round87` in a filename | kotoba | no |
| kasegi-shokunin/corpus/QUALITY.md:460-463; corpus/lessons/round-59-verifier-spotcheck.md:36 | `c1-probes-base-r59.txt` receipts | kasegi | no (receipts, not `controls/c1-probes.py`) |

Zero hits in any sibling for: `round87-rendered-cells`, `round87-gate-arm-faults`, `round86-instruments`, `round86-rendered-cells`, `ARM14_FAULTS`, `C1_PROBES` (case-sensitive), or any copy of `pre-report-gate.py` (the name glob returns only `kama-shokunin/tools/pre-report-gate.py`). `scripts/hyaku/` (lane-addendum.md, hyaku.env, inline-dispatcher.py, …) has zero hits.

Caution for the L1: the bare token `ARM14` is used as an arm label in tameshi. Do not grep for bare `ARM14` to find kama's arm; use `ARM14_FAULTS` or `round86-instruments`.

### 2. PROVINCE.md: where the selector and the gate sit (kama's own text)

- Pre-report gate, province placement: `PROVINCE.md:301` "`tools/pre-report-gate.py` runs the round's four reconciled instruments plus a round-worktree cleanliness arm and emits one `PRE_REPORT` verdict;" and `PROVINCE.md:344-345` "`tools/pre-report-gate.py` now composes the three round-78 instrument selftests as its tenth arm (`round78-instruments`), so a scored gate run executes the counters a round lands."
- Rendered-cell selector, province placement: `PROVINCE.md:408-411` "`tools/round86-rendered-cells.py` grades the lane's own self-assessment cells as a *renderer* shows them: HTML comments, backtick and tilde fences, `round-N correction` blocks and non-column-0 lines are not cells, and the head authority claim couples revision, command and receipt bytes …"
- Cross-lane placement: `corpus/knowledge/cross-lane-scope.md:95-100`: "kama's `tools/pre-report-gate.py` grades four kama instruments plus a round-scoped uncommitted class. Rule: a pre-report gate aggregates the instruments of its own lane and is never cited as another lane's evidence."
- Absent: no PROVINCE line names `round87-rendered-cells`, `round87-gate-arm-faults`, the `round86-instruments` arm, `ARM14`, or `c1-probes`. Confirmed at freeze (`git grep` rc 1) and in the working tree (grep returns only lines 300-301, 344-345, 408-414 for the gate and round-86 selector). PROVINCE line 17 (lane instruments, SCORECARD canonical list) names neither the gate nor the selector.
- The successor selector is not yet in any province line. The round-86 selector is (`:408`), so the successor is inside kama's tools surface by path but not named.

### 3. Sibling pre-report or rendered-cell instruments that would duplicate C1 or C2

Pre-report gates (lane-scoped, different populations):
- `souji-shokunin/tools/souji-pre-report-gate.sh:2` ("Read-only round pre-report checks") and `tools/souji-report-contract.py:6-10`. Own lane's checks. Duplicates neither C1 nor C2: no kama arm is composed, no cell is graded.
- `kasegi-shokunin/corpus/instruments/r46-landing-gate.py --pre-report` (`corpus/instruments/README.md:1000`: tree-clean, jj-state, remote-tip, placeholders). Overlaps only the concept of kama's existing round-clean arm, not C2's new arm. Named in `kama corpus/knowledge/cross-lane-scope.md:95-100` as a contested-purpose pre-report aggregator.
- `tameshi-shokunin/tools/receipt-revision-gate.py` (receipt-to-revision binding). Overlaps the concept of kama's `round73-receipt-claim-binding`, not C1's three facts or C2's arm.
- `tsukuroi-shokunin/tools/check-pause-gate.py` counts premises in a pause-lift entry; not a pre-report gate.

Rendered-cell / self-assessment instruments: none in a sibling grades a SCORECARD self-assessment cell, a head authority cell, a calibration row, or a disposition token. Closest, fence-only overlap with C1's R1 rule:
- `kasegi-shokunin/corpus/instruments/r46-c1-gate.py:114-115` `live_lines` (lines outside HTML comments and fences; applied to `recheck:` lines).
- `tsukuroi-shokunin/tools/check-owed-statements-r29.py:19-23` (CommonMark fences; rendered-line M1).
- `mori-shokunin/tools/mori-claim-sweep.py:45-49` `visible_lines` (CommonMark fence regex).
- `kotoba-shokunin/verifiers/verify_corpus_integrity.py:138-141,183-186,415-418` and `verify_skill_checklist.py:344-348` (CommonMark 4.5 closer rule).
- `kasegi-shokunin/corpus/instruments/r38-closure.sh:313-316`, `r39-closure.sh:80-83`, `r41-closure.sh:508-511`, `r42-closure.sh:303-306` (fence walks).

Verdict on duplication: the CommonMark fence-closer rule (C1 R1) is reimplemented in at least six sibling lanes. No sibling implements C1's R2 (disposition token after `verdict`) or R3's gate-token coupling. No sibling instrument duplicates C2. Lane-scope rule (`cross-lane-scope.md:95-100`) forbids citing another lane's gate; these are for reference only.

### 4. Adjacency observations inside kama (for the L1, from the frozen text; not collisions)

- A. After C1 integrates, `tools/round86-rendered-cells.py` and `tools/round87-rendered-cells.py` coexist (the claim says the predecessor is not edited). C2's arm `round86-instruments` runs the `--selftest` of `round86-rendered-cells.py`, `round86-mutant-owners.py` and `round86-pin-origin.py` only (`round-87-claims.md:90-92`). No arm runs the successor's selftest, and the frozen C2 text names none for it. A regression in `round87-rendered-cells.py` would not turn the gate red.
- B. `round87-gate-arm-faults.py` seeds faults only in round-86 instruments (`round-87-claims.md:95-97`). It cannot catch a fault in the C1 successor, which is the same gap as A.
- C. `ARM_ORDER` at freeze ends `… "round81-instruments", "round82-instruments", "round83-instruments"` (`tools/pre-report-gate.py`, the freeze blob). The planned `round86-instruments` is appended after `round83-instruments`; the prefix stays unchanged. No overlap.
- D. `round-87-claims.md` basename is shared with kengaku and kaidoku. Path-qualified references (`kama-shokunin/plans/…`) are unambiguous. Bare `round-87-claims.md` in notes is ambiguous.

## Verdict table

| question | answer |
|---|---|
| sibling hits for kama's exact round-87 names | none (zero for `round87-rendered-cells`, `round87-gate-arm-faults`, `round86-instruments`, `ARM14_FAULTS`, `C1_PROBES`, and copies of `pre-report-gate.py`) |
| collisions with kama round-87 names | no (ARM14 hits in tameshi are different tokens; `round-87-claims.md` basename in kengaku and kaidoku is a separate repo) |
| PROVINCE line placing the selector | `PROVINCE.md:408-411` (round-86 selector; successor absent) |
| PROVINCE line placing the gate | `PROVINCE.md:301`, `:344-345` |
| sibling instrument that duplicates C1 | no (shared fence-closer rule only, in ≥6 lanes) |
| sibling instrument that duplicates C2 | no |

VERDICT: No collisions and no sibling duplicates of C1 or C2; adjacency gaps A and B mean the gate would not catch a regression in the round-87 successor selector.
