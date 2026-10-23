# ScoutFrontier — frontier data-walk (round 31, wave 1)

Axes walked: open-frontier inventory, overlap that would make C1 a re-score, three cheapest later depth moves. Read-only. No lane file edited except this new file.

Confidence: high on the cited line numbers below. Medium on audit-era frontier rows last restated in round 24 and then dropped from later "still open" sentences (silence is not a close).

## (a) Open frontier, and what this round opens

Current authority for what is still open is the latest disposition that names the item, not the stale bullet list at `corpus/README.md:66-78` (round-5 wording, kept by the append-only rule).

This round opens one item: the `/v1/chat/completions` parameter layer on llama-server b11755. It is the depth candidate left open at `corpus/README.md:430-434` ("the same fields through `/v1/chat/completions`") and named again at `SCORECARD.md:1439-1441` (planned round 29, not taken). Round 29 and round 30 did not advance it (`corpus/README.md:444-448`, `:459-463`). C1's frozen surface is that item: a new SKILL section `## Round-31 chat-completions parameter outcomes` plus `registry/chat-param-outcomes-r31.json` (preregistration.json C1; counter docstring `count-c1.py:1-48`). At the freeze tip neither the section nor the registry exists (the only hits of those strings are the counter, the preregistration, and this wave's item specs). `PROVINCE.md:109-115` holds round-28 request fields for native `POST /completion` only and leaves "other endpoints" on the frontier. `PROVINCE.md` does not mention `/v1/chat/completions`, `response_format`, `logprobs`, or `server-common.cpp`.

Still open after that opening (not this round's C1):

| Item | Last stated open | Not closed by |
|---|---|---|
| `json_schema` compiled into `generation_settings.grammar` | `corpus/README.md:431-432`; parenthetical only at `SKILL.md:1212-1213` ("not representable in this table") | rounds 29-30 |
| Launch-dependent bounds under other argv (`n_parallel`) | `corpus/README.md:432-433`; measured only at default `n_parallel` 4 (`SKILL.md:1141`, F28-06 at `:1171`, bounds 1 to 4) | rounds 29-30 |
| Other endpoints, other builds, other engines | `corpus/README.md:432-433`; `PROVINCE.md:115` | rounds 29-30 |
| K05 beyond the lane fixture (registered consumers, large models, fit vs free memory) | `corpus/README.md:397-399`, `:462-463`; `PROVINCE.md:105`, `:125-126`; `SCORECARD.md:1567-1568` | round 25 advanced the fixture only |
| Registered-consumer reconciliation (the three rows stay `DEAD`) | `corpus/README.md:434`; `PROVINCE.md:17-29`, `:125` | no later round resampled them |
| Router-mode model errors (need a router launch; counter argv always passes `-m`) | `corpus/README.md:407-408`, `:419-420`; `corpus/lessons/round-26.md:71` | rounds 27-30 |
| Held-back round-26 signatures that are not the chat-adapter parameter table: empty input / documents / prompt, missing completion id, unknown control, decision-model, encoding-format, missing-query (`corpus/lessons/round-26.md:69`) | `corpus/README.md:407-409` | round 27 C1 withdrawn before data (`corpus/QUALITY.md:276`) |
| `--embeddings` SIGSEGV on `POST /completion`, seen once, not re-run | `SKILL.md:1129-1133`; `corpus/README.md:409-410` | rounds 27-30 |
| Self-assessment extractor still finds 69 of 141 by itself; a statement outside both populations is invisible | `corpus/README.md:461-462`; `SCORECARD.md:1567-1569` | calibration ground (C2's neighborhood), not the depth item C1 opens |

Last stated open at `corpus/README.md:386-389` (round-24 continuation) and not named again as closed or open after round 25: external-system-library identity, receipt-header minimization, historical crash-as-kill leaves. Git `>=2.45` stays an operator disposition (`corpus/README.md:382-383`). Do not treat that silence as either a close or this round's work.

## (b) Overlap — path string vs held chat-adapter outcomes

Inventory: every `*.md`, `*.json`, `*.tsv`, `*.py`, `*.sh` under the lane except `.git`. Durable files (not under `.ufo/`): 21 files, every matching line listed below. Under `.ufo/`: 433 files, 2960 matching lines, mostly vendored `server-common.cpp` copies and historical probe JSON that echo a consumer URL. Those 433 are not a second parameter table. The wave documents that actually describe the chat parser are listed after the durable table.

No durable file contains `## Round-31 chat-completions parameter outcomes` or `chat-param-outcomes-r31`. `SHONEN.md`: no hits. `PROVINCE.md`: no hits.

### Durable hits

`/v1/chat/completions` — identity, foreign-service, or one error trigger. Not a parameter-outcome table.

| File | Lines | What the hit is |
|---|---|---|
| `LOG.md` | 59 | round-1 fact: POST returns 200 for any model name |
| `SCORECARD.md` | 1440 | planned round-29 candidate, explicitly not done |
| `SKILL.md` | 160, 175 | bogus-model 200; Jetty 404 on `:8080` |
| `SKILL.md` | 1114 | E26-13 trigger path (audio content part), one signature |
| `corpus/README.md` | 431 | names the chat endpoint as still open |
| `corpus/knowledge/consumer-registry.md` | 40, 106, 108, 109, 117, 124, 125, 127, 164, 251, 252 | historical pins and the "round-trip is not identity" note |
| `corpus/knowledge/listener-census.md` | 115, 117, 175, 178, 199, 270, 277 | same census |
| `corpus/lessons/round-1.md` | 12, 15 | identity corollary |
| `corpus/lessons/round-1-critic.md` | 127, 128, 146, 166 | Jetty 404 capture |
| `corpus/lessons/round-1-safety.md` | 44, 48 | do not POST chat to probe a foreign service |
| `registry/endpoint-consumers.tsv` | 36 | `ufo-fsd-thetick` declared URL, currently DEAD |
| `registry/error-signatures-r26.json` | 329 | E26-13 request path |
| `tools/echo-recheck.py` | 12, 125, 393 | replays the round-27 echo probe, which used this path |

`response_format` — one already-held error string (S137), used as an echo-discrimination method, not as a chat-parameter outcome row (text / json_object / json_schema to slot or grammar).

| File | Lines |
|---|---|
| `corpus/SOURCES.md` | 149 (S137: how b11755 builds the type-error from the parsed value) |
| `corpus/knowledge/echo-discriminating-counters.md` | 1, 33, 51 |
| `corpus/lessons/round-26-verifier-spotcheck.md` | 107, 115 |
| `corpus/lessons/round-27.md` | 90, 108 |
| `corpus/lessons/round-27-verifier-spotcheck.md` | 114 |
| `tools/echo-recheck.py` | 89, 90, 91, 92, 93 |

`logprobs` — the `/completion` schema alias of `n_probs`, not the chat response contract (`has_logprobs` / `top_logprobs`).

| File | Lines |
|---|---|
| `corpus/SOURCES.md` | 177 (S165 quote: `add_alias("logprobs")`) |
| `corpus/lessons/round-28.md` | 109 (same quote) |

`SKILL.md` F28-26 (`:1191`) is the counted `n_probs` truncation row and does not contain the string `logprobs`.

`server-common.cpp` — cited lines are error-signature or echo sites, plus the round-26 hold-back. None is a chat-parameter outcome table.

| File | Lines | Site |
|---|---|---|
| `LOG.md` | 1773 | S137 echo |
| `SKILL.md` | 1112 | LoRA body not validated (`:280-291`) |
| `SKILL.md` | 1114 | E26-13 audio (`:1270-1273`, `:107-109`) |
| `SKILL.md` | 1115 | E26-14 prompt elements (`:1088-1115`), native `/completion` |
| `corpus/QUALITY.md` | 219 | KQ37 cites `:1375` |
| `corpus/README.md` | 416 | round-27 echo method, not a new signature |
| `corpus/SOURCES.md` | 138 (S126 `:1272`), 139 (S127 `:1114`), 149 (S137 `:1375`), 212, 248 | source rows and the round-16 lead |
| `corpus/knowledge/echo-discriminating-counters.md` | 1, 50, 56, 64 | S137 plus media-path throws `:1216,1221,1234` |
| `corpus/lessons/round-16-verifier-spotcheck.md` | 132 | `ERROR_TYPE_UNAVAILABLE` `:119-122` |
| `corpus/lessons/round-26.md` | 43, 44 | S126, S127 |
| `corpus/lessons/round-26.md` | 70 | the re-score risk (below) |
| `corpus/lessons/round-26.md` | 79 | shortcut via `:1375` |
| `corpus/lessons/round-26-verifier-spotcheck.md` | 108, 190, 195 | S137 echo; S127; error-type labels `:95-101` |
| `corpus/lessons/round-27.md` | 108 | S137 quote |
| `corpus/lessons/round-27-verifier-spotcheck.md` | 112, 199 | S137 re-fetch |
| `registry/error-signatures-r26.json` | 352, 378 | S126, S127 file cells |

### What would make C1 re-scoring

The registered surface is new: round-28's table is native `POST /completion` (`SKILL.md:1135-1142`). Identity-URL hits do not score a parameter outcome. S137 / `response_format` and S165 / `logprobs` are adjacent facts, not the four-way outcome (reject / slot / ignored / response) the frozen counter counts.

The real overlap is unregistered wave evidence of the same parser:

- `oaicompat_chat_params_parse` is `server-common.cpp:1327` in the round-31 pin (comment `:1326`, "used by /chat/completions endpoint"). `response_format` handling is `:1363-1376`. No file under `SKILL.md`, `SCORECARD.md`, `PROVINCE.md`, `SHONEN.md`, `corpus/`, or `registry/` names that function. The preregistration sentence "at base no lane file names server-common.cpp's chat parser" is true for those trees and false for `.ufo/` wave files. Named in, at least: `.ufo/waves/round-26/w1-build/out/ScribeSourcesRequest/rows.md:13-16`, `.ufo/waves/round-26/w2-falsify/advice/AttackE2613.md:87,145`, `.ufo/waves/round-27/w1a3/advice/ExecLiveEchoProbe.md:41`, `ScoutEchoSitesSnapshot.md:7,18`, `ScoutReopenS137.md:22`, `CriticEntryFactsSources.md:24`.
- `corpus/lessons/round-26.md:70`: 17 chat-completions request-validation messages, `server-common.cpp` lines 1302-1521, live twice each, scratch counter `registered 17 counted 17 target 12 met True`, returned after integration. Seat record: `.ufo/waves/round-26/w1-build/advice/ExecChatFormat.md:1-9` and `out/ExecChatFormat/`. Round 27's control `KamaR27CtlLabelKeyed` then met a signature counter from the base tree by copying those rows (`.ufo/waves/round-27/preregistration.json` field `pre_data_amendment_A2`; `controls/KamaR27CtlLabelKeyed/REPORT.md:26-30,78-82`). Round-27 C1 was withdrawn before data (`corpus/QUALITY.md:276`).
- A C1 reject row whose message is one of those 17, cited to the same lines, is a new table shape over already-measured faults, not new ground. A C1 slot / ignored / response row (mapping onto generation settings, an OAI name absent from `server-schema.cpp`, or `n_choices` / `has_logprobs` / `sse` / `sse_usage`) is not in any held table. KQ38 (`corpus/QUALITY.md:283`) still applies: a reject whose text is only the schema bounds sentence must not be counted; the frozen counter already requires adapter-authored messages to occur verbatim in the pinned `server-common.cpp` (`count-c1.py:40-48`).

`.ufo/` hit mass that is not this overlap: round-27 190 files, round-26 103, round-16 42, round-31 32 (this wave's own pins and items), round-28 24, plus smaller probe JSON under rounds 5, 10, 11, 17, 18, 20, 21, 25, 29. Round-11 `advice/SourceCompatibility.md:73-84` says Ollama's documented compat surface does not support `logprobs`; that is another engine's docs, not b11755 chat outcomes.

## (c) Three cheapest next depth moves, after this round

Each stays unmoved if the named observable is still true at the next tip. None is absorbed by C1: the frozen live argv is the default `-m --host --port` (`count-c1.py:25`), the outcome cell cannot hold raw GBNF, and the section heading is chat-completions only.

1. **json_schema to grammar.** One live `/completion` (or chat) request whose stored `generation_settings.grammar` is pinned to a quoted GBNF fragment and a source line for the compiler. Unmoved while `SKILL.md:1212-1213` is still the only statement and still says the grammar is "not representable in this table", and no registry row's outcome contains a `grammar` value.

2. **n_parallel moves n_cmpl's upper bound.** One second launch with an explicit `--parallel` other than 4, same field, same fixture. Unmoved while F28-06's only counted outcome is still `reject 400, bounds 1 to 4` (`SKILL.md:1171`) and no receipt records a different upper bound under a different argv.

3. **/v1/completions adapter, not native /completion and not chat.** `oaicompat_completion_params_parse` is the sibling parser at pinned `server-common.cpp:1139`. One table of what that parser rejects, maps, or ignores, on the same fixture. Unmoved while every counted parameter table is still either round-28 native `POST /completion` (`SKILL.md:1141-1142`) or round-31 `/v1/chat/completions`, and no SKILL section cites line 1139.

Do not spend the next depth round re-registering the 17 held-back chat validation strings; that shortcut already met a counter from the base tree (section b).

## Do not trust

- The preregistration's "no lane file names the chat parser." Wave advice names `oaicompat_chat_params_parse`. Held docs do not.
- Any C1 reject row that restates `corpus/lessons/round-26.md:70` / ExecChatFormat as if those faults had never been measured.
- URL hits in the consumer registry as evidence the chat-parameter surface was already held.
- Round-24 audit frontier rows as either closed or assigned to this round.
- This scout did not run the frozen counter and did not start a server.
