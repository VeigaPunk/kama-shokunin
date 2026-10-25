# ScoutGate — staged-id bookkeeping for the C2 admissions (kama r37 w1)

Scope: read-only. Nothing in the lane, the fleet repo, the campaign package or the jj/Git state
was written, staged, committed, moved or deleted. No package tool was run. No installs and no
`pacman` transaction. Scratch (validator mirrors) lives only under
`.ufo/waves/round-37/w1/out/ScoutGate/`.

## Provenance

| item | value |
|---|---|
| lane registry read | `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`, sha256 `1e44b4f314f2eb7f671feb537d03030af145713d484cbd326017fcbb5a83e8fe`, 462 lines |
| staged file read | `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md`, sha256 `3ad0df68504e1f49a0ab23e68b2034a9d6258345468fa03013737ced7ce234ff`, 148 lines, mtime 2026-10-24 23:33:20 -0300 |
| lane jj working copy `@` | `7e4b6071c359cd036ef4b16d38ea75b9364ea36e` |
| jj `@-` = Git HEAD | `873c5d7774b97e7c633052456f13595a2ea5775f` (2026-10-24T22:58:24-03:00, "mut4: corrupt cited blob hash in R35-WORDS row (sandbox only)") |
| frozen base | `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea` (object type `commit`, reachable read-only) |
| register read | `/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md`, 83621 bytes, mtime 2026-10-24 08:37:00 -0300 |
| recipe source | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/prompts/kama-round-37.md` §6 campaign addendum, "Quarantine — payload-absent rows" block (lines ~452-462) |

## 1. The seven staged rows, verbatim

All seven sit in the staged file's `## Registry` table (lines 7, 10, 11, 12, 23, 24, 40). Each is
one physical line carrying **11 logical cells** and **exactly one literal `\|`** (inside the
`recheck` cell) — see §4 for what that costs.

```
| S330 | vLLM V1 Guide — https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/ | docs | A | vLLM V1 scheduling and batching model as the project documents it; not a runtime observation | §Scheduler — "V1's unified scheduler treats both prompt and output tokens the same way"; §Chunked Prefill — "Chunked prefill is enabled by default whenever possible"; docs page version v0.19.1 | one token budget spans prompt and output tokens; chunked prefill is on by default; FCFS or priority scheduling via `--scheduling-policy` | mined | 2026-10-23 | 90d — re-run `curl -fsSL 'https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/' \| grep -c 'unified scheduler'` (expect ≥1) (ran 2026-10-23) | corpus/knowledge/kv-cache-reclamation-models.md |
```

```
| S333 | SGLang Radix Eviction Policy — https://docs.sglang.io/docs/advanced_features/radix_eviction_policy | docs | A | the SGLang KV-cache reclamation rule; engine-internal, carries no endpoint semantics | §Eviction candidates — "The policy scores each candidate and the lowest score is evicted first."; source docs/docs/advanced_features/radix_eviction_policy.mdx @ sgl-project/sglang 77091cea68d0701d6cc71edfb45f2815c4f8d791 (2026-09-29) | only evictable leaves are candidates (unlocked and not shadowed by a child still holding KV); the lowest score goes first; a policy scores but cannot pin KV | mined | 2026-10-23 | 90d — re-run `curl -fsSL 'https://docs.sglang.io/docs/advanced_features/radix_eviction_policy' \| grep -c 'lowest score is evicted first'` (expect ≥1) (ran 2026-10-23) | corpus/knowledge/kv-cache-reclamation-models.md |
```

```
| S334 | SGLang Session-Aware Radix Cache — https://docs.sglang.io/docs/advanced_features/session_radix_cache | docs | A | SGLang session-reference semantics; a session is not a KV pin | §Session references — "Session references are soft protection, not memory pins."; source docs/docs/advanced_features/session_radix_cache.mdx @ sgl-project/sglang d34f7b2326a10cb5f3ba8ec95efb31c761237750 (2026-09-22) | referenced KV can still be evicted; the `session_id` labels cache references only and does not append or reconstruct conversation context | mined | 2026-10-23 | 90d — re-run `curl -fsSL 'https://docs.sglang.io/docs/advanced_features/session_radix_cache' \| grep -c 'soft protection, not memory pins'` (expect ≥1) (ran 2026-10-23) | corpus/knowledge/kv-cache-reclamation-models.md |
```

```
| S335 | SGLang: Efficient Execution of Structured Language Model Programs — https://arxiv.org/abs/2312.07104 | paper | A | the primary statement of RadixAttention's evictability rule; historical, revision-free by arXiv id | §RadixAttention — "A node is evictable if its reference counter is zero."; arXiv:2312.07104 (abs page) and arXiv:2312.07104v1 (HTML full text) | nodes used by the running batch are protected by a per-node reference counter; LRU eviction recursively removes leaf nodes; cache-aware scheduling sorts the queue by matched prefix length | mined | 2026-10-23 | 90d — re-run `curl -fsSL 'https://arxiv.org/abs/2312.07104' \| grep -c '2312.07104'` (expect ≥1) (ran 2026-10-23) | corpus/knowledge/kv-cache-reclamation-models.md |
```

```
| S346 | llm 教程 第 6 章 推理引擎 — https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md | community | B | Chinese reverse-engineering write-up of vLLM and SGLang internals; reproducible file-level detail the upstream docs do not present as a source map, but not authoritative for engine behaviour | §6.4 RadixAttention — "`mem_cache/radix_cache.py` `RadixCache` 基数树 prefix cache" and "`managers/schedule_policy.py` `SchedulePolicy` LPM 等调度策略" | a Chinese-language source map contrasting vLLM's flat hash-chain prefix cache with SGLang's radix tree, naming the concrete source files that implement each | mined | 2026-10-23 | 90d — re-run `curl -fsSL 'https://raw.githubusercontent.com/AaronYang238/llm/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md' \| grep -c 'RadixCache'` (expect ≥1) (ran 2026-10-23) | corpus/knowledge/kv-cache-reclamation-models.md, corpus/knowledge/cross-literate-endpoint-venues.md |
```

```
| S347 | vLLM Automatic Prefix Caching (design) — https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html | docs | A | vLLM's own prefix-cache design at v0.9.0: how a kv-cache block is keyed and which blocks are reusable; the design page, not an observed runtime | §Automatic Prefix Caching → "Hashing" — "vLLM chooses a hash-based approach"; §Eviction (LRU); docs page version v0.9.0 | each kv-cache block is hashed by its own tokens plus the tokens of the prefix before it, so reuse requires an exact prefix match; only full blocks are cached; the hash key is not collision-free and SHA256 is advised for multi-tenant use | mined | 2026-10-23 | 90d — re-run `curl -fsSL 'https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html' \| grep -c 'hash-based approach'` (expect ≥1) (ran 2026-10-23) | corpus/knowledge/prefix-cache-reuse-models.md |
```

```
| S363 | vLLM Automatic Prefix Caching (design), current documentation line — https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/ | docs | A | vLLM's prefix-cache design at the current documentation line, including the hashing default that changed after the page the lane already holds | §Automatic Prefix Caching → Note 2 — "As of v0.11, the default hashing algorithm is sha256, which addresses collision risks."；docs page version v0.32.0 | the SHA256 advice the v0.9.0 page gave became the default at v0.11 and is selectable with `--prefix-caching-hash-algo`; the collision caveat is therefore historical, not a current obligation | mined | 2026-10-23 | 90d — re-run `curl -fsSL 'https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/' \| grep -c 'sha256'` (expect ≥1) (ran 2026-10-23) | corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md |
```

Cell-level digest (observed):

| id | kind | tier | status | opened | used-by (as staged) |
|---|---|---|---|---|---|
| S330 | docs | A | mined | 2026-10-23 | `corpus/knowledge/kv-cache-reclamation-models.md` |
| S333 | docs | A | mined | 2026-10-23 | `corpus/knowledge/kv-cache-reclamation-models.md` |
| S334 | docs | A | mined | 2026-10-23 | `corpus/knowledge/kv-cache-reclamation-models.md` |
| S335 | paper | A | mined | 2026-10-23 | `corpus/knowledge/kv-cache-reclamation-models.md` |
| S346 | community | B | mined | 2026-10-23 | `corpus/knowledge/kv-cache-reclamation-models.md, corpus/knowledge/cross-literate-endpoint-venues.md` |
| S347 | docs | A | mined | 2026-10-23 | `corpus/knowledge/prefix-cache-reuse-models.md` |
| S363 | docs | A | mined | 2026-10-23 | `corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md` |

These seven are the **complete** set of staged rows naming any of the three frozen-C2 knowledge
files (grep of the staged file for the three filenames returns exactly these seven line numbers,
7/10/11/12/23/24/40). Each id occurs exactly once as a first cell in the staged file.

Staged knowledge files also exist at
`/home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus/knowledge/` for all three C2 names, plus
`cross-literate-endpoint-venues.md`; the three C2 files carry `source:` lines for exactly these
ids: `kv-cache-reclamation-models.md` → S330, S333, S334, S335, S346; `prefix-cache-reuse-models.md`
→ S347; `prefix-cache-reuse-models-amendment-2026-10-23.md` → S363.

## 2. Id-collision re-derivation

Command (verbatim from the round prompt, run on both files):

```bash
cd /home/vgpnk/Projects/shokunin/kama-shokunin
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md | sort > /tmp/a.ids
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' /home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md | sort > /tmp/b.ids
comm -12 /tmp/a.ids /tmp/b.ids
```

Observed output: **empty** (`comm` exited 0, zero lines both with and without stripping the
`| ` prefix). Zero collisions.

Supporting counts (observed):

| quantity | lane `corpus/SOURCES.md` | staged `SOURCES.append.md` |
|---|---|---|
| first-cell id rows | 203 | 142 |
| unique ids | 203 | 142 |
| min / max | S001 / **S329** | **S330** / S471 |
| contiguous | no — 126 unused ids in 1..329 | yes — every id 330..471 present exactly once |

- The lane's id space is **full up to S329**; S330 is the first free id, and every staged id is
  strictly above the lane maximum. That is why the collision set is empty, not a coincidence of
  formatting.
- At the frozen base `6a4afdfe…`, `git show <base>:corpus/SOURCES.md` has max first-cell id
  **S329** and contains **none** of S330/S333/S334/S335/S346/S347/S363; `git ls-tree <base>
  corpus/knowledge/` contains none of the three C2 filenames. Absence-at-base holds for the ids
  and for the files.
- URL-level check (E04 is URL+scope, so ids alone are not sufficient): each of the seven staged
  source URLs has **0** occurrences in the lane registry —
  `docs.vllm.ai/en/v0.19.1/usage/v1_guide/`,
  `docs.sglang.io/docs/advanced_features/radix_eviction_policy`,
  `docs.sglang.io/docs/advanced_features/session_radix_cache`,
  `arxiv.org/abs/2312.07104`,
  the pinned `AaronYang238/llm` chapter path,
  `docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html`,
  `docs.vllm.ai/en/v0.32.0/design/prefix_caching/`.

Caveat, stated so it is not mistaken for a passed check: "zero id collisions" says nothing about
the *schema* fitness of the append block. §4 shows the block fails the census gate as staged.

## 3. Kama quarantine slice

Recipe run verbatim (§6 addendum; note the shell variables in the prompt are not needed to read
the result, and the prompt's `$A` write target was pointed at this seat's scratch instead of
`assimilation/` because this seat may not write there):

```bash
R=/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md
awk -F'|' -v l='kama' '$2 ~ ("`" l "`") && $3 ~ /round[0-9]+/ && $4 ~ /S[0-9]+/ \
  {print $4, $5}' "$R"
```

Observed output, 7 lines (all carry an S-id, so the prompt's "every line must carry an S-id"
invariant holds; the summary row `| \`kama\` | 7 |` at register line 245 matches the derivation
even though the prompt warns the summary is stale in general):

```
 S200   `payload-absent` 
 S202   `payload-absent` 
 S206   `payload-absent` 
 S210   `payload-absent` 
 S211   `payload-absent` 
 S224   `payload-absent` 
 S230   `payload-absent` 
```

Every kama row's id: **S200, S202, S206, S210, S211, S224, S230** (register data-row lines 92–98).

Register rows in full (line, round, id, source, quote):

| reg line | round | id | cited source | quote cell |
|---|---|---|---|---|
| 92 | round1 | S200 | `https://arxiv.org/abs/2312.07104` | `DOI not in Semantic Scholar` |
| 93 | round1 | S202 | `https://docs.docker.com/reference/compose-file/services/` | `service_healthy : Specifies that a dependency is expected to be 'healthy' (as indicated by healthcheck) before starting ` |
| 94 | round1 | S206 | `https://www.alibabacloud.com/help/zh/pai/deploy-an-llm/` | ``对于vLLM/SGLang，可通过模型列表接口`<EAS_ENDPOINT>/v1/models`获取。`` |
| 95 | round1 | S210 | `https://unsloth.ai/docs/jp/ji-chu/inference-and-deployment/sglang-guide` | `Page Not Found` |
| 96 | round1 | S211 | `https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md` | `still-live` |
| 97 | round3 | S224 | `https://docs.vllm.ai/en/v0.17.0/api/vllm/entrypoints/serve/instrumentator/health/` | ``/health` calls engine `check_health()` and render-only servers always return 200` |
| 98 | round3 | S230 | `https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py` | `Endpoint '/get_model_info' is deprecated and will be removed in a future version. Please use '/model_info' instead.` |

Register is a snapshot, not a live view — cross-check against the lane registry today:

| id | present in lane `corpus/SOURCES.md`? | note |
|---|---|---|
| S200 | no | open quarantine row |
| S202 | no | open quarantine row |
| S206 | **yes** (mined, same PAI URL, used-by `corpus/knowledge/serving-alias-contract.md`) | already hand-checked and adopted in round 34; re-adoption is not applicable |
| S210 | no | open quarantine row |
| S211 | no | open quarantine row |
| S224 | no | open quarantine row |
| S230 | no | open quarantine row |

Prior-round verdicts already on disk (so this seat does not re-litigate them, only records them):
`corpus/lessons/round-34-verifier-spotcheck.md:65` lists `S200 S202 S210 S211 S224 S230` as
"still quarantined", and `corpus/lessons/round-35.md:38-44` records per-row outcomes — S200
unverifiable (class-label quote), S202/S210/S230 present-not-appended, S211 unreachable (the r35
spotcheck at `round-35-verifier-spotcheck.md:95` disagrees with the stated 429 reason but agrees
on not-appended), S224 quote-not-located. **Open quarantine set = 6 rows**; S206 is closed.

Anything quarantined stays unappendable until hand-checked in a round that fetches the cited
source; the six open rows are not part of the C2 admission set and their ids (S200–S230) do not
collide with the staged 330+ block.

## 4. Schema consequence for the append block (observed, not inferred)

The round prompt's warning that staged rows are campaign-schema and fail their own census gate is
true of these seven rows in a specific, measurable way, and I proved it rather than assuming it.
Validator: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` (E01 = `NF!=13`,
E09 = recheck ∉ {ISO date, `NNd`, symbolic cadence}, E11 = used-by path missing on disk; symbolic
cadence = `^[A-Za-z][A-Za-z0-9 _-]*$`).

Mirrors (path-faithful: every real lane path symlinked, `corpus/SOURCES.md` copied and the seven
rows inserted at lane line 216, i.e. directly after the `S329` row, inside `## Registry`):
`.../out/ScoutGate/validate-{a,b,c,d}/`, run as
`sources-census.sh validate --today 2026-10-25 --file <mirror>/corpus/SOURCES.md`.

| variant | shape of the 7 rows | non-W04 findings | exit |
|---|---|---|---|
| baseline | lane file as-is, no append | none (`file ok`) | 0 |
| A | **verbatim** staged rows | `E01 S330/S333/S334/S335/S346/S347/S363 fields=12` + 8 junk `E11` | 1 |
| B | `recheck` → `90d`, `used-by` trimmed to the admitted entry | none (`file ok`) | 0 |
| C | `recheck` → `90d`, `used-by` left verbatim | `E11 S346 missing used-by corpus/knowledge/cross-literate-endpoint-venues.md` | 1 |
| D | pipe-free prose recheck (`90d — re-run … (ran 2026-10-23)`), used-by trimmed | `E09 S330/S333/S334/S335/S346/S347/S363` | 1 |

Consequences, each observed in a run above:

1. **A byte-exact append fails E01 on all seven rows.** Each row has 11 logical cells plus one
   literal `\|` in `recheck`, so gawk `-F'|'` sees 14 fields and the validator reports
   `fields=12` (its `NF-2`). The escaped pipe must be rewritten out of the anchor/recheck text
   (e.g. keep the recheck command but drop the pipe, or move the pipe-bearing command into the
   lesson Gate block and leave a valid cadence in the cell).
2. **The prose recheck fails E09 even once the pipe is gone** (variant D). `90d — re-run …`
   is not ISO, not `NNd`, not symbolic; the cell must be reduced to `90d` and the prose
   (re-verify command, expect-count, Gate pointer) recorded in the round lesson's Gate block.
3. **S346's second `used-by` entry dangles.** `corpus/knowledge/cross-literate-endpoint-venues.md`
   exists only in the staged package and is **not** one of the three frozen-C2 files, so it will
   not exist in the lane at the tip; variant C shows the exact E11 it raises. `used-by` must list
   exactly the admitted entries citing the row — for this round that is
   `corpus/knowledge/kv-cache-reclamation-models.md` alone, with
   `cross-literate-endpoint-venues.md` added in the round that admits it.
4. With 1–3 applied the mirrored append validates clean (variant B: exit 0, 93 W04 warnings, byte
   for byte the same W04 set as the untouched lane file), which is the "exit 0 before the first
   registry append" gate the prompt requires. The seven rows produce **no** E03 (duplicate id) and
   **no** E04 (duplicate URL+scope) once appended — consistent with §2.
5. The three C2 knowledge files must exist in `corpus/knowledge/` for E11 to clear on the trimmed
   `used-by` paths; all three are currently **absent** from the lane (checked by direct `-e`
   probe), so the admission and the registry append have to land together.

Scratch artifacts kept for re-derivation: `rows-verbatim.txt`, `rows-normalized.txt`,
`validate-{a,b,c,d}/corpus/SOURCES.md`, `validate-{a,b,c,d}/out.txt` under
`.ufo/waves/round-37/w1/out/ScoutGate/`.

## 5. Uncertainties / remaining unknowns

- **`recheck` normalization targets.** §4 fixes the *shape* (`90d`), not the wording of the prose
  that has to survive in the Gate block. Which exact sentence belongs in `corpus/lessons/round-37.md`
  is the scribe's call; my runs only prove the current cell cannot stay.
- **`used-by` for the amendment file.** S363's staged `used-by` names only
  `prefix-cache-reuse-models-amendment-2026-10-23.md`; if the main entry
  (`prefix-cache-reuse-models.md`) also cites S363 after adjudication, the cell needs both. That
  decision is not mine and is not settled by the staged bytes.
- **Register freshness beyond kama.** The kama slice is internally consistent (7 data rows = the
  `| kama | 7 |` summary), but the register header's global totals (194 rows / 324 quotes) and the
  mtime (2026-10-24 08:37) predate round 36; I did not re-derive non-kama lanes and did not treat
  the header as authoritative for anything.
- **E01/E09/E11 severity.** The observed exit codes come from a mirror whose only difference from
  the lane is the appended block; the round-end gate runs
  `sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`, which I did not run
  (it wants an unmodified lane and is the main agent's/executor's check, not this seat's).
