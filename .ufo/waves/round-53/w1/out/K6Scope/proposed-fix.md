# K6Scope — proposed corrections (documentation-level; no lane file edited)

## 1. Surface qualifier for the round-53 calibration reporting (smallest safe correction)

The C2 claim's type string already names its surface ("every repository path the lane's
SCORECARD.md, SHONEN.md and SKILL.md cite as evidence"). The risk is at the reporting
layer, where the plain reading of "self-assessment matched to repo state" and the
calibration 7->7 score can be read lane-wide. Suggested addition to
SCORECARD.md §Round 53 (one sentence, append-only spirit):

> C2's cited-path counter surveys only the three standing self-description surfaces
> (SCORECARD.md, SHONEN.md, SKILL.md); a seat run of the same frozen parser over
> LOG.md, corpus/README.md, corpus/QUALITY.md, corpus/knowledge/*.md and
> corpus/lessons/*.md at the build commit counts 141 further unresolved citation
> tokens (135 unique) outside that surface — 28 of them in living documents — which
> this claim does not cover and does not certify. See
> .ufo/waves/round-53/w1/out/K6Scope/ for the per-file table.

And a matching Mistakes/Errata row for corpus/lessons/round-53.md:

> The cited-path instrument's disclosure ledger is keyed to its three surfaces;
> misses on any other file cannot be disclosed by a ledger row (the counter flags
> such a row "unknown surface"). The same dead token fixed on a covered surface can
> persist adjacent: `scripts/local-helper.mjs` was corrected in place at SKILL.md
> line 113 while corpus/knowledge/consumer-registry.md lines 42,47 and
> corpus/knowledge/listener-census.md lines 118,176 still cite it dead; the build
> discloses `.ufo/watchdog.log` and `tools/server/server-schema.cpp` for SCORECARD.md
> while LOG.md lines 1105,1795 and corpus/README.md lines 232,426,501,685,686 still
> cite them dead.

## 2. Round-54 candidate claim (if the lane wants the axis rubric's full spirit)

Widen `SURFACES` in a NEW frozen counter (round53's counter stays frozen) to
LOG.md, corpus/README.md, corpus/QUALITY.md and corpus/knowledge/*.md — deliberately
NOT corpus/lessons/*.md (round-frozen historical documents; 113 of the 141 off-surface
misses live there and are expected drift, never-adopted proposals, or use-mention of
dead paths). Two new ledger classes are needed for the living docs:

- `sibling-checkout` — a path of another local project checkout (ufo-fsd-alpha's
  `scripts/local-helper.mjs`, `tests/local-helper.test.js`), evidenced like
  `upstream` but by a pinned local path that exists on disk;
- `mention` — a dead path cited as the object of discussion rather than as evidence
  (corpus/README.md:501 quoting SCORECARD's absent c2-tip.json), evidenced by the
  citing line's own text.

With those, the living-doc residue this seat measured is 28 occurrences (3 LOG.md,
5 corpus/README.md, 2 corpus/QUALITY.md, 18 corpus/knowledge/*.md), of which under the
wider instrument: 9 upstream-class, 4 sibling-checkout, 2 untracked-class
(.ufo/watchdog.log), 1 mention, 2 range-notation, 4 genuine drift
(consumer-registry.md:325 `tools/janitor_auth.ts`, consumer-registry.md:330
`scripts/vendor/scihub-paper-downloader.py`, context-capacity.md:238
`corpus/evidence/round10-fleet/r10-scout-endpoint.md`, free-tier-provider-limits.md:65
`.ufo/round-6..9/telemetry.json`), plus 1 anchor drift in a living re-verification
document (corpus/lessons/round-36-verifier-spotcheck.md:88 `README.md:550` is past
EOF at the build).
