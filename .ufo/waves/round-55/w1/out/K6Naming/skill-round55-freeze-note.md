Proposed append to `SKILL.md` (after the round-54 registry table, end of file).
This is a registry note, not a rename: the `round54-*` filenames keep their
round-54 draft provenance and stay valid for the frozen preregistration's
counting commands, the committed receipts and the frozen sha256 pins.

```markdown
### Round-55 freeze note (owner: kama)

The two counters named above were drafted in round 54 (commit `9a3104c7`, an
honest stop with claims unfrozen) and re-frozen for round 55 at `9c60eae6`
under `.ufo/waves/round-55/preregistration.json` — same paths, new bytes
(counter sha256 `c81fe971a0d2…5110579af` C1, `d70a1729174e…a326510c` C2).
The round-54 rows above describe the round-54 drafts; the operative freeze
pins are: C1 `BASE = 3a600d2f` (the round-54 tip; it was `0b75a84c` above),
the newrow source row re-pointed at S511, and every git call stripped of
inherited `GIT_*`; C2 `BASE` stays at the round-53 tip `0b75a84c` (the first
freeze's re-point to the round-54 tip let the do-nothing control pass and was
reverted — `corpus/lessons/round-55.md` §Mistakes), with 15 fixture scenarios
(it was 14 above) including the new `superseded` ledger class. The frozen
measurement for both lives under `.ufo/waves/round-55/{controls,measured,c1/battery}`.
```
