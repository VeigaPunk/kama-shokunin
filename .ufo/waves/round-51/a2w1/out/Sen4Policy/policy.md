# Sen4Policy — Round 51 policy and route check

Verdict: **wave size and attack share conform; every live role route resolves to an enabled model with a fallback chain.** The dispatch-time route map is now recoverable from the recorded config fingerprint and mapping below. Three operability/calibration defects remain: stale `hyaku.env` role labels, contradictory executor labrat instructions, and the policy `lanes[]` table omits `sentinel` while listing `labrat` (not a wave role).

## Scope and method

Read-only inspection of the frozen wave spec, its rendered dispatch and registry, `scripts/hyaku/ufo-wave-policy-v2.json`, `/home/vgpnk/.omp/agent/config.yml`, the binding run-9 lane addendum and the round's spec builder. Reproducible check: `./route_check.py` from this directory; output: `route_check.out`; exit **0**. It asserts source agreement and successful model resolution; printed drift items are findings, not test failures.

## Wave size, role counts, attack share

Spec `kama-r51-a2w1` declares 66 seats (`spec.json` `maxLanes=66`). The same role multiset appears independently in all 66 `dispatch.json` tasks and 66 `out/swarm-registry.json` members; names are unique, wave labels agree, and the validator receipt says `exit=0` (`validate.out`; stderr empty).

| Role | Seats |
|---|---:|
| executor | 18 |
| reviewer | 11 |
| critic | 9 |
| scribe | 7 |
| mutation-tester | 5 |
| scout | 5 |
| sentinel | 4 |
| connector | 4 |
| revenger | 2 |
| simplifier | 1 |
| **Total** | **66** |

The binding run-9 addendum keeps the ≥25% attack share and defines attack seats as reviewer/critic/mutation-tester/labrat (`scripts/hyaku/lane-addendum.md:18-20,153`). The wave has no labrat seats, so both the seat prompt's three-role count and the addendum's four-role count yield **25/66 = 37.88%** (reviewer 11 + critic 9 + mutation-tester 5; 17 seats are the 25% floor). Four connector seats (6.06%) satisfy the addendum's “few connector seats” guidance. Wave size 66 is inside the v2 64–128 band and below `maxLanes=256` (`scripts/hyaku/ufo-wave-policy-v2.json:83-90); dispatch policy records the same band and 256 hard ceiling. Ramp: ceil(66/5)=14 batches × 700 ms = 9.8 s.

## Live model map and counts

Resolved by `task.agentModelOverrides` → `modelRoles` → `enabledModels`; all ten wave roles have overrides, all resolved targets are enabled and each alias has a fallback chain. Dispatch tasks contain only `{agent,name,task}`—no model override—so role routing remains the operative map, as required by the addendum.

| Live model target | Roles | Seats |
|---|---|---:|
| `minimax-code/MiniMax-M3.1-Flash:high` | executor | 18 |
| `zai/glm-5.3-flash:max` | reviewer 11, mutation-tester 5 | 16 |
| `kimi-code/kimi-for-coding:max` | critic 9, scout 5 | 14 |
| `opencode-go/deepseek-v4.1-flash:high` | scribe 7, sentinel 4, revenger 2, simplifier 1 | 14 |
| `google-antigravity/gemini-3.8-flash:high` | connector | 4 |

The attack seats are split across two targets: 16 on GLM and 9 on Kimi. The retired run-7/8 “m_flash ≥50%” condition is explicitly non-binding in run 9 (`lane-addendum.md:18-19`); this report does not treat the current 14/66 m_flash share as a violation.

## Dispatch-time route-map fingerprint (round-50 closure R7)

`/home/vgpnk/.omp/agent/config.yml` was statted and hashed by `route_check.py`:

- mtime: **2026-10-26 23:39:08.510680072 -0300** (**2026-10-27T02:39:08.510680Z**); ctime identical.
- SHA-256: `0d5874660274d3a4545d9d1f9e1da320f0629a9efb384255b788b897bba6addc`; size 14,940 bytes.
- Wave registry `createdAt` (dispatch timestamp): `2026-10-27T03:46:01.304Z`; the config mtime preceded it by **4,012 seconds** (1 h 6 min 52 s). Thus the observed config file version predates dispatch and is the map recorded here.
- The role→alias→target resolution table and the exact spec/dispatch/registry fingerprints are preserved in `route_check.out`. The dispatch `policy` block records only its policy source/limits, not a `~/.omp/agent/config.yml` fingerprint; the captured mtime, digest and resolved map address that provenance gap.

## Findings

### F1 — `hyaku.env` run-9 route labels are stale for 36 seats (operability/calibration; medium)

`/home/vgpnk/Projects/shokunin/scripts/hyaku/hyaku.env:8-11` says run 9 uses the unchanged run-8 map, while the binding addendum records amendments and the current map (`lane-addendum.md:10-17`). Live `config.yml` routes four wave roles differently from those labels:

| Role | Seats | `hyaku.env` label | Live route |
|---|---:|---|---|
| executor | 18 | `@m_flash` | `@m_mim` |
| critic | 9 | `@m_flash` | `@m_kfc` |
| scout | 5 | `@m_sonnet` | `@m_kfc` |
| connector | 4 | `@m_kfc` | `@m_antigravity` |

That is **36/66 seats (54.55%)**. The stale labels imply `@m_flash` has 41 seats and omit `@m_mim`/`@m_antigravity`; the actual resolved counts are `m_flash` 14, `m_mim` 18, Kimi 14, GLM 16, Antigravity 4. A seat/auditor relying on this prompt/event-label file would misattribute model exposure and model-specific attack concentration. The role overrides in config and the binding addendum agree; the defect is the helper's run-9 summary. Smallest fix: replace the run-9 “same run-8 map, unchanged” text with the amended current map. Proposed hunk: `proposed-fixes.diff`.

### F2 — executor gets conflicting labrat permission and prohibition (operability; medium, recurring round-50 F4)

The rendered bounds grant each executor “no subagent dispatch **except your single labrat**”; exactly 18 executor tasks contain this grant. The shared round context also says “do not spawn subagents (leaf)” without exception. The binding addendum permits an executor one read-only labrat probe (`lane-addendum.md:222-223`), so this is a genuine same-prompt conflict affecting **18/66 seats**; it is not resolved by the absence of labrat-role seats, because the labrat is a subordinate probe. Smallest fix: qualify the context prohibition with the executor's one read-only labrat exception. Proposed hunk targets `kama-shokunin/.ufo/waves/round-51/build_spec.py:44` in `proposed-fixes.diff`.

### F3 — policy substrate role inventory mismatches this dispatched wave (calibration; low, carried)

Policy `nativeProfiles.omp-native-v1.proposalRoles` includes `sentinel` (`ufo-wave-policy-v2.json:104-115`), and the wave dispatches four sentinel seats; the separate `lanes[]` table at lines 256-306 instead lists `labrat` and omits `sentinel`. The validator accepted the wave (`validate.out` exit 0), and actual task routing uses config role overrides, so no dispatch failure was observed. Still, the policy table gives an inaccurate role/substrate inventory. Smallest correction: replace the `labrat` row in `lanes[]` with `sentinel` (proposed hunk included).

### F4 — two item axes are outside the wave's declared axes (calibration; informational)

Wave axes are `calibration` and `operability`; `N1Overlap` binds only `adjacency`, and `Sc5Province` binds `adjacency` plus `operability`. `adjacency` is a canonical axis (`AXES.md:16`), and the validator accepts item-level axis bindings independently; validation passed. This is therefore not reported as a defect, but the wave-level declaration does not name one axis used by two seats.

### F5 — policy `surfaceDigest` differs from live `ufo.json` (unadjudicated discrepancy)

The policy records `sha256:1064c19a…`, while `/home/vgpnk/Projects/ufo-fsd-alpha/config/ufo.json` records `sha256:610575e8…` (`route_check.out`; full values there). This seat compared the recorded values but did not recompute the canonical digest, so it does not conclude which value is stale. It is not needed to decide this wave's role counts.

## Reproduction

`cd /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/Sen4Policy && ./route_check.py` → **exit 0**, `RESULT pass`. It cross-counts all roles in spec/dispatch/registry, resolves all routes and checks enabled/fallback coverage, calculates attack share, checks the v2 band/validator receipt and records the route-map mtime/hash. The output explicitly prints F1/F3/F5 values and the 18-seat labrat grant. No campaign tool, counter, service, or Git/JJ mutation was run.
