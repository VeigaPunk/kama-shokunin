# Advice — SrcServerReadme (round 25 attempt 2, build wave 1)

Verdict: the llama.cpp server README at 704366d76 promises only one pool-sizing rule
(`--kv-unified-per-slot` -> pool = n_parallel*N); it never defines the served n_ctx
values this round's C2 cells observe, so the docs row is needed as the *promise* side of
the claim and must not be cited for any served value.

## What I did

Read first (all exit 0): `.ufo/waves/round-25/preregistration.json`,
`preregistration-amendment-1.json`, `preregistration-amendment-2.json` (binding for
attempt 2), `count-c2.py`, `pilot.md`, `build/ATTEMPT-1-DISPOSITION.md`. No llama-server
child started; no source edit; no SOURCES.md edit.

Fetched fresh:
`curl -fsSL https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md`
-> /fast/scratch/hyaku/kama-r25a2/SrcServerReadme/README-704366d.md (2402 lines, exit 0).

sha256 (fresh fetch): `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37`.
Byte-identical (`cmp -s` exit 0) to the round-16 pinned snapshot
`.ufo/waves/round-16/sources/llama.cpp-704366d/README.md` (same sha256) and to the sha256
recorded in SOURCES row S035, so the file is unchanged since round 16.

## What the docs promise n_ctx means

- Line 50 (`-c, --ctx-size`): "size of the prompt context (default: 0, 0 = loaded from
  model)" — an unset `-c` resolves to the model's context; the README does not say how a
  loaded model context divides across slots.
- Line 177 (`--parallel`): "number of server slots (default: -1, -1 = auto)".
- Line 169 (`--kv-unified`): "use single unified KV buffer shared across all sequences
  (default: enabled if number of slots is auto)" — the default flips on the auto/slot
  combination, but the resulting per-slot arithmetic is not documented.
- Line 165 (`--kv-unified-per-slot`): "when set without -c/--ctx-size, the shared KV pool
  is sized to n_parallel*N" — the only place the README ties n_ctx to pool arithmetic.
- Line 927: `/props` default_generation_settings "has the same fields as the
  generation_settings response object from the /completion endpoint" (line 671: includes
  `n_ctx`, `model`). The README never states whether this n_ctx is per-slot or pool-level.
- Line 928: `/props` `total_slots` "the total number of slots for process requests
  (defined by `--parallel` option)".
- Lines 983-1126: `/slots` returns per-slot processing state; n_ctx appears only as
  example values (65536 at lines 999 and 1064), never as a defined semantics.
- Line 1304: `/v1/models` meta example carries `n_ctx_train` (training context).
- Line 683: /completion `truncated` defines n_ctx as the context size exceeded when
  `tokens_evaluated` + `tokens predicted` > n_ctx — the only in-README definition of what
  n_ctx bounds (a single generation's evaluation).

## What the source does NOT establish (does-not-establish list)

1. Whether `/props` default_generation_settings.n_ctx is per-slot or pool-wide. The README
   never defines it; the pilot.md reading ("/props n_ctx is a per-slot value") is not in
   this file — it can only be grounded by the code row S060.
2. The served per-slot n_ctx for any `-c`/`-np`/`--kv-unified` combination (all of K1-K8,
   X1-X3 depend on values this file does not promise); the `--kv-unified-per-slot` rule is
   the only documented arithmetic.
3. The unset-context (auto, `-c 0`) split behavior that X1/X3 probe: "0 = loaded from
   model" (line 50) does not say how the loaded training context is divided across slots,
   and nothing here decides between round-20's per-slot 512 and the fit.cpp-derived 2048.
4. The full-context concurrency limit of a shared pool (L1-L3): the README has no
   statement about concurrent requests exceeding pool capacity, and no error text such as
   "Context size has been exceeded"; the `truncated` flag (line 683) is in-generation
   truncation, not a concurrency failure.
5. The runtime KV pool size: it appears in no HTTP surface described here (the count-c2.py
   requirement for a captured `llama_context: n_ctx` log line has no README counterpart).
6. Agreement between `/props`, `/slots` and `/v1/models` values — the README neither claims
   nor denies it; amendment 1's caution that they read one server function is not answered
   by this file.
7. Anything about this round's fixture (stories260K.gguf, training context 2048) — the
   README speaks generically; `n_ctx_train` values in examples belong to other models.
8. The loading/503 lifecycle — intentionally out of scope; that is S035/S036/S037.

## Existing SOURCES rows on this file

- S035: same file, same commit, but scope is only `/health` (lines 479-490) and `/v1/models`
  line 1258; it explicitly excludes `/v1/models` loading behaviour and covers none of the
  props/slots/option sections. It does not cover this claim.
- S060: the server-context.cpp code row (implementation; /props reports capped per-slot
  n_ctx) — complementary, not a substitute for the docs promise.
- No other row matches the props/slots/ctx grep.
=> A new row (S1xx draft, status queued) is needed; it is drafted in
   `out/SrcServerReadme/draft-row.md`.

## Files written

- `.ufo/waves/round-25/a2-build/out/SrcServerReadme/draft-row.md` (draft row + why-new)
- `.ufo/waves/round-25/a2-build/out/SrcServerReadme/gate-record.md` (Gate: URL, access
  date 2026-10-22, quotes, sha256, byte-identity check)

No production file was edited; no server started; no installs performed (no tool
installation was needed).
