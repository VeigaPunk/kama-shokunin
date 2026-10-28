# R63 connector CN01SiblingPattern: sibling-overlap scan (read-only)

Seat: CN01SiblingPattern (connector, leaf). Milestone: scan overlaps. Judged on: operability, calibration.
Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (kama HEAD confirmed). Lane untouched; no commits, no edits, no installs.
Evidence: `.ufo/waves/round-63/w1/out/CN01SiblingPattern/hits.tsv` (all hits, near-misses and reference examples), `files.txt` (scanned counter-like files).

## Scope and method

- Sibling lanes with a `tools/` directory: chousa, kaidoku, kotodama, mado, mori, souji, tameshi, tsukuroi (8 siblings). kama is the owning lane for the R63 counters and is not a sibling; it appears below only as the reference for the R62 defect.
- Counter-like files scanned: 57 files (`*counter*.py`, `score-*.py`, `mutants-*.py`, `*controls*.py`, `repeat-control.py`, `mutate-and-run.sh`, `*reconcile*`, `*regress*`, `cand-*selftest*`), about 53.7k lines. Kaidoku rounds 34-49 are the bulk (round-42/44/49 counters are 3-5k lines each), so the scan was targeted by search term, not read in full. Coverage is therefore partial. Each hit was confirmed by reading the cited lines.
- Pattern (a): control family credited without requiring the unmutated baseline to pass.
- Pattern (b): sensitivity or mutation check computed by replacing text and then testing for the replaced text.
- Pattern (c): controls counted as rejected without naming the failure that rejects them.

## Hits, by pattern

### (a) credit without a passing baseline

| lane | path:line | description |
|---|---|---|
| tsukuroi | tools/mutants-kernel-taint.py:378-404 | No `sys.exit` and no control gate. `control_exit` and `control_verified_rows` are printed but never consulted; the script exits 0 whatever the unmutated baseline does. `should_fail_accepted` is `0` when the counter is broken, because every mutant reads as rejected. |
| tsukuroi | tools/mutants-adjacency-overlap.py:400-414 | Same shape: `control_live_anchored_rows` and `control_live_exit` are printed only. `should_fail_accepted=0` is reported with the control red. Exit 0 always. |
| tsukuroi | tools/score-selftest-mounts-r41.py:255-262 | A failing baseline (and every non-mutant run) is re-run once and the second verdict replaces the first (`res[name] = run_selftest(...)`). The baseline pass can be earned on retry; the first failure survives only under `retried`. |
| tsukuroi | tools/score-selftest-mounts-r41.py:263-288 | Per-row `killed` (line 287) and parameter credit (line 275, from `base['labels']`) are computed before `baseline_pass` is checked. The top-level `ok` at 295-296 gates the overall verdict, so this is row-level credit only. |

Not hits (baseline gate present): tameshi `mutate-and-run.sh:536-545` (red pristine control exits 2 before kills are attributed); tsukuroi `score-selftest-literals-r40.py:161` (`baseline_pass == 1` in `ok`); tsukuroi `mutants-owed-statements-r29.py:338`, `-r29-v4shapes.py:372`, `-r29-landed.py:330`, `mutants-btrfs-space-r30.py` (return code requires control `== 10`/`marked == 12`). Kaidoku round-44/49 `c1-controls.py` controls are not gated on the positive control, but the exit is the conjunction of all controls (`return 1 if failures`), so no family is credited alone.

### (b) replace-then-test-for-the-replaced-text sensitivity

No sibling hit. I searched for `X.replace(...)` followed by a membership test of the same text, including the `pat in out.replace(pat, ...)` shape that R62 used (kama `round62-c2-counter.py:246-247, 269-271`). None found in the eight sibling lanes.

Near-misses, not hits:
- tsukuroi `mutants-owed-statements-r29-landed.py:153-154`: `s[i].replace(' | mined | ', ' | rejected | ', 1)` then `assert ' | rejected | ' in s[i]`. This is a fixture precondition (the mutation applied), not a verdict sensitivity; it is the same shape, so it is named so the L1 does not mistake it for a clean case.
- tsukuroi `check-selftest-matcher-r51.py:193-204`: mutation applied only when `text.count(needle) == 1`, and `caught` requires a `FAIL` summary with `failed >= 1` from a real re-run. Non-tautological; the reference for a correct mutation check.

### (c) controls rejected without naming the failure

| lane | path:line | description |
|---|---|---|
| kaidoku | round-44/c1-controls.py:1055-1056 | `judge()`: a red exit with no readable receipt is credited as "red as expected" by `return (want_exit != 'exit0', ...)`. Any non-zero exit (including a Python traceback, exit 1) passes a `non-zero`/`exit1` control with no named clause. |
| kaidoku | round-49/c1-controls.py:1053-1054 | Same no-receipt red-as-pass credit. |
| kaidoku | round-44/c1-controls.py:1070-1079 (round-49: 1068-1079) | `failing_includes` requires named clauses but has no collateral cap; `failing_any` is an OR over several clauses, so one named clause firing among any number of unrelated failures passes. This is the R62 defect that kama's Amendment 1 closes. |
| tameshi | tools/tally-audit-v2.py:547-548 | `check_harness()`: `run_harness()` returns `None` (harness aborted or no tally line) and the fault is `continue`d, i.e. counted as rejected. No failure named. |
| tameshi | tools/tally-audit-v3.py:751-752 | Same abort-as-rejected accounting. |
| tsukuroi | tools/score-selftest-literals-r40.py:156 | `row['killed'] = not res[name]['pass']`: a timeout (exit 124, line 103), a crash, or any non-PASS run is "killed" with no `FAIL <label>` required. Contrast `score-selftest-mounts-r41.py:195-198`, which requires exit != 0 and a FAIL label the baseline printed as PASS. |
| tsukuroi | tools/score-counter-cheats-r51.py:175-176, 182-183 | A cheat is "rejected" whenever the counter prints verdict FAIL with rc 1. The failing check is never matched to the cheat it is meant to catch. |
| tsukuroi | tools/mutants-owed-statements-r29.py:331, 333 | Should-fail "refused" is `item_ok is not True`. The expected `rule` and the `why` string are recorded (lines 322-324) but never compared. A counter that emits no row counts as a rejection. |
| tsukuroi | tools/mutants-owed-statements-r29-v4shapes.py:330, 356 | `counts = row.get('ok') is True`; refusal credited on absence of `ok: true`, with no `why` match and the exit code not consulted. |
| tsukuroi | tools/mutants-owed-statements-r29-landed.py:322-323 | Same item_ok-only refusal test (`acc`, `ref`). |
| tsukuroi | tools/mutants-kernel-taint.py:387, 391, 399 | `harness_error` mutants and any run that is not `(exit 0 and verified_rows 6)` count as rejected. No failure named. |

## Response-shape grader for an OpenAI-compatible completions endpoint

No sibling holds one.
- Searched `text_completion`, `/v1/completions`, `choices[0]`, `prompt_tokens`, `completion_tokens`, `finish_reason` across the eight sibling `tools/` trees.
- Searched the non-tool lanes (kagi, kake, kengaku, tabi, kasegi, kotoba, revenger, lore, kumitate, scripts, tools, lane3) by content, excluding `.ufo/` and `.git/`. Only false positives (`choices` as a Python variable in an ECC `solve.sh`).
- Filename search of all lanes (including `.ufo/`) found only: `kengaku-shokunin/.ufo/waves/round-29/scratch/.../src/llms/providers/openai_utils.py` (a client wrapper in scratch, not a grader) and `kengaku-shokunin/.ufo/waves/round-51/w1/SrcLlamaServer/*` (upstream llama-server README, documentation only). Content of `.ufo/` trees was not searched beyond the filename scan.
- Within kama (owning lane, for the L1's information): the completions graders are `tools/kama-completion-live.py` (checks at ~354-433, `object == text_completion`, usage, timings, `/tokenize` count), `tools/round62-c1-counter.py` (~118-145), and `tools/round63-c1-counter.py` (~177-225, live checks). `echo-recheck.py` and `kama-context-capacity.py` cover `/v1/chat/completions` and `/v1/completions` request bodies, not response shape.

## Lane-internal note for the L1 (not a sibling hit)

kama `tools/round62-c2-counter.py:246-247, 269-271` is the vacuous sensitivity expression (`mut = out.replace(pat, MUT); sensitive = not (pat in mut ...)`). `tools/round63-c2-counter.py:244-247` keeps `r62_formula` only as the witness it is tested against (`sensitivity_selftest`, lines 250-267). The sibling scan found no second instance of that shape.

## Verification

- No counter was run and no live server was contacted; the scan is read-only text evidence. Each hit was checked by reading its cited lines, and the line numbers were confirmed with the search tool.
- Coverage limit: kaidoku round-40 to round-49 counter bodies were searched by term, not read in full. Hits (a) and (c) are the ones the term searches surfaced and the cited lines confirm; a full read of the 3-5k-line kaidoku counters could surface more.

## Tool installs and updates

None. No package or binary was installed or upgraded. No pacman transaction.

## Tally

sibling-overlap: lanes=8 files_scanned=57 pattern_a=4 pattern_b=0 pattern_c=11 response_shape_grader_in_siblings=0 (kama-only: 3 completions graders)
