# ScribeLessonGate — round 16 Gate draft report

Date: 2026-10-20. Owned output: `.ufo/waves/round-16/build/drafts/lesson-gate.md`. Advice only; L1 integrates and decides.

## Findings

1. **MODEL_LOADING exact rule: admit, scoped to b11755.** The exact body occurs once in the b11755 source at `tools/server/server-http.cpp:307-325` (literals at 318-320), gated by `is_ready` for every request via the pre-routing handler (354-355). README `GET /health` documents the same body (lines 479-490). Quotes and access dates are in the draft.
2. **Reject widening to any 503 / unavailable_error.** The same type and code come from `ERROR_TYPE_UNAVAILABLE` (`server-common.cpp:119-121`), and `?fail_on_no_slot=1` with no idle slot emits "no slot available" (`server-context.cpp:5394-5396`; README line 987). A message-exact rule is what keeps that body out of MODEL_LOADING.
3. **Reject "a live toy run proves registered consumers healthy."** The toy run exercises one ephemeral instance; README 489-490 ties 200 to that server only. Consumer ports are not measured.
4. **Admit live capability, scoped.** README supports the default host, port, `--metrics` and `--slots` facts (lines 193, 194, 225, 227). The 501 `/metrics` body, `owned_by` value and `models[]` shape are L1 observations; not sourced here.
5. **S021: partial flip.** The registry URL `https://llm-d.ai/docs/operations/readiness-probes` returned HTTP 404 on fetch today. Current pages (`/docs/operations/lifecycle/readiness-probes` v1.0; `/docs/0.10/operations/readiness-probes`) carry the same statements, which describe **vLLM**. Recommended: queued → mined with vLLM-only scope and URL repair; S021 does not support any llama.cpp MODEL_LOADING claim. The round-10 lesson still links the 404 URL.

## Sources opened (2026-10-20)

- `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76/tools/server/server-http.cpp` (SHA-256 `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb`)
- `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76/tools/server/README.md` (SHA-256 `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37`)
- `tools/server/server.cpp`, `server-context.cpp`, `server-common.cpp` at 704366d76 (fetched; SHA-256 prefixes recorded in the draft)
- `https://llm-d.ai/docs/operations/readiness-probes` — HTTP 404 (observed once)
- `https://llm-d.ai/docs/operations/lifecycle/readiness-probes`, `https://llm-d.ai/docs/0.10/operations/readiness-probes` — opened
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh:415-525` — read (classify)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-15.md` — format reference
- `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:33` — S021 row

## Limits and unknowns

- Pinned to b11755 only; other llama.cpp builds not checked.
- Installed binary (`~/.local/opt/llama-b11755`) commit and asset hash not verified by this scribe.
- Live smoke output is L1's; not reproduced or checked here.
- The frozen probe's `classify()` was read, not run; no lane gate, harness or test was executed.
- Only one fetch of the S021 old URL; the 404 may be transient. Unknown.

## Tool installs or updates

None. Used `curl` (already present) to fetch raw files from official GitHub raw URLs into `/tmp`; no packages installed, no pacman use.

## Out of scope / not done

- No edits to `corpus/lessons/`, `SOURCES.md`, the probe, the harness, or any other item's file.
- No lane gate, probe run, harness run or service action.
