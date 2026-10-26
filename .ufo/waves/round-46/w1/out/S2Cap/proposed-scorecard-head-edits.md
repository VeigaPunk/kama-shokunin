# Proposed SCORECARD.md edits that accompany the round-46 canonical capability table

Line numbers are those of `SCORECARD.md` at the lane commit
`4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050`. Every item below is forced by a leg of
a counter the lane already runs; the leg is named and the failing output is in
`receipt/`. Nothing here is stylistic.

`proposed.patch` carries items 1–5 (the capability entry and its consequences);
`proposed-calibration-reanchor.patch` carries item 6 alone (a pre-existing
defect, separable); `proposed-full.patch` carries both.

## 1. Mirror intro (line 117) — `round42-selfdesc-reconcile` reads the head mirror

```
-Mirror of the round-43 canonical capability list that §Round 43 carries (a mirror, not the canonical source: ...
+Mirror of the round-46 canonical capability list that §Round 46 carries (a mirror, not the canonical source: ...
```

Not counter-enforced (the leg compares names only), but leaving it at round 43
while the table mirrors round 46 is a false statement in the head.

## 2. Mirror row (append after the `hexrun-census` row, line 129) — leg `caps`

Byte-identical to the canonical row, so `caps` (head names == canon names) holds:

| append-only-audit | Set the lane's five append-only self-description files (SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md) against its git history: list every commit that deletes >= 20 lines from one of them, report how many of those lines the file holds again at the audited revision and which later commit first restored all of them, and exit 1 on a partial or unrestored mass deletion | `tools/append-only-audit.py`; `tools/round46-append-audit-check.py`; run `python3 tools/append-only-audit.py --repo . --to <commit> --json` | 46 |

Measured necessity: dropping this row alone leaves `capability-repertoire-audit`
green (`listed 10 observed 10 met True`) but makes `round42-selfdesc-reconcile`
read `caps=1 mismatches=1` (`receipt/13-…`, `receipt/14-…`).

## 3. §Retired (line 57) — leg `retired` wants `<len(canon)> capabilities`

```
-None. 6 axes and 9 capabilities remain active.
+None. 6 axes and 10 capabilities remain active.
```

## 4. §Saturation (line 135) — leg `saturation` wants `first-working rounds <sorted unique canon firsts>`

```
-capability first-working rounds 10, 14, 16, 20, 25, 30, 41, 42, 43 (highest canonical list)
+capability first-working rounds 10, 14, 16, 20, 25, 30, 41, 42, 43, 46 (highest canonical list)
```

Same paragraph, not counter-enforced, refreshed for accuracy:
`(kept current in round 43)` → `(kept current in round 46)`; `A capability entered in
round 43, so the window is not exhausted either.` → `A capability entered in round 46, …`.

## 5. §Axes coverage row (line 17) — leg `r41` hash: PROVINCE.md's digest

`PROVINCE.md` must gain the two new tool tokens (see `proposed-province-clause.md`),
so the digest the coverage row cites stops matching:

```
-PROVINCE.md sha256 36d6bb3ac93b1cc20e07969b373fd89d473fc476647f69c2f7e1ae4333a9b6aa (186 lines)
+PROVINCE.md sha256 659a5101ce0a8bc08d2c63a23d52049cd97e183d92f226568607ebf11bc9fc49 (186 lines)
```

The clause extends an existing PROVINCE.md line, so the line count stays 186 and
only the digest moves. Observed by `round42-selfdesc-reconcile` as
`r41=1 … sha256 PROVINCE.md cited 36d6bb3a… observed 659a5101…`
(`receipt/04-selfdesc-patch.out`); the digest is not cited in
`registry/digest-ledger.tsv`, so no ledger row changes with it.

## 6. §Axes calibration row (line 18) — pre-existing, separable, verified

At `4a2a4d55` the row cites `→ 31` while the tree holds 32
`corpus/lessons/*verifier-spotcheck.md`; the 32nd landed in `0163fea2` (round-45
verifier spot-check) *after* the round-45 measured commit `21945c61`, where 31 was
correct. `round42-selfdesc-reconcile` evaluates the run fact at the tip, so it reads
`r41=1` at both `4a2a4d55` and the lane tip `96d32918`, independent of this
capability entry (`receipt/02-selfdesc-baseline.out`).

```
-→ `31` (outside closures on record)
+→ `32` (outside closures on record; re-anchored round 46)
```

Verified: with it, `round42-selfdesc-reconcile` reads `mismatches=0 met=True`
(`receipt/10-selfdesc-full.out`).

## 7. Not in these patches (integrator-owned)

- Head banner `Latest measured round: 45` → `46` and a `### Planned (round 47)` item: both keyed to `maxN`, i.e. to the `## Round 46` section heading L1 writes (legs `banner`, `planned`).
- The `## Round 46` section body, claim rows, measured results, end census.
- Placement: the fragment goes inside that section, at end of file, below every earlier canonical marker. `capability-repertoire-audit` takes the first capability-shaped table after the highest-numbered marker; `round42-selfdesc-reconcile` `canon()` takes the first table after that same marker.
