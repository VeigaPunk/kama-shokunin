source: S058 (GGUF specification da8e2a54), S060 (llama.cpp server-context.cpp at 704366d76), S039 (stories260K file); corpus/lessons/round-20.md Gate; .ufo/waves/round-20/build/advice/SrcServerNctx.md
verified-at: 2026-10-21 — pinned sources opened in round 20; existing live receipt replayed offline, not a new server observation
recheck: on-release — run tools/gguf-identity.py on a byte-pinned local model and --receipt on a newly gated receipt; reopen the pinned format and server context sources

# Declared GGUF identity versus captured serving metadata

A GGUF header declares metadata. A header reader neither loads weights nor
proves the file is loadable, good, licensed, authentic or used by a server.
A file SHA-256 binds observed bytes; the receipt remains self-reported.

## Format boundary (S058)

- The magic is the four literal bytes `GGUF`; version is uint32. V2/v3 count
  tensor and metadata pairs with uint64. V3 adds big-endian support.
- Strings carry uint64 byte lengths and UTF-8 bytes, not NUL terminators.
  Values are typed scalars or arrays; array counts are elements, not bytes.
- General architecture selects `<arch>.context_length`, `.block_count` and
  `.embedding_length`; `general.name` is just a label. Missing keys mean
  unknown, not fabricated defaults (except specified alignment default 32).
- The lane tool reads bounded metadata and streams the complete file digest;
  it does not decode tensor descriptors or payloads. Its configured limits
  intentionally reject some otherwise representable files. Decoded metadata
  is not full GGUF or loader validation.

## Serving comparison (S060)

At b11755 `server-context.cpp:4654–4663`, per-slot context is capped by
`--kv-unified-per-slot` and the effective training context. `/props`
`default_generation_settings.n_ctx` is this effective per-slot value;
`/v1/models` separately supplies `meta.n_ctx_train` (`:5183–5188`).
Do not divide `ctx` by `total_slots` blindly: KV-unified and padding affect
that relationship. Do not require served context to equal training context.
Round 25: the rule, the KV pool and the fit step are in
`corpus/knowledge/context-capacity.md`, with observed cells.

The retained round-18 fixture (`live-recovery/receipt-1.json`) has served
`n_ctx=256`, training `n_ctx_train=2048`, and a GGUF declaration of 2048.
The first comparison is an informational capacity relation; the second
checks declaration agreement with the captured loaded-model metadata.
A mismatch can be a legitimate load-time override; the tool reports it,
not a claim that the runtime is unsafe or misconfigured.

Model digest equality is necessary before comparing metadata of that file
with the receipt. Matching alias/name alone is not a byte identity check.
The captured models body must be complete, HTTP 200 and digest-consistent.
A validated old receipt is historical evidence, not current endpoint health.

## Province

This capability belongs to kama's declared-versus-served identity frontier,
not kengaku's quality/evaluation work. It reads the existing 1.2 MB CI model
and old receipts without downloads, persistent servers or consumer changes.
K05 runtime-dependent identity fields and registered consumers remain open.
