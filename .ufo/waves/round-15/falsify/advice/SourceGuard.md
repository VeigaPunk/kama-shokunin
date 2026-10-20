# SourceGuard — S034 anchor: diagnosis support, not repaired outcome

**Verdict: PASS (high confidence).** S034 landed at `corpus/SOURCES.md:46` and is
committed at HEAD `70af36c`. Its anchor is byte-exact against the pinned start
commit and demonstrates the *original* guard predicate, not the round-15 repair.
No S034 cell or citation claims a repaired or measured outcome.

## 1. Landed row (observed)

`git show HEAD:corpus/SOURCES.md` line 46, identical to the working-tree read:

- id/source: S034, `own-work`, tier `A`, status `mined`, recheck `every round`,
  used-by `corpus/lessons/round-15.md`.
- source cell: `.ufo/waves/round-15/frozen/measure-before.py`
  ("preserved exact baseline of `.ufo/waves/round-14/measure.py`").
- anchor cell: "`corpus_problems` lines 350–362 of
  `.ufo/waves/round-14/measure.py` at start commit 6e348e2, opened 2026-10-20".
- teaches cell: rejects only `if unique < MINIMUM_UNIQUE_CASES:`; never compares
  declared vs unique; >=16 distinct stripped names plus duplicates passes
  preflight — "the defect C1 repairs".

## 2. Exactness chain (observed)

| Artifact | sha256 |
|---|---|
| `.ufo/waves/round-15/frozen/measure-before.py` (worktree) | `fda61e00…b60d` |
| same path at HEAD `70af36c` (`git cat-file blob`) | `fda61e00…b60d` |
| `frozen/manifest.json` `sha256` | `fda61e00…b60d` |
| `git cat-file blob 6e348e2:.ufo/waves/round-14/measure.py` | `fda61e00…b60d` |

`frozen/manifest.json` records `source_commit
6e348e28943849aceb08d6954dee92be48ce9ba8`, `source_path
.ufo/waves/round-14/measure.py`, and the same digest. `6e348e2` is the parent of
HEAD `70af36c` (`git log --oneline -3`), so "start commit" is literal.

Line span verified on the frozen bytes (`:raw` read, lines 345–365):
`def corpus_problems(cases):` at 350, `if unique < MINIMUM_UNIQUE_CASES:` at
358, `return problems, unique` at 362. The anchor's "lines 350–362" delimits
exactly the function, and the quoted predicate is at the stated line 358.

## 3. The baseline supports the diagnosis (observed)

- `grep -c 'len(declared)'` on the frozen baseline: **0**. The declared-vs-unique
  comparison does not exist in the baseline.
- `load_cases` (frozen 109–131) performs JSON shape checks only; no name
  uniqueness test. `case_problems` (139–151) checks `expect`, `expected_exit`,
  `expected_finding` only; no name test. So nothing upstream rejects duplicates.
- `corpus_problems` builds `declared` from stripped non-blank names and computes
  `unique = len(set(declared))`; its only problem is
  `unique < MINIMUM_UNIQUE_CASES` (16, frozen line 66).
- `run()` calls `corpus_problems` before any child handling (frozen 372–384):
  a non-empty `corpus` yields `unmeasured_record` per case; the child loop
  (`measure_case`) is on the `elif tool_present` branch only. Therefore a
  duplicate corpus with >=16 unique stripped names passes preflight and reaches
  child execution — exactly the row's claim.
- The baseline's own docstrings promise the opposite (frozen line 14 "duplicated
  corpus fails the whole measurement before any child is spawned"; LIMITS line 77
  "narrower or duplicated corpora fail before any child runs"). The code does not
  implement that promise. This is the documented defect, and S034 cites the code,
  not the promise.

## 4. Repaired outcome is excluded from the anchor (observed)

The working tree changed while this seat read it: HEAD advanced from `6e348e2` to
`70af36c` ("round-15: enforce duplicate corpus admission before replay children").
At HEAD, `.ufo/waves/round-14/measure.py` is sha256 `46c5866d…5257` (size 17214;
baseline is 17134), and its lines are:

- 358: `if len(declared) != unique:`
- 359: `problems.append("duplicate case names")`
- 360: `if unique < MINIMUM_UNIQUE_CASES:`

So the *live path* at current HEAD, read line-for-line, now shows the repair and
the diagnosed predicate has shifted to 360. S034 remains diagnostic only because
its anchor pins `6e348e2` and its source cell points at the frozen copy (tracked
at HEAD, digest matching the pinned blob). Any reader who drops the commit
qualifier and opens the path at HEAD sees the repaired outcome instead of the
diagnosis. That is an anchor-precision observation, not a defect in the row as
written.

## 5. Citation scope (observed)

Every S034 mention frames diagnosis, never repair/measurement:

- `corpus/SOURCES.md:85` — "supports the original guard diagnosis".
- `corpus/README.md:199` — "supports the actual guard diagnosis".
- `SCORECARD.md:504` — "S034 records the original predicate supporting outside
  R1's diagnosis".
- `corpus/lessons/round-15.md:64` — "C1 rests on S034 plus the actual outside R1
  and the new fail-capable measurements".
- `corpus/lessons/round-15.md:57–61` — quote line 358, states "not a measured
  repaired outcome or independent source authority".

No cell cites the repaired runner, the fixture set, or a run result as S034
support.

## 6. Bounds and remaining unknowns

- No checks, tests, builds, or gates were run; no files edited except this report.
- Not adjudicated here: tier-A admission for an own-work code row (SourceReview
  F5), and the `every round` recheck cadence for an immutable baseline (also F5).
  Those are admission questions, not anchor-support questions.
- Not verified here: correctness of the committed repair itself (`70af36c`); that
  belongs to C1/R2 owners and L1 execution.
- Residual risk: the anchor's path-level line numbers are only stable under the
  `6e348e2` qualifier now that HEAD carries the repair. Evidence above shows the
  qualifier is present and the frozen digest is committed, so the diagnosis is
  reproducible without it being conflated with the repaired outcome.
