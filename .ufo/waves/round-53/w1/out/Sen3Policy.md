# Sen3Policy — round 53, lane kama, wave kama-r53-w1

**Verdict: PASS — the 66-seat v2 wave is in policy v2's 64–128 band under the 256 ceiling, its attack share is 21/66 = 31.82 % against a ≥25 % floor, and all 10 of its roles route through the live `task.agentModelOverrides` map exactly as the binding run-9 map requires (18/18 roles, zero drift, zero `model`/`modelAlias` passthrough). Four WARN-level divergences, all policy-text vs live-runtime or sizing/observability notes; 0 FAIL; nothing to fix in this wave's dispatch.**

Full deliverable: `.ufo/waves/round-53/w1/out/Sen3Policy/policy.md` (absolute
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/Sen3Policy/policy.md`),
with the re-runnable checker and raw facts listed at the end.

## 1. Method (one command, exit 0)

```
$ cd /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/Sen3Policy
$ python3 ./sen3policy-check.py --json route-facts.json --tables policy-tables.md > run.out 2> run.err
  exit=0   stderr 0 bytes   0 FAIL, 4 WARN
  WARN roles.in_policy_lanes | wave.declared_slack | concurrency.profile_ceiling | route.l1_alias
```

Inputs read (all read-only; no network; nothing written outside the out dir):

| input | sha256 |
|---|---|
| `/home/vgpnk/.omp/agent/config.yml` | `0d5874660274d3a4545d9d1f9e1da320f0629a9efb384255b788b897bba6addc` |
| `scripts/hyaku/ufo-wave-policy-v2.json` (fleet) | `f12e1d6dfeae81a4a1ff805f8de50ec8386b3a16ae7f40b171f54c5236812fff` |
| `.ufo/waves/round-53/w1/spec.json` (lane) | `43b7a9be52cf083e75eec5b9cfc7f72f97d5f1d81eb0bcd7167437a998606571` |
| `.ufo/waves/round-53/w1/dispatch.json` (lane) | `8fa275cf23631435ad1805e4b607ccd3fbd788a892cae20f5947e57a6d315623` |
| `.ufo/waves/round-53/w1/out/swarm-registry.json` (lane) | `84aab4c121d3547a94b1bec9f95ccd9ad7030c4e3378e2eddd7056f8b00897c0` |

## 2. Config record (as required)

`/home/vgpnk/.omp/agent/config.yml` — **mtime `2026-10-26T23:39:08.510680-03:00`** (epoch
1793068748.51068), **sha256 `0d5874660274d3a4545d9d1f9e1da320f0629a9efb384255b788b897bba6addc`**,
size 14940 B, mode 0600, `mtime == ctime`.

The wave registry was created `2026-10-27T06:11:43.122Z` = `03:11:43.122-03:00`, i.e. **3 h 32 m
34.6 s after** the config's last write, and the mtime still predates the wave — **no config write
during or after the spawn**, so the map measured here is the map that routed it. That is the
non-trivial part of this check: the run-9 map was amended four times on 2026-10-26
(`scripts/hyaku/lane-addendum.md:12-15`) and a seat keeps the model it was spawned with
(`lane-addendum.md:18`).

## 3. Wave shape

- 66 seats: `spec.json:4` `"maxLanes": 66`, 66 items, 66 `taskCall.tasks` in `dispatch.json`,
  66 registry members — three-way agreement, zero role mismatches.
- `dispatch.json:4-15` policy block: `maxLanes 66`, `declaredMaxLanes 66`, `hardCeiling 256`,
  `waveMinLanes 64`, `waveMaxLanes 128`; matches `ufo-wave-policy-v2.json:84-90`.
- Band 64 ≤ 66 ≤ 128 PASS (`ufo-wave-policy-v2.json:89-90`); 66 ≤ 256 PASS (`:84`);
  run-9 band identical (`lane-addendum.md:21-23`). Validator `validate.out` = `exit=0` (7 B,
  `validate.stderr` 0 B).
- Frozen-payload check: `git -C kama-shokunin show bc8e6e7f:.ufo/waves/round-53/w1/{spec,dispatch}.json | sha256sum`
  reproduces `43b7a9be…` and `8fa275cf…`, byte-equal to the working tree — the counts above describe
  the payload that was validated and spawned.

## 4. Numbers

Roles (66): executor 23 (34.85 %), critic 8 (12.12 %), scout 8 (12.12 %), reviewer 7 (10.61 %),
mutation-tester 6 (9.09 %), scribe 5 (7.58 %), sentinel 4 (6.06 %), connector 3 (4.55 %),
simplifier 1, revenger 1. All 10 roles ∈ `proposalRoles` (`ufo-wave-policy-v2.json:104-115`); no
`planner`, no `labrat` seat.

**Attack share: 21/66 = 31.82 % ≥ 25 % — PASS.** Identical under both definitions (seat item's
reviewer/critic/mutation-tester; addendum §2's list adds `labrat`, of which there are 0). Floors:
`lane-addendum.md:19-20`, roles `lane-addendum.md:150-153`. Attack independence holds by model, not
just by role: the 21 attack seats run on `zai/glm-5.3-flash` (13) and `kimi-code/kimi-for-coding`
(8), while the 23 executor seats run on `minimax-code/MiniMax-M3.1-Flash` — no attack seat shares the
executor model. Connector rule ("a few connector seats") met with 3 (4.55 %).

Per model under the live map (5 distinct models, 5 providers):

| model | seats | share | roles |
|---|---:|---:|---|
| `minimax-code/MiniMax-M3.1-Flash:high` | 23 | 34.85% | executor 23 |
| `kimi-code/kimi-for-coding:max` | 16 | 24.24% | critic 8, scout 8 |
| `zai/glm-5.3-flash:max` | 13 | 19.70% | reviewer 7, mutation-tester 6 |
| `opencode-go/deepseek-v4.1-flash:high` | 11 | 16.67% | scribe 5, sentinel 4, revenger 1, simplifier 1 |
| `google-antigravity/gemini-3.8-flash:high` | 3 | 4.55% | connector 3 |

Top concentration 34.85 %; no model above 50 %.

## 5. Route check

| role | seats | override | alias → model | fallback head |
|---|---:|---|---|---|
| connector | 3 | `@m_antigravity` | `google-antigravity/gemini-3.8-flash:high` | `cursor/gemini-3.8-flash` |
| critic | 8 | `@m_kfc` | `kimi-code/kimi-for-coding:max` | `@m_swe` |
| executor | 23 | `@m_mim` | `minimax-code/MiniMax-M3.1-Flash:high` | `opencode-go/deepseek-v4.1-flash` |
| mutation-tester | 6 | `@m_zfl` | `zai/glm-5.3-flash:max` | `devin/glm-5-3-flash-1m` |
| reviewer | 7 | `@m_zfl` | `zai/glm-5.3-flash:max` | `devin/glm-5-3-flash-1m` |
| scout | 8 | `@m_kfc` | `kimi-code/kimi-for-coding:max` | `@m_swe` |
| scribe / sentinel / simplifier / revenger | 5 / 4 / 1 / 1 | `@m_flash` | `opencode-go/deepseek-v4.1-flash:high` | `commandcode/deepseek/deepseek-v4.1-flash:high` |

- **`route.run9_map_equality` PASS** — all 18 roles of the binding run-9 map (`lane-addendum.md:15-18`)
  match the live overrides in `config.yml:350-368`; drift none; roles outside the map none.
- `roles.resolve` PASS 10/10; `models.enabled` PASS 5/5 (base ids in `config.yml:3-316`, 313 entries);
  `aliases.fallback` PASS 10/10 rows / 5 distinct aliases, every chain head on a different provider.
- `dispatch.no_model_passthrough` PASS — 0 non-null `model`/`modelId`/`modelRole`/`modelOverride`/
  `modelAlias` keys anywhere in `dispatch.json`; spec declares no wave-level `modelAlias` and no item
  declares one, so routing was role-only (`lane-addendum.md:184-185`). The dispatcher's per-seat
  `modelAlias` channel (`ufo-swarm-wave.mjs:32-46`) exists and was unused.
- Observed, not predicted: this seat is `sentinel` → `@m_flash` → `opencode-go/deepseek-v4.1-flash:high`,
  and the session reports `opencode-go/deepseek-v4.1-flash`. **1 of 66 seats corroborated live**; the
  other 65 are predictive — see W5.

## 6. Findings (WARN; none changes this wave's dispatch)

Full text, impact and remediation in `policy.md` §7. Summary:

- **W1 (low)** `ufo-wave-policy-v2.json:81` `l1Alias: "m_strong"` → `anthropic/claude-opus-5-5:max`
  (`config.yml:320`) vs the live L1 route `task`/`main` → `@m_opus` → `…:high` (`config.yml:350-352`,
  `340`). A consumer that reads the alias instead of the map pins one effort tier higher.
- **W2 (low)** `ufo-wave-policy-v2.json:98` `concurrencyCeiling: 32` (transport `omp/task`, not
  overridden by v2/resilient) vs 66 seats in one call. Live ceilings diverge five ways:
  `task.maxConcurrency 400` (`config.yml:348`), `async.maxJobs 450` (`:489`), policy
  `globalRunnerCeiling 1056`, `maxConcurrentL1 16`, addendum "~88 at once / 100 per session"
  (`lane-addendum.md:24-26`).
- **W3 (low)** `ufo-wave-policy-v2.json:256` `lanes[]` omits `sentinel` (present in `proposalRoles`
  `:104-115` and in the live map `config.yml:357`): 4/66 seats (6.06 %) on a role that enumeration
  does not list. Inherited from v1 (`b5f635af…`), not introduced by v2.
- **W4 (info)** `spec.json:4` `maxLanes 66` == 66 items: zero slack, so any residual call folded into
  this wave would exceed its own declared ceiling although the policy allows 128/256.
- **W5 (low–medium, calibration)** No seat→model binding exists anywhere: registry members carry only
  `agentId, axes, item, kind, milestone, role`; spec/dispatch declare no `modelAlias`;
  `w1.ready.dispatched` maps seat → agent id only. The dispatcher cannot record it — without a
  declared alias the payload carries `agent: <role>` and **the host** resolves at spawn
  (`ufo-swarm-wave.mjs:32-46`), and forcing it with `modelAlias` is what
  `lane-addendum.md:184-185` forbids. So `lane-addendum.md:190`'s "record a seat's actual answering
  model" can only be satisfied seat-side (as this report does for 1/66) plus L1 aggregate; a silent
  fallback chain firing would leave no trace in the artifacts.

**Proposed fix shipped, not applied:** `policy-note.diff` — one existing string
(`sighting.dispatch.swarm.note`, no new keys, no schema change) covering W1 and W2. Verified in a
scratch fixture repo: `git -C <fixture> apply --check` exit 0, file stays valid JSON (13 top-level
keys, note 853 chars). The policy file is fleet-tracked, operator-owned and frozen for this round —
this seat did not touch it.

## 7. Boundaries of this seat's evidence

Not checked here, by design: the two claim counters C1/C2 and their receipts; per-item role fitness
(whether each executor item really writes code and each scribe item really drafts prose); dead seats
(the wave was still running when this was written); the 65 seats' answering models (W5). No lane
file, no fleet file, no sibling lane, no git/jj state was written; one `mktemp -d` fixture repo in
scratch (`/fast/scratch/hyaku/kama-r53/Sen3Policy`, `git rev-parse --show-toplevel` verified equal to
it) was used only to prove the proposed diff applies, and it was removed with the scratch dir.

Process hygiene: this seat started **no** llama-server and no service. `pgrep -af llama-server` at
finish shows 2 processes, both rooted in seat **K2Design**'s scratch tree
(`/fast/scratch/hyaku/kama-r53/K2Design/hold2/…`) — that seat's processes, not mine to kill. No
pacman, no tool installs, and no network access of any kind (the checker reads local files only).

Scratch `/fast/scratch/hyaku/kama-r53/Sen3Policy` removed (`rm -rf`) after copying the only artifact
worth keeping (`policy-note.diff`) into the out dir.

## 8. Axes

**Calibration:** the wave's size/attack/model distribution is pinned to hashes of the payload that
actually ran, with a committed-blob-vs-working-tree equality check that the spec and dispatch were not
edited after validation, and the config's exact mtime/sha256 recorded so the map-measured-equals-
map-that-routed claim is falsifiable rather than asserted. **Operability:** one command with an exit
code reproduces every number, table and check; the four WARNs each name the consumer that would break
and the smallest edit that would remove the ambiguity.
