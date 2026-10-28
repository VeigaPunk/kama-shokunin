# SC06CoverageMap — completion response-shape coverage (round 63, kama)

Seat: SC06CoverageMap (leaf, recon). Axis: operability. Milestone: open and locate.
Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09`. Base: `7ee8cbdf160f8c945954e4737e7a2f797e3b2987`.
Method: read-only. Committed bytes read with `git show <rev>:<path>` and `git grep <rev>`; nothing edited, committed or run live. No scratch was needed; `/fast/scratch/hyaku/kama-r63/w/SC06CoverageMap` was removed (rm -rf, exit 0).
Evidence copies: `.ufo/waves/round-63/w1/out/SC06CoverageMap/` (`completion-request-plane.tip.md`, `tip-sha.txt`, `tip-vs-base-grep.txt`, `worktree-uncommitted.diff`).

## 0. Read-first finding: the lane working tree is not the tip

The first copy of `corpus/knowledge/completion-request-plane.md` I was handed comes from the lane working tree. That tree is dirty (`git status`: M `PROVINCE.md`, M `corpus/SOURCES.md`, M `corpus/knowledge/completion-request-plane.md`), and the dirty bytes carry a round-63 section that the tip does not have.

| Path | base 7ee8cbdf | tip 03a6a1d8 | working tree |
|---|---|---|---|
| `corpus/knowledge/completion-request-plane.md` | 71 lines, sha256 `8ddd9d51…` | identical to base | 112 lines; adds `## Round-63 strict response grading` at line 74 |
| `corpus/SOURCES.md` | `f9ff8176…` | identical; last S52x row is S526 (line 278) | adds S527 (line 279) and S528 (line 280) |
| `PROVINCE.md` | `a60591b7…` | identical; no round-63 note | adds a round-63 note (line 190) |
| `corpus/README.md` | `e9957eda…` | identical (1614 lines) | identical, not dirty |

`git diff --stat 7ee8cbdf 03a6a1d8 -- corpus` prints nothing. **The corpus did not change between base and tip.** The round-63 commits (`675cac02`, `03a6a1d8`) touch only `tools/`, `registry/`, `SCORECARD.md`, and `.ufo/waves/round-63/`.

Consequence: at the freeze tip, the committed tool and the committed knowledge doc disagree (section 3). The round-63 corpus text exists only as uncommitted working-tree bytes (`worktree-uncommitted.diff`). This is the L1's to resolve; I am reporting it, not fixing it.

## 1. What the corpus held before this round (base = tip for corpus bytes)

Surface-by-surface. "Graded" means the committed tool at that revision checks it. The base tool is v1 (`tools/kama-completion-live.py` sha `71ac4f2c…`, `SCHEMA='kama-completion-live/v1'`). The "tip tool" column is v2, from `03a6a1d8` (sha `e24bc944…`, `SCHEMA` at line 67).

| Surface | Held in corpus at base (path:line) | Status in committed corpus at tip | Graded by tip tool (v2) |
|---|---|---|---|
| Route and request body (`prompt`, `n_predict`, `temperature`, `seed`, no `model`) | `knowledge/completion-request-plane.md:21-22` | held | — (request bytes bound by `completion_request_bound`, tip tool line 437) |
| `object` = `text_completion` | `completion-request-plane.md:26` | held | `completion_envelope` (tool line 364) |
| `choices[0].text` (string, content never graded) | `:27`, non-invariant `:43-44` | held (v1 text) | `completion_choice_shape` (tool line 381), non-empty text for the fixed request |
| `choices[0].finish_reason` | `:28` | held | `completion_finish_reason` (line 390) |
| `choices` count, `index`, `logprobs` | **not described** (only `choices[0].text`) | absent | `completion_choice_shape` (line 381) |
| `id` and `created` | `:47`: "recorded but ungraded" | held as an ungraded note | `completion_id_created` (line 401) |
| `model` echo of `--alias` | `:29` | held | `completion_model_id` (line 393) |
| `system_fingerprint` shape `b<digits>-<hex>` | `:30` | held (shape only) | `completion_fingerprint` (line 397) |
| `usage` counts and total | `:31` | held (total = prompt + completion graded) | `completion_usage` (line 408) |
| `usage.prompt_tokens_details.cached_tokens` | `:31`, `:34`, `:47` | held, ungraded | `completion_usage` (line 408), bound `≤ prompt_tokens` |
| `timings.predicted_n` / `predicted_ms` | `:32` | held, presence and `predicted_n == usage.completion_tokens` | `completion_timings` (line 420), strict value bounds |
| `timings.cache_n`, `prompt_n`, per-token rates | `:32` ungraded | held, ungraded | `completion_timings` (line 420) |
| Determinism (temp 0, fixed seed) | `:34-35` | held | `completion_deterministic` (lines 458, 461) |
| Error surface: no `prompt` → 400 with `error` object | `:37-39` | held | `bad_request_graded` (in `check(` list) |
| HTTP headers (`Content-Type`) of the completion | `:52`: "(headers are not kept)" | **absent**: no completion header row anywhere in corpus | `completion_headers` (line 370) |
| Body truncation / `Content-Length` | `:51-52`: `body_truncated` recorded, never graded | recorded only | `completion_untruncated` (line 374) |
| Tokenize binding (`/tokenize` count vs `usage.prompt_tokens`) | **none for b11755 completion**; `/tokenize` only as the round-49 witness on the b11909 README (see section 4) | absent for this fixture | `completion_prompt_tokens` (line 430) |
| Streaming / SSE | `:65-66`: not observed | held as a bound | not graded |

Adjacent response-shape ground that already exists (for route neighbours, not the completion body):

| Adjacent surface | Held at base (path:line) | Note |
|---|---|---|
| Chat route `choices` length, `logprobs` presence, `usage_keys`, `prompt_tokens` | `knowledge/chat-adapter-outcomes.md:18` (response row), `:59-60` (counter normalisation) | chat route, not `/v1/completions`; a different route per `completion-request-plane.md:110-112` |
| 503 loading envelope with `Content-Type: application/json; charset=utf-8` and `Server: llama.cpp` | `knowledge/llamacpp-loading-lifecycle.md:65` (table row, "any `Content-Type`"), `:118` (observed headers, load window) | only held header surface; on a 503 loading body, not a completion 200 |
| Content-Type classification for identity (HTML = foreign) | `knowledge/endpoint-identity.md:16` (row 4) | identity probe, not completion |
| Metrics vs response timings boundary (TTFT/TPOT) | `knowledge/serving-metrics-crosswalk.md:8`, `:17-18`, `:25` | exporter metrics; "never identity evidence" |
| `usage` on runtime-health surface | — | no completion usage ground is held there; not cited |
| OpenAI `created` on `/v1/models` | `knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md` (README row 605) | models list, not completion |

## 2. What is new at the freeze tip (03a6a1d8)

- **Corpus (committed):** nothing. Zero corpus bytes changed base→tip.
- **Tool (committed):** `tools/kama-completion-live.py` moves v1→v2 (132 changed lines in the `675cac02..03a6a1d8` diff stat). The v2 check set at tip is in the tool: `completion_headers` (370), `completion_untruncated` (374), `completion_choice_shape` (381), `completion_id_created` (401), `completion_usage` (408), `completion_timings` (420), `completion_prompt_tokens` (430), `completion_request_bound` (437). The tool's committed docstring says so at line 23 (`kama-completion-live/v2 (round 63; v1 was round 62)`).
- **Counters and registry (committed):** `tools/round63-c1-counter.py`, `tools/round63-c2-counter.py`, `registry/capability-claims-r63.tsv`, `registry/hexrun-ledger.tsv`.
- **Corpus (working tree only, not at tip):** the round-63 section of `completion-request-plane.md` (lines 74-112), S527 and S528 rows (`corpus/SOURCES.md:279-280`), and the PROVINCE round-63 note (line 190). Working-tree rows by line:
  - `completion-request-plane.md:85` headers, `:86` untruncated, `:87` choice shape, `:89` id/created, `:90` usage, `:91` timings, `:92` prompt_tokens, `:93` request_bound, `:83-93` the table.
  - `:48` text now marks the v1 reading as superseded.
- Working-tree S527 cites `tools/server/server-task.cpp` lines 357-363 (usage) and 366-392 (choice, id, created). S528 cites `tools/server/server-common.cpp` lines 139-160 (timings). Both are pinned to b11755 (704366d76).

## 3. Mismatches a reader of the committed tip would hit

1. **Stale corpus vs tip tool.** The committed doc says headers are not kept (`completion-request-plane.md:52`), that `id`/`created`/`logprobs`/`index` are ungraded (`:47`), and that the receipt checks are the v1 list (`:52-56`). The tip tool grades all of these (section 1, rows marked v2). Anyone reading the committed corpus gets the v1 contract.
2. **Stale citation.** The doc's `source:` line (`:1`) and `verified-at:` line (`:2`) cite the round-62 tool sha `71ac4f2c…` at tip `65d7cad0`. The committed tip tool is `e24bc944…` (v2). Nothing at tip names the v2 sha in the corpus.
3. **Missing source rows at tip.** S527 and S528 are absent from `corpus/SOURCES.md` at tip (tip rows end at S526, line 278). The committed v2 tool cites usage and timings lines that have no SOURCES row at tip.
4. **PROVINCE frontier unchanged at tip.** `PROVINCE.md:141` and `:160` (tip) still list `/v1/completions` as frontier. The working tree adds a round-63 note (line 190) that moves it to held ground. The committed tip does not.
5. **No coverage-map row.** `corpus/README.md` has no row for `knowledge/completion-request-plane.md` at base or tip (`grep -c completion-request-plane corpus/README.md` = 0 at tip). The frontier text names `/v1/completions` as open in several places, but no coverage row holds it. `corpus/QUALITY.md` at tip has no "coverage map" rule (grep: 0 hits), so an expansion claim has no written requirement to add a row, but it also has no row to cite.

## 4. Tokenize binding: a source-release mismatch

- The only `/tokenize` ground in the corpus is the round-49 witness: `corpus/README.md:1096-1138` (`tools/round49-replay-witness-audit.py` posts a nonce to `POST /tokenize` `with_pieces` and `/detokenize`), and `:1266-1285`. Source row `corpus/SOURCES.md:247` (S494) is the llama.cpp README at **b11909** (`caa8191d`), and its scope cell says "at the b11909 commit; not other releases".
- The round-63 check `completion_prompt_tokens` (tip tool line 430) asks the **b11755** fixture's `/tokenize` for a prompt count and compares it with `usage.prompt_tokens`. The working-tree doc concedes this at `completion-request-plane.md:92`: "no pinned source line was opened for the special-token rule, so it holds for this tokenizer only".
- So the tokenize binding cites a row for a different release. This is a source-anchor gap, not a claim I am ruling on.

## 5. Coverage-map rows and frontier lines an expansion claim could cite (path:line, tip bytes)

Existing rows usable as adjacent citations (none is a completion-body row):

| Citation | What it covers | Use for a completion claim |
|---|---|---|
| `corpus/README.md:31` | `knowledge/endpoint-identity.md`: Content-Type classification | headers, identity context only |
| `corpus/README.md:97` | `knowledge/runtime-health-surface-matrix.md`: `/health` semantics | not completion |
| `corpus/README.md:98` | `knowledge/serving-metrics-crosswalk.md`: TTFT/TPOT boundaries | timings boundary, not response timings |
| `corpus/README.md:126` | `knowledge/served-identity-crosswalk.md`: llama.cpp nullable loading metadata | not completion |
| `corpus/README.md:213` | `knowledge/llamacpp-loading-lifecycle.md`: 503 loading gate | the only held header/envelope surface |
| `corpus/README.md:245` | `knowledge/llamacpp-loading-lifecycle.md` §Round 17: exact `/health` ready body | not completion |
| `corpus/README.md:476` | `knowledge/chat-adapter-outcomes.md`: chat response (`choices`, `logprobs`, `usage_keys`) | chat route, not `/v1/completions` |
| `corpus/README.md:1096-1138` | round-49 `/tokenize` `with_pieces` witness (S494, b11909) | the tokenize surface, on another release |
| `corpus/SOURCES.md:247` | S494, b11909 README, scope "not other releases" | the source for the `/tokenize` row |
| `corpus/SOURCES.md:278` | S526, b11755 README §POST `/v1/completions` (lines 1314-1336) | the route only |

Frontier lines (open-item citations for `/v1/completions`):
- `corpus/README.md:407` (round 25, K05 cells on POST `/completion`), `:417` (round 26), `:435-438` (round 28: "the same fields through `/v1/chat/completions` and other endpoints"), `:485-487` (round 31: "the same fields through `/v1/completions`"), `:518-519` (round 32), `:535-536` (round 33).
- `corpus/README.md:66-78` (current `## Frontier`) does **not** name completions.
- `PROVINCE.md:141`, `:160` (tip).

No coverage-map row at base or tip holds `knowledge/completion-request-plane.md`. An expansion claim therefore has to add a new row or cite the adjacent rows above, and it has to say which ones are chat or identity rather than the completion body.

## 6. Operability notes for the L1 (no action taken)

- The working tree is dirty with three corpus/PROVINCE files that the tip does not have. The counter reads committed tip bytes (`--repo`/`--tip`), so a counter run at `03a6a1d8` will not see the round-63 doc text.
- Corpus commit of the round-63 doc, S527/S528 and the PROVINCE note is a precondition for the doc/tool/SOURCES triangle to agree at a single tip.
- The `verified-at` line (`:2`) of the committed doc and the `source` line (`:1`) cite the round-62 sha; they will need re-derivation after the v2 doc is committed (per the doc's own recheck rule at `:3`).
- No live run, no network, no tool install, no git mutation performed by this seat.

## Tally

`SC06 recon: corpus_delta_base_tip=0 tip_doc_schema=v1 tool_schema_tip=v2 wt_only_corpus_files=3 wt_only_sources_rows=2 coverage_rows_for_completion_body=0 tokenize_source_release=b11909 (fixture b11755)`
