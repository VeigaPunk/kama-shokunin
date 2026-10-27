# Q01CritiqueRound56 — routed-defect audit (case 18)

Scope: read-only audit of `corpus/lessons/round-56-verifier-spotcheck.md`'s four routed defects against the available current-tree evidence. No source edits or VCS mutations. Axis scope per round assignment: operability + calibration; do not resolve the historical MISSION/config disagreement locally.

## Disposition for round 57

1. **Axis-authority conflict — carry as an unresolved mistake / operator criterion, not a lane fix.** Round-56 lesson routes the disagreement to operator/L0. Current `/home/vgpnk/Projects/shokunin/MISSION.md` lines 20–40 says kama `operability + freshness`; the round-57 dispatch/spec says axes `calibration`, `operability`, and the supplied assignment says SCORECARD/shokunin.conf governs this round. These are materially different authorities. Preserve the discrepancy explicitly in lesson/report and request an operator decision; do not silently substitute freshness or calibration. Evidence: retain both literal declarations and the dated authority decision.

2. **No-op / executed-entry binding — confirmed active mistake; criterion and fix required.** Round-57 `controls/freeze-amendment.txt` explicitly records the frozen checker defect: literal matching roster may pass without battery execution. `controls/noop-c1.out` records a do-nothing script returning `mismatches=0 maxN=46 met=True`, exit 0; `controls/noop-c2.out` records `canonical_table_reads=0`, `self_description_reads=0`, same green summary, exit 0. This is direct counterexample evidence, not a hypothetical. The lesson criterion should require actual canonical input/content binding and observed execution of required entries; the fix should fail closed when required reads/executions are absent. Suggested evidence: genuine base/build outputs plus omission/no-op controls proving nonzero target reads and entry execution, with omitted/changed-row mutations rejected. Keep this separate from the maxN calibration repair.

3. **S513 rejection rationale — carry as a mistake/quality criterion, not assert a new decision.** Round-56 spot-check reports the reviewer disagreed with S513 REJECT because the cited ld.so.8 source does include LD_AUDIT as well as distinct dynamic-token/secure-execution detail; broad overlap alone does not establish redundancy. The current round-56 lesson records the disagreement and its reason, so the defect is lesson-addressable, but I found no evidence in this audit that an updated round-57 lesson has landed. Criterion: distinguish overlapping coverage from redundant scope and justify rejection against the row's specific claim; capture one independently reopened admit/reject decision and whether the reviewer agrees. Advice only; this seat is a lane author, not the non-author adjudicator.

4. **Append-only/report audit defects — still require repair evidence; do not call the audit clean.** Current round-56 `measured/append-only-audit-at-784.out` reports `exit=1`, `unrestored=2`, `bad_declarations=4`, and lists stale SCORECARD bindings for two events plus four invalid historical declarations. The round-56 lesson routes this for repair. Round 57 should record it as an inherited mistake unless a new audit demonstrates repaired bindings; evidence must include exact audit command, exit, and per-event/declaration results. This receipt alone does not prove current round-57 tree is repaired.

## Case 18 independent test

The assignment's case 18 is the independent outside-defect audit. I re-opened the round-56 lesson and checked the current round-57 frozen controls and the cited round-56 audit receipt. The no-op defect remains concretely reproducible by the supplied receipts (both report green with zero inspected data); the append-only defect remains evidenced by the latest available receipt at 784. The other two are governance/discernment findings and should not be mislabeled as executable fixes owned by this lane. No sibling or tool output was treated as proof of a current repair.

## Spot-check obligations / evidence limits

- S515 row in `corpus/SOURCES.md` identifies https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT, §GIT_CONFIG_COUNT, version 2.56.0, and cites an 18-word quote about `GIT_CONFIG_KEY_<n>` / `GIT_CONFIG_VALUE_<n>` pairs. I reopened the URL on 2026-10-27, but the reader result was the page's top-level navigation/version section and did not expose the anchored §GIT_CONFIG_COUNT text; therefore I cannot honestly attest a located quote from this fetch. Another seat should capture the actual section text and ≤25-word quotation before claiming this requirement satisfied.
- Round-56 lesson's S512/S513/S514 spot-check is available; advisory only: the recorded S513 disagreement is sufficiently concrete to preserve as a criterion. I do not issue an admit/reject decision.
- Counter sanity fact: direct shell glob `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` from lane root returned `43` (exit 0). This is distinct from the round-57 frozen counter output (`maxN=56`); do not equate these counts or use it to redefine the frozen target without tracing the counter's canonical selection.

## Exact observed outputs/exits

- Read `controls/noop-c1.out`: `mismatches=0 maxN=46 met=True`; `exit=0`.
- Read `controls/noop-c2.out`: `control=no-op instrument`, `canonical_table_reads=0`, `self_description_reads=0`, `summary=mismatches=0 maxN=46 met=True`; `exit=0`.
- Read `controls/base-c1.out` (and `base-c2-frozen.out`): `r41=1 ... mismatches=1 maxN=56 met=False`; detail says the `...glob(...verifier-spotcheck.md)...` run has no stdout line `42` (underlying Python command exit 0); `base_c1_exit=1`.
- Read `.ufo/waves/round-56/measured/append-only-audit-at-784.out`: `schema=append-only-audit/v3 definition=v6 threshold=1 exit=1`; summary includes `unrestored=2`, `bad_declarations=4`.
- Run `cd /home/vgpnk/Projects/shokunin/kama-shokunin && python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"`: stdout `43`, exit 0.
- Reopened S515 URL on 2026-10-27: reader exposed navigation/version metadata (latest git-config 2.56.0; last updated 2026-09-28), not the anchor passage; quote verification remains open.

No tools installed or updated.

Report: .ufo/waves/round-57/w1/out/Q01CritiqueRound56.md
