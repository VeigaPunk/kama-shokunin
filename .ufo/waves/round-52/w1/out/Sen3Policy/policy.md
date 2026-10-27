# Sen3Policy — Round 52 wave policy and route check (kama)

**Verdict: the wave conforms to hyaku policy v2 — 70 seats inside the 64–128 band, `maxLanes` 70 ≤ 256 hard ceiling, spec/dispatch/registry agree key for key, all ten dispatched roles resolve through the live `task.agentModelOverrides` map to an enabled model with a fallback chain, attack share 26/70 = 37.14 % (≥25 % MET), and the route map in force at dispatch is fingerprinted (mtime `2026-10-27T02:39:08.510680Z`, sha256 `0d587466…addc`, 14,940 B, 8,762 s before dispatch). Four documentation drift defects found (F1–F4) plus one informational axis note (F5); none blocks the wave.**

## 1. Sources read (all read-only)

| Source | Role in this check |
|---|---|
| `/home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json` (mtime 2026-10-22 15:55:22.570413032 -0300, 12,676 B, sha256 `f12e1d6dfeae81a4a1ff805f8de50ec8386b3a16ae7f40b171f54c5236812fff`) | band, proposal roles, hard ceiling |
| `/home/vgpnk/.omp/agent/config.yml` (mtime `2026-10-27T02:39:08.510680Z` = 2026-10-26 23:39:08.510680 -0300, ctime identical, 14,940 B, sha256 `0d5874660274d3a4545d9d1f9e1da320f0629a9efb384255b788b897bba6addc`) | `task.agentModelOverrides` → `modelRoles` → `enabledModels`, `retry.fallbackChains` |
| `kama-shokunin/.ufo/waves/round-52/w1/spec.json` | 70 items, roles, axes, `maxLanes` 70 |
| `kama-shokunin/.ufo/waves/round-52/w1/dispatch.json` | `taskCall.tasks` (70), policy block, counts |
| `kama-shokunin/.ufo/waves/round-52/w1/out/swarm-registry.json` | 70 members, `createdAt` `2026-10-27T05:05:10.877Z` |
| `kama-shokunin/.ufo/waves/round-52/w1/validate.out`, `validate.stderr` | `exit=0`, stderr 0 B |
| `/home/vgpnk/Projects/shokunin/scripts/hyaku/lane-addendum.md` and `hyaku.env` | binding run-9 rules and the labels checked in F1 |

The policy file was read, never written. `ufo-wave-policy-v2.json` is frozen for this round; every defect below is a report with a proposed hunk, not an in-place edit.

## 2. Wave shape

Spec `kama-r52-w1` declares **70 seats** (`spec.json` `maxLanes` 70, `maxLanes` == item count). The same role multiset appears independently in the 70 dispatch `taskCall.tasks` agent selectors and the 70 registry members; names are unique and in the same order in all three; the wave label is `kama-r52-w1` in spec, dispatch and registry (registry `wave` field); dispatch counts are `spawn 70 / resume 0 / total 70`.

| Role | Seats | Role | Seats |
|---|---:|---|---:|
| executor | 21 | scout | 10 |
| reviewer | 12 | critic | 8 |
| mutation-tester | 6 | scribe | 5 |
| sentinel | 3 | connector | 3 |
| simplifier | 1 | revenger | 1 |
| **Total** | **70** | | |

- Band: `ufo-wave-policy-v2.json:89-90` `waveMinLanes 64 / waveMaxLanes 128` → **64 ≤ 70 ≤ 128** ✓; `:84` `maxLanes 256` (validator hard ceiling) → 70 ≤ 256 ✓.
- Dispatch policy block reproduces the policy: `{source: config, maxLanes 70, minLanes 16, waveMinLanes 64, waveMaxLanes 128, declaredMaxLanes 70, hardCeiling 256, rampBatchSize 5, rampIntervalMs 700, globalRunnerCeiling 1056}` — equal to the policy's `sighting.dispatch` values.
- Shape is the addendum's **alternative — one v2 wave** (`lane-addendum.md:21-23`: 64–128 seats, 256 hard ceiling): one wave, build and attack items together, one `task` call (`dispatch.json` `note`). Ramp: `ceil(70/5)=14` batches × 700 ms = **9.8 s**.
- Role inventory: all ten dispatched roles are in `nativeProfiles.omp-native-v1.proposalRoles` (`ufo-wave-policy-v2.json:104-115`). The profile's `planner`/`distiller`/`labrat` seats are not wave seats; `planner` is held by the L1 per the standing ruling, and this wave dispatches no labrat.

## 3. Attack share

Attack roles are reviewer, critic, mutation-tester (`lane-addendum.md:19-20` keeps the ≥25 % attack share; the addendum's four-role reading at `:151-153` adds labrat, of which this wave has 0).

| Reading | Count | Share | Floor (25 % of 70 = 18) |
|---|---:|---:|---|
| reviewer 12 + critic 8 + mutation-tester 6 | **26** | **37.14 %** | MET |
| same + labrat 0 | 26 | 37.14 % | MET |

Axis spread of attack seats (items carry ≥1 axis): **calibration 16, operability 12** (two seats bind both). Prior-round continuity: r48 34/69 = 49.0 % (`corpus/lessons/round-48-verifier-spotcheck.md:28`), r50 20/66 = 30.30 % (`.ufo/waves/round-50/w1/out/X16Policy.md:3`), r51 25/66 = 37.88 % (`.ufo/waves/round-51/a2w1/out/Sen4Policy/policy.md:27`), **r52 26/70 = 37.14 %** — the attack share is stable across four rounds while wave size grows.

Connector seats: 3 of 70 (4.29 %) — the addendum's "few connector seats" rule (`lane-addendum.md:19-20`, run-8 antecedent `:47`) holds.

## 4. Live model map and per-model seat counts

Resolved `task.agentModelOverrides` (`config.yml:350-368`) → `modelRoles` (`:320-345`) → `enabledModels`. All ten wave roles have overrides, every alias exists in `modelRoles`, every resolved base model id is in `enabledModels`, and every alias used has a `retry.fallbackChains` entry (`config.yml:370+`).

| Live model target (alias) | Roles | Seats | Share |
|---|---|---:|---:|
| `minimax-code/MiniMax-M3.1-Flash:high` (`@m_mim`) | executor | 21 | 30.00 % |
| `zai/glm-5.3-flash:max` (`@m_zfl`) | reviewer 12, mutation-tester 6 | 18 | 25.71 % |
| `kimi-code/kimi-for-coding:max` (`@m_kfc`) | scout 10, critic 8 | 18 | 25.71 % |
| `opencode-go/deepseek-v4.1-flash:high` (`@m_flash`) | scribe 5, sentinel 3, simplifier 1, revenger 1 | 10 | 14.29 % |
| `google-antigravity/gemini-3.8-flash:high` (`@m_antigravity`) | connector | 3 | 4.29 % |

Fallback chains first hop: `@m_mim` → `opencode-go/deepseek-v4.1-flash`; `@m_zfl` → `devin/glm-5-3-flash-1m`; `@m_kfc` → `@m_swe` (`devin/swe-2:max`); `@m_flash` → `commandcode/deepseek/deepseek-v4.1-flash:high`; `@m_antigravity` → `cursor/gemini-3.8-flash`; all end at `openai-codex/gpt-6-luna:low`.

`m_flash` carries **10/70 = 14.29 %**; the run-7/8 "m_flash roles carry ≥50 %" condition no longer binds (`lane-addendum.md:18-20`), so this is not a violation. Attack concentration: 18 attack seats on GLM (`@m_zfl`) and 8 on Kimi (`@m_kfc`); no attack seat runs on `@m_flash` or `@m_antigravity` — attack review is entirely on non-flash routes, which matters because the volume tier (`@m_mim`, 21 seats) carries no attack seat at all.

## 5. Dispatch-time route-map fingerprint (round-50 closure R7)

- **mtime** `2026-10-27T02:39:08.510680Z` (= `2026-10-26 23:39:08.510680 -03:00`), ctime identical.
- **sha256** `0d5874660274d3a4545d9d1f9e1da320f0629a9efb384255b788b897bba6addc`, **size** 14,940 B.
- Registry `createdAt` (dispatch): `2026-10-27T05:05:10.877Z`; the config mtime precedes it by **8,762 s (2 h 26 min 10 s)**, so the observed file is the map in force at dispatch.
- The digest is **byte-identical to the map recorded for round 51** (`.ufo/waves/round-51/a2w1/out/Sen4Policy/policy.md`, same sha256): routing did not change between the two dispatches.
- Provenance gap carried from round 50: `dispatch.json`'s `policy` block records limits but no config fingerprint; the stat/hash above is the only recoverable record.

## 6. Findings

### F1 — `hyaku.env` run-9 route labels are stale for 42/70 seats (operability; medium; repeats round-51 F1)

`scripts/hyaku/hyaku.env:10-11` says run 9 uses "the same run-8 map, unchanged", and `:7-9` prints the run-8 map. The binding addendum records amendments made during run 9 (`lane-addendum.md:10-19`) and the live config matches the addendum, not those labels:

| Role | Seats | `hyaku.env` label | Live route |
|---|---:|---|---|
| executor | 21 | `@m_flash` | `@m_mim` |
| scout | 10 | `@m_sonnet` | `@m_kfc` |
| critic | 8 | `@m_flash` | `@m_kfc` |
| connector | 3 | `@m_kfc` | `@m_antigravity` |

**42/70 seats (60.00 %)** are mislabelled. A seat or auditor reading the helper would infer `@m_flash` = 52 seats and would not see `@m_mim` at all, misattributing model exposure. Live routing is correct (config + addendum agree), so this is a label defect only. Fix: replace the run-9 comment lines with the amended map — hunk in `proposed-fixes.diff` (applies with `patch -p1`, dry-run exit 0).

### F2 — policy `lanes[]` lists `labrat` and omits `sentinel` (calibration; low; carried from round-51 F3)

`ufo-wave-policy-v2.json:267-271` (`lanes[]`, table starts `:256`) lists `labrat`; `sentinel` — a `proposalRoles` member at `:109` and 3 seats this wave — is absent. The validator accepted the wave (`validate.out` `exit=0`) and routing uses config role overrides, so no dispatch failure follows. Fix: replace the `labrat` row with `sentinel` (`proposed-fixes.diff`).

### F3 — `omp-native-v1.concurrencyCeiling` 32 is below the band it governs (operability; low; new)

`ufo-wave-policy-v2.json:98` declares `concurrencyCeiling: 32` for the profile that runs these waves, while the same file's v2 band admits 64–128 lanes (`:89-90`), this wave dispatches 70, and the binding addendum says "at most ~88 seats run at once across the fleet" (`lane-addendum.md:24`). Nothing enforces the field — `grep -rn concurrencyCeiling scripts/` matches only the two policy JSONs (v1 `ufo-wave-policy.json`, v2 `ufo-wave-policy-v2.json`), never a runner — so the observed effect is a contradictory spec, not a throttle. Smallest fix: raise to 128 (wave max) or annotate the field as the legacy v1 per-wave ceiling superseded by `sighting.dispatch.swarm`. Both are in `proposed-fixes.diff` as the value change; the annotation alternative cannot be expressed in JSON without adding a note key.

### F4 — policy `surfaceDigest` lags the canonical origin (calibration; low; round-51 F5 now resolved in direction)

Policy `:55` records `sha256:1064c19a…bb4`; the origin `/home/vgpnk/Projects/ufo-fsd-alpha/config/ufo.json:55` records `sha256:610575e8…ce3` at HEAD `0fd34cab` (2026-10-24 22:52:26 -0300), worktree clean (`git status --porcelain config/ufo.json` empty; `git show HEAD:config/ufo.json` == worktree). The policy copy is dated 2026-10-22 15:55, i.e. **before** the origin's current pin, so the policy's value is the stale side. Note `1064c19a` was itself a deliberate re-charter recorded in `kumitate-shokunin/.ufo/waves/round-35/build/ScoutSurfaceProbe.md:111`, so this is drift, not corruption. The digest recipe is `sha256(canonicalJson(manifest))` (`kumitate-shokunin/corpus/knowledge/live-surface-probe.md:129`), so a refresh is mechanical — but it must be regenerated by that recipe, not hand-copied; the hunk in `proposed-fixes.diff` shows the target value only.

### F5 — three items bind axes outside the wave declaration (calibration; informational)

Wave `axes` are `calibration`, `operability`; `N1Overlap` (connector) binds `adjacency`, `A1Assim` (scout) binds `coverage`, `Sc3Province` (scout) binds `adjacency`+`operability`. Both extra axes are canonical (`/home/vgpnk/Projects/shokunin/AXES.md:12,16`) and the validator accepts item-level bindings independently (`validate.out` `exit=0`), so this is not a defect — but the wave-level declaration does not name two axes in use. 60 items bind one axis, 10 bind two.

### Resolved / non-findings

- **Round-51 F2 (conflicting executor labrat grant) is resolved here**: `grep -c labrat` over `round-52/w1/spec.json` = 0 and over `round-52/build_spec.py` = 0; every item carries the unambiguous "leaf member — no subagent dispatch" bound.
- No per-task `model` key in the dispatch (70/70 tasks are `{agent,name,task}`): the role map is the only routing authority, as the addendum requires.
- `m_flash ≥50 %` non-binding is honoured, not violated (14.29 %).

## 7. Reproduction

```sh
cd /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/Sen3Policy
./route_check.py > route_check.out 2>&1; echo $?      # 0
```

`route_check.out` prints 20 structural PASS lines (`RESULT pass`), the attack/per-model/alias tables, the config fingerprint with the 8,762 s delta, and the F1–F5 drift flags. It reads files only: no campaign tool, no counter, no service, no git/jj mutation, no network.

Proposed fixes: `proposed-fixes.diff` (both hunks verified with `patch -p1 --dry-run`, exit 0 against pristine copies in scratch).
