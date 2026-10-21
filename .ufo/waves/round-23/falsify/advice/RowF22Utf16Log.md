# F22-utf16-log-cutoff — falsification scout

**Verdict: partially.** The row holds exactly as built (premise real, frozen
arm fails as claimed, expected outcome is the correct one, current passes),
but the channel is **not closed**: a near variant of the same i18n
log-encoding channel — repository-local `i18n.commitEncoding=UTF-16` — still
changes current's verdict on a fixture whose ordinary answer is exit 0. It
flips a clean report to `landed-omitted` (exit 1) via a shifted cutoff, or
forces `could-not-evaluate` (exit 2) when it cannot shift a cutoff. Frozen
crashes with a traceback in the same variants.

All observations below are against the committed blobs at
`245a37f69628c2c6bb29bbf17897d8fb5946c857` (my clone HEAD; blob hashes
`f10d811eafcc5bc853abdf75c4a05ec2374cd579` tools/report-landing-audit.py,
`c5dfeee9488b4113493ec295e27c84d53002d1bc`
tests/report-audit/repo-state-grid.py; frozen blob
`4fe9339f8fc3a4a4a479d9c938a850da12f1124d`). Environment: git 2.56.0,
Python 3.14.8, every git call with `GIT_CONFIG_GLOBAL=/dev/null
GIT_CONFIG_NOSYSTEM=1` and explicit identity. Note: the lane checkout's
working tree was dirty at observation (6 modified tracked files, including
both files above); I used only the committed blobs, so nothing here refers to
the dirty copies.

## 1. Is the fault premise real and observed in the frozen arm? YES

Grid builder/expectation (`tests/report-audit/repo-state-grid.py:184-191`,
row at `:565`): `base()` lane+fleet, fleet `i18n.logOutputEncoding=UTF-16`,
premise `b"\x00" in git -C fleet log --format=%at`; row expects
`(exit 0, [])`.

Hand-built fixture (not importing the grid; lane commit `round-1: work` by
`kama-shokunin` @1000, fleet report citing it committed @2000, fleet config
set). Premise probe:

```
git -C fleet log --diff-filter=A --format=%at -- .ufo/reports/round-1/kama.md
b'\xff\xfe2\x000\x000\x000\x00\n'      # BOM + UTF-16LE "2000\n", NUL present
```

Frozen blob (extracted with `git cat-file blob 4fe9339f…:tools/report-landing-audit.py`):

```
exit 1; stderr:
  File "<frozen>/frozen-audit.py", line 166, in report_cutoff
    out = git(fleet_repo, "log", "--diff-filter=A", "--format=%at", "--", rel).split()
  File "<frozen>/frozen-audit.py", line 89, in git
    proc = subprocess.run([...], capture_output=True, text=True, ...)
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0
```

Committed current, same fixture: `exit 0`, `cutoff 2000`, `required 1`,
`round_commits 1`, `defects []`, no traceback.

The grid's own row in the clone:

```
python3 tests/report-audit/repo-state-grid.py --case F22-utf16-log-cutoff --arm both
frozen  F22-utf16-log-cutoff fault exit=1 kinds=unparseable tb=1 met=NOT-MET
frozen  faults=0/1 controls=0/0 tracebacks=1 executed=0 timeouts=0 violations=1
current F22-utf16-log-cutoff fault exit=0 kinds=[] tb=0 met
current faults=1/1 controls=0/0 tracebacks=0 executed=0 timeouts=0 violations=0
```

So "frozen 0/26 faults met" is consistent for this row (I did not run the
other rows). The frozen failure is exactly the `%at` cutoff query at frozen
line 166 going through the `text=True` git helper at line 89.

## 2. Is the expected outcome the CORRECT one? YES

The fixture is a clean report: its only lane commit is cited, and nothing
else precedes the cutoff. Exit 0 is the correct audit result, not merely
what current happens to do. The neutralization is semantically neutral for
benign repos: `-c i18n.logOutputEncoding=UTF-8` merely restores git's
default log output encoding (default is `i18n.commitEncoding`, itself
defaulting to UTF-8), and the auditor parses only ASCII fields plus
surrogate-escaped subjects.

It is also not over-suppressing. Under the same fault the auditor still
**finds real defects**:

- lane and/or fleet `i18n.logOutputEncoding=UTF-16`, with an uncited lane
  `round-1: more` @1500 before the report cutoff 2000 → current `exit 1`,
  kinds `["landed-omitted"]` (frozen tracebacks in every such variant).
- lane-only UTF-16, clean report → current `exit 0`.

Fix sites: `GIT_ISOLATION` `tools/report-landing-audit.py:93-97`, applied to
every git call in `git()` `:108-131`, consumed by `report_cutoff()`
`:203-206`.

## 3. Near variant of the same channel that current still gets WRONG: YES

Channel = repository-local i18n encoding state that re-encodes git log text.
Current isolates only the **output** key (`i18n.logOutputEncoding`). The
sibling key `i18n.commitEncoding` is not isolated, and when a commit is
written under it, `git commit` records an `encoding UTF-16` header in the
commit object. `git log` then re-encodes from that per-commit header, and
`-c i18n.logOutputEncoding=UTF-8` cannot override it (verified: adding
`-c i18n.commitEncoding=UTF-8` to the log call does not restore the field
either — the header wins). For a message whose byte length is even, git
prints an **empty** `%an`/`%at`/`%s` for that commit (observed on git 2.56.0;
odd-length messages fall back to the raw bytes).

Evidence, all with the config in the fleet repo's `.git/config` at audit time
(`git config --local --get i18n.commitEncoding` → `UTF-16`):

**(a) Fleet first-add commit mangled, single add.** Report committed @2000
while `i18n.commitEncoding=UTF-16` is set; report is clean and readable at
HEAD (`git show HEAD:.ufo/reports/round-1/kama.md` succeeds). Current:
`exit 2`, `could-not-evaluate: round 1: .ufo/reports/round-1/kama.md has no
fleet commit` (`tools/report-landing-audit.py:306`) — the ordinary exit-0
verdict is lost; frozen also exit 2 here.

**(b) Fleet first-add mangled plus a later identical re-add — a wrong
verdict.** Fleet: report added @2000 (config set), lane `round-1: later`
@2500 (uncited, but authored **after** the report, so `post_report` and not
required per the docstring, `tools/report-landing-audit.py:24,30`), report
deleted @2900 and re-added identically @3000. Control (same history, no
config):

```
current exit 0  cutoff 2000  required 1  kinds []
frozen  exit 0  cutoff 2000  required 1  kinds []
```

Same fixture with `i18n.commitEncoding=UTF-16` set at publish time:

```
cutoff query under the auditor's own isolation:
  b'3000\n\n'   -> out.split() = ['3000']  (the @2000 record's %at is blank)
current exit 1  cutoff 3000  required 2  kinds ['landed-omitted']
frozen  exit 1  traceback UnicodeDecodeError (config kept; if unset at
                audit time, frozen also exits 1 at cutoff 3000, no traceback)
```

The flagged commit is the @2500 `round-1: later`; under the tool's own
first-add semantics the cutoff is 2000 and that commit is `post_report`, so
exit 0 is correct. The only difference between control and flip is the
repository-local config at publish time; the flip also persisted when the
config was unset after the @2000 commit (the header is already in the
object), so the repo-local setting need not still be present when the audit
runs. This is a verdict flip caused by repo-local git state — the exact
class C1 claims to neutralize.

The wrong verdict is avoidable from the same objects: under the auditor's
own isolation, `git log --diff-filter=A --format=%H -- <report>` returns both
add commits (blank `%at` does not affect `%H`), and `git cat-file commit
3f969fb…` still carries `author fixture <a@x> 2000 +0000`. Reading OIDs and
the raw author header recovers the true cutoff 2000; relying on the rendered
`%at` text is what loses it.

**(c) Lane commit mangled.** Lane repo sets `i18n.commitEncoding=UTF-16`
before the round commit (`round-1: work`, raw object message
`b'round-1: work\n'`). Current: `exit 2`,
`could-not-evaluate: unexpected git log record '<sha>' ''`
(`tools/report-landing-audit.py:193-197`); frozen exit 1 traceback. This is a
refusal (permitted by the exit contract), not a wrong verdict, but it is
again a loss of the ordinary verdict under the same channel.

A minimum hardening implied by (b): compute the cutoff from `%H` plus raw
`git cat-file commit` headers rather than from the re-encoded `%at` text
(and, if lane subjects must be robust, from raw commit objects as well).
Forcing `i18n.commitEncoding=UTF-8` on the command line is **not** a fix for
already-written commits.

## Also observed (adjacent, not this row; not claimed)

Both arms hang (8 s timeout, no output) on a repo whose `.git/config` has
`[include] path=<FIFO>` and on a lane whose `.git/objects/info/alternates`
is a FIFO. Here git itself blocks before the auditor can act, so I treat
this as outside the audit's controllable state; reporting it, not scoring it.

## What I did NOT verify

- Any other grid row; the full 26/26 frozen vs 26/26 current counts, 8/8
  controls, and the "0 tracebacks/executions/timeouts" totals.
- `tests/report-audit/isolation-mutants.py` (so 22/24 killed, survivors
  M02/M20, and that M03-log-encoding is the killer of this fix, are not
  independently reproduced here).
- No-harm claims: selftest 50/50, rounds 10-22 ledger byte-identity,
  `--no-errata` 9 defects.
- git < 2.56 (declared floor 2.45); no macOS/Windows; no UTF-32/UTF-16BE or
  NUL-in-message commit messages; no `encoding` headers written by tools
  other than `git commit` under `i18n.commitEncoding`.
- The lane checkout's dirty working-tree delta (I did not inspect which seat
  made it; I used only the committed blobs).

## Files written

- `.ufo/waves/round-23/falsify/advice/RowF22Utf16Log.md` (this report)
- `.ufo/waves/round-23/falsify/out/RowF22Utf16Log-2/f22-utf16-repro.py`
  (standalone reproducer; no grid import; `--lane` names a clone at 245a37f6)
- `.ufo/waves/round-23/falsify/out/RowF22Utf16Log-2/run.txt`
  (captured output of the reproducer)

No tools installed or upgraded; no commits, pushes, jj commands, or writes
to the lane checkout's tracked files.
