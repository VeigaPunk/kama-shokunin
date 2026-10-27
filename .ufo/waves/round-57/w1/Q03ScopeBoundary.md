# Q03ScopeBoundary — round-57 C1/C2 boundary check (seat report)

Lane: kama · round 57 · wave kama-r57-w1 · seat Q03ScopeBoundary (connector, leaf, no subagents).
Scope: check C1/C2 against lane boundary (PROVINCE.md), MISSION conflict, and neighbouring lane domains. Report resolved overlaps and open boundary only.
Separate case-20 evidence file: `.ufo/waves/round-57/w1/Q03ScopeBoundary.case20.md`. Receipts: `.ufo/waves/round-57/w1/receipts/Q03ScopeBoundary/`.
Installs or updates in this seat: none. No commits, no lane-file edits, no shared-file writes.

## Verdict on the boundary

- Both calibration and operability are declared axes for kama in `/home/vgpnk/Projects/shokunin/shokunin.conf` (`kama|kama-shokunin|operability + calibration`). Neither round-57 claim touches freshness.
- Ownership of both surfaces stays in kama. The problems are in the claim definitions, not in the domain split.
- Two items are not resolved and need a ruling: the axis attribution of the prereg no-op defect, and the operability target surface that the amendment changed. Details below.

## 1. Resolved overlaps (no open boundary)

| Surface | Neighbour check | Result |
|---|---|---|
| Self-description counter `tools/round42-selfdesc-reconcile.py` (SCORECARD head, README, PROVINCE, capability/saturation sections) | Calibration per AXES.md means SCORECARD/SHONEN entries match repo state. The counter reads only kama files. No sibling lane claims these files. | In-lane, calibration. Resolved. |
| Canonical capability table (highest table = round 49, 11 data rows at frozen tip) | Each row's evidence pointer is a kama tool or path listed in PROVINCE.md. | In-lane. Resolved. |
| Fleet gate consumption of the printed `met=` line | `grep -n "met=" scripts/shokunin-watchdog.sh scripts/sources-census.sh` and `grep -rn "met=" scripts/hyaku` returned no consumer of the met line. | No fleet gate depends on the kama counter's met line. Resolved. |
| Sibling do-nothing controls (e.g. mado `controls/K2DoNothing.py`, mori `controls/do-nothing-r30-gate-port.sh`) | Same craft pattern in other lanes; no shared artifact, no shared domain. | No overlap. Resolved. |

## 2. Open boundary (not resolved; for operator / closure ruling)

### 2a. Frozen C1 description does not match the repo

- Frozen text: "counter currently reports maxN=56 instead of expected 46."
- `maxN=56` is the correct latest round. SCORECARD has `## Round 56` at line 3121 of the frozen tip (`b89bdab2`).
- `46` appears only as a hard-coded literal in the do-nothing controls `controls/c1-noop.py` and `controls/noop-c2.out`. No repo source derives it.
- The canonical table at the frozen tip has 11 data rows, not 46.
- The only failing fact in `controls/base-c1.out` is the calibration run: SCORECARD states `42`, the tip counts `43` corpus/lessons `*verifier-spotcheck.md` files. This matches the amendment's description.
- Evidence: case-20 file §C.

### 2b. The amendment changes the operability target surface, not only the label order

- The frozen operability target (commit 89dc4f52) is round-42 canonical-row binding. Its controls `noop-c2.out` (`canonical_table_reads=0; self_description_reads=0`) are round-42-shaped.
- The amendment (commit 7c873d7b) replaces that target with the round-56 prereg roster check (`tools/round56-prereg-check.py`). The amendment says "supersedes ... claim ordering only, not its base/control evidence." The operability surface changed. No frozen control file in `controls/` references the prereg check.
- Evidence: case-20 file §B.

### 2c. Axis attribution of the prereg no-op defect conflicts with its own authority

Round-56 sources put the prereg check on calibration:
- SCORECARD round-56 section: "C2 (preregistration/battery roster fidelity, calibration)".
- `tools/round56-prereg-check.py` line 1: "Round-56 C2 calibration counter".
- `corpus/lessons/round-56-verifier-spotcheck.md` (outside closure): "C2 calibration 7→7 — unprovable"; routed "Strengthen C2-style calibration gates ... a roster literal/no-op harness must fail."

The round-57 amendment says "Round-56 outside verification finding is authoritative" and then places the same defect on operability. Its cited authority puts it on calibration. Open for the operator/closure to rule. Under MISSION's historical axes (operability + freshness) neither calibration move would be admissible; see 2d.

### 2d. MISSION conflict (not resolved, per seat spec)

- `MISSION.md:29` says `kama: { ... axes: "operability + freshness" }`. The line sits inside the historical example block of MISSION.md (the file says "Historical example — the upstream fleet's initial nine-lane config, not the current roster").
- `shokunin.conf` kama row and SCORECARD round-56 authority say operability + calibration.
- L0 record: `.ufo/l0-questions.md:145` (`kama | round-35 | MISSION.md:29 still says operability + freshness; ... Round 35 named the conflict, did not edit MISSION.md ...`). Still open.
- Effect on round 57: none of the claims is on freshness, so the conflict does not change admissibility under the conf. It does matter if the L0 ruling moves kama to freshness, since both round-57 calibration/operability assignments would then need re-scoring.

### 2e. Prereg no-op predicate is reachable by a dead-call harness (boundary of the repaired predicate)

Commit 7b74e2f2 makes the prereg counter require `expected <= invoked`, where `invoked` is every constant label appearing as a `run(...)` or `assert_mutant_breaks_detection(...)` argument anywhere in the AST. Independent fixture test (case-20 file §D, receipts copied):

```
fx-genuine      (battery unchanged)                             -> met=True  exit=0
fx-noop-literal (ROSTER kept, main returns 0, no calls)         -> met=False exit=1
fx-deadcall     (ROSTER kept, main's first stmt `return 0`,
                 original run() calls unreachable after it)     -> met=True  exit=0
```

The dead-call harness declares the matching roster and executes zero battery entries, which is exactly the no-op the amendment's C1 predicate says must be rejected. The predicate is not met as written. Routed to R03NoopAttack, R07KillDesign, R09CounterMutation for confirmation. I did not change any counter.

### 2f. Do-nothing rule source not located

Round-56 SCORECARD cites "§9's do-nothing-control rule". `grep -n 'do-nothing'` over `PROTOCOL.md`, `PROTOCOL-APPENDIX.md`, `AXES.md`, `LEARNING.md`, `CORPUS.md`, `corpus/QUALITY.md`, `corpus/README.md` returned no rule text. The nearest fleet owner for "gate integrity" is the protocol lane (`shokunin.conf`: `protocol|.|fleet-meta: protocol soundness, gate integrity`). Left open as a reference gap and a possible protocol-lane overlap; not claimed.

## 3. Process observations (for the main agent)

- Commit timeline on kama-shokunin (all round 57, 2026-10-27): freeze `89dc4f52` 15:05:51; amendment `7c873d7b` 15:06:45; build `7b74e2f2` 15:08:48 (prereg executed-binding, SCORECARD 42→43, round-57 lesson); measured-outcomes record `8640e34c` 15:10:17. The build commit (`7b74e2f2`) landed before any seat report, so seat evidence cannot be treated as independent of that implementation.
- Working tree at my late check: `corpus/lessons/round-57.md` modified (+3/−1). Not mine; not evaluated.

## 4. Routing summary

| Item | Owner for ruling | Evidence |
|---|---|---|
| 2a frozen C1 wording | closure / main | case-20 §C |
| 2b operability target replaced | closure / main (operator if contested) | case-20 §B |
| 2c axis attribution of prereg defect | operator / L0 | case-20 §E |
| 2d MISSION conflict | L0 (`.ufo/l0-questions.md:145`) | MISSION.md:29, shokunin.conf |
| 2e dead-call predicate gap | R03NoopAttack, R07KillDesign, R09CounterMutation | case-20 §D, receipts |
| 2f §9 rule source | protocol lane / main | case-20 §F |

## 5. Commands the main agent may re-run (read-only)

```
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show b89bdab2cc114735ec5d331c6c610134258f7864:SCORECARD.md | grep -n '^## Round 56'
git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree --name-only b89bdab2cc114735ec5d331c6c610134258f7864 corpus/lessons/ | grep -c verifier-spotcheck      # expect 43
cat /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-57/w1/receipts/Q03ScopeBoundary/prereg-deadcall.out                                              # expect met=True exit=0
grep -n 'maxN=46' /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-57/controls/c1-noop.py                                                             # hard-coded literal
```

Report: `.ufo/waves/round-57/w1/Q03ScopeBoundary.md` (this file); case-20 evidence: `.ufo/waves/round-57/w1/Q03ScopeBoundary.case20.md`.
