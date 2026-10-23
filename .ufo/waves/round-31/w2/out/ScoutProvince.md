# ScoutProvince — knowledge entry vs PROVINCE.md

Axes: claim coverage, quote fidelity, sibling-surface naming (kumitate / mado / kake), receipt integrity.

```RESULTS
sha256sum PROVINCE.md corpus/knowledge/chat-adapter-outcomes.md SKILL.md
EXIT 0
TAIL:
25a440e0fc31ede4d82913d2b7aabded500eb3b25dfe82f06d278893e7406574  PROVINCE.md
b9b31be85e897a4d2216665c1234afe260dc720690706146b2082062cd65abe3  corpus/knowledge/chat-adapter-outcomes.md
11041e2548e151f34ff65a26dece1835f0864df293cb4721efc6ee4f5b12aaaa  SKILL.md

wc -l PROVINCE.md corpus/knowledge/chat-adapter-outcomes.md SKILL.md
EXIT 0
TAIL:
  142 PROVINCE.md
   65 corpus/knowledge/chat-adapter-outcomes.md
 1292 SKILL.md
 1499 total

nl -ba corpus/knowledge/chat-adapter-outcomes.md
EXIT 0
TAIL:
    59	- The counter's normalization (`top_keys`, `n_choices`, `choice_keys`,
    60	  `has_logprobs`, `usage_keys`, `prompt_tokens`) cannot see effects outside
    61	  those fields; the round-31 falsify wave demonstrated two ways a row can be
    62	  counted while proving nothing (a mapping whose stored value equals the base's,
    63	  and an `ignored` claim on a field the session layer consumes). Those are
    64	  counter defects recorded in `corpus/lessons/round-31.md`, not evidence for the
    65	  rows involved.

rg -n 'kumitate|mado|kake|kengaku|sibling|cross-lane|SDK|provider policy' corpus/knowledge/chat-adapter-outcomes.md
EXIT 1
TAIL:
(empty stdout; ripgrep exit 1 = no match)

rg -n 'kumitate|mado|kake|kengaku' PROVINCE.md
EXIT 0
TAIL:
40:**Refuses:** model quality/eval (kengaku), credential material & auth flows (kagi),
41:dispatch/route mechanism (kumitate), remote web surfaces (kake). Boundary rule: kama
123:(kumitate's counter rerun, mori's network re-fetch of source rows), any claim
140:frontier. Sibling lanes hold no competing claim on this surface: kumitate's
141:watcher posts to `/v1/chat/completions` as a consumer and kengaku excludes the

nl -ba PROVINCE.md
EXIT 0
TAIL:
140| frontier. Sibling lanes hold no competing claim on this surface: kumitate's
141| watcher posts to `/v1/chat/completions` as a consumer and kengaku excludes the
142| model-serving plane (`.ufo/waves/round-31/w1/out/ConnSibling/overlap.md`).

sed -n '1232,1278p' SKILL.md
EXIT 0
TAIL:
## Client-facing rules

1. For a request matching a `reject` row, present the recorded status and error as an API/request error, not as generated text or a model refusal (`count-c1.py` docstring L24-L29; `server-common.cpp` L91-L132, L1326-L1347, L1357-L1375).
2. Treat a `slot` row as evidence of the server-stored setting only; if the generation effect matters, verify that behavior separately rather than promising it from `/slots` (`count-c1.py` docstring L30-L31; `server-common.cpp` L1496-L1510, L1534-L1543).
3. Do not rely on an `ignored` result beyond its measured request/profile, and treat `n_choices` only as the number of choices to inspect—not a quality score (`count-c1.py` docstring L24-L26, L32-L39, L56-L57; `preregistration.json` L21-L26; `server-common.cpp` L1524-L1541).

sed -n '1,6p;41p' ../kake-shokunin/PROVINCE.md
EXIT 0
TAIL:
- `kama` owns local model-serving endpoints; kake owns remote web properties.

sed -n '1,6p;24,27p' ../kumitate-shokunin/PROVINCE.md
EXIT 0
TAIL:
- Local model serving and endpoints → kama. Prompt and skill craft → kotoba. Research method → chousa.

sed -n '1,16p' ../mado-shokunin/PROVINCE.md
EXIT 0
TAIL:
**Refuses:** secrets in configs (shape-only, → kagi), model endpoints
(→ kama), model quality (→ kengaku). Never mutates a running compositor
state; every claim is file-byte- or screenshot-verified.

rg -n '^#+' corpus/knowledge/chat-adapter-outcomes.md
EXIT 0
TAIL:
1:# The chat-completions adapter: what it maps, refuses, and drops
20:## What the layer does
52:## Limits
```

Receipts: `.ufo/waves/round-31/w2/out/ScoutProvince/` (`01-sha256.txt` through `07-entry-headings.txt`, `skill-r31.txt`, `kake-head.txt`, `kumitate-head.txt`, `mado-head.txt`, `command-log.txt`). Paths above are relative to `kama-shokunin` except the three sibling `sed` targets.

No tool was installed or updated.

LSP: `xd://lsp` is not mounted (`No such tool: xd://lsp. Mounted devices: ast_edit, debug.`). This item is prose classification, not an exported code symbol. Grep/read is the fallback, not a definition/reference proof.

FINDING: Adjacency is not falsified. All 16 claims in `corpus/knowledge/chat-adapter-outcomes.md` stay inside local model serving on the lane-owned chat adapter (PROVINCE.md:129-138). None are client-SDK behaviour, model quality, or provider policy. The entry has no cross-lane boundary paragraph (headings are only the title, `## What the layer does`, and `## Limits`; lane-name scan exit 1). It names neither kumitate, mado, nor kake, and it does not enter those lanes' owned surfaces.

## Classification

`entry-line | province verdict | province line`

1. L3 `source: S180-S191 (llama.cpp b11755 tools/server/server-common.cpp and server-schema.cpp @ 704366d76)` | in-province | PROVINCE.md:129-136 `the /v1/chat/completions conversion layer` … `enters held ground` … `(S180-S192, llama.cpp b11755 @ 704366d)`
2. L4 `verified-at: … lane fixture (llama-server b6a31a8e…d804, stories260K.gguf 270cba1b…256d, default argv, n_slots 4), live rows in registry/chat-param-outcomes-r31.json` | in-province | PROVINCE.md:136-137 `It is the chat adapter on the lane-owned fixture` and :135 names that registry
3. L5 `recheck: on release (a new llama.cpp build; the pinned lines are the recheck anchor)` | in-province | PROVINCE.md:139 `other builds and engines … remain frontier` — the line is a recheck trigger, not a claim that another build matches
4. L7-L9 `POST /v1/chat/completions is a conversion layer over the same task parameters the native /completion endpoint uses, so the question a client faces is not "which fields exist" but "what did the adapter do with the field I sent"` | in-province | PROVINCE.md:129-130 `conversion layer` / `OpenAI-compatible chat endpoint's parameter handling`. "Client" here is the caller of this adapter, not an SDK
5. L10-L11 `four answerable forms on this fixture, each measured once per parameter and re-derived by count-c1.py` | in-province | PROVINCE.md:134-135 the SKILL section, the registry, and this knowledge file are the held record
6. L15 `reject | the request is refused before inference | HTTP status plus an error object with exactly code, message, type` | in-province | PROVINCE.md:131 `the adapter's own validation messages and their 400/500 mapping`
7. L16 `slot | the value reaches the stored task parameters, sometimes under another key | the newest /slots entry's params` | in-province | PROVINCE.md:113-114 `what the server accepts and stores for one request` and :133 `the /slots observability boundary`
8. L17 `ignored | no observable change | zero delta on the full params object and an unchanged normalized response` | in-province | PROVINCE.md:132-133 `undeclared OpenAI-standard keys copied then pruned`
9. L18 `response | the OpenAI-compatible response contract changes | choices length, logprobs presence, SSE framing, SSE usage frame` | in-province | PROVINCE.md:130 `OpenAI-compatible chat endpoint's parameter handling` on the fixture. Not a provider-policy claim
10. L22-L28 aliases: `max_tokens` alias of `n_predict`, `n` fallback alias, both stored keys, `max_completion_tokens` via the property copy, `Treat the two stored keys as one budget, not two` | in-province | PROVINCE.md:130 `alias resolution through the pinned schema` and :113-114 stored request fields, `not sampling quality`
11. L29-L32 `logprobs is a mapping, not a boolean effect` … `sets n_probs to top_logprobs or 20` … `top_logprobs alone is refused` | in-province | PROVINCE.md:132 ``logprobs` → `n_probs``
12. L33-L41 adapter validation (`messages`, `content`, `tool_calls`, `response_format.type`, `json_schema`+`grammar` → 500 `server_error` not 400; read message and type, never status alone) | in-province | PROVINCE.md:131 `validation messages and their 400/500 mapping`. Not "is the request safe" (PROVINCE.md:42-43)
13. L42-L50 `Undeclared OpenAI-standard keys are copied and then pruned`; `user`, `parallel_tool_calls`, `tools` no stored or response change; `stream` and `stream_options` change the response contract; schema absence does not prove "no generation effect" | in-province | PROVINCE.md:132-133 the copy-then-prune sentence, and :137 `not model quality`
14. L54-L55 `One request per parameter on one build, model and argv: a row is one observed point, not the parameter's response function` | in-province | PROVINCE.md:136-139 fixture-only; other builds remain frontier
15. L56-L58 `not proof the sampler used it`; a chat-session grammar never appears in `/slots`; no slot delta does not exclude a template or grammar effect | in-province | PROVINCE.md:137-138 `not model quality, and not the session-level grammar transform (which /slots does not expose)`. The sentence names the exclusion; it does not describe the transform
16. L59-L65 counter normalization cannot see effects outside its fields; two counted-but-empty patterns are counter defects in `corpus/lessons/round-31.md`, not evidence for the rows | in-province | PROVINCE.md:134 the held registry/counter record, and :138 the session layer stays outside held ground. "A field the session layer consumes" points at that exclusion

SKILL.md:1273-1277 `## Client-facing rules` (and table rows that say "clients must") were read and are not claims of this entry. They tell a caller how to read this server's status, `/slots`, and `n_choices`. They are not a client SDK.

## Cross-lane paragraph

The entry does not have one. It therefore does not name kumitate, mado, or kake.

Owned surfaces, from those lanes' PROVINCE files:

- kumitate — orchestration and tooling (OMP task/hub, ufo-fsd scripts and runtime). Its adjacent line hands `Local model serving and endpoints → kama`. The entry describes the server adapter, not dispatch or route mechanism (kama PROVINCE.md:41 refuses that). Not entered. Not named. The consumer adjacency is only in kama PROVINCE.md:140-142: kumitate's watcher posts to `/v1/chat/completions` as a consumer. That sentence is not in the entry.
- mado — desktop and compositor (Hyprland/waybar/walker). It refuses model endpoints and sends them to kama. The entry has no display or compositor claim. Not entered. Not named.
- kake — web properties and publishing (ds4cc.com, kimi.page/pro, Pages). Its adjacent line: `kama owns local model-serving endpoints; kake owns remote web properties`. The entry's "OpenAI-compatible" / "OpenAI-standard" wording is the local fixture's field handling, which kama PROVINCE.md:130-133 already holds. Not a remote web property and not provider policy. Not entered. Not named.

PROVINCE.md:140-142 names kumitate and kengaku only. It does not name mado or kake. That paragraph is province text, not the knowledge entry.

LIMITS: This is a read of the entry, PROVINCE.md, the round-31 SKILL section (SKILL.md:1232-1278), and the three sibling province openings. It does not re-run `count-c1.py`, does not open the pinned `server-common.cpp` / `server-schema.cpp` lines, and does not show that any live row is true. It does not show the entry is the only round-31 knowledge file. PROVINCE.md:136 says `S180-S192`; the entry's line 3 says `S180-S191`. A search of `corpus/SOURCES.md` for `S192|S191` showed the S191 row and the prose span `S180–S191`, and no S192 hit in that result — unresolved whether PROVINCE.md:136 over-counts, not a domain crossing. PROVINCE.md:51-53 says out-of-province findings are named for the owning lane; this entry states no such finding, so the missing sibling paragraph is a citation gap against PROVINCE.md:140-142, not evidence the entry left the domain. Exit 1 on the lane-name `rg` is no-match, not a failed read. No host server was started.
