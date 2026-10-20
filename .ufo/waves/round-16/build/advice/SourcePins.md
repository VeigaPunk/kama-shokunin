# SourcePins — round 16 advisory

## Files written
- `.ufo/waves/round-16/sources/pin.py` — urllib-only fetcher; read-only GETs, no line numbers hardcoded (all located by string search).
- `.ufo/waves/round-16/sources/llama.cpp-704366d/{README.md,server-http.cpp,server-common.cpp,server-common.h}` — pinned upstream sources.
- `.ufo/waves/round-16/sources/pins.json` — url, sha256, bytes, located line ranges per file.

Commit pinned: `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (llama.cpp b11755 tag commit).

## sha256 / bytes / located ranges

| file | sha256 | bytes | located |
|---|---|---|---|
| `tools/server/README.md` | `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37` | 119661 | `### GET /health` section: lines 479–490; `Body: {"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}` line: **486** |
| `tools/server/server-http.cpp` | `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb` | 37318 | `auto middleware_server_state` block: lines **307–328** (`};` at 328); 503 response body construction at 314–325; `return false` at 325 |
| `tools/server/server-common.cpp` | `b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442` | 75061 | `case ERROR_TYPE_UNAVAILABLE` lines: **[119]**; every `ERROR_TYPE_UNAVAILABLE` use: **[119]** (only occurrence in file; `type_str = "unavailable_error"` / `code = 503` on lines 120–121) |
| `tools/server/server-common.h` | `ee401cf81ed0fb515f9870b018c762074903e72712dcb81a652e49761fe1577b` | 25525 | every `ERROR_TYPE_UNAVAILABLE` use: **[65]** (enum member declaration `ERROR_TYPE_UNAVAILABLE, // custom error` inside `enum error_type` at 59–68) |

## Claim-relevant evidence (verified against pinned bytes)
- `server-http.cpp:307-328`: while `!is_ready.load()`, every non-`frontend_paths` request gets `res.status = 503` with JSON `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` — matches C1 description exactly (claim cited 307–325; full lambda including closing `};` runs to 328).
- `README.md:485-487` documents the same 503 body as "the model is still being loaded" under `### GET /health`.
- `server-common.cpp:119-122` maps `ERROR_TYPE_UNAVAILABLE` → `"unavailable_error"`, code 503 — the same type string used by other 503s (e.g. "no slot available"), so the `message == "Loading model"` check is required to distinguish MODEL_LOADING.
- Note: `server-http.cpp` itself contains no `ERROR_TYPE_UNAVAILABLE` token uses (its 503 is a literal JSON construction, not the error_type path).

## Notes / limitations
- Fetch is network-dependent; rerun of `pin.py` overwrites pins deterministically (same commit → same bytes → same sha256/ranges).
- `located` uses 1-based inclusive line numbers on `\n`-split text.
- "every `ERROR_TYPE_UNAVAILABLE` use" recorded per fetched file where present (README has none; server-http.cpp has none).
- No tools installed; stdlib `urllib` only. No lane gates/harnesses run.
