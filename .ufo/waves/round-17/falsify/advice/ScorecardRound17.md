VERDICT: partial — the C1/C2 counts and bounded trend assessments align, but C2 overstates K7 attribution and the planned row omits the required target.

Scope attacked: SCORECARD.md §Round 17 at commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`: C1/C2 table values, score deltas, capability statement, no-harm and other-axis readings, LEARNING trends, and planned work.

## Findings (severity order)

### P2 — C2 says all eight bad controls fail their targeted check, but K7 has no target-check attribution

`SCORECARD.md:681` says “current 0 of 8, each failing its targeted check.” The overall count is right, but the per-control attribution is too strong. `tests/llamacpp-live/controls.py:297-299` explicitly says an empty target list means “no check-level grading expected”; `controls.py:322-323` defines K7 as a bounded hang (`--ready-timeout 2`) with that empty list. The current K7 record at `.ufo/waves/round-17/runs/controls-current.json:186-202` has `expected_failed: []`, `attributed: null`, and failures `teardown_graceful`, `teardown_port_closed`, and `loading_envelope_graded`; the run is rejected with `tool_exit=2`, `gate_exit=1`, and `receipt_setup_error=ready-timeout`. Thus the evidence supports K7 rejection by timeout, not failure of a targeted check. The other seven bad controls have nonempty target lists and are attributed. Keep `0 accepted-bad / 0 inconclusive` as recorded, but qualify the targeted-check claim and identify K7 as the timeout-only case.

### P3 — The planned next move lacks an axis or capability target

`SCORECARD.md:704-708` plans outside sampling, then says “Next steered move: K05 … or the round-16 M3 harness `shutdown()` design gap”; neither alternative names a target axis or capability. `AXES.md:81` requires the planned field to list “intended claims (1–3), each with its target axis or capability.” Add the intended target for each option (or select one after the outside sample) so the next-round plan satisfies the contract.

## Cross-checks: no other disagreement found

- **C1 table:** `runs/fault-controls-{frozen,current}.json` agrees with 3 accepted of 8 (frozen) versus 0 of 8 (current); exits are 1 and 0. `runs/mutants-grid.json` agrees with frozen/pair 1 of 8 applicable, frozen/full 7 of 8, current/pair 1 of 10, and current/full 10 of 10. M6/M7 are site-missing in the frozen checker, matching the applicable denominator.
- **C2 totals and live runs:** `runs/controls-{frozen,current}.json` agrees with frozen 6 accepted-bad plus 1 inconclusive and current 0 accepted-bad plus 0 inconclusive; current `gate_flip_bad` is 0 and K0 passes. `live/gate.txt` records all three receipts VALID with exit 0; `receipt-1.json`, `receipt-2.json`, and `receipt-3.json` each contain 11 passing checks of 11.
- **Score deltas and capability:** calibration 7→7 and operability 8→8 (delta 0) are consistent with the bounded improvements and the stated refusal to convert finite control counts into mastery scores. No new capability row is warranted: `live-llamacpp-lifecycle` is the round-16 capability being hardened, with its round-17 evidence pointer updated to v2.
- **No-harm:** the raw mutant/fault artifacts pin the unchanged probe digest `36b64978…` and matrix digest `bf9068d8…`. `runs/noharm-r16-measure-clone.txt` records 55/17→72/0 and exit 0; `noharm-test-snapshot.txt` records 30/0; the check selftest records 72/72 plus 5/5 malformed cases; receipt-gate selftest records two valid receipts accepted and 39 mutations plus unreadable input rejected. The v1 receipt gate output and round-13 selftest agree with the scorecard's stated checks.
- **Other axes and trends:** the scorecard explicitly limits freshness evidence (“no registered endpoint re-sampled” at `SCORECARD.md:686-687`), so it does not present the b11756/b11757 source comparison as a live endpoint sample. Expansion unchanged is consistent with no new uncovered knowledge entry or capability; quality improved is supported by the appended v2 section superseding the existing entry's v1 limits (`corpus/knowledge/llamacpp-loading-lifecycle.md:194-203`); discernment unchanged matches the lack of a non-author round-17 sample. These align with `LEARNING.md:33-35`.
- **Source rows:** current `corpus/SOURCES.md:54-58` contains the five new mined A-tier rows S042–S046, consistent with 41→46, A 38→43, mined 31→36. The run artifacts contain the append-only guard selftest (14/14), but no final source-census output; therefore the stated census exit 0 is not independently demonstrated by the listed `runs/` artifacts.

## Residual risk and verification gaps

- LSP was unavailable: requesting `xd://lsp` returned “No such tool.” No LSP status, references, definition, or diagnostics were available; no grep output was used as semantic proof.
- Reviewer-run command: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD` — exit 0, returned the assigned commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`. No gate, count, test, or live command was run by this reviewer; findings above compare the committed raw artifacts and receipts. No ports were contacted or bound.
- No tools installed or updated. No scratch files created.
