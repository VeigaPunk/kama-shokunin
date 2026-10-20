VERDICT: confirm — `tools/kama-llamacpp-live.py` now emits `kama-llamacpp-live/v2` with fail-capable health, harness-initiated graceful teardown, ownership-gated port closure, all-bodies loading-envelope grading and always-written internal-fault receipts; every round-16 accepted-bad control now fails, v1 receipts still VALID.

# Scope

Owned file, rewritten in place (no other lane file touched):

- `tools/kama-llamacpp-live.py` — sha256
  `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac`
  (1423 lines; was `b8c5e8d4…` / 1078 lines)
- this report: `.ufo/waves/round-17/build/advice/C2LiveTool.md`

Fake server, stub probe, knob files and drivers lived under
`/tmp/KamaR17-C2LiveTool-2/` and were removed before finishing. No installs.

# Check set (11 ids, order emitted)

| id | predicate | evidence recorded |
|---|---|---|
| `health_ready` | status 200 **and** parsed body == `{"status":"ok"}` (object equality) | `{status, body, expected_body}` |
| `models_alias_id` | unchanged | `{data_ids, expected_alias}` |
| `models_owned_by_llamacpp` | unchanged | `{owned_by}` |
| `metrics_not_enabled` | unchanged (501) | `{status}` |
| `props_alias` | unchanged | `{fields}` |
| `probe_model_ok` | unchanged | `{exit, verdict, reason}` |
| `probe_mismatch` | unchanged | `{exit, verdict, reason}` |
| `teardown_graceful` | `alive_at_teardown_start is True` **and** `sigterm_sent is True` (killpg delivered) **and** `sigkill_sent is False` **and** `returncode == 0` **and** `port_listener_ownership == "child"` | all five plus `error` |
| `teardown_port_closed` | `port_refuses is True` **and** `port_listener_ownership == "child"` (vacuous → fail) | `{port_refuses, port_listener_ownership}` |
| `loading_envelope_graded` | `loading_observed is True` **and** every distinct captured 503 body is the exact envelope; no 503 observed → fail | `{loading_observed, distinct_bodies, bodies_dropped, total_503_responses, all_exact, exact}` |
| `model_unchanged` | unchanged value; DOC relabelled **input integrity** | `{pre, post}` |

`health_ready` body parse (`tools/kama-llamacpp-live.py:1176-1185`):
`health_status == 200 and health_body == HEALTH_READY_BODY`.
`HEALTH_READY_BODY = {'status': 'ok'}` at line 64.

Teardown predicates: `teardown()` at line 771 records
`alive_at_teardown_start` from a fresh `proc.poll()` (`_child_running`,
line 749) immediately before `killpg`; `sigterm_sent` is set only after
`os.killpg(…)` returns (line 783-786); the SIGKILL escalation re-checks
liveness first (line 791). `returncode == 0` is the gate; a negative value
(signal death) fails.

`loading_envelope_graded` grades `loading_503_bodies`, the deduped-by-sha256
list of every distinct 503 body (`_BodyLog`, line 239; capture at 540-568),
capped at `LOADING_BODY_MAX = 256` with `loading_bodies_dropped` recording
any overflow. This is L1's ruling: no observation is a failure, and all
bodies (not only the first) must be exact. `loading_503` (first body) and
`loading_envelope_exact` are kept unchanged for v1 compatibility.

# Sources (opened this round, pinned commit)

Commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (b11755). DOC anchors
(`DOC`, line 87 onward) now carry URL + line:

- `/health` ready body — `server-context.cpp:5288-5299`, quote at 5297:
  `res->ok({{"status", "ok"}});`. Raw:
  `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76…/tools/server/server-context.cpp`
  sha256 `dd1de0f2…c2329`. **No SOURCES row covers this file/proposition**;
  the emitted binding uses `row: null`.
- Loading 503 envelope — `server-http.cpp:314-325`, quote 314 `res.status = 503;`,
  318-320 `"Loading model"` / `"unavailable_error"` / `"code", 503`. File
  sha256 `24ede172e5…fdb` **equals SOURCES S036's recorded raw digest**;
  binding uses `row: "S036"`.
- SIGTERM → shutdown → exit status — `server.cpp:529-534` (`sigaction(SIGTERM,
  &sigint_action, NULL);` at 534), `519-523` (`ctx_server.terminate();` at 522),
  `575-590` (`return 0;` at 590). File sha256 `21439622…ef4` equals S037's
  recorded digest, **but S037's scope is start-up order (440-462, 493-515)**,
  not the signal path; those three bindings use `row: null` rather than
  mis-citing S037. A new code row is owed for the signal path.
- Python `subprocess.Popen.returncode` —
  `https://docs.python.org/3/library/subprocess.html#subprocess.Popen.returncode`,
  cited in `teardown_graceful` only for *"None until termination; negative
  means signalled"*. The `returncode == 0` proposition is grounded on the
  llama.cpp shutdown path plus the round-16 observed receipt, per the
  connector's row-grounding split. No file binding is emitted for the HTML
  page (no pinned bytes).

`source_bindings()` (line 866) emits one binding per span:
`{check, row, commit, path, url, lines:[a,b], file_sha256, span_text,
span_sha256}`. Every span was re-verified programmatically against freshly
downloaded raw files: `file=True span=True text=True` for all five spans.
This block is additive; the landed gate ignores it.

# Receipt v2 deltas

All v1 field names retained; `schema` now `kama-llamacpp-live/v2` (line 50).
Added: `loading_503_bodies`, `loading_bodies_dropped`, `internal_fault`,
`child_pid`, `port_listener_ownership` (always present, default `"unproven"`),
`source_binding`; `teardown.alive_at_teardown_start` added to the teardown
record. `teardown_exited` is gone; `teardown_graceful` replaces it.

# Controls run (fake server /tmp, all on unregistered ephemeral ports)

Each row: harness exit, failing checks, gate verdict.

| control | exit | failing checks | gate |
|---|---|---|---|
| good (40×503 then ready, SIGTERM→0) | 0 | none (11/11) | VALID |
| `health 200 {"status":"degraded"}` | 1 | `health_ready` | INVALID |
| loading body `message:"Busy"` | 1 | `loading_envelope_graded` | INVALID |
| server ignores SIGTERM (needs SIGKILL) | 1 | `teardown_graceful` (`returncode -9`, `sigkill_sent true`) | INVALID |
| no 503 observed (ready at once) | 1 | `loading_envelope_graded` (`loading_observed false`) | INVALID |
| both health+loading wrong | 1 | `health_ready`, `loading_envelope_graded` | INVALID |
| child self-exits rc 0 before ready | 2 | `teardown_graceful`, `teardown_port_closed`, `loading_envelope_graded`; `setup_error server-exited-early-rc0`, ownership `unproven` | INVALID |
| `teardown()` monkeypatched to raise | 2 | `teardown_graceful`, output also `teardown_port_closed`; `setup_error internal:RuntimeError`, receipt written, child SIGKILLed by backstop (`returncode -9`), `port_refuses true`, handlers restored | INVALID (expected) |

Round-16 accepted-bads now fail: degraded health (was 10/10), non-exact
loading body (was 10/10), self-exit `sigterm_sent false` (was
`teardown_exited` pass), SIGKILL `-9` (was pass), vacuous port-closed
(now requires ownership `child`), and the `KeyError('returncode')` escape
(now a receipt + exit 2).

Real `llama-server` development run (one run, allowed): b11755 on port
41963, 21 loading 503s, `/health` body exactly `{"status":"ok"}`,
teardown `returncode 0 / sigterm_sent true / sigkill_sent false /
term_wait_ms 3`, 11/11, exit 0, and the landed gate reports `VALID` for
that receipt. No
`llama-server` remained; `ss -ltnp` shows no 8080/34113 listener.

Gate compatibility: `tests/llamacpp-live/check-receipt.py` (concurrently
edited by the gate seat) reports `VALID` for the final good receipt and
`VALID` for the frozen v1 `.ufo/waves/round-16/live/receipt.json` (v1 path
unchanged). `teardown_graceful`, `teardown_port_closed` and
`loading_envelope_graded` re-derivations at `check-receipt.py:847-923`
agree with the producer.

# Internal faults

The `finally` (line 1256 onward) is fully `Exception`-guarded: teardown,
the killpg backstop, port re-probe, check assembly and the exit-code
computation each have their own handler; any fault sets
`receipt['internal_fault'] = "internal:<ExcType>"`, sets `setup_error`
when vacant, and forces exit 2. A last-chance `killpg(SIGKILL)` reaps a
group left running by a faulted teardown (`_child_running` gate, so a dead
child's pgid is never signalled). Handlers are restored in the emit
`finally`; the fault driver confirmed `handlers restored True` in-process
and a receipt on disk.

# Safety properties preserved

Loopback-only launch (`--host 127.0.0.1`), registered-port refusal
(`HARD_REFUSED_PORTS` + registry TSV, unchanged `pick_port`), digest gate
before launch (exit 3), killpg only on a freshly polled live child,
allowlisted child env (names only). Tightened: `_listen_inodes` now counts
only loopback-bound listeners (`127/8`, `::1`, v4-mapped 127/8), so a
child bound to `0.0.0.0` is not accepted as the loopback owner
(fail-closed).

# Limitations and residual risks

1. The landed gate re-derives the loading envelope from `loading_503`
   only (`check-receipt.py:908-923`); it cannot independently confirm the
   *other* distinct bodies. The producer now records them in
   `loading_503_bodies`; the gate seat should re-derive over that array.
   `observed.exact` is emitted as an alias for the all-bodies value so the
   gate's optional-key check sees the stronger grade.
2. `_BodyLog` dedupes by sha256: identical repeats are graded once
   (`repeats` and `total_503_responses` record the count); >256 distinct
   bodies are dropped and counted, not hidden.
3. `loading_503` remains the first body for v1-shaped consumers; the
   graded check uses the full list.
4. A `BaseException` (MemoryError, or a signal not blocked) can still
   escape the finally; `Exception` paths cannot.
5. `health_ready` is a near-duplicate of the readiness precondition; its
   remaining window is a body change between readiness and capture. It is
   now falsifiable (degraded body control).
6. `teardown_port_closed` requires ownership `"child"` at the end of the
   run; a child that self-exits after proving ownership makes the check
   fail (deliberate: the run no longer has a harness-initiated teardown).
7. The fake server is not llama.cpp; the real run is one sample, not the
   measured run (L1 owns that).

# Installs

None. pacman untouched (host-wide pause respected).

# Peers consulted

SentinelLiveSafety-2's (a)-(f) folded in: outer handler restore (via the
guarded finally + emit finally; residual BaseException limit noted),
last-chance killpg, log unlink in its own finally, `internal:<ExcType>`
without `str(exc)` in `setup_error`, loopback-only listener accounting,
`child_pid` recorded. ConnectKaidoku-2's row-grounding split applied
(Popen row grounds API value only).
