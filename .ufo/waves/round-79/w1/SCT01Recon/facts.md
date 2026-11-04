# SCT01 — six C1 facts re-derived by hand from committed bytes

Seat: SCT01Recon (round 79, wave 1, scout). Read-only: every derivation below is
`git show`/`git rev-parse`/`git ls-tree` against
`/home/vgpnk/Projects/shokunin/kama-shokunin`; no derivation wrote a lane file.

- Sealed revision: `7a3cd98243b69fcbee0cc9e31878782bd8459320` (round 78 tip)
- Lane tip at this seat's run: `f7442dea53bd8f474293a2252437b5d869801f49` (`git rev-parse master`)
- Counter: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round79-selfrecord-round78.py`
- Frozen value strings: `plans/round-79-claims.md` §C1 table

All commands below were run from `/fast/scratch/hyaku/kama-r79/SCT01Recon` (scratch; deleted at
yield) with `L=/home/vgpnk/Projects/shokunin/kama-shokunin` and
`SEALED=7a3cd98243b69fcbee0cc9e31878782bd8459320`.

## F1 — lowest assigned axis

Record sentence (sealed `SCORECARD.md`, `## Round 78`): *"the lowest assigned axis (calibration 7)
carries C1"*.

Command (same regex the counter uses, over the first axes table only):

```
git -C "$L" show $SEALED:SCORECARD.md | awk '/^### Historical axes table/{exit} /^\| *\*{0,2}(operability|freshness|depth|coverage|calibration|adjacency)/'
```

Output (scores parsed): `operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7`.
Assigned pair = `(operability, calibration)`; min = `calibration 7`.

- Counter observed value: `lowest-axis=calibration:7`
- Counter declared value: `lowest-axis=calibration:7`
- Frozen plan value string: `lowest-axis=calibration:7`
- **Match: yes (fresh).**

## F2 — population

Record sentence (sealed `SCORECARD.md`, `## Round 78`): *"Population at `rev=773c8abe`: sources
registry 292 rows …; filtered knowledge entries 51 (two new: `append-registers-at-the-tip`,
`live-reconcile-trial`); `SKILL.md` sha256 `a50f6f74…` (1736 lines …); `PROVINCE.md` sha256
`6b8c604f…` (331 lines …)"*.

Commands and output:

```
git -C "$L" show $SEALED:corpus/SOURCES.md | grep -cE '^ {0,3}\| *S[0-9]{3,}'
→ 292
git -C "$L" ls-tree -r --name-only $SEALED -- corpus/knowledge | grep -c '\.md$'
→ 53
… | grep '\.md$' | grep -v -e 'engine-sides' -e 'processes' | wc -l
→ 51
git -C "$L" show $SEALED:SKILL.md | sha256sum
→ a50f6f7445402de8f09d52d9fa1fb2d3017769ec4ea372ff4bd3baa036df672d
git -C "$L" show $SEALED:SKILL.md | python3 -c 'import sys;print(sys.stdin.buffer.read().count(b"\n"))'
→ 1736
git -C "$L" show $SEALED:PROVINCE.md | sha256sum
→ 6b8c604f045d7275aa77e8788ba318e7cf51dfbc2ae29ffed4564cb34edcd3c9
git -C "$L" show $SEALED:PROVINCE.md | … newline count
→ 331
```

- Counter observed value: `population=sources:292,knowledge:51,skill:a50f6f74/1736,province:6b8c604f/331`
- Counter declared value: same string
- Frozen plan value string: same string
- **Match: yes (fresh).**
- Note: the record names `rev=773c8abe`; the counter never parses or resolves that revision — it
  derives every component at the *sealed* revision. The numbers happen to be identical at both.

## F3 — wave shape

Command:

```
git -C "$L" show $SEALED:.ufo/waves/round-78/w1-spec.json
```

Output (counted): `items` = 12 → executor 3, scribe 3, scout 1, connector 1, reviewer 1, critic 2,
mutation-tester 1; attack roles (`reviewer`,`critic`,`mutation-tester`,`labrat`) = 1+2+1 = 4.

- Counter observed value: `wave=seats:12,executor:3,scribe:3,scout:1,connector:1,reviewer:1,critic:2,mutation-tester:1,attack:4/12`
- Counter declared value: same string
- Frozen plan value string: same string
- **Match: yes (fresh).**
- Note: the record's `= 33 %` clause is parsed (`declared["pct"]=33`) but `value("wave", …)` does
  not emit `pct`; the percentage is not part of the graded value string (see insensitivity below).

## F4 — wave dead seats

Command:

```
git -C "$L" show $SEALED:.ufo/waves/round-78/w1-results.json
```

Output: 12 result rows; non-empty `output` for `EX01C1Selfrecord`, `SC02Lesson`, `SCT01Recon`;
empty = 12 − 3 = 9.

- Counter observed value: `wave-dead=returned:3(EX01C1Selfrecord,SC02Lesson,SCT01Recon)/empty:9`
- Counter declared value: same string
- Frozen plan value string: same string
- **Match: yes (fresh).**

## F5 — tip accounting

Record sentence (sealed `SCORECARD.md`, `## Gate and tip state`): *"The tip accounting is the
round-77 counter, which is green at `rev=22cce544`"*.

Commands:

```
git -C "$L" rev-parse 22cce544
→ 22cce544b23670984fa9e42bea673d603881aae7
git -C "$L" merge-base --is-ancestor 22cce544 7a3cd98243b69fcbee0cc9e31878782bd8459320; echo $?
→ 0   (22cce544 is an ancestor of the sealed tip)
[ "$(git rev-parse 22cce544)" = "$(git rev-parse 7a3cd98)" ] → false
```

- Counter observed value: `tip-accounting=rev:22cce544/is-tip:false`
- Counter declared value: `tip-accounting=rev:22cce544/is-tip:true`
- Frozen plan observed: `is-tip:false` (an ancestor)
- **Match: stale — exactly the plan's F5.** The `is-tip:true` half of the declared string is
  synthesized by the counter from the word "green at"; it is not a literal record byte.

## F6 — pre-correction run

Record sentence (sealed `SCORECARD.md`, `### Freeze divergences` item 4): *"the pre-correction tip
run and the corrected tip run are both in the lesson, and
`.ufo/waves/round-78/measured/after/c1-facts-tip.out` (`rev=381b53dc`) prints the frozen line."*
The named receipt exists at sealed and prints `SELFRECORD_R77 claims=6 mismatches=0 corrected=4
unbacked=0` / `EXIT=0` — it is the *corrected* run.

Commands (the counter's own F6 scan, reproduced):

```
git -C "$L" ls-tree -r --name-only $SEALED -- .ufo/waves/round-78 | wc -l
→ 76
# for each of the 76 blobs:
git -C "$L" show $SEALED:$p | grep -q 'mismatches=1'      → 0 hits
git -C "$L" show $SEALED:$p | grep -qi 'pre-correction'   → 0 hits
```

- Counter observed value: `c1-pre-correction-run=absent`
- Counter declared value: `c1-pre-correction-run=committed`
- Frozen plan observed: `absent`
- **Match: stale — exactly the plan's F6.** `corpus/lessons/round-78.md` at sealed mentions
  "the pre-correction tip run" in prose (line 203) but names no receipt blob.

## Summary against the counter

Read-only run at the lane tip (no corrections exist yet; `corpus/lessons/round-79.md` is absent at
`f7442dea`):

```
python3 tools/round79-selfrecord-round78.py --repo .
SELFRECORD_R78_FACT F1..F4 fresh; F5 stale; F6 stale
SELFRECORD_R78 claims=6 mismatches=2 corrected=0 unbacked=0 | sealed=7a3cd98243b69fcbee0cc9e31878782bd8459320 tip=f7442dea53bd8f474293a2252437b5d869801f49
EXIT=1
```

The `--json` run agrees with every hand derivation above (F1–F4 fresh, F5–F6 stale, declared
strings byte-equal to the frozen plan table). Exactly the pre-freeze `measured/before/` state:
`SELFRECORD_R78_ENUM claims=6 stale=2 corrected=0`, exit 1.

Printed-line caveat: the counter emits the frozen prefix plus a suffix, i.e. the physical line is
`SELFRECORD_R78 claims=6 mismatches=0 corrected=2 unbacked=0 | sealed=<sha> tip=<sha>`. An exact
whole-line match against the plan's quoted line fails; prefix/substring matching is required (the
lane's own pre-freeze receipts use the same suffixed form).
