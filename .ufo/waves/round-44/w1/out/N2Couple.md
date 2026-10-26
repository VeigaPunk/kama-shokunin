# N2Couple — round-44 cross-claim coupling scan (C1 ⇄ C2)

**Verdict: C1 and C2 are causally separable — no file is read by both counters
and neither claim's write set intersects the other counter's read set; both
separability controls pass (C1-only tree leaves C2 met=False byte-identical to
base; C2-only tree leaves C1 met=False byte-identical to base).**

## Evidence

### 1. File-read surfaces (from the frozen counters, lane `77d1bbf5`)

- C1 counter (`tools/round44-release-recheck-audit.py`): `corpus/SOURCES.md`
  at BASE for the population (`show(repo, BASE, SOURCES)`, L267) and at TIP
  for the section (`L306`); `registry/release-recheck-b11889.tsv` at TIP
  (`L273`); used-by `corpus/knowledge/*.md` at TIP for valid drifted/removed
  rows (`L316-331`, regex `L324`); upstream llama.cpp objects at the pin and
  `d854d98b` (`L193-206`, `L272`).
- C2 counter (`tools/round44-verdict-ledger-audit.py`): `registry/verdict-ledger.tsv`
  at TIP (`L137`); `SCORECARD.md` at TIP (`L217`, `## Axes` calibration-row
  cite `L240-246`); fleet `.ufo/reports/round-N/kama.md` at `b0fd7b7f` and
  lane `corpus/lessons/round-N-verifier-spotcheck.md` at BASE `9d9cc93`
  (`side_spec`, `L110-113`, `L133`).

### 2. Write sets

- C1 writes: `registry/release-recheck-b11889.tsv`; `corpus/SOURCES.md`
  (round-44 section + rows S482/S483 — S483 drafted by S9D2Row, including one
  clause in `corpus/knowledge/runtime-health-surface-processes.md`); knowledge
  flags (draft has zero drifted/removed rows → no flags needed).
- C2 writes: `registry/verdict-ledger.tsv`; `SCORECARD.md` (`### Round-44
  calibration ledger` section + `## Axes` calibration row).

### 3. Shared files

Full incidence (read/write per claim):

| File | C1 read | C1 write | C2 read | C2 write |
|---|---|---|---|---|
| `corpus/SOURCES.md` | yes (BASE+TIP) | yes | no | no |
| `registry/release-recheck-b11889.tsv` | yes (TIP) | yes | no | no |
| `corpus/knowledge/*.md` | yes (TIP) | yes | no | no |
| `registry/verdict-ledger.tsv` | no | no | yes (TIP) | yes |
| `SCORECARD.md` | no | no | yes (TIP) | yes |
| fleet reports / lane lessons | no | no | yes (frozen) | no |
| upstream llama.cpp objects | yes | no | no | no |

**No file is shared between the claims**: no file is written by both, and no
file written by one claim is read by the other's counter. The only shared
objects are the lane clone and the `--tip` commit — structural, not causal.
Prediction: each claim's files alone leave the other counter in its base state.

### 4. Controls run (scratch `/fast/scratch/hyaku/kama-r44/N2Couple`, clones at base `9d9cc93`)

Baseline on pristine base clone — both counters:

```
$ python3 tools/round44-release-recheck-audit.py --repo <base> --tip 9d9cc93... --upstream <up> --out base.c1.out
pop=91 rows=0 valid=0 unverified=91 unchanged=0 holds=0 reworded=0 drifted=0 removed=0 flags_missing=0 section=0 met=False   (exit=1)
$ python3 tools/round44-verdict-ledger-audit.py --repo <base> --tip 9d9cc93... --fleet <fleet> --out base.c2.out
rows=0 valid=0 missing=204 bad=0 agree=0 overclaim=0 underclaim=0 other=0 absent=0 table_missing=0 table_extra=0 summary=0 axes=0 met=False   (exit=1)
```

Both reproduce the preregistration `controls.base.*` values exactly.

Control A (C1 files alone; tip `a759e4e2bf3d0451e72a0c106312fa3feed7ffd4` = base + draft C1 ledger + SOURCES section heading + S482 row):

```
$ python3 tools/round44-release-recheck-audit.py --repo <a> --tip a759e4e2... --upstream <up> --out A.c1.out
pop=91 rows=91 valid=85 unverified=6 unchanged=4 holds=81 reworded=0 drifted=0 removed=0 flags_missing=0 section=1 met=False   (exit=1; the 6 invalid rows are the draft's TODO rows)
$ python3 tools/round44-verdict-ledger-audit.py --repo <a> --tip a759e4e2... --fleet <fleet> --out A.c2.out
rows=0 valid=0 missing=204 bad=0 ... summary=0 axes=0 met=False   (exit=1)
$ diff <(tail -n +2 base.c2.out) <(tail -n +2 A.c2.out)   # empty — A.c2 ≡ base.c2 modulo tip line
```

PASS: C1 files alone leave C2 met=False byte-identical to base.

Control B (C2 files alone; tip `3cd65aa254cbc94272fd6c7d813a1234d922b8d1` = base + draft C2 ledger + placeholder scorecard section):

```
$ python3 tools/round44-release-recheck-audit.py --repo <b> --tip 3cd65aa2... --upstream <up> --out B.c1.out
pop=91 rows=0 valid=0 unverified=91 unchanged=0 holds=0 ... section=0 met=False   (exit=1)
$ python3 tools/round44-verdict-ledger-audit.py --repo <b> --tip 3cd65aa2... --fleet <fleet> --out B.c2.out
rows=204 valid=204 missing=0 bad=0 agree=61 overclaim=3 underclaim=8 other=15 absent=15 table_missing=26 table_extra=0 summary=0 axes=0 met=False   (exit=1)
$ diff <(tail -n +2 base.c1.out) <(tail -n +2 B.c1.out)   # empty — B.c1 ≡ base.c1 modulo tip line
```

PASS: C2 files alone leave C1 met=False byte-identical to base. (The C2 draft
ledger itself is 204/204 valid; only the scorecard legs are missing in the
stand-in, leaving C2 met=False on its own tree — the integration's scorecard
section supplies those.)

## Findings / notes for integration

- No defect found in the separation surface. Keep the C1 commit free of
  `SCORECARD.md` and `registry/verdict-ledger.tsv` edits, and the C2 commit
  free of `corpus/SOURCES.md`, `registry/release-recheck-b11889.tsv`, and
  `corpus/knowledge/*.md` edits; the controls assert this.
- At integration, rerun both controls with the final files (steps in
  `N2Couple/plan.md`); assertion is the two empty `diff` commands.
- No tool installs made (git/python3 already present; no pacman, no uv/npm).

Receipts (copies): `base.c1.out`, `base.c2.out`, `A.c1.out`, `A.c2.out`,
`B.c1.out`, `B.c2.out`, `diff-A-c2-vs-base.txt`, `diff-B-c1-vs-base.txt`,
`diff-A-c1-vs-base.txt`, `diff-B-c2-vs-base.txt` — all in this directory and
in `N2Couple/`.
