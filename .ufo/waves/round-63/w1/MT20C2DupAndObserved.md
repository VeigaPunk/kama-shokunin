# MT20C2 - C2 counter mutation probe (dup-row, observed-forgery, quote floor)

Seat: MT20C2DupAndObserved (mutation-tester, leaf). Judged on calibration. Milestone: falsify C2 counter.
Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (lane HEAD, freeze amendment 1).
Counter under test: tools/round63-c2-counter.py. Mutants committed only in my scratch clone
(never in the lane; no lane git/jj mutation). No tools installed.

## Verdicts

| mutant | change in counter `score()` | live counter, tip-bound | control family that escapes | verdict |
|---|---|---|---|---|
| a | delete `errs.append(f'dup-row:{cap}')` (the `continue` kept) | controls_rejected=11/12 | `duprow` | KILLED |
| b | delete the observed-forgery mismatch block (3 lines) | controls_rejected=11/12 | `observed` | KILLED |
| c | `len(row['quote']) < 8` clause removed | controls_rejected=12/12, no escape | none | SURVIVED |

**(c) SURVIVED is the prominent finding:** no control family exercises the 8-char quote floor.
The `quote` control uses NOT-A-PREFIX-QUOTE, which fails the `not in prefix` clause before the
length clause is ever reached. A mutant that accepts an empty or 6-char quote scores exactly like
the real counter.

## Caveat: `met` does not discriminate at this tip

The unmutated baseline itself prints `met=False`, because `selfdesc_mismatches=8` at 03a6 (the
freeze says this is intentional until L1 re-derives the SCORECARD head). Therefore:
- every run, including the unmutated one, prints `met=False`;
- discrimination below uses the per-control `control-escape:` lines on stderr, the
  `controls_rejected` count, and the absence of `note: baseline not met` (the baseline gate).
- For mutant (c), the `met=False` is caused only by `selfdesc_mismatches=8`. Every other gate term
  in its printed line is satisfied (covered 12/12, mismatches 0, errors 0, dead 0, sens 4/4,
  sensitive 12/12, controls 12/12, canonical 63). [DERIVED from printed fields; not separately
  run.] Once selfdesc reaches 0, mutant (c) would print met=True.

## Live runs (verbatim counter output; the counter launched the lane's live tools on unregistered loopback ports)

Runner: `cd <worktree>/tools && python3 round63-c2-counter.py --repo <clone> --tip <rev> --work <scratch>`.
Worktrees: detached at 03a6 (base), 57eadc64 (a), 2c11cd0c (b), 6923f541 (c). Each worktree's tool
bytes were checked against its commit before the run.

- base (03a6a1d8, unmutated):
  `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False`
  stderr: empty (no control-escape, no baseline note).
- a (57eadc64):
  `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=11/12 errors=0 met=False`
  stderr: `control-escape: duprow {'met': True, 'hit': False, 'tags': []}`
- b (2c11cd0c):
  `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=11/12 errors=0 met=False`
  stderr: `control-escape: observed {'met': True, 'hit': False, 'tags': []}`
- c (6923f541):
  `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False`
  stderr: empty.

`host_busy=1` in every run: context-capacity-receipt returned the declared host-busy outcome.
The live scorer for every bound row returned its recorded verdict, and the sensitivity flips held
(sensitive=12/12).

## Mutant (a): remove the dup-row error record - KILLED by `duprow`

Patch (receipt: out/MT20C2DupAndObserved/mutant-a.patch):
```
-            errs.append(f'dup-row:{cap}')
```
The duplicate is still skipped (`continue`) but silently. Escape confirmed live and in-process.

In-process discriminator (harness.py, live scorer replaced by recorded verdicts; all other code is
the committed counter): mutant a gives `duprow met=True tags=[]` (ESCAPE); the other 11 controls
hit. Variant a1 (whole `if seen[cap] > 1` block deleted, so the duplicate is scored) also escapes
`duprow` (`met=True tags=[]`), so it is also KILLED.

Limit of the kill: the `duprow` probe appends an IDENTICAL copy of row 0. With the mutant, a
planted conflicting duplicate (second sources-registry row with a bogus run and a valid verdict,
scored only) is accepted: `nonident-dup a covered=12/12 mismatches=0 errors=0 is_met=True`.
The mutant is killed only because the identical-copy probe happens to expose the missing record.
No control family probes a conflicting second row. (a1 instead scores it and reports
`run:sources-registry`.)

## Mutant (b): remove the observed-forgery mismatch - KILLED by `observed`

Patch (receipt: out/MT20C2DupAndObserved/mutant-b.patch): removes the three lines
`if row['observed'] and row['observed'] not in (want_obs or '') \ and row['observed'] not in observed:` and
`facts['mismatches'] += 1`.
Live: `control-escape: observed {'met': True, 'hit': False, 'tags': []}`, controls 11/12.
In-process: `observed met=True tags=[]` (ESCAPE); all other 11 controls hit.
The real registry is unaffected (`mismatches=0` on the real rows: their observed cells equal the
pattern or the declared alt), so only the forgery control can expose the removal, and it does.

## Mutant (c): accept a quote shorter than 8 chars - SURVIVED

Patch (receipt: out/MT20C2DupAndObserved/mutant-c.patch):
```
-        if row['quote'] not in prefix or len(row['quote']) < 8:
+        if row['quote'] not in prefix:
```
Live: `controls_rejected=12/12 errors=0`, no `control-escape` line, no baseline note. The only
failing term is `selfdesc_mismatches=8`, which the unmutated run shares (see caveat). Nothing in
the counter's control set distinguishes (c) from the real counter.

Planted quote rows (scored only, same harness; real registry otherwise; receipts in inproc.out):

| planted row | base | mutant c |
|---|---|---|
| quote `Curate` (6 chars, a substring of the prefix) | covered 11/12, `quote:sources-registry`, is_met=False | covered 12/12, errors=0, is_met=True |
| quote `` (empty; `'' in prefix` is always true) | covered 11/12, `quote:sources-registry`, is_met=False | covered 12/12, errors=0, is_met=True |

Why no control catches it (by reading the code): the `quote` control's only quote is
NOT-A-PREFIX-QUOTE, rejected by `not in prefix`; the length clause is never the reason. A probe that
would kill (c) needs a quote that IS a substring of the prefix but shorter than 8 characters, with
the expected tag `quote`. [INFERENCE: such a probe would kill (c); I did not build or run it, since
control families are frozen for this round and the L1 decides any addition.]

## Other notes

- Scoring-core summary (in-process, base): covered 12/12, mismatches 0, errors 0 on the real
  registry; base planted cases reject as expected (`dup-row`, `quote`).
- Mutant b leaves `want_obs` unused; this has no effect on the verdict.
- Working tree of the lane has other seats' uncommitted changes (PROVINCE.md, corpus/*, .ufo/waves/round-63/source/,
  w1.ready). Not mine; untouched by this seat.

## Receipts (.ufo/waves/round-63/w1/out/MT20C2DupAndObserved/)

- base.out / base.err, a.out / a.err, b.out / b.err, c.out / c.err: live counter output and stderr.
- inproc.out / inproc.err: in-process discriminator (fake scorer, per-control tags, planted rows).
- harness.py: the discriminator; variant_a1.py: the a1 variant source.
- mutant-a.patch, mutant-b.patch, mutant-c.patch: diffs against 03a6 (commits 57eadc64, 2c11cd0c, 6923f541 in the scratch clone; not in the lane).

## Tally

`MT20C2 mutants: a=KILLED(duprow) b=KILLED(observed) c=SURVIVED(no control family) | counter at 03a6: base controls_rejected=12/12 errors=0 met=False(selfdesc=8); a=11/12; b=11/12; c=12/12`
