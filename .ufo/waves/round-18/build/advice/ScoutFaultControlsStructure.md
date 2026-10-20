VERDICT: confirm — all seven named mechanisms exist at the stated paths; the extension map, per-mutant fault shapes and the four missing self-consistency assertions are below.

# ScoutFaultControlsStructure — fault-controls.py extension map

Read-only recon for C2 (calibration). No detector, check.py, probe or mutant was run; no port was bound; no lane file was edited. Everything below is static derivation from the frozen bytes. Any behavioural claim about a run is marked `[INFERENCE]`.

Axes named before work: **recon fidelity** (every claim anchored at `path:line`), **extension economy** (fewest insertion sites per new fault), **non-circularity** (self-checks that never consult the check.py under test), **operability** (exit contract, hollow-success paths).

## Identity

- Target: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tests_probe-verdicts_fault-controls.py`, 815 lines, sha256 `d3eaadeb8a061b4e322868d569df77afbd7331089d06b06c86a2063fdc31b312`.
- Byte-identical to the live `tests/probe-verdicts/fault-controls.py` (`diff -q` exit 0) and to `SHA256SUMS:7`. Line numbers below therefore hold for the file C2FaultControls starts from.
- Schema `kama-fault-controls/v1` (66). Constants: `HANG_SECONDS = 40` (67), `WRAPPER_EXIT = 9` (68), `CHECK_RUN_TIMEOUT = 150` (69), pinned matrix digest/breadth (74-76).

## 1. Pipeline (main -> run_fault -> run_check -> classify_run)

`main` 710-807: fault selection (714-726) -> `--list`/`--selftest` early exit (728-731) -> `--check`/`--probe` existence (733-740) -> staging (742-760) -> F0 run (762) -> F0 gate (764-767) -> remaining faults (769-770) -> document (780-795) -> emit (796-806) -> exit (807).

- `run_check` 346-369: argv `[sys.executable, "check.py", "--probe", "wrap.py", "--json"]` plus one `--only` per row (349-351), `cwd=scratch` (353), `start_new_session=True` (359). On timeout it `killpg`s the run and returns **124**, classified as accepted, never an own fault (362-368).
- `stage_scratch` 543-556: byte-copies the subject to `check.py` (546), byte-copies every sibling `*.json` (548-550), writes `WRAPPER` to `wrap.py` 0755 (551-553), creates `cache/` (554-555).
- `run_fault` 559-606: `rows = run["rows"]` (566), env `FAULT_MODE`/`FAULT_PROBE`/`FAULT_WRAPPER_EXIT` (568-572), F6 pre-pass (573-584), hang env (585-586), malformed env (587-588), one `run_check` (589), `classify_run` (591-592), per-run `why` tag (593-594), per-fault entry (597-606).

**Per-invocation view (load-bearing for every fault).** check.py grades one probe call per selected test: `records = [grade(entry, probe) for entry in entries]` (`tests_probe-verdicts_check.py:644`) and `proc = run_probe(probe, port, test["expect"])` (`:446`). Each wrapper invocation therefore sees a one-row document, which is why corrupting `doc["rows"][0]` (279) reaches *every* row of a three-row `--only` set (F1-F5, F7).

## 2. Wrapper-probe generation

- `WRAPPER` is one raw string, 197-305. Trampoline: `exec python3 - "$@" <<'FAULT_WRAPPER_EOF'` (198), terminator column-0 at 304. The heredoc keeps `"$@"` as `sys.argv[1:]`, and `FAULT_PROBE` names the real probe (206). `stage_scratch` (551-553) is the **only** generation site; adding a mode means editing `WRAPPER`.
- Header helpers: `args` 205, `mode` 207, `die()` -> `WRAPPER_EXIT` 210-212, unset-probe guard 215-216, `opt()` accepting `--f v` and `--f=v` 219-225, `hit()` GET-only 228-236 (reads only `--port`; **swallows every exception** 235-236).

| Mode | Arm lines | Runs real probe? | Emission |
|---|---|---|---|
| `hang` | 239-240 | yes, after the sleep (266) | sleeps past check.py's 30 s probe timeout, so the subject kills the probe first; the fall-through then reaches the unknown-mode `die` (296-297) only if the subject has no timeout |
| `f6` | 242-251 | **no** | `hit("/health")` 243, replay `FAULT_CACHE` 247, exit from cache `.rc` 249 |
| `malformed` | 253-264 | yes (258) | discards probe stdout, writes `FAULT_BODY_B64` bytes 259-263, keeps probe exit 264 |
| `pass` | 267-275 | yes (266) | optional cache + `.rc` write 268-273, stdout/exit passthrough |
| field faults | 283-295 | yes (266) | parse `doc["rows"][0]` 277-281; `reason` 283-284, `verdict` 285-289, `drift` 290-291, `served` 292-293, `exit` 294-295; unknown -> `die` 296-297 |
| emitter | 299-303 | — | `doc["rows"][0] = row` 299 always rewrites row 0 of a one-row doc; `json.dumps` 300; exit flip 301-302 |

Two structural consequences for F9+:

1. The shared emitter (299-303) can only mutate row 0 of a one-row document. A mode that must change the document **shape** (two rows, no rows, non-list) has to `sys.stdout.write(...)` and `sys.exit(...)` inside its own arm, before 266 (bypass modes) or inside the 283-297 chain.
2. A parse failure of the real probe output is an own fault (277-281), not a fault result: modes that mutate fields require the real probe to have emitted valid JSON.

## 3. Row subsets per fault

| Fault | Rows | Anchor |
|---|---|---|
| F0 | `ROWS_FULL` (5) | 88-94, 112 |
| F1-F4 | `ROWS_OK_MIS_LOAD` (3: MODEL_OK / MODEL_MISMATCH / MODEL_LOADING) | 83-87, 123/129/135/141 |
| F5 | 3 explicit rows, includes the closed-port DEAD row | 147-150 |
| F6 | `F6_ROWS = ROWS_FULL[:-1]` (4 stub rows) expanded by `_per_row` into **4 runs x 1 row** | 95-96, 99-102, 156 |
| F7 | 1 row (`ReadyControls.expect-exact-id`) | 162-164 |
| F8 | 6 variants x `ROWS_FULL` (empty-array, rows-empty, row-not-object, row-null, non-json, non-utf8) | 166-188 |

Family coverage is asserted, not incidental: `want_modes` (666) and `verdict_families` (667-668) are enforced at 678-680 and 692-697. Rows must exist in the pinned matrix (74-76, 663-665, 676-677) - **the matrix cannot grow this round**, so F9+ reuses existing row names.

## 4. F0 gate

- Definition 107-113: `positive: True`, `target: None`, one `pass` run over `ROWS_FULL`.
- Gate 762-767: F0 runs before every fault; `if not positive["detected"]:` (764) prints "suite INVALID" (765-766) and returns 2 (767).
- Positive classification 512-517: exit 0 **and** parseable JSON **and** a `records` list **and** every configured row `passed is True`.
- Exit collision: `main` returns 2 for the gate (767) and for an `OwnFault` (773) and `Exception` (776). Only the stderr text distinguishes them ("suite INVALID" at 765 vs "own fault" at 774). Any negative fixture that asserts "exit 2" must also assert the message or pick a non-cache fault (see S4).
- **F0 is not selectable.** The `--only-fault` universe includes F0 (716) but the filter walks `FAULTS` only (723), so `--only-fault F0` yields zero faults, `accepted=0`, exit 0. Static `[INFERENCE]`; same shape for `--skip-slow --only-fault F7` (725-726 filters after selection).

## 5. F6 cache

- Justification in-source: "a shared cache cannot tell rows apart when several `--only` entries replay it" (99-102) - one run per row.
- Pre-pass 573-584: cache path `f6-{fault id}-{index}` (575), the same rows re-run with `FAULT_MODE=pass` (576-579), own fault if the pre-pass exits 9 or leaves no cache/`.rc` (580-583).
- Replay 242-251: hit `/health` (243), write cached stdout (247), exit with cached rc (249). The f6 replay therefore keeps `probe_exit` honest while removing `GET /v1/models`.
- **Contamination seam:** the cache key (575) distinguishes fault and run index, not row. Any cache-mode run listing more than one row shares one cache file - exactly the round-17 "shared F6 cache" survivor (`MutFaultControlsSelf.md:74-80`). The naming scheme cannot fix this; the guard must be a table assertion (S3).

## 6. Detected predicate (targeted rows)

`classify_run` 482-541, ordered:

1. `exit_code == WRAPPER_EXIT` -> raise `OwnFault` (492-494); aborts the whole suite with exit 2.
2. exit != wanted (0 positive / 1 fault) -> `False` (495-498).
3. stdout not JSON -> `False` (499-504). A traceback is **accepted**, never a detection.
4. no `records` list -> `False` (505-507); a configured row missing -> `False` (508-511).
5. positive: every row `passed is True` (512-518).
6. fault: any row whose `passed` is not `False` (including missing/None) -> `False` (519-522).
7. declared `target`: every row's `failed_conjuncts` must contain it (523-538); failure on another conjunct only -> `False`; no declared target -> `True` (539-540).

`failed_conjuncts` 450-479 is a **local re-derivation from the check.py record**, not a query to the subject: `error` truthy (454-456), `verdict` (458-459), `reason` (460-461), `probe_exit` (462-463), `drift == (verdict != "MODEL_OK")` (464-465), `served_model` vs `contract_served_model` (466-467, 404-448), and `route` for a stub row with no `GET /v1/models` among `requests` (468-478). This is the tool's non-circularity property and every new self-check must preserve it.

The legal target vocabulary is pinned at 652-653 (`CONJUNCTS = {"verdict","reason","exit","drift","served_model","route","error"}`) and validated at 671-672 - a new target name must be added there or `--selftest` fails.

Design constraints this imposes on F9+:

- The **unmutated** check.py must exit exactly 1 with the target conjunct failing. Exit 2 (harness error) and non-JSON stdout are accepted by design (495-504), so a fault that merely crashes the subject proves nothing.
- `failed_conjuncts` reads only record fields, so a fault must corrupt a field the pristine check.py actually compares (`check.py:473-482` includes `drift`, `served_model_ok` and `route_ok is not False` at `:481`).

## 7. JSON output

Document 780-795: `schema` 781, `check` 782, `check_sha256` 783, `probe_sha256` 784, `matrix{files,tests,sha256}` 785-789, `positive_control` 790, `seconds` 791, `faults` 792, `detected` 793, `accepted` 794. Per-fault entry 597-606: `id`, `title`, `target`, `rows` (deduped, 567), `runs`, `check_exit` (scalar for one run, list otherwise, 603), `detected` = `all(runs_detected)` (604), `why` (605).

Exits: 0 iff `accepted == 0` (807); 1 otherwise; 2 own fault (721, 735, 740, 767, 773, 776). `--selftest` prints JSON regardless of `--json` (706).

Two edges worth a self-check:

- `all(runs_detected)` (604) is **vacuously true** for `runs: []`, so a table edit can mint a DETECTED fault with no evidence. The same vacuity exists in the positive arm: `run_rows=[]` yields `failing=[]` (513) and a healthy F0 (517), so emptying F0's row list neuters the gate while check.py would actually run all 72 tests. Nothing in `--selftest` rejects either today (S5).
- `check_exit` changes shape (scalar vs list) at 603; multi-run F9+ must not assume a scalar.

## 8. --selftest

Flag 635-639; dispatched at 730-731 **before** `--check`/`--probe` validation (733-740), so it needs no subject. `do_selftest` 656-707 validates:

- matrix breadth and digest vs the round-16 pin (660-665);
- per fault/run/row: target in `CONJUNCTS` (671-672), row present (676-677), `port_mode` in `{stub,closed}` (678-680); `hang` must be exactly one row (681-682); `malformed` must carry `body_b64` (683-684);
- F4 must include a non-MODEL_OK row (685-691) - the `next(f for f in FAULTS if f["id"] == "F4")` pattern to copy for any per-fault rule;
- family coverage (692-697); result document (698-705); exit 707.

What it never does: call `classify_run`, `failed_conjuncts`, `run_fault` or `main`. That is why every round-17 detector weakening survives it in all four forms - `MutFaultControlsSelf.md:106-110` ("All four detector weakenings survive the tool's own selftest").

## 9. Extension points for faults F9+

| # | Site | What to change |
|---|---|---|
| E1 | 83-96 | optional new row constant; rows must already exist in the pinned matrix |
| E2 | 188-190 | append the fault dict before the closing `]` at 190; new ids are picked up by `--only-fault` (716), `--list` (641-649) and the selftest loop (670) automatically |
| E3 | 652-653 | new `target` names |
| E4 | wrapper 242-264 | bypass modes (no real probe): insert a block before 266, pattern 242-251 |
| E5 | wrapper 283-297 | field mutations: add an `elif` before `else: die` (296-297); shape changes must self-emit and `sys.exit` (shared emitter 299-303 rewrites row 0 of a one-row doc) |
| E6 | 573-588 | env plumbing: generalize `if run["mode"] == "f6":` (573) to a cache-mode set for a second replay mode; add one branch per new env key beside 585-588 |
| E7 | 673-684 | per-mode selftest rules, mirroring 681-684 |
| E8 | 685-691 | per-fault selftest rule, copying the `next(...)` pattern |
| E9 | 198/304 | heredoc terminator must stay column-0 and unique; `WRAPPER` (197-305) is the only place wrapper behaviour exists |
| E10 | 603 | `check_exit` shape changes for multi-run faults |
| E11 | 249 | a replay mode must reproduce the honest probe exit from `.rc`, or `probe_exit` stops matching the row's expected exit |
| E12 | 628-629 | `--skip-slow` is hard-coded to `F7`; a second slow fault needs inclusion |

## 10. Per-mutant fault shapes (advice for C2FaultControls)

Exact check.py anchors for each mutant are in the sibling advice `ScoutHMutantDefs.md`; below is only what fault-controls needs. All shapes assume the current check.py is the subject.

| Mutant | New mode / arm site | Target | Why it discriminates |
|---|---|---|---|
| H1 reason case | `reason_case`, beside 283-284 (`row["reason"] = str(row["reason"]).swapcase()`) | `reason` | pristine compares exactly (`check.py:475`); the H1 mutant casefolds and passes -> exit 0 -> accepted |
| H2 verdict padded | beside 285-289 (`" " + v + " "`) | `verdict` | pristine compares exactly (`check.py:474`); note `drift` recomputes from verdict (464-465) and fires too, target still present |
| H3 method | new bypass block beside 242-251: `POST /v1/models`, then replay cache | `route` | every method reaches `_respond` (`check.py:257-260`), so the POST is recorded; pristine `fetched_models_route` requires GET (`check.py:374-376`) and `passed` includes `route_ok` (`:481`); H3 ignores method and passes |
| H5 served normalisation | beside 292-293, alter an otherwise-matching id by case or a space (do **not** reuse `kama-forged-id`) | `served_model` | F5 already kills a wholly different id; only an equal-modulo-normalisation id distinguishes H5's `lower().removesuffix(".gguf")` |
| H6 no-requests | pure cache replay with **no `hit()`** (f6 minus 243) | `error` | stub sees zero requests; pristine records the 455-459 error and keeps default `passed=False` (`check.py:428`); H6 sets it True at the same site |
| H7 index | new two-row mode: corrupt rows[0], append a **deep copy** of the original row as rows[1], emit and exit | `reason` | pristine selects `rows[0]` (`check.py:397`) -> fails; H7 selects `rows[-1]` (`MutC1Preregistered2.md:17`) -> passes -> exit 0 -> accepted -> killed |

H7 notes, because this is the fault most likely to be built wrong:

- A one-row output can never kill H7: `rows[0] is rows[-1]` `[INFERENCE]` from `check.py:395-397`. The second row is mandatory.
- Use `copy.deepcopy`/re-parse before corrupting, or the appended row aliases the corrupted dict and the mutant still fails.
- rows[0] must stay structurally valid (`verdict`/`reason` strings, `drift` bool, `check.py:398-402`), so corrupt the *value*, not the type; otherwise pristine takes the malformed path and the record fails on `error`/`verdict`/`reason` rather than the intended single conjunct.
- `f6`'s "run one row per cache" rule (99-102) does **not** apply here: H7 needs two rows inside one invocation, not two invocations.

Crash debts:

- Nested JSON depth and the 5,000-digit integer are **new F8 runs**, not new modes: add `body_b64` entries at 170-188. They become detectable only when the repaired check.py records a per-row failure instead of a traceback; a traceback stays `accepted` (499-504).
- The escaped `sleep` is outside the current observation model (stdout + exit). Expressing it needs a pidfile written by a new mode, a liveness check in `run_fault` after 589, and a classification slot ("leaked process" => accepted). That changes `run_check`'s return tuple (346-369) and `classify_run`'s inputs (482); it is not a table-only addition.

## 11. Self-consistency assertions (to kill the four MutFaultControlsSelf survivors)

Insertion point: `do_selftest` 656-707. Put table rules inside the 673-684 loop, a `_selftest_classifier(tests, problems)` call after 691, and add-only result keys at 698-705. None of these may invoke the check.py under test.

**S1 - drop-target removal** (`MutFaultControlsSelf.md:34-43`, mutation `if False and target:` at 523). Build a record from a real matrix row (`ROWS_FULL[0]`): expected `verdict`/`reason`/`probe_exit`, `drift = expected_verdict != "MODEL_OK"`, `served_model = contract_served_model(tests[row])`, `requests = [{"method":"GET","path":"/v1/models"}]`. Flip only `verdict` (and set `drift` to the matching value so drift stays consistent). Then

`classify_run(1, json.dumps({"records":[rec]}), [row], tests, {"target": "reason"})` must return ok `False`.

Pristine: failed set is `{verdict}`, target absent -> `False`. Under the mutant the guard is skipped -> `True` -> assertion fails. Non-circular: reads only local functions.

**S2 - "any nonzero exit counts"** (`:52-60`). `classify_run(1, "not json", [row], tests, {"target": "reason"})` must be `False`; `classify_run(9, ...)` must raise `OwnFault`; and a positive-control call with `passed: false` must be `False` (guards the 512-518 arm too).

**S3 - shared F6 cache** (`:74-83`). For every run whose mode is a cache/replay mode assert `len(run["rows"]) == 1`; assert `len(F6.runs) == len(F6_ROWS)` == 4. The round-17 edit (`runs` becomes one dict over four rows) then fails selftest. If cache naming is factored into a helper, additionally assert per-run keys are unique, which catches a constant cache name at 575.

**S4 - F0 gate bypass** (`:97-104`). The gate is imperative in `main` (764-767), so no table assertion can see it. Add a generated `FORGED_CHECK` fixture (a constant next to `WRAPPER`, ~306) that ignores `--probe`, honours `--only`/`--json`, prints `{"records":[{"name": <each requested name>, "passed": false}]}` and exits 0. Then in `do_selftest`, with stdout and stderr redirected (`contextlib.redirect_stdout/redirect_stderr`):

`main(["--check", forged, "--probe", <existing path>, "--matrix-dir", matrix_dir, "--only-fault", "F1", "--json"]) == 2`

- Pristine: F0 runs, classification fails at 513-516, gate returns 2 (767). No fault runs, so this is fast.
- Under the mutant (`if False and not positive[...]`): F1 runs against the fixture, gets exit 0, is classified accepted (495-498), and main returns 1 -> assertion fails -> killed.
- Pitfall: with all faults selected the F6 pre-pass raises `OwnFault` (580-583) and main **also** returns 2. Selecting a non-cache fault (`--only-fault F1`) keeps the two outcomes distinguishable by value; additionally asserting the gate message text (765-766) is the belt-and-braces form.

**S5 - vacuous detection and vacuous F0.** Assert every fault has at least one run, every run at least one row, and `POSITIVE_CONTROL["runs"][0]["rows"] == ROWS_FULL`. Without this, `runs: []` makes `all([])` DETECTED (604), and an emptied F0 row list yields `failing=[]` -> healthy F0 (513-517).

**S6 - CLI honesty (no survivor, but a hollow-success path).** Assert the `--only-fault` universe (716) equals `{F0}` plus the fault ids, and that filtering (723) yields at least one fault for each advertised id. Today `--only-fault F0` (and `--skip-slow --only-fault F7`) exits 0 with `detected=0 accepted=0` - indistinguishable from a clean suite. Static `[INFERENCE]`.

What no static assertion can prove: that a fault's declared `target` names the field its wrapper actually corrupts (table and wrapper are both code; only cross-tool mutation testing observes that), and that F0 stays healthy on the real subject (a run-time fact, not a static one).

## Limitations

- Static derivation only. No detector, check.py, probe, wrapper or port was exercised; F0 health on the current bytes is unverified here (L1 owns every official measurement).
- `[INFERENCE]` marks denote code-path derivations, not observations: the `--only-fault F0` hollow exit, the H7 index mechanics, and the H3 POST-miss degradation. `hit()` swallows every exception (235-236), so a POST that fails to land degrades the fault into a zero-request fault, which the H3 mutant **also** fails (`route_ok` False for an empty request list) - the control would then report H3 surviving and hide the intended kill. A method-capable hit variant should `die()` when the request does not land.
- `WRAPPER_EXIT = 9` is reserved for wrapper faults (68, 211-212) and check.py exits only 0/1/2 today (`tests_probe-verdicts_check.py:26-27`); a future subject that legitimately exits 9 would be misread as an own fault.
- F9+ cannot add matrix rows this round (pinned digest 74-76; enforced 663-665), so every new fault must reuse existing row names and families.
- I did not evaluate check.py semantics beyond the anchors needed to ground fault shapes; that is `ScoutHMutantDefs.md`'s subject.

## Installs

None. No pacman, uv, npx, cargo or release-binary install; no network fetch.

## Report

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/advice/ScoutFaultControlsStructure.md`
