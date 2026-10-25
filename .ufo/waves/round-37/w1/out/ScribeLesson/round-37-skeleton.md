# kama round 37 lesson — SKELETON

> **DRAFT, NOT THE CORPUS FILE.** Written by seat `L1Kama37.WidespreadGoat` (scribe) into its
> seat directory. The L1 copies accepted sections into `corpus/lessons/round-37.md`; nothing in
> this file has landed. Placeholders are marked `<...>`; draft-only notes are under
> `## Draft notes — remove before landing`.

author: `<L1 name — fill on landing>`
date: 2026-10-25
base: 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea

## Claims (slot; L1-owned, copy verbatim from the preregistration)

> C1 calibration 7 → 7. Predicate: A frozen r36-spotcheck routed statement is corrected iff corpus/lessons/round-37.md contains a correction row naming its id, the counter re-derives the cited committed-byte fact, the row carries no wrong-id restatement that its own statement forbids, and the r36 lesson blob and the r36 fleet report blob are unchanged. Counting command: `python3 tools/round37-statement-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip <full-commit>`.

> C2 coverage 9 → 9. Predicate: The round-37 coverage block names each of knowledge/kv-cache-reclamation-models.md, knowledge/prefix-cache-reuse-models.md and knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md, every one of those files exists in corpus/knowledge/, and each cites an S-id present in corpus/SOURCES.md at the tip and absent at base 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea; none of those three holds at that base. Counting command: `python3 tools/round37-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip <full-commit>`.

The two predicate sentences above are frozen text (`.ufo/waves/round-37/preregistration.json`); the L1 owns the surrounding Claims prose and the control receipts.

## Corrections — round 37

These four rows correct the statements the round-36 closure routed in `corpus/lessons/round-36-verifier-spotcheck.md` §6. The round-36 lesson file and the round-36 fleet report are not rewritten; their blobs are pinned by the C1 counter at `6fb1ec151407b1207e8d540e83ba87d6a909d8ea` (lane `master:corpus/lessons/round-36.md`) and `8b7408e663c1b1ea95826d240f498637f1961604` (fleet `HEAD:.ufo/reports/round-36/kama.md`). Each row's facts below were re-derived from the cited bytes this round, not copied from the spot-check's prose.

R36-D1: The round-36 report cites `.ufo/waves/round-36/census-end.out` as committed round-end census evidence at report:147 and report:232, but that path is absent at base 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea and was untracked at the round-36 tip. It is committed at the round-37 counting tip: 12426 bytes on disk, and its final line is `kama` + TAB + `ok` + TAB + `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`. The round-36 fleet report is not rewritten. The counter re-derives the census blob at the tip and its absence at the base.

R36-D2A: The round-36 Gate's staged-id cross-reference for the published SGLang native route list is miswritten. The staged `SOURCES.append.md` row whose URL names `native_api.mdx` is S371 (https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx); the staged S366 row is the AWS SageMaker health-check page and is not that document. Every decision in the Gate stands; only the id evidence is wrong. corpus/lessons/round-36.md is not rewritten.

R36-D2B: The round-36 Gate's other staged-id references are corrected from the staged bytes. The four staged rows whose URL is `python/sglang/srt/entrypoints/http_server.py` are S364, S365, S377 and S396 (one URL, four anchors); and the staged `endpoint-health-probe-conventions.md` (package `merge/kama/amendments/corpus/knowledge/`) cites five ids — S332, S336, S337, S338 and S339 — not the four-id range the Gate recorded. Every decision stands; only the id evidence is wrong. corpus/lessons/round-36.md is not rewritten.

R36-D3: The round-36 report accounts for 30 of the 32 wave-3 seats and omits the two seats that exited rc=1: ScribeLog and RevQ206. Both seat logs carry the same last error text, `error: failed to run prompt: provider.rate_limit: 429 Rate limit reached for requests`; RevQ206's log also records an S206 page fetch at HTTP 200 before the error, and its report file exists. The round-37 fleet report names both seats with that last error text, as spot-check §6 item 3 routes. corpus/lessons/round-36.md is not rewritten.

## Gate

Opened 2026-10-25 by the L1 and re-opened by wave-1 seats. Theme: engine internals that shape what a served endpoint answers — KV-cache reclamation and prefix-cache reuse models in vLLM and SGLang. One theme, three candidate entries, seven candidate registry rows. The staged package under `/home/vgpnk/Projects/shokuknow` was read, never written. The base README holds no row on eviction, radix reclamation or prefix-reuse mechanism (ReviewFrontier: zero matches for `evict`, `radix`, `reclaim`, `reuse`, `batch`), so all seven rows are new ground rather than a restatement.

### Candidate entries

- `corpus/knowledge/kv-cache-reclamation-models.md` — cites S330, S333, S334, S335 and S346. Draft: `.ufo/waves/round-37/w1/out/<ScribeEntries seat>/` `<PLACEHOLDER: exact draft path from ScribeEntries.md>`.
- `corpus/knowledge/prefix-cache-reuse-models.md` — cites S347. Draft: `<PLACEHOLDER: exact draft path from ScribeEntries.md>`.
- `corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md` — cites S363. Draft: `<PLACEHOLDER: exact draft path from ScribeEntries.md>`.

### Candidate rows (promote to Admit only after the receipt is committed)

**Candidate S330.** URL `https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/`. Opened 2026-10-25, HTTP 200, 435441 bytes (`.ufo/waves/round-37/w1/out/FetchS330.md`). Anchor: §Chunked Prefill, the H3's only paragraph. Located quote (20 words): "Chunked prefill is enabled by default whenever possible, unlike in V0 where it was conditionally enabled based on model characteristics." Used by `corpus/knowledge/kv-cache-reclamation-models.md`. Recheck 90d.

**Candidate S333.** URL `https://docs.sglang.io/docs/advanced_features/radix_eviction_policy`. Opened 2026-10-25, HTTP 200, 296606 bytes (`.ufo/waves/round-37/w1/out/FetchS333.md`). Anchor: §How eviction picks a victim. Located quote (12 words): "The policy scores each candidate and the lowest score is evicted first." The page carries no version pin; the recheck must re-locate the sentence rather than trust a version. Used by `corpus/knowledge/kv-cache-reclamation-models.md`. Recheck 90d.

**Candidate S334.** URL `https://docs.sglang.io/docs/advanced_features/session_radix_cache`. Opened 2026-10-25, HTTP 200, 277182 bytes (`.ufo/waves/round-37/w1/out/FetchS334.md`). Anchor: lead paragraph under the page title, immediately before `#enable-the-cache` (the TOC has no entry for it). Located quote (20 words): "Session references are soft protection, not memory pins. Referenced KV can still be evicted when reclaiming unreferenced KV is insufficient." Used by `corpus/knowledge/kv-cache-reclamation-models.md`. Recheck 90d.

**Candidate S335.** URL `https://arxiv.org/abs/2312.07104`. Opened 2026-10-25, HTTP 200: abs page 43414 bytes and HTML full text (`https://arxiv.org/html/2312.07104v1`) 214951 bytes (`.ufo/waves/round-37/w1/out/FetchS335.md`). Anchor: §5.1 RadixAttention. Located quote (10 words): "A node is evictable if its reference counter is zero." Used by `corpus/knowledge/kv-cache-reclamation-models.md`. Recheck 90d.

**Candidate S346.** URL `https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md`; fetched through `raw.githubusercontent.com` at the same path+commit. Opened 2026-10-25, HTTP 200, 36737 bytes (`.ufo/waves/round-37/w1/out/FetchS346.md`). Anchor: §6.4 RadixAttention → source map table. Located quote (5 words): "`mem_cache/radix_cache.py` `RadixCache` 基数树 prefix cache". Community write-up: tier B at most, never A. Used by `corpus/knowledge/kv-cache-reclamation-models.md`. Recheck 90d.

**Candidate S347.** URL `https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html`. Opened 2026-10-25, HTTP 200, 59059 bytes (`.ufo/waves/round-37/w1/out/FetchS347.md`). Anchor: §Automatic Prefix Caching → Hashing. Located quote (17 words): "vLLM chooses a hash-based approach. Specifically, we hash each kv-cache block by the tokens in the block". Used by `corpus/knowledge/prefix-cache-reuse-models.md`. Recheck 90d.

**Candidate S363.** URL `https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/`. Opened 2026-10-25, HTTP 200, 215347 bytes (`.ufo/waves/round-37/w1/out/FetchS363.md`). Anchor: §Automatic Prefix Caching → Note 2. Located quote (13 words): "As of v0.11, the default hashing algorithm is `sha256`, which addresses collision risks." Used by `corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md`. Recheck 90d.

### Candidate rejects (judge on PROVINCE.md and QUALITY.md; at least one reject is required)

- `cross-literate-endpoint-venues.md` (staged) — `<REJECT OR ADOPT: reason from .ufo/waves/round-37/w1/out/CriticReject.md>`. Flip: `<FLIP: the observation that would reverse the verdict>`.
- `openai-compat-host-vendor-contracts.md` (staged) — `<REJECT OR ADOPT: reason from CriticReject.md>`. Flip: `<FLIP>`.
- `hosted-health-route-configuration-amendment-2026-10-23-r4.md` (staged) — `<REJECT OR ADOPT: reason from CriticReject.md>`. Flip: `<FLIP>`.

### Coverage map (C2's counted block lives in the README, not here)

Append to `corpus/README.md`, under the exact heading `## Coverage map — round 37 addition`, one row per entry:

| Entry | Covers | Round |
|---|---|---|
| `knowledge/kv-cache-reclamation-models.md` | `<one-line covers cell from ScribeEntries draft>` | 37 |
| `knowledge/prefix-cache-reuse-models.md` | `<one-line covers cell>` | 37 |
| `knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md` | `<one-line covers cell>` | 37 |

A name outside that heading does not count (C2 selftest `outside_met=0`).

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| id-drift | `corpus/lessons/round-36-verifier-spotcheck.md` §6 item 2 re-derives five staged-id citations in the round-36 Gate that resolve to different staged rows: the `native_api.mdx` row, the four `http_server.py` rows, and the `endpoint-health-probe-conventions.md` citation set. Every r36 decision stands; only the id evidence is wrong, and the correction is an appended row, never a rewrite. | QUALITY.md | KQ46 — a foreign or staged id range cited in a lesson is a claim: re-derive every id against the named artifact before citing it; a copied range that misnames ids is a correction target, never a citation. Final KQ46 text lands in `corpus/QUALITY.md` this round (draft: `.ufo/waves/round-37/w1/out/ScribeKQ46.md`). |

## Wave evidence

Predicates and controls (frozen before scoring):

- `.ufo/waves/round-37/preregistration.json` — `frozen_before_scoring: true`, `frozen_at: 2026-10-25`, `base: 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`.
- C1 counter `tools/round37-statement-audit.py`; C2 counter `tools/round37-coverage-audit.py`.
- `.ufo/waves/round-37/controls/c1-noop.out` — `uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False`, `noop_exit=1`; its selftest printed `good_met=True pass=1`.
- `.ufo/waves/round-37/controls/c2-base.out` — `named 0 files_exist 0 cited_new 0 met False`, `base_exit=1`; its selftest printed `pass=1`.
- Round-start census `.ufo/waves/round-37/census-start.out`: 94 lines, 93 `W04` duplicate-url warnings and one final `kama` + TAB + `ok` + TAB + path line; no E-class finding.

Wave 1 dispatch:

- Spec `.ufo/waves/round-37/w1/spec.json` (37 items: build, falsifiers, fetches, executives, scribes).
- Run manifest `.ufo/waves/round-37/w1/run.json` — `counts.spawn 37`, `counts.total 37`, `reportDir .ufo/waves/round-37/w1/out`.
- Reports under `.ufo/waves/round-37/w1/out/`; the L1 closes the set and records the dead seats per the report contract.

Sources reopened this round (read-only GET; one URL per row; receipts under the same `out/` directory):

| S-id | URL | Receipt | Observed |
|---|---|---|---|
| S330 | https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/ | `FetchS330.md` | 200, 435441 bytes |
| S333 | https://docs.sglang.io/docs/advanced_features/radix_eviction_policy | `FetchS333.md` | 200, 296606 bytes; no version pin on page |
| S334 | https://docs.sglang.io/docs/advanced_features/session_radix_cache | `FetchS334.md` | 200, 277182 bytes |
| S335 | https://arxiv.org/abs/2312.07104 (+ `/html/2312.07104v1`) | `FetchS335.md` | 200, 43414 bytes; 200, 214951 bytes |
| S346 | https://github.com/AaronYang238/llm/blob/35b83cee…/chapters/06-推理引擎.md (raw route) | `FetchS346.md` | 200, 36737 bytes |
| S347 | https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html | `FetchS347.md` | 200, 59059 bytes |
| S363 | https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/ | `FetchS363.md` | 200, 215347 bytes |

Assimilation scratch (`.ufo/waves/round-37/assimilation/`): `collisions` is empty; the indented-row fixture catches S330; `quarantine-slice` lists seven kama register rows (S200, S202, S206, S210, S211, S224, S230), all `payload-absent`; the register was not edited.

Counting-tip hazard (re-derived by `ReviewAppend.md`): lane `HEAD` is detached at `873c5d77`, a four-commit r36 sandbox mutation series whose `tip:corpus/lessons/round-36.md` is `0418795f…`, not the pinned `6fb1ec15…`. Lane `master` is `6a4afdfe` (= base); `jj` `@` is `7e4b6071` and carries the clean r36 bytes. The round-37 counting tip must be a commit whose tree carries (a) the clean r36 lesson blob `6fb1ec15…`, (b) the fleet report blob `8b7408e6…` at fleet `HEAD`, and (c) `.ufo/waves/round-36/census-end.out` plus the two r36 seat logs that D3 names. The census is still untracked on disk and absent at base; without it, no correction row can make C1 meet.

Seat reports this skeleton relies on: `FetchS330.md`, `FetchS333.md`, `FetchS334.md`, `FetchS335.md`, `FetchS346.md`, `FetchS347.md`, `FetchS363.md`, `ExecCollision.md`, `ReviewAppend.md`, `ReviewFrontier.md`, `CriticD3Accounting.md`.

## Draft notes — remove before landing

- **Not the corpus file.** Copy sections out of this skeleton; never copy the file wholesale.
- **Placeholders:** author name; ScribeEntries draft paths; three coverage-map `covers` cells; three reject verdicts and flips; the final KQ46 text; the L1's Claims prose and control receipts.
- **Build dependencies before the counting tip is scored:** commit `.ufo/waves/round-36/census-end.out` (D1 leg is `census_base is None and census_tip is not None`), and keep `.ufo/waves/round-36/w3/out/seat-exit-codes.json` plus `ScribeLog/seat.log` and `RevQ206/seat.log` in the same tree (D3 leg reads them at the tip). The census file is present on disk (12426 bytes) and absent from `master`/base.
- **Row-integrity rule for the landing pass:** each correction row must stay on one physical line and keep the exact tokens the counter checks: `R36-D1` + `.ufo/waves/round-36/census-end.out`; `R36-D2A` + `S371` + `native_api` + `miswritten`; `R36-D2B` + `http_server.py` + `S364`, `S365`, `S377`, `S396` and no restatement of the four wrong ids; `R36-D3` + `ScribeLog` + `RevQ206` + `429` and no restatement of the two excluded exit classes. The draft rows above were written to those tokens; a later edit must not add a second `R36-D…:` line, because the counter keeps the last matching line per id.
- **Report-side obligation (D3):** the lesson row is not sufficient on its own; `.ufo/reports/round-37/kama.md` must name both rc=1 seats with their last error text (CriticD3Accounting §0–1), and the frozen counter forbids the full three-class split inside the lesson row.
- **D2B endpoint-health set:** verified against the staged entry at `/home/vgpnk/Projects/shokuknow/merge/kama/amendments/corpus/knowledge/endpoint-health-probe-conventions.md`, whose `source:` lines are S332, S336, S337, S338 and S339.
