# Round 71 source readings and novelty, 2026-11-03

## Exact source boundary

Official llama.cpp sources were read fresh at immutable commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad. WHATWG HTML SSE §§9.2.5–9.2.6 were read at their official living URL (page displayed Last Updated 30 October 2026). Only metadata and short quotations are retained. The recheck script fetches into memory, locates anchors, and hashes the response. Source excerpts are not runtime observations.

## Own notes

- server-context.cpp:5071–5084 emits the terminal marker when its response reader is exhausted for the compatible completion stream. Lines5113–5118 instead terminate after formatting an error. Consequently, transport closure alone is not evidence of successful completion. This reading covers that pinned implementation, not all providers.
- server-task.cpp:453–505 gives the final chat choice a finish reason of length, stop, or tool_calls and can append a usage chunk with no choices. These distinguish task terminal metadata from the transport marker. The proposed tool deliberately uses a minimal owned projection, not a complete API response validator.
- WHATWG SSE parsing: CR, LF and CRLF delimit lines. Only a blank line dispatches an event. Data fields combine with newlines; field spelling is exact, with only one optional space removed after the first colon. Comments and unknown fields do not supply data. An initial BOM is stripped. Pending EOF data is discarded by a browser; our analyzer records its existence as incomplete evidence. Strict Unicode/JSON refusal is our offline policy, not a browser decoder claim.

## Comparison, without rewriting history

The historical round31 detector (`.ufo/waves/round-31/count-c1.py`:547–560) detects SSE presence using lines and parseable JSON plus a marker. Its narrower presence objective remains historical. The new completion-evidence task needs dispatched event boundaries, finish state, explicit errors and trailing incomplete evidence. Round63 explicitly excluded SSE from its non-streaming observations (`corpus/knowledge/completion-request-plane.md`:66). Round70 concerns advertised identity and does not classify stream evidence. No endpoint, provider, runtime, weights, readiness, process ownership or model-quality claim follows here.

## Retained source-check error

The first recheck expected the error termination comment at line5117; the fetched file located it at5118. `source-recheck-first.json` and `recheck-sources-first.py` preserve that failed anchor. The corrected script uses5118 and independently reopens sources; it does not rewrite the first receipt. This is an author provenance error, not a candidate test failure or a claimed training gain.
