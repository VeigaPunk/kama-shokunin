# kama — round 34 report (2026-10-24, attempt 1)

Lane: `kama-shokunin` (local model serving and endpoint health). L1: Kimi fresh L1.
Base revision at round start: `7c35289da5f4b94e062cd900eb086919e5094003`. Lane tip at
report time: `b784e1ab273472eaa750fc10918ca4be67fa7697`.

## Work performed

Two declared claims, frozen in `.ufo/waves/round-34/preregistration.json` before any
data row landed and before the wave was dispatched (freeze commit
`5c9ef1fe1938baa06f7bd8acd2bad9fa6f7ba185`); the counters, the predicates and the
kill rules were not changed after a seat scored.

- **C1 — calibration 7 → 7 (the lowest assigned non-retired axis; operability is 8).
  The lane's SCORECARD capability self-assessment must list every capability the
  lane demonstrated.** The lane demonstrated six capabilities (rounds 10, 14, 16, 20,
  25, 30) but its canonical repertoire table carried three: the round-20, round-25
  and round-30 capabilities lived only in per-round append sections. New counter
  `tools/capability-repertoire-audit.py` parses the SCORECARD's capability-shaped
  tables, selects the canonical table by its `**Capabilities — canonical list as of
  round N**` marker, and prints `listed L observed O missing M unsubstantiated U met B`.
- **C2 — operability 8 → 8. The lane's own instrument-registry gate must evaluate
  every tracked round-scoped counter.** `tools/gate-registry-check.py` evaluated only
  `.ufo/waves/round-*/count-*.py`, so the two live round-33 counters
  (`tools/round33-claim-audit.py`, `tools/round33-gate-receipts.py`) were invisible to
  it and were documented in SKILL.md prose only — the item the round-33 closure routed
  to round 34. The population now also covers `tools/round<N>-*.py`, and both counters
  are registered as five-column rows in `SKILL.md` §"Round-34 instrument registry rows".
- Frontier step (item 10 of the round contract): ONE theme — **how a served model
  name / alias is resolved across local serving stacks** — assimilated from the
  read-only package `/home/vgpnk/Projects/shokuknow/merge/kama/`. Two entries admitted
  (`corpus/knowledge/serving-alias-contract.md`,
  `corpus/knowledge/served-model-id-resolution.md`), five source rows appended
  (S196, S205, S206, S209, S223) after an empty id-collision check, a scratch
  transformation, and a mirror census that exited 0 before the first append; one
  own-work row S324 for the widened gate population. One proposal mined from
  `considerthese/2026-10-23.md` (the shortcut-class ledger), carried as a frontier
  item, not implemented.
- Mined mistakes (lesson `corpus/lessons/round-34.md` §Mistakes): the registry
  population gap, the repertoire-table gap, the seat-dispatch flag clash
  (`Cannot combine --prompt with --auto.`, 33 seats dead at spawn) and the mirror
  census that failed on `used-by` paths the mirror did not carry.

### Wave and seats

<!-- WAVE-CENSUS:BEGIN -->
| seat | role | report returned | report bytes | seat log bytes | first line of the report |
|---|---|---|---|---|---|
| ExecCapabilityAudit | executor | no | 0 | 29546 | - |
| ExecGatePopulation | executor | yes | 3872 | 2443 | # ExecGatePopulation — round 34, wave 1 |
| ExecRegistryRows | executor | no | 0 | 36886 | - |
| ExecIdCollision | executor | yes | 2443 | 24926 | # Item-10 ID collision check — round 34, W1 |
| ExecTransformAppend | executor | no | 0 | 32532 | - |
| ScribeLesson | scribe | no | 0 | 34468 | - |
| ScribeSourcesRows | scribe | no | 0 | 19907 | - |
| ScribeScorecard | scribe | yes | 9248 | 62684 | # ScribeScorecard — round 34, wave 1 |
| ScoutCanonicalCaps | scout | no | 0 | 44864 | - |
| ScoutAliasContract | scout | no | 0 | 48318 | - |
| ScoutServedIdResolution | scout | no | 0 | 2846 | - |
| ScoutR7Amendment | scout | no | 0 | 6289 | - |
| ScoutCoverageMap | scout | no | 0 | 62579 | - |
| ScoutAbsenceRegister | scout | no | 0 | 4602 | - |
| ConnSiblingScope | connector | no | 0 | 33435 | - |
| ConnSeparability | connector | no | 0 | 20541 | - |
| ConnRouteTable | connector | no | 0 | 24725 | - |
| ReviewC1Control | reviewer | no | 0 | 35574 | - |
| ReviewC2Control | reviewer | no | 0 | 49469 | - |
| ReviewAliasQuotes | reviewer | no | 0 | 58130 | - |
| ReviewCensusBlock | reviewer | no | 0 | 2355 | - |
| CriticC1Target | critic | yes | 7561 | 44331 | # CriticC1Target — attack on the C1 target |
| CriticC2Population | critic | no | 0 | 103837 | - |
| CriticAliasScope | critic | no | 0 | 32976 | - |
| CriticPredicateIdentity | critic | no | 0 | 43971 | - |
| MutC1Counter | mutation-tester | no | 0 | 31984 | - |
| MutC2Gate | mutation-tester | no | 0 | 42551 | - |
| MutAppendBlock | mutation-tester | no | 0 | 10978 | - |
| RevengerNoOp | revenger | no | 0 | 44585 | - |
| RevengerQuarantine | revenger | yes | 3776 | 24667 | # Revenger quarantine review — kama |
| SentinelScope | sentinel | no | 0 | 354811 | - |
| SentinelReceipts | sentinel | no | 0 | 159240 | - |
| SimplifyRows | simplifier | no | 0 | 51018 | - |

**Round shape:** one v1 wave of 33 seats (policy v1 band 32-64; `ufo-swarm-wave.mjs plan`
exit 0, `counts.spawn=33`, `waveMinLanes=32`, `waveMaxLanes=64`, hard ceiling 256, one
dispatch call). Role mix: connector 3, critic 4, executor 5, mutation-tester 3, revenger 2, reviewer 4, scout 6, scribe 3, sentinel 2, simplifier 1. Attack seats (reviewer, critic, mutation-tester,
revenger, sentinel): **15 of 33 = 45.5%** (the round contract requires >=25%).
The §3 L2 floor is met inside this one wave: connector 3, executor 5, scribe 3,
scout 6, reviewer 4, critic 4. The canonical §3 planner seat is held by the L1
(Kimi fresh L1); no planner role was added - the validator refuses it - and the
bounded planning data-walk is the preregistration and this wave's spec.

**Grant:** `scripts/hyaku/wave-slot.sh acquire kama round-34-w1 33` -> exit 0,
`granted lane=kama wave=round-34-w1 seats=33 live=18 pending=0 cap=256`, taken
immediately before the dispatch; the reservation is released when the wave settles.

**Transport:** one batched dispatch of the validator's `taskCall` (33 lanes) on this
Kimi surface - one `kimi --agent ufo-<role> --add-dir <fleet> --add-dir <shokuknow>
-p <lane task>` process per lane, all launched in the same batch, each carrying the
validator's composed lane text unchanged (`/skill:godspeed` + the verbatim Godspeed
directive bytes + the shared wave context + the lane task).

**Actual seats at report time:** 5 of 33 lane reports landed in the lane repo under
`.ufo/waves/round-34/w1/out/`; 2 lane processes still live. A first dispatch
attempt died at spawn for all 33 seats with `error: Cannot combine --prompt with
--auto.`; it is recorded in `.ufo/waves/round-34/w1/out/dispatch-manifest.json`.
No seat was replaced, no wave was split, and the failed attempt is not counted as
returned work. Seats without a report are reported as dead or in flight - not as
returned - and their seat logs stay in the lane as the evidence of what they did.
<!-- WAVE-CENSUS:END -->

### Inherited state (not this round's seats)

The round-33 wave ran **after** the round-33 report was filed (its registry carries
`createdAt 2026-10-24T06:52:20Z`, `updatedAt 07:42:46Z`) and left 22 untracked
outputs under `.ufo/waves/round-33/w1/out/`. Those are round-33 evidence; they are
not round-34 seats, they were not resumed, redispatched or counted, and they are
named here for the closure. No seat of this round was replaced by them.

### Misroot sweep

`git -C /home/vgpnk/Projects/shokunin status --porcelain` shows untracked files at the
fleet root (`bm.json`, `live.html`, `nama.html`, `live_s228.html`, `s395.txt`,
`.omp/mcp.json`). Their contents name no kama lane and no round 34 (checked by
`grep -ci kama` / `grep -ci round-34`, all zero), so they belong to another lane's
seats: they were left untouched and none was copied. No file written by this round's
seats landed at the fleet root.

## Landed changes

| Change | LOG entry | Lane commit (`landed`) |
|---|---|---|
| Freeze: claims, controls, preregistration, validated wave spec, taskCall, seat grant, census start | `LOG.md` §round 34 | `5c9ef1fe1938baa06f7bd8acd2bad9fa6f7ba185` |
| C1 counter `tools/capability-repertoire-audit.py`; C2 gate population + registry rows; canonical capability table; the two assimilated entries; the six appended source rows; the before-measurements and the assimilation scratch evidence | `LOG.md` §round 34 | `29f9d1e1b20ef6e16e578e6e039f95f4f3fb4007` |
| Lesson `corpus/lessons/round-34.md`, the measured after-receipts, the do-nothing controls, the LOG entry | `LOG.md` §round 34 | `4f5a0ce4ab30f3878cf231e07e2c263df717947f` |
| Registry placement repair (census `E12`) for the six appended rows | `LOG.md` §round 34 | `5890d1a0e20c02dd2ff7832a5f7cdc2a5f5ea1d2` |

`scripts/hyaku/jj-lane.sh commit … --as kama` was the only writer of lane history; the
reported hashes are the helper's `landed` lines. Nothing was written outside
`/home/vgpnk/Projects/shokunin/kama-shokunin` except this report and the L0 line
below; `/home/vgpnk/Projects/shokuknow` was read only.

## Before → after measurements

Measured on committed bytes at the data tip `29f9d1e1b20ef6e16e578e6e039f95f4f3fb4007`.

| Claim | Axis / score | Counting command | Before → after | Control (do-nothing) |
|---|---|---|---|---|
| C1 — canonical capability repertoire table | calibration **7 → 7** (delta 0) | `python3 tools/capability-repertoire-audit.py --repo . --tip <full-commit> --out <receipt.json>` | base `7c35289`: `listed 3 observed 6 missing 3 unsubstantiated 0 met False` (exit 1, `.ufo/waves/round-34/c1-before.out`) → tip: `listed 6 observed 6 missing 0 unsubstantiated 0 met True` (exit 0, `.ufo/waves/round-34/c1-after.out`, `.ufo/waves/round-34/c1-after.json`) | a scratch SCORECARD whose canonical table repeats the three missing capability NAMES with no resolving evidence pointer reads `listed 6 observed 6 missing 0 unsubstantiated 6 met False` (exit 1) — the control does not reach the target (`.ufo/waves/round-34/controls/c1-noop-control.out`) |
| C2 — instrument-registry gate coverage | operability **8 → 8** (delta 0) | `python3 tools/gate-registry-check.py --rev <full-commit>` | base `7c35289` with the widened population: `registered 10 unregistered 2 defective 0` (exit 1, `.ufo/waves/round-34/c2-before.out`) → tip: `registered 12 unregistered 0 defective 0` (exit 0, `.ufo/waves/round-34/c2-after.out`) | the base revision, whose SKILL.md names both tools in prose only, still reads `registered 10 unregistered 2 defective 0` (exit 1, `.ufo/waves/round-34/controls/c2-prose-only-control.out`); the gate's own selftest stays `GATE_SELFTEST pass=6 fail=0` (exit 0) |

The counter's selftest is `CAP_SELFTEST pass=2 fail=0` (exit 0). Limits: C1 reads the
SCORECARD's own tables, so a capability demonstrated only in a lesson is still
invisible to it; C2 grades the registry, not the instruments it names. Neither claim
is a mastery change, an endpoint-health claim or a serving-capability claim.

## Sources & frontier

- Census before: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
  → exit 0, `kama ok …/corpus/SOURCES.md` (`.ufo/waves/round-34/census-start.out`),
  194 rows (S001–S194).
- Census after: the same command → exit 0, `kama ok …/corpus/SOURCES.md`
  (`.ufo/waves/round-34/census-end.out`), 200 rows. **Rows 194 → 200 (+6):** five
  admitted source rows S196, S205, S206, S209, S223 (all tier B except S196, tier A;
  all `mined`) and one own-work row S324 (tier A, `used-by` SKILL.md). No existing
  row's immutable cell was changed; no row was deleted; no `status`/`recheck`/
  `used-by` edit was needed this round. W04 duplicate-URL warnings are the
  long-standing ones.
- Assimilation decisions (item 10): theme = served-name / alias resolution; the
  shokuknow package was read read-only and no campaign tool was run there; the
  id-collision check was EMPTY (registry 194 ids vs staged 129 ids, S001–S194 vs
  S195–S323) so no renumber map was needed and the adopted ids continue the lane's
  space; the guard was proved once (an indented `  | S195 | …` row collides with the
  staged set under the 0–3-space pattern while a column-zero-only pattern extracts
  nothing); the staged rows were transformed into fleet schema in scratch (no
  literal or escaped pipe, `recheck` reduced to `90d`, `status` `mined`, `used-by`
  naming exactly the admitted entries) and the mirror census exited 0
  (`.ufo/waves/round-34/assimilation/validate-census.out`) before the first append.
  All five sources were re-opened by the L1 on 2026-10-24 with a located quote
  (lesson §Gate). Rejections with reason and flip are in
  `corpus/lessons/round-34.md` §Gate: the r3–r7 amendment chain, the literature
  survey entry, and the six still-quarantined payload-absent rows (S200, S202, S210,
  S211, S224, S230 — S206 was on the slice and was hand-checked and adopted).
  One proposal from `considerthese/2026-10-23.md` mined as a lesson frontier item
  (the shortcut-class ledger); the file was not edited.
- Frontier rows advanced: none of the lane's own frontier rows changed ground. The
  coverage map gains two entries on the served-name/alias theme
  (`corpus/knowledge/serving-alias-contract.md`,
  `corpus/knowledge/served-model-id-resolution.md`).

## Trend verdicts

- **expansion — improved.** Two admitted knowledge entries on the served-name/alias
  theme, each sourced to a row opened this round (S196, S205, S206, S209, S223), plus
  one own-work row (S324) and one new lane instrument. Bounded: the entries are
  documentation-level contracts re-grounded this round, not observed runtime
  behaviour.
- **quality — improved.** The two routed defects the round-33 closure named are
  closed: the two round-33 counters are now inside the gate's evaluated population
  and carry five-column registry rows, and the canonical repertoire table matches
  what the lane demonstrated. The census gate caught three of this round's own
  defects (the `E12` registry placement, the mirror's missing `used-by` paths, the
  stale `used-by` pointer of the amended entry) and each was repaired; no admitted
  entry failed its re-check.
- **discernment — unchanged.** No independent non-author admit/reject sample exists
  for round 34; the wave seats are the lane's own seats, which is not outside
  attestation. The round's own gate decisions (2 admits, 5 refusals with flip
  conditions, 1 hand-checked quarantine row) await the outside closure.

## SHONEN

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources
      → `SKILL.md` §§Decision table, Error signatures, Checklist, and the new
      "Round-34 instrument registry rows" table; the round-34 rows are registered in
      the lane's own gate, whose selftest is 6/6. Author assertion; no named
      non-author verifier.
- [~] At least one end-to-end domain task executed and logged in LOG.md
      → `LOG.md` §round 34; the round's own executed tasks are the census, the two
      counter runs and the five source re-opens (2026-10-24). No live model server was
      started this round; the round-16/17 live receipts remain the lane's end-to-end
      evidence. Author assertion; no non-author mark.
- [~] Instructions executable by an agent without oral context
      → `SKILL.md` §Checklist, `tools/capability-repertoire-audit.py --selftest`
      (`CAP_SELFTEST pass=2 fail=0`) and `tools/gate-registry-check.py --selftest`
      (`GATE_SELFTEST pass=6 fail=0`); the independent execution review remains open.
- [~] No cross-domain bleed (PROVINCE.md still accurate)
      → `PROVINCE.md` §Write boundary and `corpus/knowledge/cross-lane-scope.md`; the
      assimilation took one in-province theme (served-name resolution) and refused
      out-of-theme staged material with reasons; the shokuknow package was read only
      and never written.

**Stale-lane:** respawn-per-round driver; no other mission of this lane is open. The
round-33 wave's late seat outputs are inherited evidence, not an open mission.

**Tool installs:** none. No tool was installed or upgraded this round, so no
installation record is owed under `/home/vgpnk/.omp/agent/RULES.md`; the pacman
pause was never touched.

**Open L0 questions:** none filed by this round. Two operator-side observations are
carried in the report for the operator only: `MISSION.md`'s kama row still lists
`operability + freshness` while `shokunin.conf` and the dispatched prompt bind
`operability + calibration` (named by the round-33 closure; the lane followed the
conf/prompt), and the lane's wave seats are dispatched through the Kimi CLI
(`--agent ufo-<role> -p`) because this substrate exposes no batched `task` tool to
the L1.
