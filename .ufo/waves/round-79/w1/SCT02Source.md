# SCT02Source — llama.cpp router `GET /models` source opened and quote graded (round 79, w1)

Seat: SCT02Source (scout, coverage). Leaf: no subagent dispatch, no lane edits, no scored
gate run. Lane tip read at start: `f7442dea53bd8f474293a2252437b5d869801f49`
(`git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master`).

Graded against the item-fixed URL and SC01's anchor claim
(SC01 item text: `§Router mode, GET /models note 1, line 2227`; SC01's landed draft repeats
line 2227 and the 16-word quote). Plan read in full before the item:
`/home/vgpnk/Projects/shokunin/kama-shokunin/plans/round-79-claims.md` (C3 §Sourced claim).

**Verdict: all four checks PASS at high confidence.** Two precision caveats and two minor
wording/completeness nits on SC01's draft, none touching the frozen anchor line, URL, byte
count or sha256.

## Opened source (this seat, 2026-11-04, read-only network)

URL:
`https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md`

| Field | Observed |
|---|---|
| HTTP status | `HTTP/2 200` (two fetches: 09:38:47Z, 09:39:22Z; bodies byte-identical) |
| Bytes | `135608` (`content-length: 135608`) |
| sha256 | `8fd5abde2fb52de3b30f30a170631d4c0d92febecc8da44d0541e48b132b35c6` |
| git blob id | `6188a084bc0ce659237dfaef2bae87d5258c0af7` |
| GitHub contents API at ref `39febd2a…` | `size=135608`, `sha=6188a084bc0ce659237dfaef2bae87d5258c0af7`, `type=file`, `download_url` = the same raw URL |
| content-type / lines | `text/plain; charset=utf-8`; `wc -l` = 2616 |
| etag | `"80a8ea32c5a7a3c44214e7595a66fbaa9ce9b2bf834f1f920d183554f0b58d7e"` |

The git blob id computed from the downloaded bytes equals the blob id GitHub reports for
`tools/server/README.md` at the pinned commit, so the opened body **is** that revision's
content, not a moving `master`. Cross-reference only: `/home/vgpnk/src/llama.cpp` has
`HEAD = 39febd2adb947b70da35e95f9351b3bf58ad170a` and a byte-identical README
(`sha256 8fd5abde…`, 135608 bytes, 2616 lines). The network leg succeeded; the item's
local-copy fallback was not invoked.

## (1) Quote at the claimed line — PASS

Claimed line: **2227**. Observed, exact bytes:

```
2227:    - If a model is not running, it will be added or updated according to the source
```

- Verbatim: the 16-word sentence is a substring of that line (four leading spaces + `- ` are
  Markdown list indentation, not part of the quote).
- Occurrence count in the whole 135608-byte file: **1** (byte-level check).
- Word count 16 ≤ 25.
- Line number agrees with the SC01 item's anchor and SC01's landed draft ("Located quote
  (line 2227, 16 words)").

**Precision caveat A.** The bullet sits under note 1, whose first line is 2225: "Adding
`?reload=1` to the query params will refresh the list of models. The behavior is as follow:".
So the sentence's literal subject is the **reload/refresh** path: a not-running model is
added or updated in the list from the source when the list is refreshed. It is not, alone, a
general statement that `GET /models` lists every unloaded model. The general part is carried
by line 2199 ("Listing all models in cache...") and by the `unloaded`/`loading`/`sleeping`/
`failed` examples at 2262-2298. Citing 2227 together with the section is sound; citing it
alone over-reads the bullet.

## (2) Surrounding section is the router `GET /models` surface — PASS

Heading path around the quote (absolute lines):

- `2013: ## Using multiple models` — line 2015 defines the surface: "`llama-server` can be
  launched in a **router mode** ... The main process (the "router") automatically forwards
  each request to the appropriate model instance."; 2017 starts router mode without a model.
- `2197: ### GET \`/models\`: List available models` — body begins 2199 "Listing all models
  in cache..."; the quote at 2227 is inside it; the section runs to 2338.
- `2339: ### POST \`/models/load\`: Load a model` — next heading, so the quote is not in the
  load/unload sections.
- Note 2 at 2228 also says "info from `/v1/models` is forwarded to router's `/v1/models`",
  re-confirming router context.

**Precision caveat B.** The anchor label "§Router mode" is a paraphrase: no heading in this
README is literally named "Router mode". The real path is `## Using multiple models` →
`### GET \`/models\`: List available models`. The line number itself is exact. SC01's landed
draft already discloses this and resolves 2227 to note 1's second bullet, so this is a
locatability nit, not a false anchor.

## (3) `status.value` vocabulary documented there — PASS

Line 2261: "The `status` object can be:" followed by JSON snippets inside the same section:

| Value | Line | Extra keys shown |
|---|---|---|
| `unloaded` | 2265 | — |
| `loading` | 2271 | `args` |
| `unloaded` (+ `failed`, `exit_code`) | 2278 | `failed: true`, `exit_code: 1` |
| `loaded` | 2287 | `args` |
| `sleeping` | 2294 | `args` |
| `downloading` | 2303 | `progress` (note at 2299: parallel downloads) |
| `incomplete` | 2319 | `args: []` (2305-2320 prose: paused/interrupted download, no instance) |

The four values the item names (`loaded`, `loading`, `unloaded`, `sleeping`) are all
documented **there**, in the router `GET /models` section — plus two more (`downloading`,
`incomplete`). Two further sentences support the C3 reading that a model list is an
inventory, not a readiness claim: 2199 "Listing all models in cache" and 2230 "The server
computes both arrays offline. It does not load the model, download files, or run inference."

Consequence for the census class (sharpening, not a defect): `status.value` has at least six
values; only `loaded` implies an instance, and even `loaded` says nothing about a consumer
being healthy. A class keyed on "the registry does not govern this serving listener" cannot
be derived from `status.value`; the doc blocks using a model list as a readiness assertion,
which is exactly C3's stated reason.

## (4) Duplicate URL / existing SOURCES row — none for this URL

Method: exact commit search plus an enumeration of every `corpus/SOURCES.md` row whose
source cell mentions `server/README` or `server README` (0-3 leading spaces pattern).

- `grep -n '39febd2a' corpus/SOURCES.md corpus/QUALITY.md corpus/README.md` → **no match**
  (exit 1). The only in-tree citation of the commit is the plan itself
  (`plans/round-79-claims.md:149`).
- Six rows hold the same *file* at other revisions/URL forms; **none** scopes router
  `GET /models` (2197-2338) or `status.value`:

| Row | Where | Revision / URL form | Scope |
|---|---|---|---|
| S001 | `corpus/SOURCES.md:13` | `blob/master` (file commit `c0fd78626405…`) | `§GET /health`, `§GET /v1/models`, `§GET /metrics` |
| S035 | `:47` | `blob/704366d76…` | `§GET /health` 479-490, `§GET /v1/models` line 1258 |
| S112 | `:124` | `blob/704366d76…` | `-c/--ctx-size` 50, `--kv-unified-per-slot` 165, `--kv-unified` 169, `--parallel` 177, `/props` 839-934, `/slots` 983-1126 |
| S134 | `:146` | `blob/704366d76…` | option lines 50/165/168-169/177, `/completion` 671/683, `/props` 927-928, `/metrics` 1131-1155, `/v1/models` example 1304 |
| S494 | `:247` | `raw/…/caa8191df159…` | `§POST /tokenize`, `§POST /detokenize` (686-735) |
| S526 | `:278` | `blob/704366d76…` | `§POST /v1/completions` 1314-1336 |

- No row carries the quote or its sentence either: searching `according to the source` and
  `is not running` across `corpus/` returns nothing.
- Therefore the plan's rule — the README already held by S001 and S526 "is not re-rowed for
  the same surface" — is satisfied: the draft's surface (router-mode list = inventory with
  `status.value`) and its pinned revision (`39febd2a`) are new. The raw-URL form has
  precedent (S494), and raw+`#L` anchors have precedent (S180-S189).

## Cross-check of SC01's landed draft

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC01Sources/sources-append.md`
(9049 bytes, 06:40) and its receipt
`.ufo/waves/round-79/w1/SC01Sources/receipts/fetch-url.txt` (`EXIT=0`) agree with this seat on
every checkable datum: URL, HTTP `200`, bytes `135608`, sha256 `8fd5abde…`, lines `2616`,
content-type `text/plain; charset=utf-8`, anchor line **2227** and the 16-word quote, the
non-literal "Router mode" heading, the absence of a duplicate URL, the same six same-file
rows, next free id `S553`, and 292 rows / 654 lines. Independently, the pre-freeze receipt
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/measured/before/source-router-models.out`
(1535 bytes) records the same `http 200 bytes 135608 sha256: 8fd5abde…` and quote line 2227 —
three independent opens agree byte-for-byte.

Two wording/completeness nits in the draft (non-fatal, do not change the row's admissibility):

1. The Gate's sentence "The quote states that a model absent from the running set is still
   listed" and the row's `teaches` clause "lists every model in the cache whatever its load
   state — a model that is not running 'will be added or updated according to the source'"
   lean on 2227 for a claim that 2227 only makes for the `?reload=1` refresh. The draft does
   cite 2230 and the value spans, so the conclusion stands, but 2199 plus the examples should
   carry the "lists every cached model" half, with 2227 cited for the reload sentence.
2. The `teaches` enumeration (`loaded`, `unloaded`, `loading`, `sleeping`; `failed`,
   `exit_code`) omits `downloading` (2303, note 2299) and `incomplete` (2319), both documented
   in the same block. The frozen `scope` cell ("each carries status.value") is unaffected.

## Receipts (absolute paths, command, exit)

Seat receipts copied out of scratch:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SCT02Source/source-check.md`
  — full command/output/exit record for checks 0-4 plus the SC01 cross-check.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SCT02Source/raw-transcript.txt`
  — raw transcript of the evidence commands.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SCT02Source/headers.txt`
  — the 200 response headers (`date: Wed, 04 Nov 2026 09:39:22 GMT`, `content-length: 135608`).

Command/exit summary (cwd `$S = /fast/scratch/hyaku/kama-r79/SCT02Source`):

| Command | Result | Exit |
|---|---|---|
| `curl -sS -D headers.txt -o readme.md -w 'http=%{http_code} bytes=%{size_download} …' <URL>` | `http=200 bytes=135608` | 0 |
| `sha256sum readme.md` | `8fd5abde…b35c6` | 0 |
| `git hash-object readme.md` | `6188a084…0af7` | 0 |
| `grep -n '<quote>' readme.md` | `2227: …` | 0 |
| `sed -n '2227p' readme.md \| cat -A` | four spaces + bullet text | 0 |
| `grep -n '^#\{2,3\} ' readme.md \| awk …` | 2013/2197/2339 bounds | 0 |
| `grep -n 'The \`status\` object can be' readme.md` | `2261` (+ value spans) | 0 |
| `curl -sS -o api-contents.json '<contents API at ref 39febd2a>'` | `http=200`, `size=135608`, `blob_sha=6188a084…` | 0 |
| `grep -n '39febd2a' corpus/SOURCES.md corpus/QUALITY.md corpus/README.md` (lane cwd) | no match | 1 (expected) |
| `python3` S-row scan for `server/README\|server README` | 6 rows (13, 47, 124, 146, 247, 278) | 0 |

Scratch `$S` was deleted after these receipts were copied; no crown-jewel or host change was
made. No tools were installed (network + built-ins sufficed). No git/jj write ran; the lane
and every sibling path were read-only.

## Remaining unknowns

- Whether the live host listener actually runs the `39febd2a` build is asserted by the plan
  (C3 fixture context) and not measured here; this seat graded the document at that commit
  only. Port/registry classification is EX03/EX04's leg.
- No other unknowns: the quote, its line, the section, the status vocabulary and the
  no-duplicate-URL finding are all resolved from the opened bytes and the lane tree.
