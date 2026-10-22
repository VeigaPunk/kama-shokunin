# Advice: M17 / M33 mutation probe (C1 call-site coverage)

Verdict: M33-ref-shadow-bare-objects is KILLED by grid row F13 (exit 1); M17-ref-shadow SURVIVES the whole grid (exit 0, zero failing rows) and its check is unreachable from any input the audit can receive — the "both call sites stay covered" part of the C1 claim is not met by the current grid.

## What was run

Own clone at lane tip 1fc41e346853afd98cbd7010af5db4e54dc877f7 (git 2.56.0):
`/fast/scratch/hyaku/kama-r25a2/MutationM17M33Kill/clone`.

Grid: `python3 tests/report-audit/repo-state-grid.py --arm current --current <auditor> --json`
run three times, once per auditor (pristine, M17-mutated, M33-mutated). Mutation
instrument shapes taken from `tests/report-audit/isolation-mutants.py:81-87` (M17) and
`:117-123` (M33); each mutant is exactly the raise -> pass weakening of its registered
literal. The two mutant copies were made by copying the pristine auditor and changing
one line each.

Mutated files (hash before/after applied to copies):
- pristine `tools/report-landing-audit.py` sha256 `b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f`
- `auditor_m17.py` sha256 `44099ab947846be8632abe2344ffd5bfabd743f0832eacb492fa5dddb161817a`
  (line 275-277: `raise EvalError(... "names a ref")` -> `pass` in `lookup()`)
- `auditor_m33.py` sha256 `fe8ae79bbf6b185e072f51a3300765c1b86ba95d73854ebf59dd11526a4111f6`
  (line 212-214: same weakening in `bare_objects()`)

Anchor verification before running: M17 literal count 1, M33 literal count 1 in the
pristine auditor; after mutation each mutated file contains exactly one copy of its
mutated shape and exactly one copy of the other site's pristine shape.

## Results (recorded JSON in out/MutationM17M33Kill/)

Pristine: exit 0. faults 26/26, contracts 4/4, controls 14/14, violations 0.
M17: exit 0. faults 26/26, contracts 4/4, controls 14/14, violations 0.
  -> no row differs from pristine (`m17` vs `pristine` met-status diff: []).
M33: exit 1. faults 25/26, contracts 4/4, controls 14/14, violations 1.
  -> exactly one row differs from pristine: F13-ref-named-abbreviation.
  Under M33, F13 runs exit=0 (want 2), kinds=[] , stderr empty; expected
  `could-not-evaluate: ... citation deadbee1 names a ref`. F13 is not met.

(O01-alternates-foreign-object and O02-gitfile-redirect report NOT-MET in the pristine
run too; they are `open`-kind rows, excluded from `violations`, and are baseline
behaviour, not mutant effects.)

## Call-site coverage

- M33 call site (`bare_objects()` line 212-214): COVERED. F13 kills it. F13 is the
  round-23 ref-named-abbreviation fixture: the report lands section cites `deadbee1`
  (7-hex), the lane has tag `deadbee1` on commit `lc`; the peel path
  (`lookup(..., "^{commit}")` -> `bare_objects`, auditor line 246 and 550) resolves the
  ref and the startswith guard must refuse with `names a ref`. With the guard weakened,
  the audit completes exit 0 and the reason string is gone, so F13 fails.
- M17 call site (`lookup()` line 275-277): NOT COVERED; the mutant survives. The
  non-peel lookup (auditor line 538, `lookup(stores, full_tokens)`) receives only full
  40-hex tokens (FULL regex, line 90). For such a token git either resolves the object
  itself (parts[0] == token, startswith true, guard never fires) or answers `missing` /
  errors; a ref whose name is the full 40-hex token is not resolved by `cat-file
  --batch-check` to a different oid line. All abbreviation citations go through
  `lookup(..., "^{commit}")` (lines 550, 630), where the lookup-site guard is skipped by
  `if not peel` and M33's site is the active one. So no input the audit can receive
  makes the M17 raise execute: the surviving mutant is not killable by an added grid row
  of the registered element shape (the row that would be needed is the F13 shape, but
  with a 40-hex token, and probe runs show git returns `missing` for that token, so the
  guard still never fires). Demonstrated directly: a report citing a full 40-hex token
  that names a tag produces identical exit-1 results for pristine, M17 and M33 (probe
  fixtures with `- aaaaa...a` tag on lane commit; all three exit 1 with the same two
  defects). M17's element is effectively dead code in the current auditor against the
  current grid.

## Restoration evidence

The clone working tree was never edited; `tools/report-landing-audit.py` re-hashed
after all runs: sha256 `b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f`
(unchanged), M17/M33 literal counts still 1/1, HEAD still 1fc41e3, `git status
--porcelain` empty. Mutant copies live outside the clone in scratch; originals were
never touched.

## Files written

- `.ufo/waves/round-25/a2-build/advice/MutationM17M33Kill.md` (this report)
- `.ufo/waves/round-25/a2-build/out/MutationM17M33Kill/pristine.json`, `m17.json`,
  `m33.json`, `pristine.err`, `m17.err`, `m33.err`, `pristine.rc`, `m17.rc`,
  `m33.rc`, `auditor_m17.py`, `auditor_m33.py`

Tools installed: none.
