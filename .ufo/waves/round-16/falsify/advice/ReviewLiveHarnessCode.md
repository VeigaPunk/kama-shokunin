VERDICT: partial — the 10 checks in `tools/kama-llamacpp-live.py`: six are falsifiable by subject behavior, two cannot fail for any userspace process behavior, two more are effectively unfalsifiable in a completed run, and no check at all grades the loading envelope the harness now captures.

Reviewed revision: `tools/kama-llamacpp-live.py` sha256
`b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4`
(1078 lines), gate `tests/llamacpp-live/check-receipt.py` sha256
`6b9576a13dde1872977a6af4547599a75cf484f37fe6fe0f4f5557349b09ced6`.
The harness changed twice under me during this review (lane HEAD `b8e485c`
was 989 lines / sha `cf95f382…`; a build-wave revision was sha `53256610…`).
Every finding below was re-run against `b8c5e8d` and the current gate. The
live receipts were regenerated at 14:06:27Z and now record
`loading_observed: true`, `loading_envelope_exact: true` on `/v1/models` 503.

# What I ran

No llama-server was started. I used a fake HTTP server (`/tmp/…/fake_server.py`,
never llama-server) on harness-chosen ephemeral loopback ports, with stub probes
for the harness's probe-contract checks. All runs: `python3
tools/kama-llamacpp-live.py --server <fake> --model <tmp 32-byte file>
--model-sha256 <digest> --alias fakealias --probe <stub> --out <receipt>`.

| run | server shape | harness exit | result |
|---|---|---|---|
| good | documented surfaces | 0 | 10/10; gate VALID |
| b | wrong id, wrong `owned_by`, `/props` wrong alias, `/metrics` 200, `/health` body `{"status":"degraded"}` | 1 | failed: `models_alias_id`, `models_owned_by_llamacpp`, `metrics_not_enabled`, `props_alias`; `health_ready` passed |
| l | four 503s then ready | 0 | `loading_observed true`, `envelope true`; 10/10 |
| bl | four 503s, body `{"error":{"message":"Busy","type":"unavailable_error","code":"503"}}` | 0 | `loading_observed true`, `loading_envelope_exact false`; 10/10; gate VALID |
| hb | only `/health` body `{"status":"degraded"}` (status 200) | 0 | 10/10; `health_ready.observed {"status":200}`; gate VALID |
| se | server exits rc 0 by itself after `/health` | 2 | `setup_error pre-captures:child-exited-rc0`; `teardown_exited` **passed**, `returncode 0`, `sigterm_sent false` |
| lm | good server, stub probe that always says MODEL_OK | 1 | only `probe_mismatch` failed |
| rp | wrong-id server, probe that actually reads `/v1/models` | 1 | `models_alias_id` and `probe_model_ok` failed; `probe_mismatch` passed |
| to | `/health` always 500, `--ready-timeout 1` | 2 | `setup_error ready-timeout`; `port_listener_ownership "child"` (models phase proved it); teardown checks passed |
| hang | listens but never answers | 2 | `setup_error ready-timeout`; `port_listener_ownership "unproven"`; teardown checks passed |
| kill | fake server ignores SIGTERM | 0 | `returncode -9`, `sigkill_sent true`, 10.1 s; `teardown_exited` passed |
| fault | `teardown()` monkeypatched to raise `RuntimeError` | (driver) | `ESCAPED KeyError KeyError('returncode')`, `receipt_written False` |

Gate runs: `python3 tests/llamacpp-live/check-receipt.py <receipt>` → VALID
(exit 0) for good, l, bl, hb; INVALID (exit 1, 8 problems) for b. Scratch lived
under `/tmp/kama-r16-ReviewLiveHarnessCode/` and was removed after this report;
command lines and exits above are the record.

# Per-check verdict

| # | check (line) | what it reads | falsifiable? | evidence |
|---|---|---|---|---|
| 1 | `health_ready` (938) | fresh `/health` status | **no, in a completed run**; body ignored | hb: 200 + `{"status":"degraded"}` passed; readiness loop already required `/health` 200 + ownership ms earlier |
| 2 | `models_alias_id` (946) | parsed `data[].id` | yes | b: `wrong-id` → false |
| 3 | `models_owned_by_llamacpp` (950) | parsed `data[].owned_by` | yes | b: `someone-else` → false |
| 4 | `metrics_not_enabled` (955) | `/metrics` status | yes | b: 200 → false |
| 5 | `props_alias` (962) | parsed `/props.model_alias` | yes | b: `wrong-alias` → false |
| 6 | `probe_model_ok` (984) | probe exit/verdict/reason | yes, if the probe reads the server | rp: probe exit 2/MODEL_MISMATCH → false; but a non-reading MODEL_OK stub passes while the server serves `wrong-id` (b) |
| 7 | `probe_mismatch` (991) | probe exit/verdict/reason | yes | lm: always-OK probe → false |
| 8 | `teardown_exited` (1024) | `teardown.returncode is not None` | **no** for any userspace behavior | se: self-exit rc 0 passed with `sigterm_sent false`; kill: -9 passed; only survives-SIGKILL D-state yields None |
| 9 | `teardown_port_closed` (1029) | `port_refuses is True` | only via a surviving listener; **vacuous on failed runs** | se and to: passed though nothing was torn down; after `proc.wait()` a single-process server necessarily releases the port |
| 10 | `model_unchanged` (1037) | same-file sha256 pre/post | **no from subject behavior** | harness only reads the GGUF; [INFERENCE] llama-server opens it read-only; only external mutation can flip it |
| — | loading envelope | `loading_503` / `loading_envelope_exact` (921-922) | **no check consumes it** | bl: `envelope false` yet 10/10, exit 0, gate VALID |

Direct answer to “any check that cannot fail?”: **yes** — `teardown_exited`
(barring an unkillable D-state process) and `model_unchanged` (barring external
mutation) cannot fail for any behavior of the subject. `health_ready` can only
fail on a crash in the sub-millisecond gap after the readiness gate, and
`teardown_port_closed` is vacuous on failed runs and near-guaranteed after a
normal reaping (only a listener that outlives the process group can fail it).
Separately, the loading envelope has no check at all, so a wrong envelope is
invisible.

# Findings, by severity

## H1 — No check grades the loading envelope (high)
`loading_envelope_exact` is computed at `tools/kama-llamacpp-live.py:922` from
the first 503 body, but the 10 `_check(...)` calls at 938-1039 never read it.
The new two-phase `readiness_loop` exists to catch the ~5 ms window; the
field is then ignored. Demonstrated: `bl` returned exit 0, all 10 checks
`passed: true`, and `check-receipt.py` printed `VALID` for a body with
`message "Busy"` and string `code "503"`. The same gate accepts a receipt with
`loading_observed: false` (the old live receipts did), so C2 can be green
without ever observing the lifecycle state the capability is named for. The
harness's capture is correct — only the check set is blind.
Fix options: add an 11th check (needs the gate's `REQUIRED_CHECKS`/schema
change), or make `loading_envelope_exact is False` force exit 1, or have the
gate require `loading_envelope_exact is not False` when `loading_observed`.

## H2 — `teardown_exited` proves reaping, not teardown (high)
`tools/kama-llamacpp-live.py:1024-1028` asserts only
`receipt['teardown']['returncode'] is not None`. After `teardown()` calls
`proc.wait()` (or SIGKILL + wait, 656-683), any ordinary process yields a
returncode; the check can fail only if the process survives SIGKILL for 5 s
(uninterruptible sleep). Demonstrated `se`: the server exited by itself with
rc 0; `teardown_exited` passed, `sigterm_sent` was `false`, and nothing was
terminated. The `documented_by` string claims “the spawned process group must
terminate on SIGTERM/SIGKILL (returncode observed)” — no causation and no group
check. Fix: require `returncode in (0, -15, -9)` **and**
`(sigterm_sent or sigkill_sent)`, and/or scan the process group; otherwise
document it as “child reaped”.

## M1 — `health_ready` ignores its documented body (medium)
`tools/kama-llamacpp-live.py:938-939` compares status only; the cited DOC at
78-82 says 200 **`{"status":"ok"}`**. `hb` served 200 with
`{"status":"degraded"}`: `health_ready` passed, 10/10, exit 0, gate VALID. The
check is also a duplicate of the readiness precondition (the loop at 436-521
returns ready only after a `/health` 200 with proven ownership), so its only
new failure window is a crash between `verify_live` and the capture. Fix:
parse the body and require `status == "ok"`.

## M2 — `teardown_port_closed` is vacuous on failed runs (medium)
`tools/kama-llamacpp-live.py:1029-1032` passes whenever nothing listens on the
port. In `se` (child self-exited) and `to` (never ready), the check passed even
though no teardown occurred. On a completed run it is near-guaranteed after
`proc.wait()`; only a listener that outlives the process group can fail it.
Fix: gate it on `sigterm_sent or sigkill_sent` and on the port having been
owned; or fold it into a teardown proof that also checks no process remains.

## M3 — `model_unchanged` is a self-sentinel, not lifecycle evidence (medium)
`tools/kama-llamacpp-live.py:1037-1039` re-hashes the same file the harness
only reads. No behavior of the subject can flip it; only a third party mutating
the GGUF mid-run. Its DOC is honest (“the run mutated its input”), but it should
not be counted as a check of the server; the capability claim is unaffected.

## M4 — A teardown exception still destroys the receipt (medium, latent)
On a `teardown()` exception, line 1021 stores `{'error': ...}`; line 1026 then
indexes `['returncode']` → KeyError raised inside the `finally` block, which
the new F1 `except Exception` (try body only) does not catch. Fault injection
(`teardown` monkeypatched to raise) on `b8c5e8d`: `ESCAPED KeyError
KeyError('returncode')`, `receipt_written False`. The module documents exit 2
with a receipt for setup errors; this path loses the receipt entirely and
exits on a traceback. Fix: when `teardown` carries `error`, append a failed
`teardown_*` check with the error text and skip the keyed reads.

## L1 — Probe checks trust probe output (low)
`probe_model_ok` (984-990) and `probe_mismatch` (991-997) read only the
probe's exit/verdict/reason. `b` showed `probe_model_ok: passed` while the
server's own captured `/v1/models` served `wrong-id` (the stub did not read the
server). `rp` showed the check correctly failing once the probe actually read
the endpoint. This is by design (“kama-probe.sh classify() contract”), and the
gate validates `declared`/`expected_model_id`, but a cross-check of
`rows[0].served_model` against the captured `data[].id` would close it.

## L2 — Evidence sufficiency for `props_alias` and `metrics_not_enabled` (low)
`/props` and `/metrics` are captured with `keep_body=False` (lines 581, 611):
only the extracted `fields`/`status` are stored. The gate's “every claim is
re-derived from the stored evidence” for `props_alias` therefore compares the
producer's extracted object to itself; independent re-derivation is impossible.
Storing the props/metrics bodies (as health/models already are) would fix it.

## L3 — `port_listener_ownership` is `null` on the child-exit path (low)
The readiness map writes `child|foreign|unproven` (lines 916-918), and the
current gate understands all three (check-receipt.py:435-440). But every
`verify_live()` call also assigns its raw second return value (lines 927-928,
969-970, 976-977), and `verify_live` returns `None` when the child has already
exited (534-540). The `se` receipt therefore carries
`port_listener_ownership: null`, which the gate rejects as
`port_listener_ownership None not in child|foreign|unproven` (demonstrated).
`hang` demonstrates the `unproven` token on a ready timeout. Both receipts
already fail on `setup_error`, so this is cosmetic, but `verify_live` should
map its `None` to `unproven` for shape consistency.

# Residual risk and verification gaps
- The fake server is not llama.cpp; the six falsifiable checks were validated
  against synthetic surfaces, not against a misbehaving llama-server build.
- Probe checks were exercised with stubs, not `tools/kama-probe.sh` (that file
  and the 72-row matrix belong to the probe seat; I did not run `measure.py`).
- I did not bind or probe 8080/34113, and started no llama-server;
  `pgrep -x llama-server` was empty before and after, and no fake server
  remained after the runs.
- The harness was edited concurrently during this review; if it changes again,
  re-check H1/H2 and the M4 KeyError against the new revision. The live
  receipts at 14:06:27Z now include the loading capture and are newer than the
  `b8e485c` evidence quoted in the dispatch.
- `[INFERENCE]`: llama-server opens the GGUF read-only (M3); a grandchild in a
  different process group could hold the port past teardown (M2); the only
  `teardown_exited` failure mode left is D-state.

Installs: none.
