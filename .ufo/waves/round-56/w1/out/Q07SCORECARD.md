# Q07SCORECARD — assigned axes and lowest-axis obligation (round 56)

Seat: Q07SCORECARD (build+attack, leaf). Scope: derive kama's assigned axes and
lowest-axis obligation from `shokunin.conf` / `AXES` / `SCORECARD`; report
mismatches. Read-only over the lane; no counters run; no scratch used (no
writing commands were needed beyond this file).

## Files resolved

| Task token | Resolved path | Note |
|---|---|---|
| `shokunin.conf` | `/home/vgpnk/Projects/shokunin/shokunin.conf` | fleet root; no lane-local copy exists |
| `AXES` | `/home/vgpnk/Projects/shokunin/AXES.md` | `.md` suffix |
| `SCORECARD` | `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md` | lane file per `AXES.md` §SCORECARD.md contract; the fleet-root `SCORECARD.md` belongs to the `protocol` lane (fleet-meta axes), not kama |

## Derived answer

**Assigned axes: operability + calibration.**
`shokunin.conf:52` (literal): `kama|kama-shokunin|operability + calibration
(local model serving and endpoint health)`. The `LANES` line format is
`<lane-id>|<repo>|<axes>` per `shokunin.conf:16`.

**Obligation rule.** `AXES.md` §Working the axes: "At least one claim works the
lane's **lowest-scoring non-retired axis**, except when the stagnation nudge
… waives it." The nudge (`AXES.md` §The stagnation nudge) requires every owned
axis at/above the saturation line AND no capability entering within the lane's
stagnation window.

**Lane scores at tip `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7`** (freeze
commit; `## Axes` table in `kama-shokunin/SCORECARD.md`): operability 8,
freshness 8, coverage 9, depth 7, calibration 7, adjacency 7. `## Retired`:
"None. 6 axes and 11 capabilities remain active." `## Saturation`: line 8/10,
window N=4.

**Lowest-axis derivation.**
- Among *assigned* axes: calibration 7 < operability 8 → **calibration is the
  lowest assigned axis**, uniquely.
- Among *all owned non-retired* axes: three-way tie — calibration, depth,
  adjacency all 7. Calibration is joint-lowest either way.
- Stagnation nudge: **inactive** — calibration 7 is below the 8/10 line, so the
  saturation precondition fails regardless of the capability window.

**Obligation discharge for round 56.** Frozen preregistration
(`.ufo/waves/round-56/preregistration.json`): C1 axis `operability` (8→8),
C2 axis `calibration` (7→7). C2 works the lowest-axis axis under both readings
above, so the obligation is met. Both round-56 claims sit on assigned axes —
consistent with the assignment. Lane `### Planned (round 56)` (SCORECARD end of
`## Round 55` section, lines 3105–3114) likewise plans 1. operability
2. calibration.

## Mismatches

**M1 — MISSION.md vs shokunin.conf assignment conflict (known, still open).**
`MISSION.md:29` declares `kama: { axes: "operability + freshness (local model
serving/endpoints)" }`; `shokunin.conf:52` assigns `operability + calibration`.
The lane treats the conf row as current authority (every "Current authority"
banner since round 35: "`MISSION.md:29` still says operability + freshness, an
open L0 question since round 35"). Complication worth restating for the
closure: `shokunin.conf:3-4` itself declares "SSOT for the mission lives in
MISSION.md + AXES.md at SHOKUNIN_ROOT", and the round-10 SCORECARD section
(line 247) records `MISSION.md` *overriding* a prompt's
"operability + calibration" ("the G5 recurrence") — so the two documents still
disagree and the precedence between them was inverted at least once. Observed
at tip; unchanged.
*Proposed fix:* operator ruling on the open L0, then edit `MISSION.md:29` to
`operability + calibration` (or record a precedence rule in `PROTOCOL.md`).
Seats cannot edit either file.

**M2 — preregistration wording vs three-way tie (minor, no defect).**
`preregistration.json` `authority` says "calibration is the lowest owned
axis". Owned-and-non-retired axes have a three-way tie at 7 (calibration,
depth, adjacency); the strictly correct statement is "lowest *assigned* axis"
or "joint-lowest non-retired axis". Earlier round sections (e.g. lines 2470,
3002) use the tied phrasing. The claim routing is unaffected — C2 works
calibration either way. *Proposed fix:* adopt "lowest assigned axis (tied with
depth and adjacency at 7)" phrasing in future preregistrations.

**M3 — banner/section landing gap (integration observation).**
Committed tip `efc6b3ec` still carries the round-55 "Current authority" banner
(`git show HEAD:SCORECARD.md | sed -n 6p`). The working tree holds an
uncommitted edit (not this seat's) rewriting the banner to round 56 —
"`Latest measured round: 56` … (SCORECARD §Round 56)" — but no `## Round 56`
section exists in the file yet, so the `§Round 56` pointer currently dangles.
Same working-tree edit re-anchors the depth row to round 55 and the
calibration row's spotcheck count 41→42 (round-55 spotcheck admitted). If
integration lands the banner without a `## Round 56` section, the pointer is a
cited-path defect. *Proposed fix:* land the `## Round 56` measured-results
section in the same commit as the banner.

**M4 — historical text retained (no defect, for record).**
The archived round-5 banner under §Historical head sections (lines 147–148)
asserts "assigned LIVE axes remain operability and freshness (`../MISSION.md`)",
and §Retired (round-3 text, line 170) says "Both assigned axes". These are
explicitly superseded verbatim-kept history, not current authority.

## Non-mismatches verified

- `shokunin.conf` citation "`shokunin.conf:52`" used across the lane is exact —
  line 52 is the kama row verbatim.
- Preregistration `authority` numbers (operability 8, calibration 7) match the
  committed `## Axes` table and the round-56 banner's "Scores remain
  operability 8 and calibration 7".
- Claim axes in the frozen preregistration (C1 operability, C2 calibration)
  exactly equal the assigned-axis set; no claim targets an unassigned axis.
- Working tree is dirty only in ways consistent with the running wave
  (uncommitted banner/row edits, round-55 seat outputs); the scored `## Axes`
  numbers are unchanged between HEAD and working tree.

## Tool installs

None. Reads/greps/git-show only; pacman untouched per guard.
