# W02KnowledgeDraft — `corpus/knowledge/completion-request-plane.md` (round 62, kama)

Seat: knowledge-draft leaf (advisory). Lane tip read: `65d7cad0fce90e34de37527cde22e97b63b118bf`
(`git rev-parse master`, read-only; not my commit). Run date 2026-10-28. No verdict on C1/C2 is
offered here; nothing was committed, pushed, or mutated.

## Deliverable

`corpus/knowledge/completion-request-plane.md` — 71 lines, sha256
`8ddd9d51d5e58bab6cc2cb8716f758ca9f678dbb3f73bf084906669689d4778b`. Durable copy of the same
bytes: `.ufo/waves/round-62/w1/out/W02KnowledgeDraft/completion-request-plane.md`. The entry opens
with the provenance trio (`source:`, `verified-at:`, `recheck:`), then documented vs observed
contract, determinism, error body, non-invariants, receipt integrity, and scope bounds.

## Evidence produced by this seat

One live run of the lane tool, from my scratch, on an unregistered loopback port:

```
cd /fast/scratch/hyaku/kama-r62/w/W02KnowledgeDraft
TMPDIR=$PWD/run1/tmp python3 <lane>/tools/kama-completion-live.py \
  --work run1/work --hold-dir run1/hold --hold-timeout 90 \
  --nonce w02-r62-kn-draft-1 --out run1/receipt.json
# release written to run1/hold/release as soon as run1/hold/hold.json appeared
exit=0
```

- receipt: `.ufo/waves/round-62/w1/out/W02KnowledgeDraft/receipt.json`, sha256
  `d669e112abfc393eeac32de73d344623c18b9671237c1f6a52655dc1923e73bc`, schema
  `kama-completion-live/v1`, nonce `w02-r62-kn-draft-1`, port 41585 (absent from
  `registry/endpoint-consumers.tsv`), run at `2026-10-28T12:28:52.884Z`.
- verdict `REQUEST_OK`, 17/17 evaluated checks passed: `model_digest`, `server_digest`,
  `listener_owned`, `health_ready`, `models_alias_id`, `props_alias`, `completion_envelope`,
  `completion_finish_reason`, `completion_model_id`, `completion_fingerprint`, `completion_usage`,
  `completion_timings`, `completion_deterministic`, `bad_request_graded`, `hold_released`,
  `teardown_clean`, `teardown_port_closed`.
- fixture binding, re-hashed by me before the run: `llama-server`
  `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`
  (`/home/vgpnk/.local/opt/llama-b11755/llama-server`), `stories260K.gguf`
  `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`; tool
  `tools/kama-completion-live.py` sha256 `71ac4f2c45570a79cb1e80db91e85268609f28bf4dd421d628ffb9d10243771f`
  (equals `git show 65d7cad0:tools/kama-completion-live.py`).
- captures read from the receipt (all `body_truncated=false`): health 200
  `a29ee2b15c49…`, models 200 `5ca3273792e1…`, props 200 `7bb143848d26…`, completion 200
  `ae60d20214b5…`, completion2 200 `b914757a9eff…`, bad_request 400 `b48f2e7e9f2e…`.
- teardown: SIGTERM rc=0 in 3 ms, `child_pre_dead=false`, `port_closed=true`, hold released.
- compact transcript with every capture hash and check state:
  `.ufo/waves/round-62/w1/out/W02KnowledgeDraft/run.txt`.

Facts the entry asserts, each read out of those captured bodies (not from the docs): the response
top keys are `choices, created, id, model, object, system_fingerprint, timings, usage`;
`object="text_completion"`; `model="kama-completion-probe"` (= `--alias`); `system_fingerprint`
`b11755-704366d76`; `usage` 8/8/16 plus `prompt_tokens_details.cached_tokens` 0 then 7;
`timings.predicted_n=8` and numeric `predicted_ms`; `choices[0]` keys `finish_reason ("length"),
index, logprobs (null), text`; both requests returned text `" ground. She liked"` while `id`,
`timings.cache_n/prompt_n` and `cached_tokens` differed; malformed request (no `prompt`) answered
400 `{"error":{"code":400,"message":"[json.exception.out_of_range.403] key 'prompt' not found","type":"invalid_request_error"}}`.

## Draft repairs (calibration record)

The file existed as an uncommitted attempt-1/inherited draft (mtime 2026-10-28 09:25:56). I did not
adopt its provenance on faith. Changes, each grounded in evidence above or in repo bytes:

1. **`source:` line** pointed at `.ufo/waves/round-62/measure/c1b/receipt.json`. That path does not
   exist at read time: `.ufo/waves/round-62/` holds `measured/` (singular receipt
   `c1-before-fix.txt`), `controls/`, `census/`, `assimilation/`, `w1/`, `live/`, `source/`,
   `hexrun-evidence/`; `find .ufo/waves/round-62 -maxdepth 3 -type d -name c1b` → empty. I replaced
   it with the receipt I actually produced and read, with its sha256, nonce and tool digest bound to
   the tip. S526's anchor (heading 1314, raw sha256) and the shared README section bound were also
   tightened: the "Timings and context usage" block is lines 1428-1471 (`*Reasoning support*`
   starts at 1472).
2. **`verified-at:` line** claimed `counter met=True`. I did not run the C1 counter (it is that
   claim's instrument, and its working-tree blob differs from the tip blob — see finding 2), so I
   state only what I executed: one hold-mode run, `REQUEST_OK`, 17/17, field claims read from its
   captured bodies.
3. **Determinism sentence** said a "byte-identical second request returns the identical
   `choices[0].text`", which can be misread as identical response bodies. Observed: request bytes
   identical, text identical, bodies differ (`id`, `cache_n`, `prompt_n`, `cached_tokens`). The
   entry now says the text is the invariant, and that the check is skipped (not passed) when
   temperature ≠ 0 (tool code, `completion_deterministic`).
4. **Observed-vs-documented split** was understated. The README's shared example does name
   `usage`/`timings` keys; it does not name this route's `object` literal, `model` echo or
   `system_fingerprint` (S526's teaches cell already says the receipt-side field contract is
   observed). The entry states both halves so it neither overclaims docs backing nor contradicts
   the registry row.
5. **Table precision**: each row now names whether the tool grades it, so "observed" fields
   (`prompt_tokens_details.cached_tokens`, `id`, `created`, `logprobs`, `index`, error message text,
   fingerprint value) are visibly ungraded; timing magnitudes are explicitly ungraded.
6. **Line-anchor preservation.** Sibling reports cite this file by line range (S03FrontierRecon:
   lines 5-17, 19-47, 41-46). I rewrote the content while keeping line 5 the H1, line 17 the end of
   the documented paragraph, line 19 the observed-contract heading, line 41 the non-invariants
   heading and lines 43-46 the text/consumer non-invariants, so those citations still point at the
   intended text. Verified with `cat -n`.

## Findings for the L1 (reported, not edited)

1. `corpus/lessons/round-62.md` Mistakes row 3 (reference-drift) cites the same absent receipt path,
   `.ufo/waves/round-62/measure/c1b/receipt.json`. At read time no such directory or file exists; the
   only measured artifact is `.ufo/waves/round-62/measured/c1-before-fix.txt`. Either the receipt is
   yet to be placed there or the lesson path needs correction — that file is not mine to edit.
2. `tools/round62-c1-counter.py` in the working tree differs from the tip blob
   (`275610b51eb1…` at tip vs `a3498308938e…` in tree; three hunks: `(cj or {}).get('usage'|'timings')`
   guards and `checks['hold_released']` instead of `checks['hold']`). I read the tip blob for the
   re-derivation statement and made no counter-verdict claim.
3. The draft is untracked at report time (`?? corpus/knowledge/completion-request-plane.md`,
   alongside `?? corpus/lessons/round-62.md`); integration/commit is the L1's, not mine.

## Bounds, tools, cleanup

- Work confined to the lane checkout plus scratch `/fast/scratch/hyaku/kama-r62/w/W02KnowledgeDraft`;
  every command named an absolute or scratch cwd; no git/jj mutation, no fixture repo, no fleet repo,
  no sibling lane, no `~/.local/bin` write, no `/home/vgpnk/Projects/shokuknow` access.
- Live run used only `tools/kama-completion-live.py` on an unregistered loopback port (41585); no
  registered consumer port was contacted; no process I did not spawn was signalled.
- No tools installed or upgraded (nothing was needed; pacman is paused host-wide and no transaction
  was attempted). No pacman/uv/npx/cargo/npm command ran.
- Scratch removed after copying receipts into the wave out dir: `rm -rf
  /fast/scratch/hyaku/kama-r62/w/W02KnowledgeDraft` (verified absent below).
- Not run, deliberately: `tools/round62-c1-counter.py`, `tools/round62-c2-counter.py`, any build or
  test suite — the C1/C2 measurements and verification belong to the instruments and the main agent.

tally: draft_lines=71 draft_sha=8ddd9d51… live_runs=1/1 exit=0 checks=17/17 captures=6 receipt_path_exists=1 stale_receipt_path_citations_removed=1 installs=0

## Full text of the draft (`corpus/knowledge/completion-request-plane.md`)

```markdown
source: S526 — llama.cpp server README @ 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad (release b11755), §POST `/v1/completions` lines 1314-1336 and §Timings and context usage lines 1428-1471, raw file sha256 714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37; own-work live receipt `kama-completion-live/v1` at `.ufo/waves/round-62/w1/out/W02KnowledgeDraft/receipt.json` (nonce `w02-r62-kn-draft-1`; tool `tools/kama-completion-live.py` sha256 71ac4f2c45570a79cb1e80db91e85268609f28bf4dd421d628ffb9d10243771f at tip 65d7cad0fce90e34de37527cde22e97b63b118bf)
verified-at: 2026-10-28 — one hold-mode run of that tip's tool on the pinned fixture (`llama-server` sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804, `stories260K.gguf` sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d, alias `kama-completion-probe`, unregistered loopback port): verdict `REQUEST_OK`, 17/17 evaluated checks passed; every response-field claim below is read from that receipt's captured bodies, not from the docs
recheck: 90d, and on any `llama-server` or model pin change — re-run `python3 tools/kama-completion-live.py --work <scratch> --hold-dir <hold> --nonce <fresh>` and require `REQUEST_OK` with `system_fingerprint` still `b11755-*`; a new build restarts this entry rather than inheriting it

# llama.cpp `/v1/completions` — the request plane

The lifecycle harness (`tools/kama-llamacpp-live.py`) proves the server *starts*
and answers inventory surfaces; this entry records what a real generation
request returns on the pinned b11755 single-model build.

## Documented contract (S526)

The README names `POST /v1/completions` as the OpenAI-compatible completions
route (heading, line 1314) and defers its options to the OpenAI Completions
API reference, making no strong compatibility claim; llama.cpp `/completion`-
specific features (e.g. `mirostat`) are supported. The shared "Timings and
context usage" example names `usage`/`timings`; the route field set is observed.

## Observed contract (receipt `kama-completion-live/v1`)

A `POST /v1/completions` carrying `{"prompt", "n_predict", "temperature": 0.0,
"seed": 7, "timings_per_token": false}` and no `model` field answers 200 with:

| Field | Observed contract |
|---|---|
| `object` | literal `"text_completion"`, not `"chat.completion"` (graded) |
| `choices[0].text` | the generated string; a string is graded, its content never |
| `choices[0].finish_reason` | `"length"` or `"stop"` (graded; `length` here at `n_predict` 8) |
| `model` | echoes the `--alias` value (`kama-completion-probe`), never the model file path |
| `system_fingerprint` | shape `b<digits>-<9-40 hex>` graded as shape only; observed `b11755-704366d76` |
| `usage.prompt_tokens` / `completion_tokens` / `total_tokens` | integers ≥1, total = prompt + completion (graded); `prompt_tokens_details.cached_tokens` present, ungraded |
| `timings.predicted_n` / `predicted_ms` | `predicted_n` an integer equal to `usage.completion_tokens`, `predicted_ms` numeric (graded); `cache_n`, `prompt_n` and the per-token rates ungraded |

Determinism at `temperature: 0.0` + fixed `seed`: two byte-identical requests returned the same `choices[0].text`; the bodies differ in `id`, `timings.cache_n`/`prompt_n` and `usage.prompt_tokens_details.cached_tokens`,
so only the text is the invariant — the check is skipped, not passed, when temperature ≠ 0.

Error surface: a request without `prompt` answers 400 with an `error` object —
`{"error":{"code":400,"message":"[json.exception.out_of_range.403] key 'prompt' not found","type":"invalid_request_error"}}` —
the tool grades status 400 or 500 plus `error` being an object, never the message text or its build-specific json-exception prefix.

## Non-invariants (never graded)

- **Text content.** Model quality is out of scope: the run grades the envelope
  and accounting only, so any completion string would pass the same checks.
- **Registered consumers.** The probe serves on an unregistered loopback port;
  consumer-facing endpoints are not contacted and their health is not sampled.
- **Timing values, ids, adapter extras.** Only `predicted_n`/`predicted_ms` presence is graded, never magnitude; `id`, `created`, `logprobs`, `index` and `prompt_tokens_details.cached_tokens` are recorded but ungraded.

## Receipt integrity

Every capture records `status`, `body`, `body_sha256` and `body_truncated`
(headers are not kept). The request-plane checks are `completion_envelope`,
`completion_finish_reason`, `completion_model_id`, `completion_fingerprint`,
`completion_usage`, `completion_timings`, `completion_deterministic` and
`bad_request_graded`; the same receipt binds the alias through
`listener_owned`, `models_alias_id` and `props_alias`. The round-62 counter
`tools/round62-c1-counter.py` re-hashes each body and recomputes every check
from captured bytes — a tampered field is rejected by grading, not trusted.

## Scope and open bounds

- One build, one model, one request pair: b11755 `llama-server` on
  `stories260K.gguf` with `-c 512 -t 1`. Other builds, models and contexts,
  other engines (Ollama, SGLang, vLLM) and the chat route are outside this entry.
- `stream` was not set, so this records the non-streaming JSON body only; SSE
  framing and per-token timings are not observed here.
- `PROVINCE.md` still lists `/v1/completions` as frontier at the tip (round-31
  core note line 141; round-32 note line 160). This entry records the observed
  contract; the round-62 C1 claim owns whether the capability is acquired.
- The receipt is one dated sample of the lane's own fixture, never present
  service state of a registered consumer.
```

tally: draft_lines=71 draft_sha=8ddd9d51… live_runs=1/1 exit=0 checks=17/17 captures=6 receipt_path_exists=1 stale_receipt_path_citations_removed=1 installs=0
