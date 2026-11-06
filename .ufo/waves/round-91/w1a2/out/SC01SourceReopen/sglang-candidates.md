# SGLang v0.5.22 threshold candidates (round 91 w1a2, seat SC01SourceReopen)
# CANDIDATE ROWS ONLY — not appended to SKILL.md, not added to corpus/SOURCES.md.
# tag v0.5.22 verified upstream: refs/tags/v0.5.22 = 35ce313293052f8362e0829e7512bc9bc3d336c9
# (annotated tag -> commit baa9befa381511cd4d56f83980951e5a45fffc6d)
# fetched 2026-11-06T20:41:36-03:00; host load at fetch: load average: 32.46, 32.78, 23.96

## Source files (raw URLs, sha256 of fetched bytes, git blob sha at the tag)

python/sglang/srt/arg_groups/fields/serving.py
  raw URL : https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/66a9ab458053c31290f21d9b7ce6686c7a9d83e6387f2a12a61a0e5599ff4923
  sha256  : 13638
  bytes   : 
python/sglang/srt/arg_groups/fields/device.py
  raw URL : https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/4bb4b4e2999358946c510a3fd6d56c1bbbf5f1c2972c5cda8cd57e4f5595cdd7
  sha256  : 3576
  bytes   : 
python/sglang/srt/server_args.py
  raw URL : https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/d1b9ffc79edcbc857efd02a47d47eed9b414f8ac44bc4e3214d78a7922e90e03
  sha256  : 35396
  bytes   : 
python/sglang/srt/environ.py
  raw URL : https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/80017ce7326d2af4d331518f1c3a3d24f1a379c8193f59b2ffabd54017c21441
  sha256  : 113688
  bytes   : 
python/sglang/srt/entrypoints/http_server.py
  raw URL : https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/a89d20bb2fa8a86c511ab4d9d054f74d707423ab220f733ff25e62fcc0e49979
  sha256  : 110718
  bytes   : 
python/sglang/srt/utils/watchdog.py
  raw URL : https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/55fa2c9afe8999abbb0b4d0f0aa31a33f935870838b220ac35f85d63b0228cf7
  sha256  : 7018
  bytes   : 

## Candidate rows (8-cell SKILL.md shape: id | engine pin | threshold | value | source | line | literal | decision)

S15 | sglang v0.5.22 | default listen `port` of the SGLang HTTP server (`--port`) | 30000 | S596 | 66 | `port: A[int, "The port of the HTTP server."] = 30000` | a unit started without `--port` listens on 30000, not 8080: a registry row pinning 8080 for such a unit is port drift (`DEAD` on 8080), not a model fault; read the port from the unit argv

  literal line 66 of python/sglang/srt/arg_groups/fields/serving.py:
        port: A[int, "The port of the HTTP server."] = 30000

S16 | sglang v0.5.22 | forward-batch watchdog `watchdog_timeout` (`--watchdog-timeout`) | 300 s | S597 | 69 | `] = 300` | a forward batch that takes longer than 300 s trips the hard watchdog and the server crashes to avoid hanging; a slow decode inside 300 s is not a watchdog event

  NOTE for the L1: the watchdog default is split across lines 66-69 of the same file
    66:     watchdog_timeout: A[
    67:         float,
    68:         "Set watchdog timeout in seconds. If a forward batch takes longer than this, the server will crash to prevent hanging.",
    69:     ] = 300
    the only single line carrying BOTH the parameter name and the value is line 69 (`] = 300`),
    which does NOT contain the token 'watchdog_timeout' -> counter B7 (threshold-name token must
    also occur in the literal) would NOT bind a row whose literal is only line 69.
    The name lives on line 66, the value on line 69. A row citing line 66 with literal
    `watchdog_timeout: A[` would fail B2 (value token 300 not in the literal).
    => the hard watchdog default is NOT directly bindable by the frozen counter's B1-B7 as written;
    it needs a one-line source (e.g. the CLI registration) or a counter change (out of scope here).

S17 | sglang v0.5.22 | startup health-check timeout `HEALTH_CHECK_TIMEOUT` (`SGLANG_HEALTH_CHECK_TIMEOUT`) | 20 s | S598 | 207 | `HEALTH_CHECK_TIMEOUT = int(os.getenv("SGLANG_HEALTH_CHECK_TIMEOUT", 20))` | the `/health` probe gives up after 20 s of the server not answering; a listener inside that window that does not answer is still starting

  literal line 207 of python/sglang/srt/entrypoints/http_server.py:
    HEALTH_CHECK_TIMEOUT = int(os.getenv("SGLANG_HEALTH_CHECK_TIMEOUT", 20))

S18 | sglang v0.5.22 | startup weights-ready wait `WAIT_WEIGHTS_READY_TIMEOUT` (`SGLANG_WAIT_WEIGHTS_READY_TIMEOUT`) | 120 s | S599 | 208 | `WAIT_WEIGHTS_READY_TIMEOUT = int(os.getenv("SGLANG_WAIT_WEIGHTS_READY_TIMEOUT", 120))` | the server waits up to 120 s for weights to become ready at startup; a listener not ready inside that window has failed startup, inside it read it as loading

  literal line 208 of python/sglang/srt/entrypoints/http_server.py:
    WAIT_WEIGHTS_READY_TIMEOUT = int(os.getenv("SGLANG_WAIT_WEIGHTS_READY_TIMEOUT", 120))

S19 | sglang v0.5.22 | idle HTTP keep-alive `SGLANG_TIMEOUT_KEEP_ALIVE` | 5 s | S600 | 337 | `SGLANG_TIMEOUT_KEEP_ALIVE = EnvInt(5)` | the server closes an idle kept-alive connection after 5 s; a client that reuses one later gets a reset and must reconnect, which is not a server fault

  literal line 337 of python/sglang/srt/environ.py:
        SGLANG_TIMEOUT_KEEP_ALIVE = EnvInt(5)
  (applied to uvicorn at python/sglang/srt/entrypoints/http_server.py:2742 and :2845)

## Startup/keep-alive timeout search — what was checked
  python/sglang/srt/arg_groups/ (84 .py files fetched at the tag): only timeout-ish fields are
  grpc_response_timeout_secs (serving.py:87-91, 300 s, gRPC-only), dist_timeout (parallel.py:29-30),
  elastic_ep_scale_timeout (exec_.py:915-916), weight_cache_timeout (model.py:392),
  dynamic_batch_tokenizer_batch_timeout (serving.py:303-305).
  python/sglang/srt/server_args.py: no timeout field of its own (it composes the dataclasses).
  The two startup waits (HEALTH_CHECK_TIMEOUT, WAIT_WEIGHTS_READY_TIMEOUT) live in
  python/sglang/srt/entrypoints/http_server.py, and the keep-alive default in
  python/sglang/srt/environ.py.

## Tag existence (git ls-remote --tags)
  https://github.com/sgl-project/sglang   refs/tags/v0.5.22    35ce313293052f8362e0829e7512bc9bc3d336c9
  https://github.com/sgl-project/sglang   refs/tags/v0.5.22^{} baa9befa381511cd4d56f83980951e5a45fffc6d
