# Proposal: `corpus/knowledge/served-model-id-resolution.md` line 46 (U9Cannot, round 44)

Target file at lane commit 77d1bbf55c62: 46 lines; the dangling pointer is the last line (46), inside the
paragraph on lines 39-46 under `### A related gap this round could not close` (line 37).

## Where `CANNOT-ANSWER.md` was meant to point

`/home/vgpnk/Projects/shokuknow/lanes/kama/round2/CANNOT-ANSWER.md`, item "## 1. The 503-on-`/health`
versus 503-on-admission-rejection distinction has no proposed row" (lines 5-14). The paragraph at lines
39-46 is that item restated; its first sentences match line for line ("returns `Response(status_code=503)` when
the engine raises `EngineDeadError`, while the wave-1 engine-arguments row records that the chat route
returns 503 as a deliberate admission rejection. The lane holds the handler as S004, whose anchor is the same
source block, so no new row was opened"). It is a shokuknow campaign artifact, not a lane file. The lane
never contained a file of that name (see the report), so the line was never resolvable from inside the lane.

## Proposed replacement (primary: pointer to existing lane files, claim restated, stale "gap" closed)

Replace lines 37-46 (heading + paragraph) with:

```
### A related distinction held elsewhere in the lane

This guide's vLLM `/health` source (S004, held in `runtime-health-surface-matrix.md`) records that the
handler returns 503 when the engine raises `EngineDeadError`. A different vLLM surface returns the same
status for a different condition: the engine-arguments page (S327, v0.32.0, `--max-num-queued-reqs`) says
that when the queue limit is reached new requests are rejected with HTTP 503 so the client can retry on
another instance. The same status code therefore means "engine dead" on one surface and "deliberate
admission rejection" on another, which is the distinction the lane's "an error is not a verdict"
discipline needs. That distinction is held in `endpoint-health-probe-conventions.md`; this guide does not
add to it.
```

Why this wording:
- `endpoint-health-probe-conventions.md` (source S327) and `runtime-health-surface-matrix.md` (S004) both exist
  in `corpus/knowledge/`; S327 is a `mined` row in `corpus/SOURCES.md:213` whose `corpus/knowledge` target is
  that entry. The gap the old paragraph called "not closed" was closed by that entry, so keeping "could not
  close" and "no new row was opened" is stale as well as dangling.
- The old text says the chat route (`/v1/chat/completions`) returns the 503, and calls S004's anchor "the same
  source block" as the engine-args row. Neither holds against the lane's own rows: S327 states the 503 for
  rejected requests when the queue limit is reached and does not name a route, and S004 (stable instrumentator
  health page) is a different page from S327 (v0.32.0 engine args). The proposal drops both claims.
- "wave-1 vLLM engine-arguments row" (line 40) is a second dangling reference (to a shokuknow round-1 proposal);
  the proposal replaces it with S327.

## Alternative (minimal: only remove the dangling pointer, keep the paragraph's other claims)

Replace lines 44-46 (`already holds that handler as S004 ... CANNOT-ANSWER.md for the next wave that touches that file.`) with:

```
already holds that handler as S004, so no new row was opened for it in this round. The admission-rejection
503 is held as S327 in `endpoint-health-probe-conventions.md`.
```

This leaves line 40 ("the wave-1 vLLM engine-arguments row") and the "same source block" and route claims unrepaired; use the
primary proposal if the held-sentence review is in scope.

## Caveats

- The held-entry review in `corpus/lessons/round-43.md:113` also lists lines 39-45 of this file among eight sentences that
  need a process qualification. This proposal does not address that qualification.
- Nothing was edited in the lane; this file is the only deliverable besides the report.
