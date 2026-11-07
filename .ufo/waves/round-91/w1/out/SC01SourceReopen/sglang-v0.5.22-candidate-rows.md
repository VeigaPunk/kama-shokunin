# SGLang v0.5.22 candidate threshold rows (SC01SourceReopen)

Candidate rows only — NOT appended to `SKILL.md` or `corpus/SOURCES.md`.
Every candidate below was graded with the frozen counter's own `grade()` function
(`tools/round91-threshold-rows.py`, imported read-only) against a locally built
`SOURCES` map carrying the sha256 below; `bound=1` means the row satisfies the
frozen rules B1–B7 as written.

Tag `v0.5.22` exists upstream (`git ls-remote --tags https://github.com/sgl-project/sglang` →
`35ce313293052f8362e0829e7512bc9bc3d336c9 refs/tags/v0.5.22`, peeled commit
`baa9befa381511cd4d56f83980951e5a45fffc6d`). Every URL below was fetched live and its
bytes are identical to the same path fetched at the peeled commit and to the
`v0.5.22` release tarball (`sglang-0.5.22.tar.gz`, sha256
`9b946c6433c6b1467cd7e5b83951c1e12c84a0bb2cd05646b71e4f4a39772bc6`).

## Path correction (read this before writing any S row)

`python/sglang/srt/arg_groups/server_args.py` does **not** exist at v0.5.22 (HTTP 404).
The real layout is:

- `python/sglang/srt/server_args.py` — exists (35396 bytes, sha256 `d1b9ffc79edcbc857efd02a47d47eed9b414f8ac44bc4e3214d78a7922e90e03`).
  It is the loader/CLI-registration module; it holds **no** port or timeout defaults itself
  (it re-exports the `arg_groups` dataclass fields).
- `python/sglang/srt/arg_groups/fields/serving.py` — the HTTP `host`/`port` defaults.
- `python/sglang/srt/arg_groups/fields/device.py` — the watchdog defaults.
- `python/sglang/srt/environ.py` — the env-var defaults (`EnvInt`/`EnvFloat`).
- `python/sglang/srt/entrypoints/http_server.py` — the startup/health/warmup timeouts.

Each distinct file needs its own `SOURCES` row (one URL + one sha256 per row).

## Proposed SOURCES rows (for the L1 to append, tier A, status `mined`)

| id | file | sha256 | located quote (<= 25 words) | line |
|---|---|---|---|---|
| S596 | `python/sglang/srt/arg_groups/fields/serving.py` | `66a9ab458053c31290f21d9b7ce6686c7a9d83e6387f2a12a61a0e5599ff4923` | `port: A[int, "The port of the HTTP server."] = 30000` | 66 |
| S597 | `python/sglang/srt/environ.py` | `80017ce7326d2af4d331518f1c3a3d24f1a379c8193f59b2ffabd54017c21441` | `SGLANG_TIMEOUT_KEEP_ALIVE = EnvInt(5)` | 337 |
| S598 | `python/sglang/srt/entrypoints/http_server.py` | `a89d20bb2fa8a86c511ab4d9d054f74d707423ab220f733ff25e62fcc0e49979` | `WAIT_WEIGHTS_READY_TIMEOUT = int(os.getenv("SGLANG_WAIT_WEIGHTS_READY_TIMEOUT", 120))` | 208 |
| S599 | `python/sglang/srt/arg_groups/fields/device.py` | `4bb4b4e2999358946c510a3fd6d56c1bbbf5f1c2972c5cda8cd57e4f5595cdd7` | `watchdog_timeout: A[` / `] = 300` (name line 66, value line 69) | 66–69 |

Raw URLs (all at tag `v0.5.22`):

- https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/arg_groups/fields/serving.py
- https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/environ.py
- https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py
- https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/arg_groups/fields/device.py
- https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/server_args.py

## Candidate rows (SKILL.md shape: `| T<nn> | engine pin | threshold | value | S<nnn> | line | `literal` | decision |`)

Engine cell `sglang v0.5.22` satisfies the frozen B4 rule: pin token `v0.5.22` occurs in
every URL and the engine word `sglang` occurs in every lower-cased URL.

| id | engine pin | threshold | value | source | line | literal | probe decision | graded |
|---|---|---|---|---|---|---|---|---|
| T15 | sglang v0.5.22 | default HTTP listen `port` (`--port`) | 30000 | S596 | 66 | `port: A[int, "The port of the HTTP server."] = 30000` | a unit started without `--port` listens on 30000; a registry row for this engine on another port must cite the `--port` or `SGLANG_PORT` it was started with | bound=1 |
| T16 | sglang v0.5.22 | default HTTP host `host` (`--host`) | 127.0.0.1 | S596 | 65 | `host: A[str, "The host of the HTTP server."] = "127.0.0.1"` | the server binds loopback by default; a unit reachable only from another host was started with an explicit `--host` | bound=1 |
| T17 | sglang v0.5.22 | idle HTTP keep-alive `SGLANG_TIMEOUT_KEEP_ALIVE` | 5 s | S597 | 337 | `SGLANG_TIMEOUT_KEEP_ALIVE = EnvInt(5)` | the server closes an idle kept-alive connection after 5 s; a client that reuses one later gets a reset and must reconnect, which is not a server fault | bound=1 |
| T18 | sglang v0.5.22 | startup weights-ready wait `SGLANG_WAIT_WEIGHTS_READY_TIMEOUT` | 120 s | S598 | 208 | `WAIT_WEIGHTS_READY_TIMEOUT = int(os.getenv("SGLANG_WAIT_WEIGHTS_READY_TIMEOUT", 120))` | the API server gives up waiting for weights 120 s after start; a listener still not ready inside that window is loading, outside it failed startup | bound=1 |
| T19 | sglang v0.5.22 | startup health-check timeout `SGLANG_HEALTH_CHECK_TIMEOUT` | 20 s | S598 | 207 | `HEALTH_CHECK_TIMEOUT = int(os.getenv("SGLANG_HEALTH_CHECK_TIMEOUT", 20))` | the startup health check gives up after 20 s; a slow first answer inside that window is loading, not dead | bound=1 |
| T20 | sglang v0.5.22 | uvicorn worker healthcheck `SGLANG_UVICORN_WORKER_HEALTHCHECK_TIMEOUT` | 10 s | S597 | 340 | `SGLANG_UVICORN_WORKER_HEALTHCHECK_TIMEOUT = EnvInt(10)` | the supervisor pings each worker every 10 s; a worker that answers nothing for far longer is a stall to report | bound=1 |
| T21 | sglang v0.5.22 | warmup timeout `SGLANG_WARMUP_TIMEOUT` | -1 (unset) | S597 | 324 | `SGLANG_WARMUP_TIMEOUT = EnvFloat(-1)` | unset means "no explicit warmup deadline"; the warmup request then uses the 600 s fallback (see T22), not this value | bound=1 |
| T22 | sglang v0.5.22 | warmup request timeout `warmup_timeout` | 600 s | S598 | 2420 | `timeout=warmup_timeout if warmup_timeout > 0 else 600,` | the warmup request that precedes the first answer is bounded at 600 s by default; a longer warmup needs the env var, and the timeout is the engine's, not the probe's | bound=1 |
| T23 | sglang v0.5.22 | crash watchdog `watchdog_timeout` (`--watchdog-timeout`) | 300 s | S599 | 66–69 | (name on 66, value on 69 — see note) | a forward batch longer than 300 s crashes the server instead of hanging; a request that stops answering past that is a server-side crash to report, not a slow answer | **not bindable** |

## The watchdog row cannot be expressed under the frozen counter (read before deciding)

`device.py` declares the field across four lines:

```
66:    watchdog_timeout: A[
67:        float,
68:        "Set watchdog timeout in seconds. If a forward batch takes longer than this, the server will crash to prevent hanging.",
69:    ] = 300
```

The frozen B6 rule wants the literal to be a substring of **one** line, and B7 wants the
backticked parameter name to occur in that same literal. Neither holds for any single
line here, and the counter grades both single-line attempts as unbound:

- line 69 literal `] = 300` → `why=name-not-in-literal`
- line 66 literal `watchdog_timeout: A[` → `why=value-not-in-literal`

The generated CLI docs (`docs/docs/advanced_features/server_arguments.mdx`) split the same
way: `--watchdog-timeout` on line 736, the value `300` on line 738.

So a watchdog row needs either a counter change (multi-line literal, or a "value on line N
of the same declaration" rule) or a different, single-line source. This is the only
SGLang default I could not turn into a frozen-bindable row; it is the "watchdog timeout"
the seat asked for, so it is flagged here rather than silently dropped.

## Semantic notes for the reviewer (K2 read) — not counted by the counter

- `port` 30000 is the dataclass default; `get_serving().port` is what the uvicorn bind
  uses (`http_server.py` 2713/2738/2781/2822). `SGLANG_PORT` (`environ.py` 370) is a
  different variable (TCPStore), not the HTTP port.
- `SGLANG_TIMEOUT_KEEP_ALIVE` is consumed as `timeout_keep_alive=` for uvicorn at
  `http_server.py` 2742, 2785 and 2845 — the keep-alive reading is direct.
- `SGLANG_WAIT_WEIGHTS_READY_TIMEOUT` is read by `_wait_weights_ready()`
  (`http_server.py` 2518–2536), which polls once a second and logs
  "Weights are not ready after waiting … seconds" — a startup wait, not a request timeout.
- `HEALTH_CHECK_TIMEOUT` is read in the startup health-check loop (`http_server.py` 763).
- The warmup 600 s fallback is the non-disaggregated branch; the disaggregated branch
  uses 1800 s (`http_server.py` 2433).
