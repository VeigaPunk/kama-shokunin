# MT16C1ControlCount — round 63, C1 operability: falsify the C1 counter's control set

Seat: MT16C1ControlCount (mutation-tester, leaf). Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09` (lane HEAD, verified).
Counter under test: `tools/round63-c1-counter.py` (735 lines at tip). Mutations made only in my scratch clone
`/fast/scratch/hyaku/kama-r63/w/MT16C1ControlCount/clone` (`git clone --shared`, toplevel asserted before every commit).
Each mutant was committed in the clone and the mutated counter was run **from the clone path** against the clone
(`python3 <clone>/tools/round63-c1-counter.py --repo <clone> --tip <commit> --work <scratch>`). The live request-plane
receipt is real: the counter spawns `tools/kama-completion-live.py` on an unregistered loopback port against the pinned
`stories260K.gguf` fixture (`verdict=REQUEST_OK`, `listener_owned` true); one counter invocation takes ~1.5 s.
Installs/updates during this seat: **none** (no tool was needed; pacman not touched).
Lane: read-only use only (`git clone --shared`, `git rev-parse`, `git status`). Lane's own `M`/`??` entries
(PROVINCE.md, corpus/*, .ufo/waves/round-63/source/, w1.ready) belong to other seats; not touched by me.

## Summary

| # | Probe | Result | Verdict |
|---|---|---|---|
| 0 | Baseline (unmutated counter @ tip) | `met=True`, 44/44, eval 3/3 | control |
| 1 | Delete 5 control entries from `build_controls` | `controls_targeted=39/39 ... met=False` | KILLED (see defect D1: no reason printed) |
| 2 | `EXPECT_CONTROLS = 45` | `controls_targeted=44/44 ... met=False` | KILLED (see D1) |
| 3 | `EXPECT_CONTROLS = 43` | `controls_targeted=44/44 ... met=False` | KILLED (see D1) |
| 4 | Extra: deletion of 5 **and** `EXPECT_CONTROLS = 39` | `controls_targeted=39/39 ... met=True` | **SURVIVED** (see D2, prominent) |
| 5 | Per-control flip: 44 controls, each run with only its named check discarded | 44/44 flip; each run `controls_targeted=43/44 met=False` with exactly one `escape` line | all 44 independent |
| 6 | Per-family flip: 19 families, each run with only that family's named checks discarded | 19/19 flip exclusively; escapes == family size in every run | all families exclusive |

**Prominent defect (SURVIVED, mutant 4):** a shrunken control set is accepted when `EXPECT_CONTROLS` is lowered with it.
The counter's only pin on "44" is its own module constant; it never reads the frozen text in
`.ufo/waves/round-63/controls/freeze.txt`. See D2.

## 1. Baseline (control)

```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
exit 0, stderr empty. Control-count census by reading the code: `build_controls` appends 42 entries (the 42 `add(...)` calls)
and the fake loop adds 2 more, total 44 (matches `EXPECT_CONTROLS = 44`).

## 2. Mutant: delete five control entries (KILLED)

Patch: `mutants/del5.patch` (commit `2728924e`, 9 source lines removed). Removed:
- `stale` (nonce_match) — lines 524-525 — family vanishes
- `timing` (predicted_ms=-1.0, completion_timings) — lines 572-573
- `idcr` (created=True, completion_id_created) — lines 592-593
- `schema` (schema) — lines 616-617 — family vanishes
- `witness` (live_text) — line 626

Counter output (exit 1, stderr empty):
```
tool_present=1 live_ok=1/1 controls_targeted=39/39 eval_selftest=3/3 errors=0 met=False families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=2/2 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 shape=4/4 sigterm=1/1 tamper=8/8 timing=3/3 trunc=2/2 witness=5/5]
```
Notices a shrunken set? **Yes, but only by `met=False`.** The line shows `/39` (so an operator who knows 44 can
infer it) but the counter never states the expected count, appends no entry to `errors`, and prints nothing on
stderr. Vanished families (`stale`, `schema`) are simply absent from `families[...]` with no message.

## 3. Mutant: change `EXPECT_CONTROLS` (both KILLED)

- `EXPECT_CONTROLS = 45` (commit `1f778e2a`, `mutants/exp45.patch`):
  ```
  tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=False families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
  ```
  exit 1, stderr empty.
- `EXPECT_CONTROLS = 43` (commit `17b54602`, `mutants/exp43.patch`):
  ```
  tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=False families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
  ```
  exit 1, stderr empty.

Both are killed by the `total == EXPECT_CONTROLS and rejected == EXPECT_CONTROLS` clause, but the printed line
reads `44/44 ... met=False`: every number on it looks healthy and the reason is invisible (D1).

## 4. Extra mutant: deletion + lowered constant (SURVIVED)

Branch `mut-combo` = the deletion mutant (table row 1) plus `EXPECT_CONTROLS = 39` (commit `af6ce165`, `mutants/combo-del5-exp39.patch`).
Counter output (exit **0**, stderr empty):
```
tool_present=1 live_ok=1/1 controls_targeted=39/39 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=2/2 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 shape=4/4 sigterm=1/1 tamper=8/8 timing=3/3 trunc=2/2 witness=5/5]
```
exit 0, stderr empty. The `families[...]` line has no `stale` and no `schema` entry: both families were removed entirely.

The counter accepts a 39-control set as `met=True`. The frozen predicate and freeze.txt say "all 44 targeted
controls"; the counter does not read freeze.txt, `.ufo/waves/round-63/controls/`, or any count from a tip blob, so
44 is enforced only by a constant the mutant can change in the same commit. Kill rule in freeze.txt ("any control not
rejected by its named check") is not triggered because no control escapes — the set is simply smaller.

## 5. Per-control independence (44/44 flip)

Mutation design (one edit to the clone counter, commit `34b48d0a`, `mutants/hook-per-control.patch`): in the main
scoring loop, `if str(ordn) == os.environ.get('MUT_ID','')` → `s['fails'].discard(expect)` before `is_hit`; the fake
loop uses `name == MUT_ID`. This makes **only** the selected control's named check pass; all other controls are scored
identically. Inert check with `MUT_ID` unset: `controls_targeted=44/44 ... met=True` (exit 0).

Each sweep run printed `controls_targeted=43/44 eval_selftest=3/3 errors=0 met=False` (rc 1) and exactly one
`error: escape <family> expect=<name>` on stderr, naming the mutated control. Ordinals follow build_controls order (42 entries) plus the 2 fake controls; the map is `counter-out/map.txt`.

| id | family | named check (discarded) | residual fails after discard (`[:4]` as printed) |
|---|---|---|---|
| 0 | stale | nonce_match | [] |
| 1 | log | health_ready | inconsistent:health_ready |
| 2 | tamper | completion_envelope (cap 30) | completion_choice_shape, completion_deterministic, completion_fingerprint, … |
| 3 | tamper | hold_released | inconsistent:hold_released |
| 4 | tamper | teardown_clean (child_pre_dead) | inconsistent:teardown_clean |
| 5 | tamper | teardown_clean (returncode 137) | inconsistent:teardown_clean |
| 6 | tamper | teardown_port_closed | inconsistent:teardown_port_closed |
| 7 | tamper | verdict | [] |
| 8 | tamper | completion_deterministic | inconsistent:completion_deterministic |
| 9 | tamper | model_digest | inconsistent:model_digest, inconsistent:server_digest, live_server_sha, server_digest |
| 10 | predead | teardown_clean | inconsistent:teardown_clean |
| 11 | sigterm | teardown_clean | inconsistent:teardown_clean |
| 12 | hold | hold_released | inconsistent:hold_released |
| 13 | outside | completion_model_id | inconsistent:completion_model_id |
| 14 | hdr | completion_headers (text/plain) | inconsistent:completion_headers |
| 15 | hdr | completion_headers (pop) | inconsistent:completion_headers |
| 16 | trunc | completion_untruncated (body_truncated) | inconsistent:completion_untruncated |
| 17 | trunc | completion_untruncated (content-length+1) | inconsistent:completion_untruncated |
| 18 | timing | completion_timings (predicted_ms=-1.0) | inconsistent:completion_timings |
| 19 | timing | completion_timings (predicted_ms=True) | inconsistent:completion_timings |
| 20 | timing | completion_timings (predicted_ms=inf) | inconsistent:completion_timings |
| 21 | timing | completion_timings (cache_n popped) | inconsistent:completion_timings |
| 22 | shape | completion_choice_shape (2 choices) | inconsistent:completion_choice_shape |
| 23 | shape | completion_choice_shape (index 1) | inconsistent:completion_choice_shape |
| 24 | shape | completion_choice_shape (text '') | completion_deterministic, inconsistent:…(4 printed) |
| 25 | shape | completion_choice_shape (logprobs {}) | inconsistent:completion_choice_shape |
| 26 | idcr | completion_id_created (id '') | inconsistent:completion_id_created |
| 27 | idcr | completion_id_created (created True) | inconsistent:completion_id_created |
| 28 | idcr | completion_id_created (created 5) | inconsistent:completion_id_created |
| 29 | ptok | completion_prompt_tokens (+1) | inconsistent:completion_prompt_tokens |
| 30 | ptok | completion_prompt_tokens (tokenize +1) | inconsistent:completion_prompt_tokens |
| 31 | reqbind | completion_request_bound (prompt text) | completion_deterministic, inconsistent:… |
| 32 | reqbind | completion_request_bound (sha 0s) | completion_deterministic, inconsistent:… |
| 33 | listener | listener_owned | [] |
| 34 | digest | model_digest (decoy path) | inconsistent:model_digest |
| 35 | schema | schema (v1) | [] |
| 36 | witness | live_fp_capture | [] |
| 37 | witness | live_ptok (+1) | [] |
| 38 | witness | live_object | [] |
| 39 | witness | live_text | [] |
| 40 | witness | live_pid | [] |
| 41 | witness | live_owned | [] |
| fake-inconsistent | fake | live_ptok | live_owned, live_port |
| fake-foreign | fake | live_pid | live_port |

Reading the residuals: "[]" means the named check was the sole failure of that control, so removing it leaves nothing.
`inconsistent:<name>` means the stored `checks.<name>.passed` disagrees with the recomputed value; the counter credits a
control only via the base name, so the twin flag is not a second route to credit (it only inflates the cap count).
Exact per-run lines are in `counter-out/sweep.txt`; the sweep took 66 s for 44 runs.

## 6. Per-family flip (19/19 exclusive)

Same hook, keyed by family (`MUT_FAM`; commit `33c53cec`, `mutants/hook-per-control-plus-family.patch`). Inert
check with `MUT_FAM` unset: `controls_targeted=44/44 ... met=True`. Every run: `met=False`, and `escapes` equals the
family's size, `controls_targeted = 44 − size`:

| family | size | controls_targeted printed | escapes |
|---|---|---|---|
| stale | 1 | 43/44 | 1 |
| log | 1 | 43/44 | 1 |
| tamper | 8 | 36/44 | 8 |
| predead | 1 | 43/44 | 1 |
| sigterm | 1 | 43/44 | 1 |
| hold | 1 | 43/44 | 1 |
| outside | 1 | 43/44 | 1 |
| hdr | 2 | 42/44 | 2 |
| trunc | 2 | 42/44 | 2 |
| timing | 4 | 40/44 | 4 |
| shape | 4 | 40/44 | 4 |
| idcr | 3 | 41/44 | 3 |
| ptok | 2 | 42/44 | 2 |
| reqbind | 2 | 42/44 | 2 |
| listener | 1 | 43/44 | 1 |
| digest | 1 | 43/44 | 1 |
| schema | 1 | 43/44 | 1 |
| witness | 6 | 38/44 | 6 |
| fake | 2 | 42/44 | 2 |

Sum of sizes = 44. Every family flips, and only its own controls escape.

## Defects found (counter / control set)

- **D2 (SURVIVED, prominent).** Mutant 4: `build_controls` loses 5 controls *and* `EXPECT_CONTROLS` is lowered to 39
  in the same commit → `met=True`, exit 0. The counter's sole guard for the frozen "44" is its own constant; it does
  not compare against freeze.txt or any tip-blob count. A reviewer who reads only the counter output gets a pass.
  Suggested fix (advisory, not applied): derive the expected count from a committed list of control IDs read from a
  tip blob, or assert the frozen count string that is present in `.ufo/waves/round-63/controls/freeze.txt` at the tip.
- **D1 (operability, not a silent pass).** On a count mismatch the counter prints a line with `controls_targeted=N/N`
  and `met=False`, and appends nothing to `errors`, so stderr stays empty. Mutants 2 and 3 (table rows 2, 3) print `44/44 ... met=False`,
  which reads as a contradiction. Mutant 1 prints `39/39` and families silently drop. Suggested fix (advisory): append
  `controls: total=<t> expected=<EXPECT_CONTROLS>` to `errors` when `total != EXPECT_CONTROLS`, so the reason appears
  on stderr.
- **Note (not a defect of the controls).** Several controls are credited only through the base-name check; their
  `inconsistent:<name>` twin remains after discard. This is consistent with the rule in freeze.txt (credit requires the
  named check in the fail set); it is recorded so that a reader of `fails=[...]` knows the twin is not a second credit path.
- **Note (hook artifact, disclosed).** The discard hook removes the named check from `s['fails']` but leaves `s['met']`
  as computed before the discard. For the `fails=[]` rows this means `met=False` with an empty set. The credit test is
  `(not met) and expect in fails`, so the escape result is the same as a fully recomputed `met`; the artifact does not
  change any verdict above.

## Evidence files (under .ufo/waves/round-63/w1/out/MT16C1ControlCount/)

- `counter-out/base.out|err` (baseline), `del5.*`, `exp45.*`, `exp43.*`, `combo.*` (mutants 1-4, verbatim outputs)
- `counter-out/<id>.out|err` for ids 0-41, `fake-inconsistent`, `fake-foreign` (per-control runs, MUT_ID); `counter-out/sweep.txt` (one line per run)
- `counter-out/fam-<family>.out|err` (family sweep, 19 families) and `famsweep.txt`; `counter-out/map.txt` (ordinal map, from `map.py`)
- `mutants/*.patch` (diffs vs 03a6a1d8: del5, exp45, exp43, combo-del5-exp39, hook-per-control, hook-per-control-plus-family)
- `receipts/base-receipt.json` (the genuine REQUEST_OK receipt the controls were applied to)

## Tally

Deletion (5 entries): KILLED (met=False) · EXPECT=45: KILLED · EXPECT=43: KILLED · deletion+EXPECT=39: SURVIVED (met=True) · baseline and hooks inert: 44/44 met=True.

`per-control: 44/44 flipped (each 43/44 met=False, one named escape) · per-family: 19/19 exclusive · survived mutants: 1 (combined shrink, D2)`
