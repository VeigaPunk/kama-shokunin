VERDICT: n/a — read-only design advice; C1 is close to minimal (2 real deletions, 1 merge refusal), plus 3 live code defects and 1 doc-count drift found by reading.

Reviewed bytes (both files changed 3× while this seat ran; re-read before acting):
`tests/probe-verdicts/check.py` sha256 `b460b786…65f3c58`; `tests/probe-verdicts/fault-controls.py` sha256 `500bcbca…d61552d`. Sequence observed: check.py `b853576e` (frozen) → `0354b632` → `d8f07c53` → `b460b786`; fault-controls.py 20988 B → `baf80d17` → `500bcbca`. `mutants.py` does not exist (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/c1/` empty), so it is reviewed against `make_spec.py:66` only.

## Axes

- **Calibration** — kills per line of detector, and whether a green means the graded field was exercised.
- **Operability/cost** — wall time of a counting run; the write surface a receipt can damage.
- **Maintainability** — one authority per rule; no second convention for the probe's identity contract.

## Direct answers

1. **Could fault-controls and mutants share one module?** No. Different homes/lifecycles (shipped `tests/probe-verdicts/` test vs wave-local `.ufo/waves/round-17/c1/` tool), ~25 lines of shared scaffolding, and the design already composes them across a process boundary. See D3.
2. **Are 8 fault classes all needed?** Yes, as an exact bijection with M1–M8; removing any one control leaves exactly one surviving mutant (K1). The only redundancy is *inside* F8 — four malformed shapes, of which exactly one carries the before/after evidence (D1).
3. **Is any part YAGNI?** Two things: three of F8's four shapes (D1) and mutants.py's round-16 before-probe arm (D2). Everything else that looks optional is load-bearing: the multi-family row subsets (K2), the row type checks (K3), `--list`/`--dry-run`/`--selftest`, and the duplicate-name selftest (K4). Do not add intra-suite parallelism or new diagnostic keys (D4).

## Deletions / merges

**D1 — Keep one F8 variant end-to-end; move the other three shapes into `--selftest`.**
`fault-controls.py:125-133` runs four shapes (`[]`, `{"rows":[]}`, `{"rows":[["x"]]}`, non-JSON) over five rows each. Only `{"rows":[["x"]]}` distinguishes the repaired harness from the frozen one: the frozen `b853576e` caught `json.JSONDecodeError, KeyError, IndexError, TypeError` but `row.get` on a list raises **AttributeError**, escaping as a traceback (non-JSON stdout → fault-controls ACCEPTED); the repaired `probe_output_row` (`check.py:389` `not isinstance(row, dict)`) records the failure (DETECTED). The other three shapes are already recorded failures on both harnesses, so they add no before/after information and only re-kill M8, which any one variant kills. `probe_output_row` (`check.py:372-397`) is a pure function and is **not** exercised by `--selftest` (`grep probe_output_row`: definition + one call at `check.py:453`); the file already has the pattern for in-process cases (`check.py:533-546` TemporaryDirectory + direct call). Result: 3 harness runs × 5 stub rows become 3 deterministic calls.
Tradeoff: keep exactly one end-to-end variant, or the wiring probe→record→predicate loses its only live proof.

**D2 — mutants.py: one lane-probe run for the pair; `--before-probe PATH` optional.**
`make_spec.py:66` special-cases "frozen probe == current probe at cff9e62", confirmed by sha256 `36b64978…` for both `frozen/tools_kama-probe.sh` and `tools/kama-probe.sh`. The pair's kill contribution for M1–M8 is zero: all eight are grading weakenings and round-16 recorded "All five preserved not just the totals but every row's `verdict`, `reason`, `probe_exit`, `drift`, `passed`" (`MutateHarness.md`). The 55/17 half is pinned outside this tool (`measure.py:281-283` `EXPECTED_MATRIX_SHA256`, `EXPECTED_TESTS = 72`, `EXPECTED_LOADING = 17`). Removing the second run drops a cross-round path plus a "frozen == current" branch and 8 runs.
**Keep the remaining single run**: it is the only false-red guard for the new derivation. [INFERENCE] A wrong `served_ids` precedence reds `ReadyControls.ollama-name-not-served-id`; no fault control can detect an over-strict oracle. The before count is unchanged (frozen check.py + current probe is also 72/0, so M1–M5 still survive = 5).

**D3 — No shared module; the process boundary is the interface.**
`make_spec.py:66` already defines it: "`full` = pair plus `{LANE}/tests/probe-verdicts/fault-controls.py --check <mutant> --json`". Importing across the shipped/wave boundary needs importlib for a hyphenated name and couples a sourced lane test to a wave directory. The tempting reuse is unsafe: `measure.py:139` `run_check` ends with `out.write_text(...)` to `WAVE/run-<name>.json` (`measure.py:171-172`), so importing it would write into `.ufo/waves/round-16/`. Shared surface is only mkdtemp, copying check.py + nine `*.json`, one `subprocess.run` + `json.loads`, and sha256.
Tradeoff: ~25 duplicated lines, cheaper than the coupling. Do not create a third helper file.

**D4 — Do not add: intra-suite parallelism; new diagnostic keys.**
Eight serial faults cost ~5 s plus F7's ~40 s hang; mutants.py already parallelizes ≤6, so parallelizing inside multiplies concurrent check.py/probe processes for no wall-time gain. Diagnostics are already covered without new keys: `human_summary` prints `served_model` + expected and `route=missing-GET-/v1/models` (`check.py:572-576`).

## Keeps (parts that look YAGNI but are not)

**K1 — 8 faults ↔ 8 mutants, bijection.** F1 reason↔M1, F2 exit↔M2, F3 drift↔M3, F4 verdict-case↔M4, F5 served_model↔M6, F6 route-skip↔M7, F7 hang↔M5, F8 malformed↔M8. Remove one control and exactly its mutant survives. If "declared mutants" means only the ticket's five (M1–M5), F5/F6/F8 kill none of them — but they are the fail-capability evidence for the three new checks, i.e. the defect class this round is repairing.

**K2 — F4 works only because the row set includes non-OK rows; make that explicit.**
`fault-controls.py:68-72` uses `ROWS_OK_MIS_LOAD` = MODEL_OK + MODEL_MISMATCH + MODEL_LOADING, and `verdict` mode lower-cases without touching `drift` (`fault-controls.py:224-228`). On the MODEL_OK row the lower-cased verdict fails the *drift* clause (`check.py:472`), not the verdict clause; the kill of M4 comes only from the two non-OK rows, whose drift is already true. One-line hardening: `row["drift"] = (row["verdict"] != "MODEL_OK")` after lowering, so every faulted row isolates the verdict clause and M4 dies even if the subset is later trimmed. Round-16 recorded the hazard: "A differently cased `MODEL_OK` could still be rejected through that expression" (`MutateHarness.md`).

**K3 — Row type validation is load-bearing, not ceremony.** `check.py:472` compares with `==`, and Python's `1 == True` / `0 == False` mean a probe reporting `"drift": 1` would pass on every non-MODEL_OK row. `probe_output_row`'s `isinstance(row.get("drift"), bool)` (`check.py:395`) is the only thing stopping it.

**K4 — Duplicate-name selftest is cheap, but its count drifted.** `check.py:151` is `def load_matrix(directory=CHECK_DIR):`, so no refactor was needed. However `check.py:548` returns `"malformed_tests": len(results)` where `results` now includes the duplicate-name case, so the summary prints **5/5 malformed tests** while `SKILL.md:533` pins "`--selftest`: full matrix plus 4 malformed tests rejected". Keep `malformed_tests` = 4 and add a separate `duplicate_names` field (or rename the printed key); any `== 4` consumer otherwise silently changes meaning.

**K5 — `served_model` keyed on the OBSERVED verdict is a documented tradeoff, not a hole.** `check.py:461-462` passes `record["verdict"]`, and the docstring says so (`check.py:343`). Consequence: the clause is vacuous exactly when the verdict is wrong (it then expects `'-'` and agrees with a misclassifying probe); the independent verdict equality at `check.py:467` is what catches that. It still kills M6 (F5 forges on MODEL_OK/MISMATCH rows, where the expectation is the stub's `data[].id`). No change needed; record it so no one claims `served_model` detects misclassification.

## Live defects (static reads; suite not executed)

**B1 — Wrapper-death is reported as DETECTED.** `classify_run` raises `OwnFault` only when `exit_code == WRAPPER_EXIT` (`fault-controls.py:290`), but `exit_code` is **check.py's** exit (0/1/2; never 9). A wrapper that dies for any reason (unreadable real probe, unmutable output, unset cache) makes check.py record "malformed probe output", the row fails, and the fault reads DETECTED. Fix: have `die()` write a sentinel under the scratch dir and check it per run (or read `record["probe_exit"] == 9` from the JSON, whose `error` already names the wrapper). This is the only remaining way the suite can go green for the wrong reason.

**B2 — F6's cache is per run, not per row; its row set contains a row that cannot exhibit the fault.**
`cache = str(cache_dir / f"f6-{fault['id']}-{index}")` (`fault-controls.py:468`) is one file for five rows, and the "pass" wrapper overwrites it per row (`:207-212`), so the fault run replays one row's document for all five. Only the last-written row (ReadyControls, by matrix sort order) genuinely exercises route-match; the other four fail on verdict mismatch. Separately F6's rows are `ROWS_FULL` (`:113`), which includes the closed-port DEAD row (`:78`) — a closed row has no stub route, so it can never fail route-match and would keep F6 ACCEPTED once the cache is fixed. Fix both together: key the cache by `--port` inside the wrapper, and make F6's rows stub-only.

**B3 (minor) — `hit()` leaks the response.** `fault-controls.py:178-179` does `urlopen(...).read()` without closing; use `with urllib.request.urlopen(...) as r: r.read()`.

**Resolved during this review (no action):** the `FAULT_PROBE` plumbing. In `baf80d17` the driver never set it, so every F1–F5 run died with `die("FAULT_PROBE unset")` and read as DETECTED while the real probe never ran. `500bcbca:462` now sets `"FAULT_PROBE": str(probe_path)`, and the wrapper's `args = sys.argv[1:]` (`:150`) matches `check.py`'s probe argv (`check.py:62` `PROBE_ARGV_TAIL = ("check", …)`; `check.py:275-277`). This is the failure mode B1 must guard: it was silent, not loud.

## Doc obligation created by the repair (not my file)

`SKILL.md:533` still says the gate "grades verdict, reason, exit and drift" and "4 malformed tests rejected"; the repaired check.py also grades `served_model` and route-match, and (K4) now counts five selftest results under a label that says malformed tests. The registry row needs the L1/scribe update, not only the check.py docstring.

## Limitations

- Read-only: no gate, no `check.py` run, no `fault-controls.py`/`mutants.py` run, no scratch writes. `.ufo/waves/round-17/c1/` was empty throughout.
- Both files were edited by their owners while I read (three check.py hashes, two fault-controls.py hashes). Findings target `b460b786` / `500bcbca`; re-read before acting, and re-check B1/B2 specifically.
- B1–B3 consequences are derived from source; they are [INFERENCE], not observed runs.
- Read-only recomputation: matrix set digest `bf9068d8…` over 9 files, matching `measure.py:281`; 72 rows = 8 MODEL_OK + 3 MODEL_MISMATCH + 17 MODEL_LOADING + 37 FOREIGN_SERVICE + 5 UNAUTHORIZED_SERVICE + 1 DEAD + 1 NOT_HTTP. All 11 model rows have a non-empty `data[].id`, so the four fallback groups of `served_ids` are unexercised; `ReadyControls.json:178,187,190` is the precedence discriminator (data.id `kama-ready` vs models.name `stories260K`).
- `tests/probe-verdicts/__pycache__/check.cpython-314.pyc` appeared (py_compile residue). It does not match `*.json`, so the pins are safe, but it is untracked residue inside the matrix directory.

Installs: none.
