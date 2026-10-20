VERDICT: confirm — three pinned real runs passed the v3 gate; a zero-loading receipt remains NOT-EVALUATED, never a pass.

# LiveV3 — real producer/gate compatibility

## Scope and authority

Axes: **operability** (the delivered lifecycle producer and receipt gate agree on real b11755 surfaces) and **calibration** (observed loading evidence is distinguished from no loading observation). This is bounded advisory evidence for L1, not an outside non-author judgment or admission decision. L1 retains integration/admission authority.

The experiment used the assigned isolated clone at commit `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`; `git rev-parse HEAD` returned that exact hash. The official Round-18 statement is C1 operability 8→8, with a one-engine/host-path boundary (`/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:744-751`); the lesson’s S055 row also records three v3 runs and four-pin gate results (`corpus/lessons/round-18.md:53-54`). This seat independently repeated that bounded real-runtime test.

## Exact real experiment

Working directory: `/tmp/kama-r18-falsify-LiveV3` (isolated clone; no writes to the lane checkout). Producer invocations were serial, one server at a time, with `--out /tmp/kama-r18-falsify-LiveV3/real-N.json` for N=1,2,3:

```sh
python3 tools/kama-llamacpp-live.py \
  --server /home/vgpnk/.local/opt/llama-b11755/llama-server \
  --model /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf \
  --model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d \
  --alias kama-r18-live --out /tmp/kama-r18-falsify-LiveV3/real-N.json
```

For each receipt, the gate was run with `--require-schema v3` and all four expected digests (model, server, probe, tool):

```sh
python3 tests/llamacpp-live/check-receipt.py \
  /tmp/kama-r18-falsify-LiveV3/real-N.json --require-schema v3 \
  --expect-model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d \
  --expect-server-sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 \
  --expect-probe-sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 \
  --expect-tool-sha256 dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b
```

The producer output for each run was `TOOL_EXIT=0` (no stderr output). A sequential gate pass over all three receipts printed `VALID /tmp/kama-r18-falsify-LiveV3/real-N.json` and `GATE_N_EXIT=0` for N=1,2,3. No timeout, setup error, or unobserved loading state occurred.

| Run | Ephemeral loopback port / child PID | Recorded loading evidence | Outcome / exits | Teardown |
|---|---|---|---|---|
| 1 | `127.0.0.1:33857` / `1854353` | `loading_observed=true`; one distinct exact body SHA-256 `baa09177700f64520a799fd2628bb3663c1486b25e17e4a507f2e6c81bef957c`; 27 `/v1/models` 503 responses, zero dropped. Four transition rows: initial connection refusal at 6 ms, loading 503 at 12 ms, then `/v1/models` 200 and `/health` 200. | `pass`; tool exit 0; v3 gate `VALID`, exit 0. All 11 required checks were evaluated and `passed=true`, including `loading_envelope_graded` (`total_503_responses=27`, `all_exact=true`). | `port_listener_ownership=child`; SIGTERM sent, returncode 0, no SIGKILL, `port_refuses=true`; model post-hash equals pin. |
| 2 | `127.0.0.1:45201` / `1867646` | `loading_observed=true`; same single exact body hash; 36 `/v1/models` 503 responses, zero dropped. Four transition rows: initial connection refusal at 6 ms, loading 503 at 12 ms, then `/v1/models` 200 and `/health` 200. | `pass`; tool exit 0; v3 gate `VALID`, exit 0. All 11 required checks evaluated true; loading check records `total_503_responses=36`, `all_exact=true`. | Child ownership proven; SIGTERM/returncode 0, no SIGKILL, port refused after teardown; model post-hash equals pin. |
| 3 | `127.0.0.1:42815` / `1869288` | `loading_observed=true`; same single exact body hash; 38 `/v1/models` 503 responses, zero dropped. Four transition rows: initial connection refusal at 6 ms, loading 503 at 11 ms, then `/v1/models` 200 and `/health` 200. | `pass`; tool exit 0; v3 gate `VALID`, exit 0. All 11 required checks evaluated true; loading check records `total_503_responses=38`, `all_exact=true`. | Child ownership proven; SIGTERM/returncode 0, no SIGKILL, port refused after teardown; model post-hash equals pin. |

The 11 evaluated checks in each real receipt were `health_ready`, `models_alias_id`, `models_owned_by_llamacpp`, `metrics_not_enabled`, `props_alias`, `probe_model_ok`, `probe_mismatch`, `teardown_graceful`, `teardown_port_closed`, `loading_envelope_graded`, and `model_unchanged`. The exact child argv in each receipt was the pinned server with `-m <pinned GGUF> --alias kama-r18-live --host 127.0.0.1 --port <listed ephemeral port> -c 256 -t 1 --no-webui --offline`. All three receipts record `port_refusal_set=[8080,34113]`; each selected port is outside that set. The gate rejects missing hard pins or a selected port inside the refusal set (`tests/llamacpp-live/check-receipt.py:310-338`). The three `model_sha256_post` values equal the expected model hash.

### Pins and retained receipt identities

SHA-256 values observed in the clone and at the supplied read-only assets:

- llama-server: `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`
- GGUF: `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`
- producer `tools/kama-llamacpp-live.py`: `dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b`
- probe `tools/kama-probe.sh`: `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`
- gate `tests/llamacpp-live/check-receipt.py`: `c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335`

The temporary real receipts had SHA-256 `real-1=52714e7a6aa9add28e8a5f4356d17ae50751f3d79176fdb0355837148bebdea5`, `real-2=288624eab332820a8fbb90c29d71e408a02517eb21a346ccb7077d22a4148e0b`, and `real-3=8fa93528cb421ecf03f945bf71510bf9f16b57289259b3f07aa814dd863c2c7b`. The v3 four-pin gate stdout/exits above are from the exact path/flag set shown, not inferred from the producer outcome.

## Fake K0 versus real surfaces

The targeted fake-control command was `python3 tests/llamacpp-live/controls.py --tool tools/kama-llamacpp-live.py --gate tests/llamacpp-live/check-receipt.py --probe tools/kama-probe.sh --only k0 --json` in the clone. It exited 0 (`K0_CONTROL_EXIT=0`): K0 classified `accepted`, tool exit 0, gate exit 0, schema v3, receipt outcome `pass`, no failed checks; its receipt SHA-256 was `4b31bc75a6de6ccdc3872a18b0d5ca8a55052e766320a398d09844855fc6ba71`. `controls.py` SHA-256 was `106dd98b60e066a190ee8fea609e5be99c6b2065b9c5a404e14394ce59b6ffc8`.

Semantic comparison of K0’s generated surface (`tests/llamacpp-live/controls.py:276-305,308-382`) with the live receipts:

- **Loading 503:** both use the exact JSON body `{"error":{"message":"Loading model","type":"unavailable_error","code":503}` (body hash above). K0 scripts three `/v1/models` 503s and one `/health` 503; the live runs retained repeated `/v1/models` 503s, and did not record a `/health` 503.
- **`/health`:** K0 and all real captures return 200 with the same semantic body `{"status":"ok"}`.
- **`/v1/models`:** K0 and the real response agree on graded semantics `data[0].id == kama-r18-live` and `owned_by == llamacpp`. They are not byte/whole-shape equivalents: K0 emits only a minimal list/data row, while the real body includes `models`, aliases, tags, architecture, and metadata. The real `created` value varies by run; that timestamp was not used for this semantic comparison. No claim is made that K0 covers the extra fields.
- **`/props`:** alias and `n_ctx=256` match; the real capture also records `is_sleeping=false`. K0’s ungraded `build_info=controls-fake` and `total_slots=1` differ from real `build_info=b11755-704366d76` and `total_slots=4`. The receipt gate grades `model_alias`, not full `/props` equality.
- **`/metrics`:** K0 returns the documented 501 JSON error; the real receipt retains the 501 status only, so a real response-body comparison is unavailable. The gate’s status check passed in all real runs.
- **Probe and teardown:** fake K0 and real runs both classify the matching alias as `MODEL_OK`/`matched`/exit 0 and the mismatch as `MODEL_MISMATCH`/`served-id-mismatch`/exit 2. K0’s gate-valid graceful teardown and each real run’s child-owned graceful close agree at the checked behavior level.

This supports K0 as a detector fixture for the predicates it is meant to exercise, not as an exact emulator of every real response field. The full-body differences above are the main fidelity limit.

## No-loading outcome control

The bounded zero-loading fake control was run separately with `--only k16` (same tool/gate/probe arguments as K0). Its result was `classification=not-evaluated`, receipt schema v3 and outcome `not-evaluated`; `loading_envelope_graded` was the sole null check, producer exit 2, gate exit 3 (`NOT-EVALUATED`), and the targeted null→true gate flip was rejected with gate exit 1. Control command exit was 0. Latest emitted control receipt hash: `6d49610fbab88a03111caaf53dad4ea1bd7fe23c0c1063bc2d0a7c3b1c29ebdd`. This matches KQ24’s explicit rule (`corpus/QUALITY.md:132`): a legitimate unobserved loading property is not-evaluated, not a pass. All three real runs did observe and grade 503 bodies, so their `pass` outcomes were evaluated passes, not vacuous ones.

## Teardown, boundaries, and retained evidence

After all runs, `ps -p 1854353,1867646,1869288 -o pid,stat,comm` showed only its header. `ss -H -ltnp 'sport = :33857'`, `:45201`, and `:42815` each produced no rows; the final check printed `PORT_33857_NO_LISTENER`, `PORT_45201_NO_LISTENER`, `PORT_42815_NO_LISTENER`. This supplements each receipt’s ownership/returncode/port-refusal checks. The real server and model were only read and launched ephemerally; no registered consumer port, systemd, global config, credential, or external service was changed.

No tools were installed or updated. No build, lint, formatter, general test suite, or official counting command was run. The clone and temporary receipts were scratch only and were removed after recording the command, outcomes, hashes, and key observations here. The advice report is the sole retained artifact from this seat; no code or source-evidence files were changed.

Limits: this confirms only the specified llama.cpp b11755 binary, pinned small GGUF, delivered producer/gate revision, and three loopback runs. It says nothing about model quality, vLLM/Ollama, registered-consumer health, service restoration, full JSON-body identity, or any real-runtime zero-loading case. L1 decides whether this corroborates its admission evidence.
