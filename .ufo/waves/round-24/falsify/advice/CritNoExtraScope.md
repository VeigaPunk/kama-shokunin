# CritNoExtraScope — FALSIFIED (scoped repair correctness); partial static scope assurance

## Axes

Correct local verdict preservation; repository/store identity and lookup-order neutrality; unavailable-evidence diagnostic truth; unchanged ambiguity/parser policy; read-only production and write confinement; source/registry consistency; six-month maintenance cost.

## Snapshot and bounds

- Own `--no-hardlinks` scratch clone: `/fast/scratch/hyaku/kama-r24/falsify/CritNoExtraScope`; detached HEAD observed as `2e254a1763a9c08aa07fc53081287f506c447d84`.
- Compared base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`.
- Observed SHA-256: auditor `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`; runner `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa`; manifest `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1`; mutation probe `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`.
- Read preregistration, amendment, frozen oracle metadata and supplement. Original metadata=>unknown expectation remains withdrawn/not achieved. Live rule is the amended local-object contract plus independent opaque cells; no path-based relaxation of names_any_of is assumed.
- One benign bounded offline lookup measurement only, two store orders within that measurement. No full suite, transport, execution-bearing vulnerability probe, PM08, installation, production source edit, or nested seat.

## Counterexample: fleet-only known blob falsely becomes unavailable content

A valid blob exists only in fleet; lane has no matching object. Both repositories are ordinary offline scratch repositories, with no promisor metadata and no unavailable referenced content needed by this measurement. The same full object ID must remain a known wrong type for commit-only Landed lookup, whichever store is inspected first.

Observed token: `21bd0dfe3d72f64c2925c528132fc310c6678dd3` (blob bytes `bounded local wrong-type witness\n`).

Exact measurement command:

```text
env TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CritNoExtraScope PYTHONDONTWRITEBYTECODE=1 python3 /fast/scratch/hyaku/kama-r24/falsify/CritNoExtraScope/scoped_lookup_check.py
```

Exit: **0** (measurement completed, not an auditor success verdict). Host Git: `git version 2.56.0`.

Finding/token pairs observed:

| Store order | Base `lookup(..., ^{commit})` | Integrated lookup | Integrated refusal call |
|---|---|---|---|
| lane, fleet | `missing` / `21bd0dfe3d72f64c2925c528132fc310c6678dd3` | `unknown` / same token | `round 1: unknown: unavailable required object: 21bd0dfe3d72f64c2925c528132fc310c6678dd3 is present but its content cannot be served` |
| fleet, lane | `missing` / same token | `wrongtype` / same token | returns normally; failed-finding path |

The helper result and refusal exception are **observed**. End-to-end CLI exit2 for lane-first versus `landed-unresolved` exit1 for the noncommit citation is **inferred from static caller flow**, not separately run: `audit_round` invokes `refuse_unknown` immediately after lookup, then maps wrongtype to `landed-unresolved` (tools/report-landing-audit.py:484–500). This is not a new claim about full-grid results.

### Cause and smallest safe correction

`lookup`, lines204–223, aggregates bare lookup across all stores, then uses that aggregate `bare[token] == found` as proof that the object exists in the *current* store. At lane-first iteration, lane's missing peel is thus misclassified as an unavailable target of a locally present object. Lines242–250 query the absent object again in lane and offer `unknown`. Since unknown outranks wrongtype, the valid fleet blob cannot repair that state. In fleet-first order, wrongtype is already set and the `status == absent` guard suppresses lane's bad offer.

Fix per-store provenance, not global policy: collect bare presence/type for each store and only attempt that store's `^{}` target diagnosis when the bare object actually resolves there. Merge per-store states after deriving them. Preserve cross-store found and ambiguity rules, genuine tag-target-unavailable refusal, existing object-store identity, and the current parser. Do not mask this by reversing stores or by changing RANK to let every wrongtype defeat genuine unknowns.

This is a fixable defect against the live contract and SKILL.md:833, not an acceptable declared trade. Impacted axes: correct local verdicts, operability, order neutrality, diagnostic provenance, and documented behavior consistency.

## Static scope findings

- Base-to-pin tool diff did not change `landed_match`, full-hash classification parser, source-census parser, branch identity resolution, global Git isolation flags, or the20-second Git deadline. No intentional alternates/gitfile identity or duplicate-section policy repair is present in this scoped diff. This is static scope assurance, not adversarial proof of those inherited properties.
- New normal-audit paths perform Git reads and per-run in-memory caching; the observed new writes/unlinks in the tool occur in selftest fixture code. No added production-path external write was found by this static review. No claim is made that inherited repository-local Git effects are universally isolated.
- SKILL.md:824–846, corpus/README.md:343–347 and S102/S103/S104 consistently distinguish lane policy from Git documentation and metadata from availability. S105 explicitly rejects S095's cross-API inference; S095 teaching stays historically filed. No source-census completeness/count claim is made: final105-row verification remains L1-owned.
- SKILL.md:833 promises known blob/tree=>failed finding; the measured counterexample falsifies implementation conformance to that promise. SKILL.md:855–857 correctly retains identity/ambiguity/parser limitations as unclaimed.

## Maintenance deadweight / smallest cleanup

- `build_store` (lines680–686) is a constructor-only wrapper with duplicated explanatory text and two callers in run. Optional smallest cleanup: construct RepoStore directly and keep the rationale on the class; not a correctness blocker.
- Required-unknown refusal wording and decision branches are duplicated between `refuse_unknown` and `apply_errata` (lines429–447 versus561–582). They share status, missing-ID and opaque-hole policy but differ only in context labels. A narrowly shared diagnosis helper returning the reason would reduce drift; preserve selected-round errata gating. This is a maintenance suggestion, not grounds for broadening the repair.
- The per-run lazy cache is justified by repeated token checks; do not remove it as deadweight. Store-wide dangling-object diagnosis is explicit in the live implementation/docs, not evidence of an unrequested branch-reachability policy change.

## Files written and unverified items

Files written: this report; scratch clone and its Git metadata; scratch `scoped_lookup_check.py`; scratch `scoped-lookup-fixture/{lane,fleet}` including the one fleet blob. A scratch diff capture was also created at `/fast/scratch/hyaku/kama-r24/falsify/CritNoExtraScope.tool.diff` during initial inspection (outside the leaf scratch directory but within the falsify scratch tree); it is not production evidence or a code change. No tool installed/updated.

Unverified: complete CLI fixture, complete47-cell regrade, fixed-candidate retest, source census, mutation inventory, global external-write absence, inherited Git>=2.45 operator disposition. No score increase, serving capability, admission, integration or shipping judgment is asserted. Review stops after this assigned bounded attack.

Report: .ufo/waves/round-24/falsify/advice/CritNoExtraScope.md

## Appendix — CLI recipe requested by L1 (not executed)

Measured helper evidence above is immutable. The following is a minimal independent end-to-end recipe for the correction owner; these CLI outcomes remain inferred, not observed in this review.

1. Under a fresh owner scratch directory, create two independent SHA-1 repositories with `git init -b master`. Give each one ordinary initial commit, author `fixture-owner`, subject `fixture seed` (neither a kama author nor round subject). Disable signing explicitly. Use fixed author/committer dates `@1000 +0000`.
2. In fleet only, use `git --no-lazy-fetch -C FLEET hash-object -w --stdin` on the exact bytes `bounded local wrong-type witness\n`. Call the resulting full ID T; it must be `21bd0dfe3d72f64c2925c528132fc310c6678dd3`. Do not copy its object into lane.
3. Commit `.ufo/reports/round-1/kama.md` in fleet at fixed dates `@2000 +0000`, with exact contents `## Landed changes\n- ` followed by backtick, T, backtick, ` blob\n`. No SOURCES registry or errata is needed.
4. Invoke the pinned auditor with `python3 tools/report-landing-audit.py --lane-repo LANE --fleet-repo FLEET --branch master --lane kama --rounds 1 --no-errata --json`, setting TMPDIR to owner scratch for every subprocess. Keep every Git inspection isolated with `--no-lazy-fetch`.

Independent expected result: **exit1**, exactly one uncorrected pair **(`landed-unresolved`, `21bd0dfe3d72f64c2925c528132fc310c6678dd3`)**; no unresolved-full-hash (the full blob exists in one audited store), no landed-omitted (seed commits are not round/lane matches), no errata findings, and no unknown/exit2. The pinned lane-first implementation is inferred to refuse instead.

Mirror the physical presence in a separately created fixture: write those same blob bytes to lane only, not fleet; fleet still holds the report. The correct exact pair and exit stay identical. This exercises wrongtype-first versus absent-first while preserving lane/fleet audit roles. Do not merely swap CLI repository arguments, which would move the report and change the question. The direct helper measurement already observed both store iteration orders; neither CLI variant is claimed run here.

No production patch prepared. AuditRepair-2 remains sole correction owner per L1 direction.
