# X16Policy — wave policy check, round 50 wave kama-r50-w1

**Verdict: the wave conforms to hyaku policy v2 — 66 seats inside the 64–128 band, `maxLanes` 66 ≤ policy 256 ≤ validator hard ceiling 256, all 10 dispatched roles are proposal roles with an `agentModelOverrides` route, wave label `kama-r50-w1` is consistent across spec/dispatch/ready, m_flash share 37/66 = 56.06 % (≥50 % MET) and attack share 20/66 = 30.30 % (≥25 % MET); four documentation defects found, none blocking.**

Seat: `X16Policy`, role executor (axes calibration, operability). Full deliverable:
`.ufo/waves/round-50/w1/out/X16Policy/policy.md`; machine-readable recomputation:
`out/X16Policy/policy-check.json`; digest evidence: `out/X16Policy/surface-digest-check.txt`.

## Evidence (commands, outputs, exits)

1. Policy read (read-only):
   `python3 /fast/scratch/hyaku/kama-r50/X16Policy/policy_check.py <out>/policy-check.json` → **exit 0**.
   Key outputs: `policy_swarm = {maxLanes 256, minLanes 16, waveMinLanes 64, waveMaxLanes 128,
   rampBatchSize 5, rampIntervalMs 700}`; `policy_proposalRoles` (10) == `validator_SWARM_ROLES` (10);
   `policy_lanes_roles` = scout, reviewer, **labrat**, critic, connector, executor, mutation-tester,
   revenger, simplifier, scribe (no sentinel); `validator_MAX_SWARM_LANES = 256`,
   `validator_MIN_SWARM_LANES = 2`.
   Sources: `scripts/hyaku/ufo-wave-policy-v2.json:84-92,104-115,256-306`;
   `/home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-mission-result.mjs:2572-2573`;
   `/home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs:265-276`.

2. Band + label: `kama-shokunin/.ufo/waves/round-50/w1/spec.json` `wave=kama-r50-w1`,
   `maxLanes=66`, `reportDir=.ufo/waves/round-50/w1/out`, 66 items; `dispatch.json`
   `wave=kama-r50-w1`, `counts={spawn:66,resume:0,total:66}`, registry path
   `.ufo/waves/round-50/w1/out/swarm-registry.json`, `policy` block
   `{maxLanes:66, declaredMaxLanes:66, minLanes:16, waveMinLanes:64, waveMaxLanes:128,
   hardCeiling:256, rampBatchSize:5, rampIntervalMs:700}`; `w1.ready`
   `{lane:kama, round:50, wave:w1, l1:KamaR50}`. Checker flags: `band_check.maxLanes_in_band=true`,
   `seats_in_band=true`, `under_hard_ceiling=true`, `under_round_budget=true`.
   Contrast: policy v1 band is 32–64 (`scripts/hyaku/ufo-wave-policy.json` swarm block), so 66 seats
   required the v2 path (`scripts/hyaku/lane-addendum.md:146-147,163-167`).

3. Roles: wave roles =
   `{executor 22, reviewer 10, scribe 10, critic 6, connector 5, mutation-tester 4, scout 4,
   sentinel 3, revenger 1, simplifier 1}` = 66, names unique, identical between `spec.items` and
   `dispatch.registry.members`. Checker: `wave_roles_subset_of_proposalRoles=true`,
   `wave_roles_subset_of_SWARM_ROLES=true`, `proposalRoles_eq_SWARM_ROLES=true`,
   `frozen_topology_roles_present=[]`, `every_wave_role_has_config_override=true`.
   `dispatch.taskCall`: 66 tasks, keys `{agent,name,task}`, `agent` = bare role on all 66,
   `any model field = false` (routing by role only, per `lane-addendum.md:179-180`).

4. m_flash share (role set per `scripts/hyaku/lane-addendum.md:12-15`: executor/labrat/scribe/sonic/
   simplifier/revenger/sentinel, critic excluded): 22+10+3+1+1(+0+0) = **37/66 = 56.06 %** vs ≥50 %
   → **MET**; minimum 33 seats, margin +4 seats / +6.06 pp. Cross-check from `config.yml` aliases
   alone (seats whose role maps to `@m_flash`): also 37 / 56.06 % (`alias_mflash_seats=37`).
   Resolved aliases: `m_flash = opencode-go/deepseek-v4.1-flash:high` (`~/.omp/agent/config.yml:336`);
   overrides executor 353, labrat 355, sentinel 357, simplifier 358, revenger 359, scribe 362.

5. Attack share (reviewer/critic/mutation-tester, `lane-addendum.md:147` also lists labrat = 0 seats):
   10+6+4 = **20/66 = 30.30 %** vs ≥25 % → **MET**; minimum 17 seats, margin +3 seats / +5.30 pp.
   Remainder: scout 4 + connector 5 = 9 (13.64 %); 37+20+9 = 66 ✓.

6. Axis/vocabulary sanity: all 66 item axis tags ⊂ the lane's six-axis set (operability 40,
   calibration 40, adjacency 1); assigned judged axes are operability + calibration
   (`kama-shokunin/SCORECARD.md:137`). Policy `fixtureAxes.axes` (correctness/safety/legibility/
   coverage) is the portable fixture identity, not the campaign vocabulary — no violation.

7. Harness ceiling: `task.maxConcurrency: 400`, `maxRecursionDepth: 3`
   (`~/.omp/agent/config.yml:348-349`) ≥ 66 lanes; ramp ⌈66/5⌉ = 14 batches × 700 ms ≈ 9.8 s.

## Defects (documentation only; proposals, nothing written outside this seat's out dir)

**F1 (medium) — stale `sighting.surfaceDigest` in both fleet policy files.**
`scripts/hyaku/ufo-wave-policy-v2.json:55` and `scripts/hyaku/ufo-wave-policy.json:55` declare
`sha256:1064c19addf69f294fd46ebbaa3a99298a4fe60eb5241fcb0d1406f1c0ba6bb4`. Command that shows it:
`cd /home/vgpnk/Projects/ufo-fsd-alpha && ./scripts/ufo-sighting surface --json` (exit 0, 13141 B) then
`sha256(canonicalJson(manifest))` per `scripts/sync-ufo-contracts.mjs:451-475` →
`sha256:610575e868e0f0fe0ab4af01e9a1ff438740a552f0c83956b85235279e848ce3`, which **matches**
`ufo-fsd-alpha/config/ufo.json` and `crates/ufo-core-runtime/bundled/config.json` and **not** the two
fleet copies (`out/X16Policy/surface-digest-check.txt`). No effect on this wave (the wave validator
reads only swarm knobs, `ufo-swarm-wave.mjs:822`), but a projected config built from the policy file
fails `sync-ufo-contracts --check` with `sighting surface digest mismatch`.
Fix: set both files to `sha256:610575e868e0f0fe0ab4af01e9a1ff438740a552f0c83956b85235279e848ce3`, or
delete the key and name `ufo-fsd-alpha/config/ufo.json` as the digest authority.

**F2 (low) — the v2 note misstates its provenance.**
`scripts/hyaku/ufo-wave-policy-v2.json:88` claims "copy of ufo-fsd-alpha config/ufo.json with only the
swarm band changed". Structural diff (this seat): v2 vs upstream `config/ufo.json` = 6 deltas
(`swarm.minLanes` 16 vs 32, `waveMinLanes` 64 vs 32, `waveMaxLanes` 128 vs 256, `swarm.note`,
`sighting.dispatch.maxConcurrentL2` = 8 upstream/absent, `surfaceDigest`), while v1 → v2 = exactly 3
deltas (`swarm.note`, `waveMinLanes` 32→64, `waveMaxLanes` 64→128). v2 is a copy of **v1**.
Fix: restate the note ("copy of ufo-wave-policy.json, band raised to 64–128; minLanes 16,
maxConcurrentL2 and surfaceDigest carried from v1") so the inherited items are visible.

**F3 (low) — `lanes[]` routes a role the validator refuses and omits one the wave dispatched.**
`scripts/hyaku/ufo-wave-policy-v2.json:256-306` lists `labrat` and no `sentinel`; `labrat` is not in
`SWARM_ROLES` (`ufo-swarm-wave.mjs:265-276`) so a spec asking for it fails `unknown_role`
(`ufo-swarm-wave.mjs:988-989`), while `sentinel` is a proposal role (policy `:104-115,217-228`;
`config.yml:357 sentinel: @m_flash`) with 3 seats in this wave and no substrate row.
Command: `python3 … policy_check.py` → `roles_in_lanes_but_not_wave=["labrat"]`,
`wave_roles_missing_from_policy_lanes=["sentinel"]`.
Fix: replace the `labrat` entry with `{"id":"sentinel","role":"sentinel","substrate":"omp"}`, or add
`sentinel` and mark `labrat` probe-only (the probe is already declared at policy `:121-125`).

**F4 (low) — executor lane bounds grant a labrat while the same prompt's constraints forbid it.**
`ufo-swarm-wave.mjs:785-797` (`laneBindingSuffix`) appends "Lane bounds: leaf member — no subagent
dispatch except your single labrat." to `role === "executor"` lanes (line 789) and plain "no subagent
dispatch" to the rest (line 791). Measured: 22 of the 66 `dispatch.taskCall.tasks` carry the grant, and
they are exactly the 22 executor tasks (0 spec items mention labrat; `labrat` holds 0 seats). Those
same seats also receive the round constraint "do not spawn subagents (leaf)", so one prompt says both.
`labrat` is a valid host agent (`~/.omp/agent/config.yml:355`) but not a wave role
(`ufo-swarm-wave.mjs:265-276`; refused at 988-989), so the grant can only be spent as a plain task
call that the wave registry never sees. No impact on this wave's numbers.
Fix: emit the labrat clause only when the spec declares a labrat item, and have the constraint text
name that exception; otherwise both end at "no subagent dispatch".

**F5 (low) — `hyaku.env` keeps the pre-amendment critic label.**
`scripts/hyaku/hyaku.env:9` lists "…simplifier/**critic**/revenger/sentinel @m_flash" while
`~/.omp/agent/config.yml:365` routes `critic: "@m_kfc"` and `scripts/hyaku/lane-addendum.md:12-13`
records the operator move (critic excluded from the m_flash share). No functional drift —
`hyaku.env:2-4` names the global role map as the routing authority — but a share computed from that
label reads 43/66 = 65.15 % instead of the true 37/66 = 56.06 %.
Fix: drop `critic` from that line and note the exclusion inline.

## Tooling / hygiene

- No installs or upgrades this seat (nothing to record under the 2026-10-19 authorization).
- Scratch `/fast/scratch/hyaku/kama-r50/X16Policy` removed at the end; no lane/fleet/ufo-fsd-alpha/
  config file edited; no git or jj mutation; no wave dispatched; no llama-server started (the
  `llama-server` PIDs visible during this seat belong to X11ModelSwap / J4Decoy / J2NoPdeathsig and
  were left untouched). `ufo-sighting surface --json` is the read-only verb
  `sync-ufo-contracts --check` runs itself; its manifest was written to this seat's scratch only.
