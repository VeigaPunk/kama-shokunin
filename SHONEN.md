# kama-shokunin — Promotion checklist

Promotion to shokunin requires all of:

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources
      → Author assertion: `SKILL.md` §§Decision table, Error signatures, Checklist; no named non-author verifier.
- [~] At least one end-to-end domain task executed and logged in LOG.md
      → Author assertion: `LOG.md` §§round 1–3 records executed endpoint reconciliation and invocation history; current `DEAD` is not model readiness. Round 16 adds one live lane-owned task: `LOG.md` §round 16 and `.ufo/waves/round-16/live/receipt.json` — 10/10 `kama-llamacpp-live/v1` checks on the pinned llama.cpp b11755 build and GGUF on an unregistered loopback port (`MODEL_OK`/`matched` exit 0, `MODEL_MISMATCH`/`served-id-mismatch` exit 2, teardown proven, `loading_observed` false); a lane-owned control, not registered-consumer reconciliation, other runtimes, generation or model quality; no non-author `[x]`.
- [~] Instructions executable by an agent without oral context
      → Author assertion: `SKILL.md` §Checklist and `corpus/knowledge/snapshot-history.md` §Run it; independent execution review remains open.
- [~] No cross-domain bleed (PROVINCE.md still accurate)
      → Author assertion: `PROVINCE.md` §Write boundary and `corpus/knowledge/cross-lane-scope.md`; service repair, routing and credentials remain operator/sibling-owned.