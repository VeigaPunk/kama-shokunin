# Round-37 w1 — normalized SOURCES append block (kama lane)

Seat: `L1Kama37.MagneticAphid` (scribe). Scope: draft only — no lane corpus file was written.

## 1. Behaviour / deliverable

Normalized fleet-schema rows for the seven staged sources S330, S333, S334, S335, S346, S347, S363,
converted from `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` (read-only package) into
the lane's `SOURCES-CONTRACT-v1` registry shape: eleven columns
`id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`.

The block is append-ready and belongs **inside the `## Registry` table**, immediately after the current
last row `| S329 |` (working copy line 215), before the blank line and `## Paths` (line 217).
Placing these rows after the last `##` section instead would reproduce the round-31 defect
(`row outside Registry section`, `corpus/lessons/round-31.md` §Mistakes row 4), so the rows carry no
heading of their own.

Machine-readable draft: `.ufo/waves/round-37/w1/out/L1Kama37.MagneticAphid/registry-rows.md` (7 lines).

## 2. The block (verbatim)

```
| S330 | vLLM V1 Guide — https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/ | docs | A | vLLM V1 scheduling and batching model as the project documents it; not a runtime observation | §Scheduler — "V1's unified scheduler treats both prompt and output tokens the same way"; §Chunked Prefill — "Chunked prefill is enabled by default whenever possible"; docs page version v0.19.1 | one token budget spans prompt and output tokens; chunked prefill is on by default; FCFS or priority scheduling via `--scheduling-policy` | mined | 2026-10-25 | 90d | corpus/knowledge/kv-cache-reclamation-models.md |
| S333 | SGLang Radix Eviction Policy — https://docs.sglang.io/docs/advanced_features/radix_eviction_policy | docs | A | the SGLang KV-cache reclamation rule; engine-internal, carries no endpoint semantics | §Eviction candidates — "The policy scores each candidate and the lowest score is evicted first."; source docs/docs/advanced_features/radix_eviction_policy.mdx @ sgl-project/sglang 77091cea68d0701d6cc71edfb45f2815c4f8d791 (2026-09-29) | only evictable leaves are candidates (unlocked and not shadowed by a child still holding KV); the lowest score goes first; a policy scores but cannot pin KV | mined | 2026-10-25 | 90d | corpus/knowledge/kv-cache-reclamation-models.md |
| S334 | SGLang Session-Aware Radix Cache — https://docs.sglang.io/docs/advanced_features/session_radix_cache | docs | A | SGLang session-reference semantics; a session is not a KV pin | §Session references — "Session references are soft protection, not memory pins."; source docs/docs/advanced_features/session_radix_cache.mdx @ sgl-project/sglang d34f7b2326a10cb5f3ba8ec95efb31c761237750 (2026-09-22) | referenced KV can still be evicted; the `session_id` labels cache references only and does not append or reconstruct conversation context | mined | 2026-10-25 | 90d | corpus/knowledge/kv-cache-reclamation-models.md |
| S335 | SGLang: Efficient Execution of Structured Language Model Programs — https://arxiv.org/abs/2312.07104 | paper | A | the primary statement of RadixAttention's evictability rule; historical, revision-free by arXiv id | §RadixAttention — "A node is evictable if its reference counter is zero."; arXiv:2312.07104 (abs page) and arXiv:2312.07104v1 (HTML full text) | nodes used by the running batch are protected by a per-node reference counter; LRU eviction recursively removes leaf nodes; cache-aware scheduling sorts the queue by matched prefix length | mined | 2026-10-25 | 90d | corpus/knowledge/kv-cache-reclamation-models.md |
| S346 | llm 教程 第 6 章 推理引擎 — https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md | community | B | Chinese reverse-engineering write-up of vLLM and SGLang internals; reproducible file-level detail the upstream docs do not present as a source map, but not authoritative for engine behaviour | §6.4 RadixAttention — "`mem_cache/radix_cache.py` `RadixCache` 基数树 prefix cache" and "`managers/schedule_policy.py` `SchedulePolicy` LPM 等调度策略" | a Chinese-language source map contrasting vLLM's flat hash-chain prefix cache with SGLang's radix tree, naming the concrete source files that implement each | mined | 2026-10-25 | 90d | corpus/knowledge/kv-cache-reclamation-models.md |
| S347 | vLLM Automatic Prefix Caching (design) — https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html | docs | A | vLLM's own prefix-cache design at v0.9.0: how a kv-cache block is keyed and which blocks are reusable; the design page, not an observed runtime | §Automatic Prefix Caching → "Hashing" — "vLLM chooses a hash-based approach"; §Eviction (LRU); docs page version v0.9.0 | each kv-cache block is hashed by its own tokens plus the tokens of the prefix before it, so reuse requires an exact prefix match; only full blocks are cached; the hash key is not collision-free and SHA256 is advised for multi-tenant use | mined | 2026-10-25 | 90d | corpus/knowledge/prefix-cache-reuse-models.md |
| S363 | vLLM Automatic Prefix Caching (design), current documentation line — https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/ | docs | A | vLLM's prefix-cache design at the current documentation line, including the hashing default that changed after v0.9.0 | §Automatic Prefix Caching → Note 2 — "As of v0.11, the default hashing algorithm is sha256, which addresses collision risks."; docs page version v0.32.0 | the SHA256 advice the v0.9.0 page gave became the default at v0.11 and is selectable with `--prefix-caching-hash-algo`; the collision caveat is therefore historical, not a current obligation | mined | 2026-10-25 | 90d | corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md |
```

## 3. Per-row change note (staged cell → emitted cell)

Cell-level diff was computed mechanically against the seven staged lines, comparing cell by cell on the
contract columns; nothing below is omitted and no other cell changed.

- **S330** — `opened` `2026-10-23` → `2026-10-25` (this round's access date, as the task fixes).
  `recheck` command form → token `90d` (see Finding F1). `source`, `kind` `docs`, `tier` `A`, `scope`,
  `anchor`, `teaches` carried verbatim; `status` `mined`; `used-by` `corpus/knowledge/kv-cache-reclamation-models.md` (unchanged from staged).
- **S333** — `opened` → `2026-10-25`; `recheck` → `90d`. Everything else verbatim, including the
  commit-pinned `source docs/...radix_eviction_policy.mdx @ 77091cea…` provenance inside `anchor`.
- **S334** — `opened` → `2026-10-25`; `recheck` → `90d`. Everything else verbatim (anchor keeps
  `session_radix_cache.mdx @ d34f7b23…` (2026-09-22)).
- **S335** — `opened` → `2026-10-25`; `recheck` → `90d`. Everything else verbatim; `kind` stays `paper`,
  `tier` `A`; scope keeps the historical / revision-free-by-arXiv-id limit.
- **S346** — `opened` → `2026-10-25`; `recheck` → `90d`; `used-by`
  `corpus/knowledge/kv-cache-reclamation-models.md, corpus/knowledge/cross-literate-endpoint-venues.md`
  → `corpus/knowledge/kv-cache-reclamation-models.md`. Diff reason in Finding F2. Title, percent-encoded
  URL, `community`/`B`, scope, anchor and teaches carried verbatim.
- **S347** — `opened` → `2026-10-25`; `recheck` → `90d`. Everything else verbatim; `used-by`
  already `corpus/knowledge/prefix-cache-reuse-models.md`.
- **S363** — three edits beyond the date/recheck:
  1. `scope`: "…changed after **the page the lane already holds**" → "…changed after **v0.9.0**"
     (removes lane-relative/campaign prose; the referent is exactly the v0.9.0 page, which is S347 in
     this same batch, and the staged `teaches` already states "the SHA256 advice the v0.9.0 page gave
     became the default at v0.11").
  2. `anchor`: the fullwidth semicolon `；` between the quote and `docs page version v0.32.0` normalized
     to ASCII `;` (Finding F3). Quote bytes untouched.
  3. `opened` → `2026-10-25`; `recheck` → `90d`. `used-by` already
     `corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md`.

## 4. Gates exercised (all read-only)

| Gate | Command / method | Result |
|---|---|---|
| Contract cell count, no stray pipe | imported the lane's own parser (`tools/sources-append-only.py`, `split_cells`) and applied it to each of the 7 rows | each row → **11 cells**, matching `CONTRACT_COLUMNS`; **0** cells contain `\|` |
| Naive-split robustness | `awk -F'\|'` on the emitted block vs the sibling raw draft `out/ExecValidate/rows.raw.md` | raw staged draft line 1 → **14** fields (escaped `\|` in `recheck`); emitted block → 13 fields (11 cells + 2 outer pipes) |
| id collision with lane registry | `grep -o '^\| S[0-9]\+' corpus/SOURCES.md \| tail`; `grep -c` for each of the 7 ids | lane registry ends at **S329**; all 7 target ids **absent** from the lane file (free) |
| id absence at base (C2 precondition) | `git show 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea:corpus/SOURCES.md \| grep -c '^| S330\|…'` | **0**; base registry tail is `S327 S328 S329` |
| target knowledge files absent at base | `git show <base>:corpus/knowledge/<f>` ×3 | **absent** for all three (kv-cache, prefix-cache, prefix-cache amendment) |
| target knowledge files present in lane now | `[ -f corpus/knowledge/<f> ]` ×3 | **missing** — not yet written by the entry seats (Finding F4) |
| `recheck` vocabulary in this lane | `grep '^| S[0-9]' corpus/SOURCES.md \| awk -F'\|' '{print $11}' \| sort \| uniq -c` | 171 `on-release`, 18 `90d`, 6 `every round`, 6 `180d`, 2 `365d`; **0** rows carry an embedded command |
| used-by mapping truth (staged) | `grep -o 'S3[0-9][0-9]'` on the three staged knowledge files | kv file → `S330 S333 S334 S335 S346`; prefix file → `S347`; prefix amendment → `S363` — exactly the task's mapping |
| insertion point | `grep -n '^| S329\|^## Paths' corpus/SOURCES.md` | `S329` at line 215, `## Paths` at 217 → append after 215 |
| whole-file dry run | copied the lane `corpus/SOURCES.md` into the seat dir, inserted the 7 rows after the `| S329 |` line, and ran the lane parser's `parse_registry` on the merged text (read-only w.r.t. the lane) | parses clean: header is exactly the contract's 11 columns, **210** rows (203 existing + 7), ids in order `… S328 S329 S330 S333 S334 S335 S346 S347 S363`, no duplicate id, no malformed row, no row-like line outside the registry; `S330.recheck == '90d'`, `S346.used-by == 'corpus/knowledge/kv-cache-reclamation-models.md'` |

No `pacman`, no installs, no tool upgrades were needed or run. No mutating `git`/`jj` command was run.

## 5. Surfaces touched / untouched

Written (3 files, all mine):
- `.ufo/waves/round-37/w1/out/ScribeAppend.md` (this report — the only permitted report path).
- `.ufo/waves/round-37/w1/out/L1Kama37.MagneticAphid/registry-rows.md` (seat scratch draft, 7 rows).
- `.ufo/waves/round-37/w1/out/L1Kama37.MagneticAphid/SOURCES.dryrun.md` (seat-local copy of the lane
  registry with the 7 rows inserted — evidence for the whole-file dry-run gate; **not** a lane file and
  not to be copied over `corpus/SOURCES.md`).

Not touched: `corpus/SOURCES.md`, any `corpus/knowledge/*`, `corpus/lessons/*` (incl. round-36 files),
`MISSION.md`, `SCORECARD.md`, `LOG.md`, `considerthese/`, the staged package, any sibling lane, the fleet
repo, lane jj state and the lane Git index.

Pre-existing working-copy state observed, not created by me: `corpus/SOURCES.md` is modified vs HEAD
`873c5d77` by exactly 2 added rows (S328, S329, `git diff --stat` → `2 ++`), and
`corpus/knowledge/sglang-native-route-deprecation.md` is untracked. My block appends after those S329
bytes; it assumes that in-flight addition lands first.

## 6. Findings

- **F1 — staged `recheck` cells cannot be carried verbatim.** Every staged `recheck` is
  ``90d — re-run `curl … \| grep -c '…'` (expect ≥1) (ran 2026-10-23)``. Two independent reasons to
  reduce it to the token `90d`: (a) the task requires no `|` in any cell and the probe contains an
  escaped `\|` in all seven rows; (b) this lane's `recheck` column is a closed token vocabulary
  (203/203 rows; measured above). The probes are preserved verbatim here so the round lesson can hold
  them, and they are still executable as written:
  - S330 `curl -fsSL 'https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/' | grep -c 'unified scheduler'` (expect ≥1)
  - S333 `curl -fsSL 'https://docs.sglang.io/docs/advanced_features/radix_eviction_policy' | grep -c 'lowest score is evicted first'` (expect ≥1)
  - S334 `curl -fsSL 'https://docs.sglang.io/docs/advanced_features/session_radix_cache' | grep -c 'soft protection, not memory pins'` (expect ≥1)
  - S335 `curl -fsSL 'https://arxiv.org/abs/2312.07104' | grep -c '2312.07104'` (expect ≥1)
  - S346 `curl -fsSL 'https://raw.githubusercontent.com/AaronYang238/llm/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md' | grep -c 'RadixCache'` (expect ≥1)
  - S347 `curl -fsSL 'https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html' | grep -c 'hash-based approach'` (expect ≥1)
  - S363 `curl -fsSL 'https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/' | grep -c 'sha256'` (expect ≥1)
  Each staged probe carries `(ran 2026-10-23)`; none was re-run by this seat, so the emitted rows rest on
  the wave's fetch seats' re-opens, not on my execution.
- **F2 — S346's staged `used-by` names a file this lane does not have.** The staged `cross-literate-endpoint-venues.md`
  does cite S346 (3 occurrences, incl. a front-matter `source: S346` line), but that path does not exist in
  `kama-shokunin/corpus/knowledge/` (verified) and is a staged candidate, not an admitted entry. Keeping it
  would fabricate a lane-local citation. The emitted `used-by` is the one real citing file. If
  `cross-literate-endpoint-venues.md` is ever admitted here, S346's `used-by` gains it (mutable cell).
- **F3 — S363's staged `anchor` contained a fullwidth `；`.** Normalized to ASCII `;` so the anchor reads as
  one delimiter-separated list like every other row; quoted bytes unchanged.
- **F4 — ordering dependency.** The three `used-by` targets do not exist in the lane yet
  (`corpus/knowledge/kv-cache-reclamation-models.md`, `…/prefix-cache-reuse-models.md`,
  `…/prefix-cache-reuse-models-amendment-2026-10-23.md`). Rows and entries must land in the same commit
  (or entries first); otherwise the registry carries dangling `used-by` references, and the frozen C2
  predicate's "every one of those files exists in `corpus/knowledge/`" clause fails regardless of this block.
  All three are absent at base `6a4afdfe`, which is what C2's base-absence clause needs.
- **F5 — tier/kind carried as staged, not re-judged.** `paper`/`A` for S335 and `community`/`B` for S346 are
  the package's calls; `paper` is used by other lanes but appears **0** times in this lane's registry so far,
  so a reviewer scanning for a new `kind` value will see one. `kind` is outside the mutable set, so this must
  be settled before append, not after.

## 7. Out of scope / not done

- No lane corpus edit, no lesson text, no coverage/statement counters, no `tools/round37-*.py` run — the
  frozen predicates are the canonical judge's to execute at the tip.
- No re-fetch of any URL by this seat: the wave's fetch seats produced
  `out/FetchS333/`, `out/FetchS334/`, `out/FetchS335/`, `out/FetchS346/`, `out/FetchS363/`,
  `out/FamousTarsier/prefix_caching_v0.9.0.html`, `out/StripedMink/v1_guide.html`,
  `out/L1Kama37.AssistantToucan/S330.html`. I read their existence only; I did not re-derive any quote
  from those bytes, and no cell here claims a byte re-derivation.
- Judgement of the three staged knowledge entries themselves, and of any other staged entry, belongs to the
  planner/reviewers, not this seat.
