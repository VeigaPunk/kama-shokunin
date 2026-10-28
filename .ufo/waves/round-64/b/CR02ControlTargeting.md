# CR02ControlTargeting - round 64 wave b, C1 control targeting (advisory)

Seat: CR02ControlTargeting (leaf, no dispatch). Lane: kama. Axis: operability. Milestone: control validity.
Tip scored: f6a4ea9a8b5a876d685b08e7e582ec0723412a4a (freeze). Clone: fresh `git clone --shared`, checked out at the freeze, `rev-parse --show-toplevel` asserted.
Evidence: `.ufo/waves/round-64/b/out/CR02ControlTargeting/` (run outputs, per-control fail sets, driver scripts). No tools installed or upgraded (python3 stdlib only; `llama-server` is the pinned host binary, found by the counter).

## Summary (findings, not verdicts on claims)

1. **Baseline at freeze is met=True, 76/76, families exact** (fresh `--work`). Every named family is credited; no escapes.
2. **The credit rule checks presence, not causation.** `is_hit` credits a control when its named check is anywhere in the re-score fail set and the set is within its cap. A control with a *wrong* name is credited whenever that wrong name co-fails. Built and run 3 such mis-named variants (V1-V3): **all 3 credited, met=True (SURVIVED)**. Two mis-named variants with absent names (V4-V5) are refused (KILLED). The eval self-test never exercises a co-failing wrong name.
3. **A reused `--work` directory silently breaks the counter.** A second run on a used work dir prints met=False with 69/76 and 7 live forgeries failing `tool exited before hold.json` (reproduced twice). A fresh dir prints met=True. The counter does not refuse reuse (unlike the C2 `work-reused` rule). Mechanism: the stale `hold/release` file survives; the fakes' hold helper returns at once and unlinks `hold.json` before the counter's 0.1 s poll.
4. **`hold_fresh` has no upper bound.** A `hold.json` whose mtime is one hour in the future passes `hold_fresh` and the whole binding grade (probe, section 6). The `stale_future` control is therefore rejected by the holder start-ticks clause, not by the future mtime its name describes.
5. **17 grader checks are named by no control.** Neutering `live_server_sha` (a probe) leaves the counter at met=True, 76/76 (SURVIVED).
6. **Several controls are not independent** (section 4): two identical single edits (hold, predead), one near-duplicate pair (tamper 137 vs sigterm -9), and the forged-tool / live-fake families whose named check is one of many co-failing checks.

## 1. Method

- Counter run at the freeze: fresh work dir (`/work-fresh`) met=True. Reused work: met=False (section 3).
- Diagnostic driver `diag.py` (in out dir) loads the counter module by path, wraps only `is_hit`, and logs every credited control's expected name, cap and full fail set. It edits nothing in the counter. Run on a fresh dir: 79 rows = 76 controls + 3 eval self-test rows (the 3 self-test rows are expected to be refused).
- Mutants: one-line edits made in the clone's `tools/round64-c1-counter.py` with the edit tool, run with a fresh work dir each, then restored with `git -C <clone> checkout -- tools/round64-c1-counter.py` (clone-only git). Restoration verified by `git status --short` (empty) and grep of the on-disk file.
- Control definitions read: `build_controls` (lines 1225-1414), `run_controls` (1551-1706), `score`/`grade`/`grade_binding`/`probe_fails` (400-734), `witness_run` (856-939), the fake modes (1033-1135), `forge_variants` (1163-1184), eval self-test (1537-1548). Tool-side: `hold_for_witness` (kama-llamacpp-live.py 327-370), the tool's hold block (kama-completion-live.py 531-558).

## 2. Per-family: is the NAMED check the real cause?

Row numbers are the fresh-run order (0-based, out/CR02ControlTargeting/diag-fresh.jsonl). "Clean" = the named check is the only plain fail (inconsistent: flags from stored checks are not counted).

| family (n) | named check(s) | other fails in the same re-score | named check is the real cause? |
|---|---|---|---|
| stale (1) | nonce_match | none | yes, clean |
| log (1) | health_ready | none | yes, clean |
| tamper (8) | completion_envelope (r2, cap 30); hold_released (r3); teardown_clean (r4, r5); teardown_port_closed (r6); verdict (r7); completion_deterministic (r8); model_digest (r9) | r2: 13 gated checks (envelope gate cascade, legit under cap 30); r9: server_digest, live_server_sha | yes in all 8; r3 and r4 are duplicated (section 4) |
| predead (1) | teardown_clean (r10) | none | yes, but identical edit to tamper r4 |
| sigterm (1) | teardown_clean (r11) | none | yes; same field/check as tamper r5 (137 vs -9) |
| hold (1) | hold_released (r12) | none | yes, but identical edit to tamper r3 |
| outside (1) | completion_model_id | none | yes, clean |
| hdr (2) | completion_headers (r14, r15) | none | yes, clean (two branches) |
| trunc (2) | completion_untruncated (r16, r17) | none | yes, clean (two branches) |
| timing (4) | completion_timings (r18-r21) | none | yes, clean |
| shape (4) | completion_choice_shape (r22-r25) | r24 (text '') also completion_deterministic | yes |
| idcr (3) | completion_id_created (r26-r28) | none | yes, clean |
| ptok (2) | completion_prompt_tokens (r29, r30) | none | yes, clean |
| reqbind (2) | completion_request_bound (r31, r32) | completion_deterministic in both (request sha changes) | yes |
| listener (1) | listener_owned (r33) | none | yes (self-report field only, read from stored checks) |
| digest (1) | model_digest (r34) | none | yes, clean |
| schema (1) | schema (r35) | none | yes, clean |
| witness (5) | live_fp_capture (r36, clean); live_ptok (r37); live_object (r38, clean); live_text (r39); live_pid (r40, clean) | r37: live_ref_usage, live_run_field; r39: live_ref_text | yes; the live_ref_* co-failures are the ones the review named |
| runfield (4) | live_ref_text (r41); live_run_field (r42, r43); live_ref_usage (r44) | r41: live_ref_usage, live_run_field; r42: live_ref_usage; r43, r44 clean | yes |
| bind (20) | bind_exe x2 (r45, r46), bind_holders x3 (r47-r49), bind_listener, bind_argv x3, bind_env x3, bind_maps x3, bind_ancestry, hold_fresh x2 (r61, r62), teardown_observed, bind_stable (r64) | r45: bind_claim, bind_stable; r46: bind_claim; r47: bind_claim, bind_stable; r62: bind_stable; others clean | named check is the cause of the mutated field's failure in all 20; raw_a-only edits also fire bind_claim/bind_stable (4 controls) |
| detach (1) | bind_ancestry (r65) | none | yes, clean |
| proxy (1) | bind_holders (r66) | bind_ancestry, bind_argv, bind_claim, bind_exe, bind_maps | **no**: the same fake is rejected by 5 other binding checks |
| canned (1) | bind_exe (r67) | 15 others: bind_holders, bind_argv, bind_maps, bind_ancestry, bind_claim, live_* | **no**: bind_exe is one of ~16 rejections |
| stalehold (2) | hold_fresh (r68 old, r69 future) | 20 others each: the stale hold names a dead server, so bind_listener, live_* fail | **no** as a freshness test: old mtime fails the mtime clause; future mtime passes the mtime clause and fails only the start-ticks clause (section 6) |
| preload (1) | bind_env (r70) | none | yes, clean |
| pathcopy (1) | bind_exe (r71) | bind_argv, bind_claim, bind_maps | partly: bind_argv and bind_maps alone reject it |
| forge (3) | bind_holders (r72 A, r73 A2, r74 B2) | bind_ancestry, bind_argv, bind_exe, bind_maps (all three); bind_claim (A2, B2); listener_holders_pinned, verdict (A); live_ref_* (A, B2) | **no**: bind_exe and bind_argv reject each forgery without bind_holders |
| relabel (1) | bind_claim (r75) | listener_holders_pinned, two missing/unexpected inconsistent flags (same stripped field) | yes, both checks fire from the same edit |

Families where the named check is NOT the sole or decisive cause: proxy, canned, stalehold (freshness clause), forge x3, pathcopy (partly). In those, the rejection would survive removing the named check, so the control does not isolate it. Under the freeze's credit rule this still counts (named check present, cap respected), which is the source of finding 2.

## 3. Mis-named variants (right mutation, wrong expected check)

Each variant changes only the expected-name argument of one `add(...)` line in a clone copy of the counter (line numbers in the frozen counter). The mutation is unchanged, so the control fails exactly as before. Result = whether the counter credits it (met=True, family totals still exact) or refuses it (met=False with the escape printed).

| id | line | control (row) | mutation | expect: was -> now | fail set (plain) | counter verdict |
|---|---|---|---|---|---|---|
| V1 | 1372 | bind (r46) | holder exe = /usr/bin/python3 | bind_exe -> bind_claim | bind_claim, bind_exe | **SURVIVED** (credited) |
| V2 | 1370 | bind (r45) | holder exe_sha256 = 0s | bind_exe -> bind_stable | bind_claim, bind_exe, bind_stable | **SURVIVED** (credited) |
| V3 | 1343 | witness (r37) | probe0 usage_prompt_tokens +1 | live_ptok -> live_ref_usage | live_ptok, live_ref_usage, live_run_field | **SURVIVED** (credited) |
| V4 | 1347 | witness (r40) | witness hold_pid = 1 | live_pid -> live_port | live_pid | **KILLED** (refused) |
| V5 | 1327 | listener (r33) | listener_owned passed = False | listener_owned -> schema | listener_owned | **KILLED** (refused) |
| N1 | 708 | (coverage probe, not a variant) | `fails.add('live_server_sha')` replaced by `pass` | none names it | - | **SURVIVED** (no control names it) |

One-line outputs (verbatim from out/CR02ControlTargeting/v*.out and n1.out; the families field is pasted in full on every line):

```
V1: tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
V2: tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
V3: tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
V4: tool_present=1 live_ok=1/1 controls_targeted=75/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=4/5]
     error: escape witness/live_port expect=live_port met=False nfails=1 fails=['live_pid']
V5: tool_present=1 live_ok=1/1 controls_targeted=75/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=0/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
     error: escape listener/schema expect=schema met=False nfails=1 fails=['listener_owned']
N1: tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
```

Reading: the counter credits a control whose wrong name is a co-failure (V1-V3), because `is_hit` tests `expect in fails`, not causation. Absent wrong names are refused (V4, V5). The eval self-test (1537-1548) does not cover V1-V3: its three planted controls are (a) a nonce mutation expecting `live_ptok` (refused for the absent name), (b) an envelope mutation refused by its cap of 5 (26 fails), not by its name, and (c) the unmutated receipt (no fails). None is a co-failing wrong name.

## 4. Controls that are not independent

- **Identical single edit, two families:** `tamper` row 4 (`teardown.child_pre_dead = True`, expect teardown_clean) and `predead` row 10 (same edit, same expect). Same for `tamper` row 3 (`hold.released = False`, expect hold_released) and `hold` row 12 (same edit, same expect). Both pairs count twice toward the 76. Removing either requires an amendment (EXPECT_FAMILIES is frozen).
- **Same field and check, different value:** `tamper` row 5 (returncode 137) and `sigterm` row 11 (returncode -9) both test the `returncode in (0, -15)` clause.
- **Same clause, different input:** `bind_argv` rows 51 (argv replaced with `--port 1`) and 52 (`--port 2` appended) both fail the `port == [str(port)]` clause; `bind_env` rows 54 (LD_PRELOAD) and 55 (GLIBC_TUNABLES) both fail the same `startswith` clause.
- **Near-duplicate forgeries:** `forge` A (r72) and A2 (r73) differ by one line (the holder fabrication); B2 (r74) is A2 plus the sleeper patch. All three expect bind_holders.
- **Co-failures that make a control depend on another check:** bind_claim fires with raw_a-only holder edits (bind r45, r46, r47; pathcopy; forge A2/B2; proxy; canned); bind_stable fires with raw_a-only edits (bind r45, r47, r62). A control that names bind_exe is therefore also a control for bind_claim and bind_stable. This is exactly what V1-V2 exploit.
- **Live ref co-failures:** live_ptok (witness r37), live_text (r39), runfield r41, r42 all also fire live_ref_text/live_ref_usage/live_run_field, so they are not isolated tests of their named check.
- Stale fakes: `stale_old` and `stale_future` share one stale document and expect the same check; they differ only in mtime direction, and the future one does not exercise the future direction (section 6).

## 5. Coverage: grader checks no control names (static enumeration, confirmed by N1)

Checks produced by `grade`/`score`/`grade_binding`/`probe_fails` that appear in no control's expected name: `bad_request_graded`, `completion_fingerprint`, `completion_finish_reason`, `completion_usage`, `listener_holders_pinned` (not isolated; only co-fires in relabel/forge), `live_created`, `live_ctype`, `live_fp_shape`, `live_model`, `live_model_sha`, `live_port`, `live_probes`, `live_server_sha` (N1 SURVIVED), `live_status`, `models_alias_id`, `props_alias`, `server_digest` (co-fires in tamper r9 only).

N1 is partly mitigated: `bind_exe` re-hashes the holder's exe, so a forged server digest in hold.json is still caught on the holder side. The hold.json-declared server digest itself is not validated when the check is neutered. Other unnamed checks were not run individually; the enumeration is static (regex on the frozen counter), so treat the list as a lead, not a measured gap.

## 6. Probes on the binding grader

- **Future-dated hold.json (probe, out/fut_probe.py):** capturing the genuine live binding and re-grading with the mtime moved: genuine (mtime just after t0) -> hold_fresh true, all bind true; mtime +1 h -> hold_fresh **true**, all bind **true**; mtime before t0 -> hold_fresh false. `hold_fresh` checks `mt > t0` with no upper bound. `stale_future` (fut mode) fails only because the old holder's start_ticks predate the tool.

## 7. Work-dir reuse (operability)

- Same `--work` for the second run (run-freeze-2-reusedwork.out, run-reuse-repeat.out, identical outcome): **met=False**, `controls_targeted=69/76`, `families_exact=0`, `errors=0` in the summary line; the seven live fakes instead print detail lines `error: fake detach/proxy/canned/stale_old/stale_future/preload/pathcopy: no receipt/witness ['tool exited before hold.json']` (fake failures go to `detail`, not `errors`, so they show as zero-credit families). The live control still passed (live_ok=1/1).
- Fresh work dir (run-freeze-3-fresh.out, diag-fresh): met=True 76/76.
- Mechanism ([INFERENCE] from reading, consistent with the observed error; not separately traced): `witness_run` never clears `<work>/<label>/hold/`, so a `release` file left by the previous run is present at the start of the next run. The fake hold helper (`hold_and_release`, FAKE_COMMON 980-988) returns at once when `release` exists, unlinks `hold.json`, and the counter's 0.1 s poll misses it. The live tool's wait (kama-llamacpp-live.py 355-358) also returns at once on an existing release, yet the live control passed in both reused runs; I did not establish why, so the live pass under reuse is unexplained, not explained away.
- The counter has no refusal for a non-empty `--work` (contrast C2's `work-reused` exit 2). A reused work dir therefore gives a false negative here, and a live pass whose hold window was not counter-owned cannot be ruled out.

## 8. Freeze / counter observations for the L1

- Fake-tool scenarios use cap 99 (`credit(..., 99, ...)`); the freeze states 14 only for patched-tool forgeries. Fakes cascade: canned 16 fails, stale 21 fails. Any cap <= 15 would reject controls the counter now credits. The freeze should state the fake cap numerically.
- The eval self-test's second planted control is refused by cap, not by name (section 3).

## 9. Smallest safe corrections (for the L1 to decide; no edits made by this seat)

1. Credit rule: credit a control only when its expected check is the declared root of the mutated field (a field->check table independent of the `add(...)` argument) and the fail set is that root plus the declared cascade for that field. This is intended to refuse V1-V3; not tested by this seat (a cascade for an exe edit does not make bind_claim its root). Add V1 and V3 to the eval self-test as planted co-failing wrong names; both must be refused.
2. Work reuse: `witness_run` removes `<label>/hold/` (or the counter refuses a non-empty work dir with a `work-reused` exit, as C2 does).
3. `hold_fresh`: add an upper bound on `hold_mtime_ns` (`<= now + small tolerance`), and a control with a future-dated mtime whose holder ancestry is otherwise genuine.
4. Add controls for `live_server_sha`, `server_digest`, `live_port`, and the other unnamed checks, or record them as derived-only in the freeze.
5. Duplicate controls (hold/predead) and near-duplicates change the frozen family count; any removal is a numbered amendment.

## 10. Tools

None installed, upgraded, or removed. Pacman not used. Python stdlib only; `llama-server` and the stories260K fixture were the host's pinned copies (the counter's own check).

## Counter line (frozen tip, fresh work dir; exit 0)

tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
