# ExecLocaleArms: grid current arm under locale arms (round-23 falsify)

**Verdict: partially holds.**

- C1 grid rows hold under every assigned arm (`LC_ALL=C`, `LANG=C.UTF-8`, `PYTHONIOENCODING=ascii`, and their combinations): **0 of 37 rows changed**. Each run is 26/26 faults, 8/8 controls, 0 tracebacks, 0 executions, 0 timeouts.
- Outside the grid's rows, two outcome changes are locale-triggered:
  1. **Text-mode output under an ASCII stdout flips exit 1 to exit 2** when a committed errata row carries non-ASCII text. It fails closed (no traceback, no pass), and the JSON-only grid cannot see it.
  2. **Under a strict ASCII C locale, the grid and the selftest cannot evaluate (exit 2)** because their own fixtures pass non-ASCII argv to git. This is harness fragility; no auditor verdict changed.
- No auditor verdict was wrong in any run.

Not claimed: any change to the frozen arm, other locales, or the isolation mutants (see Not verified).

## Subject

- Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`, clone `/tmp/kama-r23w2/ExecLocaleArms`.
- Clone HEAD `245a37f69628c2c6bb29bbf17897d8fb5946c857` (verified with `git rev-parse HEAD`). `git status --short` is empty.
- Auditor `tools/report-landing-audit.py`; grid-recorded `auditor_sha256.current` = `f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7`.
- Grid `population_sha256` = `83a84702251c62c6990c8222ea6c4276e09db05344b3c2c0d862a857e50ea2f1`, identical in every run.
- No external sources cited.

## Environment and what each arm does

Host: Linux 7.2.11-arch1-1 x86_64. `/usr/bin/python3` is 3.14.8. git is 2.56.0. Installed locales: `C C.utf8 en_US.utf8 POSIX`. Session env: `LANG=en_US.UTF-8`, `LC_ALL` and `PYTHONIOENCODING` unset. Only locale and encoding variables were inspected; no secrets or other environment values were read.

Efficacy (`out/ExecLocaleArms/efficacy-probe.txt`, child Python under each per-command env):

| arm (env per command) | `sys.flags.utf8_mode` | stdout encoding/errors | locale encoding |
|---|---|---|---|
| inherited | 0 | utf-8/strict | UTF-8 |
| `env -u LC_ALL LANG=C.UTF-8` | 0 | utf-8/surrogateescape | UTF-8 |
| `env -u PYTHONIOENCODING LC_ALL=C` | **1** | utf-8/surrogateescape | utf-8 |
| `env -u LC_ALL PYTHONIOENCODING=ascii` | 0 | **ascii**/strict | UTF-8 |
| `env PYTHONIOENCODING=ascii LC_ALL=C` | 1 | **ascii**/strict | utf-8 |
| strict C (extension): `env -u LANG LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0` | 0 | ascii/surrogateescape | **ANSI_X3.4-1968**, fs ascii |

- The assigned `LC_ALL=C` arm runs Python in UTF-8 mode, so it is not an ASCII-stdout test. ASCII stdout comes only from `PYTHONIOENCODING=ascii` or the strict-C extension.
- [INFERENCE] The UTF-8-mode switch is Python's C-locale behavior. I did not check PEP 538 or 540 wording against documentation.
- The variables reach the audited processes. The grid's `env()` drops only `GIT_*` (`tests/report-audit/repo-state-grid.py:43-49`), and the grid runs the auditor with `env=env()` (`:611-612`). The auditor's git calls use `git_env()`, which also drops only `GIT_*` (`tools/report-landing-audit.py:99-105`, `:114-116`). The strict-C failures in section 3 show the variable is live in those processes.

## 1. Grid current arm under the variants: no row changes

Command per run, in the clone: `env <VARS> python3 tests/report-audit/repo-state-grid.py --arm current --json`

| run | env (per command) | exit | faults | controls | tracebacks | executed | timeouts | rows changed (normalized) |
|---|---|---|---|---|---|---|---|---|
| baseline | `env -u LC_ALL -u PYTHONIOENCODING` (inherits `LANG`) | 0 | 26/26 | 8/8 | 0 | 0 | 0 | reference |
| baseline-repeat | same | 0 | 26/26 | 8/8 | 0 | 0 | 0 | 0 |
| LC_ALL-C | `LC_ALL=C` | 0 | 26/26 | 8/8 | 0 | 0 | 0 | 0 |
| LANG-C.UTF-8 | `LANG=C.UTF-8` | 0 | 26/26 | 8/8 | 0 | 0 | 0 | 0 |
| PYTHONIOENCODING-ascii | `PYTHONIOENCODING=ascii` | 0 | 26/26 | 8/8 | 0 | 0 | 0 | 0 |
| LC_ALL-C+ascii | `LC_ALL=C PYTHONIOENCODING=ascii` | 0 | 26/26 | 8/8 | 0 | 0 | 0 | 0 |
| LANG-C.UTF-8+ascii | `LANG=C.UTF-8 PYTHONIOENCODING=ascii` | 0 | 26/26 | 8/8 | 0 | 0 | 0 | 0 |

- Raw comparison: every run, including baseline-repeat, differs from baseline in exactly 10 `stderr_tail` strings. The only difference is the random `TemporaryDirectory` name `repo-state-grid-XXXXXXXX`. After normalizing it, all 37 rows match baseline on `exit`, `kinds`, `traceback`, `executed`, `timed_out`, `met`, and `stderr_tail` in every run.
- Each run's JSON is 13,213 bytes, and each run's stderr is empty.
- Ungraded rows, identical in every arm: O01 exit 0 `kinds []` (open), O02 exit 0 `kinds []` (open), T01 exit 2 (tradeoff).
- Selftest, `python3 tools/report-landing-audit.py --selftest`, same six arms: rc 0, 50 `ok`, 0 `FAIL`, empty stderr, byte-identical output (sha256 prefix `91c3a6c99522c42e`).

## 2. Text mode: outside the grid, one locale-triggered exit change

- The grid always passes `--json` (`tests/report-audit/repo-state-grid.py:603-604`). JSON output is ASCII because of the `json.dumps` default (`tools/report-landing-audit.py:906-907`), so the grid cannot see text mode.
- Text mode prints errata tokens and corrections verbatim (`tools/report-landing-audit.py:506-525`, with the token and correction printed at `:515`, `:517`, `:519`).
- Errata come from the committed lane tip (`:362-372`, `git show {tip}:registry/report-landing-errata.tsv`). The token and correction columns are not validated (`:347-359`).

**Probe B** (`probe-errata-text-mode.py`, output `errata-text-probe.json`). Fresh `/tmp` lane with a committed errata row. Text and JSON modes, seven arms:

| fixture (errata row) | baseline text | `PYTHONIOENCODING=ascii` text (also with `LC_ALL=C` and with `LANG=C.UTF-8`) | strict-C text | JSON, all arms |
|---|---|---|---|---|
| ASCII token `deadbeef1` (control) | 1 | 1 | 1 | 1 |
| non-ASCII token `café` | 1 | **2** | **2** | 1 |
| non-ASCII correction `café` | 1 | **2** | **2** | 1 |

- `LC_ALL=C` and `LANG=C.UTF-8` text stay at 1 in every row.
- Baseline text stdout: `errata-unmatched line=1 landed-unresolved café`, then `summary … status=failed`, rc 1.
- ASCII text: stdout empty. Stderr: `could-not-evaluate: internal: UnicodeEncodeError: UnicodeEncodeError('ascii', 'round=1 … caf\xe9 …', 88, 89, 'ordinal not in range(128)')`. There is no traceback, because the catch-all at `tools/report-landing-audit.py:918-924` converts the exception.
- Why this is fail-closed and not a false pass: exit 2 is the tool's documented output-failure channel (`tools/report-landing-audit.py:42-46`). Status 0 requires no unmatched and no invalid errata (`:499-500`), so only status-1 runs print non-ASCII. The only change is 1 to 2, never to a pass. It is still a real loss of verdict text that UTF-8 output keeps, and the grid is blind to it.

**Probe A** (`probe-grid-text-mode.py`, output `grid-text-mode-probe.json`). All 37 grid fixtures, text and JSON modes, seven arms (518 cells):

- Text exit-code distribution `{0: 15, 1: 10, 2: 12}`, identical in every arm.
- Text and JSON stdout and stderr identical to baseline after normalization.
- JSON exit and kinds identical to the grid's recorded values for all 37 rows in all seven arms.
- 0 tracebacks, 0 timeouts, 0 executions.
- No grid fixture carries non-ASCII text into text output, so none flips.

## 3. Strict ASCII C (extension beyond the assignment): harness aborts, verdicts unchanged

Under `env -u LANG -u PYTHONIOENCODING LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0`:

- **Full grid**, `--arm current --json`: exit 2, stdout empty. Stderr: `could-not-evaluate: UnicodeEncodeError: 'ascii' codec can't encode character '\xe9' in position 8`. Cause: F01's builder passes `"note café"` as git argv through `commit()` (`tests/report-audit/repo-state-grid.py:216-218`, `:78`). No row is evaluated.
- **Selftest**: exit 2. Traceback: `tools/report-landing-audit.py:696` (`_commit(lane, source_fixture, …)`), then `:540` (`git … commit -q -m msg`), then `UnicodeEncodeError: 'ascii' codec can't encode character '\u2014' … position 171` (`out/ExecLocaleArms/selftest-strictC-traceback.txt`). The selftest is not evaluated under strict C.
- **Grid minus F01** (`--case` for the other 36 names): exit 0. Faults 25/25, controls 8/8, 0 tracebacks, 0 executions, 0 timeouts. Each row matches baseline after normalizing the temp name and the `current/NN` index, which shifts when F01 is excluded.

These are harness failures under pure ASCII argv, not auditor verdict changes. Exit 2 is the grid's "could not evaluate". Under `LC_ALL=C` as Python 3.14 resolves it, the harness runs normally.

## Not verified

- The frozen arm under any variant.
- `tests/report-audit/isolation-mutants.py` under any variant.
- The rounds 10 to 22 ledger under any variant.
- Other locales and encodings. Only `C`, `C.utf8`, `en_US.utf8`, and `POSIX` are installed, and I generated no other locale. `LC_ALL=C` with coercion alone disabled (no `PYTHONUTF8=0`) was not tested separately.
- Git's localized messages. All stderr I observed was English; no translated locale was tested.
- Text mode on auditor inputs beyond the 37 grid fixtures and the three errata fixtures.
- Any fix for either finding. Not implemented or tested. Candidates for the build lane only: ASCII-safe stdout (e.g., `errors="backslashreplace"`), and argv-safe fixture builders (stdin or `-F` message files) in the grid and selftest.
- Stress or repetition beyond the one baseline-repeat run. Runs were batched in parallel on a busy host.

## Host observation (affects fleet verification)

- During my first text-mode probe, `/tmp` (`/dev/nvme0n1p1`, xfs, 128G) was full: bytes 100% (3.3M free), inodes 9388926 of 9401856 used (12930 free). Twelve of 37 fixtures failed to build with disk-full errors (`No space left on device`, `unable to write new index file`, `couldn't set refs/heads/master`). The partial run is kept as `grid-text-mode-probe.ENOSPC-partial-25of37.json`; its 25 built cells showed no disk-full error and no flips. Observed readings are in `tmp-enospc-observed.txt`.
- Shortly after, other lanes had freed space: `/tmp` read 111G used, 18G free (87%), with 36M inodes free. The full rerun built 37 of 37 fixtures with `build_errors` 0 (`tmp-df-at-rerun.txt`).
- Largest `/tmp` consumers belong to other lanes: `/tmp/f14-var` 16G, `/tmp/tsukuroi-r17-boot` 2.9G, `/tmp/kama-r23` 1.7G, `/tmp/kama-r23w2` 5.4G (shared, includes other clones). I did not touch them.
- `/tmp/repo-state-grid-hyiacrq2` (owner vgpnk, 13:00) is not mine; my last grid run ended before that. Left untouched.
- Any run using the default `TemporaryDirectory` depends on free space in `/tmp`, and fault fixtures must live in `/tmp` by contract.

## Installs and updates

None. No pacman, sudo, uv, npm, or cargo activity. Tools used as installed: git 2.56.0 and Python 3.14.8.

## Files written

Lane seat output:

- `.ufo/waves/round-23/falsify/advice/ExecLocaleArms.md` (this report).
- `.ufo/waves/round-23/falsify/out/ExecLocaleArms/` (59 entries):
  - `host-context.txt`
  - Grid JSON, stderr, and rc for the seven arms (`baseline`, `baseline-repeat`, `LC_ALL-C`, `LANG-C.UTF-8`, `PYTHONIOENCODING-ascii`, `LC_ALL-C+ascii`, `LANG-C.UTF-8+ascii`)
  - `selftest-*.{txt,rc,stderr}` for the six arms, plus `selftest-strictC-*` (`.txt`, `.rc`, `.stderr`) and `selftest-strictC-traceback.txt`
  - `strictC.{json,rc,stderr}`, `strictC-minus-F01.{json,rc,stderr}`, `strictC-print-probe.stderr`
  - `efficacy-probe.txt`
  - `errata-text-probe.json`
  - `grid-text-mode-probe.json` (final, 37 of 37) and `grid-text-mode-probe.ENOSPC-partial-25of37.json` (partial)
  - `probe-errata-text-mode.py`, `probe-grid-text-mode.py` (copies of the scratch scripts)
  - `tmp-df-at-rerun.txt`, `tmp-enospc-observed.txt`

Scratch outside the lane:

- `/tmp/kama-r23w2/ExecLocaleArms/` (clone; no tracked or untracked changes) and `/tmp/kama-r23w2/ExecLocaleArms.clone.log`.
- `/tmp/kama-r23w2/probe-<arm>.{out,err}` (12 files, efficacy prints), `/tmp/kama-r23w2/probe-errata-text-mode.py`, `/tmp/kama-r23w2/probe-grid-text-mode.py`.
- Fixture roots I created and removed: `/tmp/kama-r23-locale-probe-h06rpc79`, `/tmp/kama-r23-grid-text-jtgh13yx`, `/tmp/kama-r23-grid-text-bkcwp6p5`.

Not written: lane tracked files, lane `.jj`, lane git index, `~/.omp`, sibling lanes, fleet root.
