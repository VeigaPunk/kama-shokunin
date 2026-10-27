**Verdict: `kama-r52-w1` conforms to hyaku policy v2 — 70 seats inside the 64–128 band (`maxLanes` 70 ≤ 256), spec/dispatch/registry agree key for key, all ten roles resolve through the live `task.agentModelOverrides` map to an enabled model with a fallback chain, attack share 26/70 = 37.14 % (≥25 % MET), and the dispatch-time route map is fingerprinted (mtime `2026-10-27T02:39:08.510680Z`, sha256 `0d587466…addc`, 14,940 B, 8,762 s before dispatch); four documentation drift defects (F1–F4) and one informational axis note (F5), none blocking.**

# Sen3Policy — round 52 wave policy and route check

Seat `Sen3Policy`, role sentinel, axes calibration + operability. Read-only inspection: no counter, no campaign tool, no service, no process started, no git/jj mutation anywhere. This seat launched no `llama-server`; the two processes visible at the end of the pass belong to peer `M3Live` (`/fast/scratch/hyaku/kama-r52/M3Live/c1-M04/…/kama-llamacpp-live.py`), not to this seat.

## Evidence

### E1 — structural agreement (spec ↔ dispatch ↔ registry)

```
$ cd /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/Sen3Policy
$ ./route_check.py > route_check.out 2>&1; echo $?
0
$ grep -c '^PASS' route_check.out ; grep -c '^FAIL' route_check.out ; tail -1 route_check.out
20
0
RESULT pass
```

PASS lines (all 20): spec count == maxLanes (70); names unique; dispatch `taskCall` order/names == spec; registry order/names == spec; dispatch agent selectors == spec role multiset; registry roles == spec role multiset; wave label `kama-r52-w1` consistent across all three; **no per-task `model` key**; counts `{spawn 70, resume 0, total 70}`; schemas `ufo-swarm-wave-dispatch-v1`/`ufo-swarm-registry-v1`; validator `validate.out` = `exit=0` with `validate.stderr` 0 B; band `64 ≤ 70 ≤ 128`; `70 ≤ 256`; dispatch policy block == policy v2; declared maxLanes == spec == seats; `globalRunnerCeiling` 1056 == policy; all roles are `omp-native-v1` proposal roles; all roles have overrides; all routes resolve to enabled models with fallback chains; config mtime precedes dispatch.

Sources: `spec.json` (`maxLanes` 70, 70 items), `dispatch.json` (`taskCall.tasks` 70 × `{agent,name,task}`, `compaction {applied:false}`, `note` = one batched task call), `out/swarm-registry.json` (70 members, `createdAt` `2026-10-27T05:05:10.877Z`, `wave: kama-r52-w1`), `validate.out` (`exit=0`).

Role counts (identical in all three sources): executor 21, reviewer 12, scout 10, critic 8, mutation-tester 6, scribe 5, sentinel 3, connector 3, simplifier 1, revenger 1 = **70**.

Band/ceiling citations: `/home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json:84` (`maxLanes` 256), `:89-90` (`waveMinLanes` 64, `waveMaxLanes` 128), `:104-115` (`proposalRoles`, incl. `sentinel` at `:109`); shape rule `scripts/hyaku/lane-addendum.md:21-23`. Ramp `ceil(70/5) = 14` batches × 700 ms = 9.8 s.

### E2 — attack share and axis spread

```
ATTACK reviewer+critic+mutation-tester = 26/70 = 37.14% (floor 18 seats = 25.00%) -> MET
ATTACK with labrat (addendum 4-role)      = 26/70 = 37.14% -> MET
```

reviewer 12 + critic 8 + mutation-tester 6 = **26/70 = 37.14 %**; floor = 18 seats. Attack items by axis: calibration 16, operability 12 (two seats bind both). Rule citations: `lane-addendum.md:19-20` (≥25 % attack share and few-connector rule still apply), four-role definition `:151-153` (labrat — 0 seats here). Connector 3/70 = 4.29 %. Prior rounds: r48 34/69 = 49.0 % (`corpus/lessons/round-48-verifier-spotcheck.md:28`), r50 20/66 = 30.30 % (`.ufo/waves/round-50/w1/out/X16Policy.md:3`), r51 25/66 = 37.88 % (`.ufo/waves/round-51/a2w1/out/Sen4Policy/policy.md:27`) — stable at 37 % across r51/r52.

### E3 — per-model seat counts under the live map

```
PER-MODEL SEATS (live map)
   21   30.00%  minimax-code/MiniMax-M3.1-Flash:high  [executor 21]
   18   25.71%  zai/glm-5.3-flash:max  [mutation-tester 6, reviewer 12]
   18   25.71%  kimi-code/kimi-for-coding:max  [critic 8, scout 10]
   10   14.29%  opencode-go/deepseek-v4.1-flash:high  [revenger 1, scribe 5, sentinel 3, simplifier 1]
    3    4.29%  google-antigravity/gemini-3.8-flash:high  [connector 3]

PER-ALIAS SEATS: @m_mim 21 (30.00%) | @m_zfl 18 (25.71%) | @m_kfc 18 (25.71%) | @m_flash 10 (14.29%) | @m_antigravity 3 (4.29%)
```

Resolution path `config.yml:350-368` (`task.agentModelOverrides`) → `:320-345` (`modelRoles`) → `enabledModels`; chains from `retry.fallbackChains` (`:370+`). `m_flash` 10/70 = 14.29 %; the run-7/8 "m_flash ≥50 %" condition no longer binds (`lane-addendum.md:18-20`). **Attack concentration: 18 attack seats on `@m_zfl` (GLM), 8 on `@m_kfc` (Kimi), none on the 21-seat `@m_mim` volume route** — no attack review runs on the largest model tier.

### E4 — route-map fingerprint at dispatch (round-50 closure R7)

```
CONFIG /home/vgpnk/.omp/agent/config.yml
  mtime   2026-10-27T02:39:08.510680Z (2026-10-26 23:39:08.510680-03:00)
  ctime   2026-10-27T02:39:08.510680Z
  size    14940 B
  sha256  0d5874660274d3a4545d9d1f9e1da320f0629a9efb384255b788b897bba6addc
  registry createdAt 2026-10-27T05:05:10.877Z  (config precedes dispatch by 8762s)
```

Byte-identical to the map recorded for round 51 (`Sen4Policy/policy.md`, same sha256, same 14,940 B): routing did not change between the two dispatches. Policy file fingerprint for the record: `scripts/hyaku/ufo-wave-policy-v2.json`, mtime 2026-10-22 15:55:22.570413032 -0300, 12,676 B, sha256 `f12e1d6dfeae81a4a1ff805f8de50ec8386b3a16ae7f40b171f54c5236812fff`.

## Defects

### F1 — `hyaku.env` run-9 labels are stale for 42/70 seats (operability, medium; repeats round-51 F1)

`/home/vgpnk/Projects/shokunin/scripts/hyaku/hyaku.env:10-11` states run 9 uses "the same run-8 map, unchanged"; `:7-9` prints that run-8 map. The binding addendum records the mid-run amendments (`lane-addendum.md:10-19`) and the live config matches the addendum, not the labels: executor `@m_flash`→`@m_mim` (21 seats), scout `@m_sonnet`→`@m_kfc` (10), critic `@m_flash`→`@m_kfc` (8), connector `@m_kfc`→`@m_antigravity` (3) = **42/70 = 60.00 %** mislabelled.

Command that shows it:

```
$ python3 - <<'EOF'
import re,yaml
cfg=yaml.safe_load(open('/home/vgpnk/.omp/agent/config.yml'))['task']['agentModelOverrides']
env=open('/home/vgpnk/Projects/shokunin/scripts/hyaku/hyaku.env').read()
c={}
for g,a in re.findall(r'([\w/]+)\s+(@m_\w+)',env):
    for r in g.split('/'): c[r]=a
for r in ['executor','scout','critic','connector']: print(r,c[r],'live',cfg[r])
EOF
executor @m_flash live @m_mim
scout @m_sonnet live @m_kfc
critic @m_flash live @m_kfc
connector @m_kfc live @m_antigravity
```

Fix: replace the run-9 comment block with the amended map — hunk 2 of `proposed-fixes.diff` (`patch -p1 --dry-run` exit 0).

### F2 — policy `lanes[]` lists `labrat`, omits `sentinel` (calibration, low; carried round-51 F3)

`scripts/hyaku/ufo-wave-policy-v2.json:267-271` (table opens `:256`) lists `labrat`; `sentinel` — a `proposalRoles` member at `:109`, 3 seats this wave — is absent. No dispatch effect (validator `exit=0`, routing via config overrides). Fix: swap the row (hunk 1, third section of `proposed-fixes.diff`).

### F3 — `omp-native-v1.concurrencyCeiling` 32 contradicts the band it governs (operability, low; new)

`ufo-wave-policy-v2.json:98` sets `concurrencyCeiling: 32` for the profile running these waves, while `:89-90` admits 64–128 lanes, this wave dispatches 70, and the binding addendum says "at most ~88 seats run at once across the fleet" (`lane-addendum.md:24`). Not enforced: `grep -rn concurrencyCeiling scripts/` matches only the two policy JSONs (v1 + v2), never a runner. Fix: `32` → `128`, or annotate as a legacy v1 ceiling; value change in `proposed-fixes.diff` (hunk 1, second section).

### F4 — policy `surfaceDigest` lags the canonical origin (calibration, low; round-51 F5 now resolved in direction)

```
$ grep -n surfaceDigest /home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json   # :55
  "surfaceDigest": "sha256:1064c19addf69f294fd46ebbaa3a99298a4fe60eb5241fcb0d1406f1c0ba6bb4"
$ grep -n surfaceDigest /home/vgpnk/Projects/ufo-fsd-alpha/config/ufo.json                    # :55
  "surfaceDigest": "sha256:610575e868e0f0fe0ab4af01e9a1ff438740a552f0c83956b85235279e848ce3"
$ git -C /home/vgpnk/Projects/ufo-fsd-alpha status --porcelain config/ufo.json   # (empty)
$ git -C /home/vgpnk/Projects/ufo-fsd-alpha log -1 --format='%h %ad %s' -- config/ufo.json
0fd34cab Sat Oct 24 22:52:26 2026 -0300 supervision: pause sentinel + bounded restart backoff, ...
```

Origin worktree is clean and HEAD's value equals the worktree's. Policy mtime 2026-10-22 15:55 **precedes** the origin commit that set the current pin (2026-10-24 22:52), so the policy's copy is the stale side — the direction round 51 left unadjudicated. `1064c19a` was itself a deliberate re-charter (`kumitate-shokunin/.ufo/waves/round-35/build/ScoutSurfaceProbe.md:111`), so this is drift, not corruption. Recipe is `sha256(canonicalJson(manifest))` (`kumitate-shokunin/corpus/knowledge/live-surface-probe.md:129`): regenerate, do not hand-copy. Hunk 1, first section of `proposed-fixes.diff` shows the target value only.

### F5 — three items bind axes outside the wave declaration (calibration, informational)

Wave `axes` = [`calibration`, `operability`]; `N1Overlap` (connector) binds `adjacency`, `A1Assim` (scout) binds `coverage`, `Sc3Province` (scout) binds `adjacency`+`operability`. Both extras are canonical (`/home/vgpnk/Projects/shokunin/AXES.md:12,16`) and the validator accepts item-level axes (`validate.out` `exit=0`), so this is not a defect; the wave declaration simply does not name two axes in use. 60 items bind one axis, 10 bind two.

## Resolved / non-findings

- **Round-51 F2 (conflicting executor labrat grant) does not exist here**: `grep -c labrat` over `round-52/w1/spec.json` = **0** and over `round-52/build_spec.py` = **0**; every item carries the unambiguous "Lane bounds: leaf member — no subagent dispatch."
- No per-task `model` key in the dispatch (70/70 `{agent,name,task}`) — the role map is the sole routing authority, as the addendum requires.
- `m_flash ≥50 %` is not applied (14.29 %) and not violated: the addendum retired it at `:18-19`.
- Falsifier for the "one batched task call" rule: `dispatch.json` has a single `taskCall` with `compaction {applied:false}` and `counts.spawn == 70`; no split wave.

## Reproduction

```sh
cd /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/Sen3Policy
./route_check.py > route_check.out 2>&1; echo $?        # 0, "RESULT pass", 20 PASS / 0 FAIL
patch -p1 --dry-run -d <pristine scripts/ tree> < proposed-fixes.diff ; echo $?   # 0
```

`route_check.py` reads only; it parses `spec.json`, `dispatch.json`, `out/swarm-registry.json`, `validate.out`, `ufo-wave-policy-v2.json`, `config.yml`, `hyaku.env`, `AXES.md`-adjacent values and the origin `config/ufo.json` path, prints drift flags, and exits non-zero only when a structural agreement check fails.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/Sen3Policy.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/Sen3Policy/policy.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/Sen3Policy/route_check.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/Sen3Policy/route_check.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/Sen3Policy/proposed-fixes.diff`
