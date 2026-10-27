# Sc3Report — round-55 report skeleton for the L1

**Verdict: skeleton complete and evidence-grounded — all six required sections are in
order and every non-wave number points at a committed receipt or preregistration line;
six lane defects/conflicts found in the frozen evidence set are reported, not fixed.**

## Behavior

Wrote the L1 report skeleton at
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc3Report/kama-round-55-draft.md`
(filing target `.ufo/reports/round-55/kama.md`). It follows the report contract in
`/home/vgpnk/Projects/shokunin/templates/round-prompt.md` §4 — **Work performed**,
**Landed changes**, **Before → after measurements**, **Sources & frontier**,
**Trend verdicts**, **SHONEN** — with the round-54 precedent's trailing
**Notes for the closure** and an added **Reported conflicts** block. Every section that
needs post-wave facts carries `[L1: …]` markers only there; no wave result, seat tally or
trend verdict is invented. Two claim sections are pre-filled from committed receipts:

- C1: `preregistration.json:15-20`, base `controls/base.c1.out:2` (`met=False`,
  `newrow=0`), build `measured/c1-build.out:2` (`met=True`), battery table from the
  seven `c1/battery/*.out` line-2 leg lines.
- C2: `preregistration.json:23-32`, base `controls/base.c2.out:2` (`dropped=1`,
  `met=False`; dropped token named at `:22`), build `measured/c2-build.out:2`
  (`scenarios=15/15`, `dropped=0`, `met=True`), superseded scenario at `:17`.

No counter, clone, replay or llama-server was run: the numbers are read from committed
receipts, so nothing was re-measured to decorate the report. Counter identity was checked
by digest only:

```
$ sha256sum tools/round54-replay-code-audit.py tools/round54-cited-path-check.py
c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af  tools/round54-replay-code-audit.py
d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c  tools/round54-cited-path-check.py
```

both equal `preregistration.json:16` and `:27`.

## Gates

- Section order/coverage: `grep -n '^## ' draft.md` → Work performed, Landed changes,
  Before → after measurements, Sources & frontier, Trend verdicts, SHONEN, Notes for the
  closure, Reported conflicts — matches `templates/round-prompt.md:120-135`.
- Claim admission left open on purpose: `[L1: …]` markers sit at every score/verdict,
  wave-shape, seat-tally, census-after, LOG/SCORECARD/SKILL and exit-code slot; the two
  claim score strings (8→8, 7→7) are copied from `preregistration.json:14,23`, not judged.
- No fabricated measurement: every numeric in the draft resolves to a line in
  `controls/`, `measured/`, `c1/battery/`, `preregistration.json`, `census/start.out`,
  `corpus/SOURCES.md`, `corpus/lessons/round-55.md`, `w1/spec.json` or `w1/dispatch.json`.
- Lane-frozen artifacts left untouched: preregistration, both counters, both base
  controls, `c1/battery/` receipts. Proposed edits live only in this seat's out dir.
- Host guards: no pacman/uv/npx; no `git add/commit/checkout` anywhere; no file written
  under the fleet root or any lane path except this seat's out dir; scratch
  `/fast/scratch/hyaku/kama-r55/w1/Sc3Report` created and removed; no llama-server
  started, so none to tear down.

## Touched surfaces

| Path | Action |
|---|---|
| `.ufo/waves/round-55/w1/out/Sc3Report/kama-round-55-draft.md` | written (skeleton) |
| `.ufo/waves/round-55/w1/out/Sc3Report/proposed-fixes.md` | written (6 fixes, none applied) |
| `.ufo/waves/round-55/w1/out/Sc3Report.md` | written (this report) |
| `/fast/scratch/hyaku/kama-r55/w1/Sc3Report/` | created, then `rm -rf` |
| lane, fleet, sibling lanes, shokuknow | read-only |

## Findings (defects and conflicts; none fixed)

**F1 — battery receipts record no exit code.** `c1/battery/*.out` (7 files) carry `tip=`,
one aggregate leg line and `detail:` lines; `grep -c '^exit=' c1/battery/*.out` → `0`
everywhere, yet `preregistration.json:19-20` and `build_spec.py:25-26` speak in exits and
`run-battery.py:146` prints them to stdout only. Fix proposal F1 in
`proposed-fixes.md` (append `exit=<rc>` inside `counter()`).

**F2 — two receipts are not attributable to the committed harness.** `run-battery.py:23-85`
defines four `MUTANTS`; the directory holds six `m-*` receipts:

```
$ python3 -c "import re;s=open('.ufo/waves/round-55/c1/battery/run-battery.py').read();print(sorted(re.findall(r'\"(m-[a-z-]+)\": \(', s)))"
['m-ldaudit-foreign', 'm-ldpreload', 'm-member-flip', 'm-text-flip']
$ ls .ufo/waves/round-55/c1/battery/ | grep '^m-'
m-extra-in-tree.out
m-ldaudit-foreign.out
m-ldaudit-writable.out
m-ldpreload.out
m-member-flip.out
m-text-flip.out
```

`m-extra-in-tree.out:1` → `tip=312530a9…`, `m-ldaudit-writable.out:1` → `tip=23dc15da…`;
neither key exists in the harness. The preregistration names `m-ldaudit-writable` as a
code-leg mutant (`preregistration.json:44`), so the orphan receipt is load-bearing
evidence for a mutant that cannot be regenerated from the frozen harness.

**F3 — the kill rule's literal clause vs the two `met=True` receipts.**
`preregistration.json:20`: falsified "if any battery mutant prints `met=True`";
`:43`: mutants are "each expected to fail the frozen counter with its named leg"; `:44`
names `m-ldaudit-writable` and `m-ldaudit-foreign`. Both receipts print `met=True`
(`m-ldaudit-writable.out:2` with `code=1`; `m-ldaudit-foreign.out:2` with
`hostlibs=3/3`), while `run-battery.py:52-59` labels the latter a `vector` whose pass is
the finding, and the build commit message (`8abadfed`) reports "3 live kills + 1 vector
analysis". Reported verbatim in the draft's *Reported conflicts* block; no adjudication.

**F4 — C1's before→after flips on a metadata leg only.** At base
`controls/base.c1.out:2` already reads
`bind=1 sealed=1 code=1 teardown=1 … envnames=3/3 hostlibs=3/3 twopass=3/3` — every
operative observation leg is green; the sole red leg is `newrow=0`. The round-55 C1 delta
is therefore the S511 row plus the hermetic-git/re-point edits, not a new observation
capability (counter diff `3a600d2f..9c60eae6` = 24 insertions / 8 deletions, mostly
docstring). The draft states this in *Before → after measurements*; whether that keeps
8→8 admissible is the judge's call.

**F5 — the lesson pre-claims a census receipt that does not exist.**
`corpus/lessons/round-55.md:98-101` says the round ends at census exit 0 with receipt
`census/end.out`; the tree at `8abadfed` has only `census/start.out`, whose last line
(`:102`) is `census_start_exit=1` (E11 S510 dangling used-by at round start). Fix F4 in
`proposed-fixes.md`: run the census at round end, commit `end.out`, or correct the lesson.

**F6 — stale SKILL.md registry rows.** `SKILL.md:1598` pins the C1 base as
`0b75a84c` (frozen state: `3a600d2f`, `preregistration.json:7`); `SKILL.md:1599` says
`scenarios=N/14` and "fourteen constructed scenarios" (frozen counter prints
`scenarios=15/15`, `measured/c2-build.out:2`). Checks:

```
$ sed -n 1598,1599p SKILL.md | grep -o 'base `[^`]*`\|scenarios=N/[0-9]*\|fourteen constructed scenarios'
base `0b75a84c`
scenarios=N/14
fourteen constructed scenarios
base `0b75a84c`
```

The second `base` belongs to the C2 row and is correct; only the C1 row changes. Also
absent at `8abadfed`: any `round 55` occurrence in `SCORECARD.md` / `SKILL.md`
(`grep -ni 'round.55' SCORECARD.md | wc -l` → `0`), and LOG.md's last round heading is
`## Round 53` (`LOG.md:2435`) — the integration prose (SCORECARD section, LOG entry,
live `### Planned` pointer at `SCORECARD.md:3048`) is still owed by the L1.

## Out of scope

- Wave outcomes, seat tallies, dead seats, attack share, final trend verdicts and all
  admission rulings — marked `[L1: …]`, not guessed.
- Rerunning either counter, the battery or any replay; verifying the L1's own numbers.
- Editing lane files, the frozen preregistration/controls, or the fleet repo; filing the
  report; committing anything.

## Artifacts written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc3Report/kama-round-55-draft.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc3Report/proposed-fixes.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc3Report.md`
