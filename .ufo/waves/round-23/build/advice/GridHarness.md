# GridHarness: round-23 repo-state fault grid (advice)

Seat: CloseKama22.GridHarness. Base: master 4fe9339f8fc3a4a4a479d9c938a850da12f1124d.

## Status

- Harness written: `tests/report-audit/repo-state-grid.py` in my clone `/tmp/kama-r23/GridHarness` (sha256 `c11cf56839420d741229072635bdd4cfc1d628da117077cc2aa20266fe43ec07`).
- Population SHA256 (pinned in the script): `7be080caa14787f531e24f807f196037023a30fa5a67b81ebd58e40f4545de0a`, over the 23 case rows.
- NOT executed. Per the wave rule I ran neither the grid nor `--selftest`. The only execution was an import of the module to compute the pin; the grid code paths are unexercised. Gate results are unmeasured.

## Interface

- `--arm frozen|current|both` (default `both`). `--current PATH` is resolved to an absolute path at startup and is rejected with exit 2 under `--arm frozen`.
- `--repo PATH`: git repository holding commit 4fe9339f (default: the repo containing `tests/`). The copy in `out/` needs `--repo`.
- `--json`, `--keep`, `--selftest`.
- Exit 0: the gate holds. Exit 1: the gate is violated. Exit 2: cannot evaluate (pin mismatch, frozen blob mismatch, missing current file, git setup failure, usage).
- Gates over graded rows (fault, guard, control):
  - `frozen`: every graded row meets its correct-auditor expectation. Expected 1, since frozen is the pre-fix auditor.
  - `current`: every graded row meets its correct-auditor expectation.
  - `both`: current meets every graded expectation, AND frozen violates every fault row, AND control rows have identical outcomes on both arms. Pre-fix this is 1 because current equals frozen at base; post-fix it is 0 if the fix lands and the frozen blob is unchanged.
- Per row and arm: verdict, exit, traceback, marker (a planted command ran), timed_out, sorted defect kinds, and summary status.
- Each auditor run has a 30 s limit. On timeout the process group is SIGKILLed and the verdict is `hang`.
- Fixtures: each arm gets fresh lane and fleet repos under `mkdtemp` (/tmp). Every git call runs with `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1` and no inherited `GIT_*`. Every commit, `commit-tree` and `hash-object` sets an explicit identity through the environment. Every git write is checked, so a failed write raises (exit 2) instead of passing silently.
- The promisor and gpg fixtures point at `ssh://example.invalid` and planted trap scripts. No real network host is used.

## Case table (correct-auditor expectation)

| case | kind | expectation | fixture |
|---|---|---|---|
| C1-clean | control | exit 0, [] | clean report, round commit cited |
| C2-omitted-round-commit | control | exit 1, [landed-omitted] | uncited round-1 commit (t=1200) |
| C3-unresolved-full-hash | control | exit 1, [unresolved-full-hash] | fabricated 40-hex in Notes |
| C4-ambiguous-abbrev | control | exit 1, [landed-ambiguous] | 7-hex Landed token shared by two lane blobs |
| C5-clone-shared-clean | control | exit 0, [] | `git clone --shared` of the clean lane |
| C6-landed-unresolved-abbrev | control | exit 1, [landed-unresolved] | absent `c0ffee1` in Landed (added, not in L1 list) |
| C7-section-missing | control | exit 1, [landed-omitted, landed-section-missing] | no Landed section (added, not in L1 list) |
| F1-logoutputencoding-latin1 | fault | exit 0, [] | `i18n.logOutputEncoding=ISO-8859-1`, non-ASCII subject |
| F2-invalid-utf8-report | fault | exit 2, no traceback | invalid UTF-8 bytes in committed report |
| F3-replace-hides-omitted | fault | exit 1, [landed-omitted] | lane `refs/replace` on omitted commit |
| F4-replace-fabricated-full | fault | exit 1, [unresolved-full-hash] | `refs/replace/<fabricated>` |
| F4b-fleet-replace-report-text | fault | exit 1, [unresolved-full-hash] | fleet replace changes report text; verdict must match unreplaced |
| F5-promisor-sshcommand | fault | exit 1, [unresolved-full-hash], no marker | promisor lane, `core.sshCommand` trap |
| F6-follow-renamed-report | fault | exit 1, [landed-omitted] | `log.follow=true`; first add t=1500, rename t=2500, uncited t=2000 |
| F7-showsignature-program | fault | exit 0, [], no marker | `log.showSignature=true`; `gpg.program` and `gpg.ssh.program` traps; crafted gpgsig commits |
| F8-shallow-hides-omitted | fault | exit 2 | `.git/shallow` hides omitted commit |
| F9-grafts-hides-omitted | fault | exit 2 | `.git/info/grafts` hides omitted commit |
| F10-tag-shadows-branch | fault | exit 1, [landed-omitted] | tag `master` at older commit |
| F11-mailmap-fifo | fault | exit 0, [], no timeout | FIFO at lane worktree `.mailmap` |
| F12-sha256-lane | fault | exit 2 | `git init --object-format=sha256` lane |
| F13-invalid-utf8-errata | fault | exit 2 | invalid UTF-8 committed errata, errata enabled |
| O1-alternates-fabricated | open | observed only | `objects/info/alternates` resolves a citation |
| T1-blob-filtered-partial-clone | tradeoff | observed only | `--filter=blob:none` lane over `file://` origin |

## Frozen identity (exercised)

- `git rev-parse 4fe9339f…:tools/report-landing-audit.py` = `fcc255ce5115a749dfbd09cf992ba9851a2dc90a`.
- sha256 of that blob = `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`. This matches the clone's working file and `git show … | sha256sum`.
- The script pins both values. A mismatch raises exit 2.

## Other exercised checks

- `git init --object-format=sha256` returns rc 0 on git 2.56.0. Python is 3.14.8.
- The module imports, which parses the file and builds the 23-row table. The digest above comes from that import.

## Deviations and decisions for L1

1. C6 and C7 are extra controls beyond the L1 list. They cover the `landed-unresolved` and `landed-section-missing` kinds.
2. `--arm both` is my reading of the spec. Literal "selected arm meets every expectation" cannot hold for `both` while frozen is defective. Please confirm.
3. F11 is kept as `fault`. If frozen does not hang on git 2.56, `both` reports "fault not reproduced by frozen: F11". Reclassify it to guard after the first run if that happens.
4. O1 and T1 are observe-only and never gate.
5. Every fixture was designed from the L1 probe and spec. None has been run, so whether frozen reproduces each one is unknown.

## Unverified risks (the first run decides these)

- F5: the lazy fetch from `cat-file --batch-check` runs `core.sshCommand`. The L1 probe saw this; my fixture is untested.
- F6: `log.follow=true` changes the `--diff-filter=A` cutoff from 2500 to 1500 for the renamed report.
- F7: `hash-object -t commit` must accept crafted gpgsig headers. The SSH path may not invoke `gpg.ssh.program` without an allowed-signers file. If it never runs, the marker is absent on both arms.
- F9: git 2.56 must still honor `.git/info/grafts`. If it does not, frozen gives exit 1 rather than 0; the row still violates.
- F11: depends on whether `log.mailmap` is effectively on by default in git 2.56. Unverified.
- C4: the 7-hex collision search is deterministic and bounded at 2^20 candidates. [INFERENCE] a hit exists in that range; the search raises if none.
- T1: partial clone over `file://` with `uploadpack.allowFilter` and `uploadpack.allowAnySHA1InWant`.

## Checks the main agent should run (not run by me)

1. `python3 tests/report-audit/repo-state-grid.py --selftest`. Expect exit 0.
2. `python3 tests/report-audit/repo-state-grid.py --arm frozen --json`. Expect exit 1, every fault row violated and every control row met.
3. `python3 tests/report-audit/repo-state-grid.py --arm both` at base. Expect exit 1, because current equals frozen.
4. After the fix: `python3 tests/report-audit/repo-state-grid.py --arm both --current /abs/path/tools/report-landing-audit.py`. Expect exit 0.
5. Read-only probe of the lane WIP: `--arm current --current /home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py`.

## Lane observations (not from this seat)

- The lane checkout has untracked files `tests/report-audit/isolation-mutants.py` (12:25) and `tests/report-audit/repo-state-grid.py` (27306 bytes, 12:26). I wrote neither. My harness is only in my clone and in `out/GridHarness/`. Do not integrate the lane copy as this seat's work.
- The lane's `tools/report-landing-audit.py` has uncommitted working-tree edits, including a `GIT_ISOLATION` tuple. They are not in my clone, which is at HEAD 4fe9339f. The fifth command above exercises them read-only.

## Peer exchange

- ScoutRecipeInventory was answered: `both` is 0 post-fix, `--selftest` exists, and `--current` is absolute. Frozen with `--current` is a usage error.

## Files written

- `/tmp/kama-r23/GridHarness/tests/report-audit/repo-state-grid.py` (clone; sha256 `c11cf568…3ec07`).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/out/GridHarness/repo-state-grid.py` (copy, same sha256).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/out/GridHarness/repo-state-grid.patch` (`git diff --no-index /dev/null …`, 801 lines).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/advice/GridHarness.md` (this report).
- Removed afterwards: the empty stray `out/` in my clone and the `__pycache__` created by the import.

## Installs and updates

None.

## Addendum (appended after the first write)

Two robustness edits landed after the sections above were written. Malformed audit JSON now maps to unknown defects, and an unexpected harness exception now exits 2. Neither edit touches the case table, so the population SHA256 is unchanged. The current script is 803 lines with sha256 `141c0c2c8e4dee11db35af05e725edd901b07e562f07294fed25cfd1f9482be1`. The clone and `out/GridHarness/` copies are identical, and the patch in `out/GridHarness/` is regenerated. The sha256 `c11cf568…` quoted in the Status and Files sections is superseded. `--selftest` and the grid run remain unexecuted.
