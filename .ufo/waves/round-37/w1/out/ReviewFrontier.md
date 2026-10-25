# ReviewFrontier — does corpus/README.md already cover KV-cache reclamation or prefix-cache reuse?

Verdict: **no.** Zero README rows cover the ground the three C2 entries occupy. Two rows are
adjacent (cache-usage metric names; llama.cpp KV-pool capacity); two more are false friends
("scheduling handoff", git "prefix-ambiguity"). The Frontier and Known-gaps sections never name
this theme at all. No file was edited.

## What was grepped, and the exact census

Worktree `corpus/README.md` (560 lines) is byte-identical to the frozen base README:

```
$ git diff 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea -- corpus/README.md
(empty)
```

Term census over the whole file (case-insensitive, `grep -n -i -- <term>`):

| term | matching lines |
|---|---|
| `KV` / `kv` | 395 |
| `evict` | none |
| `prefix` | 327 |
| `radix` | none |
| `schedul` | 41 |
| `batch` | none |
| `reclaim` | none |
| `reuse` | none |
| `cache` | 91 |

Line 41 is `knowledge/snapshot-history.md` ("persistence boundary, scheduling handoff");
line 91 is `knowledge/serving-metrics-crosswalk.md` ("TTFT/TPOT/queue/cache boundaries");
line 327 is the round-23 frontier note ("prefix-ambiguity overwrite", git repo safety);
line 395 is `knowledge/context-capacity.md` ("the KV pool versus the per-slot ceiling").

## The ground actually claimed by the three C2 entries

From the read-only staged bytes (`/home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus/knowledge/`):

- `kv-cache-reclamation-models.md`: vLLM V1 scheduler treats prompt and output tokens from one
  fixed per-request token budget (which is what makes chunked prefill possible, on by default);
  policy FCFS or priority with FCFS tie-break; reclamation is block-pool and admission-shaped.
  SGLang: radix tree, only *evictable leaves* (present, unlocked, not shadowed by a child holding
  KV), lowest score evicted first with LRU tie-break; a node is evictable iff its reference count
  is zero; session references are soft protection, not memory pins.
- `prefix-cache-reuse-models.md`: vLLM hashes each KV block by its own tokens *plus* the preceding
  prefix (ancestry hash), reuses only on exact full-block prefix match, LRU eviction, hash is not
  collision-free.
- `prefix-cache-reuse-models-amendment-2026-10-23.md`: as of vLLM v0.11 the default hashing
  algorithm is SHA-256, so the multi-tenant advice became the default; mechanism unchanged.

## Row-by-row: what the README rows hold versus that ground

| README row | What it actually states | Relation to the three entries |
|---|---|---|
| `:91` `serving-metrics-crosswalk.md` — "metric names and TTFT/TPOT/queue/**cache** boundaries (llama.cpp, vLLM, SGLang, OTel GenAI)" | The entry body (`knowledge/serving-metrics-crosswalk.md:17`) gives **metric names only**: `llamacpp:n_tokens_max` (context high watermark, not live KV use), `vllm:kv_cache_usage_perc`, `sglang:num_used_tokens` / `sglang:token_usage` / `sglang:cache_hit_rate` | Observability vocabulary, not mechanism. It names a pool-occupancy gauge and a hit-rate counter without stating what a "hit" is (block-hash exact match vs radix prefix), when a block is evicted, or what a session reference does. The word "cache" in the row is a measurement boundary, not a reclamation or reuse model. |
| `:395` `context-capacity.md` — "the **KV pool** versus the per-slot ceiling, fit raising an unset split context, the pool total bounding concurrent requests" | llama.cpp `n_ctx` pool sizing, split vs unified cache, `--kv-unified-per-slot`, fit interactions; live fixture b11755 | Same engine family as the entries' *subject matter* only in the loose sense: it is **llama.cpp**, not vLLM or SGLang. It sizes the pool; it does not model eviction or prefix lookup. Note the entry body does hold a llama.cpp no-free-KV path (`knowledge/context-capacity.md:132-134`: purge idle slots still holding a cached prompt, else halve the batch, else `Context size has been exceeded`) — but that is the *llama.cpp* reclaim/retry path, the README row does not say so, and it was measured with `cache_prompt` false (`:123`, `:169-171`), i.e. prefix reuse was deliberately not exercised. |
| `:41` `snapshot-history.md` — "scheduling handoff" | invocation-to-invocation state handoff between probe snapshots (round 2) | False friend. Not the request scheduler, not batching, not KV. |
| `:327` round-23 frontier note — "prefix-ambiguity overwrite" | git object/ref prefix ambiguity in the report auditor | False friend. A string collision on the word "prefix", unrelated to prefix caching. |
| `:540-541` `serving-alias-contract.md` / `served-model-id-resolution.md` | "served-name and alias resolution"; "served model id read from a local listing" | No cache text in the row. Adjacent only outside the README: the entry body (`knowledge/serving-alias-contract.md:29`) and `SOURCES.md:208` (S205) name `/reset_prefix_cache` (vLLM) and `/flush_cache` (SGLang) as a benchmark client's cache-management endpoints. That is an endpoint name, not the reuse model. |
| `:546-558` round-36 addition | SGLang `/get_model_info` deprecation at v0.5.22 | Route publication, not cache. |

Framework sections:

- **Known gaps (`:49-64`)**: stale operator pins, invocation cadence, Windows/Podman absence,
  "real-runtime reconciliation is proven for llama.cpp only … vLLM/Ollama-shaped fixtures pass,
  but neither runtime is installed" (`:60-62`), historical context size, no remote endpoint health.
  The vLLM/SGLang-install gap is a *runtime integration* gap; it does not name schedulers,
  batching, eviction or prefix reuse.
- **Frontier (`:66-75`)**: source anchors, declared-vs-served context, non-author spot-check,
  operator prerequisites. Reprised in per-round dispositions as "other engines", "router mode",
  "K05", "registered-consumer reconciliation" — router mode at `:407`, other
  engines/builds at `:430`/`:480`/`:527`, K05 at `:462`, consumers at `:480`/`:527`.
  "Other engines" is an engine-name gap, not an engine-internals gap.
- Greps over the whole lane for `kv-cache|prefix-cache|radix|evict|paged|cache_prompt` outside the
  README return only: the metrics row above, `context-capacity.md` (llama.cpp), `serving-alias-contract.md`
  (`/reset_prefix_cache`), `SOURCES.md` S109/S113/S135/S138 (llama.cpp KV-cache code and the
  KV-cache-full decode path) and S205. `SOURCES.md` holds 203 registry rows and **no**
  radix/prefix-cache/eviction design row.
- `considerthese/` (operator-authored, 2026-10-19..24) contains no `kv`, `prefix cache`, `radix`,
  `scheduler` or `batching` term.

## Findings

### F1 — MEDIUM — the entries' cited ground does not exist in the README

All three staged entries claim `ground: frontier item "serving-stack internals (schedulers,
batching, KV-cache behaviour)"`. That phrase occurs nowhere in `corpus/README.md` (`grep -n -i internals`
→ none), nowhere in `Known gaps` or `Frontier`, and nowhere else in the lane except the staged
entries themselves and one seat's copy
(`.ufo/waves/round-37/w1/out/ScoutGate/validate-b/corpus/knowledge/*.md:7,11`). So the attribution
is to a frontier item the lane has not written down. Consequence for the claim: "uncovered" here
means the theme is new to the README *as well as* to the corpus; the round-37 block is the first
place it appears, and the block must introduce the frontier line rather than point at one.

### F2 — MEDIUM — the C2 counter scores a commit, not the working tree

`tools/round37-coverage-audit.py:103-107` (`load`) reads
`git show <tip>:corpus/README.md` at `:104`; `block_names` (`:61-67`) requires the literal heading
`## Coverage map — round 37 addition`. Current tree topology is a trap:

- `git status --porcelain corpus/README.md` → ` M` (modified vs HEAD).
- `git diff --stat 6a4afdfe…HEAD -- corpus/README.md` → `16 deletions`; the worktree adds the
  deleted round-36 block back. HEAD (`873c5d7774b97e7c633052456f13595a2ea5775f`) is a
  **sandbox mutation branch** (`mut1..mut4 … (sandbox only)`), and
  `git merge-base --is-ancestor 6a4afdfe HEAD` fails.
- `grep -n 'Coverage map — round 37\|round 37' corpus/README.md` → no match.

Therefore a round-37 block that exists only as a working-tree edit scores `named 0` no matter how
correct it is. Measured at the real base, read-only, identical to the frozen control:

```
$ python3 tools/round37-coverage-audit.py --repo . --tip 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea
named 0 files_exist 0 cited_new 0 met False
exit=1
```

`--tip` must be a full commit on the base lineage when C2 is finally scored; HEAD as it stands is
not that commit.

### F3 — LOW — the name leg is substring presence, so it cannot certify that a row means anything

`block_names` counts whether each `knowledge/…` path string appears anywhere between the heading
and the next `\n## ` (`:61-67`). A prose sentence such as "see knowledge/prefix-cache-reuse-models.md"
inside the block counts; so would a sentence naming a path as *rejected*. The do-nothing control
only shows the empty case is False. The substantive leg is `cited_new` (`:82-101`, `score`): each entry must
cite an S-id present in `SOURCES.md` at the tip and absent at base. Given the current SOURCES state
(no radix/prefix row; only S205's cache-management endpoints), that leg is real work and is the
honest part of C2; the `named` leg is shape only.

### F4 — LOW — row wording at `:91` can be read as cache-internals coverage

"queue/cache boundaries" is a metrics-scope phrase, but it sits in the same table as the round-37
rows and says "cache" next to vLLM and SGLang. The round-37 rows should make the split explicit
(observability names vs mechanism), otherwise a reader can conclude the SHA-256-default correction
belongs to the metrics entry rather than to a new mechanism entry.

## What "uncovered" means for the claim

1. **Mechanically**: no existing row can be repointed or extended to satisfy C2 — `named` counts
   only inside the new heading, and `files_exist`/`cited_new` count only the three named files.
   README absence is therefore *necessary* right now (the measured 0/0/0 at
   `6a4afdfe`) but it is **not part of the predicate**: the counter never compares new rows against
   old rows. C2 can be met without demonstrating that no prior row held the ground; that
   demonstration is this report's job and it is the argument, not the counter, that establishes it.
2. **Burden of novelty** falls on PROVINCE and QUALITY, not on C2. `PROVINCE.md` "Owns (surfaces)"
   lists producer discovery, baseURL pins, served-model-id reconciliation, liveness/readiness,
   drift, consumers — no scheduler or cache-internals surface; the domain sentence is "local model
   serving & endpoint health". `corpus/QUALITY.md` has no engine-internals admission bar (its KQ
   rows govern provenance, append-only supplements, duplicate discrimination). Admitting the three
   entries as coverage therefore expands the held corpus at the documentation tier; it does not
   touch an existing owned surface.
3. **Honest limit of the achieved clause**: each staged entry ends with its own non-establishment
   section — no eviction, prefill or latency behaviour observed on this host; the vLLM page is a
   design document roughly one release line behind the versions other lane rows cite; no measured
   cache-hit rate; the SGLang session-reference rule is documentation, not a probe. So the C2 block
   may honestly say "documented models of why a served request is slow, rejected or re-prefilled",
   and must not say the endpoint's behaviour is now explained or measured. Coverage (9 -> 9) gains
   breadth of documentation; operability gains nothing, and no endpoint sample exists.
4. **Consequence for the round-37 block's cells**: a `Covers` cell that restates only the mechanism
   would be accurate; one that says the row establishes eviction behaviour, hit rates, or an
   explanation of a live request's latency would be false against the entries' own limit sections
   and would contradict `README.md:9-11` ("every knowledge/ entry is a dated census record of what
   was observed on its citation date").

## Residual risk and verification gaps

- I did not construct a synthetic round-37 block or run the counter against a hypothetical tip;
  F2/F3 are derived from reading `block_names`/`cited_ids`/`registry_ids` and from the measured base
  state, not from a mutant run. A mutation seat can confirm F3 cheaply.
- I did not verify that the S-ids in the staged entries (S330, S333, S334, S335, S346, S347, S363)
  are registered with the exact anchors the entries quote; other wave-1 seats are fetching those.
  What is verified: none of them is in `SOURCES.md` at the current tip (203 rows; radix/prefix/evict
  grep returns only S205), so the `cited_new` leg requires genuine registry additions.
- I did not exhaustively audit prose in `SCORECARD.md`/`LOG.md`; the targeted grep
  (`kv.?cache|prefix.?cache|radix|evict|scheduler|batching`) returns only three unrelated
  uses: `SCORECARD.md:24` ("round-2 scheduler decision handed to L0" — a cross-lane decision,
  not a request scheduler), `LOG.md:109` ("no scheduler was installed" — the snapshot timer)
  and `LOG.md:640` ("routing change, scheduler or upstream push" — kumitate routing). None
  claims cache-internals coverage. The lane-wide grep for the cited frontier phrase
  (`serving-stack|KV-cache behaviour`) likewise finds it only in copies of the staged entries.
- Scope: README-only per the item. `PROVINCE.md`/`QUALITY.md` were opened only to say where the
  novelty burden falls, not edited.

No files were edited; this report is the only write.
