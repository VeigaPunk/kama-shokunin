# P03UnloadAndExpires — live Ollama v0.40.11 residency, lease format, unload and preload

Round 60, kama lane, wave w1. Seat is advisory: this file reports observations, files and risks; it
does not edit lane source and states no verdict on the lane's claims.

## Provenance (every number below comes from these artifacts)

| Item | Value |
|---|---|
| binary | `~/.local/opt/ollama-v0.40.11/bin/ollama`, sha256 `b0a4becfaf872e3ad5d2e9051244e0dfe55409f03d6e2cd9bd9c34400e201b4c`, `/api/version` → `{"version":"0.40.11"}` |
| fixture | `~/.cache/kama-shokunin/models/stories260K.gguf`, sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`, imported once per run via `FROM <gguf>` |
| run A (host TZ `America/Sao_Paulo`, offset −03:00) | model `kama-1dc061ae9c11:latest`, `OLLAMA_HOST=127.0.0.1:37877`, 18 captures |
| run B (server TZ forced) | `TZ=UTC` and `TZ=Asia/Tokyo`, model `kama-6fb26cd4cebb:latest`, 4 captures each |
| server config (serve.log line 6) | `OLLAMA_KEEP_ALIVE:5m0s`, `OLLAMA_MAX_LOADED_MODELS:0`, `CUDA_VISIBLE_DEVICES:-1 HIP_VISIBLE_DEVICES:-1 GGML_VK_VISIBLE_DEVICES:-1` (CPU only), `OLLAMA_MODELS=<lane-owned scratch>` |
| raw captures | `captures.raw.jsonl.gz` beside this file: 26 records, one JSON object per line, gzipped — route, method, status, content_type, headers, req_body, body, **body_sha256 over the verbatim bytes**, client_ms, t_start_utc |
| readable view | `captures.jsonl`: the same 26 records with two large fields elided for size — the `context` token-id array and any `response` longer than 120 chars, replaced by `<elided n/chars … sha256=…>` markers; each record carries `body_sha256` (verbatim) and `body_stored_sha256` (as stored), and a self-check re-derived all 26 verbatim hashes from the gz file with 0 mismatches |
| ancillary | `evidence/summary.json` (derived notes; strings over 200 chars elided with their sha256), `evidence/serve.log` (server config + GIN access log + scheduler lines), `evidence/serve-UTC.log`, `evidence/serve-Asia_Tokyo.log`, `evidence/run.env`, `evidence/driver.py`, `evidence/run.sh`, `evidence/tzprobe.py`, `evidence/tzrun.sh` |
| self-check | `python3 evidence/reconcile.py <this dir>` re-derives every number quoted below from `captures.raw.jsonl.gz` → 18/18 checks pass, exit 0 (`evidence/reconcile.out`) |

Isolation: each server was started in the same shell invocation that killed its PID; PID from `$!`,
never killed by name. Ports used: 37877 and three ephemeral loopback ports chosen by `bind(('127.0.0.1',0))`;
nothing on 8080/34113/11434. Two `ollama serve` processes visible during the session belong to peers
(`OLLAMA_MODELS=.../P02AliasAndCopy/models`, `.../A08CpuOnlyClaim/models`) and were not touched. After
teardown no listener owned by this seat remained and the scratch dir was removed.

## Capture table (26 rows; body truncated where marked)

Reading column is this seat's one-line reading of that row, not a lane claim.

| # | label | method route | status | content-type | body (trunc) | one-line reading |
|---|---|---|---|---|---|---|
| 1 | version | GET /api/version | 200 | application/json; charset=utf-8 | `{"version":"0.40.11"}` | server is the pinned release |
| 2 | tags-before | GET /api/tags | 200 | application/json; charset=utf-8 | `{"models":[{"name":"kama-1dc061ae9c11:latest",...,"modified_at":"2026-10-27T18:36:25.537428176-03:00","size":1185492,"digest":"8cf91c71...` | model is **available** on disk before any load |
| 3 | ps-before-any-load | GET /api/ps | 200 | application/json; charset=utf-8 | `{"models":[]}` | nothing resident; empty array, not an error |
| 4 | generate-keep-alive-30s | POST /api/generate | 200 | application/json; charset=utf-8 | `{"model":"kama-1dc061ae9c11","created_at":"2026-10-27T21:36:33.566846792Z",...` | cold run: `load_duration`=252 138 068 ns, `total_duration`=7 997 112 810 ns |
| 5 | ps-after-keep-alive-30s | GET /api/ps | 200 | application/json; charset=utf-8 | `{"models":[{"name":"kama-1dc061ae9c11:latest",...,"expires_at":"2026-10-27T18:37:03.576020283-03:00","size_vram":0,"context_length":2048,...` | resident with a 30 s lease; expiry in **server-local** offset |
| 6 | ps-after-keep-alive-30s-repeat | GET /api/ps | 200 | application/json; charset=utf-8 | byte-identical to #5 (`sha256 dca08e51e122…`) | lease end is fixed for the lease, not recomputed per call |
| 7 | generate-keep-alive-0 | POST /api/generate | 200 | application/json; charset=utf-8 | `{"model":"kama-1dc061ae9c11","created_at":"2026-10-27T21:36:38.227033527Z",...` | normal 200 inference response; `load_duration` 623 190 ns (already warm) |
| 8 | ps-after-keep-alive-0-poll-0 | GET /api/ps | 200 | application/json; charset=utf-8 | `{"models":[]}` | **already absent** on the first ps, 0.001 ms after the response was read |
| 9 | ps-after-keep-alive-0-settled | GET /api/ps | 200 | application/json; charset=utf-8 | `{"models":[]}` | still absent 500 ms later |
| 10 | generate-reload-before-stop | POST /api/generate | 200 | application/json; charset=utf-8 | `{"model":"kama-1dc061ae9c11","created_at":"2026-10-27T21:36:44.247315645Z",...` | cold again: `load_duration`=252 645 769 ns ⇒ the keep_alive 0 unload was real, not a hidden map entry |
| 11 | ps-before-stop | GET /api/ps | 200 | application/json; charset=utf-8 | `…"expires_at":"2026-10-27T18:41:44.265972746-03:00"…` | default lease (no `keep_alive` sent) = 300 s |
| 12 | ps-after-ollama-stop-poll-0 | GET /api/ps | 200 | application/json; charset=utf-8 | `{"models":[]}` | absent 0.007 ms after `ollama stop` exited 0 |
| 13 | generate-empty-prompt-no-key | POST /api/generate | 200 | application/json; charset=utf-8 | `{"model":"kama-1dc061ae9c11","created_at":"2026-10-27T21:36:44.554318398Z","response":"","done":true,"done_reason":"load"}` | preload form: `done_reason":"load"`, **no** `load_duration`/`total_duration` keys; 254.063 ms client-side |
| 14 | ps-after-empty-prompt | GET /api/ps | 200 | application/json; charset=utf-8 | `…"expires_at":"2026-10-27T18:41:44.554379448-03:00"…` | preload does load: resident, lease = created_at + 300.000061 s |
| 15 | generate-empty-prompt-empty-string | POST /api/generate | 200 | application/json; charset=utf-8 | `{"model":"kama-1dc061ae9c11","created_at":"2026-10-27T21:36:44.555679067Z","response":"","done":true,"done_reason":"load"}` | `{"model":N,"prompt":""}` behaves identically, 0.789 ms (warm) |
| 16 | ps-after-empty-string | GET /api/ps | 200 | application/json; charset=utf-8 | `…"expires_at":"2026-10-27T18:41:44.555744457-03:00"…` | second preload **re-stamped** the lease (+1.36 ms) |
| 17 | generate-final-keep-alive-0 | POST /api/generate | 200 | application/json; charset=utf-8 | `{"model":"kama-1dc061ae9c11","created_at":"2026-10-27T21:36:49.358630393Z",...` | warm run (546.95 µs server-side per GIN log) before final unload |
| 18 | ps-final | GET /api/ps | 200 | application/json; charset=utf-8 | `{"models":[]}` | clean end state |
| 19 | B UTC gen-ka20 | POST /api/generate | 200 | application/json; charset=utf-8 | `{"model":"kama-6fb26cd4cebb","created_at":"2026-10-27T21:38:49.828487306Z",...` | run B, `keep_alive:"20s"` |
| 20 | B UTC ps | GET /api/ps | 200 | application/json; charset=utf-8 | `…"expires_at":"2026-10-27T21:39:09.838817785Z"…` | `TZ=UTC` server renders expiry with `Z` |
| 21 | B UTC tags-after-stop | GET /api/tags | 200 | application/json; charset=utf-8 | `{"models":[{"name":"kama-6fb26cd4cebb:latest",...,"modified_at":"2026-10-27T21:38:45.064666063Z",...` | after stop the model is still **available** in tags |
| 22 | B UTC ps-after-stop | GET /api/ps | 200 | application/json; charset=utf-8 | `{"models":[]}` | and not resident |
| 23 | B Tokyo gen-ka20 | POST /api/generate | 200 | application/json; charset=utf-8 | `{"model":"kama-6fb26cd4cebb","created_at":"2026-10-27T21:38:55.004669907Z",...` | same fixture, `TZ=Asia/Tokyo` server |
| 24 | B Tokyo ps | GET /api/ps | 200 | application/json; charset=utf-8 | `…"expires_at":"2026-10-28T06:39:15.013156099+09:00"…` | **same field, different offset** (+09:00) for the same UTC instant |
| 25 | B Tokyo tags-after-stop | GET /api/tags | 200 | application/json; charset=utf-8 | `…"modified_at":"2026-10-28T06:38:50.43894203+09:00"…` | `modified_at` follows the same server-local rendering |
| 26 | B Tokyo ps-after-stop | GET /api/ps | 200 | application/json; charset=utf-8 | `{"models":[]}` | and not resident |

## Residency timeline and timings (run A)

| t (UTC) | event | evidence | number |
|---|---|---|---|
| 21:36:25.53 | import done, ps before any generate | #3 | `{"models":[]}` at 0.38 ms |
| 21:36:33.57 | generate, `keep_alive:"30s"`, cold | #4 | `load_duration` 252.1 ms, `total_duration` 8.00 s, `eval_count` 20480 |
| 21:36:33.58 | ps | #5 | resident; `expires_at` − `created_at` = **30.009 s**; `expires_at` − client now = **29.999 s** |
| 21:36:33.83 | ps again | #6 | byte-identical body (lease stable) |
| 21:36:38.23 | generate, `keep_alive:0` | #7 | warm `load_duration` 0.62 ms |
| +0.001 ms | ps | #8 | `{"models":[]}` — absent on the **first** ps after the response |
| 21:36:44.25 | next generate | #10 | `load_duration` 252.6 ms ⇒ fresh cold load, unload was genuine |
| 21:36:44.27 | ps | #11 | resident, `expires_at` − `created_at` = **300.019 s** (no `keep_alive` sent ⇒ default 5 m) |
| 21:36:44.28 | `ollama stop NAME` | #12 | CLI exit **0**, 28.36 ms, empty stdout, stderr = ANSI control bytes only |
| +0.007 ms | ps | #12 | `{"models":[]}` |
| 21:36:44.55 | generate `{"model":N}` (preload) | #13 | 200, `done_reason:"load"`, body keys `[created_at, done, done_reason, model, response]` — **no timing fields** |
| 21:36:44.55 | ps | #14 | resident, `size_vram` 0, `context_length` 2048, lease = created_at + 300.000061 s |

`/api/ps` latency on this host: 0.17–1.41 ms (26 samples, GIN log agrees: 12–41 µs server-side).

## `expires_at`: format and clock semantics

Observed shape, four samples, all with 9 fractional digits:

```
2026-10-27T18:37:03.576020283-03:00   keep_alive 30s   (server TZ America/Sao_Paulo)
2026-10-27T18:41:44.265972746-03:00   default          (same server)
2026-10-27T21:39:09.838817785Z        keep_alive 20s   (server TZ=UTC)
2026-10-28T06:39:15.013156099+09:00   keep_alive 20s   (server TZ=Asia/Tokyo)
```

- It is RFC 3339, nanosecond precision, rendered in the **server process's local offset**. The offset
  is not fixed to `Z`: forcing the server TZ changed the same field from `-03:00` to `Z` to `+09:00`
  for the same lease mechanism (rows 5, 20, 24). Row 24's `06:39:15.013+09:00` and row 20's
  `21:39:09.838Z` differ by 20 s of lease, not by a different instant family; both were
  `created_at + keep_alive + ~10 ms`.
- Lease length = the requested `keep_alive` (`30s` → +30.009 s, `20s` → +20.008/+20.010 s) and
  300 s when the field is absent (server default `OLLAMA_KEEP_ALIVE:5m0s`).
- `expires_at` − `created_at` is `keep_alive` + 8–19 ms for inference requests and +61 µs on the
  preload path; a second preload moved the lease by +1.36 ms, so **every accepted request re-stamps
  the lease** rather than the value being fixed at load time.
- The value is stable while the lease is untouched (rows 5 and 6 are byte-identical).
- Comparing it with a clock therefore requires an offset-aware parse. A lexical compare of
  `expires_at` against a UTC "now" is wrong by the server offset — 3 h in run A, 9 h in the Tokyo run.
  [INFERENCE] the offset is `time.Local` of the server process (host `/etc/localtime` was
  `America/Sao_Paulo`, and `env -i` leaves `TZ` unset); I did not instrument the Go source to confirm
  the variable.

## Comparison with the lane's statements (no verdict; each reading names its capture)

**S1 — `corpus/knowledge/ollama-evidence-replay.md:40`:** "`expires_at` ("Time when the model will be
unloaded") is **never** compared with a clock".

- Verifiable part: neither lane tool reads the field — `grep -c "expires_at" tools/kama-ollama-evidence.py
  tools/kama-ollama-live.py` → `0`, `0`, exit 1. Only `tools/round60-c2-counter.py:9,39` mentions it,
  as a population-selection regex. So "the replay never evaluates it" holds for the shipped tools.
- Observation it does not carry: the field **is** clock data. It is an absolute RFC 3339 instant,
  equal to `created_at + keep_alive` within 8–19 ms, whose offset is the server's local offset
  (rows 5, 20, 24). Rows 8–9 show the complementary fact: when the lease ends at 0, residency is
  gone before the next ps.
- Calibration risk: a reader of that row can infer the field is inert or unparseable. The narrow true
  statement is "the replay must not use it"; the usable measurement is "it is comparable to a clock
  only after offset normalization, and its offset varies with the server's TZ".

**S2 — `corpus/knowledge/ollama-evidence-replay.md:20`:** "`available_not_loaded` means only that the
expected name is *absent from the supplied ps capture* (and present in the supplied tags capture)".

- Confirmed on live data, and quantified. Row 2 vs row 3: the imported model is in `/api/tags` with a
  digest while `/api/ps` is `{"models":[]}` before any generate. Row 21 vs row 22 and row 25 vs row 26:
  after `ollama stop`, tags still lists the model (digest `8cf91c71…`) and ps is empty. Row 8: ps is
  empty 0.001 ms after a `keep_alive:0` response — absence is not "never loaded", because row 10 then
  paid a fresh 252.6 ms cold load.
- The observation strengthens the lane's gloss rather than contradicting it: absence from one ps
  sample is exactly what the server says, and the same model remains available.

**S3 — `corpus/knowledge/ollama-evidence-replay.md:23-24`:** "Capture times, same-instant capture and
same-daemon origin are all unknown and are not validated".

- The capture-level claim is true of the lane's inputs, but the server does stamp per-entry absolute
  time into both bodies: `expires_at` in ps (rows 5, 20, 24) and `modified_at` in tags (rows 2, 21, 25),
  in the same server-local rendering. A consumer that keeps the bodies could therefore bound an entry's
  lease; "unknown" is a property of the lane's export contract, not of the wire format.

## Further calibration details observed

- **Name echo is not normalized.** Request `{"model":"kama-1dc061ae9c11"}` and the response body echo
  both use the bare name (#4, #13), while `/api/ps` and `/api/tags` report `kama-1dc061ae9c11:latest`
  (#5, #2). An exact-name match of the *request* string against a ps export fails without `:latest`
  normalization.
- **The preload form carries no timing fields.** #13/#15 return
  `{"model":…,"created_at":…,"response":"","done":true,"done_reason":"load"}` — no `load_duration`,
  no `total_duration`, no `context`. The 254 ms cold load is visible only client-side (and in the GIN
  log, 253.75 ms). A caller who wants load timing from the preload route cannot get it from the body.
- **`size` is not comparable across routes.** tags `size` = 1 185 492 (disk), ps `size` = 6 312 427
  (resident), for the same digest `8cf91c71…`.
- **Unload is process-level.** The GIN/scheduler log shows a new `llama-server` child (ports 38235 →
  44569 → 35481) after each unload, which is why the next cold generate costs the full ~252 ms.
- `/api/ps` on a CPU-only server still reports `size_vram: 0` and `context_length: 2048`; neither is a
  readiness signal, both are present.

## Not observed (marked [INFERENCE] or out of scope)

- [INFERENCE] behaviour at the *end* of a lease without an intervening request: I unloaded explicitly
  (`keep_alive:0`, `ollama stop`) and did not wait out a 30 s/300 s lease. A wall-clock expiry was not
  measured.
- Not observed: other Ollama versions, GPU placement, concurrent-model eviction, streaming responses,
  multi-model `/api/ps` ordering.
- [INFERENCE] the fitting of `expires_at − created_at` to "lease stamped after response construction";
  only the interval was measured.

## Teardown

Each run killed the PID it started in the same shell invocation (`trap 'kill $PID' EXIT` for run A,
explicit `kill $PID; wait $PID` in `tzrun.sh` for run B); the four loopback listeners this seat created
are gone, the peer servers on 33657/33475 were left running, and `/fast/scratch/hyaku/kama-r60/P03UnloadAndExpires`
was removed after `captures.jsonl`, `evidence/` and this file were copied out.
