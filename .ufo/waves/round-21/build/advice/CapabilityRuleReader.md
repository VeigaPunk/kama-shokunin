VERDICT: partial - C1 qualifies as a measured calibration axis-move (not a capability row; 7→7 recommended, 7→8 unsupported by lane precedent); C2 does NOT qualify as a capability acquisition row (operability hardening, 8→8).

# CapabilityRuleReader — round-21 claim-type rulings (kama)

Scope: rules and lane state only. Lane untouched; evidence from a scratch clone at a29bb84 (removed). Command exits: `out/CapabilityRuleReader/evidence.md`. [INFERENCE] marks unexecuted reasoning. Installs or updates: none.

## 1. Kama's assigned axes
- `shokunin.conf:52`: `kama|kama-shokunin|operability + calibration (local model serving and endpoint health)`.
- `MISSION.md:29` (`operability + freshness`) sits under MISSION.md:16-17, "Historical example … not the current roster". MISSION.md:49-51: "Axis assignments in `shokunin.conf` are initial".
- SCORECARD:226-228 (round 11): "the current kama row is operability + calibration … Calibration 7 is lowest assigned (operability 8); across the full historical table it ties depth/adjacency at 7." Round 10 (SCORECARD:192) had read MISSION:29 as authority; round 11 superseded that. Retired: none (SCORECARD:59).

## 2. Stagnation nudge: inactive
- AXES.md:68-70 waives the lowest-axis obligation only when "every axis the lane owns sits at or above the lane's saturation line" and no capability entered within the window.
- Saturation line 8 (SCORECARD:132). Calibration is 7; depth and adjacency are also 7 on the all-scored reading. Last capability entry: round 20 (SCORECARD:913). Inactive on either axis reading.

## 3. C1, calibration (report landing audit): qualifies as a measured axis-move, not a capability row
- Lowest-axis obligation met (AXES.md:33-34): calibration is lowest assigned; on the all-scored reading it ties depth and adjacency.
- Not a capability: AXES.md:59-60, the six axes "do not measure what the shokunin can now *do*". C1 checks report-versus-repo agreement (AXES calibration row) and adds no repertoire row. [INFERENCE]
- Counting commands, run with explicit `--fleet-repo` (default resolves to the scratch parent and exits 2; default works only in-fleet, audit:381):
  - `--no-errata`: defects=9, uncorrected=9, status=failed, exit 1.
  - default: corrected=9, uncorrected=0, status=clean, exit 0.
  - `--selftest`: cases=15, failed=0, exit 0. This is capability, not measurement (PROTOCOL.md:390).
- Score: the SCORECARD header allows self-assessed scores, but every calibration verdict R11-R20 lands 7→7 (e.g. SCORECARD:320, 417, 501, 610, 680, 782, 900). The only declared calibration 7→8 (R19, :821) was corrected to 7→7 at falsify (:844-845). Recommend **7→7, improved-bounded**; 7→8 needs an operator ruling (AXES.md:35-36).
- The "after" is errata coverage. Raw defects stay in the append-only reports; uncorrected 9→0 comes from one appended row per detected token. [INFERENCE: self-referential; the independent signal is the raw count plus selftest.]
- Not admissible yet under the PROTOCOL.md gate standard:
  a. Mutable input: audit:105-107 reads `Path(fleet_repo)/rel` from the working tree. PROTOCOL.md:393-397 requires a committed-snapshot run with a committed expected verdict. None in the draft.
  b. No revision named: `--json` keys are errata_invalid, errata_unmatched, results, summary. PROTOCOL.md:393-394 requires the verdict to name its revision.
  c. No registry row: SKILL.md has no match for report-landing/landing-audit. PROTOCOL.md:418-421: no gate is conformant without one.

## 4. C2, install-links pin: does NOT qualify as a capability acquisition row
- Rule: AXES.md:63-64, "Rows enter only through a round that demonstrates the capability running; a capability without a passing demonstration in the round report is pre-claiming and does not enter the table." The claim type must be declared (AXES.md:40-41; round-prompt.md:24-26). The draft's "capability-shaped" is not a declared type.
- No fleet rule defines hardening. A grep of AXES, MISSION, PROTOCOL, LEARNING and templates finds only a generic phrase, "generic hardening advice" (templates/agents/ufo-sentinel.md:22). The boundary therefore comes from lane precedent [INFERENCE]:
  - C2 adds one pin to the existing row `live-llamacpp-lifecycle` (SCORECARD:628, first working round 16).
  - R17 (:669-670): "no new capability row (the round-16 row is hardened, not new)". R18 (:749-751): "hardened, not newly acquired". R19 (:828-829): "8 → 8 (delta 0): sixth pin --expect-install-tree-sha256", no row.
  - R20 named "symlinked soname identity" as frontier (:920-922). Closing it is the same hardening.
  - "TreeCap" is a round-19 build-seat name (LOG.md:1182), not a capability row.
  - Strongest counter: before the change the gate could not reject a retargeted soname link, which reads like a new ability. Rebuttal: the R19 install-tree pin had the same blind spot for regular files and was scored 8→8 with no row.
- Ruling: operability axis-move (hardening), 8→8 with delta 0; no capabilities row in round 21. Its before→after is the grid counts (frozen 0/9 → current 9/9), claimed by the L1 and not re-run by me.
- If the operator rules "capability" anyway: the row needs an in-report demonstration, and PROTOCOL.md:355 requires "a probe against the real surface". The grid runs on a mirror copy of the live tree (`install-links-grid.py:44`, `mirror()` 83-91), so it is not that probe. The real tree has 10 soname symlinks (find, exit 0), so a read-only probe is feasible.

## 5. Other admission conditions (not claim rulings)
- Draft a29bb84 touches 7 files, none of them SCORECARD.md, LOG.md, SKILL.md or corpus/ (diff exit 0, empty). AXES.md:27-30 requires SCORECARD/LOG entries per claim.
- No `Report:` trailer on the commit (log exit 0).
- Frontier step (round-prompt.md §2b, "not a fourth claim"): corpus/SOURCES.md and the round-end census are absent.
- SKILL.md rows for check-receipt.py (lines 536, 574, 654) omit the new optional pin; the grid has no row.
- No-harm evidence (AXES.md:35-36) is absent; show legacy receipts' verdicts are unchanged through the changed gate.

## 6. Summary

| Claim | Type | Axis | Score | Blocking items |
|---|---|---|---|---|
| C1 | measured axis-move | calibration (lowest) | 7→7 recommended | committed snapshot, named revision, registry row |
| C2 | hardening axis-move, not capability | operability | 8→8 | SCORECARD/LOG entries, no-harm run, registry pin |

Not run by me (L1/verifier scope): grid, check-receipt selftest, producer runs.
