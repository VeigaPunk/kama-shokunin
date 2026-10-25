# kama round 37 lesson

author: kama L1, round 37
date: 2026-10-25
base: 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea

## Claims

C1 calibration 7 → 7. Predicate: A frozen r36-spotcheck routed statement is corrected iff corpus/lessons/round-37.md contains a correction row naming its id, the counter re-derives the cited committed-byte fact, the row carries no wrong-id restatement that its own statement forbids, and the r36 lesson blob and the r36 fleet report blob are unchanged. Counting command: `python3 tools/round37-statement-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip <full-commit>`.

C2 coverage 9 → 9. Predicate: The round-37 coverage block names each of knowledge/kv-cache-reclamation-models.md, knowledge/prefix-cache-reuse-models.md and knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md, every one of those files exists in corpus/knowledge/, and each cites an S-id present in corpus/SOURCES.md at the tip and absent at base 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea; none of those three holds at that base. Counting command: `python3 tools/round37-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip <full-commit>`.

Both predicates were frozen before scoring (`.ufo/waves/round-37/preregistration.json`). The do-nothing controls are `.ufo/waves/round-37/controls/c1-noop.out` (`uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False`, exit 1) and `.ufo/waves/round-37/controls/c2-base.out` (`named 0 files_exist 0 cited_new 0 met False`, exit 1). A control that met its target would have retired the counter before data.

MISSION.md:29 still says operability + freshness; shokunin.conf and the round prompt say operability + calibration. MISSION.md was not edited; the round-35 L0 question stays open. C1 works calibration because it is the lowest non-retired numeric axis (7). C2 works coverage on the same evidence surface the round-36 C2 measured, extended to three entries on new ground.

## Corrections

These four rows correct the statements the round-36 verifier routed. The round-36 lesson file and the round-36 fleet report are not rewritten; their blobs are pinned by the C1 counter.

R36-D1: The round-36 report cites `.ufo/waves/round-36/census-end.out` as the round-end census evidence at `report:147` and `report:232`, but the file was not tracked at the tip. The file is now committed under `.ufo/waves/round-36/census-end.out` (12426 bytes, tail line `kama\tok\t/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`), so the cited pointer resolves at closure. The report is not rewritten; the pointer now resolves.

R36-D2A: The round-36 Gate's admit paragraph cites S366 for the `native_api.mdx` staged row. That id is wrong: the staged row for `native_api.mdx` is S371, and S366 is the AWS SageMaker row. The id is miswritten in the lesson's prose; the decision the paragraph records (admit the native-API row) stands. The correction row names the right id, the document and the defect class.

R36-D2B: The round-36 Gate's code-page paragraph cites four ids as the `http_server.py` staged rows. All four are wrong: the staged rows citing that URL are S364, S365, S377 and S396. One URL takes one row; the four correct ids are the ones this correction names, and the wrong ids are absent from it.

R36-D3: The round-36 report's wave table accounts for 30 of 32 wave-3 seats. The two unaccounted seats are ScribeLog and RevQ206, both failed with `provider.rate_limit: 429` in their seat logs (RevQ206 had already fetched the S206 page and shipped a 4247-byte report). They are named here and in the round-37 report with their last error text; the seats the report already named are not restated here.

## Gate

Opened 2026-10-25 by the L1 and re-opened by wave-1 seats. Theme: engine internals that shape what a served endpoint answers — KV-cache reclamation and prefix-cache reuse models in vLLM and SGLang. Three admitted entries, seven registry rows, three rejects. The staged package under /home/vgpnk/Projects/shokuknow was read, never written.

Admit S330. URL https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/. Opened 2026-10-25, HTTP 200, 435441 bytes. Anchor: §Feature Support admonition note. Located quote (20 words): "vLLM V1's unified scheduler treats both prompt and output tokens the same way by using a simple dictionary" — and §Differences from V0 → Chunked Prefill: "Chunked prefill is enabled by default whenever possible, unlike in V0 where it was conditionally enabled based on model characteristics." (20 words). Used by corpus/knowledge/kv-cache-reclamation-models.md. Recheck 90d.

Admit S333. URL https://docs.sglang.io/docs/advanced_features/radix_eviction_policy. Opened 2026-10-25, HTTP 200, 296606 bytes. Anchor: §How eviction picks a victim. Located quote (12 words): "The policy scores each candidate and the lowest score is evicted first." Used by corpus/knowledge/kv-cache-reclamation-models.md. Recheck 90d. Same page: "Eviction only ever considers evictable leaves" — nodes whose KV is present, unlocked, and not shadowed by a child that still holds KV.

Admit S334. URL https://docs.sglang.io/docs/advanced_features/session_radix_cache. Opened 2026-10-25, HTTP 200, 277182 bytes. Anchor: lead paragraph under the page title (no heading). Located quote (20 words): "Session references are soft protection, not memory pins. Referenced KV can still be evicted when reclaiming unreferenced KV is insufficient." Used by corpus/knowledge/kv-cache-reclamation-models.md. Recheck 90d.

Admit S335. URL https://arxiv.org/abs/2312.07104. Opened 2026-10-25, HTTP 200, 43012 bytes (abs) and 214951 bytes (HTML full text, v1). Anchor: §5.1 RadixAttention. Located quote (10 words): "A node is evictable if its reference counter is zero." Used by corpus/knowledge/kv-cache-reclamation-models.md. Recheck 90d. Same paper: LRU eviction policy, cache-aware scheduling policy.

Admit S346. URL https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md (raw: https://raw.githubusercontent.com/AaronYang238/llm/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md). Opened 2026-10-25, HTTP 200, 36737 bytes. Anchor: §6.4.1 table lines 330-331. Located quote (5 words): "mem_cache/radix_cache.py RadixCache 基数树 prefix cache" (tier B, community file map; never tier A). Used by corpus/knowledge/kv-cache-reclamation-models.md. Recheck 90d.

Admit S347. URL https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html. Opened 2026-10-25, HTTP 200, 59059 bytes. Anchor: §Automatic Prefix Caching → Hashing, §Eviction (LRU). Located quote (17 words): "vLLM chooses a hash-based approach. Specifically, we hash each kv-cache block by the tokens in the block" — plus "We only cache full blocks" and the Note-2 collision caveat with SHA256 advice. Used by corpus/knowledge/prefix-cache-reuse-models.md. Recheck 90d.

Admit S363. URL https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/. Opened 2026-10-25, HTTP 200, 215347 bytes. Anchor: §Automatic Prefix Caching → Note 2. Located quote (13 words): "As of v0.11, the default hashing algorithm is sha256, which addresses collision risks." Used by corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md. Recheck 90d. Same page: `--prefix-caching-hash-algo` (sha256 default, sha256_cbor recommended for deterministic caching).

Reject `hosted-health-route-configuration-amendment-2026-10-23-r4.md` (staged, merge/kama/knowledge/corpus/knowledge/). Reason: it is a remote-platform deployment field — Google Cloud `serving_container_health_route`, SageMaker `AIP_HEALTH_ROUTE`, batch-transform lifecycle — and the lane's province assigns remote endpoint health to kake. Flip: a local container on this host whose configured health route differs from the engine route, observed by the lane's own probe.

Reject `openai-compat-host-vendor-contracts.md` (staged). Reason: it covers Alibaba Cloud and Baidu cloud-hosted endpoints (BASE_URL per region, workspace IDs, region-scoped model lists) — remote managed-platform vendor contracts, kake's province, not local serving. Flip: an in-province host vendor contract observed from a local deployment.

Reject `cross-literate-endpoint-venues.md` (staged). Reason: its Eastern-literature spine (S341-S345) covers Alibaba Cloud PAI, ARMS, ACK and unsloth guides — hosted cloud observability and deployment venues outside local endpoint health; S346 (the community source map) is carved out and admitted separately. Flip: the same questions decided from a source this lane owns or a local deployment.

### Quarantine hand-check (register not edited)

Slice derived with the operator recipe: `awk -F'|' -v l='kama' '$2 ~ ("`" l "`") && $3 ~ /round[0-9]+/ && $4 ~ /S[0-9]+/ {print $4, $5}'` over the campaign register. Seven kama rows, each carrying an S-id and class `payload-absent`. Verdicts (re-derived from the round-36 lesson's recorded verdicts; the register was not edited; no quarantine row is appended):

| id | verdict | reason | flip |
|---|---|---|---|
| S200 | absent | round-36 lesson records the quoted cell `DOI not in Semantic Scholar` does not occur on the page; fetch 2026-10-24 returned HTTP 200 | a located sentence from that page replaces the cell |
| S202 | present, not appended | docker compose services page carries `service_healthy`; no admitted entry cites S202 this round | an admitted entry cites it |
| S206 | present, not appended | Alibaba Cloud PAI EAS guide carries the span; out of local-serving province | an in-province entry cites it |
| S210 | absent | unsloth guide is reachable but `Page Not Found` cell is not on the page | the cell is replaced by a located span |
| S211 | absent | the chapter is reachable but `still-live` occurs nowhere | a located span from that chapter replaces the cell |
| S224 | quote not located | vLLM health API page carries `check_health()` and 503 but not `render-only servers always return 200` | the compound cell is split and each half re-quoted |
| S230 | present, covered by lane's own row | the lane's S329 carries the same URL, anchor and admitted entry | a later round needs a second, differently-anchored row |

### Id collision (scratch, before any append)

Registry ids 203, staged ids 142 (S325 to S458), collisions 0. The 0-3 leading-space guard was re-proven on the indented-row fixture (`  | S330 |` → collision caught) and on the real lists (`comm -12` empty). The seven adopted rows take the lane's next ids S330, S333, S334, S335, S346, S347, S363 — they are the staged ids carried by the same documents, and the lane registry has no row with any of those ids. Renumber map: none required; each adopted row's id follows its document, never arithmetic.

### Validate-before-append (scratch)

The mirror is a plain copy of the lane tree plus the seven normalized rows inside the Registry table (immediately after the S329 row) and the three admitted knowledge files at their repo-relative paths. `sources-census.sh validate --file <mirror>/corpus/SOURCES.md` exited 0 with the pre-existing W04 duplicate-url warnings and no E finding. Receipt: `.ufo/waves/round-37/w1/out/ExecValidate.md`.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| id-drift | corpus/lessons/round-36.md's Gate cites five staged ids that do not resolve (S366 → S371; S359/S360/S372/S391 → S364/S365/S377/S396; "cites S331-S334" → S332/S336/S337/S338/S339) — corpus/lessons/round-36-verifier-spotcheck.md §6 item 2 | none — the round-36 Gate was written from the staged package's own cells without re-deriving each id | KQ46: a foreign or staged id range cited in a lesson is a claim; re-derive every id against the named artifact before citing it; a copied range that misnames ids is a correction target, never a citation |
| misroot | the wave-1 seat MutD3 wrote its report to the fleet root `.ufo/waves/round-37/w1/out/MutD3.md` instead of the lane path; it was copied byte-exact into the lane, `cmp`-verified, and the fleet copy deleted | none — this round's seat context did not forbid the fleet-root write explicitly enough | wave contexts name the exact lane-absolute report path, and the misroot sweep (git status at fleet root) runs before every report lands |

## Frontier

considerthese/2026-10-24.md proposals: proposal 1 is already KQ44, proposal 2 already KQ45, proposal 3 (prepared-not-dispatched ledger) and proposal 4 not taken; the file was not edited. KQ46 is added this round as the criterion that captures the id-drift class above.

## Wave evidence

Wave 1 (37 seats, v1): reviewer 10, scout 10, critic 5, scribe 4, mutation-tester 3, executor 3, connector 1, revenger 1. Reports under `.ufo/waves/round-37/w1/out/`. All seven sources opened by both the L1 and at least one seat; seat fetches recorded HTTP 200 with byte counts and sha256 sums.
