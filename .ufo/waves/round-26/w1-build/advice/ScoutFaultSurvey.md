# ScoutFaultSurvey — C1 recon advice (llama-server b11755 fault surface)

Verdict: 8 new http-channel candidates live-confirmed on the fixture, each with
a verbatim literal in a pinned 704366d source file and a distinct trigger;
none are covered by the executor families listed in this wave.

## Candidates for registry rows (all verified)

1. signature `missing completion id` — server-context.cpp:5595 — POST
   /v1/chat/completions/control body `{}` — 400.
2. signature `unknown control action` — server-context.cpp:5599 — POST
   /v1/chat/completions/control body `{"id":"x","action":"bogus"}` — 400.
3. signature `This model is not a decision model` — server-context.cpp:5884 —
   POST /v1/systemone body `{"questions":[]}` — 501.
4. signature `Request body must be an array` — server-context.cpp:5998 — POST
   /lora-adapters body `{}` — 400.
5. signature `Pooling type 'none' is not OAI compatible. Please use a different pooling type`
   — server-context.cpp:6137 — args [`--embeddings`], POST /v1/embeddings body
   `{}` — 400.
6. signature `"input" or "content" must be provided` — server-context.cpp:6151
   — args [`--embeddings`], POST /embedding body `{}` — 400.
7. signature `The format to return the embeddings in. Can be either float or base64`
   — server-context.cpp:6161 — args [`--embeddings`], POST /embedding body
   `{"input":"x","encoding_format":"bogus"}` — 400.
8. signature `"prompt" elements must be a string, a list of tokens, a JSON object containing a prompt string, or a list of mixed strings & tokens.`
   — server-common.cpp:1114 — POST /completion body `{"prompt":42}` — 400.

## Facts backing these rows

- Server binary sha256 b6a31a8e…cd804 matches the counter pin; model sha256
  270cba1b…256d matches; all runs on 127.0.0.1, ports 47680-47683 (free before,
  closed after, one server at a time, `timeout 90` wrapper, `-t 2`).
- Every signature: >= 20 bytes, absent from base 1560e4d8 SKILL.md+corpus (git
  grep -F exit 1 for each), absent from `llama-server --help` output (grep exit
  1 for each), not present in its own request bytes, never seen in the healthy
  baseline request set.
- No substring/superstring relation among the eight; all eight triggers differ
  (clause g clean within this set).
- None require forbidden args (-m/--host/--port/--path/--log-file etc.);
  `--embeddings` is allowed (not in FORBIDDEN_ARGS).

## Source URL anchors (for SOURCES rows)

Each row names the basename in `.ufo/waves/round-26/sources/llama.cpp-704366d/`
(file sha pinned by the counter) — e.g. `server-context.cpp` lines 5595/5599/
5884/5998/6137/6151/6161, `server-common.cpp` line 1114. Sources are fresh-fetch
pinned (sha256 match set in count-c1.py SOURCE_SHA256; verified byte-identical
snapshot). Exact upstream URL: `https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5595`
(access 2026-10-23); the lane snapshot sha256 matches the counter pin for the
named file.

## Notes/risks for the integrator

- Candidates 5-7 need `--embeddings`; the fixture starts fine with it (warnings
  only). OAI path (/v1/embeddings) hits the pooling literal (5) before input
  checks, so use the legacy /embedding for 6/7.
- Candidate 8's literal ends with a period and includes leading quotes — keep
  verbatim including the trailing `.`.
- 6190 "Input content cannot be empty" was NOT confirmable (empty string
  tokenizes to BOS; returns 200). Do not register without a live repro.
- "no slot available" (5396) requires concurrent in-flight requests; unreachable
  with a one-request trigger. Skip.
- Stream endpoints live in server-stream.h (not in the pinned 13-file set) —
  their literals are not countable; skip.
- GCP /predict errors require AIP_MODE env (not expressible in registry) — skip.
- Startup-channel literals (arg.cpp) were not confirmed here; the bad-args
  family already covers that space, and A1 excludes help-text literals.

## Files written

- `.ufo/waves/round-26/w1-build/out/ScoutFaultSurvey/survey.md` (survey with
  full commands/outputs/exit codes).
- Scratch: `/fast/scratch/hyaku/kama-r26/ScoutFaultSurvey/` (run_candidates*.sh,
  live/<name>.{summary,body,server.log}).
