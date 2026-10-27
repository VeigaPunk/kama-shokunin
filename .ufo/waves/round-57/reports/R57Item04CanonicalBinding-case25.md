# R57Item04CanonicalBinding — distinct case 25 (independent)

Axis context: lane `shokunin.conf`/SCORECARD assign operability + calibration; the
historical `MISSION.md` operability + freshness conflict is not resolved here.
Scratch only, no shared/source edits, no tool installation.

Case 25 claim under test: a canonical capability-row audit can be bound to the row
**content** at a revision — not to a typed count, a `maxN` constant, or an
instrument's self-description — and its omission control can be made to fail.

## Method

`canon-row-audit.py` derives the canonical table from the single highest-numbered
`**Capabilities — canonical list as of round N**` heading in the audited
`SCORECARD.md`, then binds every row to content at `--tip`: evidence path tokens
resolve via `git cat-file -e`, first-working round is ≤ N with a matching
`## Round <n>` heading, name + first round + `what` text match the
`## Capabilities` mirror in both directions, names and whole-row digests are
unique, and the supplied row set is diffed against the derived set to expose
`omitted`/`extra`.

Driver: `distinct-case-25.py` (scratch), receipts in the artifact directory.
Invoked as `python3 distinct-case-25.py`; exit 0, eight checks, eight passes.

```
case25 check=rev-base-b89bdab2          canon=round49@2844 rows=11 bound=11 met=True exit=0            verdict=PASS
case25 check=rev-tip                    canon=round49@2844 rows=11 bound=11 met=True exit=0            verdict=PASS
case25 check=tree-canonical-noop        canon=round49@2844 rows=11 mismatches=0 met=True exit=0        verdict=PASS
case25 check=tree-no-canonical          canon=round48@2789 rows=11 mismatches=2 met=False exit=1       verdict=PASS
case25 check=mutate-what-both           digest_moved=True met=True exit=0                              verdict=PASS
case25 check=mutate-mirror-only         met=False exit=1 mismatches=1                                  verdict=PASS
case25 check=drop-canon-heading         canon=round48@2789 rows=11 exit=1                              verdict=PASS
case25 check=no-mirror-fail-closed      exit=2 streams=present                                         verdict=PASS
summary checks=8 failed=0 met=True
```

Tips used: base `b89bdab2cc114735ec5d331c6c610134258f7864` (round-56 spot-check),
tip `7b74e2f2515a6f598918488fa5144658ff29925f` at receipt generation (an earlier
pass ran at `7c873d7b4e3839489a93d6334cdf93fe5d34d19f` with the same verdicts).

## Observed evidence

- **Two revisions, same table content.** `b89bdab2` and the tip each yield
  `canon=round49 rows=11 mirror=11 bound=11 met=True exit=0`, so the audit is not
  pinned to one commit and does not carry a typed row count.
- **Frozen control trees.** `controls/canonical-noop/SCORECARD.md` still holds the
  round-49 heading: `canon=round49 rows=11 mismatches=0 met=True exit=0`.
  `controls/no-canonical/SCORECARD.md` (round-49 canonical block removed) falls
  back to `canon=round48 rows=11` and reports `bind=9 mismatches=2 met=False
  exit=1`; the two failures are
  `mirror: row 'append-only-audit' ... 'what' text differs` and
  `mirror: row 'live-receipt-replay' ... 'what' text differs`. The count is
  unchanged at 11, so a count-based counter would pass here while the content
  binding correctly fails: the round-48 canonical wording of those two rows is
  not the round-49 mirror wording.
- **Row digest is content-addressed.** Rewriting the `sources-registry` `what`
  cell in both the canonical table and the mirror leaves `met=True exit=0` but
  moves the row digest (`digest_moved=True`); rewriting the mirror cell only
  yields `met=False exit=1 mismatches=1`. The verdict tracks bytes, not names.
- **Derived authority moves with the bytes.** Deleting the round-49 canonical
  heading falls back to `canon=round48@2789` and reports `mismatches=2 exit=1`
  against the round-49 mirror; no constant `49` is retained.
- **Fail closed.** Renaming `## Capabilities` makes the audit exit `2` with a
  `could-not-evaluate: no '## Capabilities' mirror section` on stderr, rather
  than printing a green line.
- **Omission control (differential).** In the companion harness, the do-nothing
  instrument prints `canonical_reads=0 ... met=True exit 0` and is rejected;
  removing one canonical row gives `omitted=1 met=False exit=1`; an empty row set
  gives `omitted=11 met=False exit=1`; a non-resolving evidence path and an
  unevidenced first-working round each cost exactly one bound row
  (`bind=10 met=False exit=1`).

Independent calibration cross-check (`c1-crosscheck.out`), derived with a
throwaway parser and not with any lane counter:

```
commit       rounds  maxRoundHeading  canonRound  canonRows  mirrorRows
b89bdab2     57              56          49         11          11
89dc4f52     57              56          49         11          11
7c873d7b     57              56          49         11          11
7b74e2f2     57              56          49         11          11
worktree     58              57          49         11          11
```

The frozen C1 claim says the counter reports `maxN=56` where `46` is expected.
`46` is not derivable from any of these revisions: the greatest `## Round`
heading is 56 and the highest canonical round is 49 with 11 rows. The only `46`
in the frozen set is the typed output of `controls/c1-noop.py`. The worktree row
differs only because another seat's uncommitted `## Round 57` section is present
(`git status`: ` M SCORECARD.md`, `+11` lines). Reported, not resolved.

## Inference / unresolved

- The content binding is real at the audited revisions: canonical and mirror agree
  name-for-name, and `what` text, evidence paths and round headings all re-derive
  at `b89bdab2`, `89dc4f52`, `7c873d7b` and `7b74e2f2`.
- The `no-canonical` divergence is a property of that deliberately truncated
  control tree (round-48 canonical text against a round-49 mirror), not a defect
  in the live lane. It is the case that separates content binding from count
  binding.
- `maxN=56` and the canonical row count (11) are different predicates and must not
  be conflated in the C1 repair; this seat does not propose or apply that repair.
- What case 25 does **not** show: that any row's capability *claim* is true, or
  that a row entered through a demonstrating round. Those are separate predicates.

## Artifacts

`.ufo/waves/round-57/w1/out/R57Item04CanonicalBinding/`:
`distinct-case-25.py`, `case25.out`, `case25/` (per-check receipts incl.
`rev-base.out`, `rev-tip.out`, `tree-canonical-noop.out`, `tree-no-canonical.out`,
`mutated-both.out`, `mutated-mirror.out`, `drop-round49-heading.out`,
`no-mirror.out`), `canon-row-audit.py`, `omission-harness.py`, `harness.out`,
`noop-omission-control.py`, `c1-crosscheck.out`, `baseline.out`,
`readonly-proof.out`.

Report: .ufo/waves/round-57/w1/out/R57Item04CanonicalBinding.md
