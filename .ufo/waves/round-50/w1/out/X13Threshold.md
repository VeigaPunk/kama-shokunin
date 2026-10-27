# X13Threshold — sub-20 boundary revisit (round 50, lane kama)

**Verdict:** the sub-20 boundary did not move and nothing regressed. At the measured build
`97c864bead3ee4a2f629574e77263d33834ec98a` the frozen default is still 20 deleted lines per
(commit, file) (`tools/append-only-audit.py:448`, `:1122`, event filter `:520`), and
`--threshold 1` now reports **97 sub-20 events / 375 deleted lines / 112 ungraded lines**
(96 / 374 / 112 at the round-49 closure `26ecba64`; the +1 is the build's own blank separator
line in `corpus/SOURCES.md`). v5 **does grade** the real `LOG.md` loss at `ed135b3c` at line
level — `deleted=7 graded=7 ungraded=0 status=partial restored_max=2 held_at_to=2` — but the
threshold keeps it out of the report, and its `partial 2/7` is 1 genuinely re-added line plus
**1 incidental blank line**; the five HOURS-section content lines are gone at the tip. The
frozen C2 counter still meets at the build (`fixture=1 lane=1 scenarios=12/12 met=True`,
exit 0), so C2 is not at risk from this item; what is at risk is that the boundary's motivating
count is carried in the lane's docs as **three different numbers from three definitions**, and
that the two sub-20 `SOURCES.md` edits the build itself makes are owned by no instrument: the
cell guard cannot parse the built tip (`exit 2`, `corpus/SOURCES.md:251`), while the audit drops
both under the threshold.

## What was run (all read-only; clone `git clone --shared` of the lane at my scratch)

| # | command | exit | time | artifact |
|---|---|---|---|---|
| 1 | `append-only-audit.py --repo <clone> --to 97c864bead3ee4a2f629574e77263d33834ec98a --threshold 1 --json` | 1 | 1.9 s | `out/X13Threshold/t1.json` |
| 2 | same, `--threshold 20` (default) | 0 | 1.9 s | `out/X13Threshold/t20.json` |
| 3 | same, `--threshold` 3, 5, 7, 10, 15 | 1,1,1,1,1 | 4.8 s | `thr3/thr5/thr7/thr10/thr15.json`, `threshold-ladder.tsv` |
| 4 | same, `--to 26ecba64` (round-49 closure = round-50 base), `--threshold 1` | 1 | 2.1 s | `base-v5-t1.json` |
| 5 | same, `--to 3b79eadd` (lane HEAD), `--threshold 1` | 1 | 2.1 s | `head-v5-t1.json` |
| 6 | v4 tool (`git show 26ecba64:tools/append-only-audit.py`), tips `97c864b` and `26ecba64`, `--threshold 1` | 1 | 4.4 s | `tip-v4-t1.json`, `base-v4-t1.json` |
| 7 | v1 tool (`git show 4a2a4d55:tools/append-only-audit.py`), tips `4a2a4d55`, `26ecba64`, `97c864b`, `--threshold 1` | 1 | 4.4 s | `v1b-<tip>.json` |
| 8 | v3 tool (`git show c4b2175d:tools/append-only-audit.py`), tips `b85783e8`, `c4b2175d`, `--threshold 1` | 1 | 3.3 s | `v3-r48parent.json`, `v3-r48.json` |
| 9 | frozen C2 counter `round50-append-audit-v5-check.py --repo <clone> --tip 97c864b --scratch $S` | 0 | 6.0 s | `c2-counter.out` |
| 10 | `sources-append-only.py --repo <clone> --from 26ecba6 --to 97c864b` and `--from 6f3bd322 --to 3d42897b` and `--from 3d42897b --to 3b79eadd` | 2, 2, 0 | 1.8 s | `sources-guard.out` |

Apart from this report and its `out/X13Threshold/` directory, no file in the lane, fleet repo or
shokuknow was written; no pacman/uv install was needed (no tool installed or upgraded). No `llama-server` was started by this seat (`pgrep -af llama-server`
shows only other seats' processes under their own scratch dirs, none under `X13Threshold`).

## 1. The sub-20 population at the measured build

`t1.json` (`"definition": "v5"`, 327 commits, 94 contract files, threshold 1): **102 events**,
19 restored / 4 partial / 60 unrestored / 19 ungraded, `ungraded_lines 201`, `regressed 0`,
exit 1. Of those, **97 events are below the threshold**, carrying 375 deleted lines and **112
ungraded lines**; the 5 at/above-threshold events carry the other 89 ungraded lines (17 at
`dd9f5dc6` + 72 at `0718b6abbda6`), which is exactly the lane's default-threshold
`ungraded_lines 89`.

Deleted-size histogram of the 97 (max 18, none at 19): 1×40, 2×14, 3×9, 4×7, 5×4, 6×4, 7×2,
8×5, 9×3, 11×3, 12×1, 14×1, 15×1, 17×1, 18×2. By file: `SCORECARD.md` 29,
`corpus/SOURCES.md` 21, `LOG.md` 12, `corpus/README.md` 7,
`corpus/knowledge/consumer-registry.md` 4, `corpus/lessons/*` 22, `corpus/QUALITY.md` 1,
`registry/report-landing-errata.tsv` 1. Statuses: unrestored 60, ungraded 19, restored 14,
partial 4. The 112 ungraded lines are `SCORECARD.md` 93 + `corpus/knowledge/consumer-registry.md`
19 — i.e. the carve-out population, not dated-section text.

Blank-vs-content split (byte-level, `git diff -U0` per event, `sub20-classification.json`):
**96 of 97 are content-bearing** (362 content lines); exactly **one is blank-only**, and it is
the build's own `97c864b` `corpus/SOURCES.md` event (`numstat 3 1`: three SOURCES rows added,
the trailing blank separator line removed). The lane HEAD adds a second, content-bearing one
(`3d42897b` rewrites the S498 row in place to fix markdown tick parity — 1 deleted content line,
`ungraded 0`, `unrestored`; after the measured tip, so not part of the measured census).

## 2. The real `LOG.md` loss at `ed135b3c`

`ed135b3cb869c5d8a6c9d3b32dac02fb7e551ebd` — `Revert "HOURS.md: craft-hours ledger opened
(§Craft-hours canon)"`; `git diff --numstat ed135b3c^ ed135b3c` → `1 7 LOG.md` (and `0 12
HOURS.md`). The seven deleted lines are the `fallback. No failure …` sentence, the
`## 2026-10-13 — HOURS.md ledger opened` heading, a blank line, the three `- Operator seed …`
lines and `- Evidence: fleet commit; PROTOCOL.md §Craft-hours.`

**Does v5 grade it? Yes, fully, at line level.** `t1.json` event
`ed135b3cb869 LOG.md deleted=7 graded=7 ungraded=0 restored_max=2 held_at_to=2 status=partial
restored_best=ea72c3eae4ec restored_by=null`. v4 gives the byte-identical row (§4). It is not an
*event* at the frozen threshold because `deleted=7 < 20`; it appears only at `--threshold <= 7`.

**What the `partial 2/7` actually is.** Recomputing `held()` (`tools/append-only-audit.py:552-557`,
`G` = the 7 graded lines, `K` = parent lines minus `D`) at the tip:
`fallback. No failure was forced …` 1 (re-added in the same commit as a no-newline replacement)
+ the empty line 1 (`M_tip[''] = 298` blank lines vs `K[''] = 28`), total 2. At the event commit
itself the blank contributes 0 (`M[''] = 28 = K['']`), so `held=1` there. At the tip
`HOURS.md ledger opened`, `Operator seed per PROTOCOL`, `Evidence: fleet commit` have **0**
occurrences (`git show 97c864b:LOG.md`). So 5 of the 7 deleted lines are permanently lost and the
status credits one unrelated blank line. Any decision that starts watching sub-20 losses inherits
this overstatement.

## 3. The gap in practice: the build's own `corpus/SOURCES.md` events, and a second blind spot

The sub-20 gap is not hypothetical. At the build, `97c864b` deletes one line of `SOURCES.md`
(`numstat 3 1` — the blank separator above the three new S496/S497/S498 rows): graded 1/1,
`unrestored`, sub-20, so no event at the default threshold. Two commits later `3d42897b`
("build-fix - S498 row markdown tick parity so sources-append-only row parser accepts it")
rewrites **two cells of the S498 row in place**:

* cell 5 (evidence): `` §4.5 Fenced code blocks (text copy `…`; full page sha256 `c85f56cc…`) ``
  → ` §4.5 Fenced code blocks (text copy `…`) ` — the sha256 of the page the row cites is gone;
* cell 6 (quote): the quoted sentence loses the backticks around the fence characters.

`registry/append-only-contract.tsv:6` gives `corpus/SOURCES.md` the rule `A-row` — "registry rows
appended; only status, recheck and used-by change in place" (`SKILL.md:578`) — so both edits are
outside the declared mutable cells. Neither instrument grades them:

* `append-only-audit.py --threshold 1` reports `3d42897b corpus/SOURCES.md deleted=1 graded=1
  ungraded=0 status=unrestored` (`head-v5-t1.json`), and at the default threshold it is not an
  event at all;
* the cell guard cannot reach it: `python3 tools/sources-append-only.py --repo <clone> --from
  97c864bead3ee4a2f629574e77263d33834ec98a --to 3d42897b` → `exit=2`, `error: …/corpus/SOURCES.md:251:
  unterminated table row (no closing pipe)`, and `--from 6f3bd322 --to 3d42897b` → `exit=2` on the
  same line. The only range the guard can evaluate is `3d42897b..3b79eadd` → `no append-only
  violations`, exit 0 — vacuous about the two cells the fix changed.

So at the measured tip the SOURCES guard has no verdict at all (exit 2, unparseable), and the one
in-place cell edit that followed it is outside the audit's threshold and outside the guard's
reachable range. A documented boundary decision should say which instrument owns a sub-20 in-place
cell edit in an `A-row` file, because today the answer is neither.

## 4. Nothing regressed (the boundary is v5-invariant)

* Constant: `threshold=20` at `tools/append-only-audit.py:448` and `:1122`, filter `:520`,
  docstring `:91` — identical bytes at the build and at lane HEAD (`git diff 97c864b 3b79eadd --
  tools/append-only-audit.py` → 0 lines; working tree == HEAD). The preregistration says the same:
  `.ufo/waves/round-50/preregistration.json` `limits[4]` "the sub-20 threshold is unchanged".
* **v4 → v5 at the same tip, threshold 1:** identical event sets and identical statuses at both
  `97c864b` (102 events) and `26ecba64` (101); the single delta is
  `0718b6abbda6 SCORECARD.md graded 2356→2349, ungraded 65→72, status restored in both` — the
  seven `## Capabilities` mirror rows (F6), so `ungraded_lines` 89 at the default threshold
  (17 + 72). No event's deleted count, restoration or status changed.
* **Base → build (v5, threshold 1):** 101 → 102 events. One new event,
  `97c864b corpus/SOURCES.md deleted=1 graded=1 ungraded=0 status=unrestored` (the blank
  separator line above); no pre-existing event changed any field; `regressed 0` at 1, 3, 5, 7,
  10, 15, 20 and at `26ecba64`, `97c864b`, `3b79eadd`.
* **Frozen C2 counter at the build** (`c2-counter.out`): `fixture=1 lane=1 scenarios=12/12
  met=True`, exit 0; lane detail `tool exit 0 events 5 bad_declarations 0 regressed 0
  ungraded_lines 89`; `dd9f5dc6c0e6 … ungraded 17 <= v5 natively exempt 23`;
  `0718b6abbda6 … ungraded 72 <= v5 natively exempt 72`. (The counter runs the tool at its
  default and requires lane exit 0 with ≥5 events — `tools/round50-append-audit-v5-check.py:64`,
  `:100` — so the boundary constant is load-bearing for C2; see §6.4.)
* Default-threshold lane run exits 0 (5 events, all restored, `ungraded_lines 89`).

Same-definition history (so the growth is the window, not a lost limit):
v1 tool, five hard-coded files (the extracted tool's `FILES` list, line 43), `--threshold 1` —
`4a2a4d55` (round-46 measured tip) **66 = 11 restored / 6 partial / 49 unrestored**, an exact
reproduction of the recorded figure; `26ecba64` 74 = 12/12/50; `97c864b` 75 = 13/12/50. The v5
contract population at the same tips is 101 → 102 events (96 → 97 sub-20) — different population,
same direction.

## 5. What a boundary move would cost (`threshold-ladder.tsv`, v5 at `97c864b`)

| threshold | events | restored | partial | unrestored | ungraded events | ungraded lines | `ed135b3c` |
|---|---|---|---|---|---|---|---|
| 1 | 102 | 19 | 4 | 60 | 19 | 201 | yes, partial |
| 3 | 48 | 13 | 3 | 27 | 5 | 182 | yes, partial |
| 5 | 32 | 12 | 3 | 13 | 4 | 177 | yes, partial |
| 7 | 24 | 12 | 3 | 6 | 3 | 171 | yes, partial |
| 10 | 14 | 6 | 2 | 4 | 2 | 125 | no |
| 15 | 9 | 5 | 1 | 1 | 2 | 125 | no |
| 20 | 5 | 5 | 0 | 0 | 0 | 89 | no |

`ed135b3c` needs `threshold <= 7`; the cheapest setting that catches it (7) still yields 24
events, 6 unrestored, 3 ungraded and 3 partial. The lane exits 1 at every setting ≤ 15 (1, 3, 5,
7, 10, 15 each exit 1; only the frozen 20 exits 0), because `exit_code()`
(`tools/append-only-audit.py:597-602`) trips on `partial`/`unrestored`.
Note the second blind spot: `exit_code()` does **not** include `s["ungraded"]`, so the 19
ungraded events / 112 ungraded lines never make the tool exit 1 at any threshold (fixture
`native-head` exits 0 with `ungraded 25`, `c2-counter.out`). Lowering the threshold alone would
add 60 unrestored rows and still not speak about the 112 ungraded lines.

## 6. What a documented boundary decision would have to change

1. **The constant, in three places, plus its selftest:** `tools/append-only-audit.py:448`
   (`audit(..., threshold=20, ...)`), `:1122` (`--threshold` default), `:520`
   (`if ns[f] < threshold: continue`), docstring `:91`. The selftest's threshold cases
   (`below-threshold`, `exact-threshold-unrestored`, `threshold-flag` — names at `:1090-1096`)
   would need the same move.
2. **The contract needs to carry the policy** if the frontier item "the 20-line threshold as a
   derived rather than a constant policy" (`corpus/README.md:1060-1061`) is to be machine-readable:
   `registry/append-only-contract.tsv:1` is `path<TAB>rule<TAB>declared_at<TAB>region<TAB>note`,
   with no threshold field, and `parse_contract()` (`tools/append-only-audit.py:186`) has no place
   to read one. Without that, a per-file or derived threshold exists only in prose.
3. **A separate status vocabulary for sub-20 findings.** 60 of the 97 sub-20 events are
   `unrestored` — ordinary in-place row edits of ≤ 18 lines (the round-46 note: 49 events, 152
   lines). Adding them to the graded report as-is changes every round's exit to 1 and buries the
   five genuine losses (e.g. `ed135b3c`) in 60 rows.
4. **A new counter / preregistration, not a silent tool edit.** The counters are frozen before the
   tool, and the frozen C2 counter runs the tool at its default and requires lane exit 0 with ≥ 5
   events (`tools/round50-append-audit-v5-check.py:64`, `:100`; detail line `tool exit 0 events
   5`). A default of ≤ 7 makes the lane exit 1 (measured above), so C2 would read
   `met=False` against the same bytes — the boundary change must land with its own counter and
   preregistration, and the preregistration limit now says the opposite
   (`preregistration.json` `limits[4]`).
5. **A tip-anchored census line**, because the number a decision would cite is currently
   unfixed — see §7.

## 7. Documentation defects (each reproducible; no lane file edited)

All three carriers of "the boundary's count" are stale, and each is a different definition at a
different tip:

| claim | file:line | written by | what it is | live value at the measured build |
|---|---|---|---|---|
| "the 93 sub-threshold deletion events" | `corpus/README.md:1061` | `c4b2175d` (round-48 integration) | v3 tool at `b85783e8` (= `c4b2175d^`): sub-20 **93**, 98 events, `ungraded_lines 186` | **97** |
| "the 66 graded sub-threshold events" | `corpus/README.md:1227-1228` | `24e906f0` (round-49 integration) | v1 tool, five hard-coded files, at `4a2a4d55` (round-46 tip): **66** = 11/6/49 (reproduced exactly) | **97** (v5), 75 (v1 files) |
| "66 graded sub-threshold events at `--threshold 1`, one real `LOG.md` loss at `ed135b3c`" | `SCORECARD.md:2854` (and `:2799`) | round-48/49 planned items | same v1/round-46 number | same |

Reproducers (each ~2 s on a shared clone):

```
git show c4b2175d:tools/append-only-audit.py > "$S/v3.py"
python3 "$S/v3.py" --repo <clone> --to b85783e8 --threshold 1 --json          # 93 sub-20, 98 events
python3 tools/append-only-audit.py --repo <clone> --to 97c864b --threshold 1 --json   # v5 -> 97 sub-20
git show 4a2a4d55:tools/append-only-audit.py > "$S/v1.py"
python3 "$S/v1.py" --repo <clone> --to 4a2a4d55 --threshold 1 --json         # 66 = 11/6/49
```

The v5 counts I measured across the relevant tips: 95 sub-20 at `438127bc` (round-49 base) and
`74558c71` (round-49 build), 96 at `24e906f0` (round-49 measured) and `26ecba64`, **97** at
`97c864b`, 98 at `3b79eadd`; `ungraded_lines` 194 → 201 at `24e906f0` and 201 flat afterwards.
None of them is 93 or 66.

Proposed fix (report-level; the lane L1 owns the edit): replace both numbers with a tip-anchored
census line, e.g. in `corpus/README.md:1061` and `:1227` and `SCORECARD.md:2799/2854`:

```
sub-20 population at <tip> (v5, `--threshold 1 --json`): 97 events, 375 deleted lines,
112 ungraded, 60 unrestored / 4 partial / 14 restored / 19 ungraded; the round-46 figure 66
is the v1 five-file count at 4a2a4d55, the round-48 figure 93 is the v3 count at b85783e8.
```

## 8. Limits (what I did not measure)

* I classified the 97 sub-20 events blank-vs-content, not "genuine loss vs in-place row edit"
  line by line; only `ed135b3c` was deep-dived. The 60 `unrestored` sub-20 events are unjudged.
* The v1/v3 historical runs use the tool bytes from those commits against the current clone; a
  tool from an older commit can read a later tip, which is what I did for the same-definition
  trend, and those rows are labelled as such.
* I did not run the frozen C1 counter (unrelated to the boundary) and did not test any other
  boundary constant (e.g. `regressed` semantics, restoration windows).
* The `held()` blank-line credit is demonstrated on one event; I did not census how many other
  `partial` events are blank-credited (the other three sub-20 partials — `e246c40e` README 2/1,
  `ef76777e` SCORECARD 18/13, `42ea1204` SCORECARD 14/12 — were not decomposed).
