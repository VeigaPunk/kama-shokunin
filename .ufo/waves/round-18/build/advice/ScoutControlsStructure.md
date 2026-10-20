VERDICT: confirm — the frozen harness has exactly one fake-server generator, nine shape knobs and a two-class outcome model; both IPv6 loopback forms are unrecognisable to `_listen_inodes`, so a mapped-bound good server is rejected today.

Scope: read-only recon of `.ufo/waves/round-18/frozen/tests_llamacpp-live_controls.py` (700 lines, sha256 `aad8b1c758fe9616ecd7ad78538dbfd82227c7e99df3b051d2bf82d34d6e3a06`), with the frozen tool/gate read only where the controls' classification depends on them. No lane file was edited; no lane gate or measurement script was run.

## 1. How the fake server is generated

- One generated stdlib script per control. `tests_llamacpp-live_controls.py:96` — "FAKE_TEMPLATE = r'''#!/usr/bin/env python3"; it is a raw string with exactly two substitution tokens (`:94` — "Tokens %%SHAPE%% and %%PIDFILE%% are substituted per control").
- Substitution is literal `.replace`, not `%`-formatting: `tests_llamacpp-live_controls.py:340-344` — "return (FAKE_TEMPLATE / .replace('%%SHAPE%%', shape) / .replace('%%PIDFILE%%', str(pidfile)))". A new token only needs matching `%%NAME%%` spelling plus a `.replace` call.
- Staging: `tests_llamacpp-live_controls.py:374-404` `_stage_control` builds `<wd>/lane/tools/<tool>`, `<wd>/lane/registry/endpoint-consumers.tsv`, `<wd>/srv/fake_server.py` (the only file in `srv/`), `<wd>/model.gguf` (32 bytes, `:87` "MODEL_BYTES = bytes(range(32))"), chmod 0755 on the fake.
- The fake parses the tool's argv itself: `:110-118` `_val(flag, default)`; it reads `--port` (`:119`), `--alias` (`:121`) and deliberately discards the rest: `:122-123` — "-m/--host/-c/-t/--no-webui/--offline are accepted and ignored deliberately." **Consequence: bind address and behaviour cannot be steered from argv; they are baked into the generated file.**
- Pidfile: written after bind/listen (`:126-131`, `:247`, `:158`), so the tool's `install_tree` hash sees only `fake_server.py`. Cleanup verifies identity before signalling: `:346-370` — "Kill the fake's process GROUP"; `/proc/<pid>/cmdline` must name the staged fake, then `killpg(pid, SIGKILL)`.
- Serving: single-threaded `http.server.HTTPServer`, HTTP/1.1, `Server: llama.cpp` (`:178-184`); JSON `_send` at `:193-200`; fallback 404 at `:241-242`.
- Lifetime: `run_control` kills in `finally` (`:520-523`), `main` repeats the kill per control (`:667-669`); all state lives under one `TemporaryDirectory` (`:660-661`).

## 2. Existing shape knobs (the complete set)

Each row is a `SHAPE ==` test compiled into the generated fake; `k0` is the default arm.

| shape | site | behaviour |
|---|---|---|
| k4 | `:142-143` | "signal.signal(signal.SIGTERM, signal.SIG_IGN)" — needs SIGKILL escalation |
| k5 | `:144-145` | SIGTERM handler `_term_exit1` — dies rc 1 |
| k8 | `:146-147` | default disposition — killed by signal (rc -15) |
| k0/k1/k2/k3/k6 | `:148-149` | graceful `_term_exit0` |
| k7 | `:151-160` | raw `AF_INET` socket, `bind(('127.0.0.1', PORT))`, `listen(16)`, `signal.pause()` loop, never `accept()` |
| k2 | `:162-165`, `:174-175` | `BAD_ENVELOPE` — message "Busy", string code "503" |
| k0..k3,k6 | `:162-163` | `GOOD_ENVELOPE` — "Loading model", integer code 503 |
| k3 | `:219-224` | `os._exit(0)` after the second curl `/v1/models` is flushed |
| k1 | `:231` | `/health` 200 `{"status":"degraded"}` |

Data surfaces (module constants, one generated file per control so they cannot leak across runs):

- Loading window: `:166` — "LOADING = {'/v1/models': 3, '/health': 1}"; consumed in `_loading` (`:202-206`, "if hits < LOADING.get(path, 0)") against per-path counters (`:212-213`, `:227-228`).
- Ready model list: `:167-168` — "MODELS_OK = {'object': 'list', 'data': [{'id': ALIAS, ... 'owned_by': 'llamacpp'}]}".
- Props: `:169-171` — "PROPS = {'model_alias': ALIAS, 'total_slots': 1, ...}".
- Slots: `:235-236`; metrics: `:237-240` always 501 with message "metrics not enabled".
- Request-class discriminator: `:210` records the UA, `:216-217` counts curl `/v1/models`, `:222-223` gates k3 on curl. This is load-bearing: the tool's captures use `urllib` (proved UA `Python-urllib/3.14`), the probe shell uses curl (`tools/kama-probe.sh:294` and `:326` — "curl -sS --noproxy '*'"). So a knob can target *only* the tool's capture or *only* the probes by testing `'curl' in ua`.

Nothing else is parameterised: there is no shape config table, no per-shape loading count, and no per-shape model payload. Every new behaviour is a new `SHAPE ==` branch plus (for the constants) a shape-conditional expression.

## 3. How each K0-K8 is defined and classified

Definition (`:300-327`), documented tuple shape at `:296-299`: "(shape, extra tool argv, run via K6 wrapper, expected failed-check-id substrings (lowercase; empty = no check-level grading expected), description)".

| id | shape | extra argv | wrapper | expected tokens |
|---|---|---|---|---|
| k0 | k0 | — | no | — (good) |
| k1 | k1 | — | no | health |
| k2 | k2 | — | no | loading, envelope |
| k3 | k3 | — | no | teardown |
| k4 | k4 | — | no | teardown, sigkill, kill, graceful |
| k5 | k5 | — | no | teardown, graceful, signal, returncode, exit_status |
| k6 | k0 | — | yes | teardown, fault |
| k7 | k7 | `--ready-timeout 2` | no | — |
| k8 | k8 | — | no | teardown, graceful, signal, returncode, exit_status |

`ALL_IDS = tuple(CONTROLS)` at `:329`, and `--only` is constrained to it at `:635`.

Classification is exit-code arithmetic, not schema inspection (`run_control`, `:494-591`):

- good: `:551-555` — "accepted = (tool_exit == 0 and gate_exit == 0 / and not escaped and not tool_timed_out)"; `inconclusive = False`.
- bad base: `:557-566` — "base = (receipt_written and not tool_timed_out / and (tool_exit != 0 or (gate_exit is not None and gate_exit != 0)))"; `accepted = not rejected`.
- K6 override: `:560-563` — "rejected = receipt_written and tool_exit not in (0, None)"; the comment at `:561-562` states "accept any nonzero+receipt as a rejection, record the exact exit".
- attribution: `:570` — "inconclusive = bool(rejected and attributed is False)"; `_attributed` (`:454-460`) is **OR over tokens**: "return any(tok in fid for tok in expected for fid in low)". Multi-token expectations are satisfied by any one match.
- gate-flip arm: `:572-574` only for "cid != 'k0' and receipt_doc is not None", implemented at `:463-492`: deep-copy, flip every `passed is False` to `True` (`:471-474`), write `receipt-flipped.json` (`:477-479`), run the gate (`:481-486`), count `accepted` (`:487-491`). Its gate argv is fixed: `[sys.executable, str(gate), str(flip_path)]` (`:482`).
- per-control gate run on the raw receipt: `:511-519`, also fixed argv.
- empty-evidence handling: `_failed_checks` reads only `passed is False` (`:431-439`) — a `passed: null` check is invisible; an unparseable receipt appends `<receipt-unparseable>` (`:543-545`); a timeout appends `<tool-timeout>` (`:546-547`).
- K6's receipt *does* carry gradeable failures: the tool appends `teardown_graceful`/`teardown_port_closed` in a fault-tolerant block after the injected raise (`frozen/tools_kama-llamacpp-live.py:1309-1336`), so `failed` is non-empty and attribution succeeds.

Counting and exit (`main`, `:623-696`): counters initialised at `:649-656` (`accepted_bad`, `gate_flip_bad`, `inconclusive`, `good_ok`), incremented at `:665-679` (`good_ok` only from a k0 row, `:670`), `clean` at `:687-689`, exit at `:696` — "return 0 if (clean and good_ok) else 1". `--only` without k0 sets `good_ok = None` (`:684-685`). Own faults return 2 (`:680-682`); the docstring commits to that at `:28-30`.

JSON output: top-level object `schema`/`tool_sha256`/`gate_sha256`/`controls`/`accepted_bad`/`gate_flip_bad`/`inconclusive`/`good_ok` (`:649-656`); per-row keys at `:576-591` (`id`, `tool_exit`, `gate_exit`, `receipt_written`, `failed_checks`, `expected_failed`, `attributed`, `inconclusive`, `accepted`, `rejected`, `escaped`, `teardown_ok`, `gate_flip`, `tool_stderr_tail`). `--json` prints only the object (`:692-695`); the human summary line is `:616-620`. `SCHEMA = 'kama-live-controls/v1'` at `:81`.

## 4. Proven host facts about the listener detector (the suspected defect is real)

`_listen_inodes` (`frozen/tools_kama-llamacpp-live.py:311-342`) tests `endswith('00000001')` for `::1` and `addr_hex[:24] == '0000000000000000FFFF00'` for mapped IPv4 — the second literal is 22 characters compared with a 24-character slice, so it can never be equal.

Observed on this host (2026-10-20, read-only `/proc` plus one ephemeral `AF_INET6` listener on port 0, closed before exit):

- `::1`: `/proc/net/tcp6` row `00000000000000000000000001000000:0277`, state `0A`; `ss -ltn6` shows "[::1]:631" (0x277 = 631). The row ends `01000000`, not `00000001`.
- mapped: a listener on `::ffff:127.0.0.1` renders `0000000000000000FFFF00000100007F`; the tool's tests evaluate `endswith('00000001') = False`, `addr_hex[:24] == '0000000000000000FFFF00' = False`, `endswith('7F') = True`.
- the tool's own HTTP client is IPv4-only — `frozen/tools_kama-llamacpp-live.py:397` — "url = f'http://127.0.0.1:{port}{path}'" — and a v4 `urllib` GET to a `HTTPServer` subclass bound to `::ffff:127.0.0.1` returned 200, i.e. the fake can bind mapped and still be reachable.
- kernel ground truth: `get_tcp6_sock` prints four 32-bit words — `https://raw.githubusercontent.com/torvalds/linux/master/net/ipv6/tcp_ipv6.c` line 2175 — "src->s6_addr32[0], src->s6_addr32[1], src->s6_addr32[2], src->s6_addr32[3], srcp" (each word appears in little-endian order, which is why `::1` reads `01000000` in the last word).

Consequence chain for a fake bound only to `::ffff:127.0.0.1`: `_listen_inodes` returns the empty set → `port_owned_by` returns `None` (`:344-357`, "None: no listener yet, or /proc unreadable") → `verify_live` yields `port-listener-ownership-unproven` (`:627-641`) → `SetupError` → tool exit 2 with `setup_error`, no checks. A good server is therefore **rejected today** — the AF_INET6 control is red until the detector is fixed, which is exactly its job.

Minimal correct predicates (same spelling/state model as the existing tcp4 branch): `::1` = first 24 chars all `0` and last 8 == `01000000`; mapped 127/8 = `addr_hex[16:24] == 'FFFF0000'` and `addr_hex[24:32].endswith('7F')`. Note the slice must be `[16:24]` and the literal must be 8 characters `FFFF0000`; `endswith('7F')` alone is the right 127/8 test because the printed word is the v4 address byte-reversed (`127.0.0.1` → `0100007F`).

## 5. Minimal extension points for K9+ (exact lines)

**a. New fake knobs** — constants `:162-175`; per-path dispatch `:211-242`. Add one `SHAPE_CFG`-style dict inside `FAKE_TEMPLATE` (after `:175`) mapping shape → {loading counts, model list, owned_by, health status, metrics status, props alias, probe plan, bind family/host} and have `LOADING`/`MODELS_OK`/`PROPS`/`_envelope` read it. Keep the `%%NAME%%` + `.replace` convention (`:94-95`, `:340-344`). No shared state exists across controls, so this is safe.

**b. New control rows** — `CONTROLS` `:300-327` and `--only` choices `:635` (derived from `:329`). Nothing else needs editing for enumeration.

**c. An explicit expected-outcome field** — this is the load-bearing change. Today the model is binary (k0 accept, everything else reject) at `:551-570`. Add a 6th tuple element (or a sibling dict) with `expect ∈ {accept, reject, not-evaluated, gate-reject}`, then:
- replace `if cid == 'k0'` (`:551`), `if cid != 'k0'` (`:573`), `if row['id'] == 'k0'` (`:670`) and `if 'k0' not in selected` (`:684`) with membership in an `ACCEPT_IDS` set — otherwise a second good control lands in `accepted_bad` via `:557-566` and `:672`;
- add a `not-evaluated` branch comparing `tool_exit == 2 and gate_exit == 3 and outcome == 'not-evaluated'`, plus exactly one `passed is None` check whose id is `loading_envelope_graded` and `observed.not_evaluated_reason == 'no-loading-503-observed'`.
- record the result under its own counter (`:649-656`, `:665-679`, `:687-689`) and print it (`:597-604`, `:616-620`), or the human and JSON views diverge.

Two traps make the naive version wrong: with a token expectation, a legitimate not-evaluated run becomes INCONCLUSIVE because `failed` is empty (`:570` + `:454-460`); with `expected=[]`, it is silently counted as "rejected" (`:557-566`) and the suite exits 0 without ever checking exit 2 / gate exit 3.

**d. Tool-schema divergence (must be designed, not discovered)** — the same zero-loading control has different outcomes on the frozen v2 tool (tool exit 1, failed `loading_envelope_graded`) and on the round-18 v3 tool (exit 2, gate 3). A single global `expect` breaks the documented property that the script runs "verbatim against the round-17 frozen copies" (`:32-40`). Branch on the receipt's declared `schema` (or a declared-schema field in the row) and record which arm was taken.

**e. K6 tightening** — `:560-563`: replace `tool_exit not in (0, None)` with `tool_exit == 2`. Side effect is correct: the wrapper's unhandled-escape exit 4 (`:286-288`) with no receipt then fails `receipt_written` and is reported ACCEPTED-BAD. K6's wrapper patches the module attribute `teardown` (`:272-281`), so the C1 tool must keep a module-level `def teardown(proc, port, log_path)` name (`frozen/tools_kama-llamacpp-live.py:771`) or K6 raises `ControlsFault` ("patched teardown never fired", `:525-530`) and the suite exits 2.

**f. Gate-only forged controls** — `_gate_flip` (`:463-492`) is the working template for "derive a receipt, run the gate, expect rejection". Three changes are needed:
- parameterise the gate argv at `:482` (today hard-coded, no `--require-schema`; the frozen gate's argparse is `frozen/tests_llamacpp-live_check-receipt.py:1359-1370`);
- supply a base receipt. There is no stored v3 fixture in the lane (`.ufo/waves/round-18/c1` and `c2` were empty at write time), so the base must be a k0 receipt produced in the same invocation. `selected` is `ALL_IDS` in dict order (`:658`) and k0 is first, but `--only` (`:635`) breaks that ordering: either auto-run k0 as a fixture or mark these rows skipped-with-reason when no v3 base exists;
- add problem-level attribution. The gate's rejection is exit-only in controls (`:511-519`), while the gate prints "INVALID <path>: N problem(s)" followed by "  - <problem>" lines (`frozen/tests_llamacpp-live_check-receipt.py:1394-1396`). Without matching a `expected_gate_problem` substring, a forged control rejected for the wrong reason is indistinguishable from a targeted rejection — the same weakness as the OR-token attribution.

Forgery mechanics that isolate the intended defect:
- *self-declared v1 under `--require-schema v3`*: deep-copy the base, set `schema` to the v1 string, run the gate with `--require-schema v3`; expect exit 1 and a schema problem in the gate text.
- *extra argv flag*: insert the flag (e.g. `--api-key X`) **before** the tail. The tool's argv is `:1088-1095` with `--no-webui`/`--offline` last, and the frozen gate only checks specific flags plus that tail (`frozen/tests_llamacpp-live_check-receipt.py:419-421`), so a mid-list insertion is precisely the currently-undetected case.
- *non-exact 503 in transitions*: mutate a `/v1/models` 503 row's `body` and `body_sha256` to `BAD_ENVELOPE` (`:162-165`). Keep `loading_503`, `loading_503_bodies` and `repeats` self-consistent, or rejection may come from a different v3 relation [INFERENCE: the v3 relation set is not written yet].

**g. AF_INET6 bind** — template tail `:245-248`: "[HTTPServer.allow_reuse_address = True / _httpd = HTTPServer(('127.0.0.1', PORT), Handler)]". Minimal form: a subclass with `address_family = socket.AF_INET6` and `allow_reuse_address = True`, instantiated with `('::ffff:127.0.0.1', PORT)` when the shape asks for it (keep the v4 default). Do **not** try to derive the bind from `--host`: the fake ignores it (`:121-123`), the tool always sends `127.0.0.1` (`frozen/tools_kama-llamacpp-live.py:1091`) and the gate enforces exactly that (`frozen/tests_llamacpp-live_check-receipt.py:404-406`). The k7 raw-socket branch (`:151-160`) stays IPv4; the mapped control is a normal serving fake. `HTTPServer.server_bind` calls `getfqdn(host)`; on a literal address this resolves locally [INFERENCE], and my end-to-end run showed no delay. Classify the mapped fake in the ACCEPT set (item c) or it is counted as accepted-bad.

**h. `MutControlsSelf` self-checks** — the file has no self-test today (imports `:74-85`, `main` `:623-696`). Minimal insertion: extract the k0 predicate (`:551-555`) and the counting predicate (`:687-689`) into pure functions, then call a `_selfcheck()` at the top of `main` (before staging) that feeds synthetic rows through the *same* functions:
- drop `gate_exit == 0` from the k0 predicate → self-check must fail;
- make `_attributed` (`:454-460`) return `True` unconditionally → must fail;
- stub the gate with an always-0 executable → `_gate_flip` (`:481-491`) must report `accepted` (i.e. the arm can detect), and a stub that exits 1 only because of `setup_error` must be surfaced via `receipt_setup_error` (`:489-491`) rather than counted as check re-derivation;
- feed a doctored not-evaluated receipt (`passed: null` flipped to `true`) through the new validation and require rejection.
Add the failure count to `clean` (`:687-689`); otherwise the self-check is advisory. A self-check that tests a *copy* of the predicate will not kill mutants of the production path.

## 6. Traps the executor should not step in

- `_teardown_ok` (`:441-451`) coerces with `bool(c.get('passed'))`, so a v3 null teardown check reports `teardown_ok=False`. It is display-only and must not become a verdict input.
- `_read_receipt` distinguishes "no file" from "unparseable file" (`:418-428`); keep that distinction for v3, because a written-but-unparseable receipt is an escape-class defect, not a setup error.
- `_stage_control` silently substitutes an empty registry when the source registry is missing (`:386-391`); already flagged by `build/advice/SentinelControlsSafety.md` §2. New controls inherit the exposure because the tool's refused-port set is derived from that staged copy.
- `run_control` passes the whole environment to the tool (`:497-498` — "env = dict(os.environ)"); the tool's child allowlist holds (`frozen/tools_kama-llamacpp-live.py:1103-1105`), but new diagnostics must not print env values.
- `TOOL_TIMEOUT = 180.0` (`:88`) must stay ≥ the teardown+probe budget; k7's bound is the tool-side `--ready-timeout 2` (`:313-314`), so a hang control costs ~2 s, not 180 s.
- `_attributed`'s OR semantics (`:454-460`) mean an R5 control should carry exactly one token (e.g. `models_alias_id`) if "targeted" is to mean anything; today's k4/k5/k8 lists are intentionally unisolated.
- `_failed_checks` ignoring `null` means v3 null checks are invisible to attribution and to `gate_flip`'s "not failed" early return (`:467-468`) — a not-evaluated receipt gets no flip arm at all.

## 7. Suggested knob mapping for the six R5 targets (all reachable inside the existing template)

| targeted check | minimal fake change | isolation |
|---|---|---|
| `models_alias_id` | serve `data[0].id != ALIAS` only for non-curl UA (`:211-218`) | probes still see `ALIAS` |
| `models_owned_by_llamacpp` | `MODELS_OK.data[0].owned_by = 'other'` (`:167-168`) | no other check reads it |
| `metrics_not_enabled` | `/metrics` 200 instead of 501 (`:237-240`) | only the tool captures `/metrics` |
| `props_alias` | `PROPS['model_alias'] = ALIAS + '-x'` (`:169-171`) | probe does not read `/props` (`tools/kama-probe.sh:456` uses `/v1/models`) |
| `probe_model_ok` | serve an id that is neither `ALIAS` nor `kama-not-this-model` | probe 1 gets MODEL_MISMATCH, probe 2 still matches its expectation |
| `probe_mismatch` | after the first curl `/v1/models`, serve `kama-not-this-model` | uses the existing `STATE['probe_models']` counter (`:216-217`) |

Both probe knobs rely on the UA discriminator proven above; the tool's captures are `Python-urllib/3.14`, the probe's are curl.

## 8. Limitations

- No lane gate, `measure.py`, `survivors.py` or `controls.py` run was attempted (L1 owns measurements). The claims above are structural plus the two host observations described in §4.
- The mapped-address end-to-end proof used a bare `HTTPServer` subclass, not the generated fake; the fake's HTTP framing is identical, but the k0 receipt for a mapped fake has not been produced [INFERENCE].
- The exact v3 gate relation set is unknown at write time, so the "non-exact 503 in transitions" forgery's internal-consistency requirements are inferred from the frozen v2 gate (`frozen/tests_llamacpp-live_check-receipt.py:437-448`).
- `/proc/net/tcp6` word order was additionally corroborated by decoding live rows with `inet_ntop` (e.g. `4D010428…` → `2804:14d:…`), but only `::1` and the mapped bind are quoted above.

## 9. Installs / tooling

None. No package was installed or upgraded; two ephemeral loopback listeners (port 0) were created for the hex-format and HTTP-reachability proofs and closed before exit (`ss -ltn` confirmed none remained). Nothing was written outside this Report; no clone was created.
