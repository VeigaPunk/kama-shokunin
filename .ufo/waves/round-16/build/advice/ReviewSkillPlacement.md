# ReviewSkillPlacement — SKILL.md placement for MODEL_LOADING, the stub gate and the live capability

Seat: review (read-only). Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Read at 2026-10-20 10:31 -03 against the in-flight build tree (probe, matrices,
harness, receipt validator and `measure.py` had landed; `SKILL.md` is unchanged
at 504 lines, mtime 05:18). I ran no lane gate, harness, snapshot or live probe;
the only executions were `check-receipt.py --selftest` (self-contained),
`llama-server --version`, and file hashes. No installs, no upgrades.

## 1. Where the load-bearing text lives

| Concern | Location | Current content |
|---|---|---|
| Verdict vocabulary | `SKILL.md:11-14` | "Verdict vocabulary is shared with" `tools/kama-probe.sh`, then six verdicts and probe exits 0/2/1 |
| Decision table | `SKILL.md:125-141` (rows 129-140) | HTML responder → `FOREIGN_SERVICE` (129); different-kind responder → `FOREIGN_SERVICE` or `NOT_HTTP` (131); refused → `DEAD` (130) |
| Served-id normalization | `SKILL.md:142-156` | precedence `data[].id → models[].id → …`; empty ⇒ `MODEL_MISMATCH` |
| Error signatures | `SKILL.md:167-190` | September sample; llama.cpp root 404 at 177; "byte-for-byte from the live response" convention at 184-185 |
| Checklist | `SKILL.md:191-242` | item 5 liveness vs identity at 220; exit meanings at 196-202 |
| Anti-patterns | `SKILL.md:244-293` | `/health` is not identity (252-254); listening ≠ model (270-276) |
| Base gate registry | `SKILL.md:294-307` | 5-column table (301), four rows (303-306) |
| Cited sources / current artifacts | `SKILL.md:308-343` | "Current runnable artifacts" enumerates only probe, snapshot harness, registry (313-315) |
| Round registries | `SKILL.md:347`, `388`, `411`, `438`, `478` | 7-column "Verdict map / Self-test / Pinned values / Write scope / Owner" from round 12 on (`394`, `428`, `468`, `493`) |
| Exit-transfer warning | `SKILL.md:463-466` | "Do not transfer exit meanings across tools" |
| Append point | `SKILL.md:504` (EOF) | round-15 section ends; append here, change nothing above |

## 2. Findings

### High

**F1 — The header vocabulary is already contradicted by the shipped probe.**
`SKILL.md:11-14` lists six verdicts; `tools/kama-probe.sh:60` now reads
`VOCAB="… DEAD NOT_HTTP MODEL_LOADING"`, and the help at `:115` lists seven.
Append-only means the header stays stale, so the round-16 section must declare
the supersession explicitly and name the effective seven-string set. Without
that paragraph the file's primary vocabulary contract is false.

**F2 — The decision table has no loading row and points the wrong way.**
`SKILL.md:129` routes an HTML responder to `FOREIGN_SERVICE` and `:131`
"Consumer's port answers as a different kind of service" to
`FOREIGN_SERVICE` or `NOT_HTTP`; neither covers a 503 JSON envelope from a live,
not-yet-ready model runtime. A reader applying the table will "identify the
responder" and report the pin for correction — the exact overreach C1 repairs.
The append must state the loading rule, that the table's `FOREIGN_SERVICE` rows
do not apply to this envelope, and the operator action (wait and re-probe, do
not repoint).

**F3 — "drift true" is not uniform across subcommands.**
`check`/`snapshot` mark any verdict other than `MODEL_OK` as drift
(`tools/kama-probe.sh:864`: `if [ "$verdict" != "MODEL_OK" ]; then drift=true; fi`,
returning 2 at `:881`), but `consumers` exits on registry-text agreement only
(`:798`, JSON map at `:814`) — a `MODEL_LOADING` row there does not
produce exit 2. An unqualified "MODEL_LOADING is drift" sentence in the append
would overstate `consumers`. The proposed text scopes drift to `check` and
`snapshot` and says `consumers` exit 0 remains a text-match result.

### Medium

**F4 — The signature table cannot be extended in place; the append needs its own
row, sourced honestly.** `SKILL.md:167` is explicitly the "September runtime
sample", and `:177` records the *ready-state* root 404
`File Not Found`. The loading body answers every non-frontend path, so quoting
it at `:177` would be wrong even if editing were allowed. The convention at
`:184-185` says every quoted fragment is "byte-for-byte from the live
response"; the compact reordered body in
`tests/probe-verdicts/LoadingEnvelope.json` (`"why": "Byte-exact llama.cpp
b11755 loading wire body …"`) is a stub `body_text`, not a verified wire
capture. `safe_json_to_str` calls `data.dump_safe()`
(`sources/llama.cpp-704366d/server-common.cpp:1695-1696`), and nlohmann's default
object container orders keys alphabetically, so the wire order is plausibly
`code,message,type`, not `message,type,code` [INFERENCE]. The append should cite
the README rendering and state that parsing, not byte order or spacing, is what
is matched.

**F5 — The new rows must use the 7-column registry shape.**
`SKILL.md:301` is the old 5-column table (`Name | Kind / entry command | Exit
map | Self-test / pinned values | Write scope`); rounds 12-15 use the 7-column
form with separate `Pinned values` and `Owner` (`:493`). Reusing the 5-column
shape would bury the frozen-probe digest and probe-sha pins, which are the only
reason the red-before measurement is reproducible. The append follows `:493`.

**F6 — "Current runnable artifacts" (`SKILL.md:313-315`) becomes false.**
It lists probe, `test-snapshot.sh` and the registry only. After this wave there
are also `tests/probe-verdicts/check.py` + eight matrix files,
`tools/kama-llamacpp-live.py`, `tests/llamacpp-live/check-receipt.py`,
`.ufo/waves/round-16/measure.py`, `frozen/` and `sources/`. The append names
them so the "current" claim does not silently rot.

**F7 — `MODEL_LOADING` is conditional on `python3`.**
`tools/kama-probe.sh:426` is `body_is_llamacpp_loading`, which returns 1 when
`HAVE_PY=0` (`:77-78`); the header still documents python3 as optional
(`:57`: "Deps: ss, curl, flock, coreutils. python3 optional"). On a host
without python3 the loading envelope falls back to `FOREIGN_SERVICE` /
`non-2xx-non-model-http`. The append must say the verdict does not exist there;
otherwise the doc promises unconditional detection.

**F8 — The live receipt does not prove the loading envelope.**
`tests/llamacpp-live/check-receipt.py:35-45` requires exactly nine checks and
none of them is `loading_observed`; the harness records `loading_503` and
`transitions` as best-effort captures (`tools/kama-llamacpp-live.py:547-548`,
`'loading_observed': False` in the receipt initializer). A valid receipt may show
`loading_observed: false` because a tiny GGUF loads before the first poll. The
append must not let the capability stand in for the C1 measurement; the stub
matrix is the measurement.

### Low

**F9 — `registry/endpoint-consumers.tsv:31-32` still lists six verdicts**
("#   MODEL_OK | … | NOT_HTTP"). It is outside the append-only scope of
`SKILL.md` and outside every build item's owned file, so L1 must make the
one-comment companion edit or accept a stale registry header.

**F10 — The stub gate's exit 0 is classification-only and its exits are not
probe exits.** `tests/probe-verdicts/check.py:26-27` reads "Exit 0 iff every
record passes, 1 on any test failure (including a probe timeout)", with 2 for
schema/argv error. The matrix's `expected.exit` is the probe's exit (0 or 2).
The append must say so, per `SKILL.md:463-466`; otherwise a green harness reads
as `MODEL_OK`.

**F11 — The live harness's port refusal fails open.**
`tools/kama-llamacpp-live.py:144-145` returns `refused_ports()` with only
`{8080, 34113}` on registry error (`except OSError: return refused`). C2's
"never a registered consumer port" is therefore conditional on registry
readability. The receipt records `refused_ports`, so the qualification is
auditable; the append states it rather than repeating the absolute claim.

**F12 — The frozen-before verification is the red measurement's anchor.**
`.ufo/waves/round-16/measure.py:9-10` reads "Any mismatch exits 4 without
running the harness"; it checks the frozen probe against
`frozen/manifest.json` (sha256, byte count, git blob at
`20e392e:tools/kama-probe.sh`).
The append pins that manifest and the 47,443-byte sha256
`93ee4302…cd64`; otherwise "red against the frozen probe" is not reproducible
once the frozen file or the manifest can be edited.

### Positive verifications (no defect)

- Upstream C1 facts hold at the pinned commit `704366d76`:
  `middleware_server_state` spans `server-http.cpp:307-328`; the 503 body fields
  are `:318-320`; the comment at `:312-313` says "no endpoints are allowed to be
  accessed when the server is not ready"; README `:485-487` gives the same body
  for `GET /health` and "the model is still being loaded".
- The landed probe branch sits after the 401/403 branch and before the
  HTML/FOREIGN fallbacks (`tools/kama-probe.sh:501-507`), the parser requires a
  dict `error` dict, exact message/type and a non-bool int 503 (`:426-441`), and
  the listeners counter (`:731`), summary key `model_loading` (`:741`) and
  baseline whitelist (`:937`) all landed.
- All eight matrix families parse under the shared schema (64 tests, 0 schema
  violations by my check). Positive controls include the exact envelope with
  alias/wildcard/dash, permuted key order, pretty-printed body, 64 KiB padding
  and every-non-frontend-path; negative controls include `no slot available`,
  lowercase message, `server_error` type, string code, missing wrapper,
  plaintext, HTML 503, 401/403 precedence, and a closed port.
- `tools/test-snapshot.sh` gained a MODEL_LOADING baseline case and a still-
  dropped unknown verdict (`MODEL_LOADED`); the case is offline and does not
  need a live loading server.
- `check-receipt.py --selftest` reports "10 mutations + unreadable case all
  rejected; valid receipt accepted".
- Installed identities: `llama-server` → `~/.local/opt/llama-b11755/llama-server`,
  `version: 0.7.0-dev (build 11755, commit 704366d76)`, binary sha256
  `b6a31a8e…d804`; model sha256
  `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`. No
  listener on 8080/34113 at read time.

## 3. Proposed append-only text

Append after `SKILL.md:504`, changing nothing above. It uses the round-12+
7-column registry shape (`SKILL.md:493`) and the file's "owner: kama" heading
convention.

```markdown
## Round-16 calibration — llama.cpp loading envelope and live capability (owner: kama)

Round 16 adds one verdict, `MODEL_LOADING`, and one capability-acquisition tool.
The vocabulary list at the top of this file, the decision table, and the
historical signature table are the pre-round-16 text; they are preserved as
history and are not rewritten. Effective vocabulary after this round is the six
strings above plus `MODEL_LOADING`, and every `check`/`consumers`/`listeners`/
`snapshot` JSON document carries all seven in `verdict_vocabulary` because the
probe renders that field from `VOCAB` (`tools/kama-probe.sh:60`). JSON schemas
stay `kama-probe/v1` and `kama-probe/v2`; the only summary key added is
`listeners.summary.model_loading`.

`MODEL_LOADING` (reason `llamacpp-loading`) is chosen only when `GET /v1/models`
returns HTTP 503 and the body is a JSON object whose `error` object has
`message == "Loading model"`, `type == "unavailable_error"` and an integer
`code == 503`, all exact. llama.cpp b11755 (`704366d76`) installs
`middleware_server_state` at `tools/server/server-http.cpp:307-328`; while
`is_ready` is false it answers every non-frontend path, `/health` included, with
that body (fields at `:318-320`), and `tools/server/README.md:485-487` documents
the same body for `GET /health` — "the model is still being loaded".
Classification reads `GET /v1/models`; the probe's `/health` request is
corroboration only. `MODEL_LOADING` is drift for `check` and `snapshot`
(`verdict != MODEL_OK`, exit `2`), and it is not readiness, liveness, identity,
or a consumer-pin fault: wait and re-probe, and do not repoint a consumer
because a loading server answered. `consumers` still exits on registry-text
agreement, so a `MODEL_LOADING` value in its rows does not change its exit, and
`listeners` counts the verdict under `summary.model_loading`, not
`model_endpoints`.

Scope limits, all load-bearing:

- The rule is the exact b11755 envelope, never "any 503". `no slot available` is
  built by the same runtime from `ERROR_TYPE_UNAVAILABLE`
  (`server-context.cpp:5396`; `server-common.cpp:119-122` maps that type to
  `unavailable_error`/503), so the exact message is the discriminator; matrix
  case `Overbroad503.no-slot-available` pins it. Every other 503, every 2xx,
  every HTML body, and every body differing in case, type, code type, wrapper or
  nesting keeps its earlier verdict, including `FOREIGN_SERVICE` /
  `non-2xx-non-model-http`.
- The branch requires `python3` (`tools/kama-probe.sh:77-78`,
  `body_is_llamacpp_loading` at `:426`). The probe still documents python3 as
  optional (`tools/kama-probe.sh:57-58`); without it the pre-round-16
  `FOREIGN_SERVICE` path is used — fail-closed to the old verdict, never a
  silent `MODEL_OK`. A host without python3 does not produce this verdict.
- `MODEL_LOADING` is transient. A baseline row carrying it is a real prior
  verdict and is diffed, not dropped as malformed (`tools/kama-probe.sh:937`).
  A `DELTA.md` line `verdict MODEL_LOADING -> MODEL_OK` is the loading-to-ready
  edge, not a repaired pin.

### Round-16 signature (additive to the historical table above)

| Verbatim string | Where | Meaning | Next action |
|---|---|---|---|
| `{"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}` (README rendering; the probe matches parsed fields, not key order or spacing) | every non-frontend path on llama.cpp b11755 while `is_ready` is false, including `GET /v1/models` and `GET /health`; ready-state surfaces observed 2026-10-20 are `/health` 200 `{"status":"ok"}`, `/v1/models` 200, `/slots` 200, `/metrics` 501 without `--metrics` | `MODEL_LOADING` / `llamacpp-loading`: the runtime is alive, not ready, and not a foreign service | Wait, then re-probe; do not repoint the consumer and do not classify a fault |

### Round-16 local evidence registry (owner: kama)

Additive to every registry row above; none of those rows change. These entries
are lane-local evidence, never native judgment, mission-completion authority or
serving readiness.

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Loading-envelope verdict conformance | gate: `python3 tests/probe-verdicts/check.py [--probe PATH] [--only NAME] [--json]` | 0 every literal expectation met; 1 at least one verdict/reason/probe-exit mismatch or probe timeout; 2 could-not-evaluate (argv error, missing probe, duplicate names across files, unknown keys, invalid route shape, unknown `--only` name); harness exits are not probe exits, and neither 0 nor 1 is endpoint readiness | `python3 tests/probe-verdicts/check.py --selftest` runs the matrix and must reject 3 embedded malformed tests; the eight families cover the loading envelope, the loading race, non-loading statuses, overbroad 503s, ready controls, auth/dead and foreign controls | `tests/probe-verdicts/*.json` literal `verdict`/`reason`/probe `exit` per test; the harness JSON carries `probe_sha256` and `matrix_sources`; frozen pre-round-16 probe `.ufo/waves/round-16/frozen/kama-probe-before.sh` sha256 `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64` (47,443 bytes) pinned in `.ufo/waves/round-16/frozen/manifest.json` | stdout plus removed loopback stubs; no live endpoint, no network, no registry change | kama |
| Round-16 C1 measurement | measurement (not a gate): `python3 .ufo/waves/round-16/measure.py [--probe NAME=PATH]` | 0 the frozen probe fails exactly the `MODEL_LOADING` expectations and passes every other row, the current probe has no failures, and the changed set equals that expectation set; 1 the measurement ran and that condition did not hold; 2 usage error; 3 unreadable or malformed frozen manifest; 4 the frozen snapshot failed its sha256/byte/git-blob check and nothing ran | same command writes `.ufo/waves/round-16/run-<name>.json` with `command`, `exit`, `stdout_sha256`, `parsed`, `stderr_tail` | `.ufo/waves/round-16/frozen/manifest.json` pins `sha256`, `bytes`, `source_commit` `20e392e`, `source_path` `tools/kama-probe.sh`, blob `447e29b` | `run-*.json` under the round-16 directory plus stdout; no serving-state write | kama |
| Local llama.cpp live capability | capability (not a gate): `python3 tools/kama-llamacpp-live.py --model PATH --model-sha256 HEX [--server PATH] [--alias ID] [--probe PATH] [--out PATH]` | 0 every check passed; 1 at least one check failed (server ran; receipt written); 2 setup error (missing or non-executable binary, missing model or probe, launch failure, ready timeout, signal, receipt write failure); 3 model digest mismatch, refuses to launch | evidence is the `kama-llamacpp-live/v1` receipt; `python3 tests/llamacpp-live/check-receipt.py RECEIPT [--expect-model-sha256 HEX] [--expect-server-sha256 HEX]` re-derives the claims: 0 valid, 1 invalid with every problem listed, 2 unreadable or not JSON; `--selftest` exercises its valid/mutation matrix | llama.cpp b11755 `704366d76` at `~/.local/opt/llama-b11755/llama-server` (installed binary sha256 `b6a31a8e…d804`); GGUF `~/.cache/kama-shokunin/models/stories260K.gguf` sha256 `270cba1b…256d`; required checks `health_ready`, `models_alias_id`, `models_owned_by_llamacpp`, `metrics_not_enabled`, `props_alias`, `probe_model_ok`, `probe_mismatch`, `teardown_exited`, `teardown_port_closed` | one ephemeral loopback listener on a free port, refusing 8080, 34113 and every port the registry expresses while readable; temp log and optional receipt; no `~/.config`, `~/.omp`, systemd or service write; teardown proves the process exited and the port refuses | kama |

Notes:

- The live capability launches a lane-owned server, a new write class for this
  file: process and temp-file writes with teardown, no persistent surface. A
  valid receipt certifies one launch against the listed checks; it is not a
  claim that the installed binary, model or port policy suits any consumer, and
  it never authorizes a registry row. `loading_503`/`loading_observed` and
  `transitions` are best-effort lifecycle captures, not required checks, so a
  valid receipt can show `loading_observed: false` when a small model loads
  before the first poll. The loading-envelope verdict is measured by the stub
  matrix, not by the live receipt.
- The port-refusal rule fails open when `registry/endpoint-consumers.tsv` is
  unreadable: `refused_ports()` then returns only `{8080, 34113}`. The receipt
  records `refused_ports`, so the excluded set is auditable; do not read the
  capability as a guarantee beyond that set.
- The stub gate and the measurement runner contact no endpoint. Their green
  exits certify classification of stubbed bytes and one fixed before/after
  comparison, not serving state: harness exit 0 is not `MODEL_OK`, and runner
  exit 4 is not a probe error. Do not transfer exits between the harness
  (0/1/2), the runner (0/1/2/3/4), the receipt validator (0/1/2) and
  `kama-probe.sh check` (0/2/1); inspect each JSON's records, rows and scope.
- New artifacts from this round: `tests/probe-verdicts/check.py`,
  `tests/probe-verdicts/*.json`, `tools/kama-llamacpp-live.py`,
  `tests/llamacpp-live/check-receipt.py`, `.ufo/waves/round-16/measure.py`,
  `.ufo/waves/round-16/frozen/`, and `.ufo/waves/round-16/sources/` (b11755 at
  `704366d76`). `test-snapshot.sh` gains one offline case: a `MODEL_LOADING`
  baseline row is diffed, and an unknown verdict such as `MODEL_LOADED` is still
  dropped as malformed.
```

## 4. Pre-commit checks for L1

1. The exit maps above were transcribed from the landed tools at 10:31
   (`check.py:26-28`, `kama-llamacpp-live.py:16-20`, `check-receipt.py:20-22`,
   `measure.py:22-29`). If any tool changes before integration, re-read
   `--help`/docstring and edit the row, not the code.
2. Do not restate `LoadingEnvelope.canonical-alias.why`'s "byte-exact" claim in
   `SKILL.md`; it is a stub body and its key order is unverified.
3. Companion edit outside the append: `registry/endpoint-consumers.tsv:31-32`
   vocabulary comment.
4. Optional: extend the round-15-era coverage wording at `SKILL.md:303` and
   `:306` rather than leaving `test-snapshot.sh` under-described; an append note
   is already included above, so this is not required for truth.

## 5. Verification gaps and residual risk

- I did not run the stub matrix, `test-snapshot.sh`, `measure.py`, or the live
  harness; the C1/C2 numbers remain L1's to produce. My matrix claims are
  parse/schema and static-reading claims only.
- The "wire key order is `code,message,type`" conclusion is `[INFERENCE]` from
  nlohmann's default ordered object plus `dump_safe()`; I did not capture the
  live body bytes and do not claim them.
- `server-context.cpp:5396` was fetched and read at the pinned commit but is not
  in `.ufo/waves/round-16/sources/`; the in-repo pin for the no-slot case is the
  matrix test, not a saved source file. If the doc cites the upstream line, the
  citation is verified upstream but not wave-pinned.
- The live capability remains unmeasured by me: no receipt exists yet, so the
  port-refusal and teardown claims are read from code, not from an observed run.
