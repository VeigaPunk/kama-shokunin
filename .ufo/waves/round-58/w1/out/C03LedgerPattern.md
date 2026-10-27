# C03LedgerPattern — fleet pointer binding (read-only)

## Finding / axes
- **Calibration:** the stale-pointer motif is real and can be checked against a second source. Current `SCORECARD.md` calibration row says the latest outside closure is round 57, while the fleet `MANIFEST.json` (round 58 freeze references its manifest snapshot as `941acf70583a2b3a1d33460b31967e0efd291f3e`) is authoritative for the kama lane-round verdict. The frozen C2 counter is explicitly measuring this coupled pointer/verdict relationship; this is direct, reusable precedent for detecting drift.
- **Operability:** no fleet-wide shared binding check was located in the inspected tree. The existing `tools/planned-pointer-check.py` is a narrow local-file checker for the Planned section and measured-result headings; it does not read MANIFEST or resolve a SCORECARD outside-closure pointer. Existing `tools/round58-c2-counter.py` is the closest reusable implementation, but it is round-specific, not a fleet-wide registry/check.

## Evidence and bounded move
Evidence inspected: fleet `MANIFEST.json` roster (kama entry); kama `SCORECARD.md` lines 6, 18; `tools/planned-pointer-check.py`; round-58 frozen claim description (C2 counter path and manifest revision).

**Proposed move:** generalize the C2 counter’s narrow binding logic into a read-only fleet checker over each roster lane: derive the highest-numbered committed `corpus/lessons/round-N-verifier-spotcheck.md`, then require its SCORECARD calibration row to name that N and agree with the corresponding lane-round verdict in fleet MANIFEST. Emit per-lane missing/unresolvable/mismatch results rather than a single aggregate, so absence is not silently treated as agreement. Keep the round-58 frozen predicate unchanged; this is a follow-on reusable check, not a retroactive C2 rule change.

This would improve calibration by catching stale or internally inconsistent outside-closure claims; it can improve operability by making the cross-repository check repeatable. It does not imply all lanes use kama's exact SCORECARD wording or verdict vocabulary: that contract difference must be resolved before a shared checker is made normative.

## Risks / verification
Risk: lanes may lack spotcheck files, use a different calibration-row schema, or have MANIFEST closure verdicts without a one-to-one spotcheck. A naive common parser could produce false failures or treat missing evidence as clean. Preserve explicit `not-applicable`/`unresolved` outcomes and establish lane-specific schema mapping before gating.

Checks run: no executable checks; read-only inspection only. No outputs or exit codes are claimed. Verify any implementation with committed-byte fixtures covering a current match, stale round, wrong verdict, missing spotcheck, absent MANIFEST closure, and schema divergence; also run the existing round-58 C2 counter against its frozen manifest revision. No production files edited.