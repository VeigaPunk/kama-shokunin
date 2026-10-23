Draft candidate rows prepared; none is live-confirmed or counted.

## Behavior

Created 11 table-row candidates for the requested families in `rows.md`, IDs `E26-F01` through `E26-F11`. Each source cell is the requested `S1xx` placeholder. Each signature is marked as a candidate for replacement by the executor-confirmed string. The candidates are source literals or contiguous source-literal fragments; formatted runtime values are explicitly noted for infill, context-size, and startup chat-template cases.

## Findings

- House-style references read: `SKILL.md:167-192` (Historical error signatures) and `SKILL.md:677-690` (Round-25 decision rows).
- Feature predicates and candidate strings read in the pinned snapshot:
  - Metrics: `server-context.cpp:5301-5305`; route `server.cpp:280`; flag `arg.cpp:3632-3638`.
  - Slots: `server-context.cpp:5363-5368`; route `server.cpp:318-319`; flags `arg.cpp:3646-3653`.
  - Slot actions: `server-context.cpp:5405-5436`; route `server.cpp:317-319`; flag `arg.cpp:3654-3662`.
  - Props: `server-context.cpp:5450-5459`; route `server.cpp:281-282`; flag `arg.cpp:3640-3645`.
  - Embeddings: `server-context.cpp:6129-6153`; route `server.cpp:297-300`; flags `arg.cpp:3517-3523`.
  - Reranking: `server-context.cpp:5800-5833`; routes `server.cpp:300-303`; flag `arg.cpp:3524-3531`.
  - Infill: `server-context.cpp:5462-5538`; route `server.cpp:296`.
  - Context size: `server-context.cpp:3653-3693`; `arg.cpp:1642-1650`; response type mapping `server-common.cpp:123-126`.
  - Chat-template startup validation: `arg.cpp:956-961, 3711-3718, 3791-3801`.
  - LoRA request body: `server-context.cpp:5994-6026`; route `server.cpp:314-316`; parser `server-common.cpp:280-290`.
  - Audio transcription: `server-context.cpp:5651-5681`; routes `server.cpp:293-294`.
- Shared response-code mapping read: `server-common.cpp:91-126`. The `ERROR_TYPE_NOT_SUPPORTED` cases map to 501 (`:115-117`), invalid request to 400 (`:95-98`), and context-size errors to 400 (`:123-126`).
- The preregistration states that A1 excludes signatures found in `llama-server --help` and `--version` output (`.ufo/waves/round-26/preregistration.json:30`). Candidate absence from the frozen base and help/version outputs is not established here.
- FIM-token availability, audio capability, active context size, exact fixture responses, and startup exit behavior remain executor checks; no fixture result is claimed.

## Gates and limits

- Not run: live `llama-server`, frozen counter, `--help`/`--version` capture, tests, or base-absence search. No counter result or C1 count is claimed.
- No fresh upstream fetch or local/fetched SHA-256 comparison was performed by this row-drafting seat; source references above are to the lane's pinned snapshot only.
- No changes to `SKILL.md`, `registry/error-signatures-r26.json`, `corpus/SOURCES.md`, or product code. No install/update was performed.

## Touched surfaces and artifact paths

- Wrote `.ufo/waves/round-26/w1-build/out/ScribeSkillRowsFeature/rows.md`.
- Wrote `.ufo/waves/round-26/w1-build/advice/ScribeSkillRowsFeature.md`.
- All 11 signatures remain proposals. L1 must replace or reject each based on the executor's live channel evidence and the frozen counter predicate.