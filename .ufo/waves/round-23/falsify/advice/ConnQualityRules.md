# ConnQualityRules — KQ34 draft (round 23 FALSIFY, connector seat)

Base: `245a37f69628c2c6bb29bbf17897d8fb5946c857` (clone
`/tmp/kama-r23w2/ConnQualityRules`, `git -C … rev-parse HEAD` → that hash,
exit 0). Seat: `CloseKama22.ConnQualityRules-2`. No tracked file was edited.

## Verdict: partially

KQ34's direction holds: it narrows KQ32's "demonstrated separately" into a
per-channel, per-element demonstration, does not supersede KQ32/KQ28/KQ33, and
is consistent with M1's "one fault row per named channel … plus one mutant per
isolation element". The row as it currently stands in the uncommitted worktree
(`corpus/QUALITY.md:177`, absent from the base commit) is **partially
falsified by its own instrument at the base** in three narrow places, and the
lesson counts it rests on are not all reproducible. The exact replacement row
is drafted at `out/ConnQualityRules/KQ34.md`; it keeps the existing direction
and closes those three places without widening credit.

## Contradictions (stated, not scored)

1. **Tracebacks: 8 vs 9.** `lessons/round-23.md:64` says the frozen grid arm
   met `0/26` faults with "8 tracebacks, 2 executed programs, 1 hang". At
   `245a37f` the same command reports **9** tracebacks (plus 2 executed, 1
   timeout). Rows with a frozen traceback: F01, F02, F16, F18, F19, F20, F22,
   F24, **F26**. F26 was added in `34b2376`; the older count appears to have
   been carried forward — a KQ27 count defect, not a verdict change.
2. **"22/24 killed; M02 defensive-only"** is arithmetically right and
   interpretively wrong. M02 (`--no-lazy-fetch`) is load-bearing on a channel
   the grid has no row for (replicated below); M20's defensive-only label holds
   but for a different reason than `lessons/round-23.md:80` gives
   (`CritDefensiveOnly.md`).
3. **`lessons/round-23.md:65` says "every grid builder `require()`s its
   premise"**. Eight fault builders have no `require()` on their path: F02,
   F16, F17, F18, F19, F24, F25, F26. Their faults are constructed and fail
   closed (`g(check=True)` or direct byte writes), which is acceptable
   evidence, but not the mechanism the lesson claims.
4. **The worktree row would bless (2).** Its "elements no mutant kills are
   labelled defensive-only" makes survival sufficient. Survival of M02 is a
   grid-coverage gap, not redundancy; under the drafted rule the false label
   would be admitted.

## Evidence (base `245a37f`)

All commands run in the clone at `245a37f`; fixtures are fresh `/tmp` repos
with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1` and explicit
identity; the only network-shaped references are `example.invalid`. git
2.56.0.

**KQ34 is not in the base.**

```text
git show HEAD:corpus/QUALITY.md | grep -c KQ34          # 0, exit 1
git status --short                                       # lane:  M corpus/QUALITY.md (+3), worktree row at :177
grep -n '^| KQ32\|^| KQ33' corpus/QUALITY.md             # 165, 171 at the base
```

**Grid reproduces, but the frozen count differs.**

```text
python3 tests/report-audit/repo-state-grid.py --arm both --json    # rc=1 (frozen expected)
current faults=26/26 controls=8/8 tracebacks=0 executed=0 timeouts=0 violations=0
frozen  faults=0/26  controls=8/8 tracebacks=9 executed=2 timeouts=1 violations=26
population_sha256 83a84702251c62c6990c8222ea6c4276e09db05344b3c2c0d862a857e50ea2f1
auditor frozen 09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f
auditor current f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7
```

Rows and pins at the base: `tests/report-audit/repo-state-grid.py:526`
(CASES), `:579` (REASONS), `:594` (population), `:627` (met predicate).

**The mutant population omits a named element.**

```text
python3 tests/report-audit/isolation-mutants.py --json            # rc=0
mutants=24 killed=22 surviving=['M02-lazy-fetch','M20-log-sha-shape']
grep -c '"-z"' tests/report-audit/isolation-mutants.py             # 0
```

`round_commits` emits NUL-delimited records with `-z` and `%x00`
(`tools/report-landing-audit.py:183`), and F25 grades subject-record injection,
yet no mutant removes that delimiter. The element is **unkillable? No — it is
unmutated.** A single literal removal of `"-z", ` in a scratch copy gives:

```text
grid --arm current --current <scratch> --json    # rc=1
faults_met=13/26 controls_met=6/8 violations=15
C02 exit 2 'unexpected git log output (7 fields)'
C06 exit 2 'unexpected git log output (7 fields)'
F25 exit 2 'unexpected git log output (7 fields)'
```

So the kill exists, but it is a blanket parse failure shared with two controls
and thirteen fault rows. Under the drafted row any such nonzero exit earns a kill;
under the proposed row it is reported as shared-protocol, not as channel
evidence. The 24 mutants cover the `GIT_ISOLATION` entries and the
refusal/decode sites; none covers the NUL delimiter. M08 was never
defined (numbering skips it from `e0f0434`).

**Kill attribution is unconstrained.** `isolation-mutants.py:111`
(`"killed": rc != 0`) accepts any violation. Observed: M21-newlines is killed
only by `C08-cr-only-report`, a control; M03's kill is F22 alone; M01's is
F03–F05. Pasted failed rows make this visible; the drafted row does not ask for
them.

**M02 is load-bearing, not defensive-only.** Independent replication of the
peer probe on my clone (`crit probe.py`, rc=0):

```text
pristine P01/P02  exit=1 kinds=[landed-unresolved,unresolved-full-hash] exec=0 met
M02      P01/P02  exit=1 kinds=same                                     exec=1 NOT-MET
M20      P01/P02  exit=1 kinds=same                                     exec=0 met
M06      F09      exit=0 kinds=[]                                       exec=1 NOT-MET
M06+M20  F09      exit=0 kinds=[]                                       exec=1 NOT-MET
```

The fixture uses `remote.evil.url`, `remote.evil.partialCloneFilter=blob:none`,
`core.sshCommand=touch <marker>; false` and asserts no `remote.*.promisor`,
no `extensions.partialclone`, no `*.promisor` pack. The pristine tool is safe
because `--no-lazy-fetch` is present (`tools/report-landing-audit.py:93`); the
grid cannot see that because its refusal catches only the other spellings
(`:444-448`). Registered support: S089 https://git-scm.com/docs/git —
"Do not fetch missing objects from the promisor remote on demand." (11 words);
S092 https://git-scm.com/docs/partial-clone — "no check as to whether the
missing object is actually a promisor object is performed" (16 words). Both
registered in the lesson; not re-fetched.

**Extra builders do not assert a premise.** F02/F16/F17/F18/F19/F24/F25/F26
have no `require()`; e.g. `_bad_subject` writes `b"note caf\xe9\n"` and
`raw_commit`s it, and `f_huge_timestamp` hashes a literal 5000-digit author
time with `--literally`. Construction fails closed, but the lesson's uniform
`require()` claim is not what the code does.

## Affected axes

- **C1 / axis 7 (calibration).** The current arm's 26/26 + 8/8 still holds; what
  changes is what may be *credited*. The row keeps the pass and forbids
  crediting unmutated elements, un-attributed kills and survival-only
  defensive labels. No axis is widened; KQ32's trusted-repository limit stays.
- **Contract / verification surface.** The population digest and the
  failed-row list become part of the claim, so the lesson/README counts must be
  re-pinned if a row or mutant is added (KQ27).
- **Runtime / substrate.** None. No install, no host change, no service touch.

## Proposed move (one bounded proposal)

Append the exact six-line block in `out/ConnQualityRules/KQ34.md` after KQ33.
It differs from the worktree draft in six places: an explicit crosswalk that is
not self-selecting; premise "established" rather than uniformly asserted; a
mutant for every named element with pasted failed rows and channel-attributed
kill credit; defensive-only requiring a named dominating refusal plus a row
that passes without the element; pinned population/auditor digests and counts
tied to the measured revision; open rows and KQ32 preserved.

Integration consequences the row forces (L1-owned, not done here):
1. Add the record-delimiter mutant (or declare the channel open and stop
   claiming record isolation) and re-pin the mutant denominator.
2. Either add the `partialclonefilter`-only promisor row and keep
   `--no-lazy-fetch` load-bearing, or widen the refusal and re-label M02 with a
   dominance row; correct the lesson bullet as an erratum (KQ26).
3. Re-state the frozen traceback count (9 at `245a37f`) with the population
   digest.

## Risks

- "…or the channel is reported open" can be used to drop channels silently;
  the reject cell forbids the promise from naming an open channel, and KQ32
  still limits use to trusted repositories.
- A fair critic may read the M02 sentence as lifting KQ32; it does not — it
  only refuses the defensive-only label for a channel a probe shows violating
  the promise.
- Adding rows/mutants invalidates the quoted 24/22 and 26/8 counts unless the
  lesson is re-pinned; that is a required cost, not an accident.
- The row is longer than most; KQ16 at the base is 1614 characters, this row is
  within that family.

## Verification (for the integrator)

```text
git show HEAD:corpus/QUALITY.md | grep -c KQ34          # must stay 0: append-only, no rewrite
tail -6 corpus/QUALITY.md                                # exactly the six-line block
git diff --numstat corpus/QUALITY.md                     # only the appended lines
python3 tests/report-audit/repo-state-grid.py --arm both # rc=1; current 26/26, 8/8
python3 tests/report-audit/isolation-mutants.py          # rc=0; survivors must be fewer than at base
python3 .ufo/waves/round-23/falsify/out/CritDefensiveOnly/probe.py <clone>  # rc=0
```

## Not verified

- `tools/report-landing-audit.py --selftest` (the 50/50 figure is the L1's).
- git versions other than 2.56.0; the 9-traceback count is host-measured.
- The upstream `promisor-remote.c` quote in `CritDefensiveOnly.md`; I replicated
  the probe, not the source fetch.
- The lane's uncommitted worktree now appears to add `M26-record-separators`,
  `M27`–`M29` and a `partialclonefilter` fixture. Not at the base, not run, not
  counted as evidence.
- Other promisor spellings (`include.path`, `hasconfig:`, `config.worktree`) and
  the `objects/info/alternates` / gitfile open rows.

## Files written

- `.ufo/waves/round-23/falsify/out/ConnQualityRules/KQ34.md`
- `.ufo/waves/round-23/falsify/advice/ConnQualityRules.md`

No installs or upgrades were performed. No tracked lane file, Git index, `.jj`,
commit, or shared config was written.
