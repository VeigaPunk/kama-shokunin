# Located anchors — llama.cpp `tools/server/README.md` @ 704366d76

Seat: `KamaR25.SrcServerReadmeProps` (scribe, read-only source seat).
Opened: 2026-10-22 (UTC), HTTP 200.
File sha256: `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37`
(119661 bytes, 2402 lines).

Canonical URL (pinned):
`https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md`
Raw URL used for the read:
`https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md`

Byte-identity check (independent of the fetch above): the copy retained in the repo at
`.ufo/waves/round-17/sources/llama.cpp-704366d76/tools/server/README.md` has the same
sha256 `714c067b…a6a37`, and the anchor cell of `SOURCES.md` row S035 records the same
digest for the same commit. No upstream drift between the round-17/20 opens and this
round's open.

---

## A. Located quotes (each ≤ 25 words)

| # | file line | section | quote | words |
|---|---|---|---|---|
| Q1 | 928 | §GET `/props` field list | "`total_slots` - the total number of slots for process requests (defined by `--parallel` option)" | 13 |
| Q2 | 927 | §GET `/props` field list | "`default_generation_settings` - the default generation settings for the `/completion` endpoint" | 9 |
| Q3 | 850 | §GET `/props` response example | `"n_ctx": 1024,` | 2 |
| Q4 | 914 | §GET `/props` response example | `"total_slots": 1,` | 2 |
| Q5 | 999 (and 1064) | §GET `/slots` response example | `"n_ctx": 65536,` | 2 |
| Q6 | 1304 | §GET `/v1/models` response example, `meta` object | `"n_ctx_train": 131072,` | 2 |
| Q7 | 50 | §Common params | "size of the prompt context (default: 0, 0 = loaded from model)" | 11 |
| Q8 | 177 | §Server-specific params | "number of server slots (default: -1, -1 = auto)" | 9 |
| Q9 | 169 | §Server-specific params | "use single unified KV buffer shared across all sequences (default: enabled if number of slots is auto)" | 17 |
| Q10 | 165 | §Server-specific params | "context limit per parallel slot … when set without -c/--ctx-size, the shared KV pool is sized to n_parallel*N" | 17 |
| Q11 | 683 | §POST `/completion` response fields | "the number of tokens provided in the prompt … plus tokens generated … exceeded the context size (`n_ctx`)" | 16 |
| Q12 | 63 | §Common params | "original context size of model (default: 0 = model training context size)" | 11 |

## B. Section line ranges used as anchors

- §GET `/props` — heading at line 839; example block lines 845-923; field definitions
  lines 926-933; §POST `/props` starts at 935.
- §GET `/slots` — heading at line 983; example block lines 995-1126 (`n_ctx` at 999 for
  slot 0 and 1064 for slot 1).
- §GET `/v1/models` — heading at line 1254; `meta` example lines 1301-1309
  (`n_ctx_train` at 1304).

## C. What the README does not contain (verified by grep over the whole file)

- No prose definition of any `n_ctx` field. `n_ctx` occurs at lines 50 (flag), 671
  (`generation_settings` field list), 683 (`truncated` explanation), 850 (`/props`
  example), 999 and 1064 (`/slots` examples). `n_ctx_train` occurs exactly once,
  at line 1304, inside an example object.
- No statement that `/props` `default_generation_settings.n_ctx` equals `/slots`
  `n_ctx`, nor whether either is per-slot or a pool total.
- No numeric rule for splitting `-c` across slots, no padding rule, no statement that a
  served context is capped at the model's training context.
- No numeric value for the auto slot count (the README only says `-np` default `-1 =
  auto`, line 177); the value 4 is not in the document.
- No prose about `total_slots` other than line 928; no mention of `kv_unified` as a
  `/props` or `/slots` field name (the string appears only in flag help at line 169).

## D. Proposed SOURCES row (id left as S1xx; next unused id is S106)

```
| S1xx | llama.cpp server README context and slot fields @ 704366d76 (release b11755) — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md | docs | A | llama.cpp README documentation of the context and slot fields of `/props`, `/slots` and `/v1/models` at commit 704366d76 only; not the served values (code row S060) and not `/health` (S035) | §GET `/props` lines 839-934 (`default_generation_settings.n_ctx` 850, `total_slots` 914, field definitions 927-928); §GET `/slots` lines 983-1130 (`n_ctx` 999, 1064); §GET `/v1/models` lines 1254-1313 (`meta.n_ctx_train` 1304); §Common params `-c, --ctx-size` line 50; §Server-specific params `--kv-unified-per-slot` 165, `--kv-unified` 169, `-np, --parallel` 177; raw file sha256 714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37 | The README documents `total_slots` as the slot count set by `--parallel` (line 928) and shows `n_ctx` in `/props` (850) and per slot in `/slots` (999), but defines no `n_ctx` in prose: `n_ctx_train` (1304) appears only as an example value, and the per-slot-versus-total relation, the `-c` split across slots and the training-context cap are not documented. The documentation therefore cannot decide K05 numbers; only the observed receipt can. | mined | 2026-10-22 | on-release | corpus/knowledge/context-capacity.md, corpus/lessons/round-25.md |
```

Gate quote for the round lesson (≤25 words, with location):
"`total_slots` - the total number of slots for process requests (defined by `--parallel` option)"
— `tools/server/README.md` @ 704366d76, §GET `/props`, line 928 (13 words).

## E. Draft search-log note (contract rule 5)

- **2026-10-22 — round-25 context-field documentation re-open.** Question: does the
  llama.cpp server README at the pinned build document the meaning of `/props`
  `default_generation_settings.n_ctx`, `/props` `total_slots`, `/slots` `n_ctx` and
  `/v1/models` `meta.n_ctx_train`? Where: the pinned file itself
  (`raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md`,
  HTTP 200, 2026-10-22) plus the copy already retained at
  `.ufo/waves/round-17/sources/llama.cpp-704366d76/tools/server/README.md` (identical
  sha256). Identified 1, screened 1, included 1 new row (S106), excluded 0. The file
  documents only `total_slots` (line 928) and the `-c`/`-np`/`--kv-unified` flag
  semantics (lines 50, 165, 169, 177); every `n_ctx` value in the document is an
  example value, so the docs cannot settle K05 numerics. Stop: the pinned file was
  read end to end; no further upstream document bears on these four fields.
