# Frozen-harness fake-server control runs (independent C2 "before" reproduction)

Seat: KamaR17.ProbeSigtermFake-2. Independent of the C2Controls seat: own
minimal fake `llama-server` + own stub probe, both written fresh in
`/tmp/kama-r17-ProbeSigtermFake/` (removed after the report).

## Method

Because the FROZEN tool resolves `REGISTRY`/`DEFAULT_PROBE` relative to
`SCRIPT.parent.parent` (`tools_kama-llamacpp-live.py:51-54`), running it in
place under `.ufo/waves/round-17/frozen/` fails `registry-unreadable` before
launch. The frozen tool was therefore copied **byte-identical**
(sha256 `b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4`,
== the frozen file) into `/tmp/kama-r17-ProbeSigtermFake/lane/tools/` beside a
copy of `registry/endpoint-consumers.tsv`; the FROZEN gate copy is likewise
byte-identical (`6b9576a13dde1872977a6af4547599a75cf484f37fe6fe0f4f5557349b09ced6`).

Per run:
```
python3 <tmp>/lane/tools/kama-llamacpp-live.py \
    --server <tmp>/bin/fake-server --model <tmp>/fake-model.gguf \
    --model-sha256 fbb3ffcca60cedb2ffd27a8cca50db75c5ae38c2ac1c5bbb727de2f6e1b99c75 \
    --alias fakealias --probe <tmp>/bin/stub-probe.sh \
    --ready-timeout 4 --out <tmp>/runs/<shape>.receipt.json
python3 <tmp>/check-receipt.py <receipt>
```

Fake server (`/tmp/kama-r17-ProbeSigtermFake/bin/fake-server`, sha256
`256f85e2e8eebe3d341f001d769479c3a973567d3ddefe69f0994772376539c9`): stdlib
`ThreadingHTTPServer`, parses `--port`/`--alias` from argv, serves 2x 503 +
envelope on `/v1/models` then `{"data":[{"id":<alias>,"owned_by":"llamacpp"}]}`,
`200 {"status":"ok"}` on `/health`, `200` props with `model_alias`, `200 []`
slots, `501` metrics, SIGTERM -> `exit(0)`; per-shape deviations below.

Stub probe (`/tmp/kama-r17-ProbeSigtermFake/bin/stub-probe.sh`, sha256
`f1fc6d91df7da8f9350297d3af81c61c73e4edbbd84a82b22d5db24eea6b29db`): honours
`check --port P --expect E --json` and actually GETs `/v1/models`; emits a
`kama-probe/v1` row (`declared`, `expected_model_id`, `verdict`, `reason`,
`served_model`, `drift`) — an honest probe, so `probe_*` checks are meaningful.

Model: 4 KiB `/dev/urandom` file (only its sha256 matters; the fake ignores
`-m`). Driver `/tmp/kama-r17-ProbeSigtermFake/driver.py` sha256
`c1f07a9c46622e74985b002b0b62c46c2fa267bf12ed95f48341d86ed552daca`.

## Results (frozen tool exit / frozen gate exit / checks)

| shape | fake behaviour | tool exit | gate exit | receipt evidence |
|---|---|---|---|---|
| `good` | documented surfaces, SIGTERM->rc0 | **0** | **0 VALID** | 10/10 passed; teardown `rc 0, sigterm true, sigkill false, wait 7ms` |
| `hb` | `/health` 200 `{"status":"degraded"}` | **0** | **0 VALID** | 10/10; `health_ready` passed, observed `{"status":200}` — body never graded |
| `bl` | first `/v1/models` 503 body `{"message":"Busy",...,"code":"503"}` (string code) | **0** | **0 VALID** | 10/10; `loading_observed true`, `loading_envelope_exact false` — **no check consumes the field** |
| `se` | `/health` 200 then `os._exit(0)` before captures | **2** `pre-captures:child-exited-rc0` | 1 INVALID (17 problems, `setup_error`) | `teardown_exited` **passed** with `rc 0, sigterm_sent false, wait 0ms` — nothing was terminated |
| `kill` | SIGTERM ignored | **0** | **0 VALID** | 10/10; teardown `rc -9, sigterm true, sigkill true, wait 10001ms`; `teardown_exited` passed on a SIGKILL |
| `sigterm1` | SIGTERM -> `exit(1)` | **0** | **0 VALID** | 10/10; teardown `rc 1, sigterm true, sigkill false` — an unclean exit code accepted |
| `hang` | listens, never answers | **2** `ready-timeout` | 1 INVALID (17 problems) | `teardown_exited`+`teardown_port_closed` passed (`rc -15`); ownership `unproven` |
| `t500` | `/v1/models` 200 instantly, `/health` always 500 | **2** `ready-timeout` | 1 INVALID (16 problems) | `teardown_exited`+`teardown_port_closed` passed; ownership `child` |

## Accepted-bad count (frozen pair, this seat)

Green-complete runs whose subject behaviour should have failed a check:
`hb`, `bl`, `kill`, `sigterm1` = **4** (tool exit 0, gate VALID, 10/10).
Plus one partial-accept: `se` (tool exit 2, but `teardown_exited` and
`teardown_port_closed` both passed on a run where the child exited by
itself — the checks are vacuous on failed runs). Gate-side only `se`/`hang`/
`t500` receipts are INVALID, and only because `setup_error`/capture-shape
problems, not because any check re-derived the misbehaviour.

Differs from round-16 review only in one extra data point (`sigterm1`):
round-16 demonstrated hb, bl, se, kill; this run independently reproduces
all four and adds that a `returncode: 1` on harness SIGTERM also passes.

## Specific fail-open evidence vs the C2 repair spec

1. `health_ready` grades status only — `tools_kama-llamacpp-live.py:938-939`
   (`health_status == 200`); DOC at :78-82 documents body `{"status":"ok"}`.
   `hb` proves a 200 `{"status":"degraded"}` yields tool 0 / gate VALID.
2. `teardown_exited` = `returncode is not None` — :1024-1028. `se` (rc 0,
   `sigterm_sent false`), `kill` (rc -9 after SIGKILL), `sigterm1` (rc 1) all
   pass. Any reapable exit satisfies it.
3. `teardown_port_closed` = `port_refuses is True` — :1029-1032. Vacuous in
   `se` (port released by the self-exit, no signal sent).
4. `loading_envelope_exact` computed at :922 but no `_check` consumes it;
   `bl` recorded `false` yet exited 0 / gate VALID.
5. (Latent, not re-run here) teardown-exception escape — r16 M4 KeyError at
   :1021->:1026.

## Hygiene

Ports used (harness bind(:0), all ephemeral, none in
`registry/endpoint-consumers.tsv` or the 8080/34113 pins): 35651, 39159,
41207, 42681, 45447, 45471, 45613, 46451. Post-run: `pgrep -af fake-server`
empty; `ss -ltnp` shows none of the 8 ports listening. No llama-server was
started. Scratch `/tmp/kama-r17-ProbeSigtermFake/` removed after the report.
