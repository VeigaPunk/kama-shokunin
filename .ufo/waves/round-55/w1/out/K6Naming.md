# K6Naming — Naming/attribution audit of the round-55 frozen counters

Verdict: the `round54-*` filenames are **not** an attribution hazard — they correctly
encode the counters' round-54 draft provenance, every operative document
(preregistration, receipts, battery driver) uses them consistently, and renaming would
break the frozen counting commands and sha256 pins. The real hazard is **silent
staleness**: SKILL.md's round-54 registry rows still describe the pre-freeze drafts at
the freeze commit (wrong C1 base pin, wrong C2 scenario count, no round-55 freeze
mention), and `corpus/lessons/round-55.md` misattributes C2's frozen BASE in its Claims
section. `gate-registry-check` stays green throughout because it checks occurrence and
row shape only. One registry note + one lesson-line fix close it; no rename.

Scope: naming/attribution only (seat K6Naming). Counter logic, predicates and kill
rules were not re-derived; the two counters were not executed (a sibling seat owns
those). No tools installed.

## 1. The naming story (provenance)

Both counters were drafted in round 54 and frozen in round 55:

```
$ git -C <lane> log --follow --oneline -- tools/round54-replay-code-audit.py
9c60eae6 round-55 w0 freeze: round-54 counters frozen with preregistration + red base controls ...
9a3104c7 round-54 honest stop (run wrap-up): hardened counters built, integration reds repaired; claims unfrozen, no waves dispatched
$ git -C <lane> log --follow --oneline -- tools/round54-cited-path-check.py   # same two commits
```

Round 54 was an honest stop — claims unfrozen, no waves, no measurement. The first
freeze of either counter is the round-55 w0 freeze `9c60eae6f7ed84f7da93d219a406aadc30958c6c`
(preregistration `.ufo/waves/round-55/preregistration.json`). The frozen docstrings say
so themselves: `tools/round54-replay-code-audit.py:1-5` ("kama round-54 C1 … counter,
frozen for kama round 55") and `tools/round54-cited-path-check.py:1-6` (same for C2).
Freeze identity verified:

```
$ git show 9c60eae6:tools/round54-replay-code-audit.py | sha256sum
c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af   # == preregistration.json:16
$ git show 9c60eae6:tools/round54-cited-path-check.py | sha256sum
d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c   # == preregistration.json:27
```

So the filename round encodes the **draft** round (54), not the **freeze** round (55) —
a novel but defensible convention here, since the draft commit is the counters' birth
and the freeze kept the bytes' identity addressable. The round-55 preregistration's
counting commands (`preregistration.json:17,29`), the measured receipts
(`.ufo/waves/round-55/measured/c{1,2}-build.out`), the base controls
(`.ufo/waves/round-55/controls/base.c{1,2}.out`) and the battery driver
(`.ufo/waves/round-55/c1/battery/run-battery.py:14-15`, `FREEZE = 9c60eae6…`,
`COUNTER = …/tools/round54-replay-code-audit.py`) all use the same two paths — no
divergent authority, no duplicate identity.

## 2. gate-registry-check still resolves both tools

Run in my scratch clone (`git clone --shared`, toplevel verified) at three revisions;
full output in `out/K6Naming/gate-registry-check-evidence.txt`:

```
$ python3 tools/gate-registry-check.py --repo $S/lane --rev 9a3104c771509df2dad6b6fe13c023bd3c472c35   # round-54 draft
registered 54 unregistered 0 defective 0   exit=0
$ python3 tools/gate-registry-check.py --repo $S/lane --rev 9c60eae6f7ed84f7da93d219a406aadc30958c6c   # round-55 freeze
registered 54 unregistered 0 defective 0   exit=0
$ python3 tools/gate-registry-check.py --repo $S/lane                                                          # HEAD 8abadfed
registered 54 unregistered 0 defective 0   exit=0
```

The population regex `tools/round[0-9]+-…\.py` (`tools/gate-registry-check.py:24-26`)
matches both `round54-*` paths, and both occur in cells of the SKILL.md round-54
five-column registry table (`SKILL.md:1598-1599`). Resolution is green at the freeze
commit. Caveat, load-bearing for the rest of this report: per its own round-32 row
(`SKILL.md:1330`) the gate grades **occurrence and row shape only** — `thin-row`,
`empty-entry`, `missing-path` — so it cannot detect a stale pin inside a well-formed
row. Green here means "registered", not "accurate".

## 3. SKILL.md round-54 registry rows are stale at the freeze

The section `## Round-54 instrument registry` (`SKILL.md:1592`) and its two counter
rows were added by the round-54 draft commit `9a3104c7` and were **not touched by the
freeze** (`git diff --stat 3a600d2f 9c60eae6` lists no `SKILL.md`). Measured against
the frozen counters at `9c60eae6`:

- **`SKILL.md:1598` (C1 row) pins `base `0b75a84c``** in "Self-test / pinned values".
  The frozen counter's constant is `BASE = "3a600d2f729828419aaea34cc402c8b0d20fb720"`
  (`tools/round54-replay-code-audit.py:130`), re-frozen to the round-54 tip; the row
  also omits the S511 re-point (`GITDOC_URL`, `:129`) and the `GIT_*`-strip delta that
  the row's own `kills` text predates. Stale pin.
- **`SKILL.md:1599` (C2 row) says `scenarios=N/14` and "fourteen constructed
  scenarios"**. The frozen counter has `SCENARIOS = 15`
  (`tools/round54-cited-path-check.py:168`) and the build receipt prints
  `scenarios=15/15` (`.ufo/waves/round-55/measured/c2-build.out:2`); the row names no
  `superseded` class. Stale count.
- Neither row mentions the round-55 freeze, the preregistration path, or the frozen
  counter sha256s.

Hazard: the rows read as the operative description of the tools at the tip. A future
reader — or a future round's registry audit — quoting `SKILL.md:1598` would state C1's
base as the round-53 tip and C2's fixture count as 14, contradicting the frozen
counter and every round-55 receipt. That is exactly the "a claim standing in for a
re-derivation" failure mode the lane's own anti-pattern list warns about
(`SKILL.md:292-294`).

## 4. SCORECARD round sections — no hazard today

At the freeze, `SCORECARD.md` has no round-54 or round-55 section: the latest is
`## Round 53` with `### Planned (round 54)` (`SCORECARD.md:3033-3052`), and
`grep -n 'round54-\|round-55' SCORECARD.md LOG.md` matches nothing (LOG.md ends at
Round 53). Nothing to correct now. Forward note only: the wrap-up round-55 SCORECARD
section and LOG entry should name the counters with their round-55 freeze identity
(freeze `9c60eae6`, preregistration path) so the round-55 measurement is attributable
to the frozen bytes, not to the round-54 draft rows.

## 5. Defect — lesson Claims misattributes C2's frozen BASE

`corpus/lessons/round-55.md:20-21` (Claims, C2):

> `(BASE re-frozen to the round-54 tip; the `superseded` ledger class added with its …`

That describes the **reverted first freeze**, not the frozen artifact. The frozen C2
counter keeps `BASE = "0b75a84c…"` (`tools/round54-cited-path-check.py:158`, comment:
"the round-53 tip: the drop horizon must include the round-54 re-anchor … a same-tip
base would make the do-nothing control pass"); the preregistration disclosure
(`preregistration.json:10`) and the lesson's own §Mistakes ("C2's BASE reverted to the
round-53 tip (`0b75a84c`)") say the same. The Claims line contradicts all three.
Evidence command:

```
$ sed -n '20,21p' corpus/lessons/round-55.md   # says "BASE re-frozen to the round-54 tip"
$ sed -n '158p'  tools/round54-cited-path-check.py   # BASE = "0b75a84c…"  (round-53 tip)
```

Proposed fix (unified diff): `out/K6Naming/lesson-c2-base-claim.diff` — one-line
replacement with the reverted-first-freeze attribution, cross-referencing §Mistakes.

## 6. Proposed minimal fix (registry note, not a rename)

Renaming to `round55-*` is the wrong correction: it would break the frozen
preregistration's counting commands, the committed base/build/battery receipts, the
battery driver's `COUNTER` constant, and both counter sha256 pins — and it would
rewrite committed history. The names stay; the registry gains a note. Proposed text:
`out/K6Naming/skill-round55-freeze-note.md` — a short `### Round-55 freeze note`
appended after the round-54 table recording: both counters drafted at `9a3104c7`,
re-frozen at `9c60eae6` under the round-55 preregistration with the two sha256s; the
round-54 rows describe the drafts; operative pins at the freeze (C1 BASE `3a600d2f`,
S511 newrow source, `GIT_*` strip; C2 BASE stays `0b75a84c`, 15 scenarios incl.
`superseded`); frozen measurement under `.ufo/waves/round-55/{controls,measured,c1/battery}`.

This follows the lane's own precedent for keeping historical rows and adding a
superseding note rather than rewriting (`SKILL.md:1004-1007`, round-23→24 "Superseded
registry reading"; the round-28 "(retired)" row, `SKILL.md:1232`).

## Evidence index

- Freeze identity: `tools/round54-replay-code-audit.py:1-5,129-130`, `tools/round54-cited-path-check.py:1-6,158,168`; `git show 9c60eae6:<counter> | sha256sum` vs `preregistration.json:16,27`.
- Gate: `out/K6Naming/gate-registry-check-evidence.txt` (exit 0 at `9a3104c7`, `9c60eae6`, `8abadfed`).
- Stale rows: `SKILL.md:1592,1598,1599`; freeze diff `git diff --stat 3a600d2f 9c60eae6` (no `SKILL.md`); receipts `.ufo/waves/round-55/measured/c2-build.out:2`, `c1-build.out:2`.
- SCORECARD/LOG: `SCORECARD.md:3033-3052`; `grep` no-match for `round54-`/`round-55` in both.
- Lesson defect: `corpus/lessons/round-55.md:20-21` vs `:158` and §Mistakes.
- Proposals: `out/K6Naming/skill-round55-freeze-note.md`, `out/K6Naming/lesson-c2-base-claim.diff`.

Tools installed: none. Scratch clone removed on completion; no lane or fleet files
were modified (all lane writes are under `.ufo/waves/round-55/w1/out/K6Naming/`).
