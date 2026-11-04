# SK02 facts — round-82 record at sealed revision b1ba614 (fixed before any round-83 counter was read)

Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`; tip at first read `743c1060…`, at last read `ece8a646…`.
Declared bytes: `git -C <lane> show b1ba614b51255a3dcfe3e0946f32f8e31bd65c09:<path>`; line numbers are
1-based in that blob. Witnesses were run in a scratch clone of the lane checked out at b1ba614, never
in the lane tree; each reproduced its committed receipt line.

| id | file:line | exact declared string | declared | witness (committed receipt at b1ba614) | witness value | verdict |
|---|---|---|---|---|---|---|
| F1 | `LOG.md:3432` (C1 bullet opens :3424) | ``selftest `pass=18 fail=0` `` | 18 | `…/round-82/measured/after/c1-selftest.out` → `SELFRECORD_R81_SELFTEST pass=23 fail=0` | 23 | **stale** |
| F2 | `SCORECARD.md:4970` (§Round 82 C1 row) | ``selftest `pass=22 fail=0` (`measured/after/c1-selftest.out`)`` | 22 | same receipt | 23 | **stale** |
| F3 | `SCORECARD.md:18` (`## Axes` calibration row) | ``and `--selftest` → `pass=22 fail=0` `` | 22 | same receipt | 23 | **stale** |
| F4 | `LOG.md:3436` (C2 bullet opens :3434) | ``` `APPEND_DEBT_SELFTEST pass=22 → pass=25` ``` | 25 | `…/c2-debt-selftest.out` → `APPEND_DEBT_SELFTEST pass=25 fail=0` | 25 | holds |
| F5 | `LOG.md:3444` | `Frontier: registry 302 → 305 rows` | 305 | `corpus/SOURCES.md` registry-row count (command below) | 305 at b1ba614, 305 at tip, 302 at base | holds |
| F6 | `LOG.md:3437-3438` | `LATE_DELTA round=82 base=aaf974dbd3b6 population=103 carried=88 new=15 bad=0` | 15 | `…/c2-late-delta.out` → same line | 15 | holds |

All three stale facts understate the one receipt (`23`) by one arm; F4/F5/F6 reproduce exactly.

## F5 row-count command and its output at both revisions

```
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin show <rev>:corpus/SOURCES.md | grep -c '^| S[0-9]'
b1ba614b51255a3dcfe3e0946f32f8e31bd65c09 -> 305      (declared post-round 305: holds)
master (743c106065363be0cebd1036e6c33d7e6ae632dc) -> 305   (declared count also holds at the tip)
aaf974dbd3b6adb2ef914dc7293cda92b4e05551 -> 302      (declared pre-round 302: holds)
```

`^| ` (all table lines, header + separator included) is 353 at both graded revisions, i.e. 305 data
rows + header + separator. The two revisions are distinguished: 305 at b1ba614, 305 at tip
`743c1060`, re-checked 305 at `ece8a646`; no round-83 registry row has landed yet.

## Witness commands (scratch clone at b1ba614, exit 0 each)

```
python3 tools/round82-selfrecord-round81.py --selftest          -> SELFRECORD_R81_SELFTEST pass=23 fail=0
python3 tools/round81-append-debt.py --selftest                 -> APPEND_DEBT_SELFTEST pass=25 fail=0
python3 tools/round82-late-delta.py --repo . --round 82         -> LATE_DELTA round=82 base=aaf974dbd3b6 population=103 carried=88 new=15 bad=0
```

## Round-83 counter comparison (read only after the six values above were written)

Six sealed facts equal EX03's draft table (18/22/22/25/305/15 declared; 23/23/23/25/305/15
witness) — no value difference. Operational differences (token placement, token boundary) are in
`SK02.json` `differences[]` and `SK02Facts.md`.
