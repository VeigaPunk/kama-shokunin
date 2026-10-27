# Sen3Policy — wave policy and route check (kama-r53-w1, round 53, lane kama)

**Verdict: PASS.** The 66-seat v2 wave is inside policy v2's 64–128 band and under the 256 hard
ceiling; its attack share is **21/66 = 31.82 %** against a **≥25 %** floor; and all 10 roles it uses
route through the live `task.agentModelOverrides` map exactly as the binding run-9 map requires
(18/18 roles compared, **no drift**, **0** roles outside the map, **0** `model`/`modelAlias`
passthroughs in the validated payload). Four WARN-level divergences were found — every one is
policy-text vs live-runtime or a sizing/observability note, none of them altered this wave's
dispatch. No FAIL.

Two axes: **calibration** (are the recorded counts the ones that actually ran, and is the record
re-derivable?) and **operability** (can the next round recompute all of it without this seat?).

## 0. Pins (what was measured, and the bytes it was measured from)

| input | path | sha256 / identity |
|---|---|---|
| live route map | `/home/vgpnk/.omp/agent/config.yml` | `0d5874660274d3a4545d9d1f9e1da320f0629a9efb384255b788b897bba6addc` — 14940 B, mode 0600, **mtime 2026-10-26T23:39:08.510680-03:00** (epoch 1793068748.51068) |
| policy v2 | `scripts/hyaku/ufo-wave-policy-v2.json` (fleet) | `f12e1d6dfeae81a4a1ff805f8de50ec8386b3a16ae7f40b171f54c5236812fff` |
| policy v1 (for contrast) | `scripts/hyaku/ufo-wave-policy.json` (fleet) | `b5f635af526c8af7aef2c3aef8ec950a8f2495cf715ebe3fc3b64f0b5225816d` |
| wave spec | `.ufo/waves/round-53/w1/spec.json` (lane) | `43b7a9be52cf083e75eec5b9cfc7f72f97d5f1d81eb0bcd7167437a998606571` |
| validated payload | `.ufo/waves/round-53/w1/dispatch.json` (lane) | `8fa275cf23631435ad1805e4b607ccd3fbd788a892cae20f5947e57a6d315623` |
| spawn registry | `.ufo/waves/round-53/w1/out/swarm-registry.json` (lane) | `84aab4c121d3547a94b1bec9f95ccd9ad7030c4e3378e2eddd7056f8b00897c0` |
| validator result | `.ufo/waves/round-53/w1/validate.out` (lane) | 7 bytes, `exit=0`; `validate.stderr` 0 bytes |

All paths above are absolute and outside the fleet root except the two policy files, which are
fleet-tracked and read-only for this seat.

**Frozen-payload check (calibration).** The counts below must describe the payload that was
validated and spawned, not a later edit. Both blobs committed at lane commit
`bc8e6e7f1c53ea6f557001cea1e4d1e8b586c18e` hash equal to the working tree:

```
git -C kama-shokunin show bc8e6e7f:.ufo/waves/round-53/w1/spec.json     | sha256sum
  -> 43b7a9be52cf083e75eec5b9cfc7f72f97d5f1d81eb0bcd7167437a998606571   (= working tree)
git -C kama-shokunin show bc8e6e7f:.ufo/waves/round-53/w1/dispatch.json | sha256sum
  -> 8fa275cf23631435ad1805e4b607ccd3fbd788a892cae20f5947e57a6d315623   (= working tree)
```

## 1. Wave shape and size

- `spec.json:4` `"maxLanes": 66`; the spec carries **66** items and the payload carries **66**
  tasks (`dispatch.json` `taskCall.tasks`), and the registry carries **66** members — a three-way
  agreement with zero role mismatches (`seats.agreement` PASS, `registry.roles_match_spec` PASS).
- `dispatch.json:4-15` records the policy it was validated against: `maxLanes 66`,
  `declaredMaxLanes 66`, `hardCeiling 256`, `minLanes 16`, `waveMinLanes 64`, `waveMaxLanes 128`,
  `globalRunnerCeiling 1056` — matching policy v2 `sighting.dispatch.swarm`
  (`ufo-wave-policy-v2.json:84-90`).
- Band: `64 <= 66 <= 128` (policy-v2:89-90) → PASS. Hard ceiling: `66 <= 256` (policy-v2:84) → PASS.
  The binding addendum's run-9 band is the same (`scripts/hyaku/lane-addendum.md:21-23`).
- Shape: one v2 wave (the addendum's "Alternative" shape, `lane-addendum.md:151-153`) — build and
  attack items together, no residual `task` call.

## 2. Seats by role (66)

| role | seats | share | axes |
|---|---:|---:|---|
| executor | 23 | 34.85% | calibration,operability |
| critic | 8 | 12.12% | calibration,operability |
| scout | 8 | 12.12% | adjacency,calibration,coverage,operability |
| reviewer | 7 | 10.61% | calibration,operability |
| mutation-tester | 6 | 9.09% | calibration,operability |
| scribe | 5 | 7.58% | calibration,operability |
| sentinel | 4 | 6.06% | calibration,operability |
| connector | 3 | 4.55% | adjacency,calibration,operability |
| simplifier | 1 | 1.52% | calibration,operability |
| revenger | 1 | 1.52% | calibration |
| **total** | **66** | 100.00% | |

Every role is in policy v2 `nativeProfiles.omp-native-v1.proposalRoles`
(`ufo-wave-policy-v2.json:104-115`) — `roles.in_policy_proposalRoles` PASS. No `planner` seat
appears (the validator rejects it; the L1 holds the planner seat), and no `labrat` probe seat was
spawned.

## 3. Attack share

| definition | roles | seats | share | floor | result |
|---|---|---:|---:|---:|---|
| seat item (primary) | reviewer/critic/mutation-tester | 21/66 | 31.82% | ≥25% | **PASS** |
| addendum §2 (extended) | reviewer/critic/mutation-tester/labrat | 21/66 | 31.82% | ≥25% | **PASS** |

Both definitions coincide here because the wave carries **0** labrat seats; the floor is
`lane-addendum.md:19-20` (run-9: "the ≥25 % attack share and the few-connector-seats rule still
apply") and the role list is `lane-addendum.md:151-153`.

Two structural properties worth recording, both derived from the tables in §4:

- **Attack independence is by model, not just by role.** The 21 attack seats run on
  `zai/glm-5.3-flash` (13: reviewers 7 + mutation-testers 6) and `kimi-code/kimi-for-coding`
  (8: critics); the 23 executor seats — whose code and tools the attack seats falsify — run on
  `minimax-code/MiniMax-M3.1-Flash`. No attack seat shares the executor model, so a
  model-specific blind spot cannot silently agree with itself across the build/attack boundary.
- **Connector rule satisfied:** 3 connector seats (4.55 %) — "a few connector seats"
  (`lane-addendum.md:19-20`).

## 4. Seats per model under the live map

| model | seats | share | roles |
|---|---:|---:|---|
| `minimax-code/MiniMax-M3.1-Flash:high` | 23 | 34.85% | executor 23 |
| `kimi-code/kimi-for-coding:max` | 16 | 24.24% | critic 8, scout 8 |
| `zai/glm-5.3-flash:max` | 13 | 19.70% | reviewer 7, mutation-tester 6 |
| `opencode-go/deepseek-v4.1-flash:high` | 11 | 16.67% | scribe 5, sentinel 4, revenger 1, simplifier 1 |
| `google-antigravity/gemini-3.8-flash:high` | 3 | 4.55% | connector 3 |
| **distinct models: 5** | **66** | 100.00% | |

- Highest single-model concentration: **34.85 %** (23/66); nothing exceeds 50 %.
- Five distinct models across five providers (minimax-code, kimi-code, zai, opencode-go,
  google-antigravity) — no provider-outage blast radius above 34.85 %.

## 5. Route check (role → alias → model, live `task.agentModelOverrides`)

| role | seats | override | alias → model | fallback head | in `enabledModels` |
|---|---:|---|---|---|---|
| connector | 3 | `@m_antigravity` | `google-antigravity/gemini-3.8-flash:high` | `cursor/gemini-3.8-flash` | yes |
| critic | 8 | `@m_kfc` | `kimi-code/kimi-for-coding:max` | `@m_swe` | yes |
| executor | 23 | `@m_mim` | `minimax-code/MiniMax-M3.1-Flash:high` | `opencode-go/deepseek-v4.1-flash` | yes |
| mutation-tester | 6 | `@m_zfl` | `zai/glm-5.3-flash:max` | `devin/glm-5-3-flash-1m` | yes |
| revenger | 1 | `@m_flash` | `opencode-go/deepseek-v4.1-flash:high` | `commandcode/deepseek/deepseek-v4.1-flash:high` | yes |
| reviewer | 7 | `@m_zfl` | `zai/glm-5.3-flash:max` | `devin/glm-5-3-flash-1m` | yes |
| scout | 8 | `@m_kfc` | `kimi-code/kimi-for-coding:max` | `@m_swe` | yes |
| scribe | 5 | `@m_flash` | `opencode-go/deepseek-v4.1-flash:high` | `commandcode/deepseek/deepseek-v4.1-flash:high` | yes |
| sentinel | 4 | `@m_flash` | `opencode-go/deepseek-v4.1-flash:high` | `commandcode/deepseek/deepseek-v4.1-flash:high` | yes |
| simplifier | 1 | `@m_flash` | `opencode-go/deepseek-v4.1-flash:high` | `commandcode/deepseek/deepseek-v4.1-flash:high` | yes |

Sources: overrides at `config.yml:350-368`, aliases at `config.yml:317-346`, chains at
`config.yml:370-483`, `enabledModels` at `config.yml:3-316` (313 entries; the list holds base model
ids, so the `:high`/`:max` effort suffix on an alias target is dropped only for this membership
test).

Checks:

- `route.run9_map_equality` **PASS** — all 18 roles of the binding run-9 map
  (`lane-addendum.md:15-18`) are present in the live overrides with the same alias: task/main/
  planner `@m_opus`; executor `@m_mim`; reviewer/mutation-tester/security-reviewer `@m_zfl`;
  scribe/sonic/simplifier/revenger/labrat/sentinel `@m_flash`; critic/scout `@m_kfc`; connector
  `@m_antigravity`; distiller/seance `@m_haiku`. Drift: none. Roles outside the map: none.
- `roles.resolve` **PASS** — 10/10 wave roles have an `agentModelOverrides` entry (no role fell
  through to an unset default).
- `models.enabled` **PASS** — 5/5 resolved models are enabled.
- `aliases.fallback` **PASS** — 10/10 role rows (5 distinct aliases: `@m_mim`, `@m_zfl`, `@m_kfc`,
  `@m_flash`, `@m_antigravity`) have a `retry.fallbackChains` entry, and every
  chain's head is a *different* provider from the primary. One convergence worth noting: `@m_mim`'s
  fallback head is `opencode-go/deepseek-v4.1-flash` — the same family the 11 `@m_flash` seats run
  on — so a `m_mim` provider outage would collapse executor and sentinel/scribe traffic onto one
  model. That is a capacity risk, not a routing defect.
- `dispatch.no_model_passthrough` **PASS** — 0 `model`/`modelId`/`modelRole`/`modelOverride` keys
  anywhere in `dispatch.json`; the spec declares no wave-level `modelAlias` and no item declares
  one, so routing was role-only as the addendum requires. The dispatcher's per-seat `modelAlias`
  channel (`ufo-swarm-wave.mjs:32-46`) was available and unused.
- Observed, not predicted: this seat is `sentinel` → `@m_flash` → `opencode-go/deepseek-v4.1-flash:high`,
  and the session reports `opencode-go/deepseek-v4.1-flash`. That corroborates the map for **1 of 66
  seats**; the other 65 are predictive for the reason in W5.

## 6. Route stability across the spawn window

- Config last written **2026-10-26T23:39:08.510680-03:00**; the wave registry was created
  **2026-10-27T06:11:43.122Z = 2026-10-27T03:11:43.122-03:00** — the map was **3 h 32 m 34.6 s** old
  at wave creation. `mtime == ctime`, and mtime still predates the wave, so **no config write has
  happened since the map was captured**: the map that routed the spawn is byte-identical to the map
  measured here (`0d587466…`).
- This matters because the run-9 map was amended four times on 2026-10-26 (`lane-addendum.md:12-15`)
  and "a seat keeps the model it was spawned with" (`lane-addendum.md:18`). An amendment after
  03:11:43-03 would have produced a wave whose seats route to two different maps with no record of
  which; it did not happen.

## 7. Findings (all WARN; none changes this wave's dispatch)

### W1 — policy `l1Alias` names a different effort tier than the live L1 route (severity: low)
`ufo-wave-policy-v2.json:81` declares `missionFormat.l1Alias = "m_strong"` →
`anthropic/claude-opus-5-5:max` (`config.yml:320`). The live map routes the roles that spawn L1s,
`task`/`main`, to `@m_opus` → `anthropic/claude-opus-5-5:high` (`config.yml:350-352`, `340`); the
config also carries a `default` role pinned at `:max` (`config.yml:346`). Same family, one effort
tier apart.
**Impact:** a launcher that derives the L1 route from the policy alias instead of the map pins
`:max`, i.e. a cost/latency delta and a different record of "which model answered the L1". The
binding addendum makes the map authoritative (`lane-addendum.md:12-18`), so this is drift between
two declared sources, not a runtime failure — every observed L1 in this campaign routes through the
map.
**Smallest remediation:** do not edit the frozen fixture's routing keys. Extend the existing
`swarm.note` string (no new keys, no schema change) so a reader of the policy cannot mistake the
alias for the route — patch in `policy-note.diff` (applies clean, JSON stays valid; verified in a
scratch fixture repo with `git apply --check` → 0).

### W2 — policy profile ceiling 32 vs 66 seats in one `task` call (severity: low)
`ufo-wave-policy-v2.json:98` sets `nativeProfiles.omp-native-v1.concurrencyCeiling: 32` for
transport `omp/task`; `v2` and `resilient-v1` extend `omp-native-v1` additively and do not override
it. The wave dispatched 66 seats in one call. Live ceilings diverge too: `task.maxConcurrency: 400`
(`config.yml:348`), `async.maxJobs: 450` (`config.yml:489`), policy
`sighting.dispatch.globalRunnerCeiling: 1056`, `maxConcurrentL1: 16`, and the addendum's prose
"At most ~88 seats run at once across the fleet (omp caps one session at 100 running agents)"
(`lane-addendum.md:24-26`).
**Impact:** a gate that enforced the profile's 32 would refuse every legitimate run-9 v2 wave
(64–128); conversely no artifact in the wave shows it was checked against *any* ceiling except the
spec's own 66. Five numbers, one of which the wave exceeds.
**Smallest remediation:** same note extension as W1 (it covers this case in the same sentence);
W2 is a documentation defect, not a dispatch defect — the wave ran, `validate.out` is `exit=0`.

### W3 — policy `lanes[]` omits `sentinel` (severity: low)
`ufo-wave-policy-v2.json:256` enumerates 10 lane roles (scout, reviewer, labrat, critic, connector,
executor, mutation-tester, revenger, simplifier, scribe). `sentinel` is absent from `lanes[]` while
being present in `proposalRoles` (`:104-115`) and in the live map (`config.yml:357`). The same
asymmetry exists in v1 (`b5f635af…`), so it is inherited, not introduced by v2. This wave carries
**4 sentinel seats (6.06 %)**.
**Impact:** a tool that treats `lanes[]` as the admissible role set refuses 4 of 66 seats;
`proposalRoles` and `lanes[]` are two different sets that a consumer must not conflate
(`lanes[]` also lists `labrat`, which is not a proposal role).
**Smallest remediation:** record it; no edit to the frozen fixture. If the policy is ever re-cut,
make `lanes[] = proposalRoles ∪ {labrat} − {sentinel}` explicit in the file's own note.

### W4 — declared ceiling has zero slack (severity: info)
`spec.json:4` `maxLanes 66` against 66 items. Any residual call folded into this wave (the
addendum allows ≤8 reviewer/critic seats, `lane-addendum.md:155-157`) would exceed the spec's own
declared ceiling, even though the policy's `waveMaxLanes` is 128 and the hard ceiling 256.
**Impact:** sizing only — a round-54 wave should either leave slack or declare `maxLanes 128` and
size inside it.

### W5 — no seat→model binding is recorded anywhere (severity: low–medium; calibration)
Registry members carry exactly six keys — `agentId, axes, item, kind, milestone, role` — and no
model field; the spec and dispatch declare no `modelAlias`; `w1.ready.dispatched` maps seat →
*agent id* only. So the wave's actual answering model per seat cannot be verified post hoc.
**Impact:** `lane-addendum.md:190` requires recording a seat's actual answering model when a claim
depends on it. For this wave that record exists only as a predictive mapping (this document) plus
one observed seat. If a provider silently degraded and a fallback chain fired, nothing in the
artifacts would show it — the strongest available claim is "role R routes to model M under config
hash H", never "seat S answered on model M".
**Smallest remediation (not this seat's write scope).** The dispatcher *cannot* record it: without a
declared `modelAlias` the payload carries `agent: <role>` and **the host** resolves the alias at
spawn (`ufo-swarm-wave.mjs:32-46`, esp. "the HOST resolves the alias at spawn"), so the lane side
never sees the model. Forcing the binding with per-item `modelAlias` is exactly what the run rule
forbids (`lane-addendum.md:184-185`, "The role decides the route. Never pass `model`"). The workable
fix is at the other end: a seat whose claim depends on the answering model states it in its own
report (as this seat does), and the L1 records it in the round's QUALITY/LOG row — the record then
comes from the seat that ran, not from a lane-side guess.

## 8. Reproduction (operability)

```
$ cd /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/Sen3Policy
$ python3 ./sen3policy-check.py --json route-facts.json --tables policy-tables.md
  exit=0   # 0 FAIL, 4 WARN: roles.in_policy_lanes, wave.declared_slack,
           # concurrency.profile_ceiling, route.l1_alias
```

The script reads only the files pinned in §0 (paths overridable by `POLICY`, `SPEC`, `DISPATCH`,
`REGISTRY`, `CONFIG` env vars), needs no network, writes nothing outside the paths given on the
command line, and re-derives every number, table and check in this document. `route-facts.json`
holds the same facts machine-readably (including the config sha256/mtime/size/mode and the full
check list); `policy-tables.md` holds the tables verbatim.

**Axes moved.** Calibration: the wave's size, attack share and per-model distribution are now
pinned to exact hashes of the payload that ran, with a frozen-payload check that the spec and
dispatch were not edited after validation. Operability: one command reproduces the whole record, and
the four WARNs name the exact policy/consumer edit each would need — no judgment call is left
implicit in a number.
