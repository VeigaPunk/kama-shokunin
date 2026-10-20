# ScribeReadmeFrontier — round-16 README coverage rows and frontier disposition (revision 3)

Access date for every source: 2026-10-20. Draft: `.ufo/waves/round-16/build/drafts/readme-frontier.md`.

## Revisions applied (cumulative)

1. **No transient status.** Outcome-style prose plus an explicit admission gate; no "not yet on disk" narration.
2. **Revision skew resolved.** c0fd7862 carries the loading middleware (`server-http.cpp:308-320`); single-model `update_meta` precedes `is_ready` at both pins (`server.cpp:495-496` at c0fd7862; `:514-515` at b11755). The null-`meta`-while-loading sentence is not observable through single-model `/v1/models` and is not cited as a loading fact.
3. **Fixture limit stated.** The ephemeral fixture cannot evidence registered-consumer health or served-model identity (served id = caller `--alias`; no digest).
4. **Predictions kept as `[INFERENCE]`.** Sleeping and router verdicts are predictions the C2 probe cannot measure, since it runs only after `/health` 200 (reviewer-relayed).
5. **Coverage rows gated by the preamble, not by Entry-cell text.** The gating parenthetical is removed from both Entry cells (reviewer nit 1); the preamble states that omitted files drop their row.
6. **Vocabulary anchor widened.** The six-verdict list in `SKILL.md` spans `:11-13` (verified by reading lines 11-14: "`MODEL_OK` | `MODEL_MISMATCH` | `FOREIGN_SERVICE` |" / "`UNAUTHORIZED_SERVICE` | `DEAD` | `NOT_HTTP`"); the draft and sources table now cite `:11-13` (reviewer nit 2).

## Verified this session

- c0fd7862 full hash `c0fd78626405c6d9b934efef0ec7291fcc20e3d6` (reviewer-supplied; raw fetch succeeded). `server-http.cpp:308,314,318` and `server.cpp:495-496` read directly.
- b11755 `server.cpp:514-515` read directly.
- `tools/kama-probe.sh` sha256 `d0d48d8d6a5d96553adb773ae7f75d4d0f47e19be6b2d7d8a1c9b7a83f6db8fe`; predicate `:426-445` (checks only `error.message`, `error.type`, integer `error.code`); branch `:501-506`. Read directly.
- `registry/endpoint-consumers.tsv:32` and `SKILL.md:11-13` enumerate six verdicts without `MODEL_LOADING`.
- Target files `corpus/knowledge/llamacpp-loading-lifecycle.md` and `corpus/lessons/round-16.md` do not exist at this check.

## Findings for L1

- Paste the draft's outcome prose only after its admission gate is met; otherwise append one not-admitted statement naming the blocking gate.
- Not admitted by this seat: any claim that the probe change is green, that the C2 receipt exists, or that sleeping or router verdicts are measured.
- Verdict-vocabulary parity across the TSV, SKILL, endpoint-identity and consumer-registry is an open named item; no owner is assigned by this seat.

## Limits

- No lane gate, harness, probe or test was run.
- Pinned-source line numbers come from `grep -n` / `awk NR` on fetched bytes; the unresolved `server-http.cpp` count discrepancy (940 vs 946) remains.
- The L1 smoke observation is planner-supplied and unverified here.
- Consumer live state on 2026-10-20 is unknown to this draft; the 2026-10-14 census is the last recorded state.
- The c0fd7862 short SHA could not be resolved through the GitHub API (rate-limited); the reviewer's full hash was used and confirmed by a raw fetch.

## Installs and writes

- Installs or updates: none. Tools used: `curl`, `grep`, `awk`, `sha256sum`, `python3`, `ls`.
- Files written: the owned draft (edited) and this report (rewritten). Scratch fetches in `/tmp` were removed.
- Not written: corpus, tools, tests, registry, SOURCES, lessons, knowledge, MANIFEST, `.ufo/state`, or any sibling lane.
