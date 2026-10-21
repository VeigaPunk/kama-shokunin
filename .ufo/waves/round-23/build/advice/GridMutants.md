# GridMutants: mutation runner for the round-23 repo-state grid

Base: `4fe9339f8fc3a4a4a479d9c938a850da12f1124d`. Candidate under test: the
SimplifyWrapper candidate (`out/SimplifyWrapper/git-wrapper.patch`) applied to a
scratch clone. Auditor sha256 prefix `c4c257f380db`.

## Summary

- The mutation runner works against the real GridHarness. 8/8 defense mutants are
  killed by the rows predicted for them; 6/6 probes survive as predicted.
- The candidate is **not clean on the full grid**. 6 of 21 graded rows fail
  (F7, F8, F9, F10, F11, F12). These are repo-local state faults that are inside
  the claim's stated scope ("repository-local git state still changes or crashes
  its verdict"). Kills are attributed differentially, so these rows cannot mask
  a kill.
- Frontier against frozen: the candidate moves 8 of 14 fault rows to correct
  behavior (F1, F2, F3, F4, F4b, F5, F6, F13). F7 through F12 stay failing.
  All 7 controls have the same exit and defect kinds as on frozen.
- Two grid blind spots were measured outside the grid (G1, G2), and channel
  redundancy was measured (G3). None of these was fixed; GridHarness is not mine.

## Interface (observed; no stub used)

GridHarness landed during the wave, so the stub I first wrote was discarded
before delivery. No result below comes from it.

- Grid: `out/GridHarness/repo-state-grid.py`, sha256 prefix `141c0c2c8e4d`.
  Its population digest `7be080caa147...` matches its pinned constant; every run
  proceeded past the pin check.
- Call: `repo-state-grid.py --arm current --current PATH --json`.
- stdout JSON: `pass`, `reasons`, `population_sha256`, and `rows[]`. Each row has
  `case`, `kind`, `expect`, `observed.current` (`verdict`, `exit`, `traceback`,
  `marker`, `timed_out`, `defects`) and `ok.current` (true, false, or null).
- Gate for `--arm current`: every row of kind control, fault, or guard must have
  `ok.current == true` (`GRADED` at grid L44; `decide` at L563-579).
  Open and tradeoff rows never gate.
- Exit: 0 gate holds, 1 gate violated, 2 cannot evaluate.
- Each auditor child is run with `clean_env()` (grid L67-72, L523-526), which sets
  `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1`.

## Deliverables

- `out/GridMutants/mutants.py`: 14 mutants, a differential runner, and a `--list`
  option. Each mutant is a literal substring edit that must match exactly once.
  A mutant that fails to compile is reported INVALID, never counted as a kill.
  Most mutants are one line. Two-channel defenses touch 2 lines, and the
  lane-log probe rewrites 2 lines into 5.
  - Usage: `python3 mutants.py --auditor PATH [--keep DIR] [--accept-baseline IDS] [--json] [--list]`
  - Exit: 0 pristine clean, every defense killed as predicted, every probe as
    predicted; 1 a defense survived or a probe deviated; 2 pristine fails graded
    rows not listed in `--accept-baseline`, or grid error; 3 mutant not applied or
    not compilable.
- `out/GridMutants/supp-probes.py`: two fresh-fixture probes outside the grid (S1, S2 below).
- `out/GridMutants/evidence-accepted-baseline.json`: runner JSON from the exit-0 run.

## Pristine candidate on the real grid (`--arm current`)

| Row | Observed | Expected | Reading |
|---|---|---|---|
| F7 showsignature-program | clean/0 **[MARKER]** | clean, no marker | planted `gpg.program` ran via repo-local `log.showSignature`; `git_env` does not cover repo-local config |
| F8 shallow-hides-omitted | clean/0 | refusal exit 2 | false clean |
| F9 grafts-hides-omitted | clean/0 | refusal exit 2 | false clean |
| F10 tag-shadows-branch | clean/0 | failed, landed-omitted | false clean (mechanism not verified, see caveats) |
| F11 mailmap-fifo | timeout after 30 s | clean, no hang | hang on a FIFO `.mailmap` |
| F12 sha256-lane | failed/1 landed-omitted | refusal exit 2 | not refused |

Pristine passes C1-C7, F1, F2, F3, F4, F4b, F5, F6, and F13.

Runner: `mutants.py --auditor <candidate> --keep /tmp/kama-r23-mutants-run1`
gives `pristine: FAIL`, `summary: ... -> exit 2`, wall 126.9 s.
Runner: `... --accept-baseline F7,F8,F9,F10,F11,F12 --json` gives `exit 0`,
`baseline_ok true` (`evidence-accepted-baseline.json`).

## Frontier against frozen (`--arm current` on each auditor)

- Frozen auditor (`git show 4fe9339f:tools/report-landing-audit.py`, sha256
  `09ecd63b...`, equal to the grid's `FROZEN_SHA256`): 7/7 controls pass and 14/14
  fault rows fail. Each fault reproduces on frozen.
- Candidate: F1 (crash to clean), F2 (crash to exit 2), F3 (clean to landed-omitted),
  F4 and F4b (clean to unresolved-full-hash), F5 (fetch and command gone),
  F6 (clean to landed-omitted), F13 (crash to exit 2) become correct.
- F7 through F12 are still failing. Observed verdicts for F8 through F12 equal
  frozen's: clean/0, clean/0, clean/0, timeout, failed/1.

## Mutants (differential: a mutant kills the rows it newly fails)

Each defense mutant removes all channels of one defense. A probe removes exactly
one channel or one wrapper. The mutant's *new* rows are its failing rows that the
pristine candidate does not fail.

| Mutant | Group | Predicted | New rows (observed) | Verdict |
|---|---|---|---|---|
| drop-no-replace-objects (argv + env) | defense | F3, F4, F4b | F3, F4, F4b (all clean/0) | KILLED |
| drop-no-lazy-fetch (argv + env) | defense | F5 | F5 failed/1 **[MARKER]** | KILLED |
| decode-errors-replace | defense | F2 | F2 clean/0 | KILLED |
| decode-swallow-empty | defense | F2 | F2 failed/1 (section missing), **F13** clean/0 | KILLED (+F13) |
| drop-logoutputencoding-override | defense | F1 | F1 could-not-evaluate/2 | KILLED |
| drop-log-follow-override | defense | F6 | F6 clean/0 | KILLED |
| refusal-exit-clean (2 to 0) | defense | F2, F13 | F2, F13 clean/0 | KILLED |
| refusal-exit-failed (2 to 1) | defense | F2, F13 | F2, F13 failed/1 | KILLED |
| probe-drop-config-isolation | probe | none | none | SURVIVED (G2) |
| probe-lane-log-swallow | probe | none | none | SURVIVED (G1) |
| probe-replace-argv-only | probe | none | none | SURVIVED (G3) |
| probe-replace-env-only | probe | none | none | SURVIVED (G3) |
| probe-lazy-argv-only | probe | none | none | SURVIVED (G3) |
| probe-lazy-env-only | probe | none | none | SURVIVED (G3) |

Note: `decode-swallow-empty` is the grid's only kill for the errata path (F13).
That is the claim's "catch UnicodeDecodeError, status clean" case, observed as clean/0.

## Supplemental probes (outside the grid; `supp-probes.py <candidate>`)

Run twice; identical results. Fixture root under `/tmp/kama-r23-supp-*`.

- **S1, lane commit with invalid UTF-8 in its subject.** A raw commit object
  (`hash-object -t commit`) holds `round-1: late \xff`, and round-1 is omitted
  from the report.
  - Pristine: exit 2, stderr tail `... master in <root>/s1/lane: output not UTF-8`.
  - probe-lane-log-swallow: exit 0, `defects []`, `required 0`. False clean.
- **S2, global config enables `showSignature` with a fake `gpg.program`.** HOME
  holds `[log] showSignature=true`, `[gpg] program=<script that touches a marker>`.
  The lane commit carries a `gpgsig` header.
  - Pristine: exit 0, marker not created.
  - probe-drop-config-isolation: exit 0, **marker created**. Host-level gpg ran.

## Grid gaps and proposals (not implemented; GridHarness is not mine)

- **G1, no row exercises a lane-log decode failure.** F1 is protected by the `-c
  i18n.logOutputEncoding=UTF-8` override, so it never reaches that path. Proposed
  row F14: the S1 fixture with expect exit 2. Pristine gives exit 2; the swallow
  mutant gives exit 0 (S1 above).
- **G2, the grid cannot observe the auditor's own isolation.** `invoke()` already
  sets `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1` in the child env
  (grid L67-72, L523-526), and the auditor's `git_env` re-adds them. Under the grid
  the probe's survival depends on the operator's real `$HOME/.gitconfig` being
  inert for these keys, because the grid does not pin HOME. I did not inspect that
  file. Proposed: one row with HOME pointing at a planted config, run with the
  isolation env stripped for that row only.
- **G3, channel redundancy on git 2.56.0.** Each protection is enforced by an argv
  flag and by an env var, and either channel alone works (4 probes survive). The grid
  can only see loss of both. Not tested: git below 2.44, where one channel may be
  absent.

## Caveats and not verified

- F7 through F12 are residuals of the candidate, not of the mutants. I did not test
  any fix for them. Suggestions are unverified: a `-c log.showSignature=false`
  check for F7, an explicit `refs/heads/<branch>` for F10.
- F10 mechanism is [INFERENCE]: git resolves `master` to `refs/tags/master` before
  `refs/heads/master`. Observed clean/0; not checked here.
- F11 mechanism is not isolated (a `.mailmap` read from the worktree is the likely
  path). Not verified.
- Frozen F5 marker is not recorded in my readout; the frozen F5 failure is observed,
  its marker is taken from the L1 probe.
- Not run: the auditor's own `--selftest`, `--arm both` (which also checks control
  parity and fault reproduction in one gate), and any git version other than 2.56.0.
- `probe-drop-config-isolation` survival on this host was not checked against
  `$HOME/.gitconfig`; the S2 probe shows the effect when such config exists.
- Operator tooling directive: no installs or updates in this wave (no pacman, uv,
  npm, cargo, or binaries). No pacman transactions were started.

## Files written

- `.ufo/waves/round-23/build/out/GridMutants/mutants.py` (deliverable)
- `.ufo/waves/round-23/build/out/GridMutants/supp-probes.py` (deliverable)
- `.ufo/waves/round-23/build/out/GridMutants/evidence-accepted-baseline.json` (deliverable)
- `.ufo/waves/round-23/build/advice/GridMutants.md` (this report)
- Scratch, not deliverables: `/tmp/kama-r23/GridMutants` (clone, wrapper patch applied),
  `/tmp/kama-r23-frozen-audit.py`, `/tmp/kama-r23-mutants-run1/`,
  `/tmp/kama-r23-mutants-run2/`, `/tmp/kama-r23-mutants-run2.json`,
  `/tmp/kama-r23-supp-hzsf0mho/`, `/tmp/kama-r23-supp-nfruuqmo/`
