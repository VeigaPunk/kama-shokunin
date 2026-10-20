VERDICT: partial — the v2 checks reject every named health/teardown/ownership/dedup-list forgery, but the gate accepts a self-declared v1 downgrade that erases all of them, plus argv, transition-503, count, digest, `served_model` and tool-identity forgeries.

Reviewed revision: lane commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`
(`git rev-parse HEAD` in the clone). Gate under attack:
`tests/llamacpp-live/check-receipt.py` sha256 `ad6801791f2ada896a7ee188609391aac86185c47320dbf415331869ca9cd2a5`.
Receipts: round-17 `live/receipt-1.json` `f34afb54…4702a4` (base for every v2
forgery), `receipt-2` `3df31ddb…39ad9`, `receipt-3` `5e2c0511…36d90`;
round-16 `live/receipt.json` `076865e5…bd4669` (v1 base). All three round-17
receipts are mode 644.

Claim under attack (`corpus/lessons/round-17.md:40-42`): "`loading_envelope_graded`
over every stored 503 body, and a receipt on internal faults; the gate re-derives
every v2 check and still validates v1 receipts"; SCORECARD `:666-670`: "receipt
v2 checks fail on the misbehaviour they name". The gate's own docstring claims
the stronger invariant (`check-receipt.py:18`): "Every claim is re-derived from
the stored evidence; a bare".

# What I ran

No llama-server, fake server or listener was started; no port in
`registry/endpoint-consumers.tsv`, 8080 or 34113 was contacted. Every gate run
executed in `/tmp/GateForgeries-clone` at `54a2926`, receipts in
`/tmp/GateForgeries-scratch`, with `PYTHONDONTWRITEBYTECODE=1`.

| # | command | exit |
|---|---|---|
| 1 | `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/GateForgeries-clone && git -C … checkout -q 54a29268…` | 0 |
| 2 | `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-17/live/receipt-{1,2,3}.json` | 0, 0, 0 `VALID` |
| 3 | `python3 tests/llamacpp-live/check-receipt.py --selftest` | 0, "2 valid receipt(s) accepted; 39 mutations + unreadable case all rejected" |
| 4 | for each mutant: `python3 tests/llamacpp-live/check-receipt.py MUTANT.json` | per table below |
| 5 | same, adding the four pins (`--expect-model-sha256 270cba1b…256d --expect-server-sha256 b6a31a8e…d804 --expect-probe-sha256 36b64978…29d3 --expect-tool-sha256 0efd1723…46ac`) | per table |
| 6 | `python3 tests/llamacpp-live/check-receipt.py mutants/25-….json` (downgrade) with and without pins | 0 `VALID`, 0 `VALID` |

Baselines accepted as controls: untouched receipt-1 (v2) and round-16 receipt
(v1) both exit 0, so every rejection below is attributable to the single-field
mutation. Scratch matching the frozen gate's own selftest mutation names
(`v2-health-degraded-body`, `v2-sigkill-sent`, …) reproduces rows 01-08.

# Matrix (0 = gate exit 0 VALID; 1 = rejected)

| # | forged receipt | bare | +4 pins | result |
|---|---|---|---|---|
| 00a | untouched v2 receipt-1 | 0 | 0 | control, expected |
| 00b | untouched round-16 v1 receipt | 0 | 0 | control, expected |
| 01 | health body `{"status":"degraded"}`, check `passed: true` | 1 | 1 | rejected (2 problems) |
| 02 | `sigterm_sent: false` + `returncode: 0` | 1 | 1 | rejected (3) |
| 03 | `sigkill_sent: true` + `returncode: -9` | 1 | 1 | rejected (5) |
| 04 | `returncode: -15` | 1 | 1 | rejected (3) |
| 05 | `alive_at_teardown_start: false` | 1 | 1 | rejected (3) |
| 06 | `port_listener_ownership: "unproven"` | 1 | 1 | rejected (3) |
| 07 | later non-exact body appended to `loading_503_bodies` | 1 | 1 | rejected (2) |
| 08 | `loading_observed: false` with `loading_503` still stored | 1 | 1 | rejected (2) |
| 09 | `schema: kama-llamacpp-live/v1`, checks untouched | 1 | 1 | rejected (unexpected ids) |
| **09b** | **same, v1 check set (swap `teardown_graceful`→`teardown_exited`, drop `loading_envelope_graded`)** | **0** | **0** | **ACCEPTED** |
| 10 | `schema: kama-llamacpp-live/v2` on the round-16 v1 receipt | 1 | 1 | rejected (4) |
| **11** | **`--api-key X` inserted before `--no-webui`** | **0** | **0** | **ACCEPTED (mandated attack)** |
| 11b | `--api-key X` appended after `--offline` | 1 | 1 | rejected (tail) |
| **12** | **second `--host 0.0.0.0` inserted before the tail** | **0** | **0** | **ACCEPTED** |
| **13** | **second `--port 9999` inserted before the tail** | **0** | **0** | **ACCEPTED** |
| **14** | **second `--alias evil` inserted before the tail** | **0** | **0** | **ACCEPTED** |
| **15** | **`--metrics` inserted before the tail, `metrics_not_enabled` still 501** | **0** | **0** | **ACCEPTED** |
| **16** | **`internal_fault: "internal:RuntimeError"`, `setup_error: null`** | **0** | **0** | **ACCEPTED** |
| **17** | **`loading_bodies_dropped: 37`** | **0** | **0** | **ACCEPTED** |
| **18** | **`captures.health.body_sha256: "0"*64`** | **0** | **0** | **ACCEPTED** |
| **19** | **check `observed.total_503_responses: 9999`** | **0** | **0** | **ACCEPTED** |
| **20** | **503 transition body non-exact, `loading_503_bodies` left exact** | **0** | **0** | **ACCEPTED** |
| **21** | **`captures.health.body_truncated: true`** | **0** | **0** | **ACCEPTED** |
| **22** | **check `observed.body: {"status":"degraded"}` while capture is ok** | **0** | **0** | **ACCEPTED** |
| **23** | **probe row `served_model: "ghost-model"`, verdict MODEL_OK** | **0** | **0** | **ACCEPTED** |
| **24** | **`tool` block deleted** | **0** | **1** | **ACCEPTED by the bare invocation** |
| **25** | **v1 relabel + degraded health + sigterm false + sigkill true + not alive + rc -9 + loading check dropped** | **0** | **0** | **ACCEPTED** |

Accepted-bad: 15 of 24 forged receipts bare; 14 of 24 under all four pins.
Every mandated attack except 11 is rejected; 11 is accepted, and 09's
substantive form (09b/25) is accepted.

# Findings

## F1 (P1) — schema is self-declared, so every v2 guarantee is optional
`check-receipt.py:206` "if schema not in (RECEIPT_SCHEMA, RECEIPT_SCHEMA_V2):"
and `:653` "required = REQUIRED_CHECKS_V2 if is_v2 else REQUIRED_CHECKS_V1".
A forger sets `schema` to v1, renames `teardown_graceful` to `teardown_exited`
and drops `loading_envelope_graded`; the same receipt then carries a degraded
`/health` body (v1 only checks status 200), `sigterm_sent: false`,
`sigkill_sent: true`, `alive_at_teardown_start: false`, `returncode: -9`, and
still exits `VALID` under all four pins (mutant 25). Nothing binds the schema
to the producer: `tool.sha256` is not consulted when choosing the check set.
Round-17 v2 receipts are therefore downgradeable at will, which is the
load-bearing form of the mandated "v1 label on a v2 receipt" attack (the bare
relabel, mutant 09, is rejected only by the unexpected check ids).

## F2 (P1) — argv validity is checked per named flag, never as a whole
`:387` "argv consistency"; `:404` "if argv_flag(argv, \"--host\") != \"127.0.0.1\":";
`:419-421` "tail = argv[-2:]" / "if tail != [\"--no-webui\", \"--offline\"]:".
`argv_flag` (`:169-176`) returns the **first** matching value, and there is no
allowlist, no duplicate rejection and no length check. Consequences, each
accepted bare and with all four pins:
- mandated: `--api-key X` inserted anywhere before `--no-webui` → `VALID`.
  The receipt is world-readable (644); the gate's env rule says values are
  never recorded (`:371`), but argv has no such rule.
- `--host 0.0.0.0` inserted after the checked loopback value → the receipt
  still records `--host 127.0.0.1` first and claims loopback-only serving.
- `--port 9999`, `--alias evil` likewise: the checked first occurrence is
  untouched; the effective duplicate is invisible to the gate. [INFERENCE]
  llama.cpp's parameter loop assigns on each occurrence, so the later value
  wins; even if the first value won, the gate cannot distinguish the two and
  the receipt is self-contradictory.
- `--metrics` inserted while `captures.metrics.status` is 501 and
  `metrics_not_enabled` is claimed passed: the check's own `documented_by`
  says `/metrics` requires `--metrics`, so the receipt contradicts itself and
  is still `VALID`.

Reproduce row 11 (exit 0 on the gate at `54a2926`):
```python
import json
r = json.load(open(".ufo/waves/round-17/live/receipt-1.json"))
a = r["argv"]; i = a.index("--no-webui")
a[i:i] = ["--api-key", "X"]          # or ["--host","0.0.0.0"] / ["--port","9999"]
json.dump(r, open("/tmp/GateForgeries-scratch/f.json", "w"))
# python3 tests/llamacpp-live/check-receipt.py /tmp/GateForgeries-scratch/f.json
```

## F3 (P1) — "every stored 503 body" grades only a self-selected list
`:922-933` iterates only `receipt.get("loading_503_bodies")`; `:441-445` for
transitions asks only "t.get(\"status\") == 503", never parses that row's body.
`loading_bodies_dropped`, `total_503_responses`, `distinct_bodies` and
`repeats` are never read by the gate (grep: no hits outside the receipts).
Mutant 20 keeps `loading_503` and `loading_503_bodies` exact while replacing
the transitions 503 body with a non-exact envelope → `VALID`. Mutant 07 (the
same non-exact body placed in the graded list) is rejected, so the
fail-capability exists but is escapable by choosing which field carries the
bad body. Mutants 17 and 19 show the recorded loss counters can be arbitrary.
C2's wording "over every stored 503 body" is true only for the producer-chosen
dedup list, which the gate cannot tie back to `transitions`.

## F4 (P2) — `internal_fault` is never validated
The string appears nowhere in `check-receipt.py` (grep: zero hits in
`validate`). Mutant 16 sets `internal_fault: "internal:RuntimeError"` with
`setup_error: null` → `VALID`. The producer mirrors an internal fault into
`setup_error`, which the gate does reject; the exposed channel is a receipt
that advertises a fault while passing clean, or the producer dropping the
`setup_error` mirror.

## F5 (P2) — captured digests and truncation flags are not re-derived
`body_sha256` is referenced only in the selftest literals (`:1063-1110`); no
`check_digest` call covers `captures.*`, `transitions[].body_sha256` or
`loading_503.body_sha256`. Mutants 18 (`body_sha256: "0"*64`) and 21
(`body_truncated: true`) are `VALID`. The live receipt's health digest does
match its body (`a29ee2b1…d288`), so the gap is latent, but a receipt whose
hashes contradict its plaintext passes the gate.

## F6 (P2) — check `observed` evidence is only partially cross-checked
`health_ready` cross-checks only `observed.status` (`:697-700`), not
`observed.body`; mutant 22 records `observed.body: {"status":"degraded"}` with
`passed: true` while the capture is `{"status":"ok"}` → `VALID`.
`served_model` is never checked in `probes[]` rows (only the selftest literal
at `:1011`); mutant 23 records `served_model: "ghost-model"` with
`verdict: MODEL_OK` and `claimed passed` → `VALID`. `served_model` is the
field C1's repair added, so the C2 receipt accepts a probe row that
contradicts it.

## F7 (P3) — identity blocks are optional on the recorded invocation
`:351` "tool = receipt.get(\"tool\")" accepts a missing block unless
`--expect-tool-sha256` is supplied. The recorded C2 run
(`.ufo/waves/round-17/live/gate.txt`) shows only bare `VALID <path>` lines;
mutant 24 (tool block deleted) passes that invocation and fails only with the
tool pin. `pdeathsig` is similarly optional.

## What held
The mandated forgeries 01-08 and 10 are rejected for the documented reasons
(exact health body, live child + SIGTERM + no SIGKILL + rc 0, ownership-gated
port, exact dedup list, loading_observed consistency, v1 schema completeness),
each with the claimed `passed` re-derivation also listed. Gate `--selftest`
passes 41 cases. The three live receipts validate and still carry the v2
`teardown_graceful`/`loading_envelope_graded` evidence quoted in the lesson.

# Limitations

- Receipts were hand-forged; no tool run was made, so this says nothing about
  `controls.py` K0-K8 or the frozen-arm counts (C2's counting claim stands
  unrefuted here). The exposed principle is the one C2 states: the gate
  re-derives claims from stored evidence; that evidence includes channels the
  gate does not read.
- C1 was not attacked by this seat (assignment scope: the v2 receipt gate).
- `--selftest` mutants overlap rows 01-08 by design; my matrix reuses the same
  single-field shapes against the real receipt rather than the selftest
  literal.
- Duplicate-flag effectiveness on llama-server is [INFERENCE]; the gate defect
  (first-match, no duplicate/totality rule) is observed directly.

# Installs

None. No tool was installed or upgraded; no pacman/uv/npx command was run.
Scratch (`/tmp/GateForgeries-clone`, `/tmp/GateForgeries-scratch`) removed
after the runs; no listener was created.
