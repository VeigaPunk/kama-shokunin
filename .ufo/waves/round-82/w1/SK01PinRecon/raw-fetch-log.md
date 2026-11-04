# SK01 raw fetch log — round 82 w1 (2026-11-04)

Seat: `SK01PinRecon` (scout, read-only). Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Base revision `aaf974dbd3b6adb2ef914dc7293cda92b4e05551`; lane tip read at seat start
`git -C <lane> rev-parse master` → `bacae0726d7c53455bd083bc6d478bbcd6e7fffc`.
Scratch root `S=/fast/scratch/hyaku/kama-r82/SK01PinRecon` (deleted at yield; every artifact below was
copied into `./artifacts/` first). Local clock 2026-11-04T10:07–10:11 -0300.

No production file was written. No git/jj mutation was run. No sibling repo was read.

---

## 1. `tools/pin-watch.py check` — as specified, and as it actually runs

### 1a. Exactly as the dispatch and `corpus/knowledge/pin-recheck-trigger.md:5` print it

```
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/pin-watch.py check --repo /home/vgpnk/Projects/shokunin/kama-shokunin
exit=2
stdout: (empty)
stderr:
usage: pin-watch.py check [-h] --pins PINS [--tags-dir TAGS_DIR]
pin-watch.py check: error: the following arguments are required: --pins
```

Receipt: `artifacts/pinwatch-as-specified.err` (137 bytes).
The tool's parser (`tools/pin-watch.py`, `main()`) defines only `check --pins PINS [--tags-dir TAGS_DIR]`
and `selftest`; there is no `--repo` option anywhere in the file. `check --help` prints the same two options.

### 1b. Correct invocation

```
$ cd /home/vgpnk/Projects/shokunin/kama-shokunin
$ python3 tools/pin-watch.py check --pins registry/engine-pins.tsv
exit=1
engine=sglang pin=v0.5.22 newest=v0.5.23 newer=1 status=behind
engine=vllm pin=v0.32.0 newest=v0.33.0 newer=1 status=behind
engine=llama.cpp pin=b11755 newest=b12110 newer=280 status=behind
pins=3 current=0 behind=3 missing=0 error=0
```

Receipt: `artifacts/pinwatch-check.out` (234 bytes); wall time 1.37 s, network used (`--tags-dir` not named).
Output order is `registry/engine-pins.tsv` file order (sglang, vllm, llama.cpp), not the relations-register order.

**Proof the pin-watch read was live and not the committed tag list**: `newest=b12110` for llama.cpp does not
exist in `.ufo/waves/round-80/measured/after/c2-tags/llama.cpp.txt`, whose maximum `b(\d+)` release tag is
`b12103`. §5 below isolates exactly the two tags that appeared.

Shape against the recorded freshness arm: SCORECARD.md's freshness row records
`pins=3 current=0 behind=3 missing=0 error=0`; this run reproduces that line shape and exit 1. Only the
numbers inside the per-engine lines moved.

---

## 2. Fetch receipt table (every row is a fetch this seat performed)

All requests `curl -sS -L --max-time 90/120`; status is HTTP; bytes and sha256 are of the received body.

| # | document | ref (URL suffix) | HTTP | bytes | sha256 | lines |
|---|---|---|---|---|---|---|
| 1 | llama.cpp `tools/server/README.md` | `b11755` | 200 | 119661 | `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37` | 2402 |
| 2 | llama.cpp `tools/server/README.md` | `b12103` | 200 | 136429 | `eafc1b53abd787613d13d1fb9a86a1fc9f90b59f1240b3eeb88c85ea08d9a137` | 2620 |
| 3 | llama.cpp `tools/server/README.md` | `b12110` (actual newest) | 200 | 136429 | `eafc1b53abd787613d13d1fb9a86a1fc9f90b59f1240b3eeb88c85ea08d9a137` | 2620 |
| 4 | llama.cpp `tools/server/README.md` | `39febd2adb947b70da35e95f9351b3bf58ad170a` (relation row 2) | 200 | 135608 | `8fd5abde2fb52de3b30f30a170631d4c0d92febecc8da44d0541e48b132b35c6` | 2616 |
| 5 | SGLang `docs/docs/basic_usage/native_api.mdx` | `v0.5.22` | 200 | 17359 | `209087c3d30dc25cbcdb3b8a31b0453089d83e0fdfa39d317ab54646787e11eb` | — |
| 6 | SGLang `docs/docs/basic_usage/native_api.mdx` | `v0.5.23` (newest) | 200 | 18295 | `3ed171186990d6a67a1d950f1d491fe83986cf539bf24d1e65b95481e7d87a3c` | — |
| 7 | SGLang `python/sglang/srt/entrypoints/http_server.py` | `v0.5.23` (newest) | 200 | 119569 | `d5d7ae6c5e8f403f9a46617377ab96977d9d4f1f263c0b90fc9fd2769eef061e` | — |
| 8 | vLLM `docs/design/prefix_caching.md` | `v0.32.0` | 200 | 13916 | `67ee4e2b7bc23d40e9b366e4a9053ae4ecd0925ddef51f412ac5c16b9dc83a61` | — |
| 9 | vLLM `docs/design/prefix_caching.md` | `v0.33.0` (newest) | 200 | 13916 | `67ee4e2b7bc23d40e9b366e4a9053ae4ecd0925ddef51f412ac5c16b9dc83a61` | — |

Byte-identity results (`cmp -s`):
- `b12103` vs `b12110` README → **identical** (so the anchor state at the actual newest tag is exactly the
  anchor state at the register's `newest` cell).
- `v0.32.0` vs `v0.33.0` prefix-caching page → **identical**.
- `b11755` vs `b12103` README → differ (15 hunks; §4).
- SGLang `native_api.mdx` v0.5.22 vs v0.5.23 → differ (2 hunks; §6).

Cross-check against the lane's existing rows: #1 and #2 re-derive S564's and S563's recorded sha256 and byte
counts exactly (S564: 119661 B `714c067b…`, 2402 lines; S563: 136429 B `eafc1b53…`, 2620 lines), so this
seat's fetches are the same bytes the lane already cites. #4 re-derives S555's `8fd5abde…` / 135608 B.

Source identification for SGLang and vLLM came from the lane's own rows, as the item requires:
- `corpus/SOURCES.md:214` (S328) names `docs/docs/basic_usage/native_api.mdx` at `v0.5.22`; the relation
  register's newest SGLang tag is `v0.5.23`, so #5/#6 are that file at its own ref and at the newest tag.
- `corpus/SOURCES.md:222` (S363) names the vLLM prefix-caching design page at the `v0.32.0` docs line; the
  register's newest vLLM tag is `v0.33.0`, so #8/#9 are that file at both.
- `corpus/SOURCES.md:215` (S329) names the SGLang `http_server.py` route/deprecation row; #7 rechecks it.

---

## 3. `/health`, `/props`, `/slots` heading lines (exact `grep -n` output)

`grep -n '^#\{2,4\} .*\(/health\|/props\|/slots\|/v1/health\)'`

b11755:
```
479:### GET `/health`: Returns health check result
839:### **GET** `/props`: Get server global properties.
935:### POST `/props`: Change server global properties.
983:### GET `/slots`: Returns the current slots processing state
1157:### POST `/slots/{id_slot}?action=save`: Save the prompt cache of the specified slot to a file.
1177:### POST `/slots/{id_slot}?action=restore`: Restore the prompt cache of the specified slot from a file.
1197:### POST `/slots/{id_slot}?action=erase`: Erase the prompt cache of the specified slot from a file.
```

b12103 (= b12110, identical bytes):
```
480:### GET `/health`: Returns health check result
930:### **GET** `/props`: Get server global properties.
1027:### POST `/props`: Change server global properties.
1075:### GET `/slots`: Returns the current slots processing state
1249:### POST `/slots/{id_slot}?action=save`: Save the prompt cache of the specified slot to a file.
1269:### POST `/slots/{id_slot}?action=restore`: Restore the prompt cache of the specified slot from a file.
1289:### POST `/slots/{id_slot}?action=erase`: Erase the prompt cache of the specified slot from a file.
```

39febd2a: `2197:### GET `/models`: List available models` (relation row 2's own ref).

`/v1/health` is not a heading at either ref; it appears only inside the `/health` prose
("This endpoint is public (no API key check). `/v1/health` also works."), at b11755:481 / b12103:482.

The `/health` section body, b11755 479-490 and b12103 480-491, is **byte-identical** apart from its line
offset. The held quote is line 481 (b11755) / 482 (b12103).

---

## 4. `diff -u` b11755 → b12103 (server README only)

`diff -u llama-b11755-README.md llama-b12103-README.md` → exit 1, 27509 bytes, 15 hunks.
Receipt: `artifacts/server-readme-b11755-b12103.diff`.

Hunk → document section (section = nearest preceding `#{2,4}` heading in the old file):

| hunk (old lines) | section at the hunk | touches health/readiness? |
|---|---|---|
| `@@ -230,6 +230,7 @@` | `### Server-specific params` (159) | no — adds `--models-memory-margin` option row |
| `@@ -563,7 +564,7 @@` | `### POST /completion` (492) | no — `dry_sequence_breakers` gains a "64 distinct breakers" clause |
| `@@ -771,37 +772,127 @@` | `### POST /embedding` (749) | no — +90 lines of embedding docs |
| `@@ -926,9 +1017,10 @@` | `### GET /props` (839) | **adjacent** — adds a `voices` bullet; `chat_template_caps` gains `reasoning_effort_levels`. `default_generation_settings` and `total_slots` untouched |
| `@@ -1262,11 +1354,12 @@` | `### GET /v1/models` (1254) | **adjacent** — "One output value is special" → "Some output values are special"; adds `audio`; the `meta` can be `null` sentence untouched |
| `@@ -1373,6 +1466,7 @@` | `### POST /v1/chat/completions` (1345) | no — video-soundtrack bullet |
| `@@ -1491,12 +1585,78 @@` | `### POST /v1/chat/completions/control` (1478) | no — adds `### WebSocket /v1/realtime` section |
| `@@ -1527,7 +1687,8 @@` | `### POST /v1/responses` (1494) | no |
| `@@ -1649,6 +1810,8 @@` | `### POST /v1/messages` (1630) | no |
| `@@ -1669,7 +1832,8 @@` | `### POST /v1/messages` (1630) | no |
| `@@ -1725,13 +1889,17 @@` | `### POST /v1/systemone` (1703) | no |
| `@@ -1760,6 +1928,8 @@` | `### POST /v1/systemone` (1703) | no |
| `@@ -1990,8 +2160,44 @@` | `### Routing requests` (1969) | **adjacent** — WS `/v1/realtime` model-param sentence + new `### Memory-based unloading` subsection; `--no-models-autoload` and the `/props?model=` example are context (unchanged) |
| `@@ -2025,7 +2231,7 @@` | `### GET /models` (1995) | **adjacent** — the paragraph after note 2 gains an `audio` clause; note 1 and the "not running" bullet are context lines (unchanged) |
| `@@ -2242,6 +2448,18 @@` | `### GET /models/sse` (2179) | **adjacent** — adds a `model_memory` event example |

**No hunk lies in the `/health` section.** The section spans old 479-490; the previous hunk ends at old 233
and the next begins at old 560 (three context lines above old 563). A `## API Endpoints` heading and the
whole `/health` block are therefore untouched: no readiness *statement* is reworded, added or removed.

The `/props` and `/v1/models` hunks change *fields documented in those sections*, not readiness semantics:
`total_slots` (the `/props` readiness-adjacent bullet) and the `meta: null` while-loading sentence both
survive verbatim. The `### Routing requests` hunk adds a memory-based unloading policy for the router
(`--models-memory-margin`); it changes neither `is_ready` ordering nor any probe response.

---

## 5. Tag-list drift since the register's own receipt (why `newest`/`newer` no longer match)

Register receipt (cited by all five rows): `.ufo/waves/round-80/measured/after/c2-tags/llama.cpp.txt`,
sha256 `a2de12bed05a81e08aeaf6dff51a40e0f092ad67bf1551007a36e37f893134fa`, 8364 lines, max release tag `b12103`.

This seat's live `git ls-remote --tags https://github.com/ggml-org/llama.cpp.git`:
sha256 `000418f525d4d03c7631d256ab459d78e09b6154f3b034769c31f9e4e88d1e19`, 8368 lines.

`diff -u` (receipt: `artifacts/llama-tags-r80-vs-now.diff`, 929 bytes, +5/-1 with headers):
```
+13ec8f614cfef964fe97bbf872bc436dbc484a1f	refs/tags/b12109
+cd959bae99ff4bed22bef2604f45241c09bbb8c8	refs/tags/b12110
+c4261a74a59c5a719e8f73038e28633b08f2bea4	refs/tags/v0.9.0
+cd959bae99ff4bed22bef2604f45241c09bbb8c8	refs/tags/v0.9.0^{}
```
So: exactly two new build tags and one new annotated `v0.9.0` tag appeared; `b12110` and `v0.9.0^{}` are the
same commit `cd959bae…`. **`b12104`–`b12108` were never published** — the numbering skips, which is why
`newest` advanced by 7 nominally but `newer` advanced by only 2.

Consequence for the register (not a defect — it is the documented `dated`/`receipt` design): the
`newest`/`newer` cells reproduce their own committed receipt exactly; they are stale only against *today's*
upstream. Values this seat observed:

| ref | register newest/newer | today newest/newer | delta |
|---|---|---|---|
| llama.cpp `b11755` | `b12103` / 278 | `b12110` / 280 | +2 tags |
| llama.cpp `39febd2a` (tag `b11963`) | `b12103` / 110 | `b12110` / 112 | +2 tags |
| llama.cpp `b7200` | `b12103` / 3395 | `b12110` / 3397 | +2 tags |
| sglang `v0.5.22` | `v0.5.23` / 1 | `v0.5.23` / 1 | none |
| vllm `v0.32.0` | `v0.33.0` / 1 | `v0.33.0` / 1 | none |

sglang and vllm tag lists are byte-identical to their round-80 receipts
(`882d7946…`, 192 lines; `5406e20a…`, 230 lines — both re-hashed here and unchanged), so rows 4 and 5 need
no numeric movement at all.

`refs/tags/b11963` is a lightweight tag pointing directly at
`39febd2adb947b70da35e95f9351b3bf58ad170a` (no `^{}` line), confirming the relation row 2 label `tag:b11963`.
`refs/tags/b7200` is `ab49f094d29057b2c4d2b0f1e822c9140df1b0e1`.

---

## 6. Do the statements the lane holds at `b11755` still exist at `b12103`?

Mechanical test: take each anchor line verbatim from `b11755`, look the identical trimmed line up in
`b12103`. 21 of 21 anchors are present; verdicts below.

| row | anchor | b11755 | b12103 | verdict |
|---|---|---|---|---|
| S564 | `### GET /health` heading | 479 | 480 | holds (line shift) |
| S564 | "This endpoint is public (no API key check). `/v1/health` also works." | 481 | 482 | holds, byte-identical |
| S035 | 503 body `{"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}` | 486 | 487 | holds |
| S035 | 503 explanation "the model is still being loaded." | 487 | 488 | holds |
| S035 | `/v1/models` "The `meta` field can be `null`" sentence | 1258 | 1350 | holds |
| S112/S134 | `-c, --ctx-size N` option row | 50 | 50 | holds, unmoved |
| S112/S134 | `--kv-unified-per-slot N` option row | 165 | 165 | holds, unmoved |
| S112/S134 | `-kvu, --kv-unified…` option row | 169 | 169 | holds, unmoved |
| S112/S134 | `-np, --parallel N` option row | 177 | 177 | holds, unmoved |
| S112 | `### GET /props` heading | 839 | 930 | holds |
| S112/S134 | `default_generation_settings` bullet | 927 | 1018 | holds |
| S112/S134 | `total_slots` bullet | 928 | 1019 | holds |
| S112 | `### GET /slots` heading | 983 | 1075 | holds |
| S134 | `/completion` `generation_settings` bullet | 671 | 672 | holds |
| S134 | `/completion` `truncated` bullet | 683 | 684 | holds |
| S134 | `### GET /metrics` heading | 1131 | 1223 | holds |
| S134 | last `/metrics` metric table row quoted | 1155 | 1247 | holds |
| S134 | `/v1/models` example `n_ctx_train` line | 1304 | 1397 | holds |
| S526 | `### POST /v1/completions` heading | 1314 | 1407 | holds |
| S526 | OpenAI deferral sentence ("See [OpenAI Completions API documentation]…") | 1320 | 1413 | holds |
| S553/S555 | `### GET /models` heading @ 39febd2a | 2197 | 2201 | holds |
| S553/S555 | note 1 `Adding ?reload=1…` @ 39febd2a | 2225 | 2229 | holds |
| S553/S555 | "If a model is not running, it will be added or updated according to the source" @ 39febd2a | 2227 | 2231 | holds, byte-identical |

S555's recorded line numbers (heading 2197, note 1 2225, unloaded-model bullet 2227 at `39febd2a`) re-derive
exactly from this fetch. S553/S555 are anchored at `39febd2a`, whose *own* newest relation is `b12110`; the
statement survives the newer tag unchanged, shifted 4 lines.

No anchor was `reworded`, and none was `drifted`. Every difference is a line shift caused by the sections
inserted above it (audio/voice/realtime/embedding growth), plus the four `/props` and `/v1/models` field
additions noted in §4.

---

## 7. SGLang and vLLM at their newest tags

### 7a. SGLang `native_api.mdx` v0.5.22 → v0.5.23 — 2 hunks (`artifacts/sglang-native-api-v0.5.22-v0.5.23.diff`)

Hunk 1, `@@ -108,6 +108,8 @@ ## Health Check`: **two routes added**

```
 ## Health Check
 - `/health`: Check the health of the server.
 - `/health_generate`: Check the health of the server by generating one token.
+- `/ready`: Returns 200 when the server accepts new requests; 503 while starting, paused, unhealthy, or shutting down.
+- `/ping`: SageMaker health check. Returns 200 once the server is up; 503 while starting, unhealthy, or shutting down. Stays 200 while generation is paused. A failed `/health` or `/health_generate` probe marks the server unhealthy until a later probe succeeds.
```

Line numbers: v0.5.22 has `/health` 109, `/health_generate` 110 and stops there; v0.5.23 has `/health` 109,
`/health_generate` 110, `/ready` 111, `/ping` 112.

Hunk 2, `@@ -465,3 +467,5 @@`: `/tokenize` now also accepts chat `messages` (with `tools` /
`chat_template_kwargs`), and `add_generation_prompt` / `add_special_tokens` semantics. Not health-related.

Held-route check: `/get_model_info` is still the only model-info route the page names — `grep -n model_info`
returns line 9 (the route list) and line 71 (the worked example) in **both** tags, and `/model_info` does not
occur in either. S328's "the published page never names `/model_info`" therefore **holds at v0.5.23**.

### 7b. SGLang `http_server.py` at v0.5.23 (S329's recheck)

```
802:@app.get("/get_model_info")
803:async def get_model_info():
804:    """Get the model information (deprecated - use /model_info instead)."""
806:        "Endpoint '/get_model_info' is deprecated and will be removed in a future version. "
807:        "Please use '/model_info' instead."
809:    return await model_info()
812:@app.get("/model_info")
813:async def model_info():
```
S329 records lines 786 (route), 790-791 (warning literal), 796 (`/model_info`) at v0.5.22; at v0.5.23 the same
statements sit at 802 / 806-807 / 812 — a 16-line shift, **holds**. So the docs/engine gap the entry describes
still exists at the newest tag: the page advertises a route the engine still deprecates.

### 7c. vLLM prefix-caching page v0.32.0 vs v0.33.0

Byte-identical (`67ee4e2b…`, 13916 B both). S363's anchored statement is untouched:
```
25:    In previous versions, the hash key was not guaranteed to be collision-free. As of v0.11, the default hashing algorithm is `sha256`, which addresses collision risks.
27:    For `vllm serve`, you can control the hashing algorithm via `--prefix-caching-hash-algo`:
28:    - `sha256` (default): …
29:    - `sha256_cbor`: …
```
Verdict `holds`, trivially (same bytes).

---

## 8. Per relation row: can a recheck row be written mechanically, and what is the honest value?

Row numbering follows `registry/engine-pin-relations.tsv` file order (1..5).

| row | ref | kind / role | doc opened at its own ref | doc at newest | verdict | mechanical? |
|---|---|---|---|---|---|---|
| 1 | `b11755` | tag / engine-pins | README b11755 | README b12110 | holds | yes |
| 2 | `39febd2a` | commit / source-row S553 (`tag:b11963`) | README 39febd2a | README b12110 | holds | yes |
| 3 | `b7200` | tag / cross-lane kengaku S178 | **no lane document at this ref** | — | **no verdict possible** | numbers only |
| 4 | `v0.5.22` | tag / engine-pins | native_api.mdx v0.5.22 | v0.5.23 | holds + `new=/ready,/ping` | yes |
| 5 | `v0.32.0` | tag / engine-pins | prefix_caching.md v0.32.0 | v0.33.0 | holds | yes |

Honest `recheck` cell values (date + trigger + one of holds/reworded/moved/drifted):

```
row1  2026-11-04 trigger=newest:b12110 verdict=holds
row2  2026-11-04 trigger=newest:b12110 verdict=holds
row3  2026-11-04 trigger=newest:b12110 verdict=none (no lane-held document at b7200)
row4  2026-11-04 trigger=newest:v0.5.23 verdict=holds new=/ready,/ping
row5  2026-11-04 trigger=newest:v0.33.0 verdict=holds
```

Mechanical content available from this receipt for every verdictable row: engine, ref, kind, the observed
newest tag, the two document URLs, both sha256 digests, the anchor line at each ref plus the quote, and the
verdict. Rows 1, 2, 4, 5 are therefore fully mechanical. Row 3 is **not**: the lane holds no document at
`b7200`, so a verdict in that vocabulary would be invented; only the numeric cells (`newest`, `newer`) can be
re-derived, and writing `holds` there would be a fabricated claim about a document nobody opened.

Vocabulary note for row 4: the four-value set describes an *anchored statement*. The held sentence is
byte-identical at both tags (so not `reworded`/`drifted`), the section moved down one line (so `holds` with the
new line recorded, per the entry's own rule for a bare line shift). What changed is an *addition* of two routes
the lane never held. The vocabulary has no `expanded`; the honest encoding is `verdict=holds` plus an explicit
`new=` field, which is what the row above carries.

---

## 9. Findings that are defects or risks (not fixed: lane tree is read-only for this seat)

**D1 — the documented recheck command cannot run.** `corpus/knowledge/pin-recheck-trigger.md:5` reads:

```
recheck: `python3 tools/pin-watch.py check --repo .` then re-open each `behind` row's pinned document at its own ref (`S564` for llama.cpp)
```

`--repo` is not an option of `tools/pin-watch.py`; the command exits 2 with
`the following arguments are required: --pins` (receipt `artifacts/pinwatch-as-specified.err`). The lane's own
round-41 receipts (`.ufo/waves/round-41/w1/out/R41B08.md:13`, `R41B11.md:59`) use the working form
`check --pins registry/engine-pins.tsv`, so this is a regression introduced in the round-82 knowledge entry's
recheck line, not a property of the tool. Anyone following the entry (or this seat's dispatch, which repeats
the same flag) gets a usage error instead of a verdict. Suggested fix by the L1: `--pins registry/engine-pins.tsv`.

**D2 — the register's `newest`/`newer` cells are stale against upstream, but are not wrong.** Three llama.cpp
rows read `b12103`/278, 110, 3395 while today's tag list gives `b12110`/280, 112, 3397. The cells reproduce the
committed receipt exactly and the register is explicitly a dated observation; the honest resolution is a
recheck row (§8), not a silent rewrite. Recording it here so a later seat does not mistake the delta for a
defect in the round-80 instrument (`round80-engine-pin-relations.py --tags-dir …` would still print
`unexplained=0` against its own receipt).

**D3 — row 3's `role` cell is namespace-ambiguous.** It reads `cross-lane kengaku S178`. In *this* lane,
`corpus/SOURCES.md:190` also has an `S178`, which is a kumitate counter-rerun instrument row and has nothing to
do with `b7200`. `corpus/lessons/round-80-verifier-spotcheck.md:97` resolves the intended pointer
(`kengaku-shokunin/corpus/SOURCES.md:193`). A reader grepping this lane for `S178` lands on the wrong row.
Low severity; the fix is a namespace prefix in the cell (e.g. `kengaku:S178`).

---

## 10. Commands actually run (copied verbatim; exit codes as observed)

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/pin-watch.py check --repo /home/vgpnk/Projects/shokunin/kama-shokunin   # exit 2
python3 tools/pin-watch.py check --pins registry/engine-pins.tsv                                                                 # exit 1, 1.37 s
git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master                                                              # bacae072…
curl -sS -L --max-time 90 https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/README.md                     # 200
curl -sS -L --max-time 90 https://raw.githubusercontent.com/ggml-org/llama.cpp/b12103/tools/server/README.md                     # 200
curl -sS -L --max-time 90 https://raw.githubusercontent.com/ggml-org/llama.cpp/b12110/tools/server/README.md                     # 200
curl -sS -L --max-time 90 https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md   # 200
curl -sS -L --max-time 90 https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx     # 200
curl -sS -L --max-time 90 https://raw.githubusercontent.com/sgl-project/sglang/v0.5.23/docs/docs/basic_usage/native_api.mdx     # 200
curl -sS -L --max-time 120 https://raw.githubusercontent.com/sgl-project/sglang/v0.5.23/python/sglang/srt/entrypoints/http_server.py   # 200
curl -sS -L --max-time 90 https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/docs/design/prefix_caching.md               # 200
curl -sS -L --max-time 90 https://raw.githubusercontent.com/vllm-project/vllm/v0.33.0/docs/design/prefix_caching.md               # 200
git ls-remote --tags https://github.com/ggml-org/llama.cpp.git                                                                  # exit 0, 8368 lines
git ls-remote --tags https://github.com/sgl-project/sglang.git                                                                  # exit 0, 192 lines
git ls-remote --tags https://github.com/vllm-project/vllm.git                                                                   # exit 0, 230 lines
diff -u llama-b11755-README.md llama-b12103-README.md                                                                           # exit 1, 15 hunks
diff -u sglang-v0.5.22-native_api.mdx sglang-v0.5.23-native_api.mdx                                                            # exit 1, 2 hunks
diff -u r80-llama.cpp.txt llama.cpp.txt                                                                                         # exit 1, +4 refs
```

Tooling installs: none. No pacman/uv/npx transaction was run; no PATH directory was written.

Scratch: `S=/fast/scratch/hyaku/kama-r82/SK01PinRecon` removed at yield after these artifacts were copied
here. Nothing was mirrored from the lane; only documents this seat fetched and diffs this seat produced.
