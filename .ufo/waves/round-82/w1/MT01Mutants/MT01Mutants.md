# MT01 — mutant battery on round-82's two new modules

Seat MT01Mutants (mutation-tester), kama round-82 wave w1. Lane
`/home/vgpnk/Projects/shokunin/kama-shokunin`. Scratch root
`/fast/scratch/hyaku/kama-r82/MT01Mutants`, deleted before this report (verified absent).

**Verdict: 8 of 9 named mutants killed, 1 escape.** Honest modules green. All three round-82
row-introduction arms of `tools/round81-append-debt.py` proved red-capable.

## Bind

- Copies taken at `master = bacae0726d7c53455bd083bc6d478bbcd6e7fffc`; the L1 advanced the tip
  mid-run (`bacae0726d7c` → `4beb4f2b29d1` → `384ef1d5bcbf`) and the four module blobs are identical
  at every one of those tips.
- Blob ids at copy (worktree == tip): `round82-selfrecord-round81.py` `c1e08b30…`, `round82-late-delta.py`
  `efcc3017…`, `round81-append-debt.py` `965c2ee5…`, `round81-late-rows.py` `5ece45e9…`.
- sha256 of the pristine copies: selfrecord `381e8639b4d976f803462441de95b340a1bbf872d5bbb0b875c722fe1975c526`,
  late-delta `8d761ccd99fb30f0f808efbc3c00b26d372550ee3800f660cb1ffab328486e3d`,
  append-debt `93d23989654edd5f388ffc2378e5ec2f94adcba330afa6f9c025b5ee4a149540`,
  late-rows `0c2dce1c675c5c775cc9b4ba5ea8f7ba4165ac4cf2d170e66a2405c1a0292106`.

## Method

`$S/pristine/tools` copy → one named textual mutation (asserted to occur exactly once and to change
the bytes) → `python3 <mutant> --selftest` → restore the pristine file by copy → sha256 equality
check → `--selftest` again. No lane module was edited; the lane was never a write target. Each
mutant ran in its own `$S/mut/<id>/` workdir holding a full `tools/` copy, so the late-delta
`generator-import` arm had its real `tools/round81-late-rows.py`.

## Honest tallies (same bytes, before the battery)

| command | exit | tally |
|---|---|---|
| `python3 <pristine>/tools/round82-selfrecord-round81.py --selftest` | 0 | `SELFRECORD_R81_SELFTEST pass=19 fail=0` |
| `python3 <pristine>/tools/round82-late-delta.py --selftest` (cwd `$S/pristine`) | 0 | `LATE_DELTA_SELFTEST pass=12 fail=0` |
| `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round81-append-debt.py --selftest` | 0 | `APPEND_DEBT_SELFTEST pass=25 fail=0` |

## Named mutants

All mutant detector runs used `--selftest`; "red" = at least one arm printed `FAIL` (desired).

| mutant | mutation | exit | tally | red arms | restored |
|---|---|---|---|---|---|
| `selfrecord/delete-at-check` | removed `if at != sealed` from `grade()` | 1 | 18/1 | `wrong-at` | exact, 19/0 |
| `selfrecord/delete-fix-token-check` | removed the `fix` tip-bytes token test | 1 | 18/1 | `fix-without-token` | exact, 19/0 |
| `selfrecord/startswith-token-compare` | `old`/`new` compared by prefix (`declared.startswith(old)`, `witness.startswith(new)`) | 0 | 19/0 | none | exact, 19/0 |
| `selfrecord/whole-lesson-corrections` | `corrections()` scans the whole lesson, not `## Corrections` | 1 | 18/1 | `correction-outside-container` | exact, 19/0 |
| `selfrecord/holding-correction-valid` | a correction for a holding fact counts as corrected | 1 | 18/1 | `correction-for-holding-fact` | exact, 19/0 |
| `late-delta/drop-carried-bytes` | carried rows no longer compared to base bytes | 1 | 11/1 | `carried-rewritten` | exact, 12/0 |
| `late-delta/accept-equal-round` | `accepting <= deletion` → `accepting < deletion` | 1 | 11/1 | `note-not-later` | exact, 12/0 |
| `late-delta/skip-extra-scan` | extra-row scan deleted | 1 | 11/1 | `extra` | exact, 12/0 |
| `late-delta/first-two-cells-only` | new-row cells compared on `(commit, file)` only | 1 | 10/2 | `wrong-count`, `wrong-class` | exact, 12/0 |

Survivor sets per mutant (all arms except the red ones listed) are enumerated arm-by-arm in
`MT01.json` → `named_mutants.<id>.surviving_arms`. Full per-arm PASS lines are in `MT01.raw.json`.

## Escape — `selfrecord/startswith-token-compare` (headline)

- Detector: `--selftest` exit 0, `SELFRECORD_R81_SELFTEST pass=19 fail=0`, no red arm → every arm
  green, i.e. an escape. Mutant sha256 `c6891b002fe7369c3bfa366a9b7e915ab28ebaa60f6d2c937825f369474c89e3`
  vs pristine `381e8639…` (bytes really changed).
- Semantic liveness probe (`grade()` called directly on a dedicated mutant copy):
  - declared `sc81c2-pending=12`, correction `old=sc81c2-pending=1` → honest `mismatches=1 corrected=0
    unbacked=1` (row `unbacked-correction`); mutant `mismatches=0 corrected=1 unbacked=0` (row `corrected`).
  - witness `sc81c2-pending=44`, correction `new=sc81c2-pending=4` → honest `1/0/1`; mutant `0/1/0`.
- End-to-end on the live lane, same tip: honest and mutant bytes both print
  `SELFRECORD_R81 claims=6 mismatches=0 corrected=5 unbacked=0`, exit 0 — identical graded output.
- Meaning: the C1 predicate binds the correction tokens by **exact** equality (`old` is the sealed
  declared token, `new` equals the tip witness token). The shipped control set cannot distinguish
  exact from prefix equality, so a truncated/prefix token is accepted by the mutant with no arm going
  red and no graded line changing. This is a coverage finding, not permission to change the contract:
  the fix is two selftest arms where `old` is a strict prefix of the declared token and where `new` is
  a strict prefix of the witness, each required red. No lane file was changed by this seat.
- Correction to my own run, recorded: the first probe pass pointed at workdirs the battery had already
  restored, so it reported honest behaviour for both; the numbers above come from the re-run on a
  dedicated mutant copy (`probe.py`).

## Row-introduction arms of `tools/round81-append-debt.py`

Present, named from source (`tools/round81-append-debt.py:479-493`, selftest arms 21–23):
`row-intro-later` (a row appended after the register's introduction accepts a post-register event),
`row-intro-earlier` (a row introduced before the event is refused, class `not-descendant`),
`row-intro-unbound` (no resolvable row introduction → class `unbound-register`).
Bonus mutants (supplementary, not in the item's named set):
`debt/register-level-intro` (row_intro ignored, pre-repair shape) → `pass=23 fail=2`, red
`row-intro-later`, `row-intro-unbound`; `debt/no-descendant-check` (`if False:`) → `pass=23 fail=2`,
red `same-commit`, `row-intro-earlier`. All three new arms are red-capable.

## Restoration and scratch evidence

- Every mutant workdir was restored from the pristine copy; sha256 equals the pristine hash for all
  nine mutants and both bonus mutants, and the re-run tallies are green (19/0, 12/0, 25/0).
- Post-battery pristine sha256 equals the pre-battery value
  (`pristine_unchanged_after_battery: true` in `MT01.json`).
- `$S` deleted: `test ! -e /fast/scratch/hyaku/kama-r82/MT01Mutants` passes.

## Lane write audit

No production file, registry, corpus, scorecard, log, plan or fleet-root path was written.
`git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain` before the battery:
` D .ufo/waves/round-82/w1.ready.partial` and `?? .ufo/waves/round-82/w1.ready.dispatched` (dispatch
state, present at start); after: the same two plus `?? .ufo/waves/round-82/w1/SC03Knowledge/`, a
sibling seat's directory, not mine. Tooling installs: none (no pacman/uv/npx transaction was run).

## Receipts (absolute paths)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/MT01Mutants/MT01.json` —
  mutant → red arms → surviving/escaped arms, hashes, tallies, probe, bonus mutants.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/MT01Mutants/MT01.raw.json` —
  raw battery, probe and debt-bonus records.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/MT01Mutants/MT01.md` —
  33-line summary.
- `MT01Mutants.md` — this report.

Commands and exit codes: honest selftests exit 0 (tallies above); `python3 $S/mutate.py` exit 0
(nine detectors: eight exit 1 with one or two red arms, one exit 0 all-green); `python3 $S/probe.py`
exit 0 (two probe cases); the two inline bonus-mutant drivers exit 0 (each detector exit 1);
honest and mutant `--repo <lane>` runs exit 0 with identical output.

## Limits

- The detector is each module's own `--selftest`, the control the round ships; a mutation that keeps
  that output green is an escape by definition here, even if a separate hidden oracle could see it.
- Mutants other than `selfrecord/startswith-token-compare` were not run end-to-end against the lane:
  their arms are selftest-local by construction (fixture `read_map` / synthetic rows), so end-to-end
  runs would add no discriminating power.
