Proposed append to corpus/SOURCES.md (round-46 seat L2Lowthr; NOT applied — proposal text only).

Placement: appended at the end of the file's corrections region, after the last
`## Corrections — …` block, so no existing line moves (KQ7/QK22/KQ26).

---

## Corrections — round 46 (2026-10-26) — id `S192` aliasing (append-only record)

`S192` has denoted two different sources. It was first the llama.cpp b11755
`tools/server/server-schema.cpp#L64` row (`->add_alias("n") // alias "n" as
fallback (OpenAI completions API)`, "the schema declares n as the OpenAI fallback
alias of n_cmpl"), opened at `3b1e84f8` (round 31) and dropped at `54c6f4fe`
(same round: "remap S180-S191 … and drop the duplicate K31-14 row"); its text
continues at `S191`. From `c16fe3e5` (round-31 attempt 3) `S192` denotes the
OpenAI Chat Completions API reference (`response_format`). A citation `S192`
written between `3b1e84f8` and `54c6f4fe` therefore means the n_cmpl alias row,
and after `c16fe3e5` it means the OpenAI reference.

No row text was lost (the n_cmpl row text is `S191` today); what changed is the
id→source mapping. `54c6f4fe` also rewrote `S190` and `S191` on `source`, `scope`,
`anchor` and `teaches` in place, which KQ22 forbids without an appended record;
this note is that record for the three rows.
