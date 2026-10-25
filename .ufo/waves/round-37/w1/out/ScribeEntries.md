# ScribeEntries — round-37 w1, three C2 entry drafts (seat: `L1Kama37.AssistantToucan`)

Behavior: copied the three staged C2 knowledge files into the seat directory, re-opened
each cited source with a read-only GET, and rewrote the provenance block of every draft
(`source` ids + URLs + a section anchor that exists on the fetched page, `verified-at
2026-10-25`, a runnable `recheck` command, an honest `ground` line). Body claims were
kept from the staged bytes where the fetched page carries them and deleted where it does
not. Nothing was written to `corpus/knowledge/` or to any other corpus path.

## Drafts (one line each)

| draft (seat path) | one-line summary |
|---|---|
| `kv-cache-reclamation-models.md` | SGLang defines reclamation over a radix tree of scored evictable leaves with session references as soft protection, while the cited vLLM V1 page documents unified token-budget admission and a prompt-logprobs prefix-cache bypass but no eviction rule — so no vLLM eviction model is asserted. |
| `prefix-cache-reuse-models.md` | vLLM v0.9.0 keys each kv-cache block by its tokens plus the parent prefix hash, caches only full blocks, advises SHA256 for multi-tenant use and evicts LRU — a block-pool model that does not carry over to SGLang's radix tree. |
| `prefix-cache-reuse-models-amendment-2026-10-23.md` | the v0.9.0 SHA256 advice became the default at v0.11 (`--prefix-caching-hash-algo`, sha256 default, with its own reproducibility caveat), so the sibling entry's collision caveat is historical, not a current obligation. |

## Provenance block per draft

| draft | `source:` ids (all re-opened 2026-10-25) | version / revision marker actually on the page | `recheck` (90d) — command, observed count |
|---|---|---|---|
| kv-cache-reclamation-models.md | S330, S333, S334, S335, S346 | S330 `readthedocs-version-slug` v0.19.1; S333/S334 `originalFileLocation` mdx + `lastModified 2026-10-24T12:16:03.909Z`, **no commit pin**; S335 arXiv:2312.07104v1; S346 commit `35b83cee…03907` | S330 `grep -c 'unified scheduler'` = 1; S333 `'lowest score is evicted first'` = 2; S334 `'soft protection, not memory pins'` = 2; S335 `'reference counter is zero'` (html v1) = 1; S346 `'radix_cache.py'` = 3 |
| prefix-cache-reuse-models.md | S347 | `readthedocs-version-slug` v0.9.0 | `grep -c 'hash-based approach'` = 1 |
| prefix-cache-reuse-models-amendment-2026-10-23.md | S363 | `readthedocs-version-slug` v0.32.0 | `grep -c 'sha256'` = 3 |

Axes this is meant to serve: coverage (the three files the frozen C2 predicate names),
with the calibration-relevant part being that each `source:` anchor is a section that
exists on the fetched page rather than the staged label.

## Fetches (read-only GET, one per named URL, plus one full-text follow-up)

| url | HTTP | bytes | saved as |
|---|---|---|---|
| https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/ | 200 | 435441 | `S330.html` |
| https://docs.sglang.io/docs/advanced_features/radix_eviction_policy | 200 | 296606 | `S333.html` |
| https://docs.sglang.io/docs/advanced_features/session_radix_cache | 200 | 277182 | `S334.html` |
| https://arxiv.org/abs/2312.07104 | 200 | 43012 | `S335.html` |
| https://arxiv.org/html/2312.07104v1 (the staged anchor's full text) | 200 | 214951 | `S335v1.html` |
| https://raw.githubusercontent.com/AaronYang238/llm/35b83cee…/chapters/06-…引擎.md | 200 | 36737 | `S346.md` |
| https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html | 200 | 59059 | `S347.html` |
| https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/ | 200 | 215347 | `S363.html` |

No other network call was made. No tool was installed or upgraded.

## Claims deleted from the staged bytes (source does not carry them)

1. `"every request must still carry its full intended prompt"` — S334 says "each request
   must still contain the intended prompt"; the draft quotes that, not "full".
2. `"chunked prefill is on by default"` — S330 says "enabled by default **whenever
   possible**, unlike in V0"; the qualifier is restored.
3. `"Reclamation is therefore block-pool and admission-shaped, not tree-shaped"` (vLLM) —
   S330 documents allocation and admission, never reclamation. Replaced by an explicit
   statement that no vLLM eviction model is asserted, plus the one cache-bypass
   consequence the page does state.
4. `"where a collision would serve one tenant's cached KV to another"` — neither the
   v0.9.0 nor the v0.32.0 page says that; the SHA256 advice is quoted bare.
5. `"SGLang can match a shared prefix at any token boundary"` — rests only on the
   community source S346; the prefix draft now contrasts hash-keyed block pool vs radix
   tree without that claim.
6. `"roughly one release line behind the versions the lane's other vLLM rows cite
   (v0.17.0, v0.19.1, v0.32.0)"` — the registry's other vLLM rows are v0.17.0 (S196),
   v0.25.0 (S022) and v0.32.0 (S327); v0.19.1 is this round's own S330. Corrected.
7. `"any deployment older than that is still governed by the v0.9.0 wording"` (amendment)
   — neither page states it; the draft says the page states no such rule.
8. `"with LRU as the tie-break"` — **kept**: S333 carries "All of them fall back to
   least-recently-used order within a tie", and `lru` is the documented default.
9. Section anchors that do not exist: `§Scheduler` → `§Feature Support` state-legend note;
   `§Eviction candidates` → `§How eviction picks a victim`; `§Session references` → the
   page lead paragraph; `§6.4 RadixAttention` → `§6.4.1` table + `§6.4.2`.
10. `"staged by round 2"` / `"Round 2's entry"` (amendment header) — there is no lane
    round 2 entry of this name; the amendment now points at the sibling file and says the
    `2026-10-23` in its name is a filing date.
11. Staged `ground:` lines naming a frontier item `"serving-stack internals (schedulers,
    batching, KV-cache behaviour)"` — that string does not exist in `corpus/README.md`
    (base grep count 0). Not copied.

## Additions, each carried by an already-cited page

1. S334 §Eviction behavior ordering: "Unreferenced nodes first, then referenced nodes with
   fewer session references, then the configured policy such as LRU".
2. S330 §Prompt Logprobs with Prefix Caching: "the engine will ignore the prefix cache and
   recompute the prefill of full prompt to generate the logprobs" — the one served-request
   consequence the vLLM page states.
3. S363's caveat on its own new default: sha256 "Uses Python's pickle for serialization.
   Hashes may not be reproducible across different Python or vLLM versions".

## `ground:` lines — the coverage-map gap, measured

- `git show 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea:corpus/README.md | grep -c -i
  'radix\|prefix-cache\|prefix cache\|reclamation\|eviction'` → **0**.
- same blob, `grep -c -i 'hashing algorithm\|prefix-cache default\|sha256'` → **0**.
- same blob, `grep -c 'serving-stack internals'` → **0** (exit 1).
- nearest existing row: `knowledge/context-capacity.md`, "the KV pool versus the per-slot
  ceiling …" — llama.cpp capacity on the lane fixture, not reclamation policy or reuse.

Each draft therefore states the gap as a measured absence of a coverage-map row and says
in so many words that the round's theme phrasing is the assignment's, not a label already
in the corpus. No draft claims to close a listed frontier item.

## C2 relevance and what is not done here

Each draft cites at least one id that is absent at base `6a4afdfe…` and is adopted this
round: `S330/S333/S334/S335/S346` (kv), `S347` (prefix), `S363` (amendment). The registry
rows themselves are not mine to write: at the time of writing, `grep -n 'S330\|S333\|S334\|
S335\|S346\|S347\|S363' corpus/SOURCES.md` returns nothing in the lane working copy, so
`tools/round37-coverage-audit.py` cannot yet score `cited_new` against these files until
the ScribeAppend/ExecValidate rows land at the tip. I did not append, mirror, or run any
campaign tool.

## Gates and limits

- Not run here: `tools/round37-coverage-audit.py`, `tools/round37-statement-audit.py`,
  `sources-census.sh`, any build/lint/test. Main agent's call.
- The drafts sit outside `corpus/knowledge/` by design; promoting them is a different
  seat's edit.
- S333/S334 have no commit pin, so the drafts say so and lean on `lastModified` plus the
  recheck commands; a rendered page can change under the same URL.

## Artifact paths (all under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-37/w1/out/L1Kama37.AssistantToucan/`)

- `kv-cache-reclamation-models.md` (7406 B, sha256 `c4e8c637afc5bf423548ae8b203313683e1f8cad3b74dfa44b0889722720fd67`)
- `prefix-cache-reuse-models.md` (3480 B, sha256 `a0d8638675fbebf867cdb88a4d7c14918c2588c973bfd2a815ad91d9396806a1`)
- `prefix-cache-reuse-models-amendment-2026-10-23.md` (3120 B, sha256 `cc6d504b8e99c329659f1f8335b5d47b5d9753ecfd703834f95a6edbcbc10df0`)
- `staged-kv-cache-reclamation-models.md` (3533 B, sha256 `43c56573b3733cae3d003f4b1abbb8b143cc565c7376e1e22a2c1ef3189edf91`)
- `staged-prefix-cache-reuse-models.md` (2363 B, sha256 `ac4da02e09cc06629431e47ee1f68e4ac3711109a7e0e3bdda1b00ff90c56f34`)
- `staged-prefix-cache-reuse-models-amendment-2026-10-23.md` (2155 B, sha256 `928bd8c83a4c23802751743b0c0fb01e5d0ed21a4a9eda06f0af3e091944fe64`)
- fetched bytes: `S330.html`, `S333.html`, `S334.html`, `S335.html`, `S335v1.html`,
  `S346.md`, `S347.html`, `S363.html` (1 578 335 B total)

The three `staged-*` files are byte copies of the package files, kept only so the diff
between staged and adopted text is auditable in the seat; the package itself was read,
never written. The draft hashes were taken after the last edit and no later write touched
those three files.
