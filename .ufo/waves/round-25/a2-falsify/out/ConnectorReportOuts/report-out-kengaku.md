# Report-out draft: kengaku (shared-pool concurrency half)

For the round-25 report only. Not for the kengaku repo; kama writes nothing there.

**What kama found.** On llama.cpp build 11755 (commit 704366d76), the per-slot
context number limits one request; it does not promise that capacity to several
requests at once. With one shared 2048-cell pool and two concurrent requests of
1000 prompt tokens plus 600 generated tokens each, both requests failed with
HTTP 500 `Context size has been exceeded.` once each reached 1025 tokens
(2 × 1025 cells overflow 2048). Both admitted requests failed, not only the
newer one. The same requests sent one after the other both succeeded, and a
split cache four times larger succeeded concurrently. The replicate seat saw
the same outcome in 3 of 3 fresh-server runs per cell.

**Evidence path (kama lane, commit fa3b62ae).**
- `corpus/knowledge/context-capacity.md:99-125` (L1, L2, L3 table and event order).
- `.ufo/waves/round-25/final/raw/L1.server.log:1849` "send_error: task id = 2, error: Context size has been exceeded." and `:1866` "stop processing: n_tokens = 1025".
- Source S109, `tools/server/server-context.cpp` lines 4294-4341 at the pinned commit (`corpus/SOURCES.md:121`).
- Kama's own decision row: `SKILL.md:688`.

**Where it meets kengaku.** Kengaku's committed 34113 launch line has
`--ctx-size 16384 ... --fit off --kv-unified ... --parallel 2`
(`corpus/evidence/round10-fleet/r10-scout-endpoint.md:33`). Kengaku says each
slot reports "the **full** 16384, not 16384/2" (`r10-scout-endpoint.md:67`) and
"slot draws do not share a halved context" (`SKILL.md:495`). That is correct
about the per-slot cap. It is silent on concurrency: both slots draw on one
16384-cell pool. This is a refinement, not a contradiction; kengaku already
calls the cache "shared across the 2 slots" (`r10-scout-endpoint.md:74`).

**What kengaku would need to check.**
1. For any round where both 34113 slots ran draws at the same time, whether the
   two requests' prompt plus generated tokens together could exceed 16384.
2. If so, whether any HTTP 500 `Context size has been exceeded.` result, or
   both draws of a pair failing together, was graded as a model failure rather
   than a serving-capacity failure.
3. Whether `r10-scout-endpoint.md:74` and `SKILL.md:494-495` should add that
   concurrent draws are bounded by the pool total, not by the per-slot number.

**Limits.** Kama's result is from build 11755, a 2048-cell pool and one
request shape (two 1000 + 600 token requests). Kengaku's server was build
b1-d7bd3bf with a quantized q4_0 KV cache and a 16384 pool. That the same
failure mode applies there is [INFERENCE], not observed. 34113 is historical
("endpoint refuses connections since 2026-10-15", kengaku `SKILL.md:663`), so
the check runs on committed records only; nobody probes 34113.
