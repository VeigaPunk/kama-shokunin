# Offline chat-stream completion evidence
verified-at: 2026-11-03 — fresh primary-source reading and independent first-batch adjudication; .ufo/waves/round-71/result/TECHNICAL-VERDICT.md
source: SOURCES.md S544–S546; tests/round71-independent/SPEC.md
recheck: on source revision or projection-contract change; never infer current endpoint state

## What the evidence can say

A stream can contain valid-looking JSON and a marker-shaped line without showing a complete response. The practical question is whether the supplied projection contains a correctly dispatched final choice followed by a dispatched terminal marker. It is not whether a server is ready, a model is good, or any request actually happened.

The pinned llama.cpp emitter distinguishes the final chat choice, optional usage, normal stream termination, and error termination. WHATWG separates a data line from an event: the empty line is the dispatch boundary. The offline classifier combines those distinctions under its own exact, intentionally small projection grammar. It is not a complete SSE browser, HTTP client, API-schema validator or capture extractor.

## Evidence ladder

1. Validate the entire synthetic envelope, strict UTF-8/JSON and size bounds. Missing or malformed evidence is invalid, not a negative observation of a live server.
2. Parse lines using CR, LF and CRLF. Remove only one initial BOM and one optional ASCII space after a field colon. Field names are case-sensitive. Comments and unknown metadata cannot certify completion.
3. Join data fields with newlines and dispatch only on an empty terminated line. A marker in a comment, a JSON string, or an undispatched final block is not a terminal event.
4. Require a single final choice, then at most one empty-choices usage event, then a single exact DONE marker. A finish reason alone and a DONE marker alone are incomplete evidence.
5. Treat a valid error event as a separate outcome, even if a later DONE appears. Do not turn an error into success. A malformed/conflicting dispatched event anywhere is invalid; pending data at EOF is incomplete even after an otherwise complete sequence.
6. Keep readiness, weight identity, process ownership and live observation unestablished in every output. Strict UTF-8 and resource limits are offline assessment restrictions, not the browser decoder's specification.

## Decisions under the frozen projection

| Supplied evidence | Decision | Meaning |
|---|---|---|
| Valid final choice plus dispatched exact DONE, optionally usage between | COMPLETE, exit0 | The synthetic projection meets this finite completion rule |
| Missing final, missing DONE, or undispatched data tail | INCOMPLETE, exit2 | The projection cannot establish completion; not proof of server failure |
| Valid explicit error, optionally followed by DONE, no invalidity or pending data | STREAM_ERROR, exit2 | The projection records an error-shaped terminal outcome |
| Malformed JSON, wrong types/keys, duplicate terminal, conflicting order, or dispatched data after DONE | INVALID_OR_INSUFFICIENT, exit3 | Invalid projection cannot support an outcome |
| Unreadable/nonregular/symlink argument or wrong arity | Invocation failure, exit64 | No domain verdict |
| Unexpected program failure | Runtime failure, exit70 | No domain verdict |

Precedence is invalid, then pending-data incomplete, then stream error, then complete, then incomplete. This is the lane's explicitly frozen evidence policy, not an assertion about every upstream provider.

## Before using the instrument

- Supply only an explicitly authorized owned synthetic projection conforming to the frozen specification. Do not put full private captures, tokens, prompts, credentials or provider settings into this tool.
- Use the independently reviewed read-only, no-network isolation and resource envelope; Python -I alone is not isolation. The candidate reads one local regular nonsymlink input and writes stdout/stderr only.
- Read both the process exit and exact JSON status. A shared exit2 does not collapse INCOMPLETE and STREAM_ERROR.
- Do not normalize the marker with whitespace trimming or search for it as a substring. Do not stop validating when an apparent terminal marker is encountered.
- For real incident diagnosis, obtain separately authorized capture provenance and current endpoint observations. This capability neither performs those steps nor grants their authority.

## Historical comparison and limits

Round31's detector established SSE presence, not general completion. Comparing it on the new completion task demonstrates a distinction, not a retroactive failure of the old objective. Round63's non-streaming evidence and round70's advertised identity remain unchanged. The projection omits token contents, request identity, transport status, headers, timing, capture provenance and multiple choices; nothing is claimed for those excluded surfaces. Finite fixture success is not universal protocol correctness.

## Demonstrated bounded result

The first independently adjudicated batch matches all 83 frozen semantic cases, five invocation refusals, ten source-mutant challenges with ten benign controls, sixteen scope-field controls and eight historical-presence comparisons. Raw first outputs and independent READBACK-FIRST.json are retained in `.ufo/waves/round-71/result/`. No batch was repeated and no candidate repair occurred. This finite evidence supports the declared projection capability, not excluded real-serving claims.
