# FetchS346 — source reopen: llm chapter 06 (推理引擎), §6.4 SGLang

Read-only, single authorized GET. No row appended; no repo file edited.

## Fetch receipt (observed)

| Field | Value |
|---|---|
| URL requested | `https://raw.githubusercontent.com/AaronYang238/llm/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md` |
| HTTP status | `200` |
| Bytes downloaded | `36737` |
| Lines | `587` |
| sha256 | `2ed9f7acd96730f97e0bf0066c991f8bb683f40c5bc65f3f1d4ea3f42995ed8c` |
| Local copy (scratch) | `.ufo/waves/round-37/w1/out/FetchS346/06-reasoning-engine.md` |
| Fetch time | 2026-10-25, single GET, no redirects followed manually, no other URLs touched |

## Section located

- File H1: `# 阶段 6｜推理引擎深读 ★★★★ ✓` (line 1).
- `## 6.4 SGLang 深读` — **line 296**. Subsections: `### 6.4.1 架构总览：与 vLLM 的异同` (300), `### 6.4.2 RadixAttention：招牌机制` (335), `### 6.4.3 DeepSeek-V3 全套优化` (365), `### 6.4.4 适用场景与限制` (387). Section ends before `## 6.5 TensorRT-LLM(对照)` at line 405.

## File-level map lines (the requested rows)

Table introduced at line 328 by `源码定位(`python/sglang/srt/`):` — i.e. the map is rooted at the SGLang package path `python/sglang/srt/`, with columns `路径 | 类 | 职责`.

Verbatim, lines 330–331 (9 words total, ≤25):

```
| `mem_cache/radix_cache.py` | `RadixCache` | 基数树 prefix cache |
| `managers/schedule_policy.py` | `SchedulePolicy` | LPM 等调度策略 |
```

Neighbouring rows for context (same table, lines 329–334): `managers/tokenizer_manager.py | TokenizerManager`, `managers/scheduler.py | Scheduler`, `managers/tp_worker.py | TpModelWorker`, `model_executor/model_runner.py | ModelRunner`.

The same two symbols also appear in the §6.4.1 loop diagram (lines 305–311): `├─ RadixCache      # 基数树 prefix cache（SGLang 招牌）` and `├─ Policy          # 调度策略（LPM 最长前缀匹配优先等）`.

## Content bearing on the lane theme

- §6.4.2 (line 335) states the reuse/reclamation model in three numbered points — RadixCache holds KV for all live prefixes with token segments on edges and fork points as nodes; LPM schedules the longest matching prefix first; LRU evicts **leaf** branches under memory pressure while referenced nodes are untouched (lines 341–343).
- Lines 347–364 give an abbreviated RadixCache skeleton with `match_prefix`, `insert` (splits at fork points) and `evict` (`LRU：从最久未访问的叶子开始回收，被引用节点跳过`).
- §6.4.1 comparison table (line 319) contrasts `hash 链式(扁平)` in vLLM against `RadixCache 基数树(层级共享)` in SGLang.

## Tier

**B at most — never A.** This is a community write-up: a personal GitHub repository (`AaronYang238/llm`) of self-published Markdown study notes at a pinned commit `35b83cee12ae26f10b58d4163298352384503907`. Observed markers of secondary status: prose chapters with star ratings and a "自测"/"延伸阅读" apparatus (lines 554, 576), cross-references to its own "阶段" structure, and a code skeleton explicitly labelled simplified (line 347 `核心代码骨架(radix_cache.py 简化)`). It carries no upstream maintainer signature, no review, and no release tag. Its file-path and class claims are assertions *about* SGLang, verified here only as text present in this document, not against SGLang source.

## Not done / gaps

- No `corpus/SOURCES.md` edit. Recorded fact only: `grep` over `corpus/SOURCES.md` (462 lines) finds no row mentioning `AaronYang238` — this URL currently has no S-id.
- Unverified here (out of scope for this fetch): whether upstream SGLang at any given revision still organizes these under `python/sglang/srt/mem_cache/radix_cache.py` and `.../managers/schedule_policy.py`, and whether `SchedulePolicy` is the live class name. Any lane use as a path/class claim needs a primary reopen of the SGLang tree.
- Confidence: high for fetch receipt, line numbers, and verbatim text (direct byte inspection with `sha256sum` and raw line reads); **low-to-medium** for any technical assertion the chapter makes about SGLang behaviour.
