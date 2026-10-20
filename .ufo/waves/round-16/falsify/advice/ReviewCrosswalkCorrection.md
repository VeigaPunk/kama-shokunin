VERDICT: partial — §Correction — round 16 (served-identity-crosswalk) versus lines 27-60 and S036/S037 at 704366d76.

The correction's central code citations are accurate: `/v1/models` is gated by the
503 `Loading model` middleware while `is_ready` is false, and the pre-routing order
matches S036; `is_ready` is set after `load_model` in single-model mode, matching
S037. The note is nevertheless partial: one sentence preserves a blanket
"model-list match is not readiness" claim that its own gate contradicts for the
exact direct single-model case it corrects; the defect predates b11755 and was
already present at the table row's own c0fd7862 pin; and the refuted premise
survives unlisted at four other places in the same entry.

## What I ran (all read-only; no service started, no probe run)

Working root: `/home/vgpnk/Projects/shokunin/kama-shokunin`.

1. `git log --oneline -3` and `git diff HEAD~1 -- corpus/knowledge/served-identity-crosswalk.md`
   — exit 0. The round-16 change is a pure EOF append (15 lines, 136-149); no
   original line or header was edited.
2. `sha256sum .ufo/waves/round-16/sources/llama.cpp-704366d/{README.md,server-http.cpp,server.cpp}`
   — exit 0. Hashes `714c067b…`, `24ede172…`, `21439622…` match the raw sha256
   cells of `corpus/SOURCES.md` rows S035, S036, S037 respectively.
3. `curl` raw.githubusercontent.com at `c0fd7862…` `tools/server/server-http.cpp`
   — exit 0, HTTP 200, 37318 bytes; sha256 `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb`.
   `diff -q` against the 704366d pinned copy — exit 0 (byte-identical).
4. `curl` raw.githubusercontent.com at `c0fd7862…` `tools/server/server.cpp`
   — exit 0, HTTP 200, 23352 bytes; sha256 `cebd9a75…`. Its single-model branch
   starts the listener at 475, calls `load_model` at 488, and sets
   `ctx_http.is_ready.store(true)` at 496.
5. `awk` line-numbered reads of the pinned `server-http.cpp` — exit 0:
   308 `if (!is_ready.load()) {`; 309-311 frontend-asset exemption; 314-325
   `503` body with `"message", "Loading model"`, `"type", "unavailable_error"`,
   `"code", 503`; 354 state gate before 357 API-key check; 242-248 frontend set
   is `/` plus embedded UI assets only.
6. `awk` line-numbered reads of the pinned `server.cpp` — exit 0:
   router branch 455 `ctx_http.start()`, 460 `is_ready.store(true)`, 472
   `models.load_startup_models()`; single-model branch 494 start, 507
   `load_model`, 514 `routes.update_meta`, 515 `is_ready.store(true)`.
7. `awk` line-numbered reads of the pinned `README.md` — exit 0: 1258
   "`meta` field can be `null` (for example, while the model is still loading)";
   2337 sleep unloads the model from RAM; 2341-2345 exempt routes `/health`,
   `/props`, `/models`, `/metrics`; 247 `--sleep-idle-seconds` default `-1`.
8. `curl` raw.githubusercontent.com at 704366d `tools/server/server-context.cpp`
   — exit 0, HTTP 200, 264205 bytes. `get_models` at 5725-5735 uses
   `create_response(true)` and returns `cached_models` when
   `queue_tasks.is_sleeping()`; `update_cached_responses` builds it at 6301-6308.
9. `python3 -c` over `.ufo/waves/round-16/sources/pins.json` — exit 0. The
   manifest lists four files: README.md, server-common.cpp, server-common.h,
   server-http.cpp. It does not list server.cpp (S037's file) or
   server-context.cpp.
10. `nl`/`grep` on `corpus/knowledge/served-identity-crosswalk.md` lines
    9, 13, 27, 33, 50, 52, 63, 136-149 and `corpus/README.md:119` — exit 0.

## Findings

### F1 (high) — the preservation sentence is contradicted by the gate it just cited

`served-identity-crosswalk.md:146-148` says:

> The conclusion that a model-list match is not readiness still holds, for other
> reasons: router-mode catalog entries carry per-model `status` values, and a
> sleeping server answers `/v1/models` from cache.

In the exact mode the note addresses — single-model, direct `llama-server` at
704366d — `is_ready` is the same flag checked by `middleware_server_state`
(`server-http.cpp:308`, declared `std::atomic<bool> is_ready = false` in
`server-http.h:71`). The gate returns 503 for every non-frontend GET, and
`is_ready` becomes true only after `load_model` returns and `routes.update_meta`
runs (`server.cpp:507-515`). [INFERENCE from the code path] Therefore, on a
direct single-model server, a 200 `/v1/models` answer is only served after the
model finished loading; the gate itself makes a `MODEL_OK` match evidence that
load completed and the server's readiness flag is set. The note's blanket "not readiness" is true only for the
two fallback cases it names, and neither covers this mode:

- router-mode status values are on `GET /models` (README:2059-2095), not the
  probe's `GET /v1/models` (README:2026: only loaded-model info is forwarded);
- the sleeping cache is opt-in: `--sleep-idle-seconds` defaults to `-1`
  (disabled, README:247). It is a real exception (verified at
  `server-context.cpp:5725-5735`), but it is not the default direct mode.

The note should say what a 200 does prove here (the `is_ready` gate opened and
`load_model` returned) and narrow, rather than preserve verbatim, line 52's
"never establishes loaded weights" and line 9's "not that weights are loaded".
As written, the note removes the mid-load example but keeps an absolute claim
that the cited code refutes for its own mode.

### F2 (medium) — the defect predates b11755; the table's own pin already gated

`served-identity-crosswalk.md:27` labels the row `llama.cpp single-model (S001
@c0fd7862)`. At c0fd7862, `server-http.cpp` is byte-identical to the 704366d
copy (same sha256 `24ede172…`; `diff -q` exit 0), so the same 503 gate existed
at the row's own pin. c0fd7862 `server.cpp` has the same order: listener start
475, `load_model` 488, `is_ready` 496. The note's "At llama.cpp 704366d76
(b11755) …" is true for that commit, but its framing implies a build-specific
defect and does not say the row's premise was already unreachable at the pin it
cites. The correction should state both commits (identical middleware; same
ordering) so the table row is not left looking valid at c0fd7862.

### F3 (medium) — the refuted premise survives in unnamed lines, including line 27 inside 27-60

The note names only lines 33, 50 and 52 (`served-identity-crosswalk.md:138-139`).
The same premise remains live at:

- line 9 (Claim): "llama.cpp's `/v1/models` reports … but can answer while that
  model is still loading" — directly refuted by the 503 gate;
- line 13 (Prior coverage): "What is new here: … llama.cpp `/v1/models`
  answering while loading (S001)" — this is the entry's novelty claim and is now
  false at both 704366d and c0fd7862; the note does not retire it;
- line 27 (Crosswalk table, inside the attacked 27-60 range): the cell still
  presents `meta` null while loading as the documented response, with an
  `[INFERENCE]` conclusion that now needs the replacement reasons;
- line 63 (§kama use): "on llama.cpp single-model it can be observed before
  loading completes (S001)" — an operational instruction that the probe now
  contradicts with `MODEL_LOADING` (drift, exit 2).

Because the entry is append-only and the note enumerates its affected lines, a
reader who lands on line 9, 13, 27 or 63 has no pointer to the correction.
`corpus/README.md:119` also still advertises "llama.cpp nullable loading
metadata" as the entry's coverage; the round-16 index section lists
`served-identity-crosswalk.md` as an appended correction (`corpus/README.md:213`)
but the coverage row is unchanged. At minimum line 13 (novelty) and line 63
(operational use) should be named; line 27 is in the declared 27-60 range and
should be too.

### F4 (low-medium) — the sleeping-cache clause has no registered source or pin

The note's second fallback reason ("a sleeping server answers `/v1/models` from
cache") is code-verifiable at 704366d [INFERENCE from the code path] —
`get_models` uses `create_response(true)` and returns `cached_models` when
sleeping (`server-context.cpp:5725-5735`; `update_cached_responses` at
6301-6308) — but S036 and S037 cover
`server-http.cpp` and `server.cpp` only, and `server-context.cpp` has no
`SOURCES.md` row. `.ufo/waves/round-16/sources/pins.json` lists four files and
omits it (and also omits `server.cpp`, S037's file, despite the committed copy
matching S037's raw sha256). A reader of the note cannot reach this fact from
its citations. Either add a source row plus a pinned copy (with digest), or drop
the clause: the router `/models` status point already supplies the `/models`
fallback, and F1 needs the direct-mode qualification rather than this extra
unsourced one.

### F5 (low) — the round-16 section has no provenance trio

Unlike `endpoint-identity.md`'s round-16 correction (`endpoint-identity.md:184-186`:
`source:`, `verified-at:`, `recheck:`), the served-identity correction is a bare
H2 section. The entry header (`served-identity-crosswalk.md:1-3`) still declares
only S001 @c0fd7862, S016, S010, S011, S012 and S031 in `source:`, and its
`recheck:` line names only S001/S010 list pages; the new S035/S036/S037 code
rows are not represented. This is a provenance/consistency gap (KQ3/KQ6/KQ11
surface), not a false statement: the inline citations are present, but the
document-level source and recheck metadata no longer describe what the file now
relies on.

### Residual note (not a defect of this correction)

S036's wording "Every non-frontend path … answers 503" is not literally every:
`server-http.cpp:347-352` short-circuits `OPTIONS` before the state gate. The
correction's `GET /v1/models` claim is unaffected; this is a source-row
precision nit only.

## Limitations

- No live `llama-server` was started and no live 503 was captured. The lane's
  own round-16 index says the tiny model loads in about 8 ms and no 503 was
  captured by the receipt (`corpus/README.md:214-216`). The 503 statement is a
  code read supported by S036/S037, not a runtime observation.
- The c0fd7862 `server.cpp` copy was fetched read-only from raw GitHub into
  `/tmp/kama-r16-ReviewCrosswalkCorrection/`; it is not manifest-pinned in the
  lane, so its byte identity rests on the recorded sha256 in this report.
- I did not run `tests/probe-verdicts/check.py` or `measure.py`; the probe branch
  was inspected at `tools/kama-probe.sh:503-507` (`MODEL_LOADING` after the
  401/403 rules, before the HTML/model-array rules), consistent with
  `endpoint-identity.md:184-213`.
- Installs: none.

Report: .ufo/waves/round-16/falsify/advice/ReviewCrosswalkCorrection.md
