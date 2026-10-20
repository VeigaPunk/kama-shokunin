# FalsifyMeasurement — corpus outer error vs per-case finding vs total child count

Seat `KamaR15.FalsifyMeasurement` (critic, leaf). Target: the final committed candidate at HEAD `70af36c`. I executed no gate, harness, runner, classifier, test or build. My only commands were reads, `git show --stat/diff` and `jq` metadata counts over `tests/ollama-corpus-guard/*.json`. I installed nothing: pacman is paused, and nothing else was needed.

Sources read:
- `.ufo/waves/round-14/measure.py#6643`: the guard diff is exactly `:358-359`.
- `tests/ollama-corpus-guard/check.py#2C84` (746 lines).
- All 13 matrix files.
- Receipt text: `corpus/lessons/round-15.md`, `corpus/QUALITY.md` KQ18, `SCORECARD.md:483-505`, `LOG.md:856-880`, `SKILL.md:488-505`, `corpus/knowledge/ollama-evidence-replay.md:320-351`.
- Build advice: `FindingExit.md`, `MeasurementPlan.md`, `ReceiptReview.md`, and `integration-review.json`.

## Axes

- **Calibration (C1, 7→7).** Layer attribution: the outer error, the per-case finding and the child count must not stand in for one another.
- **Operability (8, no regression).** The valid-control measurement still passes.
- **Provenance.** Receipt numbers are anchored to the field that actually measures them.

## How the three quantities appear in the final code

| Quantity | Runner (`measure.py`) | Harness assertion (`check.py`) | Distinguished? |
|---|---|---|---|
| Corpus outer error | `result["error"] = "corpus: " + "; ".join(corpus)` at `:421-422`. Set only on corpus rejection; absent on measured runs. | Rejected rows: `isinstance(error,str) and DUPLICATE_REASON in error` at `:537`, a **substring** match. Valid rows: `error` is **not asserted absent**, only recorded at `:516`. | Yes on rejected rows, but loosely (F1). |
| Per-case finding | Corpus branch `:378-380`: `unmeasured_record(case, index, corpus_detail, None)`, so `observed_finding` is `None` (`:168`), `reasons == [corpus_detail]` and `observed_exit` is None. The tool-absent, timeout and staging paths use `unsupported_record`, so `observed_finding == "unsupported"` (`:186`). | Rejected rows: only `null_observed_exit_records == total` at `:558`. `observed_finding` and per-record `reasons`/`detail` are **not asserted**. Valid rows: indirect only, through the runner's self-reported `passed == total`. | **No on rejected rows (F2).** The full runner JSON is retained in `runner_result` (`:617`), so the distinction can be recovered at receipt level. |
| Total vs child count | `total = len(records)` at `:414`. On rejection it equals `len(cases)` with zero children, and `failed == total` counts unmeasured records. The runner has no child-count field. | Separate quantities:<br>• `expected.total`/`observed.total`: runner record count.<br>• `classifier_invocations` (marker) at `:503`, duplicated as `child_count` at `:615`.<br>• `runner_process_events` / `runner_popen_events` from the audit hook.<br>Rejected rows assert total == N and marker 0, events 0, Popen 0 (`:558-575`). Valid rows assert marker == Popen == N (`:596-603`). | **Yes.** A receipt can still conflate them (F3). |

## Findings

### F1: outer error matched by substring, not exact value (fixable; not blocking for the committed literals)

- **Counterexample.** A runner whose rejection error is `"corpus: duplicate case names; 15 unique case names; at least 16 required"` passes `:537`. So does any future text that merely contains the phrase. KQ18 says minimum cardinality and injectivity are *separate* conjuncts. The substring check cannot show that only the injectivity conjunct fired.
- **Evidence that it is unreachable today.** `jq` over all 50 committed tests shows:
  - every rejected row has 16 or 32 distinct stripped names;
  - no row has a blank or whitespace-only name;
  - the only non-ASCII code points are U+540D and U+524D, which are not whitespace.
  - `load_matrix` `:192-197` uses the same Python `str.strip` as the runner (`:355`) and refuses fewer than 16 distinct names. In the repaired runner, the min conjunct `:360` therefore cannot co-fire, and the expected error is exactly `"corpus: duplicate case names"` [INFERENCE from static code].
- **Smallest safe correction.** At receipt level, L1 checks `observed.error == "corpus: duplicate case names"` on every rejected row of the green run. Optionally, a later round can make `:537` an equality check. This needs no new feature.

### F2: per-case finding not asserted on rejected rows (fixable; real assertion gap)

- **Counterexample.** Suppose a regressed runner keeps the outer error but builds its corpus-branch records with `unsupported_record`. That is the tool-absent/timeout class: `observed_finding: "unsupported"`, `observed_exit: null`. It would still satisfy every rejected-row check:
  - error substring, `passed` 0, `failed == total`;
  - `tool_present` true;
  - null `observed_exit` == N;
  - marker 0 and audit 0.

  The harness cannot tell a per-case "corpus-unmeasured" record (finding `None`) from a per-case "unsupported" record. The live runner does tell them apart (`:168`, `:186`, `:380`), but `check.py` does not enforce it.
- **Impact.** This assignment requires the code to distinguish the per-case finding. It does not, mechanically, on the reject side. The defect is a regression-tolerance gap, not wrong current output. Declared C1 receipts (SCORECARD `:497`: "corpus error reason and observed process boundaries must all correspond") do not claim per-case finding enforcement, so no current receipt sentence is false.
- **Smallest safe correction (no code change).** For each rejected row of the green run, L1's receipt asserts from the retained `runner_result.records` that every record has:
  - `observed_finding == null`;
  - `observed_exit == null`;
  - `passed == false`;
  - `reasons == [runner_result.error]`.

  For valid rows, it asserts that every record has `observed_finding == expected_finding` (the template's `loaded_same_digest`) and `observed_exit == 0`, rather than relying only on the runner's self-reported `passed`. If the receipt claims the harness asserts this itself, that claim would be false.

### F3: three different "total"s plus `child_count` (receipt-conflation risk; no current false sentence)

- **Three "total"s.** The harness top-level `total` counts matrix tests. Each record's `expected.total`/`observed.total` counts runner records, which is `len(names)` even with zero children. `child_count` is the classifier-wrapper marker, i.e. the harness's grandchildren. It is **not** a runner-process count; that authority is the audit hook's `runner_process_events`/`runner_popen_events`.
- **Matrix metadata (jq, committed literals):**
  - 50 tests: 27 rejected, 23 valid.
  - Rejected rows declare 483 names in total.
  - Valid rows declare 402.
- **Expected green (repaired runner) [INFERENCE, not executed]:**
  - Rejected rows: runner `total` sums to 483 and `failed` sums to 483, while `classifier_invocations` and `runner_process_events` both sum to 0.
  - Valid rows: `total`, `passed`, `classifier_invocations` and `runner_popen_events` each sum to 402.
  - The harness top-level `total` is 50.
- **Expected red (frozen runner, explicit `--tool`/`--cases`) [INFERENCE]:**
  - The 27 rejected rows fail with `error` null and marker summing to 483.
  - The 23 valid rows pass in the same run with marker summing to 402.
- **Conflation hazards.** A receipt that quotes the summed runner `total` (885) or `failed` (483) as children or classifier findings is wrong by 483. So is one that reads `child_count` as "runner processes".
- **Correction (receipt wording only).** Report three separate numbers:
  - the test count;
  - runner records (`observed.total`), labelled "unmeasured" on rejected rows;
  - `classifier_invocations` together with `runner_process_events`.

  `child_count` should be named as an alias of the classifier marker.
- **Related wording gap.** The `SKILL.md:495` gate row cites only the "temporary invocation marker". The process-audit observer, which is the actual evidence for "before ANY child process", appears only in `lessons/round-15.md`. This is a wording omission, not a false claim.

### Non-findings (counterexamples tried and refuted)

- **Tool-absent masquerading as rejection.** Refuted: `tool_present is True` is asserted (`:551`), and the tool-absent branch never sets `error`.
- **MeasureError masquerading as rejection.** Refuted: `error_result` has `total` 0, which is not N, so the row fails.
- **Children spawned and then records overwritten.** Refuted: the rejected-row marker and audit checks are both 0 (`:563-575`).
- **Vacuous zero marker.** Refuted: missing and zero are separated by pre-created files (`:336-341` per FindingExit), and valid rows in the same run require marker == N through identical wrapper code.
- **Vacuous red.** Refuted: the frozen red on rejected rows needs an unset error and marker N, and the valid rows in the same run must pass. Red therefore cannot come from harness breakage, but only if L1 requires the valid rows to pass in the red run.
- **Strip-semantics split between matrix and runner.** Refuted for the committed literals: no blank names, and both use Python `str.strip`.
- **Error document vs measured failure.** Both carry `test_failed`/1. They differ by the presence of the `error` key, plus `total` 0 and `records` [] (`check.py` `error_document`). A receipt must not admit an `error`-bearing document as red.

## Distinguishing defect vs tradeoff

- **F2 is a fixable assertion defect relative to this attack.** It does not make the current runner wrong, and it does not falsify the declared C1 contract. It does block any receipt claim that `check.py` mechanically distinguishes per-case findings on rejected rows.
- **F1 and F3 are hardening and wording items.** Neither is a judge-reject tradeoff.
- **No change is needed** to `measure.py`, the classifier or the matrix.

## Impacted axes

- **Calibration.** Attribution is exact only if L1 adopts the F1–F3 receipt assertions. The numeric score stays 7.
- **Operability.** Unchanged.
- **Provenance.** Improved if receipt counts are labelled per field.

Report: .ufo/waves/round-15/falsify/advice/FalsifyMeasurement.md
