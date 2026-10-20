# FalsifyAdjacentDuplicate — scoped findings

Scope: `tests/ollama-corpus-guard/AdjacentDuplicate.json` against the final predicate in
`.ufo/waves/round-14/measure.py` (#6643) and the harness grader in `tests/ollama-corpus-guard/check.py` (#2C84).
Read-only. No tests, builds, linters, smoke runs, or child processes were executed. No tools installed or updated.

## Verdict

No fail finding. The fixture satisfies every stated property, and the predicate path it exercises is consistent with it.

## Fixture counts (read from file lines)

| Test id | Lines | Entries | Distinct stripped | Envelope | expected_rejected | Check |
|---|---|---|---|---|---|---|
| `AdjacentDuplicate-array` | 5-21 | 17 | 16 (`n05` at positions 6-7) | array | true | duplicate present, 16 >= 16 |
| `AdjacentDuplicate-object` | 29-45 | 17 | 16 (same) | object | true | duplicate present, 16 >= 16 |
| `AdjacentDuplicate-valid-unique-array` | 53-68 | 16 | 16 | array | false | all distinct |
| `AdjacentDuplicate-valid-unique-object` | 76-91 | 16 | 16 | object | false | all distinct |

- The fixture is valid JSON as read: a 96-line top-level array of four objects, with the required keys `name`, `names`, `envelope`, `expected_rejected`.
- No test id collides with another fixture in the directory. The 12 sibling files were checked by name listing.

## Matrix admission (harness `load_matrix`, check.py:139-226)

- Lines 192-199: `distinct >= 16` is enforced on stripped names. Both rejected controls pass, so the minimum-count guard cannot be the cause of rejection.
- Lines 201-211: `expected_rejected == true` requires a duplicate in stripped names; `false` requires none. Envelope is restricted to `array` or `object` (182-186). Both correspondences hold for all four entries.

## Runner predicate (round-14/measure.py #6643)

- `corpus_problems` (350-364) strips names, counts `len(declared) != unique` as `"duplicate case names"`, and separately checks `unique < 16`. For the rejected controls it yields `duplicate case names`, with unique = 16.
- `run()` (374-383): the corpus branch precedes the `measure_case` loop. The only child-process site is `subprocess.run` at line 240, inside `measure_case`. With a corpus problem, every record is `unmeasured_record` with `observed_exit` None and `passed` False; `error` is `"corpus: duplicate case names; ..."` (421-422). Exit is 1 (418).
- The valid controls have 16 distinct names and pass the guard, so they reach `measure_case` 16 times. Each case clones `cases[0]` (`loaded_same_digest`, exit 0), so this is the intended measured path.

## Grader predicate (check.py grade, 478-624)

Rejected expectation (528-575), all required:
- exit 1, `verdict_exit` 1
- `"duplicate case names"` substring in `error`
- `passed == 0`, `failed == total == len(names)`
- `tool_present` true (wrapper file exists)
- `observed_exit` null on all `total` records
- marker count 0 (wrapper never invoked)
- audit `process_events == 0` and `popen_events == 0`

Accepted expectation (576-604), all required: exit 0, `passed == total`, `failed == 0`, marker count `total`, Popen count `total`.

For AdjacentDuplicate:
- Rejected controls: the runner never reaches `measure_case`, so marker and Popen counts are both 0, and the error substring matches the runner text.
- Valid controls: 16 runner Popen events (one per `subprocess.run`), 16 marker lines, `total` = 16.

## Mechanism checks

- Audit hook (check.py:276-281) installs before `runpy` of the runner and records every event matching `subprocess.Popen`, `os.system`, `os.posix_spawn`, `os.fork`, `os.exec`. Nothing in the runner's pre-guard path (`load_cases`, `corpus_problems`, `tempfile`) emits those events. The rejected-path zero-spawn assertion is therefore meaningful, not vacuous.
- Wrapper (check.py:298-306) appends the marker before `runpy` of the real classifier. Marker is written by the child, so it proves only that a child ran, which is the intended observation.
- Name handling: harness writes names unstripped (`case["name"] = name`, check.py:351); runner strips for the guard and keeps the raw name for records. Both agree for this fixture because no name has leading or trailing whitespace.
- Pre-repair contrast: `.ufo/waves/round-15/frozen/measure-before.py:350-362` has only the `unique < 16` check. Against that frozen runner, AdjacentDuplicate-array would pass the minimum guard, run 17 children, and fail the grader with `classifier invocations 17 != expected 0`. So the fixture discriminates the repair (RED before, GREEN after).

## Residual risks (non-blocking, not fixture defects)

1. The audit hook observes only in-process spawns. A spawn that bypasses the listed prefixes would not be counted. This is stated in the harness LIMITS and does not change the verdict for this fixture.
2. The rejected grader does a substring match on `"duplicate case names"`. It does not check which duplicate was found, so adjacency is not distinguished from middle or trailing placement by the predicate. The fixture's adjacency property is a fixture-level fact, not a grader-level assertion.
3. Harness error handling: an absent or malformed sibling file fails the whole matrix (check.py:222-223), so one bad sibling file would block AdjacentDuplicate's result. This is intended fail-closed behavior, not a defect here.

## Verification gap

Execution has not been observed. All counts and predicate outcomes above are static reads of the final committed files. L1 should run `python3 tests/ollama-corpus-guard/check.py --only AdjacentDuplicate-array` and the other three ids once after integration to confirm the predicted outcomes.

Report: .ufo/waves/round-15/falsify/advice/FalsifyAdjacentDuplicate.md
