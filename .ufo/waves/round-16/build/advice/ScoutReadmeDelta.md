# ScoutReadmeDelta — S001 pin vs b11755 (`tools/server/README.md`)

**Seat:** leaf scout (read-only). **Axes:** calibration (7, lowest) + operability.
**Question:** every semantic difference between llama.cpp `tools/server/README.md` at
`704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (b11755) and the S001 pin
`c0fd78626405c6d9b934efef0ec7291fcc20e3d6`, for `GET /health`, `GET /v1/models`, `GET /props`,
`GET /slots`, `GET /metrics`.

**Headline:** **zero semantic differences in the five named sections — they are byte-identical.**
The whole file differs by **+2 lines and one changed cell**, both in the *Server-specific params* table,
outside the five sections.

## Method (reproducible)

Fetched both blobs from `raw.githubusercontent.com` at the exact SHAs, plus the tag blob:

| Artifact | URL | Lines | sha256 |
|---|---|---|---|
| pin c0fd7862 | `.../c0fd78626405c6d9b934efef0ec7291fcc20e3d6/tools/server/README.md` | 2400 | `ad0dbc023796480d96f551c5eee69cd1c48c216d964409eea1cc9054c083ca23` |
| new 704366d7 | `.../704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md` | 2402 | `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37` |
| tag b11755 | `.../b11755/tools/server/README.md` | 2402 | `714c067b…75a6a37` (identical to the commit blob) |

```bash
diff -u pin.md new.md     # => exactly 2 hunks (@@ -208,6 +208,8 @@ and @@ -235,7 +237,7 @@), 20 lines
diff <(sed -n '479,$p' new.md) <(sed -n '477,$p' pin.md)   # => empty: byte-identical to EOF
```

`git ls-remote https://github.com/ggml-org/llama.cpp 'refs/tags/b11755*'` →
`704366d76f8748cf9ad3df62a464bfcc8d1ae6ad	refs/tags/b11755`; commit date `2026-10-20T11:02:05Z`.
Pin commit date `2026-10-17T15:20:51Z` (GitHub API, both observed 2026-10-20 -03).

## Per-section result (all identical)

Slice hashes are over the exact section bodies (heading through the line before the next `###`); the
column shows the first 12 hex digits of the sha256, and the pin and new values are **identical** in
every row (verified with `cmp`, not just prefix equality).

| Section | pin lines | new lines | slice sha256 prefix (pin = new) | Representative quote |
|---|---|---|---|---|
| `GET /health` | 477–489 | 479–491 | `b9a260db8f67` | "the model is still being loaded." (pin:485 / new:487) |
| `GET /props` | 837–932 | 839–934 | `2f947815166e` | "By default, it is read-only." (pin:839 / new:841) |
| `GET /slots` | 981–1128 | 983–1130 | `718bb62caa74` | "If query param `?fail_on_no_slot=1` is set, this endpoint will respond with status code 503" (pin:985 / new:987) |
| `GET /metrics` | 1129–1154 | 1131–1156 | `bda217ef7924` | "This endpoint is only accessible if `--metrics` is set." (pin:1131 / new:1133) |
| `GET /v1/models` | 1252–1311 | 1254–1313 | `e3adffe06b9a` | "The returned list always has one single element." (pin:1256 / new:1258) |

(`cmp` per pair returned equal for all five; `POST /props` at pin:933–940 / new:935–942 is inside the
same identical tail and is likewise unchanged.)

## The two real changes (out of scope, but they move every line number)

1. **New flags added** — `--connect`, `--connect-code`, inside *Server-specific params* after the
   `--ui` row (pin:210 / new:210):
   - new:211 "`--connect` | (experimental) open a peer-to-peer tunnel for server using llama-connect (default: disabled)"
   - new:212 "`--connect-code CODE` | manually specify a 40-character code for --connect"
   - Pure insertion; pin:211 `--embedding, --embeddings` maps to new:213.

2. **One cell changed** — `--reasoning-preserve` default:
   - pin:238 "…not just the last assistant message (**default: enabled**)"
   - new:240 "…not just the last assistant message (**default: template default**)"
   - This is a genuine semantic change (preservation is no longer unconditionally on), but it sits in the
     options table, not in any of the five endpoint sections. `grep` of lane `corpus/`, `README.md`,
     `SCORECARD.md` and `MINT.md` finds **no** reference to `reasoning-preserve`, `--connect-code`, or the
     flag `--connect`; the only `--connect*` hits are unrelated `curl --connect-timeout` invocations
     (`corpus/knowledge/endpoint-identity.md:59,68,70,88,105`). No lane artifact depends on either row.

**Line-number mapping:** for content at or after the insertion, `new = pin + 2`. Every S001 anchor in the
five sections therefore shifts by exactly +2; e.g. the corpus-cited `meta`-null quote pin:1256 → new:1258,
`id`/`--alias` pin:1282 → new:1284, `owned_by` pin:1298 → new:1300, loading body pin:484 → new:486,
`/slots` 503 pin:985 → new:987, `/metrics` pin:1131 → new:1133.

## What this means for C1 (calibration) and the probe verdict

- **C1's citation is exact and survives.** new:486 documents the loading branch verbatim:
  `{"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}` with the note at
  new:487 "the model is still being loaded." The README's `code` is the integer `503`; L1's observed wire
  body `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` is the same object
  with different key order. Nothing here licenses matching on key order or on a stringified code.
- **The README documents this body for `/health` only.** The `/v1/models` section documents no 503 at
  all: new:1258 says "The `meta` field can be `null` (for example, while the model is still loading)" — a
  200-path shape. So `MODEL_LOADING` graded on a `/v1/models` 503 is grounded in `server-http.cpp`, **not**
  in this README. A README-citing justification for the new verdict would overstate the source.
  [INFERENCE] The `meta:null` wording most plausibly describes the router's `/models` listing
  (per-model `status`) or a post-ready state; it does not describe single-model `/v1/models` mid-load.
- **A second 503 exists and its body is undocumented.** new:987: "If query param `?fail_on_no_slot=1` is
  set, this endpoint will respond with status code 503". The README never states that body, so the
  exact matcher's `message == "Loading model"` equality is the *only* discriminator guarding against a
  no-slot 503 that otherwise shares `type`/`code`. Keep message equality exact (no prefix/substring).
- **`/metrics` disabled status is undocumented.** new:1133 says only "only accessible if `--metrics` is
  set" — no status code. L1's observed `501` is therefore uncontradicted by the README (the README's
  other `501`s, new:1837, belong to `/v1/systemone`).
- **`/health` public-ness is unchanged:** pin:479 / new:481 "This endpoint is public (no API key check)."
  (relevant to the middleware-order seat; not re-verified against code here.)

## Limitations

- Documentation-only comparison. No claim made here about wire behavior beyond L1's stated smoke
  observation; source-level checks (`server-http.cpp`, `ERROR_TYPE_UNAVAILABLE`) belong to the other seats.
- No LSP applies: both targets are remote Markdown blobs; literal `read`/`grep`/`diff` plus slice hashes
  are the evidence. GitHub Contents API was not needed; the Commits API answered (no 403 this run).
- Only the two fetched SHAs were compared; intermediate commits were not enumerated, so "first commit
  that introduced either change" is not established.
- Installs/upgrades this run: none.
