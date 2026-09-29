# kama-shokunin — Promotion checklist

Promotion to shokunin requires all of:

- [x] SKILL.md contains real decision tables, error patterns, checklists, cited sources
      → `SKILL.md` (315 lines): 12-row decision table, 11-row verbatim error-signature
      table, 13-item runnable checklist (first item = `bash tools/kama-probe.sh check`),
      11 anti-patterns each with an observed symptom, 47 `path:line` citations.
- [x] At least one end-to-end domain task executed and logged in LOG.md
      → round 1: the drift was detected, measured and reported end-to-end; the gate
      `check` run returns `registry_rows_evaluated=11 model_ok=3 drift=8 exit=2` on the
      live box, and the six mutation classes were executed against the shipped build
      (`LOG.md` §round 1).
- [x] Instructions executable by an agent without oral context
      → the checklist is command-based and host-local; `corpus/knowledge/endpoint-identity.md`
      defines the verdict precedence so an agent can re-derive every row. Verified by
      two subagents who ran the artifact from the written instructions alone.
- [x] No cross-domain bleed (PROVINCE.md still accurate)
      → `PROVINCE.md` now names the owned surfaces **and** a hard write boundary; contested
      scope is arbitrated in `corpus/knowledge/cross-lane-scope.md`. Out-of-province
      findings (bench-arena metrics scrape, LAN `/tmp` listing, DevTools port, credential
      brokers) are reported in `LOG.md`, not absorbed.

**Promotion not claimed.** `MINT.md` §Probation requires ≥3 verified rounds building
`corpus/` + `PROVINCE.md` before the operator adds a `MANIFEST.json` roster row; round 1 is
the first. The checklist boxes above describe evidence that exists, not a promotion call.