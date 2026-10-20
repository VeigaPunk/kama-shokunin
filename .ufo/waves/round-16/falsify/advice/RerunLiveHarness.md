VERDICT: confirm — C2 live-llamacpp-lifecycle harness reproduces; independent re-run yields VALID receipt with all 10 checks byte-identical to the L1 receipt.

## What I ran

1. `python3 tools/kama-llamacpp-live.py --server ~/.local/opt/llama-b11755/llama-server --model ~/.cache/kama-shokunin/models/stories260K.gguf --model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --alias kama-stories260k --out /tmp/kama-r16-RerunLiveHarness/receipt.json` → exit 0.
2. `python3 tests/llamacpp-live/check-receipt.py /tmp/kama-r16-RerunLiveHarness/receipt.json --expect-model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` → exit 0, output `VALID /tmp/kama-r16-RerunLiveHarness/receipt.json`.
3. `pgrep -x llama-server` → exit 1 (no processes) both before and after the run. `ss -tlnp | grep -E '8080|34113'` → no listeners.

## Receipt comparison vs `.ufo/waves/round-16/live/receipt.json`

- **checks**: same 10 ids, all fields (`id`, `passed`, `observed`, `documented_by`) identical for every check — `ALL 10 CHECKS IDENTICAL`.
- **probe**: identical sha256 `6edd3c4cfdf3f86c98202cef58859c29406d4a9cec17495454c514ac5972fa50`, same path.
- **server.sha256**: identical `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` (b11755 binary).
- **model**: identical path + sha256 `270cba1b…d256d`.
- **argv, port_refusal_set, child_env_keys, pdeathsig, probes**: identical after scrubbing only the ephemeral port.
- **transitions**: 3 vs 3, same shape; only diff is `t_ms` 1→2 on the two pre-listen refused probes — timing noise.
- **captures**: `/health` byte-identical (body_sha256 `a29ee2b1…d288`); `/models` body differs only in `"created"` epoch (1792504178 → 1792504418, i.e. server start time); `/props` parsed `fields` identical (build `b11755-704366d76`, n_ctx 256, alias, slots 4), body_sha256 differs only because the raw body embeds a timestamp [INFERENCE — raw body not stored, but `fields` and `Content-Length: 2070` match exactly].
- **teardown**: `sigterm_sent: true`, `sigkill_sent: false`, `returncode: 0`, `port_refuses: true` — clean lifecycle, matching baseline shape.
- **port**: 35771 vs 32845 — expected; tool picks a free unregistered port (`port_listener_ownership: "child"` both runs).
- **loading_observed**: `false` in both — stories260K loads faster than the first poll; the MODEL_LOADING path is covered by the stub matrix, not expected live.

## Limitations

- Single re-run; the harness's own `port_pick_note` acknowledges a sub-second bind(:0) collision race — not exercised.
- `loading_observed: false` means the live run does not exercise the new 503 "Loading model" envelope path; that verdict branch is only proven by the 17 stub rows + frozen-probe separability receipt, not by this harness run.
- /tmp scratch receipt removed after diffing; digests above are the retained evidence.

## Installs

None.
