VERDICT: partial — `tests/probe-verdicts/check.py --selftest`'s 4 malformed cases do **not** cover duplicate names, cover unknown keys only at test level, cover 1 of 8 route-shape guards, and cover bad exit values with a case that is doubly guarded (non-discriminative). The suite itself is green and reproducible; the *selftest's* coverage claim is narrower than the roster implies.

## What I ran (all from lane root unless stated)

| # | command | exit | key output |
|---|---|---|---|
| 1 | `python3 tests/probe-verdicts/check.py --selftest` | **0** | `tests=72 passes=72 failures=0` / `selftest: 4/4 malformed tests rejected (ok)` |
| 2 | importlib of `check.py`, `load_matrix()` over a temp dir with two files each defining `dup-name` | 0 | `load_matrix rejects duplicates: b.json: duplicate test name 'dup-name' (first defined in a.json)`; `validate_test` alone accepts both rows (`<s>[0]: dup-name` twice) |
| 3 | 18 `validate_test` calls over malformed/edge rows (temp copy) | 0 | table below |
| 4 | temp copy, **zero** `*.json` siblings, `--probe tools/kama-probe.sh --selftest` | **0** | `tests=0 passes=0 failures=0` / `selftest: 4/4 malformed tests rejected (ok)` |
| 5 | temp copy, injected a valid row labelled "must be rejected" | **1** | `selftest: 4/5 malformed tests rejected (FAILED)` |
| 6 | in-memory `VALID_EXITS=(0,1,2)` then validate the selftest's own `exit 1` case | 0 | `still rejected with membership widened: expected.exit 1 inconsistent with verdict DEAD (probe exits 2)` |
| 7 | matrix census over `tests/probe-verdicts/*.json` | 0 | `72` rows, `9` families, `72` unique names, `MODEL_LOADING: 17` |

No lane file was modified; all copies live under `/tmp/kama-r16-RerunMatrixSelftest/` (removed at end). No server or probe stub run by me (the selftest path only calls `validate_test`, `check.py:387`); `pgrep -x llama-server` empty at end.

## Decision on the four named classes

| named class | covered by the 4? | evidence |
|---|---|---|
| **duplicate names** | **NO — zero coverage** | The only duplicate guard is `check.py:169-172` inside `load_matrix`. `run_selftest` calls `validate_test` only (`check.py:387`), and `validate_test` is stateless: it accepted `dup-name` twice in run 2. Deleting `check.py:169-172` leaves `--selftest` at 4/4 green. |
| **unknown keys** | **PARTIAL** | Test-level covered (`bogus: 1`, `check.py:360-364`). Route-level `unknown route keys` (`:83-84`) and expected-level `unknown expected keys` (`:133-134`) have no selftest case — both reject correctly (run 3), just untested. |
| **bad R shapes** | **PARTIAL — 1 of 8 route guards** | Covered: `route.status` type only (`:365-370`). Untested but alive: route-not-object (`:76`), raw exactness (`:78-79`), unknown route keys (`:83-84`), status range (`:88-89`), headers string:string (`:94-95`), one-body-only (`:97-98`), `body_text` type (`:99-100`), and `default_route` validation (`:132`) — all 8 reject in run 3. |
| **bad exit values** | **NOMINAL ONLY — non-discriminative** | Case `exit 1` (`:371-374`) is rejected twice: membership `:140-142` *and* consistency `:143-146`. Widening `VALID_EXITS` (run 6) still rejects it, so the selftest cannot tell the membership guard is alive. `bool` (`False`/`True`) rejection (`:140-142`) is untested. |

## Findings by severity

**F1 (Medium) — duplicate-name guard has no self-test, against the lane's own precedent.**
`check.py:169-172` exists and works (run 2), but is unreachable from `run_selftest` (`:387`), which never calls `load_matrix` (`:464` is the only call site). The sibling harness does test this: `tests/ollama-corpus-guard/check.py:196-200` refuses a fixture whose distinct-name count could hide the duplicate guard ("so the minimum-corpus guard cannot mask the duplicate guard"). `check.py` breaks that house convention.

**F2 (Medium) — zero-matrix run is vacuously green.**
`load_matrix` globs `CHECK_DIR/*.json` (`:152`) with no minimum-count or non-empty assertion; run 4 printed `tests=0 … selftest: 4/4 … (ok)` and exited 0. A renamed/moved matrix directory (or a future `--matrix-dir` refactor) silently converts the 72/72 gate into a 0-test green. `all([])` is `True`, so an emptied `SELFTEST_MALFORMED` would likewise print `0/0 … (ok)`.

**F3 (Low) — the "bad exit" case cannot fail alone.**
Run 6 shows the `exit outside {0,2}` case survives deletion of the membership guard. The selftest records `detail` (`:390`) but never asserts it against the case label, so *which* guard fired is never checked.

**F4 (Low) — doc/help drift: 3 vs 4.**
`check.py:29` "feeds 3 embedded malformed tests"; `check.py:448` help "rejects 3 embedded malformed tests"; actual `SELFTEST_MALFORMED` (`:359-380`) has 4 and output says 4/4. A reader auditing coverage is told the wrong denominator.

**F5 (Low) — `expected.verdict` is an unconstrained string.**
`validate_test` checks `isinstance(str)` (`:140-141`) and the exit/verdict rule but not membership in the probe's closed set {MODEL_OK, MODEL_LOADING, MODEL_MISMATCH, FOREIGN_SERVICE, DEAD, NOT_HTTP, UNAUTHORIZED_SERVICE} (`tools/kama-probe.sh`, `C_VERDICT=` assignments). `{"verdict":"MODELOK","exit":2}` is **ACCEPTED** (run 3): a typo becomes a permanently-failing row, not a schema error. Fail-closed, so it cannot manufacture a green.

**F6 (Low, latent) — `route.status` accepts 100..999.**
`:88-89` allows `999` (run 3: `status 999 ACCEPTED`), beyond RFC 9110's 100–599. No shipped row exploits it (run 7: statuses `200,401,403,404,429,500,502,503,504`), but a future row with `status 999` expecting `FOREIGN_SERVICE/non-2xx-non-model-http` would grade against an impossible HTTP response. The `routes` path-key `isinstance(p, str)` check (`:122-124`) is dead code post-`json.loads`.

## What is sound (attacked, did not break)

- 72/72, 9 families, 72 unique names, 17 `MODEL_LOADING` — reproduced exactly (runs 1, 7).
- All 8 route guards, both extra key-set guards, `default_route` validation, and bool/`False` exit rejection are present and fire (run 3) — they are uncovered, not broken.
- Failure path is honest: a mislabelled case produced `(FAILED)` and **exit 1** (run 5), matching `:497-498`.
- `expect: ""` is accepted (`:114-118`) but the probe treats `''` as wildcard (`tools/kama-probe.sh:530`, `''|'*'|'-'`), so it is equivalent to `"*"`, not a hole.
- Grading is token-based, not exit-only, and asserts `drift == (verdict != MODEL_OK)` (`:344-346`), so a `MODEL_LOADING` row cannot pass with drift=false.

## Recommended minimal repair (for L1, not applied)

1. Move duplicate detection into a helper both `load_matrix` and `run_selftest` call, or have `run_selftest` feed a 2-row duplicate fixture through that helper; add a positive control (valid row accepted).
2. Add 3–4 cases: route unknown key, `body_json`+`body_text`, `raw`+`status`, `exit: False` (bool).
3. Make each case assert its `detail` prefix, and add `if not entries: fail(...)` in `main` plus `if not SELFTEST_MALFORMED: fail(...)`.
4. Fix `:29` and `:448` to 4 (or derive the count).
5. Constrain `expected.verdict` to the probe vocabulary; tighten status to 100..599.

## Limitations / verification gaps

- The "26 guard sites" enumeration is my reading of `validate_route`/`validate_test`/`load_matrix` [INFERENCE]; the 4 exercised sites are directly observed (run 1 + source labels).
- I did not test the selftest against the frozen probe, nor re-run `measure.py` (forbidden); runs 4–6 used a temp copy of `check.py` so `LANE`/`DEFAULT_PROBE` derivation there is temp-relative — `--probe` was passed explicitly and no matrix grading occurred (0 tests).
- Case 3's double guard is proven by monkeypatching the module constant in memory (run 6), not by editing the lane file.
- `tests/probe-verdicts/check.py` is unmodified at `b8e485c` (`git status --porcelain` shows no tracked change; only an untracked `tests/probe-verdicts/__pycache__/check.cpython-314.pyc`, mtime 10:56:50, not created by my commands — every import I ran targeted a `/tmp` copy, and running `check.py` as `__main__` writes no bytecode. Likely a concurrent seat importing the lane file; left untouched).

## Installs

None. No package manager invoked; no network fetches.
