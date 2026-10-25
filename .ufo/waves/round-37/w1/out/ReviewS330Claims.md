# ReviewS330Claims — claim-vs-source check for S330

Seat: `L1Kama37.HappyAnt`. Read-only. No corpus/registry/knowledge file was touched.

## Source used

`FetchS330.md` was **absent** from `.ufo/waves/round-37/w1/out/` at review time (dir listing
04:56 had `FetchS333/ S334/ S335/ S346/ S347.md S363/`, no S330). Per assignment, I ran the one
authorized GET:

```
curl -fsSL -o /tmp/S330-live.html -w 'status=%{http_code} bytes=%{size_download} url=%{url_effective}\n' \
  'https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/'
-> status=200 bytes=435441 url=https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/
```

The live bytes are **byte-identical** to the wave's pre-staged copy
(`.ufo/waves/round-37/w1/fetches/S330.html`, 435441 bytes, `cmp` → identical), so all offsets below
are valid for both. Page is minified to 13 lines; evidence is cited by raw-HTML byte offset and by
verbatim paragraph, not by line.

Headings, in document order (h1–h4, `id=` from the page):

| offset | level | heading | id |
|---|---|---|---|
| 414650 | h1 | vLLM V1 | — |
| 417590 | h2 | Differences from V0 | `differences-from-v0` |
| 417790 | h3 | Chunked Prefill | `chunked-prefill` |
| 418048 | h3 | CUDA Graphs | |
| 418215 | h3 | Semantic Changes to Logprobs | |
| 418368 | h4 | Logprobs Calculation | |
| 419219 | h4 | Prompt Logprobs with Prefix Caching | |
| 419653 | h2 | Feature Support | `feature-support` |
| 420901 | h3 | Hardware | |
| 421953 | h3 | Models | |
| 424003 | h3 | Encoder-Decoder Models | |
| 424836 | h3 | Features | |
| 428888 | h4 | Removed Features | |

**There is no `§Scheduler` heading on this page.** `id=scheduler` is absent, `#scheduler` is absent,
and every other occurrence of "scheduler" is either an API-reference **nav link**
(`api/vllm/v1/core/sched/scheduler/`, 365077; `api/vllm/config/scheduler/`, 101370) or prose in the
intro paragraph at 416379 ("significantly re-architects the core systems, covering the scheduler,
KV cache manager, worker, sampler, and API server").

## The claim set, and verdicts

Claims are listed exactly as they are attributed to S330 by (a) the staged row in
`/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` line 7 ("S330 … corpus/knowledge/
kv-cache-reclamation-models.md") and (b) the staged entry
`/home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus/knowledge/kv-cache-reclamation-models.md`.

### A. Staged row cells

| # | Claim (as written) | Verdict | Evidence |
|---|---|---|---|
| A1 | vLLM V1 Guide at `https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/`, kind `docs` | **SUPPORTED** | HTTP 200, canonical `https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/` (offset 167), official docs.vllm.ai host |
| A2 | page version v0.19.1 | **SUPPORTED (metadata only)** | `rel=canonical` (167) + `<meta name="readthedocs-version-slug" content="v0.19.1">` (2341). No visible in-body version banner found; the row's wording "docs page version v0.19.1" is fine, but the marker is not in body text |
| A3 | anchor `§Scheduler` — "V1's unified scheduler treats both prompt and output tokens the same way" | **quote SUPPORTED, section label NOT SUPPORTED** | sentence opens the admonition at 420266: "vLLM V1’s unified scheduler treats both prompt and output tokens the same way by using a simple dictionary (e.g., {request_id: num_tokens} ) to dynamically allocate a fixed token budget per request, enabling features like chunked prefills, prefix caching, and speculative decoding without a strict separation between prefill and decode phases." Nearest preceding heading = h2 **Feature Support** (419653); the identical note is duplicated at 428539, under h3 **Features** (424836). No §Scheduler exists |
| A4 | anchor `§Chunked Prefill` — "Chunked prefill is enabled by default whenever possible" | **SUPPORTED** | h3 `Chunked Prefill` (417790, `id=chunked-prefill`), subsection of h2 Differences from V0; paragraph at 417907: "Chunked prefill is enabled by default whenever possible, unlike in V0 where it was conditionally enabled based on model characteristics." Byte-exact match |
| A5 | scope: "one token budget spans prompt and output tokens" | **SUPPORTED** | "treats both prompt and output tokens the same way … dynamically allocate a fixed token budget per request" (420266). Note the page's budget is per-request, and it is *dynamically* allocated per request — the row's "one token budget spans prompt and output" is a correct compression |
| A6 | scope: "chunked prefill is on by default" | **SUPPORTED with hedge dropped** | page: "enabled by default **whenever possible**, unlike in V0 where it was conditionally enabled based on model characteristics." The row's unqualified "on by default" states more than the page does |
| A7 | scope: "FCFS or priority scheduling via `--scheduling-policy`" | **SUPPORTED (list is open)** | 420625: "The V1 scheduler supports multiple scheduling policies, **including** First-Come, First-Served (FCFS) and priority-based scheduling (where requests are processed based on assigned priority, **with FCFS as a tie-breaker**), configurable via the `--scheduling-policy` argument." "including" ≠ exhaustive; row's "FCFS or priority" reads as a closed set |
| A8 | "not a runtime observation" | **SUPPORTED / consistent** | nothing in the row asserts observation; the page is documentation only |
| A9 | recheck: `curl -fsSL '…' \| grep -c 'unified scheduler'` expect ≥1, ran 2026-10-23 | **command non-failing, scope narrow** | on the fetched bytes it returns `1` (exit 0). Because the page is 13 minified lines, both occurrences collapse to one matched line and the ≥1 test is satisfied by either copy; the command cannot detect drift in A4/A6/A7 |

### B. Entry claims attributed to S330

| # | Claim (as written) | Verdict | Evidence |
|---|---|---|---|
| B1 | source line "§Scheduler and §Chunked Prefill — page version v0.19.1" | **§Chunked Prefill SUPPORTED; §Scheduler ABSENT** | same defect as A3; the entry propagates the non-existent section anchor into its provenance line |
| B2 | "treats both prompt and output tokens the same way" | **SUPPORTED** | verbatim, 420266 (curly apostrophe `’` in "V1’s") |
| B3 | "allocating a fixed token budget per request from one dictionary" | **SUPPORTED** | "by using a simple dictionary (e.g., {request_id: num_tokens} ) to dynamically allocate a fixed token budget per request" |
| B4 | "which is what makes chunked prefill possible" | **SUPPORTED (causal wording slightly stronger)** | page says the unified treatment enables "features **like** chunked prefills, prefix caching, and speculative decoding" — enabling, not sole cause |
| B5 | "chunked prefill is on by default" | **SUPPORTED with hedge dropped** | same as A6: "whenever possible", plus the V0 contrast, are missing from the entry |
| B6 | "Scheduling policy is FCFS or priority, with FCFS as the tie-breaker" | **SUPPORTED except closed-set wording** | tie-breaker verbatim ("with FCFS as a tie-breaker", 420625); source list is introduced by "including" |
| B7 | "Reclamation is therefore block-pool and admission-shaped, not tree-shaped" | **NOT SUPPORTED BY S330 — absent** | page contains 0 occurrences of `reclaim`, 0 of `evict`, 0 of `block pool`, 0 of `admission`. `block_pool` appears twice, both as API nav links (`api/vllm/v1/core/block_pool/`, offsets inside the nav tree). With S330 as the entry's only vLLM source, this sentence has no page support and must be marked as the entry's own inference |
| B8 | entry framing that the two models explain "why a served request is slow, rejected, or re-prefilled" | **NOT SUPPORTED BY S330** | the page documents scheduler/batching/feature status; it makes no statement about served-request latency, rejection, or re-prefill |

## Findings, by severity

**H1 — HIGH, provenance fabrication: `§Scheduler` does not exist.**
Staged row cell 5 (`quote`) and entry `source:` line both anchor the scheduler sentence to
"§Scheduler". The page's headings are the twelve listed above; `id=scheduler` and `#scheduler` are
absent. The sentence is an admonition (`<p class=admonition-title>Note</p>`) at 420266/428539 inside
h2 §Feature Support / h3 §Features. A reader verifying `…#scheduler` lands on nothing (no anchor), and
a later anchor-conformance check would fail this row while the C2 predicate (S-id presence, file
existence, base absence) still passes — i.e. the defect is invisible to the frozen counters.
Correct anchor: **§Feature Support (Note), duplicated under §Features**.

**H2 — HIGH, unsupported reclamation claim on the vLLM side.**
Entry B7 (and B8) attribute a *reclamation model* to vLLM while the only vLLM source cited has zero
`reclaim`/`evict`/`block pool`/`admission` prose. The word "therefore" turns an inference into a
consequence of the quote. This is the entry's weakest link: the vLLM bullet's reclamation analysis is
not source-backed, only its scheduling/token-accounting premises are.

**M1 — MEDIUM, print fidelity of the first quote.**
The row quotes `"V1's unified scheduler…"` with an ASCII apostrophe; the page carries U+2019
(`V1’s`). Raw-byte grep for the quoted fragment therefore fails on the page, even though the
fragment is verbatim modulo the apostrophe. `"…same way" in html` → False with `'`, True with `’`.
Any mechanical quote-conformance check must normalize apostrophes, or the row will look fabricated.

**M2 — MEDIUM, hedge loss on the chunked-prefill default.**
Both A6 and B5 drop "whenever possible" and "unlike in V0 where it was conditionally enabled based on
model characteristics". The page's claim is conditional capability, not unconditional default. A
served-endpoint reader could infer chunked prefill always runs.

**L1 — LOW, closed-set reading of an open list.**
"The V1 scheduler supports multiple scheduling policies, **including** FCFS and priority-based" →
row/entry "FCFS or priority". No third policy is named on the page, so nothing contradicts it, but the
wording asserts exhaustiveness the source does not.

**L2 — LOW, recheck command coverage.**
`grep -c 'unified scheduler'` passes (returns 1 on 13 minified lines) but re-tests only A3's phrase;
A4/A6/A7 could drift entirely and the recheck would still pass. It also cannot distinguish "note
present once" from "note present twice".

**L3 — LOW, code-literal grep caveat.**
`configurable via the --scheduling-policy argument` is **not** a raw-HTML substring (the flag is
wrapped in `<code>--scheduling-policy</code>`); it is a substring only after tag stripping. A
byte-level verifier for A7 must strip markup first.

## What is NOT a finding

- The two Note paragraphs at 420266 and 428539 are byte-identical; the duplication is the page's, not
  a provenance error.
- `{request_id: num_tokens}` formatting, the emoji status legend, and "🟢 Functional" statuses are
  reproduced correctly wherever the row/entry paraphrase them.
- No claim attributed to S330 is contradicted by the page. Every **factual** proposition in the row
  (A5, A6, A7) and in the entry's stated premises (B2, B3, B6 tie-breaker) is present on the page;
  the defects are anchor attribution (H1), hedge loss (M2), and an unsourced inference (H2).

## Residual risk / verification gaps

- Byte offsets are for the 2026-10-25 fetch; the URL is version-pinned (`/en/v0.19.1/`) but the page
  carries "the guide will be updated constantly" language at 416379-adjacent prose, so "pinned" is by
  path, not by immutable content. No archive snapshot hash exists in the row.
- FetchS330's own seat report never appeared, so its HTTP/quote findings could not be cross-checked
  against mine; my numbers (200 / 435441 / no redirect) are from my single GET and agree with the
  wave-staged copy.
- Reclamation/eviction behaviour was not observed on this host and S330 would not license such an
  observation; nothing here changes the entry's "what this entry does not establish" caveat.
- No installs or upgrades were performed; only one authorized read-only `curl` GET.
