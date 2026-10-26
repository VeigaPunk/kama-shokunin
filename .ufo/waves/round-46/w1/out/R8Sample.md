# R8Sample — round 46 w1 — independent KQ65 sample-overlap labels (rounds 24/25/28/31/40)

Verdict: **done** — 142 claim-outcome lines labeled across the 10 assigned documents (5 fleet reports, 5 lane closures) into `.ufo/waves/round-46/w1/out/R8Sample/sample.tsv`; every row's `text` was extracted verbatim by `git show` and passed a mechanical expect-substring guard (0 mismatches after 15 initial mis-slices were corrected); no other seat's output was read.

## Sources labeled

| side | path | rev |
|---|---|---|
| report | `.ufo/reports/round-24/kama.md` | fleet HEAD `8577d693b5fa67acead0fb68ddb6ae1cc9f8933f` (at labeling time) |
| report | `.ufo/reports/round-25/kama.md` | same |
| report | `.ufo/reports/round-28/kama.md` | same |
| report | `.ufo/reports/round-31/kama.md` | same |
| report | `.ufo/reports/round-40/kama.md` | same |
| closure | `corpus/lessons/round-24-verifier-spotcheck.md` | `4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050` |
| closure | `corpus/lessons/round-25-verifier-spotcheck.md` | same |
| closure | `corpus/lessons/round-28-verifier-spotcheck.md` | same |
| closure | `corpus/lessons/round-31-verifier-spotcheck.md` | same |
| closure | `corpus/lessons/round-40-verifier-spotcheck.md` | same |

Declared claims per round (from each document's own declaration): r24 C1 (calibration); r25 C1 (calibration, repair-first) + C2 (coverage K05 with capability); r28 C1 (depth, counted >= 18); r31 C1 (depth) + C2 (calibration) + C3 (operability); r40 C1 (calibration) + C2 (operability).

## Labeling rules (declared up front, applied uniformly)

Inclusion: a line is labeled iff it contains a finite verdict predicate about the round's declared claim(s) or one of their registered sub-clauses/components — met, not met/achieved, partial, unprovable/not proved/unverified, verified, admitted, or equivalent, in the document's own words.

Exclusions: work descriptions, evidence pointers, census/conformance/seat-logistics lines, verbatim command-output code blocks, before-values without a verdict, axis-trend lines that state no claim outcome, SHONEN boxes, routed-defect directives, and spot-check/gate-decision tables (they rule on sources, not the claim predicate).

Outcome mapping:
- `met` — verified/met/achieved as stated (incl. "matches the report", receipt-echoed met values in prose bullets).
- `not-met` — claim/leg false, failed, withdrawn, not achieved, or its rule invalidated (incl. "counter cannot separate", control-meets-target findings that break the claim's instrument).
- `partial` — supported on a finite/recorded subset with an explicit no-broader-certificate limit.
- `unprovable` — cannot be established/proved/verified; includes the corpus's "unverified" (r40) and composite "not achieved/unprovable in full" verdicts (resolved to the document's overall epistemic ruling; plain "not achieved" without unprovable wording → `not-met`).
- `mixed` — the line states more than one outcome facet (e.g., "met on the frozen counter; NOT admitted"; "C2 verifies; C1 remains unverified").
- `unprovable-but-better` — not used: no labeled line both rules the claim unprovable and credits a beyond-claim improvement (r40 closure L49's "substance is real" is explicitly "not credited", so it stays `unprovable`).

Phrasing class (one per row; precedence attributed > measured > scoped > hedged > flat):
- `measured` — verdict carries concrete instrument values/counts/exit codes/hashes in the same line.
- `attributed` — verdict stated as another named party's finding (seat/critic/re-run).
- `scoped` — verdict about one named sub-clause/component/case rather than the whole claim.
- `hedged` — verdict qualified as not established / not proved / cannot / does not net.
- `flat` — plain unqualified verdict.

Conventions: wrapped verdict clauses are labeled at the line carrying the finite predicate; multi-claim verdict lines use compound claim values (`C1+C2`, `C1+C2+C3`); internal tabs in `text` replaced with a space (none occurred in labeled lines).

## Evidence

Commands (all read-only; exit 0):

```
git -C /home/vgpnk/Projects/shokunin show HEAD:.ufo/reports/round-{24,25,28,31,40}/kama.md
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050:corpus/lessons/round-{24,25,28,31,40}-verifier-spotcheck.md
git -C /home/vgpnk/Projects/shokunin rev-parse HEAD   # -> 8577d693b5fa67acead0fb68ddb6ae1cc9f8933f
```

Extraction: each labeled line pulled by `git show <rev>:<path>` line index inside a Python builder; every row asserted to contain a pre-registered expect-substring (guards against off-by-one). First run: 127/142, 15 expect failures (mis-sliced line numbers) → corrected → second run: 142/142, 0 errors. Integrity re-check: `awk -F'\t' 'NR>1 && NF!=9'` → `rows=142 bad_field_count=0`.

Counts per document (rows labeled):

| doc | report | closure |
|---|---|---|
| r24 | 22 | 17 |
| r25 | 8 | 11 |
| r28 | 10 | 23 |
| r31 | 16 | 13 |
| r40 | 7 | 15 |

Outcome distribution: met 47, not-met 46, unprovable 25, mixed 17, partial 7. Phrasing classes: flat 70, measured 45, hedged 13, scoped 11, attributed 3.

## Scoped findings (from the labeling corpus only)

1. Outcome-vocabulary gap: the corpus uses "unverified" (r40 report L12/L14/L35, closure L33/L105) which the assigned outcome set lacks; mapped to `unprovable` per the rule above. If the L1's scribe labels treat "unverified" differently, that is a taxonomy divergence, not a labeling error.
2. Composite verdicts are frequent in r24 ("not achieved/unprovable in full" at report L5/L63/L100, closure L14) — single-outcome columns force a resolution rule; mine is documented.
3. r40 fleet report L43 carries the 39-hex digest `35ce313293052f8362e0829e7512bc9bc3d336c` (trailing `9` dropped); independently observed during labeling — already routed as closure N2/D4, no new action proposed.
4. r24 closure L61 is a blank line inside the "Observed:" paragraph block; wrapped-verdict labeling at the predicate line handles it (L58/L59 carry the facets).
5. No defect found in the two documents' line numbering or in the assigned revs; all 10 blobs exist at the named revs.

Tool installs: none (no pacman, no new tools). Scratch `/fast/scratch/hyaku/kama-r46/R8Sample` created for TMPDIR only and removed at the end; no receipts cited beyond the TSV itself.
