VERDICT: confirm — no-trade review found zero regressions; every observed divergence is cosmetic or a strictening; residual notes are fail-closed seams, not harm.

Seat: KamaR18.NoHarm (critic, leaf). Target: pushed lane master `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`, clone `/tmp/kama-r18-falsify-NoHarm/clone` (`seat/NoHarm` branch, removed after). Frozen baselines: `.ufo/waves/round-18/frozen/*` (identical to `e75cf68` for all six production files — verified via `git show e75cf68:<path>`).

# Axis-by-axis attack and evidence

## 1. Legacy gate outputs unchanged — CONFIRMED

Differential: 123 mutated/legacy receipts through both `frozen/tests_llamacpp-live_check-receipt.py` (round-17 gate) and current `tests/llamacpp-live/check-receipt.py`. Inputs: r16 v1 receipt, r16 frozen-probe receipt, r17 receipts 1–3, each mutated by deleting any of 11 top-level keys, port+1, first-check pass→false, bogus/truncated check list, corrupted server/model/probe/tool sha256, outcome→'pass', schema→v3, empty transitions.

- Exit codes: **0 divergences in 123 cases** (and 7 more focused capture mutations).
- Text divergences (15 cases) are all cosmetic: sentinel memory address `<object object at 0x...>` inside identical problem counts; schema-name list now naming v3; `relabel-v3` rejected by the new v3 path instead of the schema-name check — same exit 1, more specific problems.
- `--require-schema` is a documented floor ("reject receipts below this schema version", check-receipt.py:2063): v3 receipt + `--require-schema v2` → exit 0; selftest rows 1874–1881 pin v2-rejects-v1 and v3-rejects-v2. Not a defect.
- Official runs agree: legacy-frozen-0..4 and legacy-current-0..4 all `VALID` exit 0; wrong-probe-pin exit 1 with identical problem text.

v3-forgery battery on `live/receipt-1.json` (pins as in runs/commands.json): argv-extra-flag → INVALID (argv tail mismatch); argv-null → INVALID; all-checks-null → INVALID (only loading_envelope_graded may be unevaluated); leg-null-while-503 → INVALID (evaluated-null while a 503 is observed); honest-not-evaluated forged → INVALID (observed fields contradict); outcome-lying-fail → INVALID (`outcome 'fail' != re-derived 'pass'`); internal_fault planted → INVALID; captures.models.status→503 → INVALID (M7 closed). No forged receipt reached exit 0.

## 2. Old detector kills + parser historical cases — CONFIRMED

- Full real-probe matrix run, frozen vs current `check.py` (72 tests, both exit 0, passes 72/72): **73 record diffs, all ephemeral port values** (and one evidence string embedding the port). Every verdict/reason/exit/drift/served_model/route_ok/evidence token identical. Exact sources below.
- Unit differential on `probe_output_row` (21 outputs incl. non-JSON, non-UTF-8, wrong types, two rows, trailing data, dup keys): **0 semantic divergences**. The only behavior deltas are the named round-18 debts: 60k-nesting (`RecursionError`) and 5000-digit int (`ValueError`) which **crash the frozen parser outright** (observed `RecursionError: Stack overflow (used 8148 kB)`) and are now recorded row errors — a gain, no regression.
- `sources-append-only.py`: real history pairs (`ccc4bb3`, `e75cf68`, `c6dc46f`, self) → identical verdicts frozen vs current. Synthetic battery in a committed scratch repo (each mutation vs true base): blank-then-tamper, tamper-only, blank-then-drop, rowlike-short, mutable-status, opened-change, blank-then-newrow → identical violations/exit everywhere except **prose-pipe**: a bare `|` in non-table prose inside `## Registry` is now exit 2 (frozen exit 0). Strictening, fail-closed (see residual note R2). `opened` cell change is now caught identically by both (frozen already compared all non-mutable cells); the new IMMUTABLE_CELLS pin makes the compared set itself a guard fault if narrowed.
- Frozen refused counter vs repaired `dispatch-provenance.py` on real artifacts: `refused_observations` on `build/refused-result-1.json` → **95 distinct labels** (the 95-seat refusal); `spawned_observations` on `build/spawn-result.json` → header/bullets/progress/pending all **75**. Old code's prose-blindness is fixed without miscounting spawned/refused.

## 3. Process safety — CONFIRMED, one unreachable own-fault path noted

- `run_probe` (check.py:279): `Popen(start_new_session=True)` + `os.killpg` on timeout; probe is its own group leader, so the kill reaches same-group children; `start_new_session` makes pgid==pid so no reincarnation hit on a live child. F17 selftest verifies the escaped child is gone.
- Tool teardown (kama-llamacpp-live.py:799-852, finally 1403-1460): signals ignored during teardown; `killpg` only when `_child_running` proves aliveness (pgid-reuse note in docstring); post-teardown backstop `killpg SIGKILL` + re-wait inside the same finally; `pdeathsig` on the child; `_emit` atomic via mkstemp+os.replace. No path observed where a SIGINT/SIGTERM/BaseException leaves the server child running.
- `controls.py` `_kill_fake` (778-813): verifies `/proc/<pid>/cmdline` names the exact staged fake path before signalling; group-kills only when pgid==leader AND != own group — a control cannot kill the harness or a pid-reused stranger. Registry is copied, not fabricated empty (fail-closed at 830-831).
- `sources-append-only.py` `run_check` now wraps `diff_registries` in the exit-2 boundary so an internal fault can never surface as exit-1 (violation).

## 4. Docs / evidence integrity — CONFIRMED

- `runs/commands.json` honestly records `measured_commit c6dc46f` and both counters `as_expected: false` exit 2; `.exit` files still show `exit=2`. `runs/c1-measure.json` fault text `"0 row(s) classified misclassified"` proves it was produced by the **pre-repair** counter (new message says "misclassified outcome bucket") — retained failure evidence, not overwritten.
- LOG/SCORECARD/PROVINCE additions match observed artifacts (95→75 refit, two counter own-faults, S047 row appended in round-18 lesson not by editing round-17's). `git diff` confirms probe and nine matrix JSONs unchanged.
- `combine_arms` (survivors.py:975): kill-dominance reorder is bounded — an arm that is `inconclusive` with no `killed` sibling still yields `inconclusive`; `survived`+`survived` still `survived`. The selftest regression cases (60/60 passed here) pin both directions.

# Residual observations (not kills)

- **R1** `check.py:292`: `except ProcessLookupError` around `os.killpg` omits `PermissionError`/`OSError` that `teardown` catches (tool:811). A `PermissionError` would escape `run_probe` uncaught as an own-fault, not a wrong verdict. Unreachable in the intended deployment (own child, group leader); left as an own-fault path, not a kill.
- **R2** `sources-append-only.py` `has_bare_pipe` (139-154): prose containing a `|` inside `## Registry` is now exit 2 where frozen returned 0. Fail-closed and documented in the docstring, but any future SOURCES.md edit adding such prose blocks the guard entirely rather than being ignored — a strictness tradeoff to keep in mind when editing that section.
- **R3** `measure.py` misclassified cross-check (573-585): skipped entirely unless every row resolves a bucket (reported) or classification fallback — a partial-shape document silently gets no cross-check. Fail-open seam; documented as v1 compatibility.
- **R4** `kama-llamacpp-live.py --selftest` now binds real tcp6 listeners (`::1`, `::ffff:127.0.0.1`, lines 1053-1082): fails on hosts without IPv6 loopback. Passed here; environmental precondition, not a lane defect.
- Corrected counters carry selftest-only evidence (measure 38/38, survivors 60/60 — both re-run and passed in this clone). No corrected rerun of the official counting invocations exists in `runs/`; the retained artifacts are the measured failures. Consistent with the lesson's could-not-evaluate framing; flagged only so no one reads `c1-measure.json`'s counts as a post-repair measurement.

# Exact experiment sources

All run inside `/tmp/kama-r18-falsify-NoHarm/clone` at `1c325b2` (python3 3.14.8). Key harnesses:

`exp/gate_diff.py` — loads each legacy receipt, applies the mutation list, writes to tmp, runs `python3 {FROZEN|CURRENT}/check-receipt.py <tmp.json>`, compares `(exit, stdout)` pairs; reported 115 cases / 15 divergences (all cosmetic per `gate_diff2.py` dissection: identical problem sets modulo `<object object at 0x...>` sentinel text, schema-name lists, relabel-v3 path). 7-case capture dissection: `del-captures`/`del-captures-health` differ only in sentinel address; `del-captures-models`, `models-status-503/404`, `health-status-404`, `models-status-200-empty` → frozen and current exits identical (1/0/0/1/1).

`exp/gate_v3.py` — 12 v3 mutations on receipt-1.json as listed above; all INVALID except the four pristine controls (VALID with and without pins).

`exp/guard_synth3.py` — `git clone` of the lane into a temp dir; per case: checkout base, write mutated `corpus/SOURCES.md`, commit, run both guards `--from BASE --to HEAD --json`. Mutations listed above; verdicts identical except prose-pipe (frozen 0 → current 2, strictening).

`exp/check_row_diff2.py` — `importlib` loads `frozen/check.py` and current `check.py`, feeds 21 crafted probe stdouts to `probe_output_row`, compares row/error semantics with crash containment. 0 semantic divergences; 2 frozen crashes now recorded row errors.

Full-matrix differential — copied `frozen/check.py` + all 9 matrix JSONs to `/tmp/fcheck`, current `check.py` + JSONs to `/tmp/ccheck`; ran `python3 check.py --probe tools/kama-probe.sh --json` in each (37.6 s both, exit 0, 72/72 pass). Diffing `records[]` by `name` across all keys: 73 diffs, every one a `.port` value plus one port-embedded `.evidence` string; zero verdict/reason/exit/drift/route_ok/served_model diffs.

Provenance — imported `dispatch-provenance.py`, called `refused_observations`/`spawned_observations` on `build/refused-result-1.json` and `build/spawn-result.json` directly.

Selftests re-run in-clone: `measure.py --selftest` 38/38 (5.9 s), `survivors.py --selftest` 60/60 (43.3 s), `dispatch-provenance.py --selftest` 30/30, `controls.py --selftest` 70/70 incl. protected-port and no-leaked-process checks.

No installs/updates performed (pacman pause honored; nothing needed). Scratch `/tmp/kama-r18-falsify-NoHarm` removed before finish; `pgrep -af 'NoHarm|fcheck|ccheck'` → no matches; no seat-owned listeners (`ss -tlnp` shows only sibling seats' and system listeners).
