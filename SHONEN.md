# kama-shokunin — Promotion checklist

Promotion to shokunin requires all of:

- [x] SKILL.md contains real decision tables, error patterns, checklists, cited sources
      → `SKILL.md` has a 12-row decision table, verbatim error signatures,
      a 14-item runnable checklist, and 11 observed anti-patterns.
- [x] At least one end-to-end domain task executed and logged in LOG.md
      → round 1 shipped the live drift gate; round 2 shipped invocation history.
      Two live snapshots produced `rows=11 model_ok=3 drift=8 transitions=0 exit=2`,
      and `bash tools/test-snapshot.sh` exercised transition/recovery/containment
      behavior with `RESULT pass=24 fail=0` (`LOG.md` §§round 1–2).
- [x] Instructions executable by an agent without oral context
      → `SKILL.md` gives the commands and exit semantics;
      `corpus/knowledge/snapshot-history.md` defines persisted fields, transition
      semantics, redaction, corruption recovery, and the unscheduled boundary.
- [x] No cross-domain bleed (PROVINCE.md still accurate)
      → `PROVINCE.md` now names the owned surfaces **and** a hard write boundary; contested
      scope is arbitrated in `corpus/knowledge/cross-lane-scope.md`. Out-of-province
      findings (bench-arena metrics scrape, LAN `/tmp` listing, DevTools port, credential
      brokers) are reported in `LOG.md`, not absorbed.

**Promotion not claimed.** `MINT.md` §Probation requires ≥3 verified rounds building
`corpus/` + `PROVINCE.md` before the operator adds a `MANIFEST.json` roster row; round 2 is
the second. The checklist boxes above describe evidence that exists, not a promotion call.