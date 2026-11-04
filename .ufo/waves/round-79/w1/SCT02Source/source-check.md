# SCT02 — opened source check: llama.cpp router `GET /models` README at `39febd2a`

Seat: SCT02Source (scout, coverage). Lane: kama, round 79, wave w1.
Frozen claim under test: C3's Sourced claim + SC01's SOURCES draft anchor
"§Router mode, GET /models note 1, line 2227" with quote
`If a model is not running, it will be added or updated according to the source`.

Source URL (item-fixed, opened read-only this round):

```
https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md
```

Scratch root (deleted before yield): `/fast/scratch/hyaku/kama-r79/SCT02Source/`.

## Verdict summary

| # | Check | Result |
|---|---|---|
| 0 | URL opens; HTTP status, bytes, sha256 recorded | **PASS** — HTTP/2 200, 135608 bytes, sha256 `8fd5abde2fb52de3b30f30a170631d4c0d92febecc8da44d0541e48b132b35c6` |
| 1 | Quote present verbatim at the line SC01 claims (2227) | **PASS** — exact bytes at line 2227, single occurrence in the file, 16 words |
| 2 | Surrounding section is the router `GET /models` surface | **PASS** — `### GET \`/models\`: List available models` (2197) inside `## Using multiple models` (2013), which defines "**router mode**" (2015); section ends 2338 |
| 3 | `status.value` vocabulary (loaded/loading/unloaded/sleeping) documented there | **PASS** — all four documented at 2261-2297; the same list also documents `downloading` (2303) and `incomplete` (2319) |
| 4 | Same URL already held by an existing SOURCES row, and at which scope | **NO for this URL** — no row holds the `39febd2a` URL. Six rows hold the same *file* at other revisions, none scoped to router `GET /models`; see §4 |

Two precision notes that do not overturn the claim (details below): the quote is a
sub-bullet under note 1's `?reload=1` refresh sentence, so its literal scope is reload
behaviour; and the anchor label "§Router mode" is a paraphrase — no heading is literally
named "Router mode".

## 0. Fetch: HTTP status, bytes, sha256

Command (cwd `$S = /fast/scratch/hyaku/kama-r79/SCT02Source`):

```
$ curl -sS -D headers.txt -o readme.md -w 'http=%{http_code} bytes=%{size_download} url=%{url_effective}\n' \
    https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md
http=200 bytes=135608 url=https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md
exit=0
```

```
$ sha256sum readme.md
8fd5abde2fb52de3b30f30a170631d4c0d92febecc8da44d0541e48b132b35c6  readme.md
exit=0
```

Response headers (selected; `headers.txt` copied beside this file):

```
HTTP/2 200
etag: "80a8ea32c5a7a3c44214e7595a66fbaa9ce9b2bf834f1f920d183554f0b58d7e"
date: Wed, 04 Nov 2026 09:39:22 GMT
content-length: 135608
```

Fetched twice, 2026-11-04T09:38:47Z and 09:39:22Z; the two bodies are byte-identical
(`cmp` exit 0) with the same sha256.

**Bytes-to-commit binding (content integrity).** The downloaded bytes hash to git blob
`6188a084bc0ce659237dfaef2bae87d5258c0af7`:

```
$ git hash-object readme.md
6188a084bc0ce659237dfaef2bae87d5258c0af7
exit=0
```

```
$ curl -sS -o api-contents.json -w 'http=%{http_code}\n' \
    "https://api.github.com/repos/ggml-org/llama.cpp/contents/tools/server/README.md?ref=39febd2adb947b70da35e95f9351b3bf58ad170a"
http=200
exit=0
name=README.md size=135608 blob_sha=6188a084bc0ce659237dfaef2bae87d5258c0af7 type=file
download_url=https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md
```

So the raw body is exactly the blob GitHub reports for that path at the pinned commit:
sha256 `8fd5abde…b35c6`, size 135608, blob `6188a084…0af7`.

Cross-reference, not a substitute for the opened URL: the local tree at
`/home/vgpnk/src/llama.cpp` has `git rev-parse HEAD` = `39febd2adb947b70da35e95f9351b3bf58ad170a`
and a byte-identical `tools/server/README.md` (sha256 `8fd5abde…b35c6`, 135608 bytes).
The network leg above succeeded, so the item's local-copy fallback was not needed.

## 1. Quote at the claimed line 2227 — verbatim

```
$ grep -n 'If a model is not running, it will be added or updated according to the source' readme.md
2227:    - If a model is not running, it will be added or updated according to the source
exit=0
```

```
$ sed -n '2227p' readme.md | cat -A
    - If a model is not running, it will be added or updated according to the source$
exit=0
```

- Line number: **2227**, exactly the line SC01 claims.
- The quoted 16-word string occurs **once** in the 135608-byte file (substring at the
  claimed line; byte-level check over the file's bytes, not a fuzzy read).
- Leading bytes are four spaces plus `- `: the quote is a Markdown sub-bullet; the
  sentence text itself is verbatim.
- Word count 16, within the round's ≤25-word anchor limit.

Context, lines 2222-2229 (absolute line numbers):

```
2222  ```
2223
2224  Note:
2225  1. Adding `?reload=1` to the query params will refresh the list of models. The behavior is as follow:
2226      - If a model is running but updated or removed from the source, it will be unloaded
2227      - If a model is not running, it will be added or updated according to the source
2228  2. When the model is loaded, the info from `/v1/models` is forwarded to router's `/v1/models`. This includes metadata about the model and the runtime instance.
2229
```

**Precision note A (does not fail the check):** the sentence sits under note 1, whose
subject is the `?reload=1` refresh ("Adding `?reload=1` ... will refresh the list of
models"), so its literal scope is reload behaviour — a not-running model is
added/updated in the list from the source on refresh. It is not, by itself, a general
statement that `GET /models` lists every unloaded model. That broader statement is
carried by line 2199 ("Listing all models in cache") and by the `status.value: "unloaded"`
examples at 2262-2265 and the non-loaded examples at 2269-2325. A row that cites 2227 for
"unloaded models are listed" is defensible only together with the section heading and
those examples; cited alone it over-reads the bullet.

## 2. Surrounding section — router `GET /models`

Heading scan (absolute lines):

```
2013:## Using multiple models
2023:### Model sources
2076:### Model presets
2135:### Routing requests
2163:### Memory-based unloading
2197:### GET `/models`: List available models
2339:### POST `/models/load`: Load a model
```

- The quote at 2227 is inside `### GET \`/models\`: List available models`, which starts
  at 2197 (line 2199: "Listing all models in cache. The model metadata will also include
  a field to indicate the status of the model:") and runs to 2338; the next heading is
  `### POST \`/models/load\`` at 2339.
- The enclosing `## Using multiple models` (2013) is the router surface: line 2015 says
  "`llama-server` can be launched in a **router mode** that exposes an API for dynamically
  loading and unloading models. The main process (the "router") automatically forwards
  each request to the appropriate model instance."; line 2017 starts router mode by
  launching `llama-server` without a model.
- Note 2 at 2228 also speaks of "router's `/v1/models`", confirming the router context.

**Precision note B (does not fail the check):** the anchor label "§Router mode, GET
`/models` note 1, line 2227" is a paraphrase of the heading path; the README has no
heading literally named "Router mode". The heading path that *does* exist is
`## Using multiple models` → `### GET \`/models\`: List available models`. A row whose
anchor names "§Router mode" is locatable but not a literal heading; recommend the anchor
name the real heading while keeping line 2227.

## 3. `status.value` vocabulary documented in the same section

```
$ grep -n 'The `status` object can be' readme.md
2261:The `status` object can be:
```

Values documented in that block (absolute lines, all within 2197-2338):

```
2265:   "value": "unloaded"
2271:   "value": "loading",                                   (+ "args")
2278:   "value": "unloaded", "failed": true, "exit_code": 1
2287:   "value": "loaded",                                    (+ "args")
2294:   "value": "sleeping",                                  (+ "args")
2299: Note: for "downloading" state, there can be multiple files be downloading in parallel
2303:   "value": "downloading",                               (+ "progress")
2319:   "value": "incomplete",                                (+ "args": [])
```

- `loaded`, `loading`, `unloaded`, `sleeping` — **all four documented there**, in this
  section, at the lines above.
- The same list also documents `downloading` (2303, with a parallel-download note at
  2299) and `incomplete` (2319, "A download that never finished ... listed under a
  separate 'incomplete' status, without an instance").
- The section's own framing supports the C3 sourced claim's reading: 2199 "Listing all
  models in cache" and 2300-2320 show non-loaded entries are listed; 2230 says the server
  "computes both arrays offline. It does not load the model, download files, or run
  inference." A model list is therefore an inventory, not a readiness assertion.
- Sharpening for the census class (not a defect in the claim): the vocabulary is six
  values, not four. `status.value` alone never means "serving"; `loaded` is the only
  value implying an instance, and even `loaded` does not by itself mean a *consumer* is
  healthy. A class that maps `status.value` to readiness must treat
  `downloading`/`incomplete`/`sleeping`/`loading`/`unloaded` as non-serving, and must not
  infer consumer readiness from `loaded`.

## 4. Duplicate URL / existing SOURCES row

Method: exact URL search, commit search, and an enumeration of every `corpus/SOURCES.md`
row whose source cell mentions `server/README` or `server README` (0-3 leading spaces
pattern, matching the registry contract).

```
$ grep -n '39febd2a' corpus/SOURCES.md corpus/QUALITY.md corpus/README.md
(no output; exit 1 for the grep)
```

The only in-tree citation of the pinned commit is the plan itself
(`plans/round-79-claims.md:149`, "pinned commit `39febd2a…`, the build the live listener
runs"), not a SOURCES row.

Six rows hold the same *file* at other revisions/URL forms (row line, id, revision, scope):

| Row | Revision / URL form | Scope (verbatim from the row) |
|---|---|---|
| S001 (`corpus/SOURCES.md:13`) | `blob/master` (file commit `c0fd78626405…`) | "§GET `/health`, §GET `/v1/models`, §GET `/metrics` @ file commit c0fd7862… (2026-10-17); repo master 4c3c5810 when the metrics section was read" |
| S035 (`:47`) | `blob/704366d76…` | "§GET `/health` lines 479-490 … and §GET `/v1/models` line 1258; raw file sha256 714c067b…" |
| S112 (`:124`) | `blob/704366d76…` | "`-c`/`--ctx-size` line 50, `--kv-unified-per-slot` 165, `--kv-unified` 169, `--parallel` 177; §GET `/props` 839-934; §GET `/slots` 983-1126" |
| S134 (`:146`) | `blob/704366d76…` | "option lines 50, 165, 168-169 and 177; /completion 671 and 683; /props 927-928; /metrics 1131-1155; /v1/models example line 1304" |
| S494 (`:247`) | `raw.githubusercontent.com/.../caa8191df159…/tools/server/README.md` | "§POST `/tokenize` … §POST `/detokenize` (lines 686-735 of the copy …)" |
| S526 (`:278`) | `blob/704366d76…` | "§POST `/v1/completions` lines 1314-1336 …; not `/health`/`/props` (S035/S112), not `/completion`" |

Findings:

1. **No SOURCES row holds the `39febd2a` URL**, in raw or blob form. The URL is new.
2. **No row's scope covers router `GET /models`** (this README section, lines 2197-2338)
   or the `status.value` vocabulary. S001's "model list" scope is the direct-server
   `§GET /v1/models`; S035's line 1258 is the direct-server `/v1/models`; S526 is
   `/v1/completions`; S112/S134 are context/KV, `/props`, `/slots`, `/metrics`;
   S494 is `/tokenize`/`/detokenize`.
3. **No row carries this quote or its sentence** (search for "according to the source"
   and "is not running" over `corpus/` returns no row).
4. The plan's constraint is therefore satisfied: the README "already held by S001 and
   S526 is not re-rowed for the same surface" — the new row is a distinct surface at a
   distinct pinned revision. Precedent for the raw-URL form is S494; precedent for
   raw + `#L` anchors is S180-S189.

**Recommendation to SC01 (not an edit to their file):** if the anchor line is kept as
2227, cite the real heading path (`## Using multiple models` → `### GET \`/models\`: List
available models`) instead of "§Router mode", and rely on 2199 plus the `unloaded`/
`loading`/`sleeping` examples for the "unloaded models are listed" half of the claim,
using 2227 only for the reload/refresh sentence it literally is. The sha256 to record is
`8fd5abde2fb52de3b30f30a170631d4c0d92febecc8da44d0541e48b132b35c6` at 135608 bytes (raw
file, pinned commit `39febd2adb947b70da35e95f9351b3bf58ad170a`).

## 5. Cross-check against SC01's landed draft

SC01's draft landed while this seat polled:
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC01Sources/sources-append.md`
(9049 bytes, mtime 2026-11-04 06:40), plus receipt
`.ufo/waves/round-79/w1/SC01Sources/receipts/fetch-url.txt` (`EXIT=0`).

Their claim, re-read after landing, is the same line this seat graded:

| SC01 statement | This seat's independent observation | Agree? |
|---|---|---|
| "Located quote (line 2227, 16 words)" | line 2227, 16 words, single occurrence | **yes** |
| URL identical to the item's | identical raw URL, HTTP/2 200 | **yes** |
| bytes `135608` | 135608 | **yes** |
| sha256 `8fd5abde2fb52de3b30f30a170631d4c0d92febecc8da44d0541e48b132b35c6` | same | **yes** |
| lines `2616` (`wc -l`), content-type `text/plain; charset=utf-8` | 2616; same content-type | **yes** |
| anchor resolves to note 1's second bullet under `### GET /models` (2197) | same; note 1 at 2225, bullet 2226 is the sibling, 2227 the quote | **yes** |
| anchor "Router mode" is not a literal heading | same (note B above) | **yes** |
| duplicate URL absent; same-file rows S001/S035/S112/S134/S494/S526; next free `S553`; 292 rows / 654 lines | same six rows, same counts (`wc -l` 654, 292 S-ids, max S552) | **yes** |
| near-neighbour `S479` is `server-models.cpp`, router declared-capacity key | row exists at `corpus/SOURCES.md:232`, same file/scope | **yes** |
| pre-freeze receipt `measured/before/source-router-models.out` names the same sha256 and line | file exists (1535 bytes); header `http: 200 bytes: 135608 sha256: 8fd5abde…` and quote line 2227 | **yes** |

Two wording divergences, both graded as precision notes rather than failures:

1. SC01's Gate says "The quote states that a model absent from the running set is still
   listed, which is the inventory predicate the row scope claims", and the row's
   `teaches` cell says "lists every model in the cache whatever its load state — a model
   that is not running 'will be added or updated according to the source'". The bullet is
   literally under the `?reload=1` refresh sentence (2225), so alone it says what a
   refresh does with a not-running model. The "lists every cached model whatever its load
   state" half is carried by line 2199 plus the `unloaded`/`loading`/`sleeping`/`failed`
   examples (2262-2298); SC01 does cite 2230 and those spans elsewhere in the Gate, so
   the row is supportable, but the quoted sentence should not stand alone for that clause.
2. The `teaches` cell enumerates `loaded`, `unloaded`, `loading`, `sleeping` (+ `failed`,
   `exit_code`). The same block also documents `downloading` (2303, with note at 2299)
   and `incomplete` (2319). The frozen `scope` cell ("each carries status.value") is
   unaffected; the enumeration is only incomplete.

Neither divergence touches the frozen anchor line, the URL, the bytes or the sha256.

## Commands, outputs, exits (receipt)

All commands ran with cwd `/fast/scratch/hyaku/kama-r79/SCT02Source`; the full raw
transcript is `raw-transcript.txt` beside this file.

| # | Command | Key output | Exit |
|---|---|---|---|
| 1 | `curl -sS -D headers.txt -o readme.md -w 'http=%{http_code} bytes=%{size_download} url=%{url_effective}\n' <URL>` | `http=200 bytes=135608 url=<URL>` | 0 |
| 2 | `sha256sum readme.md` | `8fd5abde2fb52de3b30f30a170631d4c0d92febecc8da44d0541e48b132b35c6` | 0 |
| 3 | `git hash-object readme.md` | `6188a084bc0ce659237dfaef2bae87d5258c0af7` | 0 |
| 4 | `grep -iE '^(HTTP/\|date:\|etag:\|content-length:)' headers.txt` | `HTTP/2 200`, `etag: "80a8ea32…"`, `date: Wed, 04 Nov 2026 09:39:22 GMT`, `content-length: 135608` | 0 |
| 5 | `grep -n '<quote>' readme.md` | `2227:    - If a model is not running, it will be added or updated according to the source` | 0 |
| 6 | `sed -n '2227p' readme.md \| cat -A` | four spaces + `- If a model is not running, … source$` | 0 |
| 7 | `grep -n '^#\{2,3\} ' readme.md \| awk -F: '$1>=2013 && $1<=2345'` | `2013:## Using multiple models` … `2197:### GET \`/models\`: List available models` … `2339:### POST \`/models/load\`` | 0 |
| 8 | `grep -n 'The \`status\` object can be' readme.md` + value scan | `2261`, values at 2265/2271/2278/2287/2294/2303/2319 | 0 |
| 9 | `curl -sS -o api-contents.json -w 'http=%{http_code}\n' <API contents URL at ref 39febd2a>` | `http=200`; `size=135608 blob_sha=6188a084…0af7 download_url=<raw URL>` | 0 |
| 10 | `grep -n '39febd2a' corpus/SOURCES.md corpus/QUALITY.md corpus/README.md` (cwd lane) | no output | 1 (no match) |
| 11 | `python3` row scan over `corpus/SOURCES.md` for `server/README\|server README` | 6 rows: S001, S035, S112, S134, S494, S526 (lines 13, 47, 124, 146, 247, 278) | 0 |
| 12 | `grep -rn 'according to the source\|is not running' corpus/` | no output | 0 (via pipe) |
| 13 | `cmp readme.md readme2.md` (two fetches) | identical | 0 |
