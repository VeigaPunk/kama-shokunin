# FetchS335 — source reopening: arXiv 2312.07104v1 (SGLang)

Lane: kama, round 37, wave 1. Read-only fetch; no corpus writes, no ledger row appended.

## Fetch receipts

| # | URL | Method | HTTP status | Bytes on wire | Content-Type | Saved at (seat scratch) | SHA-256 |
|---|---|---|---|---|---|---|---|
| 1 | `https://arxiv.org/abs/2312.07104v1` | GET | **200** | **43,414** | text/html; charset=utf-8 | `.ufo/waves/round-37/w1/out/FetchS335/scratch/abs-2312.07104v1.html` | `5d2d5eb082bb73d89f1f751b8ee012388c064494e1a04a98bcd3d182f32fdc0b` |
| 2 | `https://arxiv.org/html/2312.07104v1` | GET | **200** | **214,951** | text/html; charset=utf-8 | `.ufo/waves/round-37/w1/out/FetchS335/scratch/html-2312.07104v1.html` | `ea21c80c9991952494fe999449d5eef3f91fa36bb75b1af2ae42db12a3b494df` |

Both saved in full (no truncation; `-L` followed no cross-host redirect). Scratch dir is under the seat directory and is scratch-only.

## Source identity (observed)

- `citation_title` on the v1 abs page: **"Efficiently Programming Large Language Models using SGLang"**
- `citation_arxiv_id`: `2312.07104`; `citation_date` / `citation_online_date`: `2023/12/12`
- Submission history on the abs page: `[v1] Tue, 12 Dec 2023 09:34:27 UTC (380 KB)`; a `[v2] Thu, 6 Jun 2024 00:10:06 UTC (804 KB)` is also listed (not fetched; its title is not observed here).

## Located statements

Section map from the HTML full text (render-ready plain-text offsets; `<h2>`/`<h3>` order as extracted):

```
5 Runtime with RadixAttention
5.1 RadixAttention            <- spans offsets 30838..32289
5.2 Cache-Aware Scheduling    <- starts 32289
```

The two §5.1 eviction statements sit at offsets 31661 and 31929, both inside **5.1 RadixAttention** and both in paragraph `S5.SS1.p2.1` of the HTML source; the §5 intro cache-aware sentence (offset 30602) is in `S5.p2.1`, before the 5.1 heading.

### 1. Reference counter (exact target sentence)

**Section: 5.1 RadixAttention** — found verbatim, one sentence, no intervening markup:

> "A node is evictable if its reference counter is zero." (10 words)

Raw HTML context is plain text inside `<p id="S5.SS1.p2.1">`; the immediately preceding sentence is "Therefore, each node maintains a reference counter indicating how many running requests are using it."

### 2. LRU eviction policy (recursive leaf eviction)

**Section: 5.1 RadixAttention**:

> "we implement an LRU eviction policy that recursively evicts leaf nodes" (11 words)

Preceded verbatim by: "we cannot retrain infinite KV cache tensors, which necessitates an eviction policy." — note the paper's own wording is **"retrain"** (sic; "retain" intended), quoted only to flag the source spelling, not asserted as a claim.

### 3. LRU + cache-aware scheduling (cache hit rate)

**Section: 5 Runtime with RadixAttention** (intro paragraph `S5.p2.1`, which precedes the 5.1 heading at offset 30838; the sentence is at offset 30602, so it is *not* inside 5.1):

> "We implement a Least Recently Used (LRU) eviction policy, complemented by a cache-aware scheduling policy, to enhance the cache hit rate." (21 words)

### 4. Abstract-level LRU/KV-cache statement (supplementary)

**Section: Abstract**:

> "maintains a Least Recently Used (LRU) cache of the Key-Value (KV) cache for all requests in a radix tree" (19 words)

## Observations for downstream use

- The v1 text states eviction is **leaf-only and recursive** under an LRU policy, gated by per-node reference counters ("cannot evict nodes that are being used by the currently running batch"), and pairs LRU with a cache-aware scheduler. [INFERENCE] That is a different mechanism description from paged/block-level reclamation language, so it should not be conflated with vLLM's block-manager vocabulary; the paper itself says nothing about vLLM here.
- This is SGLang **v1** ("Efficiently Programming Large Language Models using SGLang"), not the later retitled paper; any knowledge file citing this id should carry the v1 title/date observed above.
- "retrain" for "retain" is present in the committed v1 bytes; verbatim quotes must preserve it.

## Confidence and gaps

- **High** for status/bytes/hashes and for every quote plus its section attribution (raw HTML paragraph ids cross-check the heading offsets).
- **Not covered (out of scope, not fetched):** v2 text and its statements; SGLang source code (no `sgl-project/sglang` code was opened, so nothing here is asserted about implementation beyond the paper's prose); no HTML equation rendering checks; no PDF cross-check.

No row appended anywhere; no corpus, ledger, or package file touched.
