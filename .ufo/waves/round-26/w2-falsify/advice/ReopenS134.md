ATTACK S134: partial

# Scope

Row S134 (KQ31 supersession of S112) at `corpus/SOURCES.md:146`, its Gate row
`corpus/lessons/round-26.md:47`, and the round-26 Gate paragraph
`corpus/lessons/round-26.md:12-20`. Fresh re-open of
`tools/server/README.md` at 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad on
2026-10-23. No llama-server started, no port block used, no install.

# Fresh fetch and hash

    $ curl -sS -L -o README.md \
      https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md
    http=200
    $ sha256sum README.md
    714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37  README.md
    $ wc -l README.md
    2402 README.md

The S134 anchor's `raw sha256 714c067b...6a37` (`corpus/SOURCES.md:146`) equals
the fresh fetch byte-for-byte hash. Cross-check against lane snapshots:

    $ sha256sum .ufo/waves/round-16/sources/llama.cpp-704366d/README.md \
                .ufo/waves/round-17/sources/llama.cpp-704366d76/tools/server/README.md
    714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37  (round-16)
    714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37  (round-17)
    $ diff -q /fast/scratch/hyaku/kama-r26w2/ReopenS134/README.md \
              .ufo/waves/round-17/sources/llama.cpp-704366d76/tools/server/README.md
    exit 0

[observed] S134's hash is correct against the fresh fetch and against both older
lane snapshots. [observed] The round-26 snapshot directory named in the Gate
does not contain the file (defect F3 below).

# Per-cell verdicts

Anchor cell (`corpus/SOURCES.md:146`, field 6):

| claim | verdict | proof |
|---|---|---|
| `option lines 50, 165, 168-169 and 177` | PASS | `sed -n '50p;165p;168p;169p;177p' README.md` -> `-c, --ctx-size N`; `--kv-unified-per-slot N`; `--cache-ram N` (maximum cache size in MiB); `--kv-unified`; `--parallel N` |
| `/completion lines 671 and 683` | PASS | heading `### POST /completion` at 492, next heading `### POST /tokenize` at 686; 671 is `generation_settings` bullet, 683 the `truncated` bullet (`sed -n '660,690p'`) |
| `/props lines 927-928` | PASS | `grep -n 'props' README.md` -> GET `/props` heading 839, POST heading 935; 927 `default_generation_settings`, 928 `total_slots` inside |
| `/metrics lines 1131-1155` | PASS | heading 1131; metric rows 1141-1155; next heading 1157 (`sed -n '1131,1165p'`) |
| `/v1/models example line 1304` | PASS | heading `### GET /v1/models` 1254; example 1288-1312; 1304 is `"n_ctx_train": 131072,` |
| `raw sha256 714c067b...6a37` | PASS (vs fetch and round-16/17 snapshots); N/A vs round-26 snapshot (file absent) | hashes above |
| scope cell ("not runtime behavior") | PARTIAL | scope forbids runtime claims, yet teaches asserts a runtime fact about `--cache-ram` (defect F2) |

Teaches cell (`corpus/SOURCES.md:146`, field 7):

| claim | verdict | proof |
|---|---|---|
| starts `supersedes S112 — ` | PASS | python: `t.startswith('supersedes S112 \u2014 ')` -> True (`grep -n '^| S134 ' corpus/SOURCES.md` -> 146) |
| "the README's only KV-pool sizing promise is --kv-unified-per-slot without -c (165)" | PASS | `grep -n "shared KV pool" README.md` -> only 165; `grep -n n_parallel README.md` -> only 165; line 165 = "context limit per parallel slot ... when set without -c/--ctx-size, the shared KV pool is sized to n_parallel*N" |
| "The --cache-ram MiB limit is for the prompt cache (168)" | FAIL (citation) | line 168 text is only `set the maximum cache size in MiB (default: 8192, 0 for decision models, -1 - no limit, 0 - disable)`. The prompt-cache link is line 170: `--cache-idle-slots ... save idle slots to the prompt cache on new task ... (default: enabled, requires cache-ram)`. `grep -ni "prompt cache" README.md` -> 170, 1157, 1161, 1177, 1181, 1197; never 168. The anchor range `168-169` excludes 170. |
| "/metrics reports n_tokens_max as a context-size high watermark, not a KV-pool metric (1131-1155)" | PASS | 1149 `llamacpp:n_tokens_max | Counter | High watermark of the context size observed.`; no KV/cache metric in 1141-1155 (`sed -n '1131,1165p'`) |
| "The options and HTTP examples do not define the served KV-pool size." | FAIL (self-contradiction) | sentence 1 of the same cell says option 165 does define it ("the shared KV pool is sized to n_parallel*N"). Unqualified, sentence 3 is false on the row's own evidence. S112's enumeration is introduced with "Otherwise n_ctx appears only as fields"; S134's sentence 3 carries no such qualifier and reads as absolute. |
| "The /v1/models example shows meta.n_ctx_train = 131072 without defining it (1304)" | PASS | `grep -n n_ctx_train README.md` -> only 1304; no prose definition anywhere in the file |
| "its training-context interpretation comes from code, not this README (S060)" | PASS | S060 (`corpus/SOURCES.md:72`) scope "per-slot served context versus training-context metadata", teaches "/v1/models separately reports n_ctx_train"; `SKILL.md:687` matches |
| status `mined`, opened 2026-10-23, recheck `on-release` | PASS | matches new-row convention and today's access date |
| used-by `corpus/knowledge/context-capacity.md, corpus/lessons/round-26.md` | PASS | `grep -n S134 corpus/knowledge/context-capacity.md` -> 258; `.../lessons/round-26.md` -> 47 |

KQ31 routing (round-25 spot-check defect 3, `corpus/lessons/round-25-verifier-spotcheck.md:213-217`):

- PASS. Defect 3 requires appended `supersedes` rows; the S112 half is satisfied
  by S134 and the old row is untouched (`corpus/SOURCES.md:124` S112 still says
  "/v1/models meta.n_ctx_train is the training context" — the exact claim S134
  corrects, so the supersession is substantive, not a duplicate). All five rows
  carry the prefix: S131->S106, S132->S107, S133->S109, S134->S112, S135->S113.
  Defect 3 explicitly did not verify the S107/S112 corrections, so no stronger
  match is required. `count-c1.py` does not reference S131-S135
  (`grep -n "S13[0-5]\|supersedes" .ufo/waves/round-26/count-c1.py` -> empty).

Gate quote (`corpus/lessons/round-26.md:47`):

- PASS on all three required properties. Located: README line 165. At most 25
  words: 12 (`python` word-split). Verbatim substring of the fetched line:
  `q in line` -> True.
- Cosmetic only: this row wraps the quote in curly quotes `“...”` while every
  neighbouring row uses backticks; the source line contains no curly quotes.

# Defects and smallest corrections

F1 (row, wording). `corpus/SOURCES.md:146` teaches sentence "The options and
HTTP examples do not define the served KV-pool size." contradicts sentence 1 of
the same cell and README:165. Smallest fix: "Apart from that conditional rule,
no option or HTTP example defines the served KV-pool size."

F2 (row, citation/scope). Same cell: "The --cache-ram MiB limit is for the
prompt cache (168)". README:168 does not mention the prompt cache; the tie is
README:170, outside the anchor range. Smallest fix: extend the anchor from
`168-169` to `168-170` and word the claim as README-bound, e.g. "cache-ram is
documented as the maximum cache size (168) and is required by the prompt-cache
carry-over option (170)".

F3 (lesson Gate, not the row). `corpus/lessons/round-26.md:14-15` says "the
fetched bytes equal the lane snapshot `.ufo/waves/round-26/sources/llama.cpp-704366d/`
(sha256 in each row's anchor cell)". Observed:

    $ find .ufo/waves/round-26/sources/llama.cpp-704366d -type f | wc -l
    13
    (arg.cpp common.cpp gguf.cpp llama-context.cpp llama.cpp llama-model-loader.cpp
     server-common.cpp server-context.cpp server.cpp server-http.cpp server-models.cpp
     server-queue.cpp server-task.cpp)

No `README.md` (S134, S112), no `fit.cpp` (S131), no `llama-kv-cache.cpp` (S135).
The equality claim is therefore false as written for S134 (and S131/S135); the
bytes do equal the round-16 and round-17 snapshots and the fresh fetch
(sha256 714c067b...), so the substance is sound. Smallest fix: add the three
files to the round-26 snapshot, or narrow the Gate sentence to the files that
snapshot actually holds and name the round-16/17 copies for docs rows.

# Notes and gaps

- No LSP involvement: this attack is line-level byte verification against a
  fetched document, not symbol resolution; no server applies.
- Unrun: the frozen counter (outside my item), any live llama-server, and every
  SKILL.md E26 claim. Nothing above rests on them.
- S134 does not appear in `registry/error-signatures-r26.json` (that registry is
  S114-S130), so no cross-file propagation of F1/F2 was found; the only citing
  files are the two used-by paths and neither restates the defective sentences.

# Files written

- `.ufo/waves/round-26/w2-falsify/advice/ReopenS134.md` (this report)
- `/fast/scratch/hyaku/kama-r26w2/ReopenS134/README.md` (scratch fetch, 2402 lines)
