Verdict: Residual self-report acceptance remains in the hexrun `unverifiable` class, GGUF receipt reconciliation, and a shared cell-definition check.

Evidence: inspected `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:296-309` (instrument registry) and tools. `tools/hexrun-census.py:26-33,41-42` accepts a ledger `unverifiable` row solely when note length is at least ten and counts it as passing. `tools/gguf-identity.py:8-10` explicitly calls receipt evidence self-report; `:4-6` accepts `--receipt`. `tools/kama-context-capacity.py:602-616,619-635` imports counter CELLS and compares them to embedded cells, leaving a shared-definition-change possibility. Counter/documentation claims were inspected, not executed; no command outputs or exit codes are claimed.

Affected axes: calibration is exposed by unverifiable self-attestation and non-independent receipts/shared definitions. Operability may conflict with making unavailable upstream evidence a hard failure.

Proposed bounded move and ranks are in `patterns.md`: first require auditable justification for hexrun's passing unverifiable disposition; second preserve GGUF's self-report distinction at every acceptance boundary; third bind context-capacity definitions to an independently frozen authority if independent calibration is intended. Risks and suggested verification cases are recorded there. No edits to lane instruments or counters.

Report: `.ufo/waves/round-48/w1/out/N4Pattern.md`
