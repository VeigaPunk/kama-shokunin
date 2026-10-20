VERDICT: confirm — independent fake-server reproduction: the frozen C2 pair (tool b8c5e8d4 + gate 6b9576a1) accepts 4 bad shapes green (hb, bl, kill, sigterm1) and its teardown checks pass vacuously on se/hang/t500.

# What I ran

Frozen files copied byte-identical into a scratch lane (frozen-in-place run is
impossible: `tools_kama-llamacpp-live.py:51-54` derives `REGISTRY` from
`SCRIPT.parent.parent`, giving `.ufo/waves/round-17/registry/endpoint-consumers.tsv`
→ `registry-unreadable`, exit 2; sentinel peer confirmed same):

- `/tmp/kama-r17-ProbeSigtermFake/lane/tools/kama-llamacpp-live.py` =
  frozen tool, sha256 `b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4`
- `/tmp/kama-r17-ProbeSigtermFake/check-receipt.py` =
  frozen gate, sha256 `6b9576a13dde1872977a6af4547599a75cf484f37fe6fe0f4f5557349b09ced6`
- `/tmp/kama-r17-ProbeSigtermFake/lane/registry/endpoint-consumers.tsv` =
  lane registry copy (supplies port-refusal set)

Own fixtures (not the C2Controls seat's):
- `bin/fake-server` (stdlib ThreadingHTTPServer, argv `--port`/`--alias`,
  shape token in a scratch file; 2x 503 envelope then ready surfaces),
  sha256 `256f85e2e8eebe3d341f001d769479c3a973567d3ddefe69f0994772376539c9`
- `bin/stub-probe.sh` (`check --port P --expect E --json`; actually GETs
  `/v1/models`, emits `kama-probe/v1` rows), sha256
  `f1fc6d91df7da8f9350297d3af81c61c73e4edbbd84a82b22d5db24eea6b29db`
- `driver.py`, sha256 `c1f07a9c46622e74985b002b0b62c46c2fa267bf12ed95f48341d86ed552daca`
- `fake-model.gguf` 4 KiB random, sha256
  `fbb3ffcca60cedb2ffd27a8cca50db75c5ae38c2ac1c5bbb727de2f6e1b99c75`
- fake in own `bin/` dir so `install_tree` (tool :146-170) hashes only it.

# Results (tool exit / gate exit)

| shape | behaviour | tool | gate | key receipt fact |
|---|---|---|---|---|
| good | documented surfaces | 0 | 0 VALID | 10/10; rc0/sigterm/7ms |
| hb | /health 200 `{"status":"degraded"}` | 0 | 0 VALID | health_ready passed, observed `{"status":200}` |
| bl | 503 body `"Busy"`, code `"503"` string | 0 | 0 VALID | `loading_envelope_exact:false`, no check consumes it |
| se | self-exit rc0 after /health 200 | 2 `pre-captures:child-exited-rc0` | 1 INVALID (setup_error) | teardown_exited **passed**: rc0, sigterm_sent false |
| kill | ignores SIGTERM | 0 | 0 VALID | teardown_exited passed on rc -9, sigkill true, wait 10001ms |
| sigterm1 | SIGTERM→exit 1 | 0 | 0 VALID | teardown_exited passed on rc 1 |
| hang | listens, never answers | 2 ready-timeout | 1 INVALID | teardown_exited+port_closed passed; ownership `unproven` |
| t500 | /health always 500 | 2 ready-timeout | 1 INVALID | teardown_exited+port_closed passed; ownership `child` |

Accepted-bad (tool 0 + gate VALID): **4** — hb, bl, kill, sigterm1. Plus
`se` where teardown checks pass vacuously. `sigterm1` (unclean rc1 on
SIGTERM accepted) is one data point beyond the round-16 review's hb/bl/se/kill.

`se`/`hang`/`t500` receipts are INVALID only via `setup_error`/capture-shape
problems — never via a re-derived check; that matches the gate's design
(complete-run validator) and is recorded as such.

# Evidence anchors

- `tools_kama-llamacpp-live.py:938-939` health_ready = `health_status == 200`; DOC :78-82 says body `{"status":"ok"}`.
- `:1024-1028` teardown_exited = `returncode is not None` (any reapable exit: 0/-9/-15/1, signalled or not).
- `:1029-1032` teardown_port_closed = `port_refuses is True` (vacuous after self-exit/timeout).
- `:921-922` `loading_envelope_exact` recorded; no `_check` reads it.
- Gate `check-receipt.py:53-64` REQUIRED_CHECKS names the same 10; `:177-179` `setup_error` → INVALID.

# Files written (lane)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/drafts/probe-frozen-live-controls.md`
  sha256 `301b85b05583e4905e589abc90b08709f12317130b2f9dbca022c386e63276ee`
- this report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/ProbeSigtermFake.md`

# Design choices

- Shape selected via a scratch file (env vars cannot pass — the harness
  allowlists `CHILD_ENV_KEYS`); one `bin/fake-server` serves all 8 shapes.
- Stub probe actually reads `/v1/models` so `probe_*` checks are honest, not
  canned; emits `declared`/`expected_model_id`/`drift`/`summary.exit` per the
  gate's row contract (`check-receipt.py:561-571`).
- `--ready-timeout 4` (not 60) to keep hang/t500 runs cheap; no behaviour
  difference — readiness polling is time-boxed, not attempt-boxed.
- Ports: harness `bind(:0)` only; used 35651, 39159, 41207, 42681, 45447,
  45471, 45613, 46451 — none registered (8080/34113/registry TSV untouched,
  never requested via `--port`).

# Limitations

- Fake is not llama.cpp: predicates were exercised against synthetic HTTP
  surfaces, not a misbehaving real build (same caveat as r16 review).
- r16's M4 (teardown exception → KeyError → no receipt) needs a patched
  tool, not a fake server; not re-run — frozen tool is untouched and may
  not be modified.
- `se` ownership recorded `null` (verify_live returns None on exited child,
  tool :534-540; L3 in r16 review) — gate flags it, cosmetic only.
- Gate INVALID for se/hang/t500 is by `setup_error`, so the vacuous
  teardown-check passes are only visible inside the receipt, not in exits.

# Cleanup / installs

Post-run `pgrep -af fake-server` empty; `ss -ltnp` shows no used port
listening; no llama-server started. Scratch
`/tmp/kama-r17-ProbeSigtermFake/` removed. Installs: none.
