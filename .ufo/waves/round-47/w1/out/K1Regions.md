# K1Regions — round 47 w1 attack: C1 SCORECARD region (never-held lines + F2 evaluation)

Verdict: **The 8 never-held SCORECARD lines are all head text the file itself declares re-derived (SCORECARD.md:6); the round-46 F2 proposal works — appending the superseded head rows verbatim under §Historical head sections turns both SCORECARD events fully restored and v2 exit 1 → 0, but a complete archive (8 never-held + 7 currently-lost round-45 head rows) is needed because v2's `restored_max` is the max over the event window, and the current tip alone holds fewer than the historical maximum (2420).**

Measurement root: fresh shared clone `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`; counter/tool run against that clone.

---

## 1. Baseline (before F2), v2 events at 3a09a1d93dcc16799cf6c4b48786e6440af134c4

Command:
```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py \
  --repo $S/lane --to 3a09a1d93dcc16799cf6c4b48786e6440af134c4 \
  --contract <(git -C $S/lane show 3a09a1d...:registry/append-only-contract.tsv) --json
```
Exit **1**. Events (85 files, 5 events):

| commit | file | deleted | restored_max | status |
|---|---|---|---|---|
| dd9f5dc6 | SCORECARD.md | 31 | 24 | partial |
| 0718b6ab | SCORECARD.md | 2421 | 2420 | partial |
| 0718b6ab | LOG.md | 2292 | 2292 | restored |
| 0718b6ab | corpus/QUALITY.md | 375 | 375 | restored |
| 0718b6ab | corpus/README.md | 663 | 663 | restored |

Receipt: `.ufo/waves/round-47/w1/out/K1Regions/events-before-3a09a1d.json`.

Independent recomputation with the counter's own `deleted_lines`/`recompute` semantics agrees (restored_max 24 and 2420; `restored_best=82b5e9d` for 0718b6ab).

## 2. The 8 never-held lines (exact identification)

Method: for each event, first-parent `git diff -U0 <c>^1 <c> -- SCORECARD.md`, deleted lines read by hunk-header counts (counter's `deleted_lines`, byte-exact), D = multiset; K = M_parent − D; line is **never-held** when held(x) = min(D[l], max(0, M_x[l] − K[l])) = 0 for every window commit x (event commit … tip). All 8 have D=1, K=0, M_tip=0 (zero copies anywhere in the window; absent at 3a09a1d).

### From event dd9f5dc6 (parent 0bfd47abdda1f5ac21a0834654122644fc23e861) — 7 lines

| parent line | bytes | content (prefix) | region | declared re-derived? |
|---|---|---|---|---|
| 17 | 484 | `Reconciled in round 41 against the measured commit (`tools/round41-scorecard-reconcile.py`, claim C1): every hash, line …` | `## Axes` intro prose | yes (head prose of the re-derived Axes section) |
| 21 | 577 | `| **operability** | **8** | registry gate `tools/kama-probe.sh` sha256 `36b64978…` …` | `## Axes` table row | yes |
| 22 | 401 | `| **freshness** | **8** | snapshot/diff harness `tools/test-snapshot.sh` sha256 `236c23c1…` …` | `## Axes` table row | yes |
| 23 | 291 | `| depth | **7** | `SKILL.md` sha256 `151023b99…` (1375 lines); `co…` | `## Axes` table row | yes |
| 24 | 358 | `| coverage | **9** | surface list `PROVINCE.md` sha256 `dbb5f4f7…` (169 lines); …` | `## Axes` table row | yes |
| 25 | 402 | `| calibration | **7** | run `python3 tools/capability-repertoire-audit.py --selftest` → …` | `## Axes` table row | yes |
| 26 | 309 | `| adjacency | **7** | `corpus/knowledge/cross-lane-scope.md` sha256 `1801cb7fa…` …` | `## Axes` table row | yes |

These are the round-41 `## Axes` table (and its intro) replaced in place by round 42. The only archived axes table below is the round-3 one (`### Historical axes table (round-3 assessment; superseded in round 41)`); the round-41 table is nowhere kept.

### From event 0718b6ab (parent 21945c6125c2fae531be94d7652ee058c68e5f83) — 1 line

| parent line | bytes | content | region | declared re-derived? |
|---|---|---|---|---|
| 16 | 331 | `| depth | **7** | `SKILL.md` sha256 `91440eb8…` (1420 lines); run `grep -c '^## ' SKILL.md` → `32`; …` | `## Axes` table row (round-45-era) | yes |

All 8 are therefore head text the file declares re-derived at **SCORECARD.md:6** (`The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are re-derived …`). The contract row (`registry/append-only-contract.tsv:3`) explicitly expects head re-anchors to be partials — so the 24/31 and 2420/2421 statuses are *expected* partials, not false positives. But they also contradict the same sentence's promise that `the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections`: the round-41 and round-45 axes generations are kept nowhere.

## 3. F2 evaluation (round-46 proposal)

Proposal: append the superseded head rows verbatim under SCORECARD §Historical head sections so the `kept verbatim` promise holds.

### Draft block (bytes from git history)
Extracted byte-exact from the parents (0bfd47ab for the round-41 rows, 21945c61 for the round-45 rows), inserted as two `###` subsections at the end of §Historical head sections (immediately before `## Round 6 — blocked dispatch, no axis claims (2026-10-18)`):

- `### Historical axes table (round-41 assessment; superseded in round 42)` — intro line 17, header, separator, rows 21–26 (verbatim).
- `### Historical axes table (round-45 assessment; superseded in round 46)` — header, separator, depth row 16 (verbatim).
- Also required for 0718b6ab: `### Head sections (round-45 text; superseded in round 46)` — the 7 round-45-era head rows currently absent at tip (banner line 6; coverage row 17; calibration row 18; §Planned pointer; §Retired paragraph; §Capabilities mirror intro; §Saturation paragraph).

Full block: 7517 bytes; `f2-block-full.bin` / `f2-block-full.md` in the out directory.

### Applied to scratch clone, committed with fixture identity
```
git -C $S/lane checkout -q -B f2 3a09a1d...
test "$(git -C $S/lane rev-parse --show-toplevel)" = "$S/lane"   # asserted before commit
# SCORECARD.md modified with the block; then:
GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=fixture@kama.invalid \
GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=fixture@kama.invalid \
GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 \
git -C $S/lane commit -q -m "F2: append superseded head rows verbatim under §Historical head sections"
```
New tip: **7dc0d1e44484b3d10fc0f71a1e13d3069d6d3114** (1 file, 18 insertions in the first partial block; combined 25 insertions).

### Events after F2 (same tool, `--to 7dc0d1e…`, exit 0)

| commit | file | deleted | restored_max | status |
|---|---|---|---|---|
| dd9f5dc6 | SCORECARD.md | 31 | 31 | restored |
| 0718b6ab | SCORECARD.md | 2421 | 2421 | restored |
| 0718b6ab | LOG.md | 2292 | 2292 | restored |
| 0718b6ab | corpus/QUALITY.md | 375 | 375 | restored |
| 0718b6ab | corpus/README.md | 663 | 663 | restored |

Summary `restored=5 partial=0 unrestored=0`; tool exit **0**. Receipt: `.ufo/waves/round-47/w1/out/K1Regions/events-after-F2-7dc0d1e.json`.

### Counter verdict at the F2 tip
```
python3 tools/round47-append-audit-v2-check.py --repo $S/lane --tip 7dc0d1e44484b3d10fc0f71a1e13d3069d6d3114 --scratch $S/counter --out …/counter-F2-7dc0d1e.out
selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True
```
Exit 0. (At the pre-wave tip 3a09a1d the counter also reads met=True — lane leg measures tool-vs-recompute agreement; the two partial SCORECARD events are the lane's own self-description state, not a counter failure.)

## 4. Findings / caveats

1. **F2 works, but the round-41/45 archive must be complete.** Because v2's `restored_max` is the maximum over the whole event window (D2 semantics), appending only the single never-held 0718b6ab line (the depth row) does *not* change its status: the max stays 2420 (attained at 82b5e9d), while the current tip holds only 2413 of the 2421 lines (7 round-45-era head rows are also absent today). The event only flips to `restored` when one window commit holds the whole deleted multiset (2421) — achieved by archiving all superseded head rows. For dd9f5dc6 a single append suffices (its historical max was 24 < 31).
2. **All 8 never-held lines are declared re-derived head text** (SCORECARD.md:6), and the contract row itself marks head re-anchors as expected partials. The `kept verbatim` promise is the sentence-level defect: the lane archives only the round-3 table, round-5 banner/planned, round-10 capabilities/saturation — not the round-41 or round-45 axes generations that F2 restores.
3. No defect found in the frozen counter itself: `deleted_lines`, numstat equality (31/31, 2421/2421), and window-max restoration all behaved as contracted; the attack is on the lane's file vs. its own declared promise, and F2 is a safe smallest correction (pure append, byte-exact history bytes).

## 5. Deliverables
- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K1Regions.md`
- Out: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K1Regions/`
  - `f2-block-full.bin` / `f2-block-full.md` (draft appended block, exact history bytes)
  - `events-before-3a09a1d.json` (v2 events, exit 1)
  - `events-after-F2-7dc0d1e.json` (v2 events, exit 0)
  - `counter-F2-7dc0d1e.out` (full C1 counter run at F2 tip, met=True)
