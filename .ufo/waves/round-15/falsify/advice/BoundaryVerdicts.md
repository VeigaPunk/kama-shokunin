# BoundaryVerdicts — outside R1 discovery versus author repair

Seat: `KamaR15.BoundaryVerdicts` (falsification connector, leaf). Scope: attribution boundary between the outside R1 finding and the author-side repair of the R1 duplicate-corpus guard. Read-only. No gate, test, runner, harness or classifier was executed. No file was edited except this report. No tool was installed or updated. No pacman transaction, no history/session/credential access.

Reads and metadata only: file reads, `sha256sum`, `diff` of two files, read-only `git rev-parse` / `git cat-file` / `git show` for blob identity, and one read-only JSON projection of `.ufo/waves/round-14/acceptance.json`.

## Axes

- **calibration** (claim strength versus evidence strength): primary axis for this attack.
- **discernment** (who decided what; outside versus author credit): secondary axis.
- **quality/provenance** (receipt bytes and frozen source identity): checked, no finding.

## Verified, no defect

1. **R1 discovery is genuinely outside.** `corpus/lessons/round-14-verifier-spotcheck.md:1-5` names the reviewer `CloseKamaR14`, the closure author as `hyaku closure (non-author integrator)`, and says the review was dispatched by the orchestrator, not the lane. R1 is at line 142. Author repair is `GuardRepair-3` (`build/advice/GuardRepair.md`), a round-15 lane seat. The discovery and the repair are on different sides of that boundary, and the round-15 lesson, LOG, QUALITY, and TrendMap credit them that way (`corpus/lessons/round-15.md:7`, `LOG.md:856-859`, `corpus/QUALITY.md:81-87`).
2. **Repair stays inside the outside-R1 predicate.** `diff .ufo/waves/round-15/frozen/measure-before.py .ufo/waves/round-14/measure.py` shows exactly two added lines, at 358–359: `if len(declared) != unique:` / `problems.append("duplicate case names")`. The frozen file's sha256 is `fda61e00…`, matching `frozen/manifest.json` and `git rev-parse 6e348e28…:.ufo/waves/round-14/measure.py` (blob `78300456…`). The same blob exists at `e545ed99…`, which the lesson cites as the measured revision, so no revision mismatch in the bytes.
3. **Historical receipt is byte-intact and the cited locators are right.** `sha256sum .ufo/waves/round-14/acceptance.json` = `fdf90a5d…`, identical to `git show HEAD:`. A read-only JSON projection shows `records[0..2].parsed.limits[3]` and `causal_red.parsed.limits[3]` each carry the false sentence; `records[3]` has no `limits`; the top level has no `limits` key. The R1 correction's locators are correct.
4. **No seat or author claims outside admission for C1.** `SCORECARD.md` round-15 section defers to "independent non-author round15 admit/reject sampling" (planned). `build/advice/QualityCriterion.md:81-82` and `TrendMap.md` say discovery credit stays with the round-14 verifier and this append claims no C1 credit. `integration-review.json` `outside_review` correctly says author-dispatched advice is not admission. Gate row "admit conditional on measured red/green" (`lesson:15`) is the author gate, grounded on "Outside R1", not an outside verdict.
5. **Outside R1 is not an executed observation.** The original sentence `[INFERENCE from static code]` at `round-14-verifier-spotcheck.md:142` is preserved in the seats' copies. I reproduced the static reading: `corpus_problems` (`measure.py:350-364`) computes `unique = len(set(declared))` and tests only `unique < MINIMUM_UNIQUE_CASES` before the repair; nothing compared `len(declared)` with `unique`. That reading is correct. It is still static.

## Findings

### F1 — Lesson presents the outside finding as demonstrated (calibration, low–medium)

- `corpus/lessons/round-15.md:7`: "Outside R1 found a real executable defect: the runner's minimum unique-name check does not reject duplicates…"
- Source label: `round-14-verifier-spotcheck.md:142` says `[INFERENCE from static code]`, and the spot-check itself says "not executed".
- No execution of the frozen runner against a duplicate corpus is recorded anywhere in the round-14 receipts. The first demonstration is the round-15 red matrix, which has not been run in this wave.
- Consequence: the lesson upgrades an outside static inference to an executed defect. The static reading is right, so the harm is in claim strength, not in the repair. The round's red/green evidence is what should carry "demonstrated".
- Bounded fix (prose only, new round-15 text, no old bytes): "Outside R1 identified, by static reading, a defect…; the frozen red measurement below is the first executable demonstration."

### F2 — Repaired runner still states the broader promise; TrendMap E12(a) overstates closure (calibration, medium)

- `measure.py:13-14` and `LIMITS[3]` at `:77` still read, unqualified: "duplicated corpora fail before any child runs".
- After the two-line repair, `corpus_problems` (`measure.py:353-355`) keeps only non-blank `str` names in `declared`. `case_name` (`:131-136`) then labels blank or non-string names `case-NN`.
- Concrete counterexample from source, not executed: a corpus with 16 distinct non-blank names plus two fixtures named `""` (or `"   "`). `declared` has 16 entries, `unique == 16`, so `len(declared) != unique` is false and `unique < 16` is false. `run()` (`:374-380`) takes the `elif tool_present:` branch and calls `measure_case` for every fixture, including both blank-named ones, under labels `case-NN`. Children spawn. The docstring promise "duplicated corpora fail before any child runs" is false for this corpus.
- The lesson does disclose blank names as out of the R1 repair (`round-15.md:88-91`: "Missing/blank/non-string fixture-name validation … explicitly outside the declared R1 duplicate-declared-name repair"). That disclosure is in the lesson only.
- `build/advice/TrendMap.md` E12(a) says "The current runner docstring and LIMITS are true once the guard is in place." That is false for the blank-duplicate class, as shown above. E12 is a seat's advice, not a committed ledger, but it reads as a closure check.
- KQ18 (`corpus/QUALITY.md:87`) requires "name injectivity over stripped names" as an independent conjunct. The repair enforces injectivity only over non-empty stripped names. Whether `""` is a "stripped name" for KQ18 is not defined in the text; the ambiguity should be resolved in the words, not by code.
- Scope note: the assignment bounds the repair to "exactly two lines". This finding does not ask for a validation expansion. The bounded options are (a) narrow the runner's docstring and `LIMITS[3]` to "duplicated non-blank declared names" in a separately approved prose edit, or (b) keep the runner text and add an explicit blank-duplicate exception sentence to the round-15 lesson's R1 paragraph. Option (b) needs no code change. Do not claim the runner's current prose is fully true.

### F3 — S034 search-log supplement omits the outside trigger (discernment, low)

- `corpus/SOURCES.md` round-15 search-log supplement (around :83–92) frames the question as lane-originated: "Question: does the original measurement guard enforce its duplicate-rejection promise…". It does not mention R1 or CloseKamaR14.
- `grep "R1" corpus/SOURCES.md` returns no S034 match; the S034 row (`:46`) does not name R1 either.
- The lesson (`round-15.md:62-64`) and SCORECARD (`:504`) credit the trigger correctly. Only the registry text drops it.
- Bounded fix: one appended sentence in the search-log supplement, "question routed by outside R1 (CloseKamaR14); S034 carries no discovery credit", as `TrendMap.md:50` already proposes. Prose append only.

### F4 — Outside locator is a different predicate (discernment, low; no repair dependence)

- R1 (`round-14-verifier-spotcheck.md:142`) cites "Tool selftest independently checks duplicates at :359–365" as corroboration.
- Actual classifier selftest (`tools/kama-ollama-evidence.py:360-365`): names are filtered by `case.get('name') != ''` with **no strip**, and the duplicate test is at `:364-365`. The runner's guard uses **stripped** names (`measure.py:353-355`). These are different predicates.
- The round-15 lesson does not lean on the selftest as corroboration (`QualityCriterion.md:61` cites it, while `ReceiptReview.md:77` correctly says it is out of scope). Do not cite the classifier selftest as independent evidence for the runner guard.

### F5 — Round-15 gate table has no "decided by" column (discernment, low)

- `corpus/lessons/round-15.md:12-19` mixes author decisions ("admit conditional on measured red/green", "reject") with outside grounding ("Outside R1", "Outside review independently recounted"). No column names the decider.
- Reader can mistake the author gate for an outside verdict. The round text disclaims outside sampling later (`:53`, "outside review is still required"). Bounded fix: add a "Decided by" column or one sentence above the table: "author gate; outside sampling pending".

## Not findings (checked)

- Receipt sha and limits locators: correct (verified above).
- Frozen manifest sha and `measure-before.py` identity: correct.
- Guard placement: the corpus branch runs before the `tool_present` branch, so duplicate rejection precedes any `measure_case` call for declared-duplicate corpora. Static reading only; not executed.
- Spot-check file read-only: `git status` lists it as unmodified.
- `tests/ollama-corpus-guard/` now exists (13 files); not reviewed here, outside this attack's scope.

## Verification the main agent should run (not run by this seat)

1. Red/green on a corpus of 16 distinct non-blank names plus one `""`-named duplicate, to confirm or refute F2 by execution. A pass on this case would mean the runner still spawns children for blank duplicates, which is the expected outcome of the repair as scoped.
2. Confirm `git show HEAD:corpus/lessons/round-14-verifier-spotcheck.md` still matches the working tree (no change by this wave).

## Limits

- Static reading only. The blank-duplicate counterexample is `[INFERENCE from static code; not executed]`.
- Did not read `tests/ollama-corpus-guard/*.json` or `check.py` in detail; F2's disposition may depend on whether a blank-duplicate control exists there (`check.py:166` rejects non-string names in a matrix, which is a harness-side check, not the runner's).
- No outside non-author admission authority is claimed or implied by this report.

Report: .ufo/waves/round-15/falsify/advice/BoundaryVerdicts.md
