VERDICT: partial — the before/after skeleton is sound, but the frozen arm is not runnable in place, K3's baseline acceptance is a sub-millisecond race, and exit-code-only detection does not attribute failures to the repaired predicates.

# Scope and method

Read-only review of the C2 measurement design as specified in the wave-2 build spec (`.ufo/waves/round-17/build/spec.json:24` C2LiveTool, `:29` C2ReceiptGate, `:34` C2Controls) and as it will be executed by L1: `accepted-bad` controls before (frozen tool+gate) → after (current tool+gate), plus one real b11755 run and gate.

Read: frozen tool `.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py` (sha256 b8c5e8d4…fe4), frozen gate `.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py` (sha256 6b9576a1…ed6), the round-16 live receipts and `live/controls.txt`, the round-16 falsify advice (`ReviewLiveHarnessCode.md`, `ReviewReceiptGateCode.md`, `MutateLiveRefusal.md`, `CriticC2Admission.md`, `CriticNoHarm.md`), the pinned b11755 sources under `.ufo/waves/round-17/sources/llama.cpp-704366d76/`, and the Python `Popen.returncode` docs.

I confirmed read-only that `tools/kama-llamacpp-live.py`, `tools/kama-probe.sh` and `tests/llamacpp-live/check-receipt.py` were byte-identical to the frozen copies at review start (same three sha256), that `~/.local/opt/llama-b11755/llama-server` is sha256 `b6a31a8e…d804`, and that the fixture model is sha256 `270cba1b…256d`. While the review ran, both C2 seats began their v2 edits: `tests/llamacpp-live/check-receipt.py` is now 59,570 bytes, sha256 `f6467f5a…5955`, and `tools/kama-llamacpp-live.py` is now 42,023 bytes, sha256 `2c2d7b61…e5f5` (both uncommitted and mid-edit); findings marked "(working-tree …)" refer to those intermediates and must be re-checked against the committed bytes. At the 12:31 tool snapshot the v2 header and constants exist but the new checks do not yet, and `teardown()` still tests `proc.returncode is None` (`tools/kama-llamacpp-live.py:672`). No llama-server was started, no port was bound, and `controls.py`/`mutants.py`/`measure.py` were not run.

No resume path is in scope for C2; the lane has one runtime (b11755) and no same-identity rerouting or saturation claim to check.

# What the real b11755 run must show for no-harm (capability still works)

The real run is the *sufficiency/no-harm* half: it shows the strengthened harness still observes and grades a conforming real server. A fake cannot substitute for it, because the fake encodes the same assumptions as the checks.

| # | Required evidence | Why / source |
|---|---|---|
| R1 | Tool exit 0; **current** gate exit 0 with all four pins: `--expect-model-sha256 270cba1b…256d`, `--expect-server-sha256 b6a31a8e…d804`, `--expect-probe-sha256 36b64978…29d3`, `--expect-tool-sha256 <new tool sha>` | The gate's pins are optional (`check-receipt.py:1105-1113`); without the server pin a different build gets `VALID` (`CriticC2Admission.md:46-55`: "no pins → exit 0 VALID"). Gate exit 0 alone is not a b11755 claim. |
| R2 | Receipt schema `kama-llamacpp-live/v2`, `setup_error: null`, the exact 11 v2 check ids, all `passed: true` | C2ReceiptGate spec (`spec.json:29`); v1 names kept where meaning is kept. |
| R3 | `health_ready`: recorded body equals `{"status":"ok"}` as a JSON object (no extra keys), status 200 | `server-context.cpp:5297` `res->ok({{"status", "ok"}});`; round-16 real receipt `receipt.json:22` and `:473` already record exactly that body. |
| R4 | `teardown_graceful`: `sigterm_sent true`, `sigkill_sent false`, `returncode 0`, `alive_at_teardown_start true` | Source: `server.cpp:519-523` shutdown handler → `:534` `sigaction(SIGTERM…)` → `:590` `return 0;`; Python negative returncode = signal death (`Popen.returncode` docs). Round-16 real receipt `receipt.json:413-415`: rc 0, sigkill false, sigterm true, `term_wait_ms 3`. |
| R5 | `teardown_port_closed`: `port_listener_ownership == "child"` and `port_refuses true`, and the receipt port is not in `port_refusal_set` (8080/34113/registry) | `receipt.json:224` (`child`) and `:412` (`port_refuses true`); gate checks pin/refusal (`check-receipt.py:203-232`). |
| R6 | `loading_envelope_graded`: record `loading_observed`; if true, the stored 503 body must be the exact envelope (message/type/int 503); if false, the tool contract permits a vacuous pass, but the working-tree v2 gate currently rejects that receipt (F13), so L1 must either observe loading or reconcile the gate first | `server-http.cpp:307-328` `middleware_server_state` / `"Loading model"`; round-16 real receipt `receipt.json:212-213` (`true/true`) and `loading_503` body at `:201`; gate `check-receipt.py:913-915`. |
| R7 | `model_unchanged`: pre == post == `270cba1b…256d`; `argv` contains `--host 127.0.0.1` and ends `--no-webui --offline`; `child_env_keys ⊆ {PATH,HOME,LANG,LC_ALL,TMPDIR}` | `receipt.json:216/218`, `:423+` transitions; gate re-derivations (`check-receipt.py:339-390`). |
| R8 | The six retained subject-behaviour checks pass with their observed values: `models_alias_id` (data[].id = alias), `models_owned_by_llamacpp`, `metrics_not_enabled` (501), `props_alias`, `probe_model_ok` (exit 0/MODEL_OK/matched), `probe_mismatch` (exit 2/MODEL_MISMATCH/served-id-mismatch) | This is the capability itself; round-16 observed exactly these (`receipt.json:98-169`). A v2 receipt that passes only the new checks is not no-harm evidence. |
| R9 | Diagnostic preservation: the v2 receipt still carries every v1 evidence surface (transitions with bodies/status, `loading_503`, captures for all five surfaces, both probe records with argv/result, teardown fields, ownership), so the gate can re-derive rather than trust `passed` | Gate re-derivation requires the stored evidence (`check-receipt.py:462-480`, `:530-598`, `:745-769`); dropping a field silently weakens the gate. |
| R10 | v1 backward compatibility: the **current** gate on both round-16 receipts still exits 0, and the frozen receipt still exits 1 under the current probe pin (the round-16 expected triple) | `live/controls.txt:17-20` records `gate_receipt_exit=0`, `gate_frozen_exit=0`, `gate_frozen_with_current_probe_pin_exit=1 (expect 1)`. This is the cheapest proof that v2 did not retroactively invalidate round-16. |
| R11 | Safety-gate regression: digest mismatch → exit 3; 34113 → exit 2 token `port-refused-registered:34113`; 8080 → exit 2; in-use port → exit 2; unreadable registry → exit 2 | Required by the C2LiveTool clause "Keep every safety property (loopback, registered-port refusal, digest gate before launch, killpg only on a live child, child env allowlist)" (`spec.json:24`). K0-K7 do not exercise any of these (see F4). |
| R12 | Environment: `pgrep -x llama-server` empty before and after; `ss -ltnp` shows no listener on the receipt port after teardown and nothing on 8080/34113; no `/tmp/kama-llamacpp-live-*.log`; no fake server left; model digest unchanged | Teardown deletes the log; the port-closed probe is the only post-teardown port evidence (`kama-llamacpp-live.py:685-700`). Operability no-harm, not just check output. |
| R13 | Repeat: at least one second run, or the five-run `ProbeSigtermExit` experiment, to show rc-0 teardown and the ~11 ms loading capture are stable; record both receipts, no retry-until-green | Round-16's own receipt has `term_wait_ms 3` and `loading_observed true`; a one-shot sample cannot tell a predicate from luck. |
| R14 | Process/provenance: the real receipt is a new round-17 artifact (do not overwrite round-16); a **new** own-work SOURCES row supersedes S041 (v1, "10 checks", `corpus/SOURCES.md:53`), not an in-place edit of S041's anchor/teaches cells | Contract rule 2 allows only status/recheck/used-by in place; round-16's spotcheck already recorded S041 edit-in-place as routed defect 3 (`corpus/lessons/round-16-verifier-spotcheck.md:184`). |

If R6's `loading_observed` is false on the real run, R1-R5 and R7-R14 can still be green, but the loading repair is then supported only by the fake K2 control; the report must say so. The tool contract explicitly allows the check to pass vacuously (`loading_observed false`), but the working-tree gate rejects that receipt (F13), so a green v2 receipt currently implies the real envelope was observed and graded; that is stronger than the contract and must be reconciled before the real run.

# What makes a fake-server control credible evidence for a real-server property

A control is an oracle for the **detector**, not for the server. It establishes the conditional "if an endpoint behaves as B at the observed interface, the tool+gate reject". The real-server property P ("the harness fails when llama.cpp does X, and still passes when it behaves") is the conjunction:

1. B is realizable/exhibitable by the real server (source anchor, or at least a real failure mode);
2. the detector rejects B (fake control);
3. the detector accepts the real server's good behaviour (real run).

The fake supplies (2) only. A control suite alone cannot establish no-harm; the real run alone cannot establish fail-capability. That is why the design needs both, and why the claim must not derive the real-server property from the fake.

Credibility conditions for the fake controls:

C1. **K0 is the observationally-equivalent good server.** Its statuses/bodies must be the b11755 contract, not invented: `/health` 200 `{"status":"ok"}` (`server-context.cpp:5297`; compare JSON, not bytes), loading 503 `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` (`server-http.cpp:307-328`), `/v1/models` with `data[].id` = alias and `owned_by "llamacpp"`, `/props.model_alias`, `/metrics` 501, SIGTERM → rc 0 (`server.cpp:519-523,534,590`), and the child owning the listener. If K0 differs from the real wire shape, its acceptance predicts nothing about the real run. The round-16 real receipt is the best fixture oracle for these bodies (`receipt.json:22`, `:201`, `:473`). [INFERENCE] Using minimal but same-shaped bodies is acceptable for the tool's parsed checks, but the differences must be stated.

C2. **One variable per negative.** Each of K1-K5 must change exactly one observable from K0, and the receipt must show the change happened: K1 health body `{"status":"degraded"}` (status stays 200); K2 a `Busy` 503 body then ready (`loading_envelope_exact false`); K3 teardown `sigterm_sent false` + `returncode 0`; K4 `sigkill_sent true`/`returncode -9`; K5 `returncode 1`. Without the observed change, a rejection is not attributable.

C3. **Attribution, not exit code.** A control "rejected" because the tool exited 1 for an unrelated check (e.g. a fake `/props` mismatch) is a false credit. Require the receipt's `failed_checks` to contain the targeted id and all other checks to equal K0's passing set; for K6 require `setup_error` `internal:<ExcType>` and a written receipt; for K7 `setup_error ready-timeout`. The spec's rule "tool exit != 0 or gate exit != 0" is too weak (`spec.json:34`).

C4. **Same apparatus both arms.** The same fake source digest, the same probe digest, and the same `controls.py` digest must be used for before and after; the registry input must be the same bytes. Otherwise the accepted-bad delta confounds tool/gate changes with fixture changes. The spec's JSON records only `tool_sha256`/`gate_sha256` (`spec.json:34`).

C5. **Through the real tool, through its safety gates.** The control invokes the measured tool file (staged if needed, see F1), not an in-process shortcut, except K6, which is explicitly a harness-fault control. The tool's model-digest gate, port selection, and `--host 127.0.0.1` argv must be the real ones.

C6. **Cleanup and port safety.** Every fake is killed by process group (K6 especially, because the tool's teardown never ran), every kernel-chosen port is confirmed closed, and no registered port is ever bound.

C7. **Timing controls need repetition and classification.** K3 is not a stable single-shot control (F2): a run that ends in the tool's setup-error path is not a detection by the new predicate; it is a window miss and must be reported as inconclusive, not counted.

Residual limits (must be in the report):
- The fake is not llama.cpp. It cannot show the real server emits B; only the source anchor plus the real run can.
- K1's degraded body and K2's `Busy` body are not b11755 states. They test *sensitivity of the predicate to a deviating body*, not a real llama.cpp failure mode. K4/K5 are plausible failure modes; K3 is a harness-integrity scenario.
- K1/K2/K7 are not subject-behaviour controls in the same sense as K3-K5; grouping them in one "accepted_bad" number conflates predicate sensitivity, harness fault handling, and timeout handling.

# Findings

## F1 [high] — the frozen arm is not runnable from the frozen path: script-relative registry

`kama-llamacpp-live.py` resolves its lane/registry from its own location: `SCRIPT = Path(__file__).resolve()` (`frozen tool:51`), `LANE = SCRIPT.parent.parent` (`:52`), `REGISTRY = LANE / 'registry' / 'endpoint-consumers.tsv'` (`:53`). For the frozen copy at `.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py`, that is `.ufo/waves/round-17/registry/endpoint-consumers.tsv`, which does not exist (verified `test -e` → exit 1). `refused_ports()` then raises `SetupError(f'registry-unreadable:{REGISTRY}')` (`:200`) and the tool exits 2 before launch, for every control. Because `resolve()` follows symlinks, staging a symlink does not help.

Consequence: `controls.py --tool .ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py` would report `good_ok false` and every bad control rejected for the wrong reason; the "before" count would be 0 (or meaningless), and the before→after delta would be an artifact.

Fix (specify in the C2Controls item or its own runbook): stage byte copies of the frozen tool as `<tmp>/tools/kama-llamacpp-live.py` (sha256 must equal the frozen manifest b8c5e8d4…fe4) with `<tmp>/registry/endpoint-consumers.tsv` copied byte-identically (sha256 `bf343625188d9f486a6f6d13c60c946e23c21d05ee1bef881204dfa14c62bc6c`), and record both digests. Do the same for the current arm so both arms run from the same layout. This is also the only way the frozen tool's `port_refusal_set` includes 8080/34113 as the round-16 receipt shows.

## F2 [high] — K3's baseline acceptance is a race, and `teardown_graceful` cannot prove causation

The v1 self-exit evidence in the round-16 advice is check-level, not end-to-end: in `se` the server exited rc 0 after `/health`; the tool exited 2 with `setup_error pre-captures:child-exited-rc0`, and `teardown_exited` still passed (`ReviewLiveHarnessCode.md:28`, `:52`: "se: self-exit rc 0 passed with `sigterm_sent false`"). For K3 to be **accepted-bad** (tool exit 0 + gate exit 0) at baseline, the fake must self-exit in the window after the post-probe liveness gate (`frozen tool:976`) and before teardown (`:656`) — a few Python statements, sub-millisecond. A timer-based fake cannot reliably hit it.

Worse, the v2 predicate cannot prove the signal caused the exit. The liveness evidence is `if proc.returncode is None:` (`frozen tool:663`; the 12:31 v2 tool still has the same test at `tools/kama-llamacpp-live.py:672`), but Python docs: "Initially None, returncode is set by a call to the poll(), wait(), or communicate() methods" (https://docs.python.org/3/library/subprocess.html#subprocess.Popen.returncode). A child that exited but was not reaped still has `returncode None`, so `sigterm_sent` can be recorded true for a dead child; and a fake that ignores SIGTERM and exits 0 by itself 20 ms later produces `sigterm_sent true`, `sigkill_sent false`, `returncode 0`, `alive_at_teardown_start true` — i.e. **teardown_graceful passes** (a deterministic false negative). [INFERENCE: the kernel delivers the discarded SIGTERM to the zombie/ignoring process and `wait` then returns the self-exit code.]

Required design change: (a) `alive_at_teardown_start` must be `proc.poll() is None` plus an OS-level state check (`/proc/<pid>/stat` not `Z`), not `returncode is None`; record the `killpg` outcome/errno; (b) K3 must count as exercised only when the receipt shows `sigterm_sent false` and `returncode 0`, must be repeated, and a run that lands in the setup-error path is INCONCLUSIVE; (c) either add a K3b control ("ignores SIGTERM, then exits 0 on its own") and document that v2 still accepts it, or add causal evidence (the documented `clean_up` shutdown log line from `server.cpp:483-490`, `SRV_INF("%s: cleaning up before exit...\n")` at `:484`, is one option, with the caveat that it is an implementation string and subject-controlled). The claim's "harness-initiated SIGTERM" wording is not currently graded.

## F3 [high] — a green real run without identity pins is not a b11755 run

The gate accepts any build unless `--expect-server-sha256` is passed (`check-receipt.py:1105-1113`); `CriticC2Admission.md:46-55` demonstrated "no pins → exit 0 VALID" for a mutated receipt with a different server digest and `b9999` build_info. The round-16 real receipt's server block does carry the right values (`receipt.json:399` sha `b6a31a8e…`, `:397` realpath `…/llama-b11755/llama-server`), but the gate never grades `build_info` and the SKILL entry command passes only the model pin. For C2's "real b11755 run", the gate invocation must pin server + model + probe + tool, and the record must show the pins. Otherwise the real run's no-harm claim is build-agnostic.

Also pass `--server /home/vgpnk/.local/opt/llama-b11755/llama-server` explicitly; the tool defaults to `shutil.which('llama-server')` and PATH resolves to the `~/.local/bin` link (`CriticNoHarm.md` F2). `readlink -f` confirms the link currently points at b11755, but the explicit path removes the PATH variable from the evidence.

## F4 [high] — the control suite does not cover the safety properties the tool edit can break

K0-K7 use a fake server, a correct model digest and a kernel-chosen port. None of them asks for 8080/34113, a wrong digest, an in-use port, or an unreadable registry. A v2 edit that drops registry parsing, drops a hard pin, or reorders the digest gate before launch still yields `accepted_bad 0` and `good_ok true` — the exact blind spot round-16's `MutateLiveRefusal.md` found: `DropRegistryParsing` "SURVIVED" and `FailOpenRegistry` "SURVIVED" the recorded digest+hard-pin controls (that advice's "Which existing controls discriminate these mutants?" table). The C2LiveTool clause "Keep every safety property (loopback, registered-port refusal, digest gate before launch, killpg only on a live child, child env allowlist)" (`spec.json:24`) therefore has no measured evidence under the current design.

Fix: add a safety group to `controls.py` (digest mismatch → 3; 34113 → 2 with the exact token; 8080 → 2; in-use → 2; unreadable registry → 2 with `registry-unreadable:`), or have L1 re-run the round-16 command set (`live/controls.txt:8-14`) against the current tool and record exits+tokens in the after evidence. Assert the stderr token, not only exit 2, because `port-in-use`, `registry-unreadable` and registered-port refusal all exit 2 (`MutateLiveRefusal.md`, "An exit-only check can confuse…"). This group is the operability no-harm measurement.

## F5 [high] — exit-code-only rejection does not attribute the failure to the repaired check

The spec's rule is "K1-K7 must be REJECTED: tool exit != 0 or gate exit != 0" (`spec.json:34`). For K1 a run whose fake `/props` is wrong (or whose probe stub misbehaves) exits 1 for `props_alias`, not `health_ready`, and still counts. The after count can therefore be 0 without any strengthened predicate firing. The JSON records `failed_checks` (`spec.json:34`) but the pass rule does not use it.

Require an expectation table in the control definition and the JSON: K1 → `health_ready`; K2 → `loading_envelope_graded`; K3/K4/K5 → `teardown_graceful`; K6 → `setup_error` `internal:<ExcType>` + receipt written; K7 → `setup_error ready-timeout`. Require all other checks to match K0's passing set, and record the gate's problem text (or the receipt's observed fields) so the reason is auditable. Also separate subject-behaviour controls (K1-K5), harness-integrity (K6), and timeout (K7) in the count and in the claim.

## F6 [medium] — the probe and fake are unpinned inputs; before/after can be confounded

All controls run `--probe PROBE` (`spec.json:34`), and the tool's `probe_model_ok`/`probe_mismatch` checks read only the probe's exit/verdict/reason (`frozen tool:984-997`). The probe is a real variable: round-16 has two receipts with different probe digests (`receipt.json` probe `36b6497…`; `receipt-frozen-probe.json` probe `93ee4302…`). The spec's JSON records `tool_sha256` and `gate_sha256` only. Pin the frozen probe (`36b6497…29d3`) for both arms, and record `probe_sha256`, `fake_sha256`, `controls_sha256` (self-hash), and `registry_sha256` in the before and after JSON. If the probe changes this round for C1, the before arm must still use the frozen bytes or the count is not a tool/gate delta.

## F7 [medium] — the loading repair can be green but vacuous; S041 and the knowledge entry are v1

`loading_envelope_graded` passes with `{"loading_observed": false}` by design (`spec.json:24`), and the round-16 real receipt happens to observe it (`receipt.json:212-213`, both true). A v2 real run that reports false can still be "all checks pass"; the no-harm statement must record `loading_observed` and must not cite the loading check as evidence in that case. Separately, S041 (`corpus/SOURCES.md:53`) is a v1/10-check row and the knowledge entry's `verified-at` cites the v1 tool sha (`corpus/knowledge/llamacpp-loading-lifecycle.md:2`). The v2 real run needs a new own-work row (dated receipt, v2, 11 checks) that supersedes S041; editing S041's anchor/teaches is the round-16 routed defect (`corpus/lessons/round-16-verifier-spotcheck.md:184`: "S041's anchor and teaches cells were amended after the row's first commit"). The gate's `documented_by` is not validated (any non-empty string passes, `RerunReceiptGate.md:66` S16), so the citation review is manual: the DOC must carry URL+line for `server-context.cpp:5297`, `server.cpp:519-523/534/590`, and the Python docs.

## F8 [medium] — fake-server credibility conditions and their limits

Covered in the section above; the essential points for the record: K0 must be built from the real receipt/source shapes, each negative must vary one field, the receipt must show the variation, the same fake/probe bytes must be used on both arms, and the suite must state that K1/K2 bodies are not real b11755 states. The round-16 receipt gives the exact good bodies: health `{"status":"ok"}` (`receipt.json:22`), loading 503 envelope (`receipt.json:201`), and the models/props/metrics surfaces from `:95-169`. The sources confirm the expected values: `server-context.cpp:5297` (`res->ok({{"status", "ok"}});`), `server-http.cpp:307-328` (`"Loading model"`), `server.cpp:519-523/534/590` (shutdown → `return 0;`). The pinned local copies have sha256 `dd1de0f2…2329`, `24ede172…5fdb`, `2143962…aef4`.

## F9 [medium] — real-run cleanliness and the bind/release race

The tool binds `:0`, releases, and lets the child rebind; the receipt records the race note (`kama-llamacpp-live.py` `port_pick_note`). A stranger that wins the port makes the run exit 2 (`port-listener-not-our-child`/`unproven`); `CriticC2Admission.md` D1 shows a stranger can receive the readiness GETs. The real run must show `port_listener_ownership: child` and `port_refuses: true`, and if it exits on the race that run is not no-harm evidence. Record `pgrep -x llama-server` before/after, `ss -ltnp` on the receipt port and on 8080/34113, and the absence of `/tmp/kama-llamacpp-live-*.log`.

## F10 [low/medium] — pre-register the before set; do not infer it after the fact

From the frozen code, the expected before outcomes are [INFERENCE]: K0 accepted; K1 accepted-bad (`health_ready` status-only, `:938`); K2 accepted-bad (`loading_envelope_exact` computed at `:922`, no check consumes it); K3 accepted-bad only if the sub-ms window is hit (F2); K4 accepted-bad (`teardown_exited` accepts `-9`, `:1024-1027`); K5 accepted-bad (same, `rc 1`); K6 escaped/accepted-bad (KeyError on the error dict, `:1020-1027`); K7 rejected (exit 2, `:504`/`:517`). Pre-register this set; any deviation is a control bug or a discovery to explain, not a new count. Timing: K4 must exceed the 10 s `TERM_GRACE` (`:63`); K7 needs `--ready-timeout 2` (`:739` default 60).

## F11 [low] — K6 leaks the fake unless the control reaps it; the v2 fault path should kill

When `teardown()` is monkeypatched to raise, the tool has not killed the child (the kill is inside `teardown`, `:656-700`). The frozen tool then KeyErrors on `receipt['teardown']['returncode']` (`:1020-1027`) and writes no receipt; the fake survives. The control must reap the fake by process group in `finally` and prove the port closed, or the next control inherits a listener. For v2, the internal-fault path should attempt a bounded kill fallback and record the child pid/alive state; "receipt written, exit 2" alone leaves an orphan if a real teardown bug occurs, which is an operability no-harm risk on the real run (R12).

## F12 [low] — SOURCES rows for the new predicates are not present yet

The C2 claim requires the health and teardown predicates to cite new SOURCES rows opened this round. `corpus/SOURCES.md` still ends at S041 (no S042+ on grep), while the pinned copies and `pins.json` already exist under `.ufo/waves/round-17/sources/llama.cpp-704366d76/`. Before admission, the new rows must carry the commit-pinned URLs + exact lines: `/health` ready body (`server-context.cpp:5297`), SIGTERM→`ctx_server.terminate()`→`return 0` (`server.cpp:519-523`, `:534`, `:590`), and the Python `Popen.returncode` anchor (negative = signal death). The tool's DOC strings alone are not the source row; the gate does not validate them.

## F13 [high, working-tree gate] — the v2 gate rejects the vacuous loading pass that the tool contract allows, and K0 as specified trips it

`tests/llamacpp-live/check-receipt.py:913-915` (working-tree v2) reports `loading_envelope_graded: no loading_503 body stored, nothing graded` when `want_lef is None`. The C2LiveTool contract says the opposite: "if none observed, pass with observed `{"loading_observed": false}`" (`spec.json:24`). Consequence 1: the after-arm K0 good control, whose shape in the C2Controls spec has no 503 phase ("/health 200 {"status":"ok"}", `/v1/models`, `/props`, `/metrics 501`, "exit 0 on SIGTERM", `spec.json:34`), produces `loading_observed false`; the tool's check passes, the gate exits 1, `good_ok` is false, and the counting command exits 1 even with `accepted_bad 0`. Consequence 2: a real b11755 run that misses the ~11 ms loading window is INVALID at the gate although the tool grades it green — the no-harm gate becomes hostage to the window. The window is fragile: at review time `CriticC2Admission.md` D4 records both then-current receipts with `loading_observed false`; only the regenerated 14:06 receipts captured a 503 (at `t_ms 11`, `receipt.json:212-213`). Fix: the v2 gate must accept `want_lef is None` only when `loading_observed is false` and the check's observed equals the contract's `{"loading_observed": false}`; it must still reject a check that claims `passed` true with an observed value that does not match. Add a separate K0b good control that emits a short exact 503 phase, so the non-vacuous loading path is exercised without contorting K0. Re-check this against the final committed gate (the working-tree file is an intermediate, sha256 `f6467f5a…5955`).

On the positive side, the working-tree gate already implements the v2 re-derivations the design needs: health body equality (`check-receipt.py:686-697`), the four teardown fields (`:847-881`), port ownership (`:889-902`), and a 12-case v2 mutation selftest (`:1255-1297`) including the two K3 shapes (`sigterm_sent false` with rc 0, and `alive_at_teardown_start false`). The remaining tool-side risk is the *truthfulness* of `alive_at_teardown_start` (F2), which the gate cannot re-derive.

## F14 [low, working-tree tool] — the v2 header lost the exit-3 line and carries a malformed comment

At the 12:31 snapshot, `tools/kama-llamacpp-live.py:21` jumps from the exit-2 description to "Receipt schema:", dropping the "3 model digest mismatch (refuses to launch)" line, while the code still returns 3 (`:806` `model digest mismatch`). Line 62 is `# a 200 with {"status":"degraded"} is not ready).` — an unmatched parenthesis and no opening sentence. Both are transient if the seat is still editing, but the final file must restore the exit-3 line (the safety-gate regression in F4 asserts exit 3) and remove the stray comment.

# Recommended measurement record (minimal, audit-ready)

- `.ufo/waves/round-17/c2/controls-before.json` and `controls-after.json` from one pinned `controls.py` (self-sha), with per-control: expected check id, tool exit, gate exit, receipt sha256, `failed_checks`, the observed field that proves the stimulus (health body / loading body / sigterm / sigkill / returncode / setup_error), and `outcome ∈ {detected, accepted_bad, inconclusive}`.
- `.ufo/waves/round-17/c2/live/receipt.json` (v2, new artifact), `gate.txt` (pins + exit + problem text), `digests.txt` (tool/gate/probe/server/model/fake/registry), `negatives.txt` (R11 exits+tokens), `cleanup.txt` (pgrep/ss/log/model digest).
- A `before` set with the frozen pair staged as in F1, and an `after` set with the current pair; both with the same fake and probe digests. Report the raw sets, not only the totals; the round-16 `live/controls.txt` is the precedent.

# Limitations

- Read-only, static review: I did not run `controls.py`, the tool, the gate, or any control; the before/after counts above are [INFERENCE] from code reading and round-16 advice/evidence. I did not start llama-server or bind a port.
- The C2 implementation files (`tools/kama-llamacpp-live.py` v2, `tests/llamacpp-live/check-receipt.py` v2, `tests/llamacpp-live/controls.py`) were not present at review start and were mid-edit at review end; findings about them describe the contract, the frozen baseline, and the 12:31 snapshots, not final committed code.
- The K3/killpg/zombie reasoning is a static/POSIX inference; the exact kernel behaviour of a discarded SIGTERM to a zombie was not measured here.
- Upstream lines were read from the pinned copies and the raw commit URLs; the pinned copies' digests match `pins.json`.
- No resume/saturation/rerouting path applies to C2.

# Installs

None.
