# WR04 draft — SCORECARD round-63 append and head re-derivation (not applied to the lane)

Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09`. Placeholders `<C1_LINE>`, `<C2_LINE>`, `<TIP>` are filled by the L1 after measurement. `apply-selfdesc-r63.py` applies Part B's head edits and appends Part A verbatim.

## Part A — text appended to the end of SCORECARD.md

### Round-63 measured results

- C1 (operability, live request plane): `python3 tools/round63-c1-counter.py --repo <lane> --tip <TIP> --work <scratch>` → `<C1_LINE>`; receipt `.ufo/waves/round-63/measured/c1-final.out`, exit code beside it in `c1-final.exit`.
- C2 (calibration, twelve capabilities bound to live rows): `python3 tools/round63-c2-counter.py --repo <lane> --tip <TIP> --work <scratch>` → `<C2_LINE>`; receipt `.ufo/waves/round-63/measured/c2-final.out`, exit code beside it in `c2-final.exit`.
- Measured tip: `<TIP>`. Both counters read the tip from git blobs at `--rev`, never from the working tree.

Admission rule (frozen in `.ufo/waves/round-63/controls/freeze.txt`): a claim is admitted only when its counter line above prints `met=True` with exit 0. `live-completion-request-plane` is not in the twelve-row round-63 list; it enters a canonical list only under that rule. Scores stay operability 8 / calibration 7 unless a later section records a verdict that moves them.

### Planned (round 64)

1. Operability (C1): settle the round-63 C1 verdict through a non-author falsification wave before any admission. Re-run `tools/round63-c1-counter.py` at the measured tip against a mutation battery (the lane's own mutants plus a non-author set) and record each SURVIVED mutant as the first round-64 repair target; the round-62 claim stayed provisional because its wave never settled.
2. Operability (C1 admission path): if the printed C1 line is `met=True`, record in this section how `live-completion-request-plane` enters the canonical list, because the frozen round-63 list excludes it and the freeze's rule does not name a list; if `met=False`, repair the controls the printed line names and re-freeze the counter instead of editing it in place.
3. Calibration (C2): if the printed C2 line is `met=False`, re-freeze with a repair limited to the family or mismatch it names; if `met=True`, plant a fifth defective verdict function written by a non-author seat and confirm the sensitivity self-test rejects it before crediting the sensitivity conjunct.
4. Self-description: run `tools/round42-selfdesc-reconcile.py` and `tools/round41-scorecard-reconcile.py` at every closure commit, not only the measured one. At `03a6a1d` the round-41 coverage row still read 36 while the tree holds 38 knowledge files (two were landed by rounds 61 and 62 without a head re-derivation).
5. Corpus: land `corpus/lessons/round-63.md` with the one mistake the round-63 freeze promises to mine; it is absent at `03a6a1d`.
6. Ownership: before any closure commit, resolve the lane worktree's untracked round-63 wave paths and its modified `PROVINCE.md` and `corpus/SOURCES.md` (both seen at the draft's cut; `git status` at the lane root also lists an untracked `kama-shokunin/` entry). Commit only owned paths.

## Part B — exact replacements (what `apply-selfdesc-r63.py` does, with the tip line each one lands on)

Each old string occurs exactly once at tip `03a6a1d`; the script aborts otherwise.

### B1. PROVINCE.md — append at end of file (tip has 188 lines; the new file has 190 lines)

Append after the existing last line (blank line, then):

```
**Round-63 claim tables — provenance (2026-10-28).** `registry/ollama-live-claims-r61.tsv` is the round-61 claim table for the live Ollama lifecycle (capability `live-ollama-lifecycle`, instrument `tools/kama-ollama-live.py`); `registry/capability-claims-r63.tsv` is the round-63 twelve-row binding that `tools/round63-c2-counter.py` reads; `tools/round63-c1-counter.py` grades the request-plane instrument `tools/kama-completion-live.py` (schema `kama-completion-live/v2`). These are frozen inputs and instruments; a counter line admits a claim only in the SCORECARD round section that cites it.
```

The new PROVINCE.md sha256 is printed by the script (`applied: PROVINCE.md sha256=… lines=…`) and must be the value used in B2's coverage row. In the scratch clone test it is `6fcc474ba627144b3d83561252e415e4af583c838be9ef6a9049a95266790a77` (190 lines); the L1 must recompute it from the file it actually commits.

### B2. SCORECARD.md head

- **Line 6 (banner), whole line** replaced by:

```
**Current authority (round 63):** assigned axes are operability + calibration (`shokunin.conf` kama row; the MISSION.md freshness conflict remains open at `.ufo/l0-questions.md:145`). Latest measured round: 63 (wave verdicts recorded in §Round 63 measured results). Calibration 7 remains the lowest assigned axis, below operability 8; nudge inactive. Scores are held at operability 8 / calibration 7 pending the round-63 verdicts. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived by `tools/round42-selfdesc-reconcile.py`; round-specific outcomes stay in their round sections.
```

- **Lines 51–53 (`## Planned`)**: the sentence `Superseded in round 42. The live plan is `### Planned (round 61)` below; the round-5 plan this section carried is kept verbatim under §Historical head sections.` becomes:

```
The live plan is `### Planned (round 64)` at the end of this file, after §Round 63 measured results. Earlier plans stay in their round sections; the round-5 plan this section carried is kept verbatim under §Historical head sections.
```

- **Line 57 (`## Retired`)**: `None. 6 axes and 11 capabilities remain active.` → `None. 6 axes and 12 capabilities remain active.` (rest of the paragraph unchanged).

- **Line 117 (`## Capabilities` intro)**: `Mirror of the round-49 canonical capability list that §Round 49 carries` → `Mirror of the round-63 canonical capability list that §Round 63 carries`.

- **Insert after line 131** (the `live-receipt-replay` row of the head mirror), a copy of the round-63 canonical row for `live-ollama-lifecycle`, i.e. SCORECARD.md line 3320 at tip, verbatim:

```
| live-ollama-lifecycle | Start the pinned Ollama v0.40.11 binary on an unregistered loopback port, create a qualified model from the lane GGUF fixture, capture tags/ps/v1 surfaces before and after one generation with an outside-observer hold window, grade /api/show, and tear it down with pdeathsig and child_pre_dead recorded | `tools/kama-ollama-live.py`; `.ufo/waves/round-61/live/receipt.json`; `registry/ollama-live-claims-r61.tsv` | 61 |
```

- **Line 137 (`## Saturation`)**, three substitutions in the same paragraph:
  - `47 (highest canonical list)` → `47, 61 (highest canonical list)`
  - `(kept current in round 49)` → `(kept current in round 63)`
  - `The last capability entered in round 47 is older than the N=4 stagnation window; the nudge remains inactive solely because the lowest assigned axis remains below saturation.` → `The last capability entered is live-ollama-lifecycle (round 61), inside the N=4 stagnation window; nudge inactive, because the lowest assigned axis, calibration 7, remains below saturation.`

- **Line 17 (`## Axes`, coverage row)**, two substitutions:
  - `→ `36` (round 60 added `corpus/knowledge/ollama-live-lifecycle.md`)` → `→ `38` (round 60 added `corpus/knowledge/ollama-live-lifecycle.md`; round 61 added `corpus/knowledge/ollama-live-amendment-r61.md`; round 62 added `corpus/knowledge/completion-request-plane.md`)`
  - `` `PROVINCE.md` sha256 `a60591b77ac8a8f0bd90f3436d75fc8cbe1fbab820d37e6f57b0e386c32a01a9` (188 lines) `` → the new PROVINCE.md sha256 and line count from B1.

### B3. SCORECARD.md tail

Part A (above) is appended after the last line of the file, after one blank line.

## Notes for the L1 (not part of the text)

- The working tree differs from the tip: `PROVINCE.md` (190 lines, a round-63 note that is not at the tip) and `corpus/SOURCES.md` are modified uncommitted, and the draft was cut against tip blobs. If the L1 commits the working-tree `PROVINCE.md`, the coverage row's hash and line count must be recomputed from the committed file, and B1's paragraph must be merged into it instead of appended.
- If a verdict moves a score, edit the Saturation vector and nudge line as well (the reconciler checks the vector string in head-table order).
- If C1 is `met=True` and the L1 admits `live-completion-request-plane`, the head mirror, Retired count (13), Saturation first-working list (add its round), and PROVINCE must change again; the reconciler then needs the new names in whichever canonical list the L1 designates. The freeze does not say which list; this is for the L1 to decide. A new `## Round 64` heading would move maxN and the required Planned heading to round 65.
- Re-running `tools/round63-c2-counter.py` at any later tip fails on `newest canonical list is round N` if a higher canonical list is added. That is the frozen rule, not a defect; record measurements at their measured tip.
