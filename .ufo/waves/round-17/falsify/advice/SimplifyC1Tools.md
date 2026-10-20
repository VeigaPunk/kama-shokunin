VERDICT: confirm — 136 of 2,156 lines in the two C1 tools are provably dead weight; deleting them reproduces every recorded C1 number byte-identically; the rest is load-bearing.

Seat: KamaR17.SimplifyC1Tools (FALSIFY wave, round 17). Attacked: `tests/probe-verdicts/fault-controls.py` (815 lines) and `.ufo/waves/round-17/c1/mutants.py` (1,341 lines) at commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`. Axes: calibration (measured numbers preserved), operability (runtime cost), maintainability (dead paths, second conventions), safety (pins, process hygiene). All work in a `/tmp` clone of the lane at that commit; the only lane write is this Report. The deletions below were APPLIED in the clone and verified; they are recommendations for the lane, not lane edits.

## 1. Deletions proven safe (applied in scratch clone, all checks identical)

### 1a. mutants.py — 15 unfired mutant-fallback candidates + 2 then-dead helpers (−107 lines; 1341 → 1234)

Evidence they never fire: in the committed `.ufo/waves/round-17/runs/mutants-grid.json`, every one of the 36 applicable (cell, mutant) entries fired its FIRST candidate only — labels `conjunct-neutralize`/`literal-delete`/`literal-casefold`/`literal-insert`/`pass-before-return`/`and-false`/`conjunct-served_model_ok`/`conjunct-route_ok`. Every fallback below is unreachable on both real subjects (frozen `b853576e…`, current `ddc3f3cc…`) and on both selftest fixtures, and the docstring contract makes a missing site honest n/a: "A mutant whose site is absent is reported ``site_missing`` (n/a), never silently skipped" (mutants.py:14).

| Delete (original line ranges) | Entry labels |
|---|---|
| mutants.py:463-464 | M0 `literal-true` |
| mutants.py:473-475 | M1 `conjunct-neutralize` |
| mutants.py:484-486 | M2 `conjunct-neutralize` |
| mutants.py:495-496 | M3 broad `record["drift"]` neutralize |
| mutants.py:518-520 | M5 `timeout-branch-insert` |
| mutants.py:532-544 | M6 `conjunct-served_model`, `lhs-served_model_ok`, `lhs-served_model_expected` (+ comments) |
| mutants.py:555-577 | M7 `conjunct-route-generic`, `lhs-route_ok`, `lhs-route_match`, `return-models-route`, `conjunct-models-path` (+ comments) |
| mutants.py:590-602 | M8 `except-unparseable`, `conjunct-error-none`, `row-none-branch` (+ comments) |
| mutants.py:615-617 | M9 `stmt-false` |
| mutants.py:376-402, 405-411 | `replace_stmt`, `set_lhs_true` — after the above, zero callers |

Calibration gain, not just weight: the deleted fallbacks are match-broadening patterns (`neutralize_conjunct(s, [r'route'], prefer=…)`; `set_lhs_true(…, r'/v1/models|route')`). On any future reworded check.py they could neutralize a DIFFERENT conjunct than the mutant name claims — a misattributed kill. After deletion, rewording surfaces as `site_missing` (n/a), which is the tool's own declared semantics and what ReviewMeasureDesignC1.md C8 asks for.

### 1b. fault-controls.py — four dead CLI knobs + tail handler (−29 lines; 815 → 786)

No recorded command, shipped doc row, or in-repo caller uses any of them. The counting commands are `fault-controls.py --check <check.py> --json` (round-17.md §Measurements) and mutants' `run_controls` (`[sys.executable, str(FAULT_CONTROLS), "--check", str(check_path), "--json"]`, mutants.py:787-788). The shipped registry rows name only `[--check PATH] [--json]` + `--list` (SKILL.md:571) and `--grid --out PATH` + `--selftest`, `--dry-run` (SKILL.md:572).

| Delete (original line ranges) | Why dead |
|---|---|
| fault-controls.py:621-623 (+ uses :729, :745-746, :754, :756 → `MATRIX_DIR`) | `--matrix-dir` can never succeed with a non-default value; the digest pin exits 2 first. The executor's own report concedes it: "`--matrix-dir` is accepted, but the pinned set digest makes anything but the canonical nine-file set an immediate exit 2" (`build/advice/C1FaultControls.md:53`). |
| fault-controls.py:618-620 (+ :736-740 → `DEFAULT_PROBE`) | `--probe` is unusable by design: mutants deliberately does not forward the before probe — "the before probe is deliberately not forwarded because F0's identity control requires the clean pass-through" (`build/advice/C1FaultControls.md:63`); any non-lane probe breaks F0/matrix expectations, so no measured number can depend on it. [INFERENCE on "no number can depend": follows from F0 gating + pinned matrix.] |
| fault-controls.py:624-627, 714-722 | `--only-fault`: zero recorded invocations; not in SKILL.md:571; debug-only. Note: it IS named in the build spec (`make_spec.py:58` `[--only-fault ID]`), so deletion deviates from that historical spec text — flag for L1 sign-off. Same for `--probe` (`make_spec.py:58`). `--matrix-dir`/`--skip-slow` are not in the spec (executor additions). |
| fault-controls.py:628-629, 723-724 | `--skip-slow`: zero recorded invocations; the ~40 s F7 is part of the counted suite in every measurement. |
| fault-controls.py:812-815 | `except BrokenPipeError` tail: every lane invocation redirects stdout to a file; `--list | head` is not a lane pattern. Micro. |

## 2. Verification actually run (clone at `54a2926…`, `PYTHONDONTWRITEBYTECODE=1`)

Baseline — unmodified tools reproduce the committed evidence exactly:

- `fault-controls.py --check <frozen> --json` → exit 1, detected 5, accepted 3 {F5, F6, F8}; document **byte-identical** to committed `runs/fault-controls-frozen.json` after removing `seconds` (53.0 s vs 53.1 s).
- `fault-controls.py --check tests/probe-verdicts/check.py --json` → exit 0, detected 8, accepted 0; byte-identical to `runs/fault-controls-current.json` modulo `seconds` (59.9 s vs 59.8 s).
- `mutants.py --selftest` → exit 0 (30 cases, pass); `--dry-run` frozen → totals {mutants 10, site_found 8, site_missing 2}; `--dry-run` current → {10, 10, 0}; committed (current, full) cell `evidence.mutation` labels == my dry-run labels (python compare → True).

After applying §1 deletions:

- `python3 -m py_compile` both files → OK.
- `mutants.py --selftest`, `--dry-run` (frozen, current), `fault-controls.py --selftest`, `fault-controls.py --list` → all exit 0 and **byte-identical** to the pre-edit outputs (`diff` empty, five checks).
- Full suites re-run post-edit (112.83 s wall): frozen exit 1, document identical to pre-edit modulo `seconds` (53.1 s), 5 detected / 3 accepted {F5, F6, F8}; current exit 0, identical modulo `seconds` (59.6 s), 8 / 0. Headline lesson numbers (§Measurements: frozen 5 detected/3 accepted; current 8/0) preserved exactly.
- Grid reproduction follows structurally, not by rerun: `--grid` = dry-run-proven mutant application (byte-identical mutated sources) × untouched runtime machinery (`run_cell`/`run_check`/`run_controls` unedited). I did NOT re-run `--grid` (~tens of minutes); L1 can.

## 3. Next-repin candidates — NOT free today (would change committed evidence shapes)

- **F8 variant trim** — delete `fault-controls.py:171-175` (`empty-array`, `rows-empty`) and `:179-184` (`row-null`, `non-json`); keep `row-not-object` (:176-178) and `non-utf8` (:185-188, named by the claim "malformed or non-UTF-8"). Committed frozen-arm evidence shows the frozen harness tracebacks exactly on row-not-object, row-null, non-utf8 ("check exited 1 but stdout is not parseable JSON (traceback or human text)" ×3, `runs/fault-controls-frozen.json` F8 `why`), so F8 stays accepted on frozen and detected on current with two variants — headline numbers unchanged. Saves 20 of F8's 30 check.py runs per suite (~15-20 s of the ~53-60 s suite [INFERENCE]). Cost: the committed `fault-controls-*.json` F8 six-variant `why` strings stop reproducing. Do it only together with a re-recording of the two counting runs.
- **FIXTURE_V1 in mutants.py (:1131-1170 approx)** — a second, hand-copied authority for the frozen grading shape. Kept today: `--selftest` must stay self-contained ("touches nothing in the lane") and its 30-case output is committed evidence (`runs/selftest-.ufo_waves_round-17_c1_mutants.py_--selftest.txt`). Revisit only if the selftest is ever re-recorded; the manifest-pinned frozen file is the one authority for the real shape.

## 4. Considered and kept (looks optional, is not)

- F0 positive control + exit-2 gating, and classify_run's target-conjunct rule — the safety properties that stop reject-all and wrapper-crash false detections (both recorded in the committed runs).
- Matrix digest/breadth pins in both tools, frozen-manifest `verify_frozen`, `--out` refusal inside `tests/probe-verdicts/` — the counting preconditions.
- `start_new_session` + `killpg(SIGKILL)` timeouts + `PYTHONDONTWRITEBYTECODE=1` — process/port hygiene.
- F6 per-row pre-pass cache and stub-only `F6_ROWS` — fixes recorded in build-wave review; the committed F6 `runs: 4` depends on it.
- `--check`/`--detector` single mode (docstring CLI; falsify verification recipes use it), r17/r16 before-probe selection (its label is recorded in the committed grid baselines), `--list`/`--selftest` (SKILL.md:571-572).
- Duplicated `sha256_file` between the two files — process-boundary composition, already adjudicated (`build/advice/SimplifierC1.md` D3).

## 5. Commands run (all in `/tmp/SimplifyC1Tools-clone` at `54a2926…`, `PYTHONDONTWRITEBYTECODE=1`)

- `git clone -q <lane> /tmp/SimplifyC1Tools-clone && git checkout -q 54a2926…` → OK
- `mutants.py --selftest` → 0; `--dry-run --check <frozen>` → 0; `--dry-run --check tests/probe-verdicts/check.py` → 0
- `fault-controls.py --selftest` → 0; `--list` → 0
- `fault-controls.py --check <frozen> --json` → 1; `--check tests/probe-verdicts/check.py --json` → 0 (112.99 s both)
- post-edit: `py_compile` both → 0; the five narrow checks → 0 each, diffs empty; the two full suites → 1 and 0 (112.83 s both), documents identical modulo `seconds`
- comparisons: committed-vs-baseline `True`/`True`; after-vs-before `True`/`True`; grid-label binding `True`
- `ss -ltnp` → no listener from any process I started (remaining listeners are host shims started 09:57:11, before this seat); check.py's stubs bind `127.0.0.1:0` ephemerally inside their own processes. No llama-server started; 8080/34113/registry ports untouched.

## 6. Limitations

- `--grid` was not re-run post-edit (cost); equivalence is proven at the mutant-application layer, which is the only layer the deletions touch.
- No `lsp` device is mounted (`read xd://lsp` → "No such tool: xd://lsp"); caller/uniqueness proofs are literal grep over the clone plus the committed run documents — textual, not semantic.
- Line ranges are original (committed) numbering at `54a2926…`; the numbers come from pre-edit `grep -n` anchors quoted in this report.
- The frozen-arm escaper set (row-not-object, row-null, non-utf8) is read from the committed JSON, not re-derived per variant here.

## 7. Installs

None.

## 8. Writes

This Report only. Scratch `/tmp/SimplifyC1Tools-clone` and `/tmp/SimplifyC1Tools-scratch` (clone, baseline/after JSONs, diffs) removed after this write. No lane file, `.ufo/state/`, fleet root, or sibling lane touched; no `jj`/git write anywhere.
