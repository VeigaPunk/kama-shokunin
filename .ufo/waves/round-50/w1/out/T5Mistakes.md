# T5Mistakes — round 50 mistake-mining sweep (closures 45–49)

**Verdict: 6 rows proposed, all new; 3 routed items still have no committed carrier, and two of the prior sweeps' "dropped" verdicts are false — `corpus/README.md` carries them.** Calibration finding: the lane's capture medium for carried items is the README frontier disposal, which no sweep searched and no check compares.

Seat: T5Mistakes (scribe, calibration), leaf, read-only. Snapshot: `git clone --shared` of the lane at `3b79eadd` (round-50 build `97c864be`, freeze `601c8889`), HEAD at read time. No counter run, no lane write, no git/jj mutation, no service started. Detail and the full ledger: `.ufo/waves/round-50/w1/out/T5Mistakes/sweep.md`.

## 1. What the sweep checked

Ledger: every routed item in `corpus/lessons/round-{45..49}-verifier-spotcheck.md` §Routed defects — r45 `:146-150`, r46 `:137-142`, r47 `:97-105`, r48 `:110-121`, r49 `:103-108` — against every `## Mistakes` row (r45 `:27-31`, r46 `:35-42`, r47 `:45-50`, r48 `:28-32`, r49 `:34-38`), QUALITY `KQ70-KQ79` (`corpus/QUALITY.md:397-424`), prereg `limits`, and `corpus/README.md` §Frontier disposition.

```
grep -n '^|' corpus/lessons/round-4[5-9].md
grep -nE '^\s*(-|[0-9]+\.)\s*\**\**[DR][0-9]' corpus/lessons/round-4[5-9]-verifier-spotcheck.md
grep -rn '<id>' corpus/ registry/
python3 .ufo/waves/round-50/w1/out/T5Mistakes/checks.py --repo <clone> --rev 3b79eadd    # exit 1
```

Result: 30 closure items, 32 ledger lines after splitting r46-D3 and r48-R5. 19 carry a Mistakes row or a KQ; 13 do not — 6 with a committed non-row carrier (3 README frontier, 2 prereg limits, 1 policy disclosure), 4 in flight (r49-R1…R4, closed by the build, rows due in the round-50 lesson), 3 with no carrier at all: r46-D3's two named sub-gaps, r46-D4's rule, r47-D2. Operator lines excluded.

## 2. Proposed rows (all new; full text and evidence in `sweep.md` §4)

| # | Class | Defect (file:line) | Fix shown able to fail |
|---|---|---|---|
| F1 | `label-drift` | `.ufo/waves/round-50/spec.json` item `T4Lesson` writes "round-49 closure R2/R3 (report placeholders and census paraphrase)" and "round-49 closure R4-style source-count mistake". Those are **round-48** items (`round-48-verifier-spotcheck.md:111-113`), already rows 1–3 of `round-49.md:34-36`; round-49 R2/R3/R4 are teardown, C2 definitions, mutation survivors (`round-49-verifier-spotcheck.md:104-106`). The brief also never asks for a row on **r49-R1** (pid join / canaries / model binding), the defect this round's C1 claim closes. Spec item `X12Zip` has the same drift by hand ("Record-time archive bounds (round-49 closure R1)" = round-48 R1) | `checks.py` check A → `FAIL (2 finding(s))`, exit 1; same run passes `T1Log` (its seats K1Cheat/K1Design/R0Controls/X1Kill/K2Origin/K2Cheat/V2Ctr are exactly r49-R1/R2/R3), so it is not blanket-failing (`checks.out` §A) |
| F2 | `fix-without-mechanism` | `round-48.md:31` fixed dropped routed items with a prereg `routed` block. `.ufo/waves/round-49/preregistration.json` and `round-50/preregistration.json` key sets both lack `routed`/`carried` (r50 keys: lane, round, attempt, author, frozen_at_utc, base, authority, separability, claims, controls, limits) | `checks.py` check B: round-48 `has_routed=True` (8 lane items), round-49 `False` (3), round-50 `False` (5) → exit 1 |
| F3 | `sweep-not-consumed` | `.ufo/waves/round-49/w1/out/N5Mistakes/sweep.md` (12 findings) is cited by no committed `corpus/` or `registry/` file; the round-48 sweep is (`round-48.md:31`) | `checks.py` check C: round-48 `cited=True`, round-49 `False` → exit 1 |
| F4 | `sweep-verdict-stale` | round-49 sweep F9 (`sweep.md:99`) says `tools/sources-append-only.py` is "unfixed … never integrated"; the repair is commit `c4b2175d` (round-48 integration, "sources guard repair") and the tool passes today. `round-47.md:49` still reads "Not fixed this round"; `c4b2175d` is cited only by `round-48-verifier-spotcheck.md:42,60` and by `grep -rn c4b2175d corpus/lessons/round-4[7-9].md` → 0 | pre-repair tool (`git show c4b2175d^:tools/sources-append-only.py`) on the r45 lesson's failing pair: `error: 052cb1e9:corpus/SOURCES.md:514 … refusing to drop it`, `exit=2`; tip tool on the same pair `exit=0`, `--selftest` `45/45`, `exit=0` (`sources-guard*.out`) |
| F5 | `scoped-grep-false-negative` | round-48 F1/F5 and round-49 F1/F5 published "dropped / never tracked" from greps scoped to `corpus/lessons/` + `registry/`; `corpus/README.md:755` carries r45-D1, `:719` floating-series, `:1068-1069` and `:1233-1234` S013/S022/S002–S004 | `grep -rn 'floating-series' corpus/lessons/ registry/ \| wc -l` → 2; `grep -rn 'floating-series' corpus/` → 5, incl. `corpus/README.md:719`; `grep -n 'Round-45 D1' corpus/README.md` → `755` |
| F6 | `closed-without-capture` | r46-D4 (hexrun rule), r47-D2 (replay all receipts), r47-D8's repair closed by commits, recorded in no lesson row; KQ75 covers the projection not the receipt count, KQ55 predates the ledger-row rule | `grep -rn 'c4b2175d' corpus/lessons/round-4[7-9].md` → no output (exit 1) |

## 3. Items deliberately left without a row (calibration)

r45-D1, r47-D7, r48-R5 record-time/sub-20, r49-R5 — each has a committed disposition (README frontier or prereg `limits`); a row would restate a declared limit. r48-R5 mutants and r49-R4 — disclosed by policy, and round 50 runs four mutation seats. r49-R1/R2/R3 — in flight; **F1 is the warning that the lesson brief does not ask for R1 and mislabels R2/R3**. Operator/L0 lines (r45-#5, r46-D6, r48-R4 doc correction, r49-R6) are correctly never lane rows. Known integration items from the seat brief are not re-reported.

## 4. Limits of this sweep

- The round is in flight: reads are at `3b79eadd`, not the integration tip; the round-50 lesson, SCORECARD/LOG/README entries and the `used-by` of S496–S498 do not exist yet. F1's consequence is a prediction about the lesson, not an observed row error.
- Check A resolves descriptors and seat lists; it does not judge whether a correct-looking citation supports the seat's claim. The `X12Zip` instance is hand-read.
- F5's flip is about carriers that exist; it does not establish that the README disposition is sufficient for the dropped-item rule.

## 5. Paths

- `.ufo/waves/round-50/w1/out/T5Mistakes/sweep.md` — full sweep, ledger, findings, proposed rows.
- `.ufo/waves/round-50/w1/out/T5Mistakes/checks.py` — four fail-capable checks (A–D), read-only `git show`.
- `.ufo/waves/round-50/w1/out/T5Mistakes/checks.out` — exit 1, findings per check.
- `.ufo/waves/round-50/w1/out/T5Mistakes/sources-guard.out` — repaired guard: `exit=0`, `45/45`, round-50 window adds S496/S497/S498.
- `.ufo/waves/round-50/w1/out/T5Mistakes/sources-guard-pre-repair.out` — pre-repair guard: `exit=2`.

No tool was installed or upgraded. Scratch `/fast/scratch/hyaku/kama-r50/T5Mistakes` deleted after use; no `llama-server` was started, so none is left behind.
