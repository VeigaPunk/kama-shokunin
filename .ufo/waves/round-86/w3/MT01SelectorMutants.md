# MT01SelectorMutants — w3 scoped report (C1 selector mutation beyond the committed driver)

Seat scope: mutate `tools/round86-rendered-cells.py`'s selector in a scratch copy of
`bafae7afb41843564ac2468d28beb8e0bb98e8e6`, run the same bounded detector (`--selftest`, 17 arms) on
pristine / mutated bytes. Full detail + diffs: `w3/out/MT01SelectorMutants/findings.md`; receipts:
`w3/out/MT01SelectorMutants/receipts/`, mutant sources `w3/out/MT01SelectorMutants/src/`.
Pristine identity: `sha256sum tools/round86-rendered-cells.py` →
`f9d36b5be0683fdc486da343f6c3aa2e140f250efc94c377ddda1a36ba6e633b`, equal to
`git show bafae7af…:tools/round86-rendered-cells.py | sha256sum`. Lane untouched:
`git status --porcelain tools/round86-rendered-cells.py` → 0 lines.

## Item 1 — committed driver: CONFIRMED

```
$ python3 .ufo/waves/round-86/measured/after/c1-mutants.py <copy>
… a-fence-off: exit=1 red_arms=fenced-shadow,tilde-fence-shadow,unclosed-fence-fails-closed
… i-backtick-info-off: exit=1 red_arms=backtick-info-not-a-fence
RENDERED_CELLS_MUTANTS mutants=10 killed=10 escaped=0      exit=0
```

Each of the 10 kills names a specific red arm (not merely exit 1). Baseline in the same run:
`RENDERED_CELLS_SELFTEST pass=17 fail=0`, exit=0.

## Item 2 — five new mutants (three killed, two survivors)

| id | rule disabled | edit | selftest | verdict |
|----|---------------|------|----------|---------|
| MA | column-0 on the authority paragraph | `AUTHORITY.match(line)` → `.match(line.lstrip())` | `pass=16 fail=1`, red arm **`indent-shadow`** (`mismatches=2 gate=1`) | killed |
| MB | column-0 on the calibration row | `CALIBRATION.match(line)` → `.match(line.lstrip())` | `pass=16 fail=1`, red arm **`indent-row-shadow`** (`mismatches=1 gate=0 closure=1 disposition=1`) | killed |
| MC | first top-level cell wins (accept a later duplicate authority line) | `if authority is None and AUTHORITY.match(line)` → `if AUTHORITY.match(line)` | `pass=16 fail=1`, red arm **`backtick-info-not-a-fence`** | killed **incidentally** — see below |
| MD | coupled assertion (token from a different paragraph) | `gate_fact(tree, authority, …)` → `gate_fact(tree, authority + "\n" + rendered(score), …)` | `pass=17 fail=0`, exit=0 | **SURVIVOR** |
| ME | row first-wins (accept a later duplicate calibration row) | `if in_axes and row is None and CALIBRATION.match(line)` → `if in_axes and CALIBRATION.match(line)` | `pass=17 fail=0`, exit=0 | **SURVIVOR** |

Survivor counterexamples (same fixture, pristine vs mutant):

```
MD  pristine: mismatches=1 gate=0  FINDING gate no coupled PRE_REPORT token in the rendered authority cell  exit=1
MD  mutated : mismatches=0 gate=1 closure=1 disposition=1                                                 exit=0
ME  pristine: mismatches=2 gate=1 closure=0  FINDING closure row names round-84 newest committed closure is round-85
ME  mutated : mismatches=0 gate=1 closure=1 disposition=1                                                 exit=0
```

MC's kill is not owned by its rule: deleting the single arm `backtick-info-not-a-fence` from the MC
source yields `RENDERED_CELLS_SELFTEST pass=16 fail=0`, exit=0 — the authority first-wins rule has no
arm whose subject is ordering. Probe P2 shows the rule is contract-load-bearing (stale banner first,
correct banner second: pristine `mismatches=1` exit=1 vs MC `mismatches=0` exit=0).

## Probe — "inside the FIRST `## Axes` section" is not enforced

Row moved to a second `## Axes` section, first section rowless: pristine prints
`RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1`, exit=0. Latent only (the live
SCORECARD has one `## Axes` at line 8, live row at line 18).

## Live-record consequence (mutants vs `--rev bafae7af…`)

pristine / MA / MB / MD → `mismatches=0` exit=0; **MC → `mismatches=1 gate=0` exit=1**;
**ME → `mismatches=2 closure=0 disposition=0` exit=1**. The terminal green depends on document-order
selection (≈25 historical top-level banners, 2 calibration rows in `## Axes` at lines 18 and 29).

## Record audit against committed bytes

- `after/c1.out` reproduced exactly at `bafae7af…` (`mismatches=0 … newest_gate=85 newest_closure=85`, exit 0);
  `after/c1-selftest.out` reproduced byte-for-byte modulo its `$ python3 …` prompt header (`pass=17 fail=0`).
- `newest_gate=85` is faithful: no `PRE_REPORT round=86` receipt exists under `.ufo/waves/round-86/measured/`.
- Arm expansion is disclosed (`SCORECARD.md:14` "17/0 at the terminal tree (11/0 at the freeze)"; LOG
  "the w2 falsification added six arms") and the freeze's 11 arms match `measured/before/c1-selftest.out`.
- **MISMATCH**: `corpus/lessons/round-86.md:59-60` cites "`RENDERED_CELLS_MUTANTS mutants=7 killed=7
  escaped=0`, `.ufo/waves/round-86/measured/after/c1-mutants.out`", but that path's committed bytes at
  the same revision read `RENDERED_CELLS_MUTANTS mutants=10 killed=10 escaped=0`; `7/7` was the
  receipt's content at `c5d71b7a`. SCORECARD correctly says 10.

## Verdict

Column-0 rules: armed and killed. Ordering and paragraph-coupling rules: **three survivors**
(MD, ME, and MC once its incidental killer is removed) — a control-discrimination gap in the 17-arm
battery that the graded artifact only partially masks (MC/ME flip it red, MD is invisible). Plus one
record-product mismatch (lesson 7/7 vs receipt 10/10) and one latent contract divergence
("first `## Axes` section").

Tools installed/upgraded: none (python3 stdlib). Scratch removed on exit; no git/jj mutation.
