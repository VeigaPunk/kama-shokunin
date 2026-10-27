# Kama round 58 — verifier spot-check

author: hyaku closure (non-author integrator, @m_opus)

## Conformance

- Report `.ufo/reports/round-58/kama.md` is substantive and filed by fleet identity `kama-shokunin` (commit `a70599060e0e43d138473713cb2d236ef84ec1a0`); it has `## SHONEN` with four `[~]` lines. All cited lane commits exist and are ancestors of `master`, including cited HEAD `8f7f58cd161f2b7dfa1709450c3ae79599c12833` (`git merge-base --is-ancestor … master` exit 0). Prompt contains round-level and child-lane contract. Status `ok`; SHONEN items remain author assertions. The lane helper reports `ahead=0`, but current status contains six unrelated round-60 untracked outputs; these are later work, not round-58 residue.
- Dispatch/completion digest copied from watchdog: `2026-10-27T16:37:20-03:00 launch kama round=58 pgid=2085611 driver=hyaku-inline attempt=1`; `2026-10-27T17:13:08-03:00 complete kama round=58; hyaku-inline attempt=1`.

## Claim re-checks and axis verdicts

| Claim | Re-check and observed committed evidence | Axis verdict |
|---|---|---|
| C1 operability 8→8 | Re-derived SOURCES count: `git show 2f53614e6f5895560edb775cc3e74841aa0dd44c:corpus/SOURCES.md \| grep -cE '^ {0,3}\\\|[[:space:]]*S[0-9]{3,}[[:space:]]*\\\|'` = 257; same at `8f7f58cd161f2b7dfa1709450c3ae79599c12833` = 259. Evidence-verified (not rerun): committed frozen receipt `.ufo/waves/round-58/measured/c1-final.out` at measured `9351cc58…`: genuine 1/1, benign 3/3, no-op rejected 11/11, errors 0, `met=True`; base receipt has benign 1/3 and no-op rejected 1/11. The lesson/knowledge entry explicitly limits this to frame entry and recorded argv, not subprocess outcome or sandboxing. | improved (claim verifies; score remains 8) |
| C2 calibration 7→7 | Evidence-verified (not rerun): `.ufo/waves/round-58/measured/c2-final.out` at `9351cc58…` records `r42=0 missing=0 stale=0 verdict=0 including=0 mismatches=0 met=True`; base control has 4 mismatches. The report explicitly says the committed measured tree predates this spot-check and that typed population 44 becomes stale. | improved (claim verifies; score remains 7) |

Owned-axis harm: none observed; scores unchanged. Non-owned coverage evidence 34→35 is in the report. The append-only audit is disclosed red (unrestored 8→9); this is a conformance defect routed below, not evidence of owned-axis harm. Other axes unchanged. Discernment claim C2 is numerically verified, but no non-author review had yet judged the round's gate choices in the lane report.

## Discernment spot-check

| Item | Decision | Re-opened source | Agreement | Reason |
|---|---|---|---|---|
| S518 | Admit | https://man7.org/linux/man-pages/man8/ld.so.8.html, §ENVIRONMENT / Secure-execution mode and §LD_AUDIT | Agree, scope caveat | Reopened page states `LD_AUDIT` is ignored in secure-execution mode and names nonzero `AT_SECURE`; quote “LD_AUDIT is ignored in secure-execution mode.” is present (6 words). Supports S518's scoped distinction; does not itself establish runtime behavior of this checker. |
| S513 (carried reject) | Reject | https://man7.org/linux/man-pages/man7/rtld-audit.7.html, §DESCRIPTION; compare reopened ld.so(8) above | Agree with retaining the narrow rejection; disagree with original blanket rationale | rtld-audit(7) says `LD_AUDIT` must contain a colon-separated list of shared libraries, sufficient for name-presence detection. It lacks secure-execution/token details; the reopened loader page includes them, so general redundancy is not a sound rejection rationale outside the narrow question. This is consistent with the lesson's claim-scoped supersession, not erasure. |

S517 additional reopen: https://docs.python.org/3.15/library/sys.html#sys.setprofile, §`sys.setprofile`; quote “only on call and return, but the return event is reported even when an exception has been set” is present (18 words). It supports the stated boundary: profile hook reports call/return, not each executed line. The opened documentation also explicitly warns Python audit hooks are not a sandbox.

## Trend verdicts

- **Expansion — improved (narrow):** one admitted knowledge entry on instrument evidence, with `source: S517`; new S517/S518 rows and 259 final SOURCES rows are evidenced. This is checker knowledge, not expanded serving capability.
- **Quality — improved:** the committed finite matrix rejects the previously accepted no-op family (11/11), while the corpus entry and report disclose escaped cases and the in-process, non-sandbox boundary. No sampled admitted entry was found false.
- **Discernment — improved:** outside sample agrees with S518 admit and with retaining narrow S513 rejection; the broad original rationale is explicitly rejected and scope narrowed in the lesson. Reopened S517 quote also matches.

## Routed defects for next round

- Route self-defect: append-only audit remains red at tip (`unrestored=9` vs base 8); add a durable, contract-valid correction path for the S517 anchor edit and remeasure, not prose-only disclosure.
- Route self-defect: frozen C1/C2 controls have disclosed survivors/mutants (C1 roster-match/kills-controls/stack-pop; C2 stale/verdict/including); next-round controls must independently target them before data.
- Route self-defect: lane report's trend discernment was still `unprovable-but-better` pending outside judgment; reconcile with this spot-check in the next lesson/report without rewriting this filed record.
- Operator-owned: report notes fleet-root `o.bin` was unattributed; preserve for operator attribution/removal decision. MISSION/config axis mismatch also remains open/operator-owned.
- Census command `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`: completed with `kama ok`, but emits W04 duplicate-URL warnings and W01 S481 tier-C mined warning (including new S518 duplicate URL); status remains validator `ok`.
