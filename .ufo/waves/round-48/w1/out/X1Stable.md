# X1Stable — round 48, item X1Stable: v3 graded/ungraded stability under a moving `--to`

**Verdict:** v3's per-event `graded`/`ungraded` never moved across **any** of the 32 tips of the round-48 range
(`33e0058~30..380bcdff`; eight sampled in full detail), so the C1 claim's numbers are stable through the wave and
not merely at its tip — and the measured tip reproduces the claim byte-for-byte and deterministically. The quantity
is nevertheless **tip-indexed by construction**: a later commit that regrows an `exempt=` section moves deleted
lines from graded to ungraded (fixture A: `ungraded` 0 → 14, exit 1 → 0) and `restored_max` can **fall**
(fixture B: 24 → 10), because v3's eligibility is a window maximum, not a fact about the event. That is the
frozen, spec'd carve-out (asserted as a pass in `tools/append-only-audit.py:774-781`), so it is **not a stability
defect of the measured claim**; it is a limit that two frozen statements currently under-describe — the C1
counter's `stable` leg compares these content-sensitive fields for equality (a *correct* v3 can score
`stable=0`, `tools/round48-append-audit-v3-check.py:755-759`), and the C1 `limits` in
`.ufo/waves/round-48/preregistration.json` do not name the tip-indexing. Advisory text in
`X1Stable/proposed-limits-and-stable-leg.md`; nothing was edited.

Tooling: nothing installed, no `pacman`, no network. Lane accessed read-only; all runs against
`git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` with `--to` pinned.

## 1. Objects under test and method

```
ec9c6d206fccfd9b9b04526b54da34207c48ab9f0768c3285128cd59fcf60f72  tools/append-only-audit.py   (append-only-audit/v3)
ca0618e50fadc4b0d53b0d8a61868b0ea7fbf33b3429c125a0d5643022a77075  registry/append-only-contract.tsv (v3 header, 5 rows)
```
Both files in the lane working tree are byte-identical to `git show 380bcdff…:<path>`; the eight-tip runs were
repeated with the blobs extracted from `380bcdff` itself and the JSON is identical at every tip
(`events_identical True` ×8). The contract is passed as a **file** (the measured commit's), so the only input that
moves between runs is `--to`; note that the tool's default is the contract **at `<to>`**
(`tools/append-only-audit.py:371`), which would make the split depend on the contract revision as well.

```
S=/fast/scratch/hyaku/kama-r48/X1Stable; export TMPDIR="$S"
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"     # toplevel asserted = $S/lane
python3 <lane>/tools/append-only-audit.py --repo "$S/lane" --to <rev> \
        --contract <lane>/registry/append-only-contract.tsv --json
```
The range is 32 commits, **0 merges**, one parent each (so each event's `window = commits[i:]`,
`tools/append-only-audit.py:404`, is a suffix that only grows). Eight sampled tips are rev-list indices
1, 5, 10, 15, 20, 25, 30, 32; the full per-event series over all 32 tips is `X1Stable/res/all32-trajectory.json`
and the per-tip summary is `X1Stable/res/all32-summary.json`.

Determinism at the measured tip (two runs, byte-compare): `sha256 7b5c065c834d58ca4b6305f69cda5d61d3f6a0e8b5c01ac4d6295097bb8778e4`
for both. Measured tip output (claim reproduced exactly):

```
event dd9f5dc6c0e6 SCORECARD.md deleted=31 graded=14 ungraded=17 restored_max=14 held_at_to=14 status=restored …
event 0718b6abbda6 LOG.md deleted=2292 graded=2292 ungraded=0 restored_max=2292 held_at_to=2292 status=restored …
event 0718b6abbda6 SCORECARD.md deleted=2421 graded=2349 ungraded=72 restored_max=2349 held_at_to=2349 status=restored …
event 0718b6abbda6 corpus/QUALITY.md deleted=375 graded=375 ungraded=0 restored_max=375 held_at_to=375 status=restored …
event 0718b6abbda6 corpus/README.md deleted=663 graded=663 ungraded=0 restored_max=663 held_at_to=663 status=restored …
summary commits=311 files=89 events=5 restored=5 partial=0 unrestored=0 ungraded=0 ungraded_lines=89 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0   (exit 0)
```

## 2. The eight tips

| # | tip | files | events | graded/ungraded per event | `held_at_to` | exit | why |
|---|---|---|---|---|---|---|---|
| 1 | `d48e8cc32fef` | 82 | 1 | dd9f5dc6 SCORECARD 14/17 | 14 | 1 | 3 unbound declarations |
| 5 | `052cb1e94c0a` | 83 | 1 | same | 14 | 1 | 3 unbound declarations |
| 10 | `0fddf257a0c5` | 84 | 5 | dd9f5dc6 14/17; 0718b6ab SCORECARD 2349/72, LOG 2292/0, QUALITY 375/0, README 663/0 | 2349 | 1 | 3 unbound declarations |
| 15 | `4a2a4d55d09d` | 85 | 5 | same | 2349 | 1 | 3 unbound declarations |
| 20 | `42ea1204aef3` | 86 | 5 | same | **2348** | 1 | `regressed=1` |
| 25 | `46a924e027f0` | 87 | 5 | same | 2348 | 1 | `regressed=1` |
| 30 | `33e005827742` (base) | 89 | 5 | same | 2348 | 1 | `regressed=1` |
| 32 | `380bcdff9c8a` (measured) | 89 | 5 | same | **2349** | **0** | — |

Full per-field table (deleted / graded / ungraded / restored_max / held_at_to / status / exit, one row per
tip×event): `X1Stable/table.md`. `graded`/`ungraded` are constant (14/17, 2292/0, 2349/72, 375/0, 663/0) and
`restored_max` is constant at 14 / 2292 / 2349 / 375 / 663 at every tip from the restoration commit `82b5e9d3`
onwards (0 at the event commit `0718b6ab` itself). What moves is
`held_at_to`: `0718b6ab SCORECARD` 0 at its own commit → 2349 from `82b5e9d3` → **2348** from `4340cf2f` through
`12284ba3` → 2349 again at `380bcdff` (the build's two superseded banners). `summary.regressed` follows it exactly:
`regressed=1` at tips 18–31 and at tip 8, 0 elsewhere — i.e. **14 of the 32 tips (44 %) exit 1 on the lost
round-45 banner alone**, and only the measured tip exits 0.

Why the early tips exit 1 is worth stating so nobody attributes it to the events: at tips 1–7 and 9–17 the exit is
produced solely by `bad_declarations=3` — the frozen v3 contract is graded against revisions where the declaring
line `corpus/README.md:761` (and the `exempt=`/`only=` pointers) do not yet exist, and binding is evaluated at
`<to>` (`tools/append-only-audit.py:218-243`). At `0fddf257`/`4a2a4d55` the tool would exit 0 with those three
lines present. Tip 8 (`0718b6ab`) is the event commit itself: four events `unrestored` plus the same three
unbound declarations.

## 3. Answer: does graded/ungraded change as the tip moves?

**In the measured range: no.** For every event at every one of the 32 tips, `graded` and `ungraded` are the
constants above — the line in `tools/append-only-audit.py:409-411` that computes eligibility never flips inside this
range, so the claim's 14/17 and 2349/72 are not just tip-pinned, they are range-invariant.

**In general: yes, one way only.** With a fixed contract file:

- `|D|` and the parent's per-section counts are fixed per event, so `graded + ungraded` cannot change;
- `eligible` is `{T : max over window of count(T,x) >= count(T,parent)}` (`tools/append-only-audit.py:409-411`) and
  the window `commits[i:]` (`:404`) only grows with the tip (in this range the history is linear, 0 merges; a merge
  can only insert descendants of the old tip, still inside the suffix);
- therefore `eligible` can only grow (`tools/append-only-audit.py:23-25` says exactly this), so
  `graded` is non-increasing and `ungraded` is non-decreasing in `<to>`. Neither can ever go back.

So `ungraded` is **monotone, one-way, and tip-indexed**: it can rise at any tip where a later commit regrows an
exempt section, and it never falls.

## 4. Fixture A — `ungraded` changes with `--to` (the requested construction)

`X1Stable/xstab_fixture.py` (sha256 `ff655769…`), own repo, toplevel asserted before the first commit, throwaway
identity via `git -c`; contract row `score.md⇥A-corr⇥NOTES.md:2⇥exempt=## Axes@NOTES.md:3`. Parent `score.md`:
`## Body` = heading + b01..b10 (11 lines), `## Axes` = heading + a01..a16 (17 lines). Event `c2` deletes
b01..b10 + a01..a14 = **24 lines** (≥ threshold 20); at `c2` Axes holds 3 < 17 → not eligible → all 24 graded.

```
tip tag  tip       event    deleted graded ungraded restored_max held_at_to status      rc
c2       b5e8179f  b5e8179f      24     24        0            0          0 unrestored   1
c3       f7058729  b5e8179f      24     24        0           10         10 partial      1
c4       e22f4bfc  b5e8179f      24     10       14           10         10 restored     0
c5       af75b3a9  b5e8179f      24     10       14           10         10 restored     0
ungraded by tip: [('c2',0),('c3',0),('c4',14),('c5',14)]  non-decreasing=True
graded   by tip: [('c2',24),('c3',24),('c4',10),('c5',10)]  non-increasing=True
```
`c3` restores the ten Body lines byte-exact; `c4` appends fourteen new Axes lines, taking the section to 17 = the
parent's count → eligible → the fourteen Axes deletions become ungraded; `c5` **deletes those fourteen lines
again** (sub-threshold, no new event) and the event stays `graded=10 / restored` with exit 0: once excused by any
later regrowth, the deletion is excused permanently for every later tip. Exit flips **1 → 0** on the same history.

**Is that a stability defect for the claim?** No, for the claim as frozen:

- the docstring defines `eligible` over "the window … up to `<to>`" (`tools/append-only-audit.py:23-25`) and the
  claim names one tip (`380bcdff`), which I reproduce exactly and deterministically;
- the behaviour is asserted as a pass in the tool's own selftest — `t_exempt_gutted_then_regrown`
  (`tools/append-only-audit.py:774-781`) expects `ungraded=24`, `status=ungraded` **and `exit_code(res) == 0`**;
- the direction is monotone (ungraded never falls), so no tip can turn an excused event back into a graded one and
  no oscillation is possible.

The real consequence is narrower and belongs to the artifacts' descriptions, not to the count: a correct v3 can
*change its answer for the same historical deletion* because lane content changed later, and v3 offers no pin that
would refuse a re-verification at a later tip. Concretely, if a future round re-verifies C1 at a tip with a regrown
SCORECARD head, it will see different `graded`/`ungraded` values than the claim lists and **must not** read that as
a defect in either direction.

## 5. Fixture B — `restored_max` can fall with the tip (stable-leg consequence)

Same fixture builder, `--case-b-dir` mode: parent Axes = heading + a01..a39 (40 lines); `c2` deletes 10 Body + 14
Axes (24); `c3` restores all 24 texts, the fourteen Axes texts landing in a `## Cited` section (the preregistered
whole-file multiset limit, `limits`: "Held lines are a multiset over the whole file"); `c4` regrows Axes with 14
**new** lines → 40 = parent count → eligible.

```
c2 c0b6a5bc  deleted=24 graded=24 ungraded=0  restored_max=0  held_at_to=0  unrestored rc=1
c3 2904f2c7  deleted=24 graded=24 ungraded=0  restored_max=24 held_at_to=24 restored   rc=0
c4 4a5eadf0  deleted=24 graded=10 ungraded=14 restored_max=10 held_at_to=10 restored   rc=0
restored_max c3=24 -> c4=10 (falls: True)
```

This reverses the round-47 property the v2→v3 repair was praised for ("no value falls as the tip moves", round-47
`X1Stable` §D2), and it is what the frozen C1 counter's `stable` leg compares for **equality**:

```
tools/round48-append-audit-v3-check.py:755-759
    if t is None or … any(t.get(f) != e.get(f) for f in
            ("deleted", "graded", "ungraded", "restored_max", "restored_best")):
        detail.append(f"stable: … changed or missing at tip");  stab = False
```
Applied to the fixture (base `c3`, tip `c4`) that predicate prints `stable: … changed` on `graded 24→10`,
`ungraded 0→14` (case A) and on `restored_max 24→10` (case B) and sets `stable=0`. **On the lane the leg passes,
non-vacuously**: base `33e00582` vs tip `380bcdff`, all five events, all five fields **EQUAL** — so the frozen
counter's `stable=1` and my independent runs agree. But a correct v3 could score `stable=0` for lane content
reasons alone (a section regrown between base and tip), so the leg is a content-sensitive strict-equality check
rather than a pure tool-stability check. The advisory in `proposed-limits-and-stable-leg.md` proposes the
directional form (`ungraded@tip >= ungraded@base`, `graded@tip <= graded@base`) plus attribution of the tip that
made the section eligible; it also warns against relaxing to "any event at base", which V1Ctr closed.

## 6. Retained evidence and limits

- `X1Stable/table.md` — 8-tip per-event table, 32-tip value sets, `held_at_to` transition series, 32-tip exit table.
- `X1Stable/res/<8 tips>.json` — raw `--json` of the eight runs; `res/all32-trajectory.json`,
  `res/all32-summary.json` — every tip in the range.
- `X1Stable/xstab-fixture.out`, `xstab-fixture-b.out`, `xstab-fixture.json`, `xstab-fixture-b.json`,
  `fixture-contract.tsv`, `fixture-b-contract.tsv`, `xstab_fixture.py`, `runlog.txt`.
- Limits of this evidence: the eligibility and `G` computations are the tool's own code path, so "stability" here
  is a property of v3's implementation plus the constructed fixtures; the fixtures' expectations come from line
  counts by construction (ground truth), not from the tool. `held_at_to`/`regressed` movement is additionally
  anchored on lane bytes (`git diff --numstat`/`git show` of the SCORECARD head, consistent with round-47 §D2).
  Case B leans on the preregistered whole-file multiset limit; without text relocation, restoring an exempt
  section's lines in place always re-eligibilises that section, so the two effects coincide.
- No defect in the frozen counter's *verdict* at the measured tip was found: `selftest/contract/lane/fixture/
  stable` are reproduced by the runs above; the known integration items from the wave brief were not re-reported.

## 7. Paths written (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Stable.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Stable/table.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Stable/runlog.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Stable/res/` (8 tip JSONs + `all32-trajectory.json` + `all32-summary.json`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Stable/xstab_fixture.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Stable/xstab-fixture.out`, `xstab-fixture.json`, `xstab-fixture-b.out`, `xstab-fixture-b.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Stable/fixture-contract.tsv`, `fixture-b-contract.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Stable/proposed-limits-and-stable-leg.md`
