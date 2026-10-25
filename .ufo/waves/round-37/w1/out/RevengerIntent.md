# RevengerIntent — why the three C2 entries belong in kama's corpus

role: revenger (reconstruct, do not judge)
round: 37, attempt 1, wave 1
date: 2026-10-25
seat: L1Kama37.PeculiarAlligator
edits: none. Reads only. No fetch performed here (source reopening is delegated to
the FetchS333/S334/S335/S346/S363 seats in this wave).

Question assigned: *why do the three C2 entries belong in this lane's corpus at all*,
and does `corpus/README.md` already cover KV-cache/eviction/prefix-reuse ground.

Short answer: **the map does not cover it.** The lane holds the *names* of the cache
observables, the *capacity* of one engine's cache, and one *admission* valve, but no
model of what the numbers mean, no reclamation rule, and no reuse rule. The three
staged entries close that specific gap — reason attribution for what a served
endpoint answers — and nothing wider. They also carry six corpus-internal statements
that are already false against this lane's bytes (section 5); those, not the topic,
are the real admission risk.

---

## 1. What the three files are, and where they came from

The three files are one campaign thread, not three independent topics. Provenance,
read only (`/home/vgpnk/Projects/shokuknow/`, never written):

| step | campaign round | file | merged id(s) |
|---|---|---|---|
| 1 | corpus-expansion-1 | `kv-cache-reclamation-models.md` | S330, S333, S334, S335, S346 |
| 2 | corpus-expansion-2 | `prefix-cache-reuse-models.md` | S347 |
| 3 | corpus-expansion-3 | `prefix-cache-reuse-models-amendment-2026-10-23.md` | S363 |

- The campaign's own scout report asked the lane question
  "serving-stack internals (vLLM/SGLang-class schedulers, batching, KV-cache
  behaviour)" (`.ufo/scopes/corpus-expansion-1/ScoutKama.md:21,34`,
  `lanes/kama/DOMAIN.md:79`). That vocabulary is the campaign's; it is **not**
  kama's `PROVINCE.md` wording (section 4).
- Step 2 exists because the campaign recorded step 1 as asymmetric:
  `lanes/kama/CANNOT-ANSWER.md:6-16` — "The vLLM prefix-caching design page was
  never opened … without it, the entry … describes vLLM's only from its scheduler
  page — an asymmetry a reviewer will notice."
- Step 3 exists because step 2 quoted a superseded page: v0.9.0 says SHA256 is
  advised, v0.32.0 says it is the default since v0.11.
- Ids are all staged/campaign-provisional. Measured: `grep -c "^| S330 "` etc. over
  `corpus/SOURCES.md` at the working tip → **0** for all seven
  (S330, S333, S334, S335, S346, S347, S363); and over
  `git show 6a4afdfe…:corpus/SOURCES.md` → **0** for all seven. Both legs of C2's
  "present at tip, absent at base" requirement are currently unmet and are unmet
  trivially — nothing has been appended yet.
- One precedent matters: the same campaign package's entry 1,
  `serving-alias-contract.md`, was **already admitted** by this lane in round 35
  (`corpus/README.md`, "Coverage map — round 35 addition"; its row S196 is at
  `corpus/SOURCES.md:207`). So the thread is not foreign matter the lane has never
  touched; it is the remaining part of a question the lane has already answered
  once.

## 2. Does the coverage map already cover this ground? Measured: no

Every place in the lane corpus that mentions cache, eviction, prefix or prefill
(`grep -rniE 'kv[- ]?cache|prefix[- ]?cach|evict|radix|prefill|reclaim' corpus/`),
with what it actually holds:

| held artifact | what it holds | what it does **not** hold |
|---|---|---|
| `corpus/knowledge/context-capacity.md` | llama.cpp b11755 **KV pool vs per-slot ceiling**, fit raising an unset split context, pool total bounding concurrent requests, and the full-cache rejection chain (`try_clear_idle_slots` → batch halving → `Context size has been exceeded.` to every slot; S109/S133/S138; measured cells L1–L3) | any reclamation or reuse **policy**; its own "Does not establish" names "other engines" and "prompt caching" explicitly |
| `corpus/knowledge/serving-metrics-crosswalk.md:17` | the gauge **names**: `vllm:kv_cache_usage_perc`, `sglang:num_used_tokens`, `sglang:token_usage`, `sglang:cache_hit_rate` | what a hit *is*, so what any of these numbers mean |
| `corpus/knowledge/endpoint-health-probe-conventions.md` | a vLLM 503 can be a deliberate **admission** rejection (`--max-num-queued-reqs`, `--max-num-queued-tokens`; S327) | any resource-side cause: KV exhaustion, preemption, eviction |
| `corpus/knowledge/runtime-health-surface-matrix.md:15-16` | per-engine `/health` semantics (vLLM 503 only on `EngineDeadError`; SGLang `/health_generate`) | engine-internal state behind a passing health path |
| `corpus/knowledge/sglang-native-route-deprecation.md` | one published-route-vs-handler mismatch at v0.5.22 | anything about the radix tree |
| `corpus/knowledge/served-identity-crosswalk.md:28` | sleep mode unloads "the model and its associated memory (including the KV cache)" | eviction order, reuse, or the difference between engines |

Two structural confirmations:

- `corpus/README.md` contains exactly **two** matches for those tokens in 560 lines:
  line 327 (`prefix-ambiguity overwrite`, a git-defect term, unrelated) and line 395
  (the `context-capacity.md` coverage row). No coverage-map row, in any round, names
  KV-cache reclamation, eviction or prefix reuse.
- The README's **Known gaps** list (lines 50–60) names none of them either. So this
  is not a declared gap waiting its turn; it is an **unnamed** gap. The single place
  the corpus admits it is one sentence inside `context-capacity.md`'s
  "Does not establish": "other builds, other engines, router mode, context shift or
  prompt caching".

Of 27 `corpus/knowledge/*.md` entries, zero are about cache policy.

## 3. The gap reconstructed for the endpoint-health question

kama's boundary rule (`PROVINCE.md`): *is the thing at this baseURL the model this
config believes it is, right now* — never *is the model good* or *is the request
safe*. Within that rule, cache policy is in scope only where it changes **what the
endpoint answers**, and it does so in four ways the corpus cannot currently explain:

1. **Verdict attribution for 5xx.** The lane now distinguishes three rejection
   classes: llama.cpp loading 503 (`MODEL_LOADING`, KQ19), vLLM admission 503 (S327),
   llama.cpp shared-pool 500 `Context size has been exceeded.` (L1 cells). All three
   are "the process is up and refusing". Nothing in the corpus says *which resource*
   is exhausted or whether the refusal is recoverable. The reclamation entry supplies
   the two different answers: vLLM reclaims by **block-pool admission** (one token
   budget for prompt+output, chunked prefill on by default), SGLang by **radix-leaf
   eviction** (present, unlocked, unshadowed; lowest score first; LRU tie-break).
   A probe that wants to tell "saturated, retry elsewhere" from "misconfigured" needs
   that distinction; S327 only proves the first exists.
2. **Cache-hit observability.** The crosswalk publishes `vllm:kv_cache_usage_perc`
   and `sglang:cache_hit_rate` with no definition of a hit. The prefix entry supplies
   the definition that makes the gauge readable — and it is **not the same** on the
   two engines: vLLM hashes each block by its own tokens *plus* its whole ancestry
   and matches only on full blocks of an identical prefix; SGLang matches at any
   token boundary in the radix tree. So a `cache_hit_rate` reading, and any TTFT
   comparison across requests, is uninterpretable without naming the engine's match
   rule. This is exactly a "what does the probe number mean" fact, which is the
   lane's business.
3. **Served-answer correctness beyond model identity.** Two documented facts move the
   answer without moving the model id: (a) vLLM's pre-v0.11 default hash was not
   collision-free, so a multi-tenant deployment could reuse one tenant's cached KV for
   another's identical-hash prefix — the served model is unchanged and the served
   **ancestry** is not; (b) SGLang session references are "soft protection, not memory
   pins", and `session_id` labels cache references without carrying context, so a
   client that reads a session as continuity gets a silent re-prefill (latency), not
   an error. Both are failure shapes a metadata-only probe cannot see, and both are
   in-province because they are about what came back, not about quality or safety.
4. **Non-portability of the conclusion.** The lane documents vLLM and SGLang side by
   side in two entries already (`runtime-health-surface-matrix`,
   `serving-metrics-crosswalk`). Those tables are safe today *because* they are per
   engine. A "prefix caching" statement written without the engine name would not be —
   and the corpus has no entry that says so. That warning is the third file's job: the
   amendment is what keeps the second file from being read as a general rule.

So the entries close a **reason-attribution gap**, not a capability gap: they let the
lane explain, per engine and per pinned revision, *why* a healthy endpoint answered
slow, rejected, or re-prefilled instead of reused. They add no live observation, and
each says so in its own "What this entry does not establish" section.

## 4. Province test, stated plainly

`PROVINCE.md` lists surfaces: producer discovery, baseURL pins, served-model-id
reconciliation, liveness/readiness probe conventions, drift, consumer registry. It
does **not** list "serving-stack internals", and the campaign's `DOMAIN.md:79`
assertion that kama owns them is campaign-authored, not lane-authored.

The entries qualify under the lane's own established precedent, not under the
campaign's claim: from round 10 the lane has admitted **revision-pinned documentation
surfaces that determine how a served endpoint answers** —
`runtime-health-surface-matrix` (10), `serving-metrics-crosswalk` (10),
`gguf-runtime-compatibility-boundary` (10), request-field schema (28), the chat
conversion layer (31), the published-vs-current native route (36). Each is
documentation, explicitly not local integration. These three are the same kind: the
reclamation and reuse rules are the layer *below* the routes those entries already
hold.

What does not qualify, and should be fenced if the files land:

- **Eviction tie-break internals** (FCFS-vs-priority, LRU tie-break) are not
  observable through any kama surface — not `/health`, not `/props`, not `/slots`,
  not `/metrics`, and not the probe. They are context, not verdict-relevant ground.
- **The Chinese file map** (S346) is already labelled tier-B orientation in the entry
  and introduces nothing the loop relies on. It stays as orientation or not at all.
- **Cross-tenant KV reuse** is descriptive configuration fact. Framed as "is the
  request safe" it would cross into the province's explicit refusal; framed as "the
  served answer can carry another prefix's KV under this hash default" it stays.

## 5. Divergences — statements that are already false or unprovable against the lane

This is the part an admission decision must answer. Each row is checkable from the
committed bytes; none is a style complaint.

| id | statement in the staged file | measured against the lane | class |
|---|---|---|---|
| D1 | `ground:` cites "frontier item 'serving-stack internals (schedulers, batching, KV-cache behaviour)'" (all three files) | `grep -rn 'serving-stack internals'` over the lane repo → **0 hits**. The README's Frontier list is: source anchors, declared-vs-served context, non-author spot-check, operator/integrator prerequisites. The item exists only in campaign text. | false citation |
| D2 | "the lane held engine *surfaces* (metrics, health routes) but no documented account of *why* a served request is slow, rejected, or re-prefilled" | False for llama.cpp: `context-capacity.md` (round 25) holds the rejection chain and measured it (L1 both slots 500 at 1025 tokens; L2 200s). True only for vLLM/SGLang policy. | overstatement |
| D3 | "roughly one release line behind the versions the lane's other vLLM rows cite (v0.17.0, v0.19.1, v0.32.0)" | The lane's actual vLLM doc pins are `stable` ×4 (S002–S005), **v0.17.0** (S196, `corpus/SOURCES.md:207`), **v0.25.0** (S022, `:34`, per-request metrics), **v0.32.0** (S327, `:213`). No v0.19.1 row exists; v0.25.0 is omitted. | wrong list |
| D4 | "staged by round 2" / "Round 2's entry" / "wave 1 documented SGLang's…" | kama round 2 is `snapshot-history.md` + `lessons/round-2.md`. A reader of this corpus would resolve "round 2" to the lane's own round 2. | false reference |
| D5 | `recheck: … in SOURCES-PROPOSED.md` | `ls SOURCES-PROPOSED.md corpus/SOURCES-PROPOSED.md` → both absent; the file exists only in the read-only package (`shokuknow/lanes/kama/`). | unreachable recheck |
| D6 | amendment is a **separate** file | Corpus convention appends corrections inside the entry (KQ7: "every correction appended at the end of its file"; KQ26 names superseded text). A separate file is defensible only if the parent entry points at it; otherwise the parent's superseded SHA256 paragraph stands unmarked for anyone reading the parent alone. | convention conflict |
| D7 | S335 quotes "a node is evictable if its reference counter is zero" under `§RadixAttention` on `arxiv.org/abs/2312.07104` | The abs page is an abstract; the reference-counter rule reads as paper-body text. KQ45 requires the located quote at the anchored bytes. **[INFERENCE — not fetched here]**; FetchS335/FetchS346 are reopening. | unverified quote |
| D8 | provenance block carries `ground:`; `verified-at: 2026-10-23` | No lane knowledge entry has a `ground:` line (0 of 27); the lane's trio is source / verified-at / recheck. Harmless as content, but it is the only visible sign the file was not written from the lane's template. Also note C2's required filename keeps the staged date `2026-10-23` while the round lands on 2026-10-25 — the date must be read as the verification date, not the landing date. | format |

Also worth carrying into any gate: the amendment's own argument is *about a quote*.
If it is admitted while the parent's v0.9.0 paragraph is not visibly marked as
superseded in the parent, the corpus would hold a correction that no reader of the
corrected file can find — the same defect class round 36 fixed for route deprecation.

## 6. Confidence

| proposition | confidence | basis |
|---|---|---|
| The coverage map does not already cover KV-cache/eviction/prefix-reuse ground | **high** | full-corpus token grep, 27-entry inventory, README lines 327/395 only, Known-gaps list read in full |
| The README's gap is unnamed rather than declared | **high** | one sentence in `context-capacity.md` "Does not establish" is the only admission |
| The three files are one campaign thread, and one sibling entry from it was already admitted (round 35) | **high** | ScoutKama/CANNOT-ANSWER/DOMAIN + `README` round-35 row + `SOURCES.md:207` |
| The gap they close is verdict/reason attribution, not capability | **high** | four documented endpoint-facing consequences, each tied to a corpus line the lane lacks |
| In-province under the lane's documentation-surface precedent | **medium-high**; weakest for the eviction tie-break internals and the cross-tenant framing | PROVINCE surfaces + rounds 10/28/31/36 precedent |
| D2, D3, D4, D5 | **high** | derived from committed lane bytes |
| D7 (quote location) | **low / unknown** | not fetched by this seat, by design |

No admission verdict is stated in this report. The finding to carry forward is that
the topic is in-province and uncovered, while six of the staged lines are not yet
true of this lane's corpus; the copy cannot be a byte-copy for the same reason round
36 refused one.
