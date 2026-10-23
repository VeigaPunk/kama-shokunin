ATTACK tools/prereg-time-check.py: partial

The pristine checker reproduces the claimed historical results. Its shipped selftest kills the horizon removal but falsely passes the author-clock and ignored-seconds mutants. A historical output assertion kills the author-clock mutant; an explicitly supplemental subminute case kills ignored seconds. Skipping lines without `Z` is equivalent under the existing regex, not a coverage defect. No production files were changed.

## Scope and axes

- Calibration: committer time, not author time.
- Precision: preserve seconds at the comparison boundary.
- Specificity: preserve the documented 24-hour horizon.
- Isolation: one mutant at a time, exact restoration and identical detector.

Measured source: landed tip `f4066979096e3452ae731c0e09e50155c6d8258a`, `tools/prereg-time-check.py`, sha256 `3d508f776e5b8fac2685dcb80f5bb5c3865427baec3046c4f5b51bed336358c1`.

Scratch root `S=/fast/scratch/hyaku/kama-r26w2/MutPreregTimeCheck`; evidence root `E=.ufo/waves/round-26/w2-falsify/out/MutPreregTimeCheck` (paths below are lane-relative unless absolute). The checker was extracted with `git archive` from an isolated bare clone. Historical reads use that clone, never the lane index. Context files required by the assignment were read; no upstream-source assertion or live-counter result is made by this probe.

## Commands and fixed detector

Setup commands, exit 0:

```sh
mkdir -p /fast/scratch/hyaku/kama-r26w2/MutPreregTimeCheck/work /fast/scratch/hyaku/kama-r26w2/MutPreregTimeCheck/selftests /fast/scratch/hyaku/kama-r26w2/MutPreregTimeCheck/evidence
env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE timeout 90 git clone --bare --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r26w2/MutPreregTimeCheck/history.git
env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE timeout 30 git --git-dir=/fast/scratch/hyaku/kama-r26w2/MutPreregTimeCheck/history.git archive f4066979096e3452ae731c0e09e50155c6d8258a tools/prereg-time-check.py | timeout 30 tar -x -C /fast/scratch/hyaku/kama-r26w2/MutPreregTimeCheck/work
```

Clone stdout/stderr: `Cloning into bare repository '/fast/scratch/hyaku/kama-r26w2/MutPreregTimeCheck/history.git'...` / `done.`

The same command below was run with each phase in the next table, in that order; each phase runs all 12 cases:

```sh
env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE prlimit --as=1073741824 --nproc=8192 -- timeout --kill-after=5 240 python3 /fast/scratch/hyaku/kama-r26w2/MutPreregTimeCheck/probe.py PHASE
```

| PHASE | Detector exit | Shipped `--selftest` exit | Failed detector cases |
|---|---:|---:|---|
| pristine | 0 | 0 | none |
| drop-horizon | 1 | 1 | shipped-selftest, r26-tip |
| restored-horizon | 0 | 0 | none |
| author-time | 1 | 0 | r26-freeze, r25-original, r25-amendment-1, supplement-author-skew |
| restored-author | 0 | 0 | none |
| ignore-seconds | 1 | 0 | supplement-subminute-future |
| restored-seconds | 0 | 0 | none |
| skip-no-Z | 0 | 0 | none |
| restored-no-Z | 0 | 0 | none |

The driver was fixed before the pristine run and never changed: sha256 `c8f3465f77d058dbae6ba516f855cd2b1f0068c7fca9b20d6ca42a54061255b3`. Source copy: `E/probe.py`. It checks exits plus selected clock/delta diagnostics, not just exits. Two supplemental fixtures were included from the outset, not added after mutation. They are **not** shipped selftest cases. Their exact creation commands, dates and revisions are in `E/boundary-fixtures.json`.

Every child command, complete stdout/stderr and exit code is in `E/PHASE.txt` and `E/PHASE.json`. Child commands have a 45-second timeout; no timeout or baseline failure occurred.

## Pristine selftest output

Command (`E/pristine.txt:6`), exit 0:

```sh
timeout --kill-after=2 45 python3 /fast/scratch/hyaku/kama-r26w2/MutPreregTimeCheck/work/tools/prereg-time-check.py --selftest --scratch /fast/scratch/hyaku/kama-r26w2/MutPreregTimeCheck/selftests
```

Case-result output verbatim (full diagnostic output is `E/pristine.txt:8-52`):

```text
[PASS] clean: timestamp before commit: expect 0, got 0
[PASS] flag: minute-precision guess after commit: expect 1, got 1
[PASS] flag: seconds-precision guess after commit: expect 1, got 1
[PASS] clean: legitimate far-future data beyond horizon: expect 0, got 0
[PASS] flag: strict mode flags far-future too: expect 1, got 1
[PASS] clean: mixed past and present-boundary times: expect 0, got 0
[PASS] clean: no timestamps at all: expect 0, got 0
[PASS] clean: malformed Z-suffix lookalike is skipped: expect 0, got 0
[PASS] missing path: expect 2, got 2 (ERROR could not evaluate: no commit touches missing.json at HEAD)
[PASS] bad revision: expect 2, got 2 (ERROR could not evaluate: git log failed rc=128: fatal: bad object deadbeefdeadbeefdeadbeefdeadbeefdeadbeef)
SELFTEST PASS
```

## Mutant kill table

Each change below was made alone to the scratch checker. Locations refer to the pristine `tools/prereg-time-check.py`.

| Mutant | Smallest change | Shipped selftest / named real revision killer | Actual output and verdict |
|---|---|---|---|
| Drop 24 h horizon | line 110: replace the horizon expression with `horizon = None` | Selftest `clean: legitimate far-future data beyond horizon` | `[FAIL] ... expect 0, got 1`; `SELFTEST FAIL`, exit 1 (`E/drop-horizon.txt:23-52`). **Killed.** Tip also exits 1 instead of 0 for the provider reset at `2026-10-25T14:27:28Z` (`:84-92`). |
| Author instead of committer | line 81: `%cI` → `%aI` | Selftest survives. `a4a159c39967e88a89b0808dcd201c79c474efd1` kills it **by clock/delta output**, not by exit. | Pristine prints `committer_time=2026-10-23T00:18:51-03:00` and `+1569s`; mutant prints `committer_time=2026-10-22T07:50:45-03:00` and `later than commit by 60855s`. Both exit 1 (`E/author-time.txt:55-61`). **Killed by full detector; survives shipped selftest and exit-only history checks.** |
| Ignore seconds | line 75: datetime seconds argument `s` → `0` | No shipped selftest case or one of the three named revisions kills it. | `SELFTEST PASS`, exit 0. The existing seconds case uses `03:25:00Z`, so zeroing seconds does not change its result (`E/ignore-seconds.txt:18-22`). **Survives requested existing cases; killed only by supplemental subminute fixture.** |
| Skip lines without `Z` | after line 112: add `if "Z" not in line: continue` | None | `SELFTEST PASS`, exit 0; complete detector exit 0 (`E/skip-no-Z.txt:161-162`). **Survived, equivalent mutant:** `TIME_RE` at line 39 already requires a literal `Z`; no matching timestamp can occur on a line without it. No contract change or extra coverage is justified. |

### Supplemental discrimination (not shipped selftests)

- **Author clock:** fixture revision `da1103251e85a74b71eaa5888852e3ed10957820` has author time `03:00:00Z`, committer time `03:19:43Z`, timestamp `03:18:51Z`. Pristine/restored exit 0. Author mutant exits 1 and prints `FLAG ... later than commit by 1131s` (`E/author-time.txt:143-149`). This is an actual mutant-induced false fail.
- **Seconds:** fixture revision `c4df5732c81102023ecfc25c5defeb882b54a113` has committer time `03:19:43Z` and timestamp `03:19:59Z`. Pristine/restored exit 1, `later than commit by 16s`; ignored-seconds mutant exits 0 and prints `ok ... (at/before commit)` (`E/ignore-seconds.txt:152-158`). This is an actual mutant-induced false pass.

The ignored-seconds mutant also changes the far-future diagnostic by 28 seconds, but the shipped selftest asserts only exit codes. The supplemental case proves a decision-level failure, not merely a changed diagnostic.

## Named round-26 revisions

These are **checker exits**, not detector exits. Path is `.ufo/waves/round-26/preregistration.json` for all three. Exact child commands and output are in each phase log at lines 55-81.

| Revision | Pristine / all four restored runs | Horizon mutant | Author mutant | Ignore-seconds mutant | Skip-no-Z mutant |
|---|---:|---:|---:|---:|---:|
| a4a159c39967e88a89b0808dcd201c79c474efd1 | 1 | 1 | 1 | 1 | 1 |
| a12850c5cbc1013e60cc5bba2d6800d1cd634499 | 1 | 1 | 1 | 1 | 1 |
| f071209a0f956680b5722e09242e784a1644e216 | 0 | 0 | 0 | 0 | 0 |

Pristine flags `03:45Z` by 1569 seconds at the freeze, flags `03:45Z` / `03:55Z` by 1517 / 2117 seconds at A0, and passes the corrected `03:18:51Z` / `03:19:43Z` values. These reproduce the landed lesson's historical claim. Merely asserting `1, 1, 0` does **not** kill any of these four mutants.

## Round-25 amendments at introducing revisions

Introduction commits were obtained with read-only `git log --diff-filter=A --name-status` on the five preregistration paths. Pristine results below are in `E/pristine.txt:95-140`; every mutation and restoration ran the same checks.

| File under `.ufo/waves/round-25/` | Introducing revision | Commit time UTC | Actual flags / exit |
|---|---|---|---|
| preregistration.json | efe58e96e6cfbef88a0fba9d64505e18b7ad7356 | 08:29:44 | line 5 `08:31:00Z`, +76 s; exit 1 |
| preregistration-amendment-1.json | efe58e96e6cfbef88a0fba9d64505e18b7ad7356 | 08:29:44 | line 5 `08:30Z`, +16 s; line 10 `08:31:00Z`, +76 s; exit 1 |
| preregistration-amendment-2.json | 5388b7cf1d5bad9c228da6f95c40f323414be2f1 | 09:28:44 | line 6 `09:30Z`, +76 s; exit 1 |
| preregistration-amendment-3.json | c808ba07f09c4be55413d3d6516c542ab69b64f8 | 09:38:45 | line 6 `09:40Z`, +75 s; exit 1 |
| preregistration-amendment-4.json | 46fb04bd54978a2a3c47b3da098a2526804014e0 | 09:42:31 | line 6 `09:38:47Z` and line 19 `09:28:44Z` both before commit; exit 0 |

All dates in that table are 2026-10-22. No pristine whole-file false pass or false fail was observed under the documented all-Z-timestamps predicate. None of the four mutants changes those whole-file exits. The author mutant does corrupt original/amendment-1 clock diagnostics (for example amendment-1 +19230 / +19290 s instead of +16 / +76 s), which the fixed detector rejects (`E/author-time.txt:104-111`).

Important semantic limit: amendment 1 line 10 explicitly quotes and retracts the original false timestamp. That additional flag is not evidence of a second new clock guess. The scanner is lexical, not a semantic truth checker. The whole amendment still independently fails because its own line 5 is 16 seconds after the introducing commit; this is not a whole-file false fail. Amendment 4's correction text passes. This probe did not infer filesystem write times from commit times.

## Smallest corrections to the coverage findings

1. `tools/prereg-time-check.py:144-150,170-176`: all shipped selftest commits give author and committer identical dates. Add one case with distinct author/committer dates (the clean supplemental fixture above) and expect exit 0. Alternatively preserve the a4a159c3 clock/delta assertion; exit-only historical checks are insufficient.
2. `tools/prereg-time-check.py:192-193`: the seconds-precision case has seconds `00`. Add the same-minute `03:19:59Z` case against the existing `03:19:43Z` commit and expect exit 1. This is a two-line extra `case(...)` call; no checker-contract change is needed.
3. Horizon removal is already covered. The no-Z prescreen is equivalent. No production correction is recommended for either.

These are advice only; no tests, implementation, lesson or frozen predicate were changed.

## Hashes and restoration

Before each mutant and after each reversal the checker had original hash `3d508f776e5b8fac2685dcb80f5bb5c3865427baec3046c4f5b51bed336358c1`.

| Mutant phase | Mutated sha256 | Restored detector exit |
|---|---|---:|
| drop-horizon | 6416ea3f7675261b64ed3ccd5f586b77a201f625398f2c2c638ce5aedc6b82ec | 0 |
| author-time | 162a3705488628bea14c64afbf44288bc743e4d255aa28db98eaa25b7f2ce5d9 | 0 |
| ignore-seconds | eafcae88c3ed63fe78b18cf6590dde35bed24975841d0ed8ba01beea13cd4272 | 0 |
| skip-no-Z | f5ce5d8040ec9994dddc11f9a2e1106f115e0fe23a08f8a3a06c3c70492a5b6b | 0 |

`E/restoration.txt` records the exact initial/final `sha256sum` commands, outputs and exit 0. Final lane and scratch checker hashes are identical to the initial hash. All four restored runs passed all 12 fixed detector cases. No inconclusive run is counted as a kill.

No server was started, no port opened, no frozen counter or other runtime invoked, no tool installed or updated. Cleanup command `timeout 10 pgrep -af '/fast/scratch/hyaku/kama-r26w2/Mut[P]reregTimeCheck'` returned no output, exit 1. The separate llama-server process observation is recorded in `E/restoration.txt`; the unrelated peer process was not signalled.

## Files written

The complete authored/workload path list is `E/writes-manifest.json` (37 named files), including this report and the manifest itself. Lane evidence consists of `E/{pristine,drop-horizon,restored-horizon,author-time,restored-author,ignore-seconds,restored-seconds,skip-no-Z,restored-no-Z}.{txt,json}`, plus `E/summary.json`, `E/probe.py`, `E/boundary-fixtures.json`, `E/restoration.txt`, and `E/writes-manifest.json`.

Scratch files are `S/probe.py`, `S/boundary-fixtures.json`, `S/boundary-fixtures/f.json`, the restored `S/work/tools/prereg-time-check.py`, and the nine selftest `f.json` paths individually named in the manifest. Git-generated state remains only in `S/history.git`, `S/boundary-fixtures/.git`, and those selftest repositories' `.git` directories. No lane production file, lane Git index or sibling source was written.
