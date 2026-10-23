# Defect 6 — round-25 SCORECARD trend correction

## Frozen line evidence

Revision: `a23c0e042114016a909eb15173aa6df74b5b7eb0`.

`SCORECARD.md:1306-1309`:

> 1306: Trend reading by the author: expansion improved (one entry on uncovered
> 1307: ground, one capability), quality unchanged-to-improved (routed wording and
> 1308: count corrections, KQ36), discernment improved (five attack findings turned
> 1309: into stricter counters, scoped claims and a filed axis dispute). Outside

Supporting verdicts:

- Fleet round-25 report `.ufo/reports/round-25/kama.md:120-126` says `quality: unchanged`; lines 127-129 say `discernment: unchanged`.
- Frozen closure `corpus/lessons/round-25-verifier-spotcheck.md:187` says `Quality: unchanged`; line 194 says `Discernment: unchanged`. Lines 200-201 explicitly state that the SCORECARD trend line contradicts the report, which says both are unchanged.

## Exact text to append to `SCORECARD.md`

```markdown
## Round 26 correction — round-25 trend verdicts (2026-10-23)

The round-25 trend line quoted above conflicts with the round-25 report and closure: the report records quality unchanged (`.ufo/reports/round-25/kama.md:120-126`) and discernment unchanged (`:127-129`); the closure records quality unchanged (`corpus/lessons/round-25-verifier-spotcheck.md:187`) and discernment unchanged (`:194`).

Correction: the round-25 trend verdicts are **quality unchanged** and **discernment unchanged**. Expansion remains improved. The earlier “quality unchanged-to-improved” and “discernment improved” wording is withdrawn. This correction is appended; the earlier scorecard bytes remain unchanged.
```

## Check performed

Read the frozen SCORECARD lines and the report/closure verdicts cited above. This is a proposed append-only correction, not an applied SCORECARD edit.