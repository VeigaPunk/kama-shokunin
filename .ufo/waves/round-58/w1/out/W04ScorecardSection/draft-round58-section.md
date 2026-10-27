## Historical authority text — round 57

The exact former current-authority line is retained here; the live authority above supersedes it.

```text
**Current authority (round 57):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35). Latest measured round: 57. Calibration 7 is the lowest assigned axis, below operability 8 and the saturation line, so the stagnation nudge is inactive. Round 57 froze and measured C1 (no-op battery roster-control, operability) and C2 (stale self-description verifier-spotcheck count, calibration) with controls committed before data (SCORECARD §Round 57). Scores remain operability 8 and calibration 7; no capability enters. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived by `tools/round42-selfdesc-reconcile.py`; the historic round-56 statement is preserved under §Historical pre-integration authority.
```

## Round 58 — execution-bound battery checker and MANIFEST-bound closure pointer (2026-10-27)

Pre-data freeze: `dcd69473dd7e33b316e2ba238a48e5119a6cd809`; do-nothing controls: `cb1ef10228193d2134440bca1175bf560b2e67be`. C1 replaces the round-57 call-site inventory with an execution-bound battery checker (operability); C2 binds the calibration row's outside-closure pointer to the fleet MANIFEST verdict (calibration). Base `2f53614e6f5895560edb775cc3e74841aa0dd44c`; build tip `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a`.

| Claim | Axis, score | Before → after | Counting command and evidence |
|---|---|---|---|
| C1 — execution-bound battery-roster check, not call-site inventory | operability 8→8 | base round-57 checker `genuine=1/1 benign=1/3 noop_rejected=1/11 met=False` → PENDING `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True` | `python3 tools/round58-c1-counter.py --repo <repo> --tip <revision>`; the 15 variant files under `tests/round58-battery-variants/` (1 genuine, 3 behaviour-preserving, 11 enumerated no-ops); the do-nothing controls (unchanged base checker, always-accept, always-reject, hash-only) fail the frozen predicate, receipts under `.ufo/waves/round-58/controls/`; measured receipt PENDING at the round-58 measured tip; sourced on S517 |
| C2 — calibration row's outside-closure pointer bound to the fleet MANIFEST verdict | calibration 7→7 | base `mismatches=4 met=False` (r42=1 stale=1 verdict=1 including=1; the row stated round 56 `admitted` while the fleet MANIFEST holds `rejected-honest-stop`) → PENDING `mismatches=0 met=True` | `python3 tools/round58-c2-counter.py --repo <repo> --tip <revision> --manifest-rev 941acf70583a2b3a1d33460b31967e0efd291f3e`; the do-nothing controls (claim deleted, verdict flipped only) fail the frozen predicate, receipts under `.ufo/waves/round-58/controls/`; measured receipt PENDING at the round-58 measured tip |

Scores held at operability 8 and calibration 7; no capability added. C1 scores the checker only against the 15 enumerated variants — a survivor outside that set is a reported limit, not C1 credit, and never a reason to widen the frozen predicate. C2 binds one row to a fleet ledger verdict; it is not an independent outside admit/reject judgement of the round.

### Planned (round 59)

1. Operability: push the checker past the enumerated variant set — freeze a generated no-op survivor hunt before data, and assert the harness observes the battery's own reads rather than its exit status alone.
2. Calibration: replace the ledger-bound pointer with an outside non-author admit/reject spot-check at the measured tip, and re-freeze C2 against that spot-check rather than against the fleet MANIFEST verdict token.
