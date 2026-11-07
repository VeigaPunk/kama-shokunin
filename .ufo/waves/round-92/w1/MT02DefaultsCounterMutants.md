# Round 92 w1 — MT02DefaultsCounterMutants (C1 counter mutation probe)

## Scope

Mutation-tested `tools/round92-server-defaults.py` (C1 counter, blob `a49e8984bb1e90274b7ee123e027ff2f8a858e26d3c7e3e5a414c8f5f02101f6`,
identical at F `309eadaf`, M2 `fa8aedb7` and M1 `18153ebb`) with 23 single-point mutants covering B1–B7, H1–H3,
the supersedes rule (gate + id set + membership filter), the duplicate rule, `MIN_ROWS`/`MIN_ENGINES`/`MIN_HELP`
and the `MOVING` list, then graded survivors with purpose-built fixtures. No frozen predicate was attacked or
changed; nothing was written to the lane except this file and my out dir.

## Commands and outputs

Scratch `/fast/scratch/hyaku/kama-r92/MT02DefaultsCounterMutants/`, TMPDIR exported to it, one `--shared` clone
(`git rev-parse --show-toplevel` = scratch/wt) detached at M1 `18153ebb5f9e2ae83f53e7fef57ee579bc409331`.

| # | command | exit | output |
|---|---|---|---|
| 1 | `python3 out/c1-mutbattery.py … --counter <pristine>` | 0 | `C1_MUTBATTERY cases=10 as_expected=10` (3.35 s; P0/P1/V7 exit 0, V1–V6 exit 1, V8 exit 2) |
| 2 | `python3 out/mutants.py --work …` | 0 | `MUTANTS total=23 killed=6 survived=17` (15 s wall) |
| 3 | `python3 out/grade.py --work …` | 0 | `GRADE total=23 killed=6 exit_masked=1 survived=16` |
| 4 | `python3 out/c1-discriminators.py … --counter <pristine>` | 0 | 15 fixtures, every one exit 1 for exactly its targeted `why=` (3.4 s) |
| 5 | same, `--counter work/mutants/M*,py` (17 runs, -P4) | 0 | 16 mutants hit ≥1 discriminating fixture; M18 hits none |
| 6 | `python3 <lane>/.ufo/waves/round-92/controls/c1-forgeries.py …` (restored bytes) | 0 | `C1_FORGERIES cases=9 as_expected=9` |

Restoration: lane counter/SKILL/SOURCES sha256 after all runs = before (`a49e8984…`, `fee65caf…`, `2c639663…`);
the mutation base is byte-equal to the lane blob (`diff -q` clean). Each mutant is one hunk, one `-`/`+` line
(`mutants.diff`). Host load during runs: load average 45.31 / 41.78 / 40.87 (`uptime`, 21:55). No tool installed.

## Findings

**F1 DEFECT (control coverage, not the counter).** The frozen battery cannot tell a counter *with* a rule from one
*without* it: 16 mutants leave all ten cases byte-identical — fifteen rule losses (B1, B3, the three B4 legs
moving-ref/pin-in-url/engine-in-url, B5, B6, B7, H2 loosened from `/tools/server/` to `/tools/`, the duplicate-pair
rule, `MIN_ROWS`, `MIN_ENGINES`, `MIN_HELP`, the `MOVING` entry, the `SUPERSEDE` membership filter) plus M18, which
is equivalent (F3). Every one is discriminated by an executed fixture that
flips the exit 1 → 0 (`mutation-matrix.md`): B1→X04, B3→X10, moving-ref→X06 (also kills M22), pin→X11, engine→X12,
B5→X07, B6→X08, B7→X09, H2→X13, duplicate-pair→X05, `MIN_ROWS`→X01, `MIN_ENGINES`→X02, `MIN_HELP`→X03,
membership→X15.
The four legs that catch exactly a K2 "row misstates its source" claim — source status/tier, sha256 pin,
literal-at-line, name-in-literal — therefore have *zero* control coverage in the pre-freeze battery
(`battery-pristine.log`, `disc-pristine.out`). The plan does not claim otherwise; the coverage gap is real and
should be closed by adding X01–X15 to `controls/` in a later round, not by editing the frozen counter.

**F2 DEFECT (exit-only grading has a false-negative class in this battery).** V5 and V6 expect exit 1, but their
rows also drop `help_checked` 7→6 and `supersedes` 14→13, so the exit is satisfied by `MIN_HELP` alone even when the
rule under test is gone. Proof: M14 (`H3` `llama-flag-not-option` return removed) makes the V6 row *bind*
(`bound=14→15`, `unbound=1→0`, `why=llama-flag-not-option` gone) and V6 still exits 1 → exit-identical to pristine
(`battery-logs/battery-M14.log`, V6 line: `bound=14→15`, `unbound=1→0`, exit 1). Fixture X14 restores `help_checked=7` and kills M14 by exit (1→0). Consequence for
this probe's own rule: "any battery case changes exit" under-reports; `grade.py` adds the `SERVER_DEFAULTS` line
comparison and is what surfaces M14.

**F3 NOTE (equivalent mutant).** M18 removes `dup == 0` from the `met` expression and no fixture distinguishes it,
including X05 (`duplicates=1`): a duplicate row is skipped, so `bound == n` already fails. The clause is redundant,
not an untested requirement. Removing it would be a behaviour-preserving simplification; leaving it costs nothing.

**F4 NOTE (what the real table actually exercises).** At M1 the real 15-row table changes exit only under M03
(unsigned `NUM_RE`) and M12 (unsigned `default:` regex), both via R05's `-1 (off)` value; every other rule mutation
leaves `P1-real-M1` at exit 0. Reproduced predicate at M1: `rows=15 bound=15 unbound=0 duplicates=0 engines=3
fetch_failures=0 help_checked=7 help_disagree=0 supersedes=14`, exit 0.

**F5 NOTE (positive control on the counter itself).** All 15 fixtures fail on pristine bytes for their named
reason, so the survivors in F1 are battery blindness, not missing counter logic: X04 `empty-cell`, X05 `duplicate`,
X06 `moving-ref`, X07 `sha-mismatch`, X08 `literal-not-at-line`, X09 `name-not-in-literal`, X10
`source-status=mined/tier=C`, X11 `pin-not-in-url`, X12 `engine-not-in-url`, X13
`derived-default-not-entry-point`, X14 `llama-flag-not-option`, X01/X02/X03/X15 by threshold
(`disc-pristine.out`). No mutation made the counter accept a row it should reject *on the real table*; the disclosed
V7 limit is untouched by this probe.

**F6 NOTE.** Nothing here falsifies C1: the counter is unchanged, the predicate reproduces at M1, and the restored
frozen controls are 9/9. The defects are in the *evidence strength* of the pre-freeze battery, which is what F1–F2
quantify.

## Deliverables

In `.ufo/waves/round-92/w1/out/MT02DefaultsCounterMutants/`:
`c1-mutbattery.py` (10-case battery, `--counter` parameterized, adds `P1-real-M1`), `mutants.py` (23 mutants +
run), `mutants.diff`, `mutants.sha256`, `mutation-matrix.md`, `results.json`, `grade.py` (exit + field regrade),
`c1-discriminators.py` (15 fixtures X01–X15), `disc-pristine.out`, `disc-out/M*.out` (17 runs),
`battery-pristine.log`, `battery-logs/` (pristine + 23 mutant runs), `grade.out`, `mutants-run.out`,
`battery-baseline-run.out`, `frozen-controls.out`. The mutant run and the field regrade were reproduced from a second
clone after scratch cleanup with identical counts (6 killed / 1 exit-masked / 16 survived).

VERDICT: partial — C1's predicate reproduces at M1 on the frozen bytes and every probed rule is live, but the 10-case battery is exit-identical for 16/23 mutants (15 real rules + 1 equivalent) and sees one H3 loosening only in the summary line (M14).
