# WR04ScorecardDraft — round-63 scorecard append and head re-derivation (drafting item, calibration)

Seat: WR04ScorecardDraft (leaf, advisory). Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09` (lane HEAD, = round-63 amendment 1 commit). No measurement of C1/C2 was run (not this item's assignment; counters are launched only by the L1). `SCORECARD.md` was not edited; no lane commit, no lane git mutation. Scratch clones lived under `/fast/scratch/hyaku/kama-r63/w/WR04ScorecardDraft` and were removed before this report.

Deliverable: `.ufo/waves/round-63/w1/out/WR04ScorecardDraft/scorecard-append.md` (Part A = text appended to SCORECARD.md; Part B = the exact head and PROVINCE replacements).
Machine form: `.ufo/waves/round-63/w1/out/WR04ScorecardDraft/apply-selfdesc-r63.py REPO` (run only on a scratch clone; it reads Part A from `scorecard-append.md`, asserts every old string occurs exactly once, and writes nothing on drift).

## 1. Reconciler at the tip (read-only, `--repo` = lane, `--tip` = 03a6a1d)

Receipt: `out/WR04ScorecardDraft/reconcile-tip-03a6a1d.out`.

```
tip=03a6a1d850902a66a13dfad33f89cf3a8b759a09
r41=1 banner=1 planned=2 retired=1 saturation=1 caps=1 receipts=0 readme=0 province=1 rel=0 mismatches=8 maxN=63 met=False
```

Round-41 counter, imported by the reconciler, reports one of its own facts (`r41=1`): `axes=6 facts=37 ... run_bad=1 ... mismatches=1 met=False`.

Every failing fact, with its file, the tip line range it lands on, and the replacement:

| # | Fact (detail line) | File : tip lines | Replacement (what the draft does) |
|---|---|---|---|
| 1 | r41 coverage run prints 38, not `36` | `SCORECARD.md` 17 (`## Axes`, coverage row) | `→ \`36\`` → `→ \`38\`` with the round-61 and round-62 knowledge files named (the tree holds 38 `corpus/knowledge/*.md` after the filter; `ollama-live-amendment-r61.md` came in `7848fbea`, `completion-request-plane.md` in `dc5e1010`). The same row's PROVINCE.md sha256/line count is re-derived too (see 8). |
| 2 | banner: head lacks `Latest measured round: 63` | `SCORECARD.md` 6 (whole banner line, before first `## `) | Whole line replaced with the round-63 banner (`Current authority (round 63)`, `Latest measured round: 63`, scores held at 8/7 pending verdicts). Keeps `operability + calibration`; contains neither forbidden phrase. |
| 3 | planned: `## Planned` section does not name `### Planned (round 64)` | `SCORECARD.md` 51–53 (`## Planned` body, sentence on line 53) | `Superseded in round 42. The live plan is ### Planned (round 61) below; …` → `The live plan is \`### Planned (round 64)\` at the end of this file, after §Round 63 measured results; …` |
| 4 | planned: no line `### Planned (round 64)` followed by a numbered item | end of `SCORECARD.md` (after line 3320) | Part A appended: `### Planned (round 64)` heading, next non-blank line `1. Operability (C1) …`, six numbered items. |
| 5 | retired: does not state `12 capabilities` | `SCORECARD.md` 57 (`## Retired`) | `None. 6 axes and 11 capabilities remain active.` → `None. 6 axes and 12 capabilities remain active.` |
| 6 | saturation: does not state `first-working rounds 10, …, 47, 61` | `SCORECARD.md` 137 (`## Saturation`) | `47 (highest canonical list)` → `47, 61 (highest canonical list)`; `(kept current in round 49)` → `(kept current in round 63)`; the stale "last capability entered in round 47 … older than the N=4 window" sentence → "last capability entered is live-ollama-lifecycle (round 61), inside the N=4 window; nudge inactive, because … calibration 7, remains below saturation." |
| 7 | caps: head mirror names 11 capabilities; canon (round 63) names 12, missing `live-ollama-lifecycle` | `SCORECARD.md` 117 (intro) and insert after 131 (`live-receipt-replay` row of the mirror) | Intro: `Mirror of the round-49 canonical capability list that §Round 49 carries` → `Mirror of the round-63 canonical capability list that §Round 63 carries`. Insert after line 131 a verbatim copy of round-63 canon row (tip line 3320): `\| live-ollama-lifecycle \| Start the pinned Ollama v0.40.11 binary … \| \`tools/kama-ollama-live.py\`; \`.ufo/waves/round-61/live/receipt.json\`; \`registry/ollama-live-claims-r61.tsv\` \| 61 \|`. |
| 8 | province: `PROVINCE.md` lacks `registry/ollama-live-claims-r61.tsv` (canon row evidence) | `PROVINCE.md` end of file (tip has 188 lines) | Append one paragraph (blank line, then `**Round-63 claim tables — provenance (2026-10-28).**`) naming `registry/ollama-live-claims-r61.tsv`, `registry/capability-claims-r63.tsv`, `tools/round63-c1-counter.py`, `tools/round63-c2-counter.py`, `tools/kama-completion-live.py`. File becomes 190 lines; sha256 `6fcc474ba627144b3d83561252e415e4af583c838be9ef6a9049a95266790a77` in the scratch test. Fact 1's coverage row must carry this new hash and line count. |

Facts that already pass at tip and must stay untouched: `readme=0` (no new top-level entries), `receipts=0` (the draft adds no `.ufo/` tokens under a round-40/41 heading), `rel=0` (each axis row's run fact is unchanged), and the `## Axes` score vector (`operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7`).

## 2. Verification of the draft (scratch clones, deleted afterwards)

Clone of the lane at the tip, `git clone -q --shared`, `rev-parse --show-toplevel` asserted; `apply-selfdesc-r63.py` run on the clone; one scratch commit by `seat <seat@seat.invalid>` in the clone only.

```
applied: PROVINCE.md sha256=6fcc474ba627144b3d83561252e415e4af583c838be9ef6a9049a95266790a77 lines=190
tip=44e1a4039a1ef5669daaaa00ee40865fff7e5ad2
r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=63 met=True
axes=6 facts=39 hash_bad=0 lines_bad=0 run_bad=0 dead=0 score_bad=0 hollow=0 mismatches=0 met=True
```

Receipts: `reconcile-applied-draft.out`, `r41-applied-draft.out`, `applied-draft.diff` (the SCORECARD + PROVINCE diff, 91 lines).

The C2 counter's canonical-list rule was checked in-process by importing `canon_problems` from `tools/round63-c2-counter.py` (no live run): tip → `canon_round 63 rows 12 problems []`; applied scratch → `canon_round 63 rows 12 problems []`. Receipt `c2-canon-parse-check.out`. The head mirror insertion therefore does not change what the counter resolves.

Also checked: `maxN` stays 63 (Part A introduces only `### ` headings, no `## Round 64`), so the required planned heading is round 64; the head section `## Planned` contains the pointer text and the body contains the exact numbered block.

Caveat on the check itself: the reconciler verifies that the Planned heading exists and is followed by a numbered item. It does not check the placeholders `<C1_LINE>`, `<C2_LINE>`, `<TIP>` in the measured-results block. They must be filled from the real counter output by the L1; the script does not do it.

## 3. Part A — the measured-results and planned blocks (summary; full text in scorecard-append.md)

- `### Round-63 measured results`: one bullet per counter with the exact command, `→ <C1_LINE>` / `→ <C2_LINE>`, receipt paths `.ufo/waves/round-63/measured/c{1,2}-final.{out,exit}`, the measured tip `<TIP>`, and the frozen admission rule (a claim is admitted only when its counter line prints `met=True` with exit 0).
- `### Planned (round 64)`, six numbered items: (1) settle the C1 verdict through a non-author falsification wave, SURVIVED mutants become first repair targets; (2) C1 admission path, which the freeze does not name for `live-completion-request-plane` (the frozen list excludes it); (3) C2 repair limited to the named family/mismatch if `met=False`, or a non-author fifth planted defect if `met=True`; (4) run both reconcilers at every closure commit (the round-41 coverage row sat at 36 while 38 files were in the tree); (5) land `corpus/lessons/round-63.md` (absent at tip, promised by the freeze); (6) resolve the lane worktree ownership (round-62 routed defect 3).

## 4. Notes for the L1 (decisions the draft does not make)

1. **Working tree vs tip.** The lane worktree has uncommitted `PROVINCE.md` (190 lines, with a round-63 note not in the tip), `corpus/SOURCES.md` and `corpus/knowledge/completion-request-plane.md` modifications, and untracked round-63 paths (`.ufo/waves/round-63/w1/`, `.ufo/waves/round-63/source/`, `w1.ready*`, and a nested `kama-shokunin/` entry). The draft was cut against tip blobs, because the reconciler reads tip. The working-tree `SCORECARD.md` is byte-identical to the tip (md5 `4bd1579d…`), so it is not a problem. If the L1 commits the working-tree `PROVINCE.md`, merge fact 8's paragraph into it and recompute the coverage row's sha256 and line count from the committed file.
2. **Score moves.** The draft keeps operability 8 / calibration 7. If a verdict moves a score, the Saturation vector and nudge sentence must move too (the reconciler checks the vector in head-table order).
3. **C1 admission.** If C1 prints `met=True` and `live-completion-request-plane` is admitted, the head mirror (+1 row), Retired (`13 capabilities`), Saturation (+ its first-working round), PROVINCE and the canonical list all change. The freeze says the capability "enters the canonical list only if C1 verifies" but does not say which list; that is for the L1 to decide. A new `## Round 64` heading would move maxN and the required Planned heading to round 65.
4. **Later C2 re-runs.** `round63-c2-counter.py` fails `newest canonical list is round N` at any later tip that adds a higher canonical list. That is the frozen rule; record each measurement at its measured tip.

## 5. Host and tool record

- No tools installed or upgraded. Used only `git` (clone, cat-file, show, status, log, diff, rev-parse on the lane and on the scratch clone), `python3` stdlib, and the lane's own reconciler/counter modules (in-process import, no live server).
- No pacman transaction, no write to `~/.local/bin` or any PATH directory, no write to the fleet root, no write to another seat's files, no contact with any port.
- No write to `SCORECARD.md`, `PROVINCE.md` or any lane tracked file. Written only: `.ufo/waves/round-63/w1/WR04ScorecardDraft.md` and `.ufo/waves/round-63/w1/out/WR04ScorecardDraft/` (scorecard-append.md, apply-selfdesc-r63.py, receipts).
- Scratch `/fast/scratch/hyaku/kama-r63/w/WR04ScorecardDraft` removed (`SCRATCH_REMOVED`).
- Working-tree git state was only read (`git status`, `git diff --stat`); the lane's index and branch were not touched.

## Tally

`reconcile tip=03a6a1d mismatches=8 met=False` (r41=1 banner=1 planned=2 retired=1 saturation=1 caps=1 province=1); draft applied to a scratch clone: `reconcile mismatches=0 met=True maxN=63`, `r41 facts=39 mismatches=0 met=True`.
