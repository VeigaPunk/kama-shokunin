# ScribeKnowledgeEntry — round-16 advice (llamacpp-loading-lifecycle draft)

Access date for every upstream fact: 2026-10-20. Pinned upstream: llama.cpp commit 704366d76 (release b11755).

## Behavior

Drafted the append-ready knowledge entry `.ufo/waves/round-16/build/drafts/llamacpp-loading-lifecycle.md` (the only file written in the lane, besides this report). Its provenance trio mirrors `corpus/knowledge/ollama-evidence-replay.md` lines 1-3 (`source:`, `verified-at:`, `recheck:`). It covers the loading-to-ready lifecycle, the MODEL_LOADING verdict mapping against FOREIGN_SERVICE / DEAD / NOT_HTTP / MODEL_OK, the exact-envelope scope limits, and a "Live observation" section that lists receipt fields for L1 with no values.

## Gates

- No lane gate, harness, probe or test was run. No llama-server was started.
- `strings` was run once on the installed binary (provenance check only).
- `sha256sum` was run once on `~/.cache/kama-shokunin/models/stories260K.gguf`; it matched the contract value `270cba1b…d256d`.

## Upstream evidence (fetched read-only; line numbers from `curl` of the pinned files)

| Claim | Location | Quote (≤25 words) |
|---|---|---|
| Gate is a single atomic | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76/tools/server/server-http.h:71 | `std::atomic<bool> is_ready = false;` |
| Middleware body on not-ready | …/tools/server/server-http.cpp:314-325 | `res.status = 503;` then `{"message", "Loading model"}, {"type", "unavailable_error"}, {"code", 503}` |
| Frontend exemption | …/server-http.cpp:309-311 | "frontend asset, allow it to load and show 'loading'" |
| Rationale comment | …/server-http.cpp:312-313 | "no endpoints are allowed to be accessed when the server is not ready" |
| Order: state before API key | …/server-http.cpp:354-359 | `if (!middleware_server_state(req, res))` precedes `if (!middleware_validate_api_key(req, res))` |
| Router sets ready early | …/tools/server/server.cpp:440-460 | `if (is_router_server)` … `ctx_http.is_ready.store(true);` (line 460) |
| Single-model sets ready after load | …/server.cpp:507-515 | `ctx_server.load_model(params)` … `ctx_http.is_ready.store(true);` (line 515) |
| Health handler once ready | …/tools/server/server-context.cpp:5288-5299 | "error and loading states are handled by middleware" (comment, line 5289) |
| Documented 503 body | …/tools/server/README.md:485-487 | "the model is still being loaded" |
| Sleep does not reload on health/models | …/README.md:2341-2345 | "the following endpoints are exempt from being considered as incoming tasks" |
| Sleep serves cached models | …/server-context.cpp:5725-5730 | "this endpoint must be accessible during sleep" |
| /slots 503 is not the loading body | …/server-context.cpp:5394-5397; …/server-common.cpp:119-121 | `res->error(format_error_response("no slot available", ERROR_TYPE_UNAVAILABLE));` ; `code = 503;` |

Pinned sha256 (fetch-time): server-http.cpp `24ede172…`, server.cpp `21439622…`, server-context.cpp `dd1de0f2…`, server-common.cpp `b4f4aae7…`, README.md `714c067b…`, server-http.h `fafbdb8d…`.

Local evidence: `tools/kama-probe.sh` classify(): `/v1/models` decides the verdict (lines 418-420); the loading body currently falls to `FOREIGN_SERVICE non-2xx-non-model-http` at lines 521-522 (quote: "(non-2xx HTTP from a non-model service)").

## Findings

1. **Probe overreach is confirmed by source.** The 503 body is emitted by the middleware for every non-frontend path while `is_ready` is false (server-http.cpp:307-328). The current probe's non-2xx branch (kama-probe.sh:521-522) therefore labels a loading llama.cpp as a non-model service. Calibration claim C1 is supported.
2. **Router vs single-model.** In router mode the router's own `is_ready` is set at server.cpp:460 before any model loads, so the router process does not emit the loading body. Only single-model mode (server.cpp:515 after `load_model`) does. The MODEL_LOADING rule should be understood as applying to single-model processes. Whether a child's loading 503 is relayed by the router's proxy is **not verified** (server-models.cpp not read).
3. **Ready is monotonic.** `is_ready` is only ever set true in the fetched files. Sleep does not reset it, and sleep serves `/v1/models` from cache (server-context.cpp:5725-5730). Sleep is therefore not a source of the loading body. [INFERENCE from code paths; not run.]
4. **Auth ordering.** The state gate runs before the API-key gate, so a loading server with `--api-key` answers 503 to unauthenticated probes, not 401. The 401 verdict appears only after ready.
5. **Exact-envelope rule holds.** The only other 503 unavailable_error in the fetched tree is the `/slots?fail_on_no_slot=1` path with message "no slot available". It is not on `/v1/models`, so it cannot reach the MODEL_LOADING branch; the exact-message test keeps it FOREIGN_SERVICE, as the contract requires.
6. **Binary provenance.** `strings` on the installed binary shows the string `704366d76` seven times. This supports the commit label but does not prove the shipped middleware bytes match the fetched source.

## Contract-line check

The contract cites server-http.cpp:307-325 for the loading middleware. Verified: the lambda starts at 307 and the 503 body is at 314-325; the lambda closes at 328. The README `/health` 503 documentation is at README.md:485-487, as stated.

## Out of scope / not done

- No edits to product code, tests, probe, harness, corpus, MANIFEST, receipts, or any sibling lane. The `corpus/knowledge/` entry is not written; the draft is for L1 to integrate.
- No source registry IDs assigned (`S0xx`); L1 to assign if the corpus requires them.
- Ollama and third-party gateway error envelopes not checked.
- Router proxy relay (server-models.cpp) not read.

## Known tooling quirk for L1

The `read`/`grep` tools' line numbers on fetched artifacts did not match the upstream file lines (an artifact-header offset was observed and was inconsistent between files). All line numbers in the draft were taken from `curl`-downloaded copies in `/tmp` (`/tmp/kama-r16-*.cpp`, `/tmp/kama-r16-README.md`, `/tmp/kama-r16-server-http.h`) using `grep -n`/`read` on those local files. L1 should re-derive them the same way if the entry is re-verified.

## Installs / updates

None. No package, tool or binary was installed or updated by this seat. `curl` (already present) was used for read-only fetches.

## Artifacts

- Draft: `.ufo/waves/round-16/build/drafts/llamacpp-loading-lifecycle.md` (owned).
- This report: `.ufo/waves/round-16/build/advice/ScribeKnowledgeEntry.md`.
- Scratch copies of pinned upstream files: `/tmp/kama-r16-server-http.cpp`, `/tmp/kama-r16-server.cpp`, `/tmp/kama-r16-server-context.cpp`, `/tmp/kama-r16-server-common.cpp`, `/tmp/kama-r16-server-http.h`, `/tmp/kama-r16-README.md` (outside the lane; not product files; may be deleted by L1). A file `/tmp/kama-r16-b11755-server-http.cpp` was already present and was not created or modified by this seat.

## Checks for L1 to run

- Re-open `llamacpp-loading-lifecycle.md` and confirm the line citations against the pinned commit before integrating.
- When the C2 receipt exists, fill only the "Live observation" rows from it; leave `unrecorded` where it is silent.
- Confirm `tools/kama-probe.sh` classify() line numbers (415-525) are unchanged after C1's repair before the draft's table is merged.
