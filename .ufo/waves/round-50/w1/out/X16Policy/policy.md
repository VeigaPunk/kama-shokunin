# X16Policy — hyaku v2 wave policy check (round 50, lane kama, wave kama-r50-w1)

Verdict: **conformant on band, maxLanes, role allowlist and wave label; the ≥50 % m_flash share
(56.06 %) and the ≥25 % attack share (30.30 %) are both met.** Four documentation defects found
(policy surfaceDigest stale, policy note misdescribes its source, `lanes[]` carries `labrat` but not
`sentinel`, `hyaku.env` keeps a stale critic label). None blocks the wave.

Seat: executor (axes calibration, operability). Read-only: no lane, fleet, ufo-fsd-alpha or config
file was written; no server, wave, counter or git/jj mutation was started.

## 1. Policy file and the wave's declared band

`/home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json` (tracked; last commit
`f47ad6ba8d30…`, "repair: restore fleet tree deleted by stray commit 35b91714"):

| key | value | line |
|---|---|---|
| `sighting.dispatch.swarm.maxLanes` (per-L1 round budget) | 256 | 84 |
| `sighting.dispatch.swarm.minLanes` | 16 | 85 |
| `sighting.dispatch.swarm.waveMinLanes` | 64 | 89 |
| `sighting.dispatch.swarm.waveMaxLanes` | 128 | 90 |
| `sighting.dispatch.swarm.rampBatchSize` / `rampIntervalMs` | 5 / 700 | 91–92 |
| `sighting.surfaceDigest` | `sha256:1064c19a…` (**stale**, §5 F1) | 55 |
| `nativeProfiles["omp-native-v1"].proposalRoles` | 10 roles, incl. `sentinel` | 104–115 |
| `lanes[]` (role → substrate table) | 10 entries, incl. `labrat`, **no `sentinel`** | 256–306 |
| `nativeProfiles["omp-native-v1"].concurrencyCeiling` | 32 (native-trial topology, not this wave); `l3Evidence` 64, `devin-native-v1` 16 | 98, 160, 211 |

Validator authority (`/home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-mission-result.mjs:2572-2573`):
`MAX_SWARM_LANES = 256`, `MIN_SWARM_LANES = 2`. Policy `maxLanes` 256 = that ceiling ✓.

Wave identity (`.ufo/waves/round-50/w1/`), all four sources agree on the label and seat count:

| source | value |
|---|---|
| `spec.json` `wave` / `maxLanes` / `reportDir` | `kama-r50-w1` / **66** / `.ufo/waves/round-50/w1/out` |
| `dispatch.json` `wave` / `counts` / `registry.path` | `kama-r50-w1` / spawn 66, resume 0, total 66 / `.ufo/waves/round-50/w1/out/swarm-registry.json` |
| `w1.ready` | lane `kama`, round 50, wave `w1`, l1 `KamaR50` |
| `dispatch.json` `policy` block | maxLanes 66, declaredMaxLanes 66, minLanes 16, waveMinLanes 64, waveMaxLanes 128, hardCeiling 256, ramp 5/700 ms, globalRunnerCeiling 1056 |

Band check: **66 seats ∈ [64, 128]** ✓ (floor + 2); spec `maxLanes` 66 ∈ band ✓; 66 ≤ policy
`maxLanes` 256 ✓; 66 ≤ validator hard ceiling 256 ✓. Dispatch rendered the same numbers, so the
validator agreed (it is the file that wrote `waveMinLanes 64`, `waveMaxLanes 128` into
`dispatch.json`). This wave could not have validated under policy v1 (`waveMaxLanes` 64 < 66):
v1 band is 32–64 (`scripts/hyaku/ufo-wave-policy.json` swarm block), which is exactly why the v2
dispatch path was required (`scripts/hyaku/lane-addendum.md:146-147,163-167`).

Ramp feasibility: ⌈66 / 5⌉ = 14 batches × 700 ms ≈ 9.8 s to full wave; the session task budget is
`task.maxConcurrency: 400`, `task.maxRecursionDepth: 3` (`~/.omp/agent/config.yml:348-349`), so the
66 lanes are inside the harness ceiling. Payload shape: exactly one batched `taskCall`
(`dispatch.json` `note`), 66 tasks, keys `{agent, name, task}`, `agent` = bare role, **no `model` /
`modelAlias` field on any task** — routing is by role only, as the addendum requires.

## 2. Allowed roles

Wave role multiset (`spec.json` items, identical to `dispatch.json` registry members, 66 unique names):

| role | seats | config.yml override (line) | resolved alias |
|---|---|---|---|
| executor | 22 | `@m_flash` (353) | `opencode-go/deepseek-v4.1-flash:high` (336) |
| reviewer | 10 | `@m_zfl` (366) | `zai/glm-5.3-flash:max` (334) |
| scribe | 10 | `@m_flash` (362) | deepseek-v4.1-flash |
| critic | 6 | `@m_kfc` (365) | `kimi-code/kimi-for-coding:max` (329) |
| connector | 5 | `@m_kfc` (367) | kimi-for-coding |
| mutation-tester | 4 | `@m_zfl` (356) | glm-5.3-flash |
| scout | 4 | `@m_sonnet` (360) | `anthropic/claude-sonnet-5-5:high` (341) |
| sentinel | 3 | `@m_flash` (357) | deepseek-v4.1-flash |
| revenger | 1 | `@m_flash` (359) | deepseek-v4.1-flash |
| simplifier | 1 | `@m_flash` (358) | deepseek-v4.1-flash |

- {10 wave roles} ⊆ `proposalRoles` (policy 104–115) ✓
- {10 wave roles} ⊆ `SWARM_ROLES` (`ufo-swarm-wave.mjs:265-276`) ✓ — the two sets are equal, so no
  wave role can hit `unknown_role` (`ufo-swarm-wave.mjs:988-989`).
- No frozen-topology role present (`planner`, `distiller`, `labrat`, `main`, `task`): 0 seats ✓
  (the addendum forbids `planner`; the L1 holds the planner seat).
- Every one of the 10 roles has a `task.agentModelOverrides` entry (`config.yml:350-368`) ✓; no role
  falls through to the `task` default `@m_opus`.
- `lanes[]` (substrate routing table) is the one inventory that does **not** match: it lists `labrat`
  and omits `sentinel` while this wave dispatches 3 sentinel seats and 0 labrat seats (§5 F3).

## 3. m_flash share (executor/scribe/simplifier/revenger/sentinel; critic excluded)

Role set taken from the run-9 operator amendment, `scripts/hyaku/lane-addendum.md:12-15`
("count only executor/labrat/scribe/sonic/simplifier/revenger/sentinel seats"), cross-checked against
`config.yml` aliases (every role in that set resolves to `@m_flash`; `labrat` and `sonic` resolve to
`@m_flash` too but hold 0 seats in this wave).

| role | seats |
|---|---|
| executor | 22 |
| scribe | 10 |
| sentinel | 3 |
| simplifier | 1 |
| revenger | 1 |
| labrat | 0 |
| sonic | 0 |
| **total** | **37 / 66 = 56.06 %** |

- Threshold **≥ 50 %**: **MET**, margin +6.06 pp (+4 seats over the 33-seat floor).
- Independently recomputed from `config.yml` alone (seats whose role maps to `@m_flash`): 37 seats,
  56.06 % — same number, so the seat-class count and the routing map agree.
- If the stale `hyaku.env:9` label were used instead (critic listed as `@m_flash`), the share would
  read 43/66 = 65.15 %. The routing authority is `config.yml:365` (`critic: @m_kfc`), and
  `hyaku.env:2-4` itself says "the global role map remains the routing authority" — so the honest
  number is 56.06 % and the label is a defect (§5 F5).

## 4. Attack share (reviewer/critic/mutation-tester)

`scripts/hyaku/lane-addendum.md:147` defines the attack roles as reviewer, critic, mutation-tester,
labrat; `labrat` holds 0 seats, so both enumerations give the same count.

| role | seats |
|---|---|
| reviewer | 10 |
| critic | 6 |
| mutation-tester | 4 |
| labrat | 0 |
| **total** | **20 / 66 = 30.30 %** |

- Threshold **≥ 25 %**: **MET**, margin +5.30 pp (+3 seats over the 17-seat floor).

Non-m_flash, non-attack remainder: scout 4 + connector 5 = 9 seats (13.64 %) — the connector seats the
addendum asks each wave to carry ("every wave still carries a few connector seats", line 41).

Table integrity: 37 + 20 + 9 = 66 = seat count ✓.

## 5. Defects (documentation only; none blocks this wave)

**F1 — policy `surfaceDigest` is stale in both fleet policy files.**
`scripts/hyaku/ufo-wave-policy-v2.json:55` declares
`sha256:1064c19addf69f294fd46ebbaa3a99298a4fe60eb5241fcb0d1406f1c0ba6bb4`. The live wall manifest
does not hash to it:

```
$ cd /home/vgpnk/Projects/ufo-fsd-alpha && ./scripts/ufo-sighting surface --json   # exit 0, 13141 B
$ sha256(canonicalJson(manifest))          # canonicalJson per scripts/sync-ufo-contracts.mjs:451-462
live computed: sha256:610575e868e0f0fe0ab4af01e9a1ff438740a552f0c83956b85235279e848ce3
STALE  sha256:1064c19a…  scripts/hyaku/ufo-wave-policy.json:55
STALE  sha256:1064c19a…  scripts/hyaku/ufo-wave-policy-v2.json:55
MATCH  sha256:610575e8…  ufo-fsd-alpha/config/ufo.json:55
MATCH  sha256:610575e8…  ufo-fsd-alpha/crates/ufo-core-runtime/bundled/config.json
```

Impact: no effect on this wave (the validator reads only the six swarm knobs,
`ufo-swarm-wave.mjs:822`), but the policy file's claim about the wall surface it was validated
against is wrong, and a projected config carrying it would fail `sync-ufo-contracts --check` with
`sighting surface digest mismatch`.
Proposed fix (fleet root, not written by this seat): set `sighting.surfaceDigest` to
`sha256:610575e868e0f0fe0ab4af01e9a1ff438740a552f0c83956b85235279e848ce3` in both policy files, or
drop the key and name `ufo-fsd-alpha/config/ufo.json` as the digest authority.

**F2 — the v2 note misdescribes its own provenance.**
`scripts/hyaku/ufo-wave-policy-v2.json:88` says "copy of ufo-fsd-alpha config/ufo.json with only the
swarm band changed". Structural diff (recursive walk, this seat):
`ufo-wave-policy-v2.json` vs `ufo-fsd-alpha/config/ufo.json` = 6 deltas —
`swarm.minLanes` 16 vs 32, `swarm.waveMinLanes` 64 vs 32, `swarm.waveMaxLanes` 128 vs 256,
`swarm.note`, `sighting.dispatch.maxConcurrentL2` (=8 upstream, absent in v2), and
`sighting.surfaceDigest`; while `ufo-wave-policy-v2.json` vs `ufo-wave-policy.json` = exactly 3 deltas
(`swarm.note`, `waveMinLanes` 32→64, `waveMaxLanes` 64→128). So v2 is a copy of **v1**, not of
`config/ufo.json`, and `minLanes` 16, the missing `maxConcurrentL2` and the stale digest were
inherited silently.
Proposed fix: restate the note as "copy of ufo-wave-policy.json with the wave band raised to 64–128
and the note updated; minLanes 16, maxConcurrentL2 and surfaceDigest carried from v1 (F1 open)".

**F3 — `lanes[]` routes `labrat`, which can never be a swarm lane, and has no `sentinel` row.**
`scripts/hyaku/ufo-wave-policy-v2.json:256-306` lists `scout, reviewer, labrat, critic, connector,
executor, mutation-tester, revenger, simplifier, scribe`; the dispatched wave uses
`…sentinel…` and no `labrat`. `labrat` is excluded from `SWARM_ROLES`
(`ufo-swarm-wave.mjs:265-276`), so a spec asking for one would fail `unknown_role`
(`ufo-swarm-wave.mjs:988-989`); `sentinel` is a real proposal role (policy 104–115, 217–228; config
`sentinel: @m_flash`, line 357) with no substrate row.
Impact: cosmetic here (the wave routes through one `task` call and the config override; every lane ran
on `omp`), but the policy's role table advertises a role the validator refuses and omits one it
dispatched 3 times.
Proposed fix: in `lanes[]` replace the `labrat` entry with `{"id":"sentinel","role":"sentinel",
"substrate":"omp"}`, or add `sentinel` and annotate `labrat` as a probe-only seat (policy lines 121-125
already carry the probe depth/parent).

**F4 — executor lane bounds grant a labrat while the same item's constraints forbid subagents.**
`ufo-swarm-wave.mjs:785-797` (`laneBindingSuffix`) appends, for `role === "executor"` only (line 789),
"Lane bounds: leaf member — no subagent dispatch except your single labrat."; every other role gets
"no subagent dispatch" (line 791). Measured on this wave: 22 of the 66 `dispatch.taskCall.tasks`
contain the grant and they are exactly the 22 executor tasks (0 spec items mention labrat; `labrat`
holds 0 seats). Each of those seats also receives the round's own constraint block, which says
"do not spawn subagents (leaf)" — so the two statements in one prompt contradict each other, and
because no labrat lane exists nothing in the wave observes which one the seat followed. `labrat` is a
legitimate host agent (`config.yml:355 labrat: @m_flash`) but not a wave role
(`ufo-swarm-wave.mjs:265-276`, refusal at 988-989), so the grant can only be spent as a plain task
call — unobservable to the wave's registry.
Proposed fix (ufo-fsd-alpha, not written by this seat): emit the labrat clause only when the spec
declares a labrat item, and have the round's constraint text say "except the labrat your lane bounds
grant" when it does; otherwise both texts end at "no subagent dispatch".

**F5 — `hyaku.env` keeps the pre-amendment critic label.**
`scripts/hyaku/hyaku.env:9` reads "…executor/labrat/scribe/sonic/simplifier/**critic**/revenger/sentinel
@m_flash", while `~/.omp/agent/config.yml:365` routes `critic: "@m_kfc"` and
`scripts/hyaku/lane-addendum.md:12-13` records the operator amendment ("critic moved from `@m_flash`
to `@m_glm53`, then to `@m_kfc`; … critic seats no longer count toward it"). No functional drift —
`hyaku.env:2-4` declares the global role map the routing authority — but it is the file a share
auditor reads first, and it yields 65.15 % instead of the true 56.06 %.
Proposed fix: delete `critic` from that line (and note the exclusion inline).

## 6. What this seat did not do

No counter, preregistration, control, lane file, fleet file, ufo-fsd-alpha file or config was edited;
no wave dispatched; no git/jj mutation; no llama-server started (the `llama-server` processes visible
during this seat belong to sibling seats X11ModelSwap / J4Decoy / J2NoPdeathsig and were left alone).
`ufo-sighting surface --json` is the read-only verb `sync-ufo-contracts --check` itself runs; its
manifest was written only to this seat's scratch.
