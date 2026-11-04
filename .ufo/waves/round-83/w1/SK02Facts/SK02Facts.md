# SK02 — independent re-derivation of the six round-83 facts (scout, read-only)

Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`; sealed revision C2 grades
`b1ba614b51255a3dcfe3e0946f32f8e31bd65c09`; lane tip `743c1060…` at first read, `ece8a646…` at last.
All declared bytes came from `git -C <lane> show <rev>:<path>`; the lane tree was never edited.
The six values were derived from the sealed blobs and written to `facts.md`; the plan's §C2 table and
the EX03 draft were read only afterwards (one bare `grep -n C2` locator over the plan file was issued
in the same tool batch as that write, returning locating line hits). Witness runs used a scratch clone
of the lane at b1ba614 (`$S/clone`), never the lane.

| id | file:line at sealed | declared | witness | verdict |
|---|---|---|---|---|
| F1 | `LOG.md:3432` (C1 bullet :3424) | `selftest \`pass=18 fail=0\`` | `c1-selftest.out` → `SELFRECORD_R81_SELFTEST pass=23 fail=0` | **stale** 18≠23 |
| F2 | `SCORECARD.md:4970` (§Round 82 C1 row) | `selftest \`pass=22 fail=0\`` | same receipt → 23 | **stale** 22≠23 |
| F3 | `SCORECARD.md:18` (`## Axes` calibration row) | `--selftest` → `pass=22 fail=0` | same receipt → 23 | **stale** 22≠23 |
| F4 | `LOG.md:3436` (C2 bullet :3434) | `APPEND_DEBT_SELFTEST pass=22 → pass=25` | `c2-debt-selftest.out` → `APPEND_DEBT_SELFTEST pass=25 fail=0` | holds 25=25 |
| F5 | `LOG.md:3444` | `Frontier: registry 302 → 305 rows` | SOURCES registry-row count | holds 305=305 |
| F6 | `LOG.md:3437-3438` | `LATE_DELTA … population=103 carried=88 new=15 bad=0` | `c2-late-delta.out` → same line | holds 15=15 |

Every declared token is unchanged at the tip as well (the round-82 filed bytes are not rewritten).

## F5 row-count command and both revisions

```
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin show <rev>:corpus/SOURCES.md | grep -c '^| S[0-9]'
b1ba614b51255a3dcfe3e0946f32f8e31bd65c09   -> 305   (declared post-round 305: holds)
master 743c106065363be0cebd1036e6c33d7e6ae632dc -> 305
master ece8a6468641a833caf65ab46dc0fa4377e2f4f5 -> 305   (no round-83 registry row yet)
aaf974dbd3b6adb2ef914dc7293cda92b4e05551   -> 302   (declared pre-round 302: holds)
```

`^| ` (header + separator + data rows) is 353 at both graded revisions = 305 data rows + 2.

## Witness commands (scratch clone at b1ba614; each exit 0)

```
python3 tools/round82-selfrecord-round81.py --selftest   -> SELFRECORD_R81_SELFTEST pass=23 fail=0
python3 tools/round81-append-debt.py --selftest          -> APPEND_DEBT_SELFTEST pass=25 fail=0
python3 tools/round82-late-delta.py --repo . --round 82  -> LATE_DELTA round=82 base=aaf974dbd3b6 population=103 carried=88 new=15 bad=0
```

The committed receipts at the same revision print the same three lines, and the three receipt
files are byte-identical at b1ba614 and at the tip (sha256 equal).

## Comparison with EX03's draft table

Draft `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/EX03SelfRecord/round83-selfrecord-round82.py`:
`old_values [18,22,22,25,305,15]`, `new_values [23,23,23,25,305,15]`. **No value difference** — the
draft's six declared/witness values and its stale/holds partition equal this seat's. Compared bytes
sha256 `62bd3dcd88f0…`; the L1's `tools/round83-selfrecord-round82.py` is byte-identical at read.
At the current tip its honest run is red as expected (no corrections landed yet): `mismatches=3 corrected=0`, exit 1;
`--enumerate` prints `stale=3`, exit 1; `--no-corrections` prints `mismatches=3`, exit 1; `--selftest`
prints `pass=16 fail=0`, exit 0.

Four operational differences against the plan prose, all exercised in a scratch clone:

1. **Placement.** Tokens only in the regions the plan names (a `LOG-CORRECTION` line; the
   `#### round-83 correction` block) are stripped as restatements and grade all three corrections
   `unbacked`: `claims=6 mismatches=3 corrected=0 unbacked=3`, exit 1. The target line is reachable
   only with each token also in its fix path outside those regions: `claims=6 mismatches=0 corrected=3
   unbacked=0`, exit 0.
2. **Token boundary.** `whole_token` rejects a token followed by `.` (also `-`, `_`, `~`, `=`, alnum);
   space, comma, `)` and EOL pass. `calib82-selftest=23.` at sentence end grades unbacked.
3. **Block extent.** A `#### round-N correction` block appended at EOF runs to EOF; a token line after
   it with no heading of level ≤4 is stripped too. A `## …` heading resets the region.
4. **Sealed/tip binding.** Declared tokens are read at the sealed revision; witnesses at the tip; F5's
   population at the sealed revision per the plan's freeze bind — no value effect today because the
   receipts are byte-stable, and the sealed bind is what will keep F5 at 305 once round-83 rows land.

## Receipts (absolute; command and exit as recorded)

| receipt | command | exit |
|---|---|---|
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/SK02Facts/tip-honest.out` | draft `--repo <lane>` at `ece8a646…` | 1 |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/SK02Facts/tip-enumerate.out` | draft `--enumerate` | 1 |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/SK02Facts/tip-nocorr.out` | draft `--no-corrections` | 1 |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/SK02Facts/tip-selftest.out` | draft `--selftest` | 0 |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/SK02Facts/reach-A.out` | clone fixture `01f9f56c` (plan-prose placements) | 1 |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/SK02Facts/reach-B.out` | clone fixture `66c33707` (F3 token + `.`) | 1 |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/SK02Facts/reach-C.out` | clone fixture `979e6a7b` (tokens backed) | 0 |

Scratch root `/fast/scratch/hyaku/kama-r83/SK02Facts` is deleted before yield; no tool was installed.
