source: S563 — llama.cpp server README at the newest release tag b12103, https://raw.githubusercontent.com/ggml-org/llama.cpp/b12103/tools/server/README.md (fetched 2026-11-04, HTTP 200, sha256 `eafc1b53…a137`, 136429 bytes, 2620 lines)
verified-at: 2026-11-04 — S563, S564 and S565 fetched with `curl -sS` and sha256'd in the seat dir; the anchors below were re-located in the retained bytes
recheck: `python3 tools/pin-watch.py check --pins registry/engine-pins.tsv` (live `git ls-remote --tags`; exit 1 with `status=behind` is the trigger), then re-open each `behind` row's pinned document at its own ref and locate the anchored statement

# A `behind` relation is a recheck trigger, not knowledge drift

## What the relation register binds

`registry/engine-pin-relations.tsv` relates every pinned serving-engine ref the lane holds to the
newest upstream release tag at a dated read. Its header is `engine ref kind role relation newer
newest receipt dated`. A tag row whose version key sorts below upstream's newest carries
`relation=behind`; the `newer` cell is **how many release tags sort above the pin**, and `newest`
is the tag observed at that read. The llama.cpp row for the lane's pin `b11755` (role
`engine-pins.tsv`, dated 2026-11-04, receipt `.ufo/waves/round-80/measured/after/c2-tags/llama.cpp.txt`)
reads `behind`, `newer=278`, `newest=b12103`. A recount of that committed tag list gives 7608
`b<digits>` release tags and 278 above `b11755`, newest `b12103`.

`behind` is therefore a **trigger**, never a drift finding:

- `newer` counts release tags under the registry's per-engine pattern, not every git ref; `newest`
  is a dated observation — a live recheck read `newest=b12110`, whose README is byte-identical to S563.
- The row says only that releases exist above the pin. It says nothing about the documents the lane
  cites, so it cannot by itself make a held statement wrong.

## The only drift test: re-open the pinned document at its own ref

A `behind` row licenses one question: does the document the lane cites still state what the lane
holds? The cheapest honest resolution re-opens the **pinned** document (S564,
https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/README.md, sha256
`714c067b…6a37`, 119661 bytes, 2402 lines) beside the newest-tag document (S563), locates the
anchored statement in both, and records a verdict:

| verdict | when |
|---|---|
| `holds` | the anchored statement is unchanged; a line shift is recorded, not scored as drift |
| `reworded` | the statement's wording changed; re-derive the held row against the new wording |
| `moved` | the statement survives at a different anchor (file or section) |
| `drifted` | the statement is gone or contradicts the held row |

The round-82 read: the `GET /health` heading sits at line 479 in `b11755` and 480 in `b12103`; the
anchored sentence — "This endpoint is public (no API key check). `/v1/health` also works." — is
byte-identical at both (S564 line 481, S563 line 482). Verdict: `holds`.

## The newest document may differ without the held knowledge being wrong

The two documents are not identical, and the held statement survives anyway. `b12103` grows
2402 → 2620 lines and adds sections `b11755` does not have: `POST /tts` (line 850), `WebSocket
/v1/realtime` (line 1588) and `Memory-based unloading` (line 2167); the health section shifts one
line because an earlier options-table insertion adds `--models-memory-margin`. Those are located
differences outside the anchored statement, so they show the newest document can differ while the
held `/health` knowledge remains correct. A recheck grades the anchored statement, not the
document's whole diff.

## What a recheck cannot use

Anchoring is not optional: SGLang's `behind` row (`v0.5.22` → `v0.5.23`) cannot be resolved from
the newest tag's README, because that README (S565,
https://raw.githubusercontent.com/sgl-project/sglang/v0.5.23/README.md, 120 lines, sha256
`a7654a48…303c`) names no health, `/v1/models` or served-identity route. The flip is a docs page at
the same tag that names the anchored route. A graded recheck row names the relation row (engine +
ref), the newest tag observed, both document URLs with sha256, the located anchor (line and quote),
and the verdict.

## Boundary

The relation register and a recheck say nothing about model quality, served behavior or whether an
engine is running; those stay with the probe and the registry rows. A `behind` count is not a
finding about the code either: what a pinned document states is graded by re-opening that document
at its own ref, never by the release gap alone.
