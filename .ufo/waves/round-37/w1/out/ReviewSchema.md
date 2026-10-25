# ReviewSchema — fleet-schema conformance of the normalized append rows

Seat: L1Kama37.MinimumPartridge · round 37 · wave 1 · reviewer
Contract: `/home/vgpnk/Projects/shokunin/CORPUS.md` §SOURCES.md (Contract v1, frozen), 11 columns / NF=13.
Tool of record: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate`.
Objects checked, in order of availability:
- staged rows: `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` (read-only package);
- **normalized rows ExecValidate actually built**: `.ufo/waves/round-37/w1/out/ExecValidate/corpus/SOURCES.md` (mirror came up mid-check; this report's verdict rests on it, the staged rows are kept as the red-before state).

Scratch (seat dir only): `rows7.txt`, `mirror-SOURCES.md`, `mirror-B-depiped.md`, `mirror-C-cadence.md`, `landcheck/`, `execvalidate-independent.out`.

## Verdict per checked row (ExecValidate mirror, the rows that would land)

| row | 11 cells | literal/escaped `|` | kind | tier | status | community≠A | anchor not bare homepage | used-by truthful |
|---|---|---|---|---|---|---|---|---|
| S330 | ✓ | ✓ none | docs ✓ | A ✓ | mined ✓ | n/a | ✓ §Scheduler/§Chunked Prefill + v0.19.1 | ✗ 2 of 3 false |
| S333 | ✓ | ✓ none | docs ✓ | A ✓ | mined ✓ | n/a | ✓ §Eviction candidates + commit 77091ce | ✗ 2 of 3 false |
| S334 | ✓ | ✓ none | docs ✓ | A ✓ | mined ✓ | n/a | ✓ §Session references + commit d34f7b2 | ✗ 2 of 3 false |
| S335 | ✓ | ✓ none | paper ✓ | A ✓ | mined ✓ | n/a | ✓ §RadixAttention + arXiv v1 | ✗ 2 of 3 false |
| S346 | ✓ | ✓ none | community ✓ | B ✓ | mined ✓ | ✓ (B) | ✓ §6.4 + commit-pinned URL | ✗ 2 false, 1 true citation dropped |
| S347 | ✓ | ✓ none | docs ✓ | A ✓ | mined ✓ | n/a | ✓ §Hashing/§Eviction + v0.9.0 | ✗ 2 of 3 false |
| S363 | ✓ | ✓ none | docs ✓ | A ✓ | mined ✓ | n/a | ✓ §Note 2 + v0.32.0 | ✗ 2 of 3 false |

Row placement and blast radius of the mirror: `.ufo/waves/round-37/w1/out/ExecValidate/corpus/SOURCES.md:216-222`, inside `## Registry` (next heading `## Paths` at :224, so the r36 E12 trap is avoided); `diff` against the lane tip is exactly 7 added lines and 0 removed; `census --file` reports `rows 210` (203 + 7).
Fleet tool on the mirror, from the mirror root: **0 E01, 0 E12, 0 E05/E06/E07/E08/E09/E10 for the seven ids**; the only codes naming them are 21 E11 lines, all caused by the mirror root having no `corpus/knowledge/` tree (see F4).

---

## Findings

### F1 — HIGH (staged rows only): escaped pipe in the `recheck` cell makes every row a 12-field row (E01)

All seven staged rows carry a backslash-escaped pipe inside the `recheck` cell, which the fleet parser splits on. Offending cell, all seven rows, `recheck`:

```
S330 recheck: 90d — re-run `curl -fsSL 'https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/' \| grep -c 'unified scheduler'` (expect ≥1) (ran 2026-10-23)
S333 recheck: 90d — re-run `curl -fsSL 'https://docs.sglang.io/docs/advanced_features/radix_eviction_policy' \| grep -c 'lowest score is evicted first'` (expect ≥1) (ran 2026-10-23)
S334 recheck: 90d — re-run `curl -fsSL 'https://docs.sglang.io/docs/advanced_features/session_radix_cache' \| grep -c 'soft protection, not memory pins'` (expect ≥1) (ran 2026-10-23)
S335 recheck: 90d — re-run `curl -fsSL 'https://arxiv.org/abs/2312.07104' \| grep -c '2312.07104'` (expect ≥1) (ran 2026-10-23)
S346 recheck: 90d — re-run `curl -fsSL 'https://raw.githubusercontent.com/AaronYang238/llm/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md' \| grep -c 'RadixCache'` (expect ≥1) (ran 2026-10-23)
S347 recheck: 90d — re-run `curl -fsSL 'https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html' \| grep -c 'hash-based approach'` (expect ≥1) (ran 2026-10-23)
S363 recheck: 90d — re-run `curl -fsSL 'https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/' \| grep -c 'sha256'` (expect ≥1) (ran 2026-10-23)
```

Evidence:
- `awk -F'|' '{print $2, NF}'` on the seven staged rows → 14 for all seven (contract: NF=13).
- Contract's own frozen counter on a scratch mirror built from the lane tip + these seven rows, inserted inside `## Registry` (`mirror-SOURCES.md`):
  `awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF!=13 {n++} END{print n+0}'` → **7** (lane tip: **0**).
- `sources-census.sh validate` on that mirror, cwd = lane root:
  `file E01 S330 fields=12` … `file E01 S363 fields=12` (7 lines, exit 1).

Why it matters beyond the field count: the malformed row also shifts `used-by` into the 12th cell for the separate used-by pass, which re-splits on `,`. Observed consequences on the same mirror:

```
file	E11	S330 missing used-by grep -c 'unified scheduler'` (expect ≥1) (ran 2026-10-23)
file	E11	S334 missing used-by grep -c 'soft protection
file	E11	S334 missing used-by not memory pins'` (expect ≥1) (ran 2026-10-23)
file	E11	S363 missing used-by grep -c 'sha256'` (expect ≥1) (ran 2026-10-23)
```

S334 splits into two phantom paths because its grep pattern contains a comma.

Scope: the defect is systemic in the staged block, not just the seven admits — of 142 row-shaped lines in `SOURCES.append.md`, **90** carry a `\|`, and the lane's committed registry has **0** escaped pipes across 203 rows (all NF=13). The rule violated is literal: "No `|` inside any cell."

Status: **cured in ExecValidate's normalized rows** (0 escaped pipes, NF=13 on all seven). The staged file must therefore never be appended verbatim.

### F2 — MEDIUM (staged rows only): `recheck` is not a cadence, so the same cell also fails E09

Contract field definition: "`recheck` — ISO date or cadence (`90d`, `180d`, `on-release`)". The staged cell is a cadence followed by a whole shell command and a run date. Proof isolating this defect from F1 (variant `mirror-B-depiped.md`: same rows, `\|` replaced by process substitution `grep -c 'pat' <(curl -fsSL 'url')`, nothing else changed):

```
file	E09	S330 recheck=90d — re-run `grep -c 'unified scheduler' <(curl -fsSL 'https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/')` (expect ≥1) (ran 2026-10-23)
… same shape for S333, S334, S335, S346, S347, S363 (7 lines, exit 1)
```

`symbolic()` in the validator is `/^[A-Za-z][A-Za-z0-9 _-]*$/` and `90d` alone matches `^[0-9]+d$`; the trailing prose matches neither. Lane precedent agrees: of 203 committed rows, every `recheck` cell is a bare cadence (`on-release` 171, `90d` 18, `every round` 6, `180d` 6, `365d` 2) — none carries a command. Staged block: 140 of 142 non-bare.

Status: **cured in the mirror** (bare `90d` in all seven). Variant `mirror-C-cadence.md` (de-piped + bare `90d`) produces **no E01 and no E09** for the seven.

### F3 — HIGH (ExecValidate's normalized rows, would land as false cells): blanket `used-by` — 14 of 21 claims name a file that does not cite the row

Every one of the seven mirror rows carries the same three-path cell, independent of which knowledge entry actually cites the id. Offending cell, all seven rows, `used-by`:

```
corpus/knowledge/kv-cache-reclamation-models.md, corpus/knowledge/prefix-cache-reuse-models.md, corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md
```

Contract field definition: "`used-by` — repo-relative paths of the knowledge entries or lessons citing the row". Cross-check of each claim against the staged knowledge files' `source:` lines (`/home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus/knowledge/`):

| row | true citing files | false claims in the cell |
|---|---|---|
| S330 | kv-cache-reclamation-models.md | prefix-cache-reuse-models.md, …-amendment-2026-10-23.md |
| S333 | kv-cache-reclamation-models.md | same two |
| S334 | kv-cache-reclamation-models.md | same two |
| S335 | kv-cache-reclamation-models.md | same two |
| S346 | kv-cache-reclamation-models.md, cross-literate-endpoint-venues.md | same two — **and the true second citation is dropped** |
| S347 | prefix-cache-reuse-models.md | kv-cache-reclamation-models.md, …-amendment-2026-10-23.md |
| S363 | prefix-cache-reuse-models-amendment-2026-10-23.md | kv-cache-reclamation-models.md, prefix-cache-reuse-models.md |

14 false claims out of 21; one true citation missing (S346 → `corpus/knowledge/cross-literate-endpoint-venues.md`, which cites S346 three times). The blanket triple is also the only reason the cell would pass at land time: it names exactly the three files the round intends to create, and it silently drops the one true citation whose file is not among the round's three admits.

This is invisible to the fleet counter. Proof: `landcheck/` = ExecValidate's mirror + the four staged knowledge files at their lane paths; `sources-census.sh validate --file landcheck/corpus/SOURCES.md --today 2026-10-25` returns **no finding naming S330/S333/S334/S335/S346/S347/S363** (the run's 471 findings are other rows whose knowledge files I did not copy). A row set with 14 false `used-by` cells validates clean.

### F4 — LOW: `used-by` existence is a land-order precondition, not a row property

On the mirror as it stands (no `corpus/knowledge/` under the mirror root) the fleet tool emits 21 E11 lines, three per row, e.g. `file E11 S330 missing used-by corpus/knowledge/kv-cache-reclamation-models.md`. That is the mirror's missing tree, not a cell defect: the three files in the frozen C2 predicate do not yet exist in `corpus/knowledge/`, and `cross-literate-endpoint-venues.md` does not exist there either. ExecValidate's paste of E11 therefore proves the mirror root is sparse, not that the rows are wrong; conversely, when the files do land, E11 turning green proves nothing about F3.

### F5 — LOW: S346 `anchor` names a section but carries no revision in the cell

Offending cell (S346, `anchor`):

```
§6.4 RadixAttention — "`mem_cache/radix_cache.py` `RadixCache` 基数树 prefix cache" and "`managers/schedule_policy.py` `SchedulePolicy` LPM 等调度策略"
```

Contract: "`anchor` — exact section / heading / page / line plus revision (version, commit, or publication date)". The revision exists in the row — the `source` URL is commit-pinned (`…/blob/35b83cee12ae26f10b58d4163298352384503907/…`) — but not in the anchor cell. Not a "bare homepage" violation (the anchor is a numbered section of a commit-pinned file). Lane precedent: 34 of 203 committed anchors likewise omit an in-cell revision token. Recommend adding `@ commit 35b83ce` to the cell for the freshness sweep's sake; not a blocker under current practice.

### Passes (checked, no violation)

- 11 cells on all seven mirror rows; `awk -F'|'` NF=13 on all seven; zero empty cells.
- No literal pipe, no escaped pipe, and no look-alike vertical (`U+FF5C`, `U+2502`, `U+2223` all absent) in any cell of the seven mirror rows.
- `kind` ∈ {docs, paper, community}, `tier` ∈ {A, B}, `status` = mined — validated by the fleet tool itself on the corrected mirror (no E05/E06/E07), not by eye.
- community never tier-A: S346 is `community` / `B`; no E10.
- `opened` = 2026-10-23 ≤ today → no E08. `source` cells carry `title — URL` on all seven.
- Ids collide with nothing: lane tip's highest id is S329; no E03, no E04.
- Append file's own header and separator are 11 columns (`| id | … | used-by |`, `|---|`×11).

## Residual risk

1. **The counter cannot see F3.** `used-by` truthfulness has no code: E11 only tests existence, and the `landcheck/` run proves a 14-false-cell row set exits green for those ids. Any round that treats a clean `validate` as proof that `used-by` is right will ship false provenance (the same class the corpus contract's rule 4 depends on: "expansion counts admitted knowledge entries whose `source:` cites a `mined` row" — a false `used-by` corrupts the mirror-image of that count).
2. **Malformed rows hide their own enum defects.** In `sources-census.sh` the E01 branch `next`s, and the frozen contract's enum one-liner is guarded by `NF==13`; on the as-staged mirror only **203 of 210** rows are enum-checked, i.e. exactly the seven broken rows are exempt. A green enum sweep over a block containing E01 rows is not evidence about those rows.
3. **Staged-to-mirror divergence is silent.** The staged block's `recheck` cell carried a re-runnable command; the mirror's carries bare `90d`. The recheck command is thereby lost from the registry — acceptable under the field definition, but the C2/spotcheck reproduction story must then live in the round lesson, not in SOURCES.md.
4. **Land order.** If rows land before the three knowledge files (or before `cross-literate-endpoint-venues.md` is decided), E11 fires on up to 21 cells; if `used-by` is corrected to the truthful sets first, E11 on S346's `cross-literate` path fires unless that file lands too.

## Verification gaps

- Not checked by me: whether the seven `teaches` cells are grounded in the fetched bodies (peers own the fetches; `w1/fetches/` exists for all seven). I checked cell shape only.
- Not checked: the other 135 staged rows beyond the two aggregate counts (90 escaped pipes, 140 non-bare recheck). I did not enumerate their individual violations.
- Not run: the validator against a mirror with the complete `corpus/knowledge/` tree, so the pre-existing E11 noise is present in `landcheck.out` (471 lines) and excluded from my per-row claims by filtering on the seven ids.
- No source URL was re-opened by me; no network call was made.
- The mirror was read while ExecValidate was still running; if it rewrites `corpus/SOURCES.md` after 04:58, F1–F5 must be re-derived against the new bytes.
