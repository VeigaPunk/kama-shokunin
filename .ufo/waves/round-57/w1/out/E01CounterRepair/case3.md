# E01CounterRepair — distinct case 3 evidence (independent fixture)

Separate evidence file for the seat's assigned distinct case. Independent of the
main fx1 repair fixture: a fresh clone at the frozen base, its own commits, its own
probe order. Axis lens: calibration (the counter's own output must be derived, not
asserted). Scratch root (removed after receipts were copied):
`/fast/scratch/hyaku/kama-r57/E01CounterRepair`. No lane source edits, no commits,
no installs.

## Setup (independent)

```
git clone -q --no-hardlinks <lane> /fast/scratch/.../fx2
git -C fx2 checkout -q b89bdab2cc114735ec5d331c6c610134258f7864
git -C fx2 rev-parse --show-toplevel   # asserted == fx2 before any fixture commit
git -C fx2 config user.email e01-case3@scratch.local
```

## P1. 46 is not derivable from the frozen tree

`receipts/fx2/derivations.out` (computed from committed SCORECARD bytes at b89bdab2):

```
max(^## Round N headings) = 56 (headings=57)
max(**Current authority (round N)**) = 56
highest canonical-list heading round = 49 (rows=11)
canonical first-working rounds = [10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47] (max=47)
stale round-46 canonical first-working rounds = [10, 14, 16, 20, 25, 30, 41, 42, 43, 46] (max=46)
no-op control literal maxN = 46
```

46 appears only in the do-nothing control literal and in the superseded round-46
canonical table (`**Capabilities — canonical list as of round 46**`). No live
derivation from the SCORECARD round headings, head authority, or selected canonical
table yields 46. The expected value in the frozen claim context is therefore the
no-op's fiction, not a tree-derived expectation.

## P2. The no-op control, executed

`receipts/fx2/noop-c1-executed.out`:

```
$ python3 .ufo/waves/round-57/controls/c1-noop.py (no --repo, no reads)
mismatches=0 maxN=46 met=True
exit=0
```

The source performs zero reads and prints the summary. Reproducing it proves only
that a literal can be printed, not that any counter leg holds.

## P3. The r41 leg is the only stale datum, and it flips causally

`receipts/fx2/r41-base.out` at b89bdab2:

```
axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=1 dead=0 score_bad=0 hollow=0 mismatches=1 met=False
detail: calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '42' (exit 0)
exit=1
```

One-token fixture commit (`42` -> `43` on the calibration row), then
`receipts/fx2/r41-repaired.out`:

```
axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=0 dead=0 score_bad=0 hollow=0 mismatches=0 met=True
exit=0
```

Committed blob count at the frozen base is 43 (`git ls-tree -r --name-only
b89bdab2 corpus/lessons | grep -c verifier-spotcheck.md` -> `43`), so 42 was stale
and 43 is the re-derivable value.

## P4. maxN is live, not a literal

`receipts/fx2/counter-round57-heading.out` — the repaired fixture plus an appended
`## Round 57 — E01 probe heading` line:

```
r41=0 banner=1 planned=2 ... mismatches=3 maxN=57 met=False
detail: banner: head lacks 'Latest measured round: 57'
detail: planned: section does not name '### Planned (round 58)'
exit=1
```

The derivation tracks committed bytes (56 -> 57) and the dependent banner/planned
legs move with it. This is why forcing 46 cannot be a repair.

## P5. Canonical row content binds (selection unchanged)

`receipts/fx2/counter-canonical-row-renamed.out` — one canonical row renamed in the
round-49 table (`hexrun-census` -> `hexrun-censusX`), head unchanged:

```
r41=0 ... caps=1 ... mismatches=1 maxN=56 met=False
detail: caps: head names [...] != canon (round 49) [... 'hexrun-censusX' ...]
exit=1
```

The counter selects the highest canonical heading (round 49, 11 rows) and compares
actual parsed row names; deleting or renaming a row is not a no-op.

## P6. Falsification probe: forced maxN=46

`receipts/fx2/forced46-tool-on-repaired.out` — scratch copy of the tool with
`maxn = 46` substituted for `maxn = max(rounds)`, run against the correctly repaired
fixture:

```
r41=0 banner=1 planned=1 ... mismatches=2 maxN=46 met=False
detail: banner: head lacks 'Latest measured round: 46'
detail: planned: section does not name '### Planned (round 47)'
exit=1
```

A repair that makes the counter print the claim's expected 46 loses two legs. The
claim target is therefore rejected on its own counter.

## P7. Advisory (not changed): equal-N duplicate canonical marker

`receipts/fx2/canon-duplicate-marker-probe.out`:

```
synthetic duplicate equal-N marker -> (57, [['stale-first', 'x', '1']])
live SCORECARD canonical markers: ['16','34','41','42','43','46','47','48','49']
duplicate marker rounds: []
exit=0
```

With two round-57 markers, the earlier (stale) table wins because `canon()` keeps
`N > best` rather than `>=`/last-occurrence-wins. This is latent, not triggered by
the live SCORECARD (no duplicate rounds). Binding canonical rows structurally is
E02's scope; this seat preserves the existing heading selection as instructed and
records the hazard without patching it.

## Case-3 verdict

The assigned case is independently reproduced: the stale value is the calibration
self-description count (42 -> 43), while `maxN=56` at the frozen base is correct and
the claim's `expected 46` is a no-op literal. The smallest repair is one token in
SCORECARD.md; no counter-script change is justified. Receipts copied here before
scratch removal.

Report: .ufo/waves/round-57/w1/out/E01CounterRepair.md
