# X9Tally — shortcut tally (round 47, considerthese/2026-10-26 proposal 3)

**Verdict: the running count is buildable, it is monotone in disclosure and flat in
counter hardness — across the rounds that filed a disclosure the number of frozen
counters a shortcut can satisfy is 3, 3, 2, 2, while the number of separately named
shortcut controls rises from 5 (r42) to 8 (r46) and mutation survival falls from
20/53 (38%) to 25/117 (21%); the r43 dedicated falsify wave never ran and the r45
wave produced no reports.** No lane file, counter, preregistration or control was
edited; no tool was installed; the lane was read through a `git clone --shared`
detached at `3a09a1d93dcc16799cf6c4b48786e6440af134c4`.

Deliverable: `.ufo/waves/round-47/w1/out/X9Tally/shortcut-tally.py`
(stdlib only, read-only, 534 lines, sha256
`ae35d7037a6d3a7ba418d13933c17031daaef99164c3d91d28a534c7dfe9626a`). Its module
docstring is the extraction contract; it reads `SCORECARD.md` and
`.ufo/waves/round-4[0-6]/` and nothing else.

## 1. Run at the build tip (clone detached at `3a09a1d9`)

```
$ S=/fast/scratch/hyaku/kama-r47/X9Tally
$ git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
$ git -C $S/lane checkout -q --detach 3a09a1d93dcc16799cf6c4b48786e6440af134c4
$ git -C $S/lane rev-parse HEAD
3a09a1d93dcc16799cf6c4b48786e6440af134c4
$ python3 <out>/shortcut-tally.py --lane $S/lane --rounds 40-46
round  shortcuts  ids                                                        counters  cheats           mutants  falsify              status
40     -          -                                                          -         0                -        yes(w1)              no-disclosure
41     -          -                                                          -         0                -        yes(w1)              no-disclosure
42     5          R42A05,R42A13,R42B05,R42B06,R42C06                         C1,C2,C3  0                -        yes(w1)              ok
43     2          W1R01,W1R02                                                C1,C2,C3  0                20/53    planned-not-run(w2)  ok
44     2          K1Cheat,K2Cheat                                            C1,C2     K1Cheat,K2Cheat  22/79    yes(w1,folded)       ok
45     -          -                                                          -         0                -        stalled(w1)          no-disclosure
46     8          K1Cheat,K1R01,K1R07,K1R10,K2Cheat,K2Hist,V1Code,X2Fixture  C1,C2     K1Cheat,K2Cheat  25/117   yes(w1,folded)       ok
detail: round 42: disclosure SCORECARD.md:2287
detail: round 43: disclosure SCORECARD.md:2333
detail: round 43: mutants SCORECARD.md:2333
detail: round 44: disclosure SCORECARD.md:2395
detail: round 44: M1Ctr .ufo/waves/round-44/w1/out/M1Ctr.md 7/39
detail: round 44: M2Ctr .ufo/waves/round-44/w1/out/M2Ctr.md 1/22
detail: round 44: M3Tool .ufo/waves/round-44/w1/out/M3Tool.md 14/18
detail: round 46: disclosure SCORECARD.md:2658
detail: round 46: M1Ctr .ufo/waves/round-46/w1/out/M1Ctr.md 3/46
detail: round 46: M2Ctr .ufo/waves/round-46/w1/out/M2Ctr.md 12/32
detail: round 46: M2Tool .ufo/waves/round-46/w1/out/M2Tool.md 10/39
exit 0
```

(`tally.out`; a second run is byte-identical, `determinism.diff` empty.)

## 2. It can fail — one invocation per branch

**Shortcut count above the limit** (the required failing invocation):

```
$ python3 <out>/shortcut-tally.py --lane $S/lane --check 7
... table as above ...
latest=46 shortcuts=8 limit=7 result=FAIL (latest round 46 shortcuts=8 > limit 7)
exit 1
```

At the same limit the round-46 disclosure names exactly 8 controls, so the
instrument is sensitive to its own measurement, not just to a hardcoded bound:

```
$ python3 <out>/shortcut-tally.py --lane $S/lane --check 8 | tail -1
latest=46 shortcuts=8 limit=8 result=PASS
exit 0
```

**Data for a round unreadable, even with a limit of 99** (two constructed fixtures
under `$S`, never in the lane):

- `fix1`: the clone's `SCORECARD.md` with the `## Round 44 — ` heading deleted.
  `round 44` → `unreadable:no-section`;
  `latest=46 shortcuts=8 limit=99 result=FAIL (unreadable rounds [44])`, exit 1.
- `fix2`: the clone's round-46 `M2Tool.md` verdict changed from
  `**10 survived with demonstrated pristine-vs-mutant divergence**` to
  `**10 mutants with demonstrated pristine-vs-mutant divergence**`.
  `note: round 46: .ufo/waves/round-46/w1/out/M2Tool.md: no survived count`,
  round 46 → `unreadable:mutation-report`, mutants `-`;
  `latest=46 shortcuts=8 limit=99 result=FAIL (unreadable rounds [46])`, exit 1.
- A lane root without `SCORECARD.md` exits 2
  (`shortcut-tally: no SCORECARD.md under ...`, `usage-nonexistent-lane.out`).

## 3. What the tally says (calibration read)

- **Counter hardness is flat; disclosure is what grew.** Shortcut-satisfiable
  counters: r42 `C1,C2,C3` (`SCORECARD.md:2287`), r43 `C1,C2,C3`
  (`SCORECARD.md:2333`), r44 `C1,C2` (`SCORECARD.md:2395`), r46 `C1,C2`
  (`SCORECARD.md:2658`). No round retires a shortcut path; rounds 44 and 46 have
  one fewer claim because they run two claims, not because a shortcut was closed.
- **Named controls per round: 5 → 2 → 2 → 8.** r46's eight are
  `K1Cheat` (91/91 rows greened from git alone), `K1R01`–`K1R10` critics (range
  endpoints counted), `K1R07` (flag-leg blind spot), `V1Code`
  (`check-fragment.py` VALID for an out-of-population id), `K2Hist` and
  `X2Fixture` (shared `--`-prefix definition; 7 fixtures where tool and counter
  agree and both differ from the oracle), `K2Cheat` (three non-capabilities at
  `met=True`). Rising disclosure is not the same number as rising exposure: the
  r42 count includes one named control (`R42B05`) that is a tool review rather
  than a cheat.
- **Mutation survival falls, but the denominators are not comparable.** r43
  20/53 (`SCORECARD.md:2333`, report W1R03 outside the M\* family), r44 22/79
  (7/39 C1 counter + 1/22 C2 counter + 14/18 tool), r46 25/117
  (3/46 + 12/32 + 10/39). Absolute survivors rose 20 → 25; the share fell 38% →
  21%. Different batteries (counter vs tool, 18 to 46 mutants), so this is a
  trend in the record, not a like-for-like hardness metric.
- **Falsify waves.** r40–r42 ran a falsify-and-verify wave (`yes(w1)`); r43's
  dedicated `wave 2 = FALSIFY` has a dispatch record (48 spawn in
  `.ufo/waves/round-43/w2/dispatch.json`) but no seat wrote a report
  (`planned-not-run(w2)`, matching `SCORECARD.md:2333` "was not dispatched");
  r44 and r46 fold the attacks into the one v2 wave (`yes(w1,folded)`); r45's
  wave dispatched with no reports (`stalled(w1)`, matching
  `SCORECARD.md:2441` "The planned wave did not run (dispatch stalled at 32 of 64
  spawned)").
- **Three rounds filed no disclosure at all** (r40, r41, r45). For r41 the wave
  did record a cheap-edit shortcut (`R41A06`), and the round section says the
  counter "can be met by low-cost edits"; no `met=True` paragraph consolidated
  it. The tally shows `-`, not `0`: the distinction matters, and the script keeps
  it (`no-disclosure` ≠ shortcut-free).

## 4. Limits of this instrument (stated, not hidden)

1. `shortcuts` counts **named controls**, not variants: `K2Cheat`'s three
   non-capabilities and `K1Cheat`'s eight scored variants each count once. The
   `counters` column is the stricter, proposal-text unit ("counters that a
   shortcut can satisfy").
2. A control named in the same sentence as a mutant battery is excluded, so
   r46 `M2Ctr` — which also reports that "the pristine counter accepts a tool
   whose default threshold is 21" (`SCORECARD.md:2658`) — is not counted while
   `M2Tool` and `M1Ctr` are mutation seats only. This undercounts by one.
3. `K1R01–K1R10` is a printed range: only its two endpoints are ids, so the
   r46 count of 8 would be 15 if the range were expanded (K1R01-K1R10 plus
   K1Cheat, K2Cheat, K2Hist, V1Code, X2Fixture).
4. Mutant totals sum batteries of different sizes and kinds (counter vs tool);
   read them per round, not as one series.
5. `falsify` is a wave-shape signal: "ran" means a report file exists under the
   wave's `out/`. It does not measure attack completeness (r43's wave 1 filed
   four early falsifiers and is reported only through the r43 paragraph).
6. The mutant pairs for rounds without `M*Ctr/M*Tool` reports come from the
   disclosure prose (`SCORECARD.md:2333` for r43); a prose pair with two
   different values is `unreadable`, not a guess.
7. Round 47 is in flight and outside `--rounds 40-46`; the script does not read
   its own wave.

## 5. Scoped findings outside the deliverable

- **The disclosure practice is not round-symmetric.** Rounds 40 and 41 ran
  shortcut attacks and filed no `met=True` paragraph; the practice starts at
  round 42. A tally cannot compare rounds that do not disclose, so the series
  phrase "counter design getting harder" is only measurable from r42.
- **No defect found in the frozen round-47 counters, preregistration or
  controls.** This seat did not score them; the only lane surface read was
  `SCORECARD.md` and `.ufo/waves/round-4[0-6]/`.

## 6. Reproduction

```sh
S=/fast/scratch/hyaku/kama-r47/X9Tally; mkdir -p "$S"; export TMPDIR="$S"
git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
git -C "$S/lane" rev-parse --show-toplevel   # must print $S/lane
git -C "$S/lane" checkout -q --detach 3a09a1d93dcc16799cf6c4b48786e6440af134c4
P=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X9Tally/shortcut-tally.py
python3 "$P" --lane "$S/lane" --rounds 40-46          # table, exit 0
python3 "$P" --lane "$S/lane" --check 7               # exit 1 (8 > 7)
python3 "$P" --lane "$S/lane" --json                  # records, exit 0
```

Read-only on the lane; no git mutation outside the scratch clone; no service
started; no tool installed or upgraded; `/tmp` unused. The clone and both
fixtures were removed (`rm -rf "$S"`).

## 7. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X9Tally/shortcut-tally.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X9Tally.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X9Tally/tally.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X9Tally/tally.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X9Tally/check-fail.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X9Tally/check-pass.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X9Tally/unreadable-nosection.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X9Tally/unreadable-report.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X9Tally/usage-nonexistent-lane.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X9Tally/run.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X9Tally/exit-tally.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X9Tally/exit-check.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X9Tally/determinism.diff`
